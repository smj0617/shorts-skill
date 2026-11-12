# 도구 스킬 — 흐름이 부르는 자리

흐름 파일(grill, make, complete)이 이 파일을 가리키는 자리에서만 읽는다. 스킬마다 부르는 자리와 쓰는 범위를 적는다.

## HyperFrames 공식 스킬

HyperFrames 공식 스킬(`npx hyperframes skills update`로 설치·갱신)은 아래 자리에서 Skill 도구로 부른다. 한 세션에서 한 번 부른 스킬은 다시 부르지 않는다. 순서, 승인, 그림 방식, 소리 기준은 쇼츠 스킬과 `docs/agents/shorts-defaults.md`를 따른다. HyperFrames 스킬에서는 컴포지션 규칙과 CLI 사용법만 가져오고, 그 스킬의 작업 순서(기획·스토리보드 절차)는 따르지 않는다.

| 스킬 | 부르는 자리 | 쓰는 것 |
|---|---|---|
| `hyperframes` | make.md M2 4 애니메틱 만들기 전, M3 시작 (레이어 에이전트 브리프에도 "먼저 부를 것") | 렌더 계약(`window.__timelines`, `data-*`, seek에 안전한 움직임). 자막은 그 스킬의 `references/captions.md`, 소리 배치는 `references/sound.md`만 필요할 때 Read 한다 |
| `hyperframes-cli` | M2 4의 snapshot 전, complete.md C1 시작 | `snapshot`·`preview`·`check`·`render` 옵션과 렌더 실패 복구. 렌더는 영상 `package.json`에 고정된 버전으로 돌리고, 옵션이 스킬 설명과 다르면 `npx --yes hyperframes@<고정 버전> <명령> --help`가 기준이다 |
| `hyperframes-registry` | M3 3에서 표·생성 스크립트로 안 되는 이름 붙은 효과(전환, 필름 그레인 등)를 손 스크립트로 만들기 전 | 이미 있는 블록을 찾아 쓴다. 낙서 그림과 화면 글자는 늘 쓰던 생성 스크립트로 만든다 |
| `media-use` | 효과음이 필요할 때만 | 무료 출처(내장 효과음, Openverse CC BY는 출처 표기)만 쓴다. 나레이션은 Gemini TTS, 곡은 곡 목록·보관함 클래식, 그림은 코드 낙서 그대로 둔다. HeyGen 로그인과 유료 크레딧은 쓰지 않는다 |
| `reverse-any-video`, `style-sampling` | 사용자가 참고 영상이나 스타일을 주며 "이것처럼"이라고 할 때만 | 그 영상의 구성·움직임을 뽑아 기획안 연출 칸에 반영한다 |

## claude.ai 플러그인 스킬

같은 방식으로 부른다. Skill 목록에서는 이름 앞에 플러그인 id가 붙으므로(`<id>:anidoodle`) 끝 이름으로 찾는다. 목록에 없으면 건너뛰고 늘 하던 대로 한다.

| 스킬 | 부르는 자리 | 쓰는 것 |
|---|---|---|
| `anidoodle` | make.md M1 2, 모음에 없는 사물을 새로 그리기 전 | 코드 낙서로 사물의 모양과 획 순서를 빨리 잡는다. 결과는 늘 쓰던 낙서 설명(`<영상>/doodles/<id>.json`)으로 옮기고, 종이·펜·색은 `doodles/rules.md`를 따른다. 그 스킬의 31가지 스타일이나 곡 만들기는 쓰지 않는다 |
| `streamline-expert` (Streamline Icons) | M1 2, anidoodle과 같은 자리 | 사물의 뼈대 모양을 오픈소스 세트(Lucide, Heroicons, Phosphor, Font Awesome Free)에서만 가져와 낙서 획으로 다시 그린다. Streamline 유료 세트와 아이콘 그대로 붙이기는 쓰지 않는다 |
| `watch-video` | complete.md C1 6, 그릴링에서 사용자가 참고 영상을 줄 때 | 렌더한 영상이나 참고 영상의 말을 받아 적고 프레임을 뽑는다. 받아 적기는 로컬 faster-whisper만 쓰고, Groq·OpenAI 같은 호스팅 쪽은 쓰지 않는다 |
