# 완성과 게시 (`/shorts complete`, 단계 7~10)

`<영상>`과 `PY`는 [start.md](start.md) 머리의 뜻이다. 명령은 모두 프로젝트 루트에서 돌린다(`npm`·`npx`만 `<영상>`에서). 게시 명령의 입력·출력·종료 코드는 `publish/publish.py` 첫 주석이 원본이다.

영상 폴더에서 이 흐름이 쓰는 파일:

| 파일 | 누가 쓰나 | 뜻 |
|---|---|---|
| `renders/final.mp4` | 렌더 | 올릴 영상 |
| `publish.draft.json` | Claude | 게시 정보 초안. 사용자에게 보여 주는 것은 항상 이 파일 그대로다. 승인을 물을 때 `release`(일정: `now` 또는 `YYYY-MM-DD`)도 들어간다 |
| `publish.json` | Claude, 승인 때만 | 승인된 게시 정보와 일정. 게시 명령은 이 파일만 읽는다 |
| `publish-state.json` | 게시 명령 | `video_id`(올라간 영상), `thumbnail_done`, 공개·예약 요청과 적용 결과(키 이름은 게시 명령 첫 주석) |

연작은 다 만든 뒤 한 번에 올린다(제작 기본값 "게시 일정"). 마지막 편이 아닌 편은 C1과 초안까지 하고 보류하며("연작의 앞 편"), 마지막 편의 C2에서 모든 편의 게시 정보와 일정을 한 번에 승인받는다. 한 편뿐인 주제는 그 편이 마지막 편이다. 몇 편 중 몇 편인지는 쇼츠 명세 `## 의견 목록`의 편 목록 줄로 안다. 다른 편의 영상 이름은 이 영상 이름에서 편 번호만 바꾼 것이다([start.md](start.md), 예: `cache-1-shorts`, `cache-2-shorts`).

## 게시 문턱

업로드는 사용자 채널에 올라가는 게시물이다. 게시 명령(`publish/publish.py`)은 아래 둘이 모두 참일 때만 부른다.

1. **승인**: 사용자가 마지막으로 전체를 보여 준 초안(연작이면 모든 편의 초안과 일정)에 "네"(또는 "승인", "올려 주세요")라고 명시적으로 답했고, 편마다 `publish.json`이 그 초안과 한 글자도 다르지 않다.
2. **프레임 확인**: 올릴 편마다 지금의 `renders/final.mp4`에서 뽑은 프레임을 이번 실행에서 Read 해 봤다(C1-6). 보류했던 앞 편도 이번 실행에서 C1-1로 렌더가 그대로인지 보고 C1-6만 다시 한다.

둘 중 하나라도 아니면 게시 명령을 부르지 않고, 빠진 쪽(C2 승인 또는 C1-6 프레임 확인)으로 돌아간다. 질문, 고칠 곳이 섞인 답("제목만 바꾸고 올려"), "괜찮네" 같은 감상은 승인이 아니다. 고칠 곳을 반영해 전체를 다시 보여 주고 "이대로 올릴까요?"라고 다시 묻는다.

## C0 — 들어오기

`python .claude/skills/shorts/scripts/active.py show`를 돌리고 단계로 나눈다.

| 단계 | 할 일 |
|---|---|
| 진행 중 쇼츠 없음, 1~5 | 지금 단계와 다음 할 일을 [status.md](status.md)대로 알리고 끝낸다. 단계를 바꾸지 않는다 |
| 6 | `active.py stage 7`을 부르고 C1과 C2를 같은 메시지에서 함께 시작한다 |
| 7 | C1과 C2를 함께 시작한다. C1-1에서 쓸 수 있는 렌더면 다시 렌더하지 않는다. 초안은 명세 `## 의견 목록`의 게시 정보 의견을 반영해 다시 쓴다. 연작의 앞 편이면 C2-3에서 "연작의 앞 편"으로 간다 |
| 8 | C3 |
| 9 | C3. 게시 명령이 `publish-state.json`을 보고 영상은 건너뛰고 썸네일부터 다시 한다 |
| 10 | `active.py show`의 보류 목록에 같은 연작의 편이 있고 그 명세 첫 줄이 `Stage: 9.`이면 `active.py start <그 편>`을 부르고 9단계 줄로 간다. 아니면 이미 게시 완료다. 명세 `## Comments`의 영상 주소와 Studio 링크를 다시 알리고, 새 쇼츠는 `/shorts <주제>`라고 한 줄 덧붙이고 끝낸다 |

## C1 — 최종 검수와 렌더 (단계 7, C2와 동시에)

시작할 때 이 세션에서 아직 부르지 않았으면 Skill `hyperframes-cli`를 부른다(SKILL.md "HyperFrames 스킬"). 렌더가 실패하면 그 스킬의 복구 절을 먼저 따른다. 검수 하나가 막혀도 C2는 계속 진행한다. 렌더(4)는 검사·snapshot·Studio가 끝난 뒤 혼자 돌린다. 같이 돌면 메모리가 모자라 렌더가 크게 느려진다(2026-11-11 transaction: 약 10분). 렌더 옵션은 아래 4의 기본이 가장 빠르다(2026-11-11 spring-lazy 70초 영상 측정: 기본 167초, `--gpu` 209초, 조각 방식 `HF_SEGMENTED_CAPTURE` 311초이고 조각이 하나뿐이라 고친 뒤 `--resume`도 288초).

1. **다시 쓸 렌더인지 본다.** `renders/final.mp4`가 있고 아래 명령이 아무것도 찍지 않으면 2~5를 건너뛰고 6으로 간다.
   `find <영상> -type f -newer <영상>/renders/final.mp4 -not -path '*/renders/*' -not -path '*/node_modules/*' -not -path '*/.harness/*' -not -path '*/handoff-notes/*' -not -name 'publish*.json'`
2. **check**: 전체 검사 `python .claude/skills/shorts/scripts/check_parallel.py <영상> --full --parts 6`(구간별 동시, 대비·craft 켬, 캐시 없음; 제작 기본값 "검사"). 렌더·Studio가 돌지 않을 때라 동시 6개로 쪼갠다(12코어). 막을 일: CPU가 비어 있는데 기본 동시 수(3)로 검사를 돌리며 그 결과를 기다리는 것(transaction-shorts 2026-11-11: 렌더가 끝난 뒤에도 3개로 돌려 사용자가 "검사를 병렬로 실행하라고" 짚음). 오류 0.
3. **연락 시트**: `npx hyperframes snapshot --at <시각들>`로 장면마다 핵심 순간과 `music.hits` 시각을 8~12장 찍고 모두 Read 한다. 볼 것: 잘린 글자, 쇼츠 안전 영역(하단 1/4, 오른쪽 120px) 침범, 낙서 스토리보드 칸과 다른 낙서, 빈 화면, 엔딩 로고. 문제가 있으면 [make.md](make.md) M4처럼 렌더 없이 고치고 2부터 다시 한다. 취향이 걸린 것만 사용자에게 번호 질문으로 묻는다. 7단계에 머문다.
4. **렌더**: 시작 시각을 적어 두고 `<영상>`에서 `npx --yes hyperframes@0.8.209 render --quality delivery -o renders/final.mp4`를 백그라운드로 돌린다(Bash `run_in_background`, 또는 effort `low` 에이전트).
5. **새 파일인지와 음량**: `renders/final.mp4`의 수정 시각이 4의 시작 시각보다 뒤다. `ffprobe`로 1080x1920과 길이를 본다. `ffmpeg -i <영상>/renders/final.mp4 -af ebur128 -f null -`의 통합 음량(I)이 약 −16 LUFS(±1 LU)다. 벗어나면 측정값과 함께 알리고 고친 뒤 다시 렌더한다.
6. **프레임 확인**: 3과 같은 시각마다 `ffmpeg -ss <시각> -i <영상>/renders/final.mp4 -frames:v 1 <영상>/.harness/complete/frame-<시각>.png`로 뽑아 모두 Read 하고 3의 snapshot과 비교한다. 검은 화면, 깨진 프레임, snapshot과 다른 장면이 없어야 한다.
7. PushNotification으로 "렌더 완료"를 알리고, 측정값(해상도, 길이, 통합 음량)을 한 줄로 알린다.

C1 완료: 6의 프레임을 모두 봤고 이상이 없다. 이것이 게시 문턱 2다.

## C2 — 게시 정보 초안과 승인 (단계 7)

1. **초안 파일**을 Write 한다: `<영상>/publish.draft.json` = `{"topic", "title", "description", "tags"}`.
   - `topic`: 기획안의 주제(게시 목록의 주제 열).
   - `title`: 질문형 훅, `#Shorts`를 포함해 40자 이내. 썸네일 훅 글자와 어조를 맞춘다(이름 오해가 있으면 오해, 없으면 필요 장면의 불편).
   - `description`: 빈 줄로 나눈 다섯 덩어리, 이 순서다.
     1. 남길 문장(`video.json`의 `keep` 그대로)
     2. "개발 용어로 보면" 2~3줄(기획안의 그 칸, 영상에서 뺀 정확한 이름과 세부. `<`, `>`는 게시 명령이 막으므로 쓰지 않는다)과, 사실 확인 코드를 공개 저장소에 올렸으면 그 링크 한 줄. 저장소가 아직 없거나 이번 코드를 올리지 않았으면 초안을 보일 때 "사실 확인 코드(`IdeaProjects/<주제>-check`)를 공개 저장소에 올리고 링크를 넣을까요?"를 번호 없는 네/아니요로 따로 묻는다. 저장소 만들기·올리기는 "네"가 있어야 하고, 답이 없으면 링크 없이 간다. 저장소 이름과 공개 범위는 처음 만들 때 함께 묻는다.
     3. 해시태그 3~5개 한 줄
     4. `{{출처 표기}}` 한 줄. 출처 표기는 손으로 쓰지 않는다. 아래 2가 곡 목록의 문구로 바꾼다
     5. 코드일지 서명 `코드일지` 한 줄
   - `tags`: 주제 키워드 5~10개(`#` 없이).
2. **출처 표기 채우기와 보이기**: 아래를 돌린다. 곡 목록의 문구를 그대로 넣고, 실제로 올라갈 제목·설명란·태그를 찍는다.

   ```bash
   python - "<영상>" <<'EOF'
   import json, sys
   from pathlib import Path
   sys.stdout.reconfigure(encoding="utf-8")
   sys.path.insert(0, "music"); import songs
   v = Path(sys.argv[1]); p = v / "publish.draft.json"
   d = json.loads(p.read_text(encoding="utf-8"))
   src = Path(json.loads((v / "video.json").read_text(encoding="utf-8"))["music"]["src"]).name
   title = next(s["title"] for s in songs.load() if s["file"] == src)
   d["description"] = d["description"].replace("{{출처 표기}}", songs.attribution(title))
   p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
   print(f"제목({len(d['title'])}자): {d['title']}\n--- 설명란({len(d['description'].encode())}바이트) ---\n{d['description']}\n---\n태그({len(d['tags'])}개): {', '.join(d['tags'])}")
   EOF
   ```

3. **보여 준다.** 연작의 앞 편이면 찍힌 게시 정보를 보이고 의견만 받은 뒤 아래 "연작의 앞 편"으로 간다(올릴지 묻지 않는다). 마지막 편이면:
   1. **일정**: `PY publish/publish.py --plan <편 수>`를 돌린다. 줄마다 `<편 번호> <now|YYYY-MM-DD>`다. 편마다 `publish.draft.json`에 `"release": "<그 값>"`을 문자열로 넣는다. 윈도에서는 줄 끝에 `\r`이 붙어 나오므로 값만 옮긴다(`\r`이 들어가면 게시 명령이 형식 오류로 멈춘다).
   2. 편마다 2의 명령을 그 편 폴더로 다시 돌려(앞 편도) 찍힌 제목, 설명란 전체(코드 블록, 줄바꿈 그대로), 태그를 대화에 옮기고, 그 아래 일정 표(편 | 영상 이름 | 바로 공개 또는 `YYYY-MM-DD 18:00 예약`)를 붙인다.
   3. "이대로 올릴까요? 편마다 비공개로 올린 뒤 처리와 썸네일이 확인되면 위 일정대로 공개·예약합니다. 고칠 곳이 있으면 알려 주세요"로 끝낸다. 렌더가 아직 돌고 있으면 그렇다고 한 줄 덧붙인다.
4. **고칠 곳**: `publish.draft.json`의 해당 값만 Edit 하고, 2의 명령으로 다시 찍어 전체를 다시 보여 준다(출처 표기는 이미 들어 있어 그대로 남는다. 연작이면 3-2처럼 모든 편과 일정 표를 다시 보인다). 7단계에 머문다. 의견은 고친 편의 명세 `## 의견 목록`에 적는다. 출처 표기 줄을 바꾸자는 요청에는, 곡 목록의 문구를 그대로 옮기는 줄이라 여기서는 바꾸지 않는다고 알린다.
5. **승인**(게시 문턱 1): 사용자가 마지막으로 보여 준 전체에 "네"라고 하면
   1. 편마다 `cp <영상>/publish.draft.json <영상>/publish.json`
   2. 편마다 명세 `## 의견 목록`에 `<날짜> 게시 정보 승인(일정 <release>)`을 적는다.
   3. `active.py stage 8`을 부르고 C3으로 간다. C1이 아직 끝나지 않았으면 "렌더와 프레임 확인이 끝나면 올립니다"라고 알리고 C1 완료를 기다린다.

## 연작의 앞 편 (마지막 편이 아닐 때, 단계 7에서 보류)

1. C1이 끝났고(프레임 확인까지) C2-1~2의 초안이 있다. 게시 정보 의견은 초안에 반영해 둔다.
2. 명세 `## 의견 목록`에 `<날짜> 연작 대기: <마지막 편 영상 이름>과 함께 올림`을 적고 `active.py hold`.
3. 다음 편으로 넘긴다: SKILL.md "단계마다 새 세션"대로 새 세션을 열고, 브리프에 `/shorts <주제> <다음 편 번호>편`과 편 목록 줄의 위치를 적는다. 1편의 눈길 지표 회고는 기다리지 않는다.

## C3 — 업로드와 썸네일 (단계 8, 9)

연작은 1편부터 차례로 한 편씩 올린다(게시 목록에 줄을 덧붙이므로 동시에 돌리지 않는다). 승인 직후 진행 중인 편은 마지막 편이므로, 아래 편 바꾸기로 1편부터 시작한다. 편을 바꿀 때는 지금 편이 10단계면 바로, 아니면(8단계, 또는 실패로 9단계) `active.py hold` 뒤 `active.py start <다음 편 영상 이름>`(보류한 단계로 돌아온다) → `active.py stage 8`. 편마다 1~4를 하고, 종료 0이면 그 편의 C4 1~6을 한 뒤 다음 편으로 바꾼다. 모든 편을 돌린 뒤 9단계로 남은 편이 있으면 `active.py start <그 편>`으로 진행 중으로 되돌려 둔다(다음 `/shorts complete`가 C0의 9단계로 들어온다. 둘 이상이면 앞 편 하나만, 나머지는 C0의 10단계 줄이 잇는다).

1. **문턱 확인**: `cmp <영상>/publish.draft.json <영상>/publish.json`이 같다. `publish.json`이 없거나 다르면 `active.py stage 7`을 부르고 C2-3으로 돌아간다. 이번 실행에서 C1-6을 하지 않았으면 지금 한다.
2. 사용자에게 한 줄로 알린다(연작은 처음 한 번): "비공개로 올린 뒤 확인되면 일정대로 공개·예약합니다. 브라우저에 Google 동의 창이 뜨면 '허용'을 눌러 주세요." 로그인 토큰이 만료되거나 게시 명령의 권한이 늘었으면 동의 창이 다시 뜨고, 사용자가 허용하면 게시 명령이 이어 간다.
3. `PY publish/publish.py <영상> --release <publish.json의 release>`를 백그라운드로 돌린다(처리 대기가 최대 30분이다). `PY`는 03에서 Google 패키지를 넣은 파이프라인 venv다.
4. 결과로 나눈다. 실패 이유는 stderr의 `게시 실패: <이유>`다.

| 결과 | 할 일 |
|---|---|
| 종료 0 | stdout의 `영상 id`와 `Studio 편집` 주소를 들고 C4로 간다 |
| 실패, `publish-state.json`에 `video_id` 없음, 이유가 제목·설명·태그·출처 표기 검사 | 아무것도 올라가지 않았다. 이유를 알리고 `active.py stage 7`. C2-4처럼 초안을 고쳐 전체를 다시 보여 주고 새 "네"를 받는다 |
| 실패, `video_id` 없음, 그 밖의 이유(인증, 네트워크, 클라이언트 없음) | 아무것도 올라가지 않았다. 이유를 알리고 8단계에 머문다. 고친 뒤 `/shorts complete`면 다시 올린다 |
| 실패, `video_id` 있음 | 영상은 비공개로 올라갔고 썸네일이나 처리가 실패해 공개·예약은 걸지 않았다. `active.py stage 9`를 부르고, "썸네일 실패" 또는 "처리 실패"와 이유, Studio 링크(`https://studio.youtube.com/video/<video_id>/edit`)를 알린다. 썸네일 없이 공개하지 말라고, 다시 `/shorts complete`면 영상은 다시 올리지 않고 썸네일부터 다시 시도해 성공하면 원래 일정대로(시각이 지났으면 바로) 공개한다고 알린다. 연작이면 이 편은 9단계로 두고 다음 편을 계속 올린다. 다른 편의 공개·예약은 그대로다 |

이유가 "공개·예약 바꾸기 실패"면 영상과 썸네일은 됐고 공개·예약만 못 걸었다. 위 `video_id` 있음 줄처럼 9단계로 두고 알린다. 다시 `/shorts complete`면 공개·예약만 다시 한다. 인증·네트워크 실패는 다음 편도 같으므로 연작이면 거기서 멈추고 알린다. 9단계에서 다시 들어오면 `publish.json`은 건드리지 않고 같은 명령을 다시 부른다. 이유가 썸네일 파일 자체(크기, 형식)면 `thumbnail/thumb.png`만 고쳐 만든 뒤 부른다. 이유가 처리 실패(`failed`, `rejected`, `terminated`)면 다시 시도해도 같으니 Studio에서 영상 상태를 보라고 알린다.

## C4 — 게시 완료 (단계 10)

여러 번 돌려도 결과가 같게, 이미 된 것은 건너뛴다.

1. **루트 mp4**: `cp <영상>/renders/final.mp4 <영상 이름>.mp4`, 그다음 `cmp`로 같은지 본다.
2. **명세에 영상 주소**: `.scratch/<영상 이름>/spec.md`의 `## Comments`에 `- <날짜> 게시(<공개|예약 YYYY-MM-DD 18:00>): https://www.youtube.com/shorts/<영상 id> / Studio: <Studio 편집 주소>`. 같은 영상 id 줄이 있으면 건너뛴다.
3. **곡 목록 사용 기록**: `music.cuts`의 구간마다 곡 목록에 덧붙인다. 같은 영상·구간이 이미 있으면 건너뛴다.

   ```bash
   python - "<영상>" <<'EOF'
   import json, sys
   from pathlib import Path
   sys.stdout.reconfigure(encoding="utf-8")
   sys.path.insert(0, "music"); import songs
   v = Path(sys.argv[1]); name = v.name
   music = json.loads((v / "video.json").read_text(encoding="utf-8"))["music"]
   song = next(s for s in songs.load() if s["file"] == Path(music["src"]).name)
   for c in music["cuts"]:
       start, end = c[0], c[1]          # a third value is the stretch (music.py)
       if {"video": name, "start": float(start), "end": float(end)} in song["uses"]:
           print(f"이미 있음: {start}~{end}")
       else:
           songs.add_use(song["title"], name, start, end); print(f"덧붙임: {start}~{end}")
   EOF
   ```

4. **낙서 모음**: `<영상>/doodles/*.json`마다(고르지 않은 썸네일 시안처럼 영상과 썸네일에 쓰지 않은 낙서는 뺀다: 낙서 모음은 승인받은 낙서만 모은다) `PY doodles/storyboard.py add <파일> --seed <씨앗>`. 씨앗은 그 파일의 `seed` > `<영상>/storyboard/storyboard.json`의 `seed` 순이다. 같은 id면 모음의 것을 바꾸므로 다시 돌려도 된다. 모음 이름으로만 쓴 낙서는 `<영상>/doodles/`에 없어 넣을 것이 없다.
5. **요약 기록**(SKILL.md 성장 고리의 추리기, 회고를 하지 않아도 교훈이 다음 기획안에 닿게): `.claude/skills/shorts/references/summary.md`의 "다룬 주제"와 "최근 3개 영상"에 이 영상 한 줄을 더한다(최근은 3편만 남긴다). 기획 피드백 `docs/agents/planning-feedback.md`의 이 영상 제목 아래 "다음부터" 줄을 summary.md 교훈으로 추린다(review R5의 교훈 규칙대로, 10줄 안). 이미 있는 줄은 건너뛴다.
6. `active.py stage 10`을 부른다.
7. 연작은 마지막 편의 C4가 끝났을 때 한 번만(9단계로 남았던 편을 나중에 다시 올려 끝냈으면 그 실행에서 그 편 하나로 한 번): PushNotification으로 "업로드 완료"를 알리고, 대화에 편마다 Studio 편집 주소, 영상 주소, 공개·예약 일정, 게시 목록 `published.md`에 줄이 생겼다는 것을 알린다. 9단계로 남은 편이 있으면 함께 알린다. 사용자 할 일 한 가지: "Studio에서 썸네일과 저작권 검사 결과(문제 없음)를 확인해 주세요." 퍼블릭 도메인이나 CC BY 녹음도 Content ID가 잘못 걸릴 수 있다. 저작권 주장이 보이면 알려 달라고 덧붙인다(예약 편은 예약 시각 전에 비공개로 돌린다). 그 곡은 곡 목록에 그 사실을 적고, 다음부터는 추천하지 않는다. 끝에 한 줄 덧붙인다: "기억이 생생할 때 '회고하자'라고 하시면 제작 회고를 해요."

C4 완료: 1~7이 모두 되었다. 새 쇼츠는 `/shorts <주제>`로 받을 수 있다.
