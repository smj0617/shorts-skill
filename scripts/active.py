"""진행 중 쇼츠 상태 기록(.scratch/shorts-active.json)과 쇼츠 명세(.scratch/<영상 이름>/spec.md)의 Stage: 줄.

두 곳의 단계를 항상 함께 바꾼다. 새 세션은 이 둘만 읽고 이어 간다. 프로젝트 루트(video1)에서:

    python .claude/skills/shorts/scripts/active.py show             # 진행 중 쇼츠와 단계, 없으면 "없음"
    python .claude/skills/shorts/scripts/active.py start <영상 이름>   # 1. 기획으로 시작(보류한 쇼츠면 그 단계로 이어 감)
    python .claude/skills/shorts/scripts/active.py stage <번호|이름>   # 단계 바꾸기
    python .claude/skills/shorts/scripts/active.py hold             # 진행 중 쇼츠를 보류 목록으로

진행 중 쇼츠가 있는데(게시 완료 제외) 다른 쇼츠를 start하면 ActiveError로 멈춘다. 먼저 hold한다.
"""
import json
import re
import sys
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


class ActiveError(Exception):
    pass


def _state_path(root):
    return Path(root) / ".scratch" / "shorts-active.json"


def _spec_path(root, name):
    return Path(root) / ".scratch" / name / "spec.md"


def _load(root):
    path = _state_path(root)
    if not path.exists():
        return {"active": None, "held": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _save(root, state):
    path = _state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def show(root=ROOT):
    current = _load(root)["active"]
    if current is None:
        return None
    return {"name": current["name"], "stage": current["stage"], "stage_name": STAGES[current["stage"] - 1]}


def held(root=ROOT):
    return list(_load(root)["held"])


def start(root, name):
    state = _load(root)
    current = state["active"]
    if current is not None and current["name"] != name and current["stage"] != len(STAGES):
        raise ActiveError(f"{current['name']}이(가) {current['stage']}. {STAGES[current['stage'] - 1]} 단계로 진행 중이다. "
                          "이어 하거나, hold로 보류한 뒤 시작한다.")
    if current is not None and current["name"] == name:
        return
    if name in state["held"]:
        state["held"].remove(name)
        number = _spec_stage(root, name)
    else:
        number = 1
        _write_spec_stage(root, name, number)
    _set_active(state, name, number)
    _save(root, state)


def hold(root=ROOT):
    state = _load(root)
    if state["active"] is None:
        raise ActiveError("보류할 진행 중 쇼츠가 없다.")
    state["held"].append(state["active"]["name"])
    state["active"] = None
    _save(root, state)


def _spec_stage(root, name):
    path = _spec_path(root, name)
    first = path.read_text(encoding="utf-8").split("\n", 1)[0] if path.exists() else ""
    match = STAGE_LINE.match(first)
    if not match:
        raise ActiveError(f"{path} 첫 줄에 Stage: 줄이 없다.")
    return _stage_number(int(match.group(1)))


def set_stage(root, stage):
    state = _load(root)
    if state["active"] is None:
        raise ActiveError("진행 중인 쇼츠가 없다. 먼저 start한다.")
    number = _stage_number(stage)
    name = state["active"]["name"]
    _set_active(state, name, number)
    _write_spec_stage(root, name, number)
    _save(root, state)


def _set_active(state, name, number):
    state["active"] = {"name": name, "stage": number}


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    command, args = argv[0], argv[1:]
    try:
        if command == "show" and not args:
            current = show()
            print("없음" if current is None else f"{current['name']}: {current['stage']}. {current['stage_name']}")
            print("보류: " + (", ".join(held()) or "없음"))
        elif command == "start" and len(args) == 1:
            start(ROOT, args[0])
        elif command == "stage" and len(args) == 1:
            set_stage(ROOT, args[0])
        elif command == "hold" and not args:
            hold(ROOT)
        else:
            raise SystemExit(__doc__)
    except ActiveError as error:
        print(f"상태 기록 실패: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
