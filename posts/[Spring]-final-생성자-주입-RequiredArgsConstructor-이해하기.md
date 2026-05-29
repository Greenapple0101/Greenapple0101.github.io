---
title: "[SPRING] final, 생성자 주입, @RequiredArgsConstructor 이해하기"
source: "https://velog.io/@yorange50/SPRING-final-생성자-주입-RequiredArgsConstructor-이해하기"
published: "2026-04-30T01:07:33.258Z"
tags: ""
backup_date: "2026-05-29T14:52:52.782589"
---

Spring에서 Controller를 만들다 보면 아래와 같은 코드를 보게 된다.

```java
public class BoardController {

    private final BoardService boardService;

    public BoardController(BoardService boardService) {
        this.boardService = boardService;
    }
}
```

처음 보면 단순한 생성자처럼 보이지만, 사실 이 코드는 **의존성 주입(Dependency Injection)**의 핵심 구조다.

---

## 1. final이 붙으면 뭐가 달라질까?

```java
private final BoardService boardService;
```

여기서 `final`은

> “이 변수는 한 번 값이 들어오면 절대 바뀌면 안 된다”

는 의미다.

즉, `BoardController`가 생성될 때 **반드시 BoardService가 주입되어야만 한다**는 뜻이다.

---

## 2. 그래서 왜 생성자를 쓰는 걸까?

```java
public BoardController(BoardService boardService) {
    this.boardService = boardService;
}
```

이 코드는

> “이 클래스가 만들어질 때, BoardService를 반드시 넣어줘라”

라는 의미다.

Spring은 이 생성자를 보고 자동으로

* BoardService 객체를 찾아서
* Controller에 넣어준다

이걸 **생성자 주입**이라고 한다.

---

## 3. 왜 이 방식이 중요할까?

이 구조의 핵심은 두 가지다.

* 객체가 생성될 때 이미 필요한 값이 다 들어와 있음
* 중간에 값이 바뀌지 않아서 안정적

즉,

> “안전하게 완성된 상태로 객체를 만들기 위한 방식”

---

## 4. @RequiredArgsConstructor가 하는 일

이제 여기서 Lombok이 등장한다.

```java
@RequiredArgsConstructor
public class BoardController {

    private final BoardService boardService;

}
```

이렇게 쓰면 Lombok이 자동으로 아래 코드를 만들어준다.

```java
public BoardController(BoardService boardService) {
    this.boardService = boardService;
}
```

즉,

> 생성자를 대신 만들어주는 역할

---

## 5. Lombok 없으면?

Lombok을 안 쓰면 직접 써야 한다.

```java
public BoardController(BoardService boardService) {
    this.boardService = boardService;
}
```

그래서 말하는 거다:

> “Lombok 안 쓰면 저걸 만들어줘야 합니다”

---

## 6. @Autowired는 왜 안 쓰는 걸까?

예전에는 이렇게 많이 썼다.

```java
@Autowired
private BoardService boardService;
```

하지만 이 방식은

* 객체 생성 시점이 명확하지 않고
* 테스트나 유지보수에서 불리하다

그래서 지금은

> 생성자 주입 방식이 표준

---

## 정리

* final → 반드시 값이 들어와야 하는 변수
* 생성자 → 객체 생성 시 값 주입
* 생성자 주입 → Spring이 자동으로 의존성 넣어줌
* @RequiredArgsConstructor → 생성자 자동 생성
* Lombok 없으면 → 생성자 직접 작성

---

이 흐름이 잡히면 Spring 구조에서

Controller → Service 연결이 어떻게 이루어지는지 자연스럽게 보이기 시작한다.
