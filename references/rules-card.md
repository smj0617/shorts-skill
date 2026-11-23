# 쇼츠 규칙 카드 (긴 대화·압축 뒤에 훅이 다시 넣는다)

긴 대화에서 처음 읽은 규칙이 묻혀 어겼다(addressbar-2: 250k~350k에서 3번). 원본은 `.claude/skills/shorts/SKILL.md`·`docs/agents/shorts-defaults.md`, 헷갈리면 다시 Read 한다. 넣고 빼는 기준은 위반 장부 집계(`.scratch/rule-stats.md`), 15줄 한도.

- 승인은 기획안(2)과 미리보기(6, 다 본 뒤 `/shorts complete`) 두 번. 게시 명령은 7단계의 명시적인 "네" 없이는 부르지 않는다. TTS는 대본 전체를 보이고 "네"를 받은 뒤에만.
- 검사(`check_parallel.py`·`hyperframes check`)와 점검(점검표 검토 에이전트)은 렌더 직전 complete C1에서 한 번뿐. 5·6단계 확인은 snapshot만(훅이 막음).
- 단계를 넘길 때는 `active.py stage <번호> --video <영상>`을 먼저 부른다(동시 진행 중이면 `--video` 필수).
- 사용자 의견·결정은 들어오는 대로 spec `## 의견 목록`에 날짜와 함께 적는다. 그림 의견은 `doodles/rules.md` 피드백에도.
- 승인된 곡 구간·문구·연출을 제작 중 바꿀 땐 적용 전에 묻는다. 의견을 물으면("어때?") 파일을 고치지 말고 답만.
- 고를 것이 여럿이면 번호마다 추천을 붙이고, 답 없는 번호는 추천대로 정했다고 한 줄 알린다.
- 같은 것을 세 번째로 다시 보이게 되면 하나를 또 고치지 말고 까닭 한 줄 + 후보 3개.
- `make_props.py --board`, `.harness/*/build_board.py`처럼 storyboard.json을 덮어쓰는 스크립트는 인계 메모가 막으면 돌리지 않는다.
- 사용자 시각은 분:초 + 나레이션 몇 마디로, 바뀐 곳마다 Studio 바로가기.
- 160k부터 새 큰 일을 시작하지 않고 의견 묶음·단계가 끝나는 경계에서 넘긴다. 큰 출력·낱장 이미지는 메인 대화에 들이지 않는다(요약·모음 한 장·`--zoom`).
- 대화가 200k 토큰을 넘거나 한 번이라도 압축됐으면 하던 일을 마치는 대로 인계 메모(상태와 사실만, 규칙·절차는 적지 않음)를 쓰고 새 세션을 연다(`mcp__ccd_session__start_session`, 없으면 `orca agent launch --agent claude --surface chat --prompt "<브리프>" --json`). 훅이 그때까지 끝내기를 막는다.
