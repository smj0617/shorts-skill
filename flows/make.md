# 낙서와 애니메틱부터 미리보기까지 (단계 4~6)

`<영상>`과 `PY`는 [start.md](start.md) 머리의 뜻이다. 낙서 도구의 형식과 명령은 `doodles/doodle.py`·`doodles/storyboard.py` 첫 주석이 원본이다. 기획안 승인 전에는 움직임(컴포지션, 애니메이션)을 만들지 않는다. 낙서 스토리보드(시트)는 Claude가 그림을 맞춰 보는 정지 그림이고, 사용자에게는 움직이는 애니메틱으로 보인다.

## M1 — 낙서 그리기 (3단계와 동시에)

1. **낙서 모음 먼저.** 기획안 장면 목록의 "화면에 그릴 사물"마다 `doodles/library/*.json`의 `name`·`id`를 본다.
   - 같은 사물이 있으면 장면 목록에 `{"doodle": "<이름>"}`으로 그대로 쓴다. 모음에 저장된 씨앗이 쓰인다.
   - 조금 고쳐 쓸 것이면 그 json을 `<영상>/doodles/`로 복사해 고친다. `id`, 획 id, `seed`는 그대로 둔다. 그래야 고치지 않은 획이 모음과 같게 그려진다.
2. **없는 사물만 새로 그린다.** 사물 하나에 낙서 설명 하나, `<영상>/doodles/<id>.json`. 손으로 좌표를 짜기 전에 Skill `anidoodle`로 모양과 획 순서를 잡거나, Skill `streamline-expert`로 오픈소스 아이콘을 뼈대로 가져와 낙서 획으로 다시 그린다([references/tools.md](../references/tools.md), 러프 시간을 줄이려는 것이다). 개념은 보면 바로 알 수 있는 주제의 사물로 그리고, 반복 캐릭터는 두지 않는다. 주인공 사물은 기획안에서 고른 러프의 사물과 구도를 따라 공들여 그린다(훅의 공들인 모습 하나와 뒤 장면의 상태 그림, 제작 기본값 "그림"). 주인공은 `<영상>/doodles/hero.py` 한 곳에서 그리고 상태 그림은 `hero.pose(...)`·`hero.emit(...)`으로 뽑는다. 낙서 갈래를 나눠도 그리기 함수를 복사하지 않는다(transaction-shorts: 세 벌로 복사돼 고칠 때마다 어긋났다). 영상 낙서는 `lighten.write`가 무게 상한을 넘으면 쓰지 않고 멈추므로, 그 자리에서 빗금을 성기게 하거나 채움 면으로 바꾼다. 낙서를 스크립트로 그리면 표정·자세처럼 의견이 자주 오는 값은 M3 3의 "자주 바뀌는 값"처럼 스크립트 위쪽 상수로 둔다.
3. **장면 목록** `<영상>/storyboard/storyboard.json`을 쓴다. 키의 원본은 `shorts-template/compositions/make_words.py`(화면 글자)와 `make_scene_a.py`(`cue`) 첫 주석이고, 모든 키를 쓴 예는 `shorts-template/compositions/test_compositions.py`의 `board`다.
   - 기획안 장면 하나에 `scenes` 한 칸. `id`는 기획안 장면 id(= `narration/script.json`의 장면 id)다. 다르면 장면 레이어가 그 장면을 말없이 건너뛴다. `name`은 그 장면의 핵심 순간이다.
   - 화면 글자: `toc`는 장면마다 `""`로 둔다(목차는 쓰지 않는다, ADR-0002. 빼면 `text`가 목차로 나온다). `text`·`keyword`(핵심 키워드)는 이름 붙이는 장면에만 기술 이름으로 두고, 나레이션이 그 말을 할 때 써진다. 이름표는 `labels`(`{"text": "DB", "doodle": "<낙서 파일 이름>", "word": "<이름표가 나오는 말>"}`).
   - 낙서 항목의 `cue`: `{"line": <문장 번호>, "word": "<그 문장 속 말>"}`. 그 말이 나올 때 그리기 시작한다. 없으면 k번째 낙서가 k번째 문장에 그려진다. 그림 순서는 나레이션의 단어 순서를 따른다.
   - 맨 위 `red_words`: 빨간 펜으로 쓸 화면 글자. Claude가 기획안을 보고 고른다(제작 기본값 문서 "화면"의 빨간 펜 규칙). 길이, 영어 여부, 줄나눔으로 정하지 않는다.
   - `thumbnail` 칸: `text`는 기획안의 썸네일 글자, `doodles`는 고른 러프를 공들인 낙서.
   - `seed`를 하나 정한다. 승인 뒤에는 바꾸지 않는다. 낙서마다 쓰이는 씨앗은 장면 항목의 `seed` > 낙서 설명의 `seed` > 장면 목록의 `seed` 순이고, 제작과 낙서 모음도 같은 순서로 씨앗을 고른다.
4. **첫 영상인지 본다.** `doodles/rules.md`의 `## 피드백`에 영상 이름(`…-shorts`)이 붙은 항목이 하나도 없으면 첫 영상이다.
5. **시트를 만든다.** 프로젝트 루트에서:
   - 첫 영상: `PY doodles/storyboard.py sheet <영상>/storyboard/storyboard.json --candidates` → `storyboard.candidates.png`. 후보 A(`rules.json`), A~B 중간, B(`rules-max.json`)가 줄마다 같은 장면을 그린다. 후보는 이 범위 안에서만 낸다.
   - 그 밖: `PY doodles/storyboard.py sheet <영상>/storyboard/storyboard.json` → `storyboard.png`.
6. **첫 영상이면 함께 정할 것**을 준비한다: 종이 바탕, 손글씨 글씨체(OFL처럼 영상에 써도 되는 라이선스만), 엔딩 모양. 각각 후보 두 개와 추천. 종이와 글씨체는 `<영상>/thumbnail/make_thumbnail.py`의 "바꿀 자리"를 바꿔 만든 썸네일로 작은 시안을 보인다.

M1 완료: 시트 PNG를 Read 해서 봤고, 장면 칸 수가 기획안 장면 수와 같고, 마지막 칸이 썸네일이다.

## M2 — 애니메틱으로 연출 확인 (단계 4, 기다리지 않음)

S6이 끝나면 녹음 시각(`narration/timing.json`)과 곡(`assets/bgm.mp3`)이 있다. 이것으로 칸마다 움직임 계획을 쓰고, 움직임 표로 옮겨 애니메틱(거친 미리보기)을 만든다. 사용자 승인은 기획안과 미리보기 두 번뿐이다(2026-11-11 사용자: 목표 영상 하나 1시간, 정지 스토리보드 승인 대신 빠른 애니메틱으로 연출 확인). 정지 시트로는 클로즈업 크기, 주인공이 나오는 때, 되감기 세기가 안 보여 미리보기에서야 의견이 몰렸다(transaction-shorts). proxy-shorts는 움직임을 미리보기에서야 맞추느라 같은 장면을 여러 번 다시 만들고 검사했다.

1. **움직임 계획.** 장면 목록의 장면 칸마다 `motion` 한 줄을 적는다: `<cue 시각>초 "<말>" · <음악 세기> · <무엇이 어떻게 움직이는지> — <왜>`.
   - cue 시각: 그 칸 낙서의 `cue` 말이 나오는 영상 초. `compositions/scene_kit.py`의 `at_word`로 `timing.json`의 그 문장에서 잰다. 사건이 여럿이면 시각마다 적는다.
   - 음악 세기: `timing.json` `music`의 표지(합주, 마지막 화음 등)로 본 그 칸의 구간(조용함/합주)과 박 간격. 박 간격은 `<영상>`에서 `python narration/seam/periods.py assets/bgm.mp3 <칸 시작> <칸 끝>`으로 잰다.
   - 예: `8.9초 "대리인이라는" · 조용함, 박 0.42초 · 신문 프락치가 그려진다 — 이름이 나오는 순간 그 사물을 보인다`.
2. **점검.** 계획 전체를 아래 여섯으로 보고, 걸린 칸을 고쳐 모든 칸이 여섯을 통과한 뒤 보인다.
   - 사물은 그 이름이 나오는 말에 그려진다(proxy: 9초 "대리인"에 대리인 그림이 나오지 않았다).
   - 대사의 사건(부르다, 넘기다, 막다 같은 동작)마다 화면의 움직임이 하나 있다(proxy: 43초 "부르면"에 부르는 장면이 없었다).
   - 음악이 빨라지거나 커지는 구간(합주부터)은 화면도 박에 맞춰 빨라진다(proxy: 합주 뒤에도 화면이 정적이었다).
   - 엔딩에 주인공 사물이 선다: 남길 문장 칸의 계획에 `video.json` `ending.doodle`로 세울 주인공 사물의 상태 그림을 적는다.
   - 무대: 필요 장면은 무대 하나 위에서 상태와 구도만 바뀐다. 구도 바뀜(가까이·넓게·옮겨 가기)은 이야기 단계 경계(불편 → 해결 → 이름 붙이기 → 함정)와 음악 프레이즈 경계에 있다. 새 무대로 갈아타는 칸은 까닭을 적는다(제작 기본값 "그림").
   - 이름 붙이기: 그 칸이 곡의 가장 큰 타격점에 있고, 그 순간 빨간 펜 핵심 키워드가 써지고 이름표가 그림에 붙는다(제작 기본값 "소리").
3. **움직임 표.** 계획을 `storyboard.json`의 표로 옮긴다: 상태 그림이 여럿인 사물은 맨 위 `cast`, 장면마다 `keys`(형식은 `<영상>/compositions/keys.py` 첫 주석, 예는 `<영상>/storyboard/keys-example.json`). 에이전트 없이 Claude가 쓴다. 표에 없는 낙서도 cue 말에 저절로 그려지므로 움직이는 칸만 적는다.
   - 움직임 틀은 제한이 아니라 자주 쓰는 동작을 빠르게 조합하는 부품이다. 주제와 대본에 맞는 연출이 부품에 없으면 줄이지 말고 `<영상>/compositions/moves.py`에 몇 줄짜리 `@action("이름")`으로 더해 표에서 쓴다(예: `shake`, `spin`, `pulse`). 그래도 안 되는 무대만 첫 장면에 `"script"`를 적고 M3에서 손 스크립트로 짠다.
   - 움직임은 애니메틱 하나로 확인한다(예전 거친 움직임 정지 시트 `motion-<장면 id>.json`의 자리).
4. **애니메틱을 만들고 스스로 맞춰 본다.** Skill `hyperframes`와 `hyperframes-cli`를 먼저 부른다([references/tools.md](../references/tools.md)). `<영상>`에서 `python compositions/keys.py --animatic` → `.harness/animatic/`(떨림 없음, 글자·엔딩 없음, 나레이션·곡 있음, 왼쪽 위에 장면 이름). 1초 안팎이고, 출력의 줄마다 표 한 줄의 실제 시각이 나온다. 계획의 cue 시각들로 `.harness/animatic`에서 `npx hyperframes snapshot --at ...`을 찍어 모음(contact sheet)을 Read 하고, 계획과 다른 칸은 표 값을 고쳐 다시 돌린다.
5. **보이기 전 점검.** 애니메틱 모음, 낙서 시트, 움직임 계획을 SKILL.md "보이기 전 점검"에 돌린다(점검표 "그림"·"낙서 스토리보드" 절).
6. **보이고 바로 넘어간다.** `active.py stage 4`를 부르고, 모음(이미지)과 `cd .harness/animatic && npx hyperframes preview`, 움직임 계획(칸 번호마다 한 줄), 빨간 펜으로 쓸 말(`red_words`)과 고른 까닭 한 줄을 보이고 PushNotification으로 알린다. "연출 의견이 있으면 시각을 붙여 주세요, 기다리지 않고 제작을 시작합니다"라고 붙인다. 이어서 기다리지 않고:
   - 첫 영상이면(답 없는 번호는 추천대로 정한다):
     - 고른 후보의 수치를 `doodles/rules.json`과 `rules.md` 표에 넣는다(A면 그대로). `rules.md` 피드백에 "출발점: 후보 X"를 적는다.
     - 종이 바탕, 글씨체, 엔딩 모양을 `docs/agents/shorts-defaults.md` "그림"에 적고, 영상 폴더와 `shorts-template/`의 같은 자리(`thumbnail/make_thumbnail.py` "바꿀 자리", `narration/template.html` `:root`, `compositions/make_ending.py`)에 넣는다.
   - `video.json`의 `thumbnail`(`small`, `big`, `doodle`, `seed`)을 썸네일 칸대로, `ending.doodle`을 남길 문장 칸의 움직임 계획대로 적는다. M3에서 `make_ending.py`가 "사물 낙서 자리가 없다"로 멈추면 `ending.keep_lines`의 줄 수를 줄인다(문구는 그대로, proxy: 네 줄 → 세 줄).
   - `active.py stage 5`를 부르고 SKILL.md "단계마다 새 세션"대로 넘긴다. 이어 받는 세션(또는 여기서 계속하는 이 세션)이 M3을 한다. 시트로 답이 안 나는 취향 문제는 시트에 가까운 쪽으로 정하고 의견 목록에 "정함: …"으로 남긴다.

애니메틱이나 제작 중에 의견이 오면 그 의견이 가리키는 것만 고친다. 연출 의견은 표 값이라 1~2초에 다시 만든다.

| 의견 | 고치는 곳 |
|---|---|
| 한 장면의 배치·크기 ("3번 장면 서버를 더 크게") | 장면 목록의 그 장면 `doodles` 항목의 `x`·`y`·`scale` |
| 사물의 모양 ("서버 다리를 없애") | 그 낙서 설명에서 해당 획만 고치거나 더하거나 지운다. 다른 획 id와 씨앗은 그대로 둔다. 모음 낙서면 먼저 `<영상>/doodles/`로 복사한다 |
| 선 전체의 거칠기·굵기 ("선이 너무 떨린다") | `doodles/rules.json`의 수치와 `doodles/rules.md` 표. `rules-max.json`을 넘지 않는다 |
| 장면 순서·글자·연출 | 장면 목록의 해당 칸, 필요하면 기획안 |
| 움직임 ("43초에 부르는 장면을 넣어", "2안으로") | 그 칸의 `motion` 줄과 `keys`의 그 줄(없는 동작이면 `moves.py`에 더함). 그림이 나오는 때를 옮기면 그 낙서의 `cue`도 |
| 연출 ("컷 때 더 크게", "더 일찍 나와", "되감기 세게") | `keys`의 그 줄 값(`frame` `to`, `at` 더할 초, `rewind` `slide`) → `python compositions/keys.py --animatic` |
| 빨간 펜 ("이건 빨갛게 하지 마") | 장면 목록의 `red_words` |

고친 뒤 `keys.py --animatic`(M3 중이면 `keys.py --only <장면 id>`)을 다시 돌려 바뀐 칸 모음만 보인다. 그림 의견은 낙서 규칙에, 나머지는 의견 목록에 적는다(SKILL.md "의견 기록").

## M3 — 제작 (단계 5)

`<영상>/AGENTS.md`(HyperFrames 규칙)와 제작 기본값 문서의 "에이전트 운용"을 먼저 읽고, 이 세션에서 아직 부르지 않았으면 Skill `hyperframes`·`hyperframes-cli`를 부른다([references/tools.md](../references/tools.md)). 레이어 에이전트 브리프에는 "작업 전에 Skill `hyperframes`를 부를 것"을 넣는다. 표·생성 스크립트로 안 되는 이름 붙은 효과는 손 스크립트 전에 Skill `hyperframes-registry`로 찾아본다.

레이어 html은 손으로 쓰지 않는다. 모두 생성 스크립트가 만들고, 고칠 때도 스크립트나 그 입력(`storyboard.json`, 낙서 설명, `video.json`)을 고쳐 다시 돌린다. 도구 설명의 원본은 `<영상>/README.md` "만드는 순서" 5~7과 각 스크립트 첫 주석이다. 시각은 모두 `narration/timing.json`에서 읽으므로, 다시 녹음하면 스크립트만 다시 돌린다.

1. **뼈대와 미리보기.** `<영상>/narration`에서 `python make_timeline.py`, `<영상>`에서 `python narration/build.py`(`index.html`, 종이 `compositions/paper.html`, 엔딩 `compositions/ending.html`을 만든다), 그다음 `npx hyperframes preview --background`. 주소를 적어 두고 끝날 때까지 켜 둔다. 움직임 계획에 박에 맞출 칸이 있으면 박 시각 `narration/beats.json`도 이때 만든다(만든 법은 `proxy-shorts/narration/beats.json`의 `_`).
2. **장면 레이어는 먼저 표로.** `python compositions/keys.py`가 M2 애니메틱의 표(`cast`·`keys`)로 장면 레이어를 모두 만든다(`compositions/scene-<무대 첫 장면>.html`과 `host:` 줄, 떨림 있음). 무대(`"continue": true`로 이어진 장면)마다 레이어 하나다. 상태 바꾸기, 줌·클로즈업, 되감기, 박에 튀기, 등장·퇴장, 덧붙이기·깜빡임은 표로 된다. 표로 안 되는 움직임이 있는 무대만 첫 장면에 `"script": "make_scene_<x>.py"`를 적고 아래처럼 에이전트에게 맡긴다(그 스크립트도 `kit.Family`로 상태 묶음을 쓴다). 두 영상에서 같은 손 움직임이 나오면 마무리 때 `keys.py`의 `do`로 올린다.

   손으로 짜는 무대는 장면(또는 이어진 장면 2~3개)마다 레이어 하나, 에이전트 하나다. 한 파일은 한 에이전트만 고친다.
   - 에이전트는 `compositions/make_scene_a.py`를 `make_scene_<x>.py`로 복사해 `COMP_ID`, `SCENES`(맡은 장면 id), `layout`(배치), `LABELLED`(이름표가 붙을 낙서)만 고치고 돌린다 → `compositions/scene-<x>.html`(z 2)과 마지막 줄의 `host:` 줄. 확인은 `--harness`(`.harness/scene-<x>/`).
   - 공통 부분은 `compositions/scene_kit.py`(배치 검사: 가운데 x 540·좌우 120·아래 y 1290·이름표 자리 75px, 말 시각, 펜·떨림·지우기, host 줄)와 `compositions/pen_chunks.py`(그리기 길이: 문장 앞 40%·최대 1.5초, 획 60개 넘으면 덩어리 그리기)다. 장면 에이전트는 이 둘을 고치지 않는다. 고칠 일이 생기면 Claude에게 알린다.
   - 썸네일은 따로 effort `low` 에이전트: `PY thumbnail/make_thumbnail.py` → `thumbnail/thumb.png`.

   에이전트 지시에는 담당 파일, 읽기만 할 파일(`video.json`, `narration/timing.json`, `narration/beats.json`(있으면), `storyboard/`, `doodles/`, `compositions/scene_kit.py`, `compositions/pen_chunks.py`), 하네스 폴더 `.harness/<이름>/`, 아래 3을 적는다. effort는 장면 레이어 `high`, 썸네일 `low`.
3. **그림과 움직임은 장면마다 정한다(표가 먼저, 손 스크립트는 표로 안 되는 것만).** 도구가 정하는 것은 배치 검사, 펜으로 그려지는 방식, 표의 움직임 종류(`keys.py` 첫 주석)다.
   - 낙서 모양은 영상마다의 낙서 설명(`<영상>/doodles/*.json`, 모음 낙서는 모음 json)에서 나온다. 씨앗은 M1의 순서로 고르고 규칙은 `doodles/rules.json` 그대로라서, M1 시트의 모양이 그대로 나온다.
   - 움직임은 M2의 움직임 계획(장면 목록의 그 칸 `motion`)과 애니메틱의 표(`cast`·`keys`)대로, 적힌 cue 시각과 박에 맞춘다.
   - **자주 바뀌는 값**: 표정·자세·자리·속도·박 수처럼 의견이 자주 오는 값은 스크립트 위쪽 상수 한 줄로 둔다(예: proxy-shorts `compositions/make_scene_how.py`의 자리 `SPOTS`, 바퀴당 박 수 `LAPS`). 그러면 의견 하나가 그 값 고치기와 그 장면 다시 만들기로 끝난다.
   - 장면만의 움직임(날아와 붙기, 잠듦·깨어남 같은 상태 변화, 옮겨 가기)은 그 장면 스크립트에서 `layer.js`로 GSAP 줄을 더해 만든다(예: spring-lazy-shorts `compositions/make_scene_a.py`의 날아와 붙는 꼬리표). scene_kit에 없는 움직임이라고 펜 그리기만으로 줄이지 않는다.
   - 같은 움직임이 두 영상에서 쓰이면 마무리 때 scene_kit으로 올리고 템플릿 `README.md` "바뀐 점"에 적는다(Claude가 한다).
4. **화면 글자는 장면 레이어가 다 나온 뒤에.** `<영상>`에서 `python compositions/make_words.py` → `compositions/words.html`(z 5). 장면 레이어 html의 낙서 자리를 읽어 목차·핵심 키워드·이름표를 놓는다. `!!`로 시작하는 줄은 이름표 자리가 모자란다는 뜻이니 그 장면의 `layout`을 고쳐 장면 레이어부터 다시 돌린다. 장면 레이어를 다시 만들면 이것도 다시 돌린다.
   - 사용자 몫 앞당기기(SKILL.md "기다리는 시간 채우기"): 레이어 에이전트를 띄운 직후 게시 정보 초안(`publish.draft.json`)과 썸네일 시안을 보이고 의견을 받는다.
5. **루트 통합은 Claude 혼자 한다.** 장면이 루트에 들어가 6~7의 맞춰 보기·점검을 통과하면 그 장면만 바로 보인다(SKILL.md "기다리는 시간 채우기", Studio 바로가기는 `review_links.py`). 그 장면 의견은 M4 표대로 바로 고친다. 레이어가 끝나는 대로 `host:` 줄을 `narration/template.html`의 host 자리에 끼우고(words 줄 포함) `python narration/build.py`, 그 장면의 가벼운 검사 `python .claude/skills/shorts/scripts/check_parallel.py <영상> --range a,b`(표의 사건 시각만, 대비·craft 없이, 캐시, 동시 3개). 모든 레이어와 words가 끝나면 같은 명령을 `--range` 없이 한 번(사건 시각 전체). 대비·craft까지 보는 `--full`은 렌더 직전(complete C1)에만 한다(`npm run check`를 한 번에 돌리지 않는다).
6. **시트와 움직임 계획에 맞춰 본다.** 장면마다 핵심 순간을 움직임 계획의 cue 시각에 `npx hyperframes snapshot --at ...`으로 6장 안팎 찍어 시트의 칸과 계획의 사건에 비교한다. 다른 곳은 그 레이어 에이전트에게 돌려보낸다.
7. **보이기 전 점검.** 그 snapshot과 장면 파일을 SKILL.md "보이기 전 점검"에 돌린다(점검표 "미리보기" 절). 걸린 곳도 그 레이어 에이전트에게 돌려보낸다.

M3 완료: `check_parallel.py <영상>` 오류 0, `make_words.py`에 `!!` 줄이 없고, snapshot이 시트의 장면 칸과 움직임 계획의 사건에 맞고, 보이기 전 점검의 걸린 줄이 고쳐졌거나 까닭이 적혔고, `npx hyperframes preview --status`가 켜져 있다고 나온다.

## M4 — 미리보기 (단계 6)

의견을 하나씩 받아 고치면 같은 장면을 여러 번 다시 만들고 검사하게 된다(proxy-shorts). 그래서 의견은 한 번 끝까지 본 뒤 목록으로 받고, 장면별로 나눠 동시에 고치고, 검사는 끝에 한 번 한다.

1. `active.py stage 6`을 부르고, PushNotification으로 알리고, 미리보기 주소와 함께 "한 번 끝까지 보신 뒤 '9초 …', '43초 …'처럼 시각을 붙인 의견을 목록으로 한 번에 주세요"라고 알린다.
2. **장면별로 나눠 동시에 고친다.** 목록이 오면 의견 목록에 적고(SKILL.md "의견 기록"), 시각으로 고칠 장면 레이어를 찾아 장면별로 묶는다. 묶음마다 에이전트 하나에게 동시에 맡겨, 제작 기본값 문서의 "렌더 전 피드백 루프"대로 렌더 없이 고친다.
   - **연출 의견은 에이전트 없이 표로.** 클로즈업 크기·자리(`frame`의 `to`), 나오는 때(`at`의 말·더할 초), 되감기 세기(`rewind`의 `slide`), 튀는 높이(`hop`의 `h`), 깜빡 수(`count`)처럼 표에 있는 값은 Claude가 `storyboard.json`의 그 줄을 고치고 `python compositions/keys.py --only <장면 id>`를 돌린다(1~2초). 의견 시각은 출력 줄의 시각으로 표의 줄을 찾는다. 에이전트는 `script` 무대와 표에 없는 새 움직임에만 쓴다.
   - 낙서 모양은 M2 표대로 낙서 설명을 고친 뒤 그 장면의 레이어(`keys.py --only <장면 id>` 또는 `make_scene_<x>.py`)를 다시 돌린다.
   - 여러 장면이 함께 쓰는 것(`video.json`, 모음 낙서, `make_words.py`, 루트 `build.py`)은 장면 고침이 다 끝난 뒤 Claude가 한 번에 고치고 돌린다.
   - 목록 뒤에 따로 온 의견은 그 장면의 묶음에 더한다(그 에이전트가 돌고 있으면 그 에이전트에게 보낸다).
   - 맡기기 전에 목록에서 가리키는 대상이 둘일 수 있는 의견은 한 줄로 되묻고, 취향 의견(더 보기 좋게, 더 역동적으로)은 2~3안으로 낸다(제작 기본값 "묻는 것과 정하는 것"). 나머지 묶음은 기다리지 않고 맡긴다.
3. **대사 의견은 모아서 다시 녹음한다.** 대사를 고치는 의견은 대본(`narration/script.json`)과 의견 목록에 적고, 목록의 대사 의견을 모아 `python tts_budget.py --need 1`을 확인한 뒤 `PY make_tts.py <장면 id> <장면 id> ...`로 요청 1회에 다시 녹음한다(백그라운드, 장면 고침과 동시에). 녹음이 끝나면 `make_timeline.py`, `build.py`, 장면 레이어와 `make_words.py`를 다시 돌린다. 하루 2회 계획(S3)을 넘을 것 같으면 먼저 알린다.
4. **검사는 모든 고침이 끝난 뒤에.** 돌고 있는 에이전트, 다시 녹음, 남은 고침이 모두 끝나면 바뀐 구간마다 가벼운 검사를 동시에 돌린다(제작 기본값 "검사"). 전체 검사는 렌더 직전(complete C1)에 한 번 한다. 오류가 0이면 고친 순간들의 snapshot을 보이기 전 점검(점검표 "미리보기" 절)에 돌린 뒤, 한 번에 보이고 "미리보기에서 확인해 주세요"라고 한다.
5. 에이전트가 길어지면 제작 기본값 문서의 "에이전트 갱신(인계)"대로 인계 메모를 쓰고 바꾼다.
6. 사용자가 다 봤다고 하면 SKILL.md "단계마다 새 세션"대로 넘긴다. 연 세션(또는 여기서 계속하는 이 세션)이 `/shorts complete`로 완성과 게시를 시작한다. 단계는 6에 둔다(7로는 complete 흐름이 넘긴다).
