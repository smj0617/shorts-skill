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


if __name__ == "__main__":
    unittest.main()
