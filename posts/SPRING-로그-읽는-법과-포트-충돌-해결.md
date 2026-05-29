---
title: "[SPRING] 로그 읽는 법과 포트 충돌 해결"
source: "https://velog.io/@yorange50/SPRING-로그-읽는-법과-포트-충돌-해결"
published: "2026-04-28T23:38:48.449Z"
tags: ""
backup_date: "2026-05-29T14:52:52.787489"
---

스프링 실행이 실패하면 마지막에 보통 이렇게 나온다.

```text
BUILD FAILED
```

근데 이건 **결과**일 뿐이다.
진짜 원인은 항상 그 위에 있다.

---

## 1. 로그에서 제일 먼저 볼 곳

아래 문구를 찾으면 된다.

```text
APPLICATION FAILED TO START
```

그 아래에 보통 원인이 나온다.

이번 로그에서는 이게 핵심이었다.

```text
Web server failed to start. Port 8080 was already in use.
```

뜻은 단순하다.

**스프링 서버를 8080번 포트로 띄우려 했는데, 이미 다른 프로그램이 8080번을 쓰고 있다.**

---

## 2. 포트가 뭐냐

포트는 컴퓨터 안에서 프로그램이 통신하는 문 번호라고 보면 된다.

```text
localhost:8080
```

이 말은:

```text
내 컴퓨터의 8080번 문으로 들어가겠다
```

는 뜻이다.

스프링부트는 기본적으로 8080번 포트를 사용한다.

---

## 3. 누가 8080을 쓰는지 확인

맥 터미널에서 입력한다.

```bash
lsof -i :8080
```

그러면 이런 식으로 나온다.

```text
java  30527  baegseoyeon  ...
```

여기서 중요한 건 PID다.

```text
30527
```

PID는 실행 중인 프로그램의 번호다.

---

## 4. 포트 쓰는 프로그램 종료

```bash
kill -9 30527
```

뜻은:

```text
30527번 프로세스를 강제로 종료해라
```

그 다음 다시 확인한다.

```bash
lsof -i :8080
```

아무것도 안 나오면 성공이다.

---

## 5. 다시 스프링 실행

```bash
./gradlew bootRun
```

성공하면 이런 로그가 나온다.

```text
Tomcat started on port 8080
Started BoardApiApplication
```

이러면 서버가 켜진 상태다.

---

## 6. 한 번에 죽이는 명령어

8080을 쓰는 프로세스를 바로 죽이고 싶으면:

```bash
kill -9 $(lsof -t -i:8080)
```

다만 처음에는 이 방식보다 아래 순서를 추천한다.

```bash
lsof -i :8080
kill -9 PID
```

직접 보고 죽이는 습관이 로그 읽는 감각을 키워준다.

---

## 한 줄 정리

```text
BUILD FAILED만 보지 말고,
APPLICATION FAILED TO START 아래의 Description을 봐라.
Port 8080 was already in use면 lsof로 PID 찾고 kill 하면 된다.
```
