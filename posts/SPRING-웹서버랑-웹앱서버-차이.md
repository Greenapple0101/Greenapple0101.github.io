---
title: "[SPRING] 웹서버랑 웹앱서버 차이"
source: "https://velog.io/@yorange50/SPRING-웹서버랑-웹앱서버-차이"
published: "2026-05-14T04:00:26.898Z"
tags: ""
backup_date: "2026-05-29T14:52:52.743102"
---

웹서버랑 웹앱서버 차이는 한 줄로 이렇게 잡으면 돼.

```text
웹서버, Nginx
= 요청을 받아서 정적 파일을 주거나, 뒤쪽 서버로 넘겨주는 서버

웹앱서버, Tomcat
= Java/Spring 애플리케이션 코드를 실행해서 동적인 응답을 만들어주는 서버
```

# 1. 웹서버란?

웹서버는 클라이언트의 HTTP 요청을 받는 서버다.

대표적으로:

```text
Nginx
Apache HTTP Server
```

가 있다.

웹서버는 주로 이런 일을 한다.

```text
HTML 파일 응답
CSS 파일 응답
JavaScript 파일 응답
이미지 응답
동영상 응답
요청을 다른 서버로 전달
HTTPS 처리
로드밸런싱
```

예를 들어 브라우저가 이런 요청을 보냈다고 해보자.

```http
GET /index.html
```

그러면 Nginx는 서버에 있는 `index.html` 파일을 찾아서 그대로 응답할 수 있다.

```text
브라우저
  ↓
Nginx
  ↓
index.html 응답
```

이런 걸 **정적 파일 제공**이라고 한다.

정적 파일은 이미 만들어져 있는 파일이다.

```text
index.html
style.css
main.js
logo.png
```

즉, 웹서버는 이미 존재하는 파일을 빠르게 전달하는 데 강하다.

---

# 2. 웹앱서버란?

웹앱서버는 말 그대로 **웹 애플리케이션을 실행하는 서버**다.

대표적으로 Java 진영에서는:

```text
Tomcat
Jetty
WildFly
```

같은 것들이 있다.

Spring Boot를 실행하면 보통 내부적으로 Tomcat이 같이 뜬다.

로그에서 이런 걸 본 적 있을 거야.

```text
Tomcat started on port 8080
```

이 말은:

```text
Spring Boot 애플리케이션 안에 내장 Tomcat이 실행됐고,
8080 포트에서 요청을 받을 준비가 됐다
```

는 뜻이다.

---

# 3. Tomcat은 뭘 하냐?

Tomcat은 Java 웹 애플리케이션을 실행한다.

예를 들어 Spring Controller에 이런 코드가 있다고 해보자.

```java
@GetMapping("/hello")
public String hello() {
    return "hello";
}
```

브라우저가 `/hello`로 요청을 보내면 단순 파일을 주는 게 아니라, Java 코드가 실행된다.

```text
브라우저
  ↓
Tomcat
  ↓
Spring Controller 실행
  ↓
"hello" 응답 생성
```

즉, Tomcat은 이런 동적인 처리를 담당한다.

```text
DB 조회
로그인 처리
회원가입 처리
게시글 작성
주문 생성
API 응답 생성
```

예를 들어 게시글 목록을 요청한다고 해보자.

```http
GET /boards
```

이 요청은 단순히 `/boards.html` 파일을 주는 게 아닐 수 있다.

Spring Boot는 DB에서 게시글 목록을 조회하고, 그 결과를 JSON이나 HTML로 만들어서 응답한다.

```text
브라우저
  ↓
Tomcat
  ↓
Spring Controller
  ↓
Service
  ↓
Repository
  ↓
DB
  ↓
응답 생성
```

이런 게 **동적 응답**이다.

---

# 4. 정적 응답과 동적 응답 차이

## 정적 응답

이미 만들어진 파일을 그대로 주는 것.

```text
HTML
CSS
JS
이미지
```

예시:

```text
사용자 요청: /logo.png
서버 응답: logo.png 파일 그대로 반환
```

이런 건 Nginx가 잘한다.

---

## 동적 응답

요청이 들어올 때마다 서버 코드가 실행되어 결과가 달라질 수 있는 것.

예시:

```text
사용자 요청: /my-page
서버 처리:
  1. 로그인한 사용자 확인
  2. DB에서 사용자 정보 조회
  3. 주문 내역 조회
  4. 화면 또는 JSON 생성
```

이런 건 Tomcat 같은 웹앱서버가 담당한다.

---

# 5. Nginx와 Tomcat 차이 표

| 구분         | Nginx                | Tomcat                        |
| ---------- | -------------------- | ----------------------------- |
| 종류         | 웹서버                  | 웹 애플리케이션 서버                   |
| 주 역할       | 정적 파일 제공, 프록시, 로드밸런싱 | Java/Spring 애플리케이션 실행         |
| 잘하는 일      | 빠른 파일 응답, 요청 분배      | 비즈니스 로직 실행                    |
| 대표 포트      | 80, 443              | 8080                          |
| 동적 처리      | 직접 비즈니스 로직 처리하지 않음   | Controller, Service, DB 로직 실행 |
| Spring과 관계 | 보통 앞단에 둠             | Spring Boot 안에 내장되는 경우 많음     |

---

# 6. 실무에서는 둘을 같이 쓴다

Spring Boot 앱은 Tomcat만 있어도 실행된다.

```bash
java -jar app.jar
```

그러면 내장 Tomcat이 실행되고, 보통 8080 포트에서 요청을 받는다.

```text
브라우저
  ↓
Spring Boot 내장 Tomcat
  ↓
Controller
```

그런데 운영 환경에서는 앞에 Nginx를 두는 경우가 많다.

```text
사용자
  ↓
Nginx
  ↓
Spring Boot / Tomcat
  ↓
DB
```

왜 굳이 Nginx를 앞에 둘까?

---

# 7. Nginx를 앞에 두는 이유

## 1. 80, 443 포트를 받기 좋음

사용자는 보통 이렇게 접속한다.

```text
https://example.com
```

이때 기본 포트는 443이다.

Nginx가 443 포트로 요청을 받고, 내부의 Spring Boot 8080 포트로 넘긴다.

```text
사용자
  ↓
https://example.com:443
  ↓
Nginx
  ↓
localhost:8080
  ↓
Spring Boot
```

사용자는 8080을 몰라도 된다.

---

## 2. HTTPS 인증서 처리를 맡길 수 있음

HTTPS를 쓰려면 인증서 설정이 필요하다.

이걸 Spring Boot에 직접 넣을 수도 있지만, 운영에서는 Nginx에서 처리하는 경우가 많다.

```text
사용자 HTTPS 요청
  ↓
Nginx에서 SSL/TLS 처리
  ↓
Spring Boot에는 HTTP로 전달
```

이걸 SSL termination이라고도 한다.

---

## 3. 정적 파일을 빠르게 줄 수 있음

이미지, CSS, JS 같은 파일은 Spring Boot까지 보내지 않고 Nginx가 바로 줄 수 있다.

```text
/static/logo.png 요청
  ↓
Nginx가 바로 응답
```

그러면 Spring Boot는 API 처리 같은 핵심 로직에 집중할 수 있다.

---

## 4. 로드밸런싱 가능

Spring Boot 서버를 여러 개 띄워두고 Nginx가 요청을 나눠줄 수 있다.

```text
사용자
  ↓
Nginx
  ├── Spring Boot 1
  ├── Spring Boot 2
  └── Spring Boot 3
```

이렇게 하면 한 서버에만 트래픽이 몰리지 않는다.

---

## 5. 리버스 프록시 역할

Nginx는 앞단에서 요청을 받아서 뒤쪽 서버로 전달한다.

```text
/api 요청 → Spring Boot로 전달
/images 요청 → Nginx가 직접 응답
/admin 요청 → 다른 서버로 전달
```

이런 식으로 경로에 따라 요청을 나눌 수 있다.

---

# 8. 요청 흐름으로 이해하기

## Nginx만 있는 경우

```text
브라우저
  ↓
Nginx
  ↓
HTML, CSS, JS, 이미지 응답
```

정적 웹사이트라면 이걸로 충분할 수 있다.

예를 들어 회사 소개 페이지, 랜딩 페이지, 정적 블로그 같은 것.

---

## Tomcat만 있는 경우

```text
브라우저
  ↓
Spring Boot 내장 Tomcat
  ↓
Controller 실행
  ↓
응답 생성
```

개발 환경에서는 이 구조가 흔하다.

```bash
./mvnw spring-boot:run
```

또는:

```bash
java -jar app.jar
```

이렇게 실행하면 Tomcat이 같이 뜬다.

---

## Nginx + Tomcat 같이 쓰는 경우

```text
브라우저
  ↓
Nginx
  ↓
Spring Boot 내장 Tomcat
  ↓
Controller / Service / DB
```

운영 환경에서 흔한 구조다.

조금 더 자세히 보면:

```text
1. 사용자가 https://example.com/boards 접속
2. Nginx가 443 포트에서 요청 받음
3. Nginx가 내부의 Spring Boot 8080 포트로 전달
4. Tomcat이 요청을 Spring Controller로 넘김
5. Controller가 Service, Repository, DB를 거쳐 응답 생성
6. 응답이 다시 Tomcat → Nginx → 사용자에게 전달
```

---

# 9. 아주 쉽게 비유하면

```text
Nginx
= 건물 1층 안내 데스크

Tomcat
= 안쪽 사무실에서 실제 업무 처리하는 직원
```

사용자가 건물에 들어오면 먼저 안내 데스크를 만난다.

안내 데스크는 이렇게 판단한다.

```text
이건 바로 줄 수 있는 안내문이네 → 바로 줌
이건 담당자가 처리해야 하네 → 안쪽 사무실로 넘김
```

여기서 안내 데스크가 Nginx고, 실제 업무 처리자가 Tomcat이다.

---

# 10. 핵심 정리

```text
웹서버, Nginx
= HTTP 요청을 받아 정적 파일을 응답하거나,
  뒤쪽 애플리케이션 서버로 요청을 전달하는 서버

웹앱서버, Tomcat
= Java/Spring 애플리케이션을 실행하고,
  요청에 따라 동적인 응답을 만들어내는 서버
```

최종적으로 이렇게 기억하면 된다.

```text
Nginx는 앞단에서 요청을 받고 나눠주는 서버

Tomcat은 뒤쪽에서 Java/Spring 코드를 실행하는 서버
```

Spring Boot 기준으로는:

```text
Spring Boot 앱 실행
= 내장 Tomcat이 떠서 8080 포트에서 요청을 받음

운영 환경 배포
= 보통 Nginx가 80/443 포트에서 요청을 받고
  Spring Boot 8080으로 프록시함
```

그래서 둘은 경쟁 관계라기보다 역할이 다르다.

```text
Nginx
= 문지기, 프록시, 정적 파일 담당

Tomcat
= Java 웹 애플리케이션 실행 담당
```
