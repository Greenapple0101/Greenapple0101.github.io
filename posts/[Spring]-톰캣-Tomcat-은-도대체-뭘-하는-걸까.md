---
title: "[SPRING] 톰캣(Tomcat)은 도대체 뭘 하는 걸까?"
source: "https://velog.io/@yorange50/SPRING-톰캣Tomcat은-도대체-뭘-하는-걸까"
published: "2026-05-11T11:00:24.463Z"
tags: ""
backup_date: "2026-05-29T14:52:52.764205"
---


스프링 공부하다 보면 계속 이런 말을 듣는다.

* 내장 톰캣
* 톰캣 서버
* WAS
* 톰캣 띄운다
* 8080 포트

근데 처음엔 진짜 헷갈린다.

```text id="ql8h7u"
“그래서 톰캣이 서버야?”
“스프링이 서버 아니야?”
“내가 만든 API는 누가 실행하는 거지?”
```

오늘 이걸 한 번 정리해보자.

---

# 한 줄 정의

## 톰캣(Tomcat)

```text id="l4w9ga"
자바 웹 애플리케이션을 실행시켜주는 웹 서버(WAS)
```

이다.

---

# 먼저 가장 중요한 개념

우리가 만든 스프링 코드는:

```java id="lr7d4g"
@RestController
public class BoardController {

    @GetMapping("/hello")
    public String hello() {
        return "hello";
    }
}
```

이런 코드다.

근데 이 코드는:

```text id="v53bz9"
“누가 실행해줘야”
```

한다.

그냥 `.java` 파일만 있다고 인터넷 요청을 받을 수 있는 건 아니다.

---

# 누가 HTTP 요청을 받아줄까?

예를 들어 브라우저에서:

```text id="u1xptu"
http://localhost:8080/hello
```

접속했다.

그러면 누군가는:

* 8080 포트 열고
* 요청 받고
* 스프링 코드 호출하고
* 응답 반환

해야 한다.

그 역할을 하는 게:

```text id="phj9g2"
톰캣
```

이다.

---

# 흐름으로 보면 이해 쉽다

```text id="m1r4af"
브라우저 요청
        ↓
톰캣이 요청 받음
        ↓
스프링에게 전달
        ↓
컨트롤러 실행
        ↓
응답 반환
        ↓
톰캣이 브라우저에 전달
```

---

# 톰캣 없으면 어떻게 될까?

사실 스프링 코드는:

```text id="5af46g"
그냥 일반 자바 코드
```

다.

즉:

```java id="9j4b9h"
public class Test {
}
```

랑 본질적으로 크게 다르지 않다.

HTTP 요청을 받으려면:

* 포트 열기
* 소켓 연결
* HTTP 파싱
* 응답 처리

같은 작업이 필요하다.

그걸 대신 해주는 게 톰캣이다.

---

# 톰캣은 WAS(Web Application Server)

여기서 많이 나오는 단어:

## WAS

```text id="mylq52"
Web Application Server
```

웹 애플리케이션 실행 서버.

---

# 왜 그냥 서버라고 안 하고 WAS라고 할까?

단순 웹 서버는:

* 정적 파일 전달

정도만 한다.

예:

* HTML
* CSS
* JS
* 이미지

---

## 대표적인 웹 서버

* Nginx
* Apache

---

# 그런데 스프링은 "동적 처리"가 필요함

예를 들어:

```text id="l4c05d"
회원가입
로그인
DB 조회
게시글 저장
```

이런 건 코드 실행이 필요하다.

그래서:

```text id="ltw2ta"
자바 코드 실행 가능한 서버
```

가 필요한데 그게 WAS다.

톰캣이 대표적인 자바 WAS.

---

# 스프링부트 이전엔 더 복잡했다

예전에는:

```text id="0m2g6u"
1. 톰캣 설치
2. war 파일 생성
3. 톰캣 webapps 폴더에 넣기
4. 톰캣 실행
```

해야 했다.

즉:

```text id="33qu8l"
스프링 앱과 톰캣이 분리
```

되어 있었다.

---

# 그런데 Spring Boot가 바꿔버림

스프링부트는:

```text id="tfgr87"
내장 톰캣(Embedded Tomcat)
```

개념을 넣었다.

즉:

```text id="pw8h1m"
jar 안에 톰캣까지 포함
```

시켜버린 것.

---

# 그래서 지금은 이렇게 됨

```bash id="1h1x0l"
java -jar app.jar
```

만 하면:

* 톰캣 실행
* 스프링 실행
* 서버 실행

이 한 번에 된다.

엄청 편해진 거다.

---

# 실제 로그 보면 보임

스프링 실행하면:

```text id="e4ehyf"
Tomcat started on port 8080
```

같은 로그가 뜬다.

이 의미는:

```text id="61s9z5"
“톰캣이 8080 포트 열고 HTTP 요청 받을 준비 완료”
```

라는 뜻.

---

# 포트 8080은 왜 쓰는 걸까?

예:

```text id="2t34wl"
localhost:8080
```

여기서:

* localhost → 내 컴퓨터
* 8080 → 열려있는 서버 포트

다.

즉 톰캣이:

```text id="xupowf"
8080 포트에서 대기
```

하고 있는 것.

---

# 스프링 코드와 연결되는 구조

예를 들어:

```java id="12bj2v"
@GetMapping("/hello")
public String hello() {
    return "hello";
}
```

브라우저 요청:

```text id="2fl5pk"
GET /hello
```

↓

톰캣이 받음

↓

스프링 DispatcherServlet 호출

↓

컨트롤러 실행

↓

응답 반환

---

# DispatcherServlet은 뭐냐?

스프링 내부의 "교통정리 담당".

톰캣이 요청을 받으면:

```text id="9n3i6g"
“이 URL 누구한테 보낼까?”
```

를 DispatcherServlet이 처리한다.

---

# 쉽게 비유하면

## 톰캣

```text id="x5ffu7"
건물 입구 경비원
```

* 요청 받음
* 사람 들여보냄
* 연결 관리

---

## 스프링

```text id="sz3mdg"
건물 안 직원들
```

* 실제 업무 처리
* DB 조회
* 응답 생성

---

# Docker랑 연결해서 보면

Dockerfile:

```dockerfile id="c7a7vx"
FROM eclipse-temurin:21-jdk

COPY app.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
```

실행하면 내부에서:

```text id="kgmyo2"
JVM 실행
→ Spring Boot 실행
→ 내장 톰캣 실행
→ 8080 포트 오픈
```

된다.

---

# 그래서 docker run -p 가 중요함

예:

```bash id="o2xj85"
docker run -p 8080:8080 app
```

의미:

```text id="0okf79"
내 컴퓨터 8080
↓
컨테이너 내부 톰캣 8080 연결
```

이다.

즉 컨테이너 안의 톰캣 서버에 연결되는 것.

---

# 실무에서는 Nginx랑 같이 많이 씀

구조 예시:

```text id="5ibjjt"
클라이언트
   ↓
Nginx
   ↓
Spring Boot + Tomcat
```

---

# 왜 굳이 Nginx 앞에 둠?

Nginx가:

* SSL 처리
* 정적 파일 처리
* 로드밸런싱
* 리버스 프록시

를 잘하기 때문.

톰캣은 자바 애플리케이션 실행에 집중.

---

# 정리하면

## 톰캣 역할

```text id="k0fjlwm"
HTTP 요청 받기
포트 열기
스프링 코드 실행 연결
응답 반환
```

---

# 핵심 구조

```text id="kkl78f"
브라우저
   ↓
톰캣
   ↓
스프링
   ↓
컨트롤러
   ↓
DB
```

---

# 핵심 요약

## 톰캣은

```text id="7ocm7l"
자바 웹 애플리케이션 실행 서버(WAS)
```

---

## 스프링부트는

```text id="sg4p6i"
내장 톰캣을 포함
```

해서:

```bash id="q0rjzb"
java -jar
```

만으로 서버 실행 가능.

---

# 결론

스프링 코드만으로는 인터넷 요청을 받을 수 없다.

중간에서:

* 포트 열고
* HTTP 처리하고
* 스프링과 연결해주는 존재

가 필요한데,

그 역할을 하는 핵심 서버가:

```text id="mbrxyd"
톰캣(Tomcat)
```

이다.