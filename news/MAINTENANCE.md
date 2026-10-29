# On y va 뉴스 단어장 유지보수

원격 저장소: elisa0402-bot/fran-ais-flashcard
앱 경로: news/
기본 브랜치: main
어휘 원본: news/data.json
웹 주소: https://elisa0402-bot.github.io/fran-ais-flashcard/news/

## 어휘 추가

뉴스 브리핑의 프랑스어 표현만 추출한다. 전체 대화나 개인 학습 기록은 공개 저장소에 올리지 않는다.
JSON 형식은 schemaVersion=1, updated=한국 날짜, cards=누적 배열이다.
표현별 필수 필드는 id, fr, ko, examples이다. examples는 fr, ko가 있는 배열이다.
news 카드에는 deck=news, added=최초 날짜, dates=등장 날짜 목록, source=국제뉴스 브리핑을 넣는다.
같은 표현은 Core.normalize 규칙(NFKC, 소문자, 곧은 아포스트로피, 공백 정리)으로 중복을 합친다.
새 id는 news-와 정규화 표현 SHA256 앞 16자를 결합한다. 기존 id와 added는 변경하지 않는다.
예문은 자연스러운 실생활 프랑스어와 한국어 번역으로 작성한다. 실제 뉴스 사건에 관한 새로운 주장은 피한다.
가급적 예문은 1~2개로 유지한다. JSON을 검증하고 신규 수와 총수를 확인한다.

## 업데이트 게시

GitHub 파일을 최신 상태로 읽은 뒤 data.json을 병합한다. 다른 파일이나 기존 카드 페이지를 덮어쓰지 않는다.
단어만 추가할 때 data.json만 갱신해도 실행 중인 앱과 다음 실행이 자동으로 수신한다.
배포용 시작 데이터도 유지하려면 seed.js를 window.CARNET_SEED = [data JSON]; 형식으로 갱신한다.
기존 학습 기록은 localStorage의 onyva-news-carnet-v1이며 서버로 전송하지 않는다.
앱 코드 업데이트 때 sw.js의 캐시 버전을 올린다.

## 자동화 연결

한국시간 매일 09:00 현재 Codex 채팅의 자동화가 국제뉴스 원본 대화에서 새 브리핑을 확인한다.
원본 ChatGPT 대화 ID는 공개 저장소에 저장하지 않으며 자동화 프롬프트에만 둔다.
새 브리핑이 없거나 본문을 읽을 수 없으면 임의의 어휘를 생성하지 않는다.
최근 실행 이후 신규분 전체를 처리해서 잠든 컴퓨터 때문에 누락된 날짜도 따라잡는다.
신규 어휘가 있는 경우에만 알린다. 변화가 없으면 조용히 종료한다.
실패나 사용자 조치가 필요한 경우는 정확한 원인과 마지막 성공일을 알린다.
