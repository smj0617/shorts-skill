"""제작 속도 장부와 기준(2026-11-11 사용자: 목표 영상 하나 1시간, "작업이 느려지는 부분을 스스로 감시하고, 기준을 세워
느려지면 즉시 빠른 방법으로 바꾸는 프로세스", "기준은 5분: AI가 하나의 작업을 5분 넘게 잡고 있으면 바로 더 빠른 방법으로").
장부는 .scratch/<영상 이름>/pace.jsonl(진행 중 쇼츠, active.py).

    python .claude/skills/shorts/scripts/pace.py start "<일>" --kind <종류>   # 일 시작(종류는 FIX의 키)
    python .claude/skills/shorts/scripts/pace.py alarm                       # 백그라운드로: 그 일이 5분을 넘기면 "!!"를 찍고 끝난다
    python .claude/skills/shorts/scripts/pace.py end ["메모"]                 # 가장 최근에 시작한 일 끝(알람도 조용히 끝난다)
    python .claude/skills/shorts/scripts/pace.py check                       # 5분 넘은 일·되풀이: "!!" 줄 + 바로 바꿀 것. 있으면 종료 코드 2
    python .claude/skills/shorts/scripts/pace.py report                      # 단계별·종류별 시간, 느린 일 다섯(회고용)

기준은 하나다: 일 하나가 LIMIT(5분)를 넘기면 느린 것. 그 순간(알람이 끝났다는 알림, 또는 check의 "!!") Claude는 그 줄의
"바로 바꿀 것"으로 즉시 방법을 바꾸고 사용자에게 한 줄 알린다. 하던 긴 명령은 백그라운드로 넘기거나 멈추고, 에이전트는
나눠 다시 맡긴다. 같은 "!!"가 두 번이거나 바로 바꿀 것이 맞지 않으면 감시 에이전트(.claude/agents/pace-watcher.md)를
띄워 원인을 분석한다(SKILL.md "속도 감시"). 새로 찾은 원인과 해결은 아래 FIX에 올린다(다음부터 즉시 바꾸기).
단계 목표(STAGE_BUDGET, 합 60분)는 회고와 감시 에이전트가 보는 참고값이다.
"""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import active  # noqa: E402

TOTAL = 60          # 영상 하나 목표(분)
# 단계별 목표(분): 사용자를 기다리는 시간은 빼고 Claude가 일한 시간(start~end 합). 합이 TOTAL.
STAGE_BUDGET = {1: 8, 2: 4, 3: 10, 4: 10, 5: 15, 6: 8, 7: 5}
LIMIT = 5           # 일 하나의 기준(분). 넘으면 즉시 빠른 방법으로(사용자 기준)
POLL = 10           # 알람이 일이 끝났는지 보는 간격(초)
# 일 종류: 5분을 넘겼을 때 바로 바꿀 것.
FIX = {
    "기획": "질문은 번호 질문 한 번에 묶고 답 없는 번호는 추천대로. 대본 판을 늘리지 말고 막힌 문장 하나만 다시 쓴다. 새 후보를 내기 전에 planning-feedback 오늘 절의 '다음부터'를 모두 점검표로 묶어 통과한 것만 보인다. 해결·필요 장면이 승인되기 전에는 훅을 다듬지 않는다(stream-1)",
    "러프": "러프는 대본판에서 필요 장면·주인공 사물이 확인된 뒤 2~3개를 한 에이전트(low)로 한 번에 그리고, 고른 하나만 공들인다(stream-1: 대본이 바뀌는 동안 러프 12차, 무대가 바뀌어 3·4판을 버림)",
    "낙서": "주인공은 hero.py 포즈 인자로만 뽑고 갈래마다 복사하지 않는다. 모음 낙서를 먼저 쓴다. 시안은 한 칸만, 점검·다듬기는 고른 것만",
    "녹음": "녹음은 백그라운드로 돌리고 그동안 낙서·표를 한다. 고칠 장면은 모아 요청 한 번",
    "애니메틱": "움직임은 표(keys)로만. 정지 움직임 시트를 따로 만들지 않는다. 표에 없는 동작은 moves.py 몇 줄",
    "레이어": "keys.py로 표의 무대를 한 번에. 손 스크립트는 표로 안 되는 무대만, 그것도 파일마다 에이전트 하나로 동시에",
    "의견": "연출 의견은 에이전트 없이 표 값 고치기 + keys.py --only <장면>. 의견은 목록으로 모아 장면별로 동시에",
    "검사": "check_parallel.py 기본(사건 시각만, 대비·craft 없이, 캐시)으로 바뀐 구간(--range)만. --full은 렌더 직전 한 번. 렌더·Studio가 안 돌면 --parts 6으로 더 쪼갠다(12코어, 기본 3에 머물러 기다리지 않는다)",
    "렌더": "렌더 로그에 'falls back to screenshot capture ... too little memory'가 있으면 메모리 부족이다: 같이 도는 검사·snapshot·Studio를 멈추거나 끝난 뒤로 미룬다(2026-11-11 transaction: --full 검사 브라우저 3개와 겹쳐 렌더 약 10분, 느린 스크린샷 캡처). 전체 검사 --full은 6단계 끝(미리보기 의견을 다 고친 직후)에 돌려 7단계 렌더는 혼자 돈다. 옵션은 기본 그대로(--gpu·조각 방식 HF_SEGMENTED_CAPTURE는 측정에서 더 느렸다: 기본 167초 vs 209·311초). 진행 중 렌더는 남은 시간이 다시 찍는 시간보다 짧으면 두고 원인만 고친다",
    "에이전트": "파일이 겹치지 않게 나눠 동시에, effort를 낮추고(값 고치기 medium, 생성·실행 low), 길어지면 인계 메모로 바꾼다",
    "명령": "2분 넘는 명령은 백그라운드로 돌리고 기다리는 동안 다른 일을 한다",
    "썸네일": "썸네일은 make_thumbnail.py 한 번, 시안은 --out drafts로 한 장씩. 기준 테스트로 확인",
    # 2026-11-11 transaction-shorts 회고(7.7시간): 시간은 일 하나보다 '판'(같은 것을 다시 보이기)에서 샜다.
    "곡": "곡은 하나씩 맞추지 말고 후보 3곡을 '개념의 특성 = 곡의 짜임' 한 줄씩과 함께 30초 시험 판으로 한 번에 들려주고 고르게 한다. 고른 곡만 대본 길이에 맞춘다",
    "시안": "시안이 두 번 퇴짜면 같은 축으로 또 그리지 말고, 지난 쇼츠 문법(주인공 사물 가운데 크게)과 사물·성격·화풍 축을 나눈 후보 3개를 한 장에 나란히 낸다",
    "깜빡임": "눈으로 찾지 말고 상태가 바뀌는 시각마다 앞뒤 0.1초 snapshot을 한 번에 찍어 비교한다. 고친 뒤엔 그 시각들만 다시 찍는다",
}
REPEAT = 3          # 같은 일(이름)을 이만큼 다시 시작하면 원인을 본다(같은 장면을 세 번째 다시 만듦)


class PaceError(Exception):
    pass


def _ledger(root=ROOT):
    cur = active.show(root)
    if not cur:
        raise PaceError("진행 중 쇼츠가 없다(active.py start)")
    return Path(root) / ".scratch" / cur["name"] / "pace.jsonl", cur


def _read(path):
    if not path.exists():
        return []
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _append(path, rec):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def start(step, kind, root=ROOT, now=None):
    if kind not in FIX:
        raise PaceError(f"종류 {kind!r}가 없다(있는 것: {', '.join(FIX)})")
    path, cur = _ledger(root)
    _append(path, {"t": time.time() if now is None else now, "ev": "start", "step": step, "kind": kind, "stage": cur["stage"]})


def end(note="", root=ROOT, now=None):
    path, _ = _ledger(root)
    open_ = _open_steps(_read(path))
    if not open_:
        raise PaceError("끝낼 일이 없다(pace.py start 먼저)")
    _append(path, {"t": time.time() if now is None else now, "ev": "end", "step": open_[-1]["step"], "note": note})


def _open_steps(recs):
    stack = []
    for r in recs:
        if r["ev"] == "start":
            stack.append(r)
        elif r["ev"] == "end":
            for i in range(len(stack) - 1, -1, -1):
                if stack[i]["step"] == r["step"]:
                    stack.pop(i)
                    break
    return stack


def spans(recs, now=None):
    """[(step, kind, stage, 분, 끝났나)]."""
    now = time.time() if now is None else now
    out, open_ = [], {}
    for r in recs:
        if r["ev"] == "start":
            open_.setdefault(r["step"], []).append(r)
        elif r["ev"] == "end" and open_.get(r["step"]):
            s = open_[r["step"]].pop()
            out.append((s["step"], s["kind"], s["stage"], (r["t"] - s["t"]) / 60, True))
    for lst in open_.values():
        for s in lst:
            out.append((s["step"], s["kind"], s["stage"], (now - s["t"]) / 60, False))
    return out


def check(root=ROOT, now=None):
    """기준을 넘은 것마다 "!!" 줄(바로 바꿀 것 포함). 없으면 빈 목록."""
    path, cur = _ledger(root)
    recs = _read(path)
    sp = spans(recs, now)
    out = []
    for step, kind, stage, m, done in sp:
        if m > LIMIT:
            out.append(f"!! {kind} '{step}' {m:.1f}분{'' if done else '(진행 중)'} > 기준 {LIMIT}분 → 바로 바꿀 것: {FIX[kind]}")
    counts = {}
    for r in recs:
        if r["ev"] == "start":
            counts[r["step"]] = counts.get(r["step"], 0) + 1
    for step, n in counts.items():
        if n >= REPEAT:
            out.append(f"!! '{step}'을 {n}번째 다시 함 → 원인 분석: 감시 에이전트(pace-watcher)를 띄운다")
    return out


def alarm(root=ROOT, poll=POLL, clock=time.time, sleep=time.sleep):
    """가장 최근에 시작한 일이 LIMIT를 넘기면 "!!" 줄을 돌려준다(끝나면 None). 백그라운드로 돌려 그 순간 알림을 받는다."""
    path, _ = _ledger(root)
    open_ = _open_steps(_read(path))
    if not open_:
        raise PaceError("지켜볼 일이 없다(pace.py start 먼저)")
    s = open_[-1]
    while True:
        if s["step"] not in [o["step"] for o in _open_steps(_read(path))]:
            return None
        m = (clock() - s["t"]) / 60
        if m > LIMIT:
            return (f"!! {s['kind']} '{s['step']}' {m:.1f}분째 > 기준 {LIMIT}분 → 지금 바로 바꿀 것: {FIX[s['kind']]}"
                    " (하던 긴 명령은 백그라운드로·멈춤, 에이전트는 나눠 다시)")
        sleep(poll)


def report(root=ROOT, now=None):
    path, cur = _ledger(root)
    sp = spans(_read(path), now)
    lines = [f"{cur['name']} 속도 (목표 {TOTAL}분)"]
    by_stage, by_kind = {}, {}
    for step, kind, stage, m, done in sp:
        by_stage[stage] = by_stage.get(stage, 0) + m
        by_kind[kind] = by_kind.get(kind, 0) + m
    for stage, m in sorted(by_stage.items()):
        lines.append(f"  {stage}단계 {m:5.1f}분 / 목표 {STAGE_BUDGET.get(stage, '-')}분")
    lines.append("  종류: " + ", ".join(f"{k} {m:.1f}분" for k, m in sorted(by_kind.items(), key=lambda x: -x[1])))
    lines.append("  느린 일: " + "; ".join(f"{s}({k}) {m:.1f}분" for s, k, _, m, _ in sorted(sp, key=lambda x: -x[3])[:5]))
    lines.append(f"  합계 {sum(by_stage.values()):.1f}분")
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description="제작 속도 장부")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("step")
    s.add_argument("--kind", required=True)
    e = sub.add_parser("end")
    e.add_argument("note", nargs="?", default="")
    sub.add_parser("check")
    sub.add_parser("alarm")
    sub.add_parser("report")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "start":
            start(a.step, a.kind)
        elif a.cmd == "end":
            end(a.note)
        elif a.cmd == "alarm":
            msg = alarm()
            print(msg or "기준 안에 끝남")
            sys.exit(2 if msg else 0)
        elif a.cmd == "check":
            bad = check()
            print("\n".join(bad) if bad else "기준 안")
            sys.exit(2 if bad else 0)
        else:
            print("\n".join(report()))
    except PaceError as err:
        raise SystemExit(str(err))


if __name__ == "__main__":
    main()
