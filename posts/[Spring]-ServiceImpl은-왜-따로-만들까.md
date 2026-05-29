---
title: "[SPRING] ServiceImpl은 왜 따로 만들까?"
source: "https://velog.io/@yorange50/SPRING-ServiceImpl은-왜-따로-만들까"
published: "2026-04-30T01:12:22.811Z"
tags: ""
backup_date: "2026-05-29T14:52:52.782264"
---


Spring 프로젝트를 하다 보면 이런 말을 듣게 된다.

> “Service에는 껍데기만 두고, 실제 비즈니스 로직은 Impl에서 구현합니다.”

처음에는 굳이 왜 나누는지 이해가 잘 안 됐다.
그냥 `BoardService` 클래스 하나에 로직을 다 넣으면 되는 것 아닌가 싶었다.

---

## 1. 처음에는 Service에 다 구현할 수 있다

게시판 API를 처음 만들 때는 보통 이렇게 작성한다.

```java id="26fnmd"
@Service
public class BoardService {

    public List<String> getBoards() {
        return List.of("게시글1", "게시글2", "게시글3");
    }
}
```

이 구조는 간단하다.

`BoardService` 안에 게시글 목록을 조회하는 로직이 바로 들어가 있다.

작은 프로젝트나 연습용 코드에서는 이렇게 해도 문제는 없다.

---

## 2. 하지만 실무에서는 구조를 나누는 경우가 많다

레이어드 아키텍처에서는 보통 Service를 두 부분으로 나눈다.

```text id="lv4fx4"
BoardService      → 기능을 정의하는 껍데기
BoardServiceImpl  → 실제 로직을 구현하는 클래스
```

즉, `Service`는 “무엇을 할 수 있는지”만 정하고,
`Impl`은 “그걸 실제로 어떻게 할지”를 작성한다.

---

## 3. BoardService는 인터페이스로 만든다

```java id="ky8c90"
public interface BoardService {

    List<String> getBoards();

    Board createBoard(String title);
}
```

여기에는 실제 로직이 없다.

그냥 이런 뜻이다.

> “게시판 서비스에는 게시글 목록 조회 기능이 있고, 게시글 생성 기능이 있어야 한다.”

즉, 약속만 적어둔 것이다.

---

## 4. BoardServiceImpl에서 실제 로직을 구현한다

```java id="7w7g0x"
@Service
public class BoardServiceImpl implements BoardService {

    @Override
    public List<String> getBoards() {
        return List.of("게시글1", "게시글2", "게시글3");
    }

    @Override
    public Board createBoard(String title) {
        return new Board(1L, title);
    }
}
```

여기서 중요한 키워드는 `implements`다.

```java id="02mmv5"
public class BoardServiceImpl implements BoardService
```

이 말은:

> “BoardService에서 약속한 기능들을 BoardServiceImpl이 실제로 구현하겠다.”

라는 뜻이다.

---

## 5. 쉽게 비유하면

`BoardService`는 메뉴판이다.

```text id="j0a5d4"
- 게시글 목록 조회
- 게시글 생성
- 게시글 수정
- 게시글 삭제
```

메뉴판에는 음식이 실제로 들어있지 않다.
그냥 어떤 메뉴가 가능한지만 적혀 있다.

`BoardServiceImpl`은 주방이다.

메뉴판에 적힌 음식을 실제로 만드는 곳이다.

즉,

```text id="3l8ke4"
Service = 메뉴판
Impl = 실제 요리하는 주방
```

---

## 6. Controller는 Impl을 직접 몰라도 된다

Controller에서는 이렇게 쓴다.

```java id="g39zy7"
@RestController
@RequiredArgsConstructor
public class BoardController {

    private final BoardService boardService;

}
```

여기서 Controller는 `BoardServiceImpl`을 직접 쓰지 않는다.

```java id="tnz1i7"
private final BoardService boardService;
```

인터페이스인 `BoardService`만 바라본다.

Spring이 알아서 `BoardServiceImpl`을 찾아서 연결해준다.

---

## 7. 왜 이렇게 하는 걸까?

핵심은 유지보수와 확장성이다.

지금은 게시글을 메모리에 저장하지만,
나중에는 DB에 저장할 수도 있다.

또는 테스트용 서비스와 실제 운영용 서비스를 나눌 수도 있다.

```text id="csig5s"
BoardServiceImpl        → 실제 서비스 로직
FakeBoardServiceImpl    → 테스트용 로직
DbBoardServiceImpl      → DB 연결 로직
```

인터페이스가 같으면 Controller 코드를 크게 바꾸지 않고 구현체를 바꿀 수 있다.

---

## 8. 그럼 항상 Impl을 만들어야 할까?

꼭 그런 것은 아니다.

작은 프로젝트나 연습 단계에서는 Service 클래스 하나에 바로 구현해도 괜찮다.

하지만 팀 프로젝트나 실무에서는 구조를 명확히 하기 위해

```text id="0qd2l8"
Controller
Service(interface)
ServiceImpl
Repository
```

이런 식으로 나누는 경우가 많다.

---

## 정리

* `Service`는 기능을 정의하는 인터페이스
* `ServiceImpl`은 실제 비즈니스 로직을 구현하는 클래스
* `implements`는 “이 인터페이스의 기능을 내가 구현하겠다”는 뜻
* Controller는 Impl을 직접 보지 않고 Service만 바라본다
* 이렇게 나누면 유지보수와 테스트, 확장이 쉬워진다

처음에는 코드가 더 많아 보여서 복잡해 보이지만,
프로젝트가 커질수록 역할이 분리되어 관리하기 편해진다.
