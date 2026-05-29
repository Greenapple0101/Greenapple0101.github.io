---
title: "[SPRING] @RequiredArgsConstructor란? (Lombok 없이 쓰면 어떻게 될까)"
source: "https://velog.io/@yorange50/SPRING-RequiredArgsConstructor란-Lombok-없이-쓰면-어떻게-될까"
published: "2026-04-30T01:03:17.409Z"
tags: ""
backup_date: "2026-05-29T14:52:52.783050"
---

Spring 코드를 보다 보면 이런 어노테이션을 자주 보게 된다.

```java
@RequiredArgsConstructor
@RestController
public class BoardController {

    private final BoardService boardService;

}
```

처음 보면 “이게 뭐지?” 싶지만, 사실은 **생성자를 대신 만들어주는 도구**다.

---

## 1. @RequiredArgsConstructor의 역할

이 어노테이션은

> **final이 붙은 필드를 기준으로 생성자를 자동 생성해준다**

즉, 아래 코드:

```java
private final BoardService boardService;
```

이걸 보고 Lombok이 자동으로 이걸 만들어준다:

```java
public BoardController(BoardService boardService) {
    this.boardService = boardService;
}
```

---

## 2. 왜 이게 필요할까?

Spring에서 의존성 주입을 할 때 가장 권장되는 방식이

> 생성자 주입

이다.

즉, 이렇게 쓰는 게 정석이다:

```java
public BoardController(BoardService boardService) {
    this.boardService = boardService;
}
```

그런데 클래스마다 이걸 매번 쓰면 귀찮고 코드가 길어진다.

그래서 Lombok을 쓰면:

```java
@RequiredArgsConstructor
```

한 줄로 끝낼 수 있다.

---

## 3. Lombok 안 쓰면 어떻게 해야 할까?

Lombok을 안 쓰면 **직접 생성자를 만들어야 한다**

```java
@RestController
public class BoardController {

    private final BoardService boardService;

    public BoardController(BoardService boardService) {
        this.boardService = boardService;
    }
}
```

즉,

* Lombok 있음 → 자동 생성
* Lombok 없음 → 직접 작성

---

## 4. 왜 final을 붙일까?

```java
private final BoardService boardService;
```

여기서 `final`이 중요한 이유는:

* 한 번 주입되면 바뀌지 않도록 보장
* 생성자 주입을 강제
* 코드 안정성 증가

그리고 Lombok도 **final 기준으로 생성자 만들어준다**

---

## 5. 핵심 흐름

정리하면:

1. Controller가 Service를 사용해야 함
2. 그래서 생성자로 받아야 함
3. 그 생성자를 Lombok이 대신 만들어줌

---

## 6. 한 줄 정리

* @RequiredArgsConstructor → final 필드 기준 생성자 자동 생성
* Lombok 없으면 → 생성자 직접 작성해야 함
* Spring에서는 생성자 주입이 기본 패턴

---

이걸 이해하면 지금 코드에서

```java
this.boardService = boardService;
```

이게 왜 필요한지도 자연스럽게 연결된다.

다음 단계는
→ “왜 필드 주입(@Autowired)보다 생성자 주입이 좋은지”

이거까지 가면 설계 이해도가 한 단계 올라간다.
