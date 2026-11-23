"""검사를 구간으로 나눠 동시에 돌리고 결과를 합친다 (2026-11-11 사용자: "전체 검사도 병렬로 해서 병합하는 방식으로",
"검사가 느리다": 고치는 중에는 사건 시각만 가볍게, 렌더 직전 전체 검사만 대비·craft를 켠다).

`npm run check` 한 번은 10분을 넘긴다(proxy-shorts, transaction-shorts). 구간마다 브라우저를 따로 띄우므로 동시 수만큼
빨라진다. 동시 수는 기본 3(그 이상은 브라우저끼리 CPU를 다퉈 오히려 느려진다).

    python .claude/skills/shorts/scripts/check_parallel.py <영상 폴더>           # 고치는 중(기본, 가벼움)
    python .claude/skills/shorts/scripts/check_parallel.py <영상 폴더> --full    # 렌더 직전 전체 검사(한 번)

  기본(고치는 중): 사건 시각에서만 본다(--at). 사건 시각은 compositions/keys.py가 남긴 .harness/check-times.json
                  (표의 줄 시각), 없으면 timing.json 문장마다 시작·가운데. --no-craft --no-contrast --cache --budget 120s.
  --full:         장면 경계로 자른 구간(--range)마다 기본 표본 + 대비 + craft, 캐시 없이.
  --parts N       동시 수(기본: --range 있으면 3, 없으면 6).  --range a,b 여러 번: 그 구간만(바뀐 구간만 다시 볼 때, 그 구간의 사건 시각만).
  --cli           검사 CLI(기본 CHECK_CLI). craft·cache·budget은 0.9 판부터 있어 렌더용 고정 판(package.json)과 따로 둔다.
                  "pinned"면 npm run check(고정 판). 그 판이 모르는 옵션은 빼고 무엇을 뺐는지 알린다.
  -- 뒤:          check에 그대로 넘길 인자.

구간마다 로그는 <영상>/.harness/check/<이름>.log. 끝나면 구간별 종료 코드와 error·warning 줄만 모아 찍고,
하나라도 실패하면 종료 코드 1.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CHECK_CLI = "hyperframes@0.9.85"   # 0.9.30은 2026-11-23 Chrome을 못 띄움(장면 에이전트 셋이 모두 0.9.85로 돌림)
PARTS = 3          # --range로 바뀐 구간만 볼 때
WHOLE_PARTS = 6    # --range 없는 전체(가벼운 전체·--full): 12코어라 6갈래(2026-11-23 사용자: "전체검사 할 때도 구간별로 나눠서 병렬로 … 왜 안 지켜")
LIGHT = ["--no-craft", "--no-contrast", "--cache", "--budget=120s"]
FULL = ["--contrast", "--craft", "--no-cache"]


def cut(timing, parts):
    total = timing.get("total") or timing["scenes"][-1]["start"] + timing["scenes"][-1]["duration"]
    starts = sorted({round(s["start"], 2) for s in timing["scenes"]} | {0.0})
    want = [total * i / parts for i in range(1, parts)]
    bounds = [0.0] + sorted({min(starts, key=lambda s: abs(s - w)) for w in want} - {0.0}) + [round(total, 2)]
    return list(zip(bounds, bounds[1:]))


def event_times(vid, timing):
    """사건 시각: keys.py가 남긴 표의 줄 시각, 없으면 문장마다 시작·가운데."""
    p = vid / ".harness" / "check-times.json"
    if p.exists():
        return sorted(set(json.loads(p.read_text(encoding="utf-8"))["times"]))
    out = []
    for sc in timing["scenes"]:
        for s in sc.get("sentences", []):
            out += [s["start"] + 0.05, (s["start"] + s["end"]) / 2]
    return sorted({round(t, 2) for t in out})


def split(times, parts):
    """시각들을 parts 묶음으로(이어진 시각끼리, 개수가 비슷하게)."""
    n = max(1, min(parts, len(times)))
    size = -(-len(times) // n)
    return [times[i:i + size] for i in range(0, len(times), size)]


def supported(cli, vid):
    """그 CLI의 check가 아는 옵션 이름들."""
    cmd = ["npm.cmd" if sys.platform == "win32" else "npm", "run", "check", "--", "--help"] if cli == "pinned" else \
        ["npx.cmd" if sys.platform == "win32" else "npx", "--yes", cli, "check", "--help"]
    text = subprocess.run(cmd, cwd=vid, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    return set(re.findall(r"(--[a-z][a-z-]*)", text))


def keep_known(args, known):
    """(그 CLI가 아는 옵션만, 뺀 옵션). 옵션은 "--이름" 또는 "--이름=값" 한 덩어리."""
    out = [x for x in args if x.split("=")[0] in known]
    return out, [x for x in args if x not in out]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--parts", type=int, default=None)
    ap.add_argument("--full", action="store_true", help="렌더 직전 전체 검사(구간마다 대비·craft)")
    ap.add_argument("--light", action="store_true", help="(예전 이름) 기본과 같다")
    ap.add_argument("--range", action="append", default=[])
    ap.add_argument("--cli", default=CHECK_CLI)
    ap.add_argument("extra", nargs="*")
    a = ap.parse_args()
    vid = Path(a.video).resolve()
    timing = json.loads((vid / "narration" / "timing.json").read_text(encoding="utf-8"))
    ranges = [tuple(float(x) for x in r.split(",")) for r in a.range]
    if a.parts is None:
        a.parts = PARTS if ranges else WHOLE_PARTS
    if a.full:
        jobs = [(f"{lo:g}-{hi:g}", ["--range", f"{lo},{hi}"]) for lo, hi in (ranges or cut(timing, a.parts))]
        base = FULL
    else:
        times = event_times(vid, timing)
        if ranges:
            times = [t for t in times if any(lo <= t <= hi for lo, hi in ranges)]
        if not times:
            raise SystemExit("볼 사건 시각이 없다(--range를 넓히거나 --full)")
        jobs = [(f"at{g[0]:g}-{g[-1]:g}", ["--at", ",".join(f"{t:g}" for t in g)]) for g in split(times, a.parts)]
        base = LIGHT
    known = supported(a.cli, vid)
    base, dropped = keep_known(base, known) if known else (base, [])
    if dropped:
        print(f"{a.cli}가 모르는 옵션은 뺐다: {' '.join(dropped)}")
    logdir = vid / ".harness" / "check"
    logdir.mkdir(parents=True, exist_ok=True)
    if a.cli == "pinned":
        head = ["npm.cmd" if sys.platform == "win32" else "npm", "run", "check", "--"]
    else:
        head = ["npx.cmd" if sys.platform == "win32" else "npx", "--yes", a.cli, "check"]
    procs = []
    for name, sel in jobs:
        args = head + sel + base + a.extra
        log = logdir / f"{name}.log"
        procs.append((name, log, subprocess.Popen(args, cwd=vid, stdout=log.open("w", encoding="utf-8"),
                                                  stderr=subprocess.STDOUT)))
        print(f"시작 {name} -> {log.relative_to(vid)}", flush=True)
    bad = 0
    for name, log, p in procs:
        code = p.wait()
        text = log.read_text(encoding="utf-8", errors="replace")
        hits = [ln.strip() for ln in text.splitlines() if re.search(r"\b(error|errors|warning|warn|fail)", ln, re.I)]
        print(f"\n== {name}  종료 {code}")
        for ln in hits[:30]:
            print("  ", ln)
        bad |= code != 0
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
