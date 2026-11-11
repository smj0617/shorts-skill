"""시나리오 점검용 가짜 유튜브 클라이언트. 실제 유튜브에 아무것도 보내지 않는다.

점검용 프로젝트 사본에서만 publish/youtube_client.py로 복사해 쓴다(scenarios.md "준비").
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
LOG = HERE / "fake-calls.log"            # 받은 요청을 한 줄씩 남긴다
FAIL_THUMB_ONCE = HERE / "fail-thumb-once"  # 이 파일이 있으면 썸네일을 한 번 실패시키고 지운다


class _Fake:
    def _log(self, line):
        with LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def upload(self, video_path, body):
        # 첫 업로드는 FAKE123, 그 뒤는 FAKE124, FAKE125…(연작의 편마다 게시 목록 줄이 따로 생기게)
        lines = LOG.read_text(encoding="utf-8").splitlines() if LOG.exists() else []
        done = sum(line.startswith("upload ") for line in lines)
        self._log("upload " + json.dumps(body, ensure_ascii=False))
        return f"FAKE{123 + done}"

    def processing_status(self, video_id):
        return "succeeded"

    def set_thumbnail(self, video_id, image_path):
        self._log(f"thumbnail {video_id}")
        if FAIL_THUMB_ONCE.exists():
            FAIL_THUMB_ONCE.unlink()
            raise RuntimeError("가짜 썸네일 오류")

    def set_status(self, video_id, status):
        self._log(f"status {video_id} " + json.dumps(status, ensure_ascii=False))


def make_client():
    return _Fake()
