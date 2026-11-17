import tempfile
import unittest
from pathlib import Path

import active


class ActiveTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def spec(self, name):
        return (self.root / ".scratch" / name / "spec.md").read_text(encoding="utf-8")

    def test_nothing_in_progress(self):
        self.assertIsNone(active.show(self.root))

    def test_start_records_first_stage_in_state_and_spec(self):
        active.start(self.root, "cache-shorts")
        self.assertEqual(active.show(self.root), {"name": "cache-shorts", "stage": 1, "stage_name": "기획"})
        self.assertEqual(self.spec("cache-shorts").splitlines()[0], "Stage: 1. 기획")

    def test_stage_by_name_or_number_rewrites_only_the_stage_line(self):
        active.start(self.root, "cache-shorts")
        spec = self.root / ".scratch" / "cache-shorts" / "spec.md"
        spec.write_text("Stage: 1. 기획\n\n# 캐시\n\n## 기획안\n\n남길 문장: 캐시는 빠르다.\n", encoding="utf-8")
        active.set_stage(self.root, "기획안 승인 대기")
        self.assertEqual(self.spec("cache-shorts"), "Stage: 2. 기획안 승인 대기\n\n# 캐시\n\n## 기획안\n\n남길 문장: 캐시는 빠르다.\n")
        active.set_stage(self.root, 9)
        self.assertEqual(active.show(self.root)["stage_name"], "썸네일")
        self.assertEqual(self.spec("cache-shorts").splitlines()[0], "Stage: 9. 썸네일")

    def test_unknown_stage_changes_nothing(self):
        active.start(self.root, "cache-shorts")
        for bad in ("기획안 승인", 0, 11):
            with self.assertRaises(active.ActiveError):
                active.set_stage(self.root, bad)
        self.assertEqual(active.show(self.root)["stage"], 1)

    def test_stage_without_active_short_fails(self):
        with self.assertRaises(active.ActiveError):
            active.set_stage(self.root, "제작")

    def test_second_short_waits_until_first_is_held(self):
        active.start(self.root, "cache-shorts")
        with self.assertRaises(active.ActiveError):
            active.start(self.root, "jwt-shorts")
        self.assertEqual(active.show(self.root)["name"], "cache-shorts")

    def test_held_short_resumes_at_its_spec_stage(self):
        active.start(self.root, "cache-shorts")
        active.set_stage(self.root, "제작")
        active.hold(self.root)
        self.assertIsNone(active.show(self.root))
        self.assertEqual(active.held(self.root), ["cache-shorts"])
        active.start(self.root, "jwt-shorts")
        active.hold(self.root)
        active.start(self.root, "cache-shorts")
        self.assertEqual(active.show(self.root), {"name": "cache-shorts", "stage": 5, "stage_name": "제작"})
        self.assertEqual(active.held(self.root), ["jwt-shorts"])

    def test_published_short_makes_room_for_a_new_one(self):
        active.start(self.root, "cache-shorts")
        active.set_stage(self.root, "게시 완료")
        active.start(self.root, "jwt-shorts")
        self.assertEqual(active.show(self.root)["name"], "jwt-shorts")
        self.assertEqual(active.held(self.root), [])
        self.assertEqual(self.spec("cache-shorts").splitlines()[0], "Stage: 10. 게시 완료")

    def test_parallel_start_joins_without_stopping_the_active_one(self):
        active.start(self.root, "xss-1-shorts")
        with self.assertRaises(active.ActiveError):
            active.start(self.root, "xss-2-shorts")
        active.start(self.root, "xss-2-shorts", parallel=True)
        self.assertEqual(active.show(self.root)["name"], "xss-1-shorts")
        self.assertEqual(active.parallel(self.root), [{"name": "xss-2-shorts", "stage": 1, "stage_name": "기획"}])
        self.assertEqual(self.spec("xss-2-shorts").splitlines()[0], "Stage: 1. 기획")

    def test_parallel_start_keeps_the_stage_already_in_the_spec(self):
        spec = self.root / ".scratch" / "xss-3-shorts" / "spec.md"
        spec.parent.mkdir(parents=True)
        spec.write_text("Stage: 3. 곡 받기와 녹음\n\n# XSS 3\n", encoding="utf-8")
        active.start(self.root, "xss-3-shorts", parallel=True)
        self.assertEqual(active.show(self.root, "xss-3-shorts")["stage"], 3)
        self.assertEqual(self.spec("xss-3-shorts"), "Stage: 3. 곡 받기와 녹음\n\n# XSS 3\n")

    def test_stage_with_video_changes_only_that_video(self):
        active.start(self.root, "xss-1-shorts")
        active.start(self.root, "xss-2-shorts", parallel=True)
        active.start(self.root, "xss-3-shorts", parallel=True)
        active.set_stage(self.root, "제작", video="xss-2-shorts")
        active.set_stage(self.root, 2, video="xss-1-shorts")
        self.assertEqual(active.show(self.root, "xss-1-shorts")["stage"], 2)
        self.assertEqual(active.show(self.root, "xss-2-shorts")["stage"], 5)
        self.assertEqual(active.show(self.root, "xss-3-shorts")["stage"], 1)
        self.assertEqual(self.spec("xss-2-shorts").splitlines()[0], "Stage: 5. 제작")
        self.assertEqual(self.spec("xss-3-shorts").splitlines()[0], "Stage: 1. 기획")
        self.assertIsNone(active.show(self.root, "xss-9-shorts"))
        with self.assertRaises(active.ActiveError):
            active.set_stage(self.root, 2, video="xss-9-shorts")

    def test_hold_with_video_moves_only_that_video_and_start_resumes_it(self):
        active.start(self.root, "xss-1-shorts")
        active.start(self.root, "xss-2-shorts", parallel=True)
        active.set_stage(self.root, 4, video="xss-2-shorts")
        active.hold(self.root, video="xss-2-shorts")
        self.assertEqual(active.parallel(self.root), [])
        self.assertEqual(active.held(self.root), ["xss-2-shorts"])
        self.assertEqual(active.show(self.root)["name"], "xss-1-shorts")
        active.start(self.root, "xss-2-shorts", parallel=True)
        self.assertEqual(active.show(self.root, "xss-2-shorts")["stage"], 4)
        self.assertEqual(active.held(self.root), [])

    def test_published_parallel_short_stays_until_the_next_parallel_start(self):
        active.start(self.root, "xss-2-shorts", parallel=True)
        active.set_stage(self.root, "게시 완료", video="xss-2-shorts")
        self.assertEqual(active.show(self.root, "xss-2-shorts")["stage_name"], "게시 완료")
        active.start(self.root, "xss-3-shorts", parallel=True)
        self.assertEqual([e["name"] for e in active.parallel(self.root)], ["xss-3-shorts"])
        self.assertEqual(active.spec_stage(self.root, "xss-2-shorts")["stage"], 10)

    def test_old_state_file_without_parallel_list_still_works(self):
        state = self.root / ".scratch" / "shorts-active.json"
        state.parent.mkdir(parents=True)
        state.write_text('{"active": {"name": "xss-1-shorts", "stage": 1}, "held": []}', encoding="utf-8")
        active.start(self.root, "xss-2-shorts", parallel=True)
        self.assertEqual(active.show(self.root)["name"], "xss-1-shorts")
        self.assertEqual(len(active.parallel(self.root)), 1)

    def test_sessions_changing_at_once_lose_no_video(self):
        import threading
        names = [f"xss-{i}-shorts" for i in range(1, 7)]

        def session(name):
            active.start(self.root, name, parallel=True)
            for stage in range(2, 7):
                active.set_stage(self.root, stage, video=name)

        threads = [threading.Thread(target=session, args=(n,)) for n in names]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(sorted((e["name"], e["stage"]) for e in active.parallel(self.root)), [(n, 6) for n in names])
        self.assertFalse((self.root / ".scratch" / "shorts-active.lock").exists())
        self.assertEqual(list((self.root / ".scratch").glob("*.tmp")), [])

    def test_cli_show_lists_active_parallel_and_held(self):
        import contextlib
        import io
        active.start(self.root, "xss-1-shorts")
        active.start(self.root, "xss-2-shorts", parallel=True)
        out = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
        old = active.ROOT
        active.ROOT = self.root
        try:
            with contextlib.redirect_stdout(out):
                active.main(["stage", "3", "--video", "xss-2-shorts"])
                active.main(["show"])
                active.main(["show", "--video", "xss-2-shorts"])
        finally:
            active.ROOT = old
        out.flush()
        self.assertEqual(out.buffer.getvalue().decode("utf-8").splitlines(), [
            "xss-1-shorts: 1. 기획",
            "동시 진행: xss-2-shorts: 3. 곡 받기와 녹음",
            "보류: 없음",
            "xss-2-shorts: 3. 곡 받기와 녹음",
        ])


if __name__ == "__main__":
    unittest.main()
