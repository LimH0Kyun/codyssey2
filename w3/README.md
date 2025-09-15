# 스토리
아주 단순한 웹서버는 만들었지만 여전히 제대로 된 웹서버는 아직 멀었다. 단순한 메시지가 아니라 내가 만든 조금은 더 그럴듯한 웹 페이지를 보여주고 싶다. 그리고 쓸만한 이미지들도 포함한 웹페이지를 보여주고 싶다. 그리고 사용자들의 요청이 얼마나 오고 있는지 분석도 하고 싶다.

시간이 많으니 이런 저런 생각들도 많이 떠오르긴 하지만 모두다 좋은 생각만은 아니기에 무엇인가라도 계속 몰두할 것이 필요했다. 그런 용도로 언제인지 모르지만 홈페이지 만들기는 좋은 소일거리가 되어 주었다.

---
## 구현 개요 (요약)
- 표준 라이브러리 `http.server` 의 `HTTPServer`, `BaseHTTPRequestHandler` 를 이용해 8080 포트 HTTP 서버 구현
- `index.html` (우주 해적 소개 페이지) 를 루트(`/` 또는 `/index.html`) 요청 시 200(OK) 로 응답
- 매 요청마다 서버 콘솔에 접속 시간(UTC) 과 클라이언트 IP, 경로 출력: `[ACCESS] time=... ip=... path=...`
- 기타 경로는 404 처리
- 외부 서드파티 패키지 전혀 사용하지 않음

## 파일 구성
```
w3/
  web_server.py   # 서버 실행 스크립트
  index.html      # 제공되는 우주 해적 소개 페이지
  README.md       # 요구사항 + 사용 방법
```

## 실행 방법
Python 3.x 환경에서 아래 명령을 실행합니다.
```
python w3/web_server.py
```
출력 예:
```
Starting HTTP server on 0.0.0.0:8080
[ACCESS] time=2025-09-15 12:34:56 UTC ip=127.0.0.1 path=/
```
브라우저에서 `http://127.0.0.1:8080/` 에 접속하면 `index.html` 이 렌더링됩니다.

## 동작 확인 체크리스트
| 요구사항 | 구현 여부 | 비고 |
|----------|-----------|------|
| http.server 사용 | O | `web_server.py` 내 `HTTPServer`, `BaseHTTPRequestHandler` |
| 포트 8080 | O | 상수 `PORT = 8080` |
| 200 응답 전송 | O | 루트/`/index.html` GET 시 `send_response(200)` |
| index.html 작성 (우주 해적 소개) | O | 풍부한 HTML/CSS 포함 |
| index.html 읽어 전송 | O | 바이너리 read 후 `wfile.write` |
| 접속 시 시간/IP 출력 | O | `print(format_log(...))` |
| 표준 라이브러리만 사용 | O | 추가 import 없음 |
| PEP8 스타일 준수 | O | snake_case / CapWords / 공백 규칙 적용 |
| 경고 없이 실행 | O | 기본 실행 테스트 완료 |

## 보너스 과제 (아이디어)
IP 기반 위치 조회는 외부 API 가 필요하므로 제약(외부 라이브러리 금지) 하에서는 직접 호출이 제한될 수 있습니다. 허용된다면 표준 라이브러리 `urllib.request` 로 공개 GeoIP JSON API (예: `http://ip-api.com/json/<ip>` ) 를 호출하여 결과를 캐싱 후 로그에 함께 출력할 수 있습니다. (네트워크 접근 정책 허용 시에만 권장)

예시 (추가 가능):
```python
from urllib.request import urlopen
import json

def geo_lookup(ip):
    try:
        with urlopen(f'http://ip-api.com/json/{ip}?fields=country,city,query', timeout=2) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return f"{data.get('country','?')}/{data.get('city','?')}"
    except Exception:
        return 'UNKNOWN'
```
`format_log` 에 위치 문자열을 덧붙이면 됩니다.

## 추가 개선 여지
- 간단한 액세스 로그를 파일(`access.log`) 로도 남기기
- 정적 자산(css, 이미지) 서빙을 위한 경로 매핑 추가
- Keep-Alive / gzip (요구사항엔 없으나 성능 향상 가능)
- 간단한 요청 수 카운터 및 /metrics 엔드포인트 제공

---
이 구현은 주어진 README 요구사항을 모두 충족합니다.
