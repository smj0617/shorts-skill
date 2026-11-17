"""진행 중 쇼츠 상태 기록(.scratch/shorts-active.json)과 쇼츠 명세(.scratch/<영상 이름>/spec.md)의 Stage: 줄.

두 곳의 단계를 항상 함께 바꾼다. 새 세션은 이 둘만 읽고 이어 간다. 프로젝트 루트(video1)에서:

    python .claude/skills/shorts/scripts/active.py show             # 진행 중 쇼츠·동시 진행 목록·보류 목록, 없으면 "없음"
    python .claude/skills/shorts/scripts/active.py start <영상 이름>   # 1. 기획으로 시작(보류한 쇼츠면 그 단계로 이어 감)
    python .claude/skills/shorts/scripts/active.py stage <번호|이름>   # 단계 바꾸기
    python .claude/skills/shorts/scripts/active.py hold             # 진행 중 쇼츠를 보류 목록으로

연작을 편마다 다른 세션에서 동시에 만들 때(동시 진행 목록, 세션마다 자기 편만 --video로 바꾼다):

    python .claude/skills/shorts/scripts/active.py start <영상 이름> --parallel     # 진행 중 쇼츠가 있어도 동시 진행 목록에 더한다
    python .claude/skills/shorts/scripts/active.py stage <번호|이름> --video <영상>  # 그 영상의 단계만(진행 중 쇼츠든 목록이든)
    python .claude/skills/shorts/scripts/active.py show --video <영상>             # 그 영상의 단계만, 없으면 "없음"
    python .claude/skills/shorts/scripts/active.py hold --video <영상>             # 그 영상만 보류 목록으로

진행 중 쇼츠가 있는데(게시 완료 제외) 다른 쇼츠를 --parallel 없이 start하면 ActiveError로 멈춘다. 먼저 hold한다.
start --parallel은 명세가 이미 있으면 그 Stage 단계로, 없으면 1. 기획으로 더한다(보류 목록에 있던 편은 거기서 뺀다).
동시 진행 목록에서 10. 게시 완료가 된 편은 목록에 "게시 완료"로 남아 있다가 다음 start --parallel 때 빠진다
(빠진 뒤에도 명세 Stage 줄은 남으므로 pace.py --video report는 그대로 된다).
여러 세션이 거의 동시에 고쳐도 다른 편 기록이 날아가지 않게, 고치기는 잠금 파일(.scratch/shorts-active.lock) 안에서
읽고-고치고-쓰기를 한 번에 하고, 쓰기는 임시 파일을 만든 뒤 원자적으로 바꿔 끼운다.
"""
import json
import os
import re
import sys
import time
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
STAGES = (
    "기획",
    "기획안 승인 대기",
    "곡 받기와 녹음",
    "애니메틱 연출 확인",
    "제작",
    "미리보기",
    "완성",
    "업로드",
    "썸네일",
    "게시 완료",
)
STAGE_LINE = re.compile(r"^Stage: (\d+)\. .*$")
LOCK_WAIT = 10      # 잠금을 기다리는 최대 시간(초)
LOCK_STALE = 30     # 이보다 오래된 잠금 파일은 죽은 세션이 남긴 것으로 보고 지운다(초)


class ActiveError(Exception):
    pass


def _state_path(root):
    return Path(root) / ".scratch" / "shorts-active.json"


def _spec_path(root, name):
    return Path(root) / ".scratch" / name / "spec.md"


def _load(root):
    path = _state_path(root)
    state = {"active": None, "held": [], "parallel": []}
    for _ in range(50):
        try:
            if path.exists():
                state.update(json.loads(path.read_text(encoding="utf-8")))
            break
        except (PermissionError, json.JSONDecodeError):  # 다른 세션이 바꿔 끼우는 순간
            time.sleep(0.02)
    state.setdefault("parallel", [])
    return state


def _save(root, state):
    path = _state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.{time.monotonic_ns()}.tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for _ in range(100):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:  # Windows: 다른 세션이 읽는 중
            time.sleep(0.02)
    tmp.unlink(missing_ok=True)
    raise ActiveError(f"{path}를 바꿔 끼우지 못했다.")


@contextmanager
def _locked(root):
    """읽고-고치고-쓰기를 다른 세션과 겹치지 않게 한다. 안에서 state를 고치면 나갈 때 저장한다(예외면 저장 안 함)."""
    lock = _state_path(root).with_suffix(".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + LOCK_WAIT
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            try:
                if time.time() - lock.stat().st_mtime > LOCK_STALE:
                    lock.unlink()
                    continue
            except (FileNotFoundError, PermissionError):
                pass
        except PermissionError:  # Windows: 다른 세션이 잠금 파일을 지우는 순간
            pass
        if time.monotonic() > deadline:
            raise ActiveError(f"{lock} 잠금이 {LOCK_WAIT}초 넘게 풀리지 않는다.")
        time.sleep(0.01)
    try:
        state = _load(root)
        yield state
        _save(root, state)
    finally:
        os.close(fd)
        try:
            lock.unlink()
        except FileNotFoundError:
            pass


def _stage_number(stage):
    if isinstance(stage, int) or str(stage).isdigit():
        number = int(stage)
        if 1 <= number <= len(STAGES):
            return number
    elif stage in STAGES:
        return STAGES.index(stage) + 1
    raise ActiveError(f"없는 단계: {stage}. 단계는 " + ", ".join(f"{i}. {s}" for i, s in enumerate(STAGES, 1)))


def _write_spec_stage(root, name, number):
    path = _spec_path(root, name)
    line = f"Stage: {number}. {STAGES[number - 1]}"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{line}\n\n# {name}\n\n## 기획안\n\n## 의견 목록\n\n## Comments\n", encoding="utf-8")
        return
    lines = path.read_text(encoding="utf-8").split("\n")
    if lines and STAGE_LINE.match(lines[0]):
        lines[0] = line
    else:
        lines[:0] = [line, ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def _view(entry):
    return {"name": entry["name"], "stage": entry["stage"], "stage_name": STAGES[entry["stage"] - 1]}


def _find(state, name):
    """진행 중 쇼츠나 동시 진행 목록에서 그 영상의 기록(고치면 state에 반영된다). 없으면 None."""
    if state["active"] is not None and state["active"]["name"] == name:
        return state["active"]
    return next((e for e in state["parallel"] if e["name"] == name), None)


def show(root=ROOT, video=None):
    state = _load(root)
    current = state["active"] if video is None else _find(state, video)
    return None if current is None else _view(current)


def held(root=ROOT):
    return list(_load(root)["held"])


def parallel(root=ROOT):
    return [_view(e) for e in _load(root)["parallel"]]


def spec_stage(root, name):
    """명세 Stage 줄의 단계(목록에서 빠진 게시 완료 편 등). 없으면 None."""
    try:
        return _view({"name": name, "stage": _spec_stage(root, name)})
    except ActiveError:
        return None


def start(root, name, parallel=False):
    with _locked(root) as state:
        if _find(state, name) is not None:
            return
        current = state["active"]
        if not parallel and current is not None and current["stage"] != len(STAGES):
            raise ActiveError(f"{current['name']}이(가) {current['stage']}. {STAGES[current['stage'] - 1]} 단계로 진행 중이다. "
                              "이어 하거나, hold로 보류한 뒤 시작한다(동시에 만들면 --parallel).")
        if name in state["held"]:
            number = _spec_stage(root, name)
            state["held"].remove(name)
        elif parallel and spec_stage(root, name) is not None:
            number = _spec_stage(root, name)
        else:
            number = 1
            _write_spec_stage(root, name, number)
        if parallel:
            state["parallel"] = [e for e in state["parallel"] if e["stage"] != len(STAGES)]
            state["parallel"].append({"name": name, "stage": number})
        else:
            state["active"] = {"name": name, "stage": number}


def hold(root=ROOT, video=None):
    with _locked(root) as state:
        if video is None:
            if state["active"] is None:
                raise ActiveError("보류할 진행 중 쇼츠가 없다.")
            name = state["active"]["name"]
            state["active"] = None
        else:
            if _find(state, video) is None:
                raise ActiveError(f"{video}은(는) 진행 중 쇼츠도 동시 진행 목록에도 없다.")
            name = video
            if state["active"] is not None and state["active"]["name"] == video:
                state["active"] = None
            state["parallel"] = [e for e in state["parallel"] if e["name"] != video]
        state["held"].append(name)


def _spec_stage(root, name):
    path = _spec_path(root, name)
    first = path.read_text(encoding="utf-8").split("\n", 1)[0] if path.exists() else ""
    match = STAGE_LINE.match(first)
    if not match:
        raise ActiveError(f"{path} 첫 줄에 Stage: 줄이 없다.")
    return _stage_number(int(match.group(1)))


def set_stage(root, stage, video=None):
    number = _stage_number(stage)
    with _locked(root) as state:
        entry = state["active"] if video is None else _find(state, video)
        if entry is None:
            if video is None:
                raise ActiveError("진행 중인 쇼츠가 없다. 먼저 start한다.")
            raise ActiveError(f"{video}은(는) 진행 중 쇼츠도 동시 진행 목록에도 없다. 먼저 start --parallel한다.")
        entry["stage"] = number
        _write_spec_stage(root, entry["name"], number)


def _line(entry):
    return f"{entry['name']}: {entry['stage']}. {entry['stage_name']}"


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    command, args = argv[0], list(argv[1:])
    video = None
    if "--video" in args:
        i = args.index("--video")
        if i + 1 >= len(args):
            raise SystemExit(__doc__)
        video = args[i + 1]
        del args[i:i + 2]
    is_parallel = "--parallel" in args
    if is_parallel:
        args.remove("--parallel")
    try:
        if command == "show" and not args and not is_parallel:
            if video is not None:
                current = show(ROOT, video)
                print("없음" if current is None else _line(current))
            else:
                current = show(ROOT)
                print("없음" if current is None else _line(current))
                print("동시 진행: " + (", ".join(_line(e) for e in parallel(ROOT)) or "없음"))
                print("보류: " + (", ".join(held(ROOT)) or "없음"))
        elif command == "start" and len(args) == 1 and video is None:
            start(ROOT, args[0], parallel=is_parallel)
        elif command == "stage" and len(args) == 1 and not is_parallel:
            set_stage(ROOT, args[0], video)
        elif command == "hold" and not args and not is_parallel:
            hold(ROOT, video)
        else:
            raise SystemExit(__doc__)
    except ActiveError as error:
        print(f"상태 기록 실패: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
