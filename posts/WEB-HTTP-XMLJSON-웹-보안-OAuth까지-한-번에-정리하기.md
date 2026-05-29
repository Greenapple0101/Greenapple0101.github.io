---
title: "[WEB] HTTP, XML/JSON, 웹 보안, OAuth까지 한 번에 정리하기"
source: "https://velog.io/@yorange50/WEB-HTTP-XMLJSON-웹-보안-OAuth까지-한-번에-정리하기"
published: "2026-05-12T18:55:58.791Z"
tags: ""
backup_date: "2026-05-29T14:52:52.754165"
---

웹 기술을 깊게 이해한다는 것은 단순히 “API를 호출할 줄 안다”는 뜻이 아니다.

실무에서는 이런 질문에 답할 수 있어야 한다.

```text
브라우저가 서버에 요청을 보낼 때 실제로 무슨 일이 일어나는가?
HTTP 요청과 응답은 어떤 구조인가?
GET과 POST는 왜 다르게 쓰는가?
JSON과 XML은 무엇이 다르고 언제 쓰는가?
쿠키, 세션, JWT는 각각 어떤 문제를 해결하는가?
인증과 인가는 무엇이 다른가?
OAuth는 왜 등장했는가?
CORS, CSRF, XSS 같은 보안 이슈는 왜 생기는가?
```

이 글에서는 웹 백엔드, 클라우드, DevOps, MLOps 실무에서 자주 마주치는 웹 기술의 핵심을 정리한다.

---

## 1. 웹 기술을 왜 깊게 알아야 할까?

백엔드 서버를 만들거나 클라우드 환경에서 서비스를 운영하다 보면 문제는 단순히 코드 안에서만 생기지 않는다.

예를 들어 API 요청이 실패했을 때 원인은 다양하다.

```text
URL 경로가 틀림
HTTP 메서드가 틀림
요청 Body 형식이 틀림
Content-Type이 없음
인증 토큰이 없음
권한이 없음
CORS에 막힘
쿠키가 전송되지 않음
프록시나 로드밸런서 설정 문제
HTTPS 인증서 문제
```

이런 문제를 해결하려면 HTTP, 데이터 포맷, 인증/인가, 웹 보안 흐름을 같이 봐야 한다.

즉 웹 기술은 백엔드 개발자만의 지식이 아니라, 서버를 운영하고 배포하고 장애를 보는 사람에게도 필요한 기본기다.

---

# 2. HTTP란 무엇인가?

HTTP는 HyperText Transfer Protocol의 약자다.

브라우저와 서버가 데이터를 주고받기 위한 약속이다.

사용자가 브라우저에서 주소를 입력하면 브라우저는 서버에 HTTP 요청을 보낸다.

```text
브라우저 → HTTP Request → 서버
브라우저 ← HTTP Response ← 서버
```

예를 들어 사용자가 게시글 목록을 본다고 하자.

```text
GET /boards
```

브라우저나 클라이언트가 서버에 “게시글 목록을 줘”라고 요청하는 것이다.

서버는 그 요청을 처리한 뒤 응답을 보낸다.

```json
[
  {
    "id": 1,
    "title": "첫 번째 글"
  },
  {
    "id": 2,
    "title": "두 번째 글"
  }
]
```

---

# 3. HTTP 요청 구조

HTTP 요청은 보통 다음 요소로 구성된다.

```text
Request Line
Headers
Body
```

예시를 보면 이해가 쉽다.

```http
POST /boards HTTP/1.1
Host: localhost:8080
Content-Type: application/json
Authorization: Bearer xxxxx

{
  "title": "hello",
  "content": "world"
}
```

각 부분의 의미는 다음과 같다.

```text
POST /boards HTTP/1.1
→ 어떤 메서드로 어떤 경로에 요청하는지

Host: localhost:8080
→ 어느 서버에 요청하는지

Content-Type: application/json
→ 요청 본문이 JSON 형식이라는 뜻

Authorization: Bearer xxxxx
→ 인증 토큰

Body
→ 실제로 서버에 전달할 데이터
```

백엔드에서 API가 안 될 때는 이 구조를 하나씩 확인해야 한다.

```text
메서드가 맞는가?
URL이 맞는가?
헤더가 맞는가?
Body 형식이 맞는가?
인증 정보가 들어갔는가?
```

---

# 4. HTTP 응답 구조

HTTP 응답은 보통 다음 요소로 구성된다.

```text
Status Line
Headers
Body
```

예시는 다음과 같다.

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 1,
  "title": "hello"
}
```

여기서 중요한 것은 상태 코드다.

```text
200 OK
```

상태 코드는 서버가 요청을 어떻게 처리했는지 알려준다.

---

# 5. HTTP 메서드

HTTP 메서드는 클라이언트가 서버에 어떤 동작을 원하는지 표현한다.

| 메서드    | 의미    | 예시        |
| ------ | ----- | --------- |
| GET    | 조회    | 게시글 목록 조회 |
| POST   | 생성    | 새 게시글 작성  |
| PUT    | 전체 수정 | 게시글 전체 수정 |
| PATCH  | 부분 수정 | 제목만 수정    |
| DELETE | 삭제    | 게시글 삭제    |

예를 들어 게시글 API는 보통 이렇게 설계한다.

```text
GET /boards          → 게시글 목록 조회
GET /boards/1        → 1번 게시글 조회
POST /boards         → 게시글 생성
PUT /boards/1        → 1번 게시글 전체 수정
PATCH /boards/1      → 1번 게시글 일부 수정
DELETE /boards/1     → 1번 게시글 삭제
```

이런 방식이 REST API의 기본적인 형태다.

---

# 6. GET과 POST의 차이

GET은 데이터를 조회할 때 쓴다.

```http
GET /boards?page=1
```

GET 요청은 보통 Body를 사용하지 않고, 필요한 값을 URL의 Query Parameter로 보낸다.

```text
/boards?page=1&size=10
```

POST는 데이터를 생성하거나 서버 상태를 변경할 때 쓴다.

```http
POST /boards
Content-Type: application/json

{
  "title": "hello",
  "content": "world"
}
```

정리하면 다음과 같다.

| 항목     | GET                 | POST       |
| ------ | ------------------- | ---------- |
| 목적     | 조회                  | 생성/처리      |
| 데이터 위치 | URL query parameter | Body       |
| 캐싱     | 비교적 쉬움              | 보통 캐싱하지 않음 |
| 멱등성    | 보통 있음               | 보통 없음      |

멱등성이란 같은 요청을 여러 번 보내도 결과가 같다는 뜻이다.

예를 들어 `GET /boards/1`은 여러 번 호출해도 단순 조회이기 때문에 결과가 같다.

반면 `POST /orders`를 여러 번 보내면 주문이 여러 개 생성될 수 있다.

---

# 7. HTTP 상태 코드

상태 코드는 실무 트러블슈팅에서 매우 중요하다.

| 상태 코드   | 의미                     | 실무 해석            |
| ------- | ---------------------- | ---------------- |
| 200     | OK                     | 요청 성공            |
| 201     | Created                | 생성 성공            |
| 204     | No Content             | 성공했지만 응답 Body 없음 |
| 301/302 | Redirect               | 다른 URL로 이동       |
| 400     | Bad Request            | 요청 형식이 잘못됨       |
| 401     | Unauthorized           | 인증 안 됨           |
| 403     | Forbidden              | 권한 없음            |
| 404     | Not Found              | 경로 또는 리소스 없음     |
| 405     | Method Not Allowed     | HTTP 메서드 틀림      |
| 409     | Conflict               | 데이터 충돌           |
| 415     | Unsupported Media Type | Content-Type 문제  |
| 429     | Too Many Requests      | 요청 너무 많음         |
| 500     | Internal Server Error  | 서버 내부 오류         |
| 502     | Bad Gateway            | 게이트웨이/프록시 문제     |
| 503     | Service Unavailable    | 서비스 사용 불가        |
| 504     | Gateway Timeout        | 게이트웨이 타임아웃       |

예를 들어 `curl localhost:8080`을 했는데 404가 나오면 서버가 죽은 게 아니다.

서버는 응답하고 있지만 `/` 경로가 없다는 뜻이다.

반대로 다음 에러는 서버 포트에 연결 자체가 안 된 것이다.

```text
curl: (7) Failed to connect to localhost port 8080
```

이 둘은 완전히 다르게 봐야 한다.

---

# 8. HTTP Header

Header는 요청이나 응답에 대한 부가 정보를 담는다.

자주 보는 Header는 다음과 같다.

| Header        | 의미                 |
| ------------- | ------------------ |
| Content-Type  | Body의 데이터 형식       |
| Accept        | 클라이언트가 받고 싶은 응답 형식 |
| Authorization | 인증 정보              |
| Cookie        | 쿠키 정보              |
| Set-Cookie    | 서버가 쿠키 저장 요청       |
| User-Agent    | 클라이언트 정보           |
| Origin        | 요청 출처              |
| Referer       | 이전 페이지 정보          |
| Cache-Control | 캐시 정책              |

예를 들어 JSON 데이터를 보낼 때는 보통 이렇게 한다.

```bash
curl -X POST http://localhost:8080/boards \
  -H "Content-Type: application/json" \
  -d '{"title":"hello","content":"world"}'
```

`Content-Type`을 빼면 서버가 Body를 JSON으로 해석하지 못할 수 있다.

---

# 9. JSON이란?

JSON은 JavaScript Object Notation의 약자다.

웹 API에서 가장 많이 쓰이는 데이터 형식이다.

예시는 다음과 같다.

```json
{
  "id": 1,
  "title": "hello",
  "tags": ["spring", "api"],
  "published": true
}
```

JSON의 장점은 다음과 같다.

```text
가볍다
읽기 쉽다
JavaScript와 잘 맞는다
대부분의 언어에서 쉽게 파싱할 수 있다
REST API에서 표준처럼 쓰인다
```

Spring Boot에서는 JSON 요청을 받을 때 보통 `@RequestBody`를 사용한다.

```java
@PostMapping("/boards")
public Board createBoard(@RequestBody Board board) {
    return boardService.save(board);
}
```

클라이언트가 JSON을 보내면 Spring이 자동으로 Java 객체로 변환해준다.

이때 내부적으로 Jackson 같은 라이브러리가 사용된다.

---

# 10. XML이란?

XML은 eXtensible Markup Language의 약자다.

데이터를 태그 기반으로 표현하는 형식이다.

예시는 다음과 같다.

```xml
<board>
  <id>1</id>
  <title>hello</title>
  <content>world</content>
</board>
```

JSON보다 길고 무겁지만, 구조를 엄격하게 표현할 수 있다.

XML은 다음 영역에서 아직 많이 볼 수 있다.

```text
공공기관 API
금융권 시스템
레거시 시스템
SOAP API
설정 파일
문서 기반 데이터 교환
```

JSON과 XML을 비교하면 다음과 같다.

| 항목    | JSON         | XML              |
| ----- | ------------ | ---------------- |
| 구조    | Key-Value 중심 | 태그 중심            |
| 가독성   | 비교적 간단       | 비교적 장황           |
| 용량    | 작음           | 큼                |
| 웹 API | REST에서 많이 사용 | SOAP/레거시에서 많이 사용 |
| 스키마   | JSON Schema  | XSD              |
| 파싱    | 간단           | 상대적으로 복잡         |

요즘 신규 REST API는 대부분 JSON을 사용하지만, 회사 시스템에서는 XML을 만날 가능성이 충분히 있다.

---

# 11. 인증과 인가

웹 보안을 이해하려면 인증과 인가를 먼저 구분해야 한다.

```text
인증 Authentication
→ 너 누구야?

인가 Authorization
→ 너 이거 해도 돼?
```

예를 들어 로그인은 인증이다.

```text
아이디/비밀번호를 확인해서 사용자가 누구인지 확인
```

게시글 삭제 권한 확인은 인가다.

```text
이 사용자가 이 게시글을 삭제할 권한이 있는지 확인
```

상태 코드로 보면 보통 이렇게 연결된다.

```text
401 Unauthorized
→ 인증 실패

403 Forbidden
→ 인증은 됐지만 권한 없음
```

이 차이는 실무에서 중요하다.

401이 나면 “로그인/토큰 문제인가?”를 봐야 하고, 403이 나면 “권한/Role 문제인가?”를 봐야 한다.

---

# 12. 쿠키와 세션

HTTP는 기본적으로 stateless하다.

stateless란 서버가 이전 요청을 기억하지 않는다는 뜻이다.

예를 들어 사용자가 로그인을 했더라도, 다음 요청에서 서버는 그 사용자가 방금 로그인한 사람인지 기본적으로 모른다.

그래서 상태를 유지하기 위한 방식이 필요하다.

대표적인 방식이 쿠키와 세션이다.

## 쿠키

쿠키는 브라우저에 저장되는 작은 데이터다.

서버는 응답에 `Set-Cookie` 헤더를 담아 브라우저에게 쿠키 저장을 요청할 수 있다.

```http
Set-Cookie: sessionId=abc123
```

이후 브라우저는 같은 서버로 요청을 보낼 때 쿠키를 자동으로 같이 보낸다.

```http
Cookie: sessionId=abc123
```

## 세션

세션은 서버 쪽에 저장되는 사용자 상태 정보다.

흐름은 다음과 같다.

```text
1. 사용자가 로그인한다
2. 서버가 세션을 만든다
3. 서버가 sessionId를 쿠키로 내려준다
4. 브라우저는 이후 요청마다 sessionId 쿠키를 보낸다
5. 서버는 sessionId로 서버 안의 세션 정보를 찾는다
```

즉 쿠키는 브라우저 쪽 저장소, 세션은 서버 쪽 저장소라고 볼 수 있다.

---

# 13. JWT

JWT는 JSON Web Token의 약자다.

사용자 정보를 JSON 형태로 담고, 서명해서 위조 여부를 확인할 수 있는 토큰이다.

JWT는 보통 다음 구조를 가진다.

```text
Header.Payload.Signature
```

예시 형태는 이렇다.

```text
xxxxx.yyyyy.zzzzz
```

JWT 기반 인증 흐름은 다음과 같다.

```text
1. 사용자가 로그인한다
2. 서버가 JWT를 발급한다
3. 클라이언트가 JWT를 저장한다
4. 이후 요청마다 Authorization 헤더에 JWT를 넣는다
5. 서버는 JWT 서명을 검증하고 사용자를 식별한다
```

요청 예시는 다음과 같다.

```bash
curl -H "Authorization: Bearer 토큰값" http://localhost:8080/api/me
```

JWT의 장점은 서버가 세션 저장소를 반드시 유지하지 않아도 된다는 점이다.

하지만 단점도 있다.

```text
토큰이 탈취되면 만료 전까지 위험할 수 있음
토큰 폐기가 세션보다 어렵다
Payload는 암호화가 아니라 인코딩에 가깝기 때문에 민감정보를 넣으면 안 됨
```

JWT는 편하지만 보안적으로 조심해서 써야 한다.

---

# 14. OAuth란?

OAuth는 다른 서비스의 자원에 접근할 수 있도록 권한을 위임하는 프로토콜이다.

쉽게 말하면 이런 상황에서 등장한다.

```text
내 서비스가 사용자의 Google 계정 정보를 일부 가져오고 싶다
내 서비스가 사용자의 GitHub Repository 목록을 읽고 싶다
내 서비스가 사용자의 Kakao 프로필 정보를 가져오고 싶다
```

이때 사용자의 Google 비밀번호를 내 서비스에 직접 입력하게 하면 위험하다.

그래서 OAuth는 비밀번호를 공유하지 않고, 제한된 권한만 위임하는 방식을 제공한다.

---

# 15. OAuth 2.0의 핵심 등장인물

OAuth에는 주요 역할이 있다.

| 역할                   | 의미                 |
| -------------------- | ------------------ |
| Resource Owner       | 자원 소유자, 보통 사용자     |
| Client               | 자원에 접근하려는 애플리케이션   |
| Authorization Server | 인증과 권한 부여를 담당하는 서버 |
| Resource Server      | 실제 자원을 가지고 있는 서버   |

예를 들어 “내 서비스에서 Google 로그인하기”를 생각해보자.

```text
Resource Owner → 사용자
Client → 내 서비스
Authorization Server → Google 인증 서버
Resource Server → Google API 서버
```

---

# 16. OAuth 흐름

가장 대표적인 흐름은 Authorization Code Flow다.

```text
1. 사용자가 내 서비스에서 Google 로그인 버튼을 누른다
2. 사용자는 Google 로그인 페이지로 이동한다
3. 사용자가 로그인하고 권한 제공에 동의한다
4. Google은 내 서비스의 redirect_uri로 authorization code를 보낸다
5. 내 서버는 authorization code를 Google에 보내 access token을 받는다
6. 내 서버는 access token으로 Google API를 호출한다
7. 사용자 정보를 받아 내 서비스 로그인 처리를 한다
```

핵심은 사용자의 Google 비밀번호가 내 서비스에 직접 전달되지 않는다는 것이다.

내 서비스는 비밀번호 대신 access token을 받는다.

---

# 17. Access Token과 Refresh Token

OAuth나 JWT 기반 인증에서 자주 나오는 개념이 Access Token과 Refresh Token이다.

## Access Token

Access Token은 실제 API 접근에 사용하는 토큰이다.

```text
Authorization: Bearer access_token
```

보통 만료 시간을 짧게 둔다.

이유는 탈취됐을 때 피해를 줄이기 위해서다.

## Refresh Token

Refresh Token은 Access Token을 다시 발급받기 위한 토큰이다.

Access Token보다 더 오래 유효한 경우가 많다.

대신 더 안전하게 보관해야 한다.

정리하면 다음과 같다.

| 토큰            | 목적               | 만료 시간 |
| ------------- | ---------------- | ----- |
| Access Token  | API 접근           | 짧게    |
| Refresh Token | Access Token 재발급 | 길게    |

---

# 18. CORS

CORS는 Cross-Origin Resource Sharing의 약자다.

브라우저가 보안상 다른 출처의 요청을 제한하는 정책과 관련이 있다.

출처 Origin은 다음 세 가지로 결정된다.

```text
프로토콜
도메인
포트
```

예를 들어 다음 둘은 다른 Origin이다.

```text
http://localhost:5173
http://localhost:8080
```

포트가 다르기 때문이다.

React/Vite 프론트엔드는 5173에서 돌고, Spring Boot 백엔드는 8080에서 돌면 브라우저 입장에서는 서로 다른 출처다.

그래서 CORS 설정이 필요할 수 있다.

자주 보는 에러는 이런 식이다.

```text
Access to fetch at 'http://localhost:8080/api' from origin 'http://localhost:5173' has been blocked by CORS policy
```

Spring Boot에서는 컨트롤러에 임시로 이렇게 붙일 수 있다.

```java
@CrossOrigin(origins = "http://localhost:5173")
@RestController
public class BoardController {
}
```

하지만 실무에서는 보통 전역 CORS 설정을 따로 둔다.

---

# 19. Preflight 요청

CORS에서 중요한 개념이 Preflight 요청이다.

브라우저는 위험할 수 있는 요청을 보내기 전에 먼저 OPTIONS 요청을 보낼 수 있다.

```http
OPTIONS /api/boards
Origin: http://localhost:5173
Access-Control-Request-Method: POST
```

서버가 “이 Origin과 Method를 허용한다”고 응답하면 그때 실제 요청을 보낸다.

즉, 개발자가 POST 요청을 보냈다고 생각했는데 서버 로그에는 OPTIONS가 먼저 찍힐 수 있다.

이걸 모르면 “왜 내가 보낸 적 없는 OPTIONS가 오지?”라고 헷갈릴 수 있다.

---

# 20. XSS

XSS는 Cross-Site Scripting의 약자다.

공격자가 웹 페이지에 악성 스크립트를 삽입하는 공격이다.

예를 들어 게시판 댓글에 이런 값을 넣는다고 하자.

```html
<script>alert('hacked')</script>
```

이 값이 그대로 페이지에 렌더링되면 사용자의 브라우저에서 스크립트가 실행될 수 있다.

XSS를 막으려면 다음이 중요하다.

```text
사용자 입력을 그대로 HTML에 삽입하지 않기
출력 시 escape 처리하기
Content Security Policy 적용하기
쿠키에 HttpOnly 옵션 사용하기
```

특히 JWT나 세션 쿠키가 탈취되면 계정 탈취로 이어질 수 있다.

---

# 21. CSRF

CSRF는 Cross-Site Request Forgery의 약자다.

사용자가 로그인된 상태를 악용해서 원치 않는 요청을 보내게 만드는 공격이다.

예를 들어 사용자가 은행 사이트에 로그인한 상태라고 하자.

공격자가 만든 페이지에 접속했을 때, 그 페이지가 몰래 은행 서버로 송금 요청을 보내게 만들 수 있다.

브라우저는 해당 사이트의 쿠키를 자동으로 같이 보낼 수 있기 때문에 문제가 된다.

CSRF 방어 방법은 다음과 같다.

```text
CSRF Token 사용
SameSite Cookie 설정
중요 요청에 추가 인증 요구
GET 요청으로 상태 변경하지 않기
```

---

# 22. HTTPS와 TLS

HTTP는 기본적으로 평문 통신이다.

중간에서 누군가 패킷을 보면 내용이 노출될 수 있다.

HTTPS는 HTTP에 TLS 암호화를 적용한 것이다.

```text
HTTP + TLS = HTTPS
```

HTTPS를 사용하면 다음을 보호할 수 있다.

```text
기밀성: 중간에서 내용을 읽기 어렵게 함
무결성: 통신 중 데이터 변조를 감지
인증: 서버가 진짜 그 서버인지 인증서로 확인
```

실무에서는 HTTPS 인증서 만료도 중요한 장애 포인트다.

인증서가 만료되면 브라우저나 클라이언트가 연결을 차단할 수 있다.

---

# 23. 웹 보안에서 자주 보는 쿠키 옵션

쿠키를 사용할 때는 옵션이 중요하다.

| 옵션                | 의미                       |
| ----------------- | ------------------------ |
| HttpOnly          | JavaScript에서 쿠키 접근 차단    |
| Secure            | HTTPS에서만 쿠키 전송           |
| SameSite          | Cross-site 요청에서 쿠키 전송 제한 |
| Max-Age / Expires | 쿠키 만료 시간                 |
| Path              | 쿠키가 적용되는 경로              |
| Domain            | 쿠키가 적용되는 도메인             |

예를 들어 세션 쿠키는 보통 이런 옵션을 고려한다.

```http
Set-Cookie: sessionId=abc123; HttpOnly; Secure; SameSite=Lax
```

`HttpOnly`는 XSS로 JavaScript가 쿠키를 훔치는 것을 어렵게 만든다.

`Secure`는 HTTPS 환경에서만 쿠키가 전송되게 한다.

`SameSite`는 CSRF 방어에 도움이 된다.

---

# 24. 웹 API 트러블슈팅 순서

API 요청이 안 될 때는 다음 순서로 보면 좋다.

```text
1. URL이 맞는가?
2. HTTP Method가 맞는가?
3. Header가 맞는가?
4. Content-Type이 맞는가?
5. Body JSON 형식이 맞는가?
6. 인증 토큰이 들어갔는가?
7. 권한이 있는가?
8. CORS 에러인가?
9. 서버 로그에 예외가 있는가?
10. 프록시, 로드밸런서, HTTPS 설정 문제인가?
```

예를 들어 401이면 인증부터 본다.

```text
토큰 없음
토큰 만료
Authorization 헤더 형식 오류
Bearer 누락
```

403이면 권한을 본다.

```text
Role 부족
소유자 불일치
관리자 API 접근 시도
```

415면 Content-Type을 본다.

```text
Content-Type: application/json 누락
서버가 지원하지 않는 형식
```

500이면 서버 로그를 본다.

```text
NullPointerException
DB 연결 실패
외부 API 실패
JSON 파싱 실패
```

---

# 25. curl로 연습하기

웹 기술은 curl로 직접 쳐보면 빨리 는다.

GET 요청:

```bash
curl http://localhost:8080/boards
```

POST JSON 요청:

```bash
curl -X POST http://localhost:8080/boards \
  -H "Content-Type: application/json" \
  -d '{"title":"hello","content":"world"}'
```

Authorization 헤더 포함:

```bash
curl http://localhost:8080/api/me \
  -H "Authorization: Bearer 토큰값"
```

응답 헤더까지 보기:

```bash
curl -i http://localhost:8080/boards
```

요청/응답 상세 보기:

```bash
curl -v http://localhost:8080/boards
```

리다이렉트 따라가기:

```bash
curl -L http://example.com
```

이 정도만 익혀도 API 디버깅이 훨씬 쉬워진다.

---

# 26. 실무적으로 정리하면

웹 기술에 대한 심도 있는 이해는 결국 다음을 연결해서 볼 수 있는 능력이다.

```text
HTTP 요청/응답 구조
HTTP Method
Status Code
Header
JSON/XML 데이터 포맷
쿠키/세션/JWT
인증과 인가
OAuth 흐름
CORS
XSS
CSRF
HTTPS/TLS
API 트러블슈팅
```

하나씩 따로 외우는 게 아니라, 실제 요청 하나를 기준으로 보면 이해가 잘 된다.

예를 들어 로그인된 사용자가 게시글을 작성하는 요청은 이렇게 볼 수 있다.

```http
POST /boards HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer access_token

{
  "title": "hello",
  "content": "world"
}
```

이 요청 안에는 많은 개념이 들어 있다.

```text
POST → 생성 요청
/boards → API 경로
Content-Type → JSON 요청
Authorization → 인증 토큰
Bearer access_token → JWT 또는 OAuth 기반 접근 토큰
Body → 서버에 전달할 데이터
응답 코드 → 성공/실패 판단
```

즉 웹 기술을 깊게 안다는 것은 이 한 요청을 보고 어디서 문제가 생길 수 있는지 예측할 수 있다는 뜻이다.

---

# 27. 결론

HTTP, XML/JSON, 웹 보안, OAuth 같은 개념은 백엔드 개발자만의 지식이 아니다.

클라우드, DevOps, MLOps, 인프라 운영에서도 매우 자주 나온다.

서비스가 안 될 때 단순히 “서버가 죽었나?”만 보는 것이 아니라,

```text
요청이 올바른가?
응답 상태 코드는 무엇인가?
JSON 형식은 맞는가?
인증 토큰은 있는가?
권한은 충분한가?
CORS에 막힌 건 아닌가?
쿠키 정책 문제는 아닌가?
HTTPS 인증서 문제는 아닌가?
```

이렇게 볼 수 있어야 한다.

결국 웹 기술의 핵심은 요청과 응답을 읽는 능력이다.

HTTP 요청 하나를 보고 메서드, 경로, 헤더, Body, 인증, 보안, 응답 코드까지 해석할 수 있으면 실무에서 API 문제를 훨씬 빠르게 해결할 수 있다.