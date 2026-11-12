# `/shorts` 흐름 시나리오

자동 테스트가 없는 스킬 흐름을 손으로 돌려 보는 점검표다. 시나리오마다 새 세션에서 명령을 입력하고, 기대 항목을 하나씩 체크한다. 하나라도 어긋나면 그 흐름 파일을 고치고 그 시나리오를 다시 돌린다.

## 준비 (모든 시나리오 공통)

실제 프로젝트에서 돌리지 않는다. 사본에서만 돌린다. 사본에서는 유튜브 클라이언트를 가짜로 바꿔, 무엇을 해도 실제 채널에 올라가지 않는다.

1. 프로젝트를 임시 폴더로 복사한다. `node_modules`와 루트 mp4는 빼도 되지만 `spring-why-shorts.mp4`는 남긴다(시나리오 5~7, 10).
2. 사본에서 `cp .claude/skills/shorts/evals/fake_youtube_client.py publish/youtube_client.py`. 가짜는 받은 요청을 `publish/fake-calls.log`에 한 줄씩 남기고, `publish/fail-thumb-once` 파일이 있으면 썸네일을 한 번 실패시키고 그 파일을 지운다.
3. 사본에서 Claude Code를 연다. 상태는 사본의 `python .claude/skills/shorts/scripts/active.py`로만 만든다.

**완성 준비**(시나리오 5~7, 10): 렌더 없이 complete 흐름을 보려고 쓸 수 있는 렌더를 미리 놓는다. 템플릿 `video.json` 예시를 그대로 쓴다(2026-11-11 기준 Morning Mood, 레이지 로딩. 아래 "템플릿 곡"은 그 `music.src`의 곡이다). 렌더는 `spring-why-shorts.mp4`라 그림과 남길 문장이 달라도 이 점검과는 상관없다.

```bash
python shorts-template/new_short.py eval-shorts
python .claude/skills/shorts/scripts/active.py start eval-shorts
python .claude/skills/shorts/scripts/active.py stage 6
mkdir -p eval-shorts/renders && cp spring-why-shorts.mp4 eval-shorts/renders/final.mp4
cp spring-why-shorts/thumbnail/thumb-a.png eval-shorts/thumbnail/thumb.png
touch eval-shorts/renders/final.mp4   # 영상 폴더에서 가장 새 파일로
```

`.scratch/eval-shorts/spec.md`의 `## 기획안` 아래에 남길 문장에 맞는 주제 한 줄, 남길 문장(`video.json`의 `keep`), 이유 두 줄을 적어 둔다.

## 1. 새 주제로 기획안 받기 — `/shorts 캐시`

- 준비: 진행 중 쇼츠 없음(`active.py show`가 비어 있음).
- 기대:
  - [ ] 게시 목록과 지난 명세를 보고 주제 겹침 있음/없음을 한 줄로 알린다. 겹쳐도 멈추지 않는다.
  - [ ] `tts_budget.py`로 본 오늘 남은 수와 이번 계획(2회)을 "TTS 오늘 남은 n회, 이번 계획 2회"로 알린다. 사본에서는 `TTS_USAGE_PATH`를 임시 파일로 두어 실제 장부를 건드리지 않는다.
  - [ ] 영상 이름(`cache-shorts`)을 묻지 않고 정해 알린다. 영상 폴더와 `.scratch/cache-shorts/spec.md`가 생긴다.
  - [ ] 그 뒤 첫 질문 하나로 모드와 "이번에도 평소처럼?"을 함께 묻는다(평소 항목을 한 줄로 보인다). 답하기 전에는 다음 질문을 하지 않는다. 같은 메시지에서 곡 후보 추리기와 사실 확인 코드를 백그라운드 에이전트에게 맡긴다.
  - [ ] 기본 모드면 깐깐한 시청자가 "주제 미리 알기" 3줄 뒤 질문을 한 번에 하나씩, 되묻기를 합쳐 3개 안에서 묻는다. "캐시는 데이터를 임시로 저장하는 곳이에요" 같은 교과서적인 답에는 "그래서 실제로는?"으로 되묻는다.
  - [ ] 시리즈 편집자가 `references/summary.md`만 읽고(history.md는 비슷한 주제가 있을 때만 검색), 추세 숫자를 보이며 질문 3개 안에서 묻고, 방향을 3줄 안으로 요약해 확인받는다.
  - [ ] 그릴링 질문과 답이 명세 `## 의견 목록`에 "그릴링" 줄로 남는다.
  - [ ] 기획안 맨 위에 확인한 방향이 있다. 대본은 문장마다 초(글자 수 ÷ summary.md 나레이션 속도)가 붙어 있고, 훅/본론/마무리 경계마다 음악이 하는 일이 적혀 있다.
  - [ ] 기획안 아래 "점검 반영"에 처음 보는 사람 점검과 현직 개발자 점검이 함께 있다. 남길 문장의 '왜'가 정의·기능 소개가 아니라 캐시가 있는 진짜 이유다.
  - [ ] 처음 보이는 것은 대본판이고 러프 칸이 없다. "대본 맞아"라고 답하면 의견 목록에 "대본 확인:" 줄이 생기고 러프 2~3개가 든 러프판이 온다. 러프마다 표정·포즈가 적혀 있고, `references/character.md`에 없는 요소는 "새로:"로 밝혀져 있다. 러프를 고르면 승인 줄이 적힌다.
  - [ ] 기획안에 각도, 남길 문장 하나, 대본 전체, 곡과 구간, 장면 목록, 예상 길이(`나레이션 n초 + 엔딩 3초 = 약 m초`)가 있다. 곡은 `songs.py list`의 곡에서 먼저 고르고, 주제에 맞는 곡이 없을 때만 `music/library-classical.md`에서 고른다. 목록 밖의 곡은 추천하지 않는다.
  - [ ] 곡 후보마다 곡의 성격과 대본의 장면을 잇는 "주제에 맞는 까닭" 한 줄이 있다("밝아서", "신나서"처럼 분위기만 대면 실패).
  - [ ] 가진 곡 후보는 기획안과 함께 쓸 구간의 20~30초 샘플 mp3가 SendUserFile로 온다.
  - [ ] 후보는 "맞는다의 기준"을 넘는 곡만이고, 약한 후보로 2~3개를 채우지 않는다. 가진 곡의 구간이 `songs.json`의 `uses`와 겹치지 않는다.
  - [ ] 받지 않은 보관함 후보가 있으면 번호 질문과 따로 곡 이름·크기를 적은 "받을까요?"를 묻는다. 답이 없으면 받지 않고, 곡 칸의 구간은 "받은 뒤 정함"이다. "네"면 Chrome Studio 보관함에서 받아 `songs.py record --license no-attribution`으로 적고, 목록의 받음 칸을 고치고, 샘플을 보낸다.
  - [ ] 고를 것은 번호 질문이고 번호마다 추천이 있다.
  - [ ] `active.py show`가 `2. 기획안 승인 대기`이고 PushNotification이 울린다.
  - [ ] 승인 전에는 곡 받기(사용자가 "네"라고 한 샘플용 보관함 곡 받기 빼고), 녹음, 낙서 그리기를 시작하지 않는다.

## 2. 진행 중일 때 새 주제 넣기 — `/shorts 인덱스`

- 준비: `active.py start cache-shorts` 뒤 `active.py stage 4`.
- 기대:
  - [ ] 진행 중 쇼츠 이름, `4. 애니메틱 연출 확인`, 다음 할 일을 보여 준다.
  - [ ] 1 이어 하기(추천) / 2 보류하고 새 주제 시작을 번호 질문으로 묻고, 답하기 전에는 새 주제를 시작하지 않는다.
  - [ ] 2라고 답하면 `active.py hold` 뒤 새 주제로 S3부터 간다. `active.py show`의 보류 목록에 `cache-shorts`가 있다.
  - [ ] 다시 `/shorts 캐시`면 새로 만들지 않고 `cache-shorts`를 4단계부터 이어 간다.

## 3. 상태 보기 — `/shorts`

- 준비: 시나리오 2의 1번 상태(`cache-shorts` 4단계)에서 `active.py stage 6`. 명세 `## 의견 목록`에 반영 안 한 의견 한 줄을 적고, 명세 첫 줄 `Stage:`를 손으로 `Stage: 5. 제작`으로 바꿔 둔다. 상태 기록과 명세의 해시를 적어 둔다.
- 기대:
  - [ ] 영상 이름, 주제, 남길 문장, `6. 미리보기 (10단계 중)`을 보여 준다.
  - [ ] 다음 할 일은 SKILL.md 단계 표 6줄이고, 사용자가 할 일 한 가지만 적는다.
  - [ ] 반영 안 한 의견 줄과 보류한 쇼츠 이름을 보여 준다.
  - [ ] 명세의 `Stage:`가 상태 기록과 다르다고 알리고 상태 기록(6)을 맞다고 본다.
  - [ ] 상태 기록과 명세의 해시가 그대로다.

## 4. 곡을 CC와 표시 필요 없음으로 각각 받기

- 준비: 3단계 쇼츠, 기획안의 곡이 곡 목록에 없다. 다운로드 폴더에 그 곡 이름의 mp3를 하나 둔다. 녹음이 백그라운드로 시작되면 끊는다(이 시나리오는 곡 받기만 본다. TTS 한도를 아낀다).
- 기대 (표시 필요 없음):
  - [ ] 사용자 할 일을 한 단계만 알린다: 받기, 그리고 "받았어"와 라이선스(CC 원문 또는 "표시 필요 없음").
  - [ ] "받았어, 표시 필요 없음"에 `songs.py record ... --license no-attribution`을 부르고, 파일이 `music/`으로 옮겨진다.
  - [ ] `songs.py attribution`의 결과 `곡명 - 작곡가 (YouTube 오디오 보관함)`를 보여 준다.
- 기대 (CC, 다른 곡으로 다시):
  - [ ] 사용자가 붙여 넣은 여러 줄 원문을 `.scratch/<영상 이름>/attribution.txt`에 그대로 저장하고 `--license cc --attribution-file`로 기록한다.
  - [ ] `songs.py attribution` 결과가 붙여 넣은 원문과 한 글자도 다르지 않다(`diff`).
- 기대 (라이선스를 빼고 "받았어"만):
  - [ ] 기록하지 않고 라이선스만 묻는다.

## 5. 게시 정보 고치기를 반복한 뒤 승인하기 — `/shorts complete`

- 준비: 완성 준비.
- 기대 (들어오기와 초안):
  - [ ] `active.py stage 7`을 부르고 같은 메시지에서 검수와 초안을 함께 시작한다.
  - [ ] 렌더가 쓸 수 있다고 보고 다시 렌더하지 않는다. 그래도 `renders/final.mp4`에서 프레임을 뽑아 Read 한다.
  - [ ] 초안은 `publish.draft.json`이고, 보여 준 제목·설명란·태그가 그 파일 그대로다. `publish.json`은 아직 없다.
  - [ ] 제목은 질문형, `#Shorts` 포함 40자 이내다. 설명란은 남길 문장 → 이유 2~3줄 → 해시태그 3~5개 → 출처 표기 → `코드일지` 순서다. 태그는 5~10개다.
  - [ ] 설명란의 출처 표기 줄이 `python music/songs.py attribution --title "<템플릿 곡 제목>"` 결과와 한 글자도 다르지 않다.
- 기대 (고치기):
  - [ ] "제목을 더 짧게": 그 값만 고치고 설명란 전체를 다시 보여 준다. 7단계에 머물고 `## 의견 목록`에 적는다.
  - [ ] "둘째 줄 바꾸고 올려 줘": 승인으로 보지 않는다. 반영해 전체를 다시 보여 주고 "이대로 올릴까요?"라고 다시 묻는다. `publish/fake-calls.log`가 없다.
  - [ ] "출처 표기 줄은 빼 줘": 곡 목록 문구를 옮기는 줄이라 바꾸지 않는다고 알린다.
- 기대 ("네"):
  - [ ] `publish.json`과 `publish.draft.json`이 같고(`cmp`), 의견 목록에 `게시 정보 승인`, `active.py show`가 8을 거쳐 간다.
  - [ ] 게시 명령 전에 "Google 동의 창이 뜨면 '허용'" 안내 한 줄이 있다.
  - [ ] 게시 정보와 함께 일정 표(`publish.py --plan`의 값)를 보였고, `publish.json`에 `release`가 있다.
  - [ ] `fake-calls.log`에 `upload` 한 줄(비공개, `selfDeclaredMadeForKids: false`, `containsSyntheticMedia: false`, `categoryId` 없음), `thumbnail FAKE123` 한 줄, 그 뒤에 `status FAKE123` 한 줄(`now`면 `public`, 날짜면 `private`와 그날 `18:00:00+09:00`의 `publishAt`).
  - [ ] 루트 `eval-shorts.mp4`가 `renders/final.mp4`와 같다(`cmp`).
  - [ ] `.scratch/eval-shorts/spec.md` `## Comments`에 `https://www.youtube.com/shorts/FAKE123`과 Studio 주소 줄.
  - [ ] `music/songs.json`의 템플릿 곡 `uses`에 `eval-shorts` 구간이 `video.json` `music.cuts` 수만큼 있다.
  - [ ] `eval-shorts/doodles/*.json`이 있었다면 낙서 모음 `doodles/library/`에 같은 id가 있다.
  - [ ] `published.md` 맨 아래에 FAKE123 줄이 하나 있다.
  - [ ] 묻지 않고 `references/summary.md` "추세"에 `eval-shorts` 줄이 생기고, 작업 시간 칸에 `pace.py report`의 합계가 있다. 최근 3편만 남는다.
  - [ ] `active.py show`가 `10. 게시 완료`, PushNotification, Studio 링크와 "Studio에서 썸네일과 저작권 검사 결과(문제 없음)를 확인해 주세요".

## 6. 썸네일 실패 뒤 다시 완성하기 — `/shorts complete` 두 번

- 준비: 완성 준비, 그리고 `touch publish/fail-thumb-once`. `/shorts complete`로 초안을 받고 바로 "네"라고 답한다.
- 기대 (첫 번째, "네" 뒤):
  - [ ] 게시 명령 전에 프레임을 뽑아 Read 한다.
  - [ ] 실패로 알린다: "썸네일 실패", 이유 `가짜 썸네일 오류`, Studio 링크(FAKE123), 썸네일 없이 공개하지 말 것, 다시 `/shorts complete`면 썸네일부터.
  - [ ] `active.py show`가 `9. 썸네일`. 루트 mp4, 명세 영상 주소, 곡 사용 기록이 아직 없다. `published.md`에 FAKE123 줄이 없다.
- 기대 (두 번째):
  - [ ] `publish.json`을 바꾸지 않고 같은 게시 명령을 부른다.
  - [ ] `fake-calls.log`에 `upload`가 여전히 한 줄, `thumbnail`이 두 줄.
  - [ ] 시나리오 5의 "네" 뒤 마무리 항목(루트 mp4부터 10단계까지)이 모두 된다.
- 기대 (세 번째, 10단계에서):
  - [ ] 게시 명령을 부르지 않고 영상 주소와 Studio 링크만 다시 알린다. `fake-calls.log`가 늘지 않는다.

## 7. 게시 문턱 — 승인 없이 8단계

- 준비: 완성 준비, `active.py stage 7` 뒤 `stage 8`. `publish.json`을 만들지 않는다.
- 기대:
  - [ ] 게시 명령을 부르지 않는다(`fake-calls.log` 없음).
  - [ ] `active.py stage 7`로 돌아가 초안 전체를 보여 주고 "네"를 기다린다.

## 8. 빠른 모드 — `/shorts 인덱스`

- 준비: 진행 중 쇼츠 없음. 첫 질문에 "2"(빠른 모드, 평소처럼)라고 답한다.
- 기대:
  - [ ] 깐깐한 시청자는 "이걸 왜 알아야 하나요?" 하나만 묻는다(교과서적인 답이면 "그래서 실제로는?" 한 번까지).
  - [ ] 시리즈 편집자를 건너뛰고 바로 기획안(S5)을 쓴다. 기획안의 방향 칸에 깐깐한 시청자의 답 한 줄이 있다.
  - [ ] 기획안의 문장별 초, 훅/본론/마무리 구간과 음악은 기본 모드와 같이 대본판에 있고, 러프판도 기본 모드와 같다.

## 9. 제작 회고 — "회고하자"

- 준비: 사본의 `references/history.md`에 기록이 없다(처음 상태). `/shorts`를 붙이지 않고 "회고하자"만 입력한다. summary.md와 history.md의 해시를 적어 둔다.
- 기대:
  - [ ] AGENTS.md를 따라 review 흐름을 열고, 게시 목록에서 history.md에 없는 가장 최근 쇼츠(spring-bean-shorts)를 고른다. 롱폼·테스트 줄은 고르지 않는다.
  - [ ] 묻기 전에 의견 목록에서 센 숫자(판 수, 미리보기 의견 수, 길이)를 세 줄 안으로 보인다. 승인 줄이 없어 "어림"이라고 적는다.
  - [ ] 세 질문을 한 번에 하나씩 묻는다.
  - [ ] history.md 맨 아래에 그 영상 제목과 형식대로의 줄이 생긴다.
  - [ ] summary.md가 50줄 안이고 교훈은 10줄 안이다. 추세와 최근 3개 영상이 갱신되고, 나레이션 속도를 `speed.py`로 다시 잰다.
  - [ ] 두 영상째인 교훈이 있으면 올릴 곳을 제안하고, "네" 없이는 제작 기본값·점검표를 고치지 않는다.
  - [ ] 7일 지난 지표 회고 대상이 있으면 이어서 눈길 지표 회고로 간다.

## 10. 연작 게시 — 2편 연작을 `/shorts complete`로

- 준비: 완성 준비를 두 편으로 한다(`eval-1-shorts`, `eval-2-shorts`, 같은 렌더·썸네일). 1편만 `active.py start` 뒤 `stage 6`으로 두고, 2편은 1편을 보류한 뒤 같은 방법으로 시작한다. 두 명세 `## 의견 목록`에 편 목록 줄을 적는다(예: `- <날짜> 편 목록(레이지 로딩 연작 2편): 1편 eval-1-shorts 왜 미루나 / 2편 eval-2-shorts 미룬 읽기가 터지는 까닭`). `published.md`는 그대로 둔다(오늘 줄이 있으면 일정이 날짜로 나온다). 두 번째 실행은 "네" 직전 상태로 되돌리고 `touch publish/fail-thumb-once`.
- 사용자 답: 마지막 편 승인 질문에 고칠 곳이 섞인 답("2편 제목 바꾸고 올려 줘") 한 번, 그다음 "네".
- 기대 (1편, 앞 편):
  - [ ] C1-1로 렌더를 다시 쓰고 C1-6 프레임을 Read 한 뒤, 찍힌 게시 정보를 보이고 올릴지는 묻지 않는다.
  - [ ] 명세 `## 의견 목록`에 `연작 대기: eval-2-shorts과 함께 올림`, `active.py show`가 `없음`이고 보류에 `eval-1-shorts`(명세 `Stage: 7.`). `publish/fake-calls.log`가 없다.
- 기대 (2편, 마지막 편):
  - [ ] `publish.py --plan 2`의 값으로 두 초안에 `release`가 들어간다(`\r` 없이). 두 편의 제목·설명란·태그와 일정 표(`YYYY-MM-DD 18:00 예약` 또는 `바로 공개`)를 한 번에 보인다.
  - [ ] 고칠 곳이 섞인 답에는 그 값만 고쳐 모든 편과 일정 표를 다시 보이고 "이대로 올릴까요?"라고 묻는다. `publish.json`과 `fake-calls.log`가 없고 7단계다. 의견은 고친 편의 명세에 적힌다.
  - [ ] "네" 뒤 편마다 `publish.json`이 초안과 같고(`cmp`), 편마다 `게시 정보 승인(일정 <release>)` 줄이 있다.
- 기대 (올리기):
  - [ ] 마지막 편(8단계)을 보류하고 1편으로 바꿔(`start` → `stage 8`) 시작한다. 1편도 C1-1과 C1-6 프레임 Read를 다시 한 뒤 게시 명령을 부른다.
  - [ ] `fake-calls.log`가 1편 `upload → thumbnail → status`, 그다음 2편 `upload → thumbnail → status` 순서다. 날짜 일정은 `private`와 그날 `18:00:00+09:00`의 `publishAt`, `now`는 `public`이다. 각 편의 `publish-state.json` `sent`가 승인한 제목·설명란·태그와 같다.
  - [ ] 편마다 C4 1~6(루트 mp4, 명세 영상 주소, 곡 사용 기록, 10단계)이 되고, PushNotification "업로드 완료"는 2편의 C4가 끝났을 때 한 번이다.
- 기대 (두 번째 실행, `fail-thumb-once`):
  - [ ] 1편이 `게시 실패: 썸네일 실패: 가짜 썸네일 오류`로 9단계에 남고(명세 `Stage: 9.`), 보류 뒤 2편이 계속 올라가 10단계가 된다. 2편의 `status`는 그대로 걸린다.
  - [ ] 2편의 C4 알림에 9단계로 남은 1편과 Studio 링크가 함께 있다. 그 뒤 `active.py start eval-1-shorts`로 1편을 진행 중(9단계)으로 되돌려 둔다.
  - [ ] 다시 `/shorts complete`면 C0이 9단계로 들어가 C1-6 프레임을 다시 Read 하고, `publish.json`을 바꾸지 않고 같은 명령을 부른다. `fake-calls.log`에 1편 `upload`는 여전히 한 줄이고 `thumbnail`·`status`만 더해진다. 1편 C4까지 끝나 10단계다.
- [ ] 가짜 클라이언트는 업로드마다 `FAKE123`, `FAKE124`…를 돌려준다. 게시 목록에 편마다 줄이 하나씩 생기고, 예약 편은 날짜가 공개일이며 비고가 `예약 18:00`이다.
