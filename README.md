# /shorts — 주제 한 줄로 만드는 개발 개념 쇼츠

코드일지 유튜브 채널의 개발 개념 쇼츠를 [Claude Code](https://claude.com/claude-code) 스킬 하나로 만든다. 주제 한 줄을 주면 묻고(그릴링) → 기획안 → 녹음과 낙서 → 미리보기 → 렌더 → 업로드까지 이어 가고, 사용자는 기획안과 미리보기, 게시 정보만 승인한다.

## 무엇을 담나

- 영상은 지식이 아니라 **'왜'** 하나를 담는다. 기술 이름이 나오기 전에, 그 기술이 없을 때의 불편을 누구나 겪어 본 일상 장면으로 먼저 보여 준다. 코드는 쓰지 않는다.
- 한 편은 **30초 내외**, 다섯 박자(훅 → 불편 → 해결 → 이름 붙이기 → 남길 문장)다.
- 더 담을 것이 있는 주제는 **연작**으로 나눈다: 1편 왜 있나, 2편 실제 쓰임의 판단, 3편 함정이 생기는 까닭. 연작은 다 만든 뒤 한 번에 올려, 1편은 바로 공개하고 뒤 편은 하루씩 18:00에 예약한다.
- 그림은 SVG 펜 낙서, 나레이션은 Gemini TTS, 영상은 [HyperFrames](https://github.com/heygen-com/hyperframes) 컴포지션이다.

## 사용법

| 명령 | 하는 일 |
|---|---|
| `/shorts <주제>` | 새 쇼츠(또는 연작의 다음 편) 시작 |
| `/shorts` | 진행 상태 보기 |
| `/shorts complete` | 최종 검수·렌더·게시 정보 승인·업로드 |
| `/shorts review` | 제작 회고와 7일 뒤 눈길 지표 회고 |

## 폴더

| 경로 | 내용 |
|---|---|
| `SKILL.md` | 진입점: 분기, 단계 열 개, 그릴링 역할, 성장 고리, 모든 흐름에 걸리는 규칙 |
| `flows/` | 흐름별 절차: 시작(start), 그릴링(grill), 제작(make), 완성과 게시(complete), 회고(review), 상태(status) |
| `references/` | 영상마다 자라는 출발점: 교훈 요약(summary), 영상별 회고(history), 캐릭터(character) |
| `scripts/` | 상태 기록 도우미(active), 속도 감시(pace), 구간 병렬 검사(check_parallel)와 테스트 |
| `evals/` | 손으로 돌리는 흐름 시나리오와 평가용 가짜 유튜브 클라이언트 |

## 이 스킬이 기대는 것 (이 저장소에는 없음)

스킬은 작업 폴더(video1)의 아래 파일과 함께 돌아간다. 여기에는 스킬만 올렸다.

- 제작 기본값 `docs/agents/shorts-defaults.md`, 용어집 `GLOSSARY.md`, 결정 기록 `docs/adr/`
- 게시 명령 `publish/`(YouTube Data API, 비공개로 올린 뒤 공개·예약), 게시 목록 `published.md`
- 영상 템플릿 `shorts-template/`, 낙서 도구와 규칙 `doodles/`, 곡 목록과 도구 `music/`
- 상태와 명세 `.scratch/`
- HyperFrames 공식 스킬(`hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `media-use` 등): `npx hyperframes skills update`로 설치한다. 부르는 자리는 `SKILL.md` "HyperFrames 스킬"

## 자라는 방식

영상마다 의견과 결정을 원본 기록에 쌓고, 게시와 회고 때 출발점(`references/`)으로 추리고, 두 영상에서 되풀이되면 규칙 문서로 올린다(`SKILL.md` "성장 고리").
