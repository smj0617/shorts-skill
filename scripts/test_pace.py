"""제작 속도 장부(pace.py) 테스트.

    cd .claude/skills/shorts/scripts && python -m unittest test_pace -v
"""
import json
import tempfile
import unittest
from pathlib import Path

import pace


class PaceTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.root = Path(self.d.name)
        (self.root / ".scratch").mkdir()
        (self.root / ".scratch" / "shorts-active.json").write_text(
            json.dumps({"active": {"name": "demo-shorts", "stage": 5}, "held": []}), encoding="utf-8")

    def tearDown(self):
        self.d.cleanup()

    def test_any_step_over_five_minutes_says_what_to_switch_to(self):
        pace.start("need 클로즈업 의견", "의견", self.root, now=0)
        pace.end("", self.root, now=4 * 60)
        self.assertEqual(pace.check(self.root, now=4 * 60), [])          # 4분: 기준 안
        pace.start("scene-b 레이어", "레이어", self.root, now=300)
        pace.end("", self.root, now=300 + 6 * 60)
        bad = pace.check(self.root, now=1000)
        self.assertEqual(len(bad), 1)
        self.assertIn("기준 5분", bad[0])
        self.assertIn("keys.py로 표의 무대를", bad[0])

    def test_an_open_step_is_measured_until_now(self):
        pace.start("전체 검사", "검사", self.root, now=0)
        self.assertEqual(pace.check(self.root, now=60), [])
        self.assertIn("(진행 중)", pace.check(self.root, now=6 * 60)[0])

    def test_alarm_fires_at_five_minutes_and_stays_quiet_when_the_step_ends(self):
        pace.start("렌더", "렌더", self.root, now=0)
        clock = iter([60, 200, 301, 400])
        msg = pace.alarm(self.root, clock=lambda: next(clock), sleep=lambda s: None)
        self.assertIn("5.0분째", msg)
        self.assertIn("백그라운드", msg)
        pace.end("", self.root, now=320)
        pace.start("의견 하나", "의견", self.root, now=330)

        def sleep(_):
            pace.end("", self.root, now=340)
        self.assertIsNone(pace.alarm(self.root, clock=lambda: 335, sleep=sleep))

    def test_the_third_redo_asks_the_watcher(self):
        for i in range(3):
            pace.start("scene-a 다시 만들기", "레이어", self.root, now=i * 10)
            pace.end("", self.root, now=i * 10 + 5)
        self.assertTrue(any("pace-watcher" in ln for ln in pace.check(self.root, now=100)))

    def test_report_shows_stage_times_against_the_hour(self):
        pace.start("레이어 전부", "에이전트", self.root, now=0)
        pace.end("", self.root, now=16 * 60)
        self.assertIn("5단계  16.0분 / 목표 15분", " | ".join(pace.report(self.root, now=16 * 60)))
        self.assertEqual(sum(pace.STAGE_BUDGET.values()), pace.TOTAL)

    def test_unknown_kind_and_nothing_to_end(self):
        with self.assertRaises(pace.PaceError) as e:
            pace.start("x", "잡일", self.root)
        self.assertIn("의견", str(e.exception))
        with self.assertRaises(pace.PaceError):
            pace.end("", self.root)


if __name__ == "__main__":
    unittest.main()
