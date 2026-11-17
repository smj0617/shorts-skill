# 곡 받기 절차

[flows/start.md](../flows/start.md)의 곡 추천(S5)과 곡 받기(S6)가 가리킬 때만 읽는다. 곡 고르기 기준과 샘플은 start.md S5에 있다.

## 보관함에서 받기

Claude가 Chrome에서 한다.

1. Chrome에서 `https://studio.youtube.com/channel/mine/music`를 연다(사용자의 Studio 로그인을 쓴다. 로그인 화면이 나오면 사용자에게 로그인해 달라고 하고 기다린다).
2. 검색창("보관함 검색 또는 필터링")에 보관함 클래식 목록의 제목을 넣고 Enter. 같은 이름의 다른 사람 곡이 함께 나온다(예: Kevin MacLeod의 "Dance of the Sugar Plum Fairies"는 CC BY 곡이다). 제목에 "(by 작곡가)"가 붙고 아티스트·길이가 목록과 같은 줄만 받는다.
3. 그 줄의 라이선스를 데이터로 확인한다. 줄 버튼의 설명 글은 CC 곡에도 "YouTube 오디오 보관함 라이선스"라고 붙어 있어 믿지 않는다. 페이지에서 `document.querySelector('ytmus-library-table').polymerController.__data.audioTracks`를 읽어 그 곡의 `licenseType`이 `CREATOR_MUSIC_LICENSE_TYPE_YOUTUBE`인지 본다(화면에서는 라이선스 칸 아이콘이 CC가 아니라 재생 모양). 아니면 받지 않고 알린다. 맞으면 그 줄의 "오프라인 저장" 버튼을 누른다. 몇 초 안에 다운로드 폴더에 `<제목> - <아티스트>.mp3`로 저장된다.
4. `python music/songs.py record --title "<보관함 제목>" --composer "<작곡가 전체 이름>" --artist "<보관함 아티스트>" --license no-attribution`로 곡 목록에 적는다. 이 명령이 다운로드 폴더의 파일을 `music/`으로 옮기므로 먼저 손으로 옮기지 않는다(옮겨 두면 "곡 파일이 없다" 오류). `music/library-classical.md`의 받음 칸을 "받음"으로 고친다.
5. 다 받으면 연 탭을 닫는다.
6. Chrome을 쓸 수 없으면 사용자 할 일로 바꾼다: "오디오 보관함에서 <제목>을 받아 주세요. 다 받으면 '받았어'라고 알려 주세요." 한 곡씩 알리고, "받았어"가 오면 4를 한다.

## Commons에서 찾기

보관함에 주제에 맞는 곡이 없고 사용자가 원할 때.

- `python music/find_music.py search "<작곡가 작품명, 영어>"`(예: "Grieg Peer Gynt", "Marine Band Strauss"). 라이선스 규칙과 위험도 규칙의 원본은 `music/find_music.py` 첫 주석이다.
- 후보는 위험도 "낮음"에서만 2~3개 낸다. 후보마다 곡명, 연주자, 길이, 파일 이름과 크기, 라이선스와 위험도 까닭, 파일 페이지 링크를 적는다. 사용자는 그 페이지의 재생기로 받지 않고 바로 들어 본다.
- 기획안에 "고르시면 기획안 승인 뒤 그 파일을 Wikimedia Commons에서 받습니다"라고 적는다. 사용자가 후보 번호를 직접 말한 것이 그 파일(이름·크기를 적은 것)을 받는 승인이다. 답하지 않아 추천대로 정해진 것은 받는 승인이 아니다. 그때는 S6에서 받기 전에 그 파일을 받을지 한 번 묻는다. 받기는 S6(기획안 승인 뒤)에만 한다.
- "확인 필요" 후보는 사용자가 원할 때만 까닭과 함께 보인다.

## 곡 받기

승인 뒤(S6) 고른 곡이 아직 곡 목록에 없을 때.

- **보관함 클래식 곡인데 아직 안 받았으면**(샘플 없이 골랐을 때): 위 "보관함에서 받기"로 Claude가 묻지 않고 받는다(보관함 클래식 목록의 곡은 묻지 않고 받는다, 2026-11-15 사용자, start.md S5 "곡 추천" 6).
- **Commons 후보**(S5에서 사용자가 고른 것): Claude가 받는다.
  1. `python music/find_music.py fetch "File:<파일 이름>" --title "<곡명>" --composer "<작곡가>" --performer "<연주자>"`. 받기 직전에 라이선스를 다시 읽고, 크기와 SHA-1을 대조하고, 증거를 `music/licenses/<이름>.json`에 남기고, 곡 목록에 기록한다.
  2. 라이선스가 바뀌어 멈추면 그렇다고 알리고 S5의 다른 후보를 고르게 한다.
  3. `python music/songs.py attribution --title "<곡명>"`로 저장된 출처 표기를 보여 준다.
- **보관함 클래식 목록에 없는 보관함 곡**(사용자가 그 곡을 원한 경우, 또는 Chrome을 쓸 수 없을 때): 사용자 할 일을 한 단계씩 알려 준다.
  1. "오디오 보관함에서 <곡명>을 받아 주세요. 다 받으면 '받았어'와 함께, CC 곡이면 보관함의 표기 문구를 그대로 붙여 넣고 아니면 '표시 필요 없음'이라고 알려 주세요."
- 사용자가 "받았어"라고 하면 곡 목록에 기록한다(다운로드 폴더에서 가장 최근의 그 곡 파일을 찾아 `music/`으로 옮긴다).
  - 표시 필요 없음: `python music/songs.py record --title "<곡명>" --composer "<작곡가>" --artist "<연주자>" --license no-attribution`
  - CC: 사용자가 붙여 넣은 문구를 한 글자도 바꾸지 않고 `.scratch/<영상 이름>/attribution.txt`에 저장한 뒤 `... --license cc --attribution-file .scratch/<영상 이름>/attribution.txt`
  - 사용자가 라이선스를 알려 주지 않았으면 기록하지 않고 그것만 묻는다.
- 기록 뒤 `python music/songs.py attribution --title "<곡명>"`로 저장된 출처 표기를 보여 준다.
