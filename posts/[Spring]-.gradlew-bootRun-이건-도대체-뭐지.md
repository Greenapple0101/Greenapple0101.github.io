---
title: "[SPRING] ./gradlew bootRun 이건 도대체 뭐지?"
source: "https://velog.io/@yorange50/SPRING-.gradlew-bootRun-이건-도대체-뭐지"
published: "2026-04-28T23:35:05.409Z"
tags: ""
backup_date: "2026-05-29T14:52:52.787769"
---

스프링 프로젝트를 처음 실행할 때 자주 보게 되는 명령어가 있다

```bash
./gradlew bootRun
```

처음 보면 이게 뭔지 감이 잘 안 온다.
그냥 “서버 실행하는 명령어인가?” 정도로 넘어가기 쉬운데, 이 안에는 중요한 개념이 몇 개 들어 있다.

---

## 1. ./gradlew 는 뭐야?

`gradlew`는 **Gradle Wrapper**라는 것이다.

쉽게 말하면:

* 프로젝트 안에 포함된 실행 도구
* 컴퓨터에 Gradle이 따로 설치되어 있지 않아도 실행 가능

즉,

👉 “이 프로젝트는 이 방식으로 실행해” 라고 정해진 실행기

---

## 2. bootRun 은 뭐야?

`bootRun`은 **Spring Boot 프로젝트를 실행하는 명령어**

이걸 하면 내부적으로:

* 자바 코드 컴파일
* 필요한 라이브러리 로드
* 스프링 컨테이너 생성
* 서버 실행 (기본 8080 포트)

까지 한 번에 다 진행된다

---

## 3. 전체 해석

```bash
./gradlew bootRun
```

이 한 줄을 풀어서 보면:

👉 “이 프로젝트에 맞는 Gradle로, 스프링 서버를 실행해라”

---

## 4. 실행하면 실제로 일어나는 일

터미널에서 실행하면 이런 로그가 뜬다:

```text
Tomcat started on port 8080
Started Application in X seconds
```

이 상태가 되면:

👉 서버가 살아있는 상태

---

## 5. 그 다음 해야 할 것

서버가 실행됐으면 이제 API를 호출해볼 수 있다

예를 들어:

```bash
http://localhost:8080/boards
```

이걸 브라우저나 Postman으로 호출하면
Controller → Service → 응답 흐름이 실제로 동작한다

---

## 6. 왜 중요한가

이 명령어 하나로:

* 서버 실행
* API 테스트
* 전체 구조 확인

이 다 가능하다

즉,

👉 “내가 만든 백엔드가 실제로 돌아가는지 확인하는 첫 단계”

---

## 한 줄 정리

**./gradlew bootRun
→ 스프링 서버를 실행해서 API를 실제로 동작시키는 명령어**

---

이걸 이해하면 다음 단계는 자연스럽게 이어진다

👉 “실행된 서버에 내가 만든 API를 붙여보기”
👉 “Controller → Service 흐름 확인하기”

여기까지 되면 스프링 구조가 단순 문법이 아니라
“동작하는 시스템”으로 보이기 시작한다
