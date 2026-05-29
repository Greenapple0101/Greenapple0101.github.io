---
title: "[SPRING] this로 Service랑 Controller를 연결한다는 게 무슨 뜻일까?"
source: "https://velog.io/@yorange50/SPRING-this로-Service랑-Controller를-연결한다는-게-무슨-뜻일까"
published: "2026-04-28T09:54:01.145Z"
tags: ""
backup_date: "2026-05-29T14:52:52.788224"
---

스프링을 공부하다 보면 이런 코드를 보게 된다.

```java
@RestController
public class BoardController {

    private final BoardService boardService;

    public BoardController(BoardService boardService) {
        this.boardService = boardService;
    }
}
```

처음 보면 여기서 막힌다.

“this가 뭐지?”

---

### this는 “지금 이 객체 자신”이다

핵심은 이거 하나다.

**this = 지금 생성된 객체 자기 자신**

---

### 변수 이름이 같은 이유 때문에 this가 필요하다

코드를 자세히 보면 같은 이름이 두 개 있다.

```java
private final BoardService boardService;   // 클래스 안 변수
```

```java
public BoardController(BoardService boardService) // 파라미터
```

둘 다 이름이 `boardService`다.

이 상태에서

```java
boardService = boardService;
```

이렇게 쓰면 누구한테 누구를 넣는 건지 모른다.

---

### 그래서 this가 등장한다

```java
this.boardService = boardService;
```

이걸 풀어서 보면 이렇게 된다.

* this.boardService → “이 객체 안에 있는 변수”
* boardService → “외부에서 들어온 값”

즉,

**“외부에서 받은 boardService를, 이 객체 안에 넣겠다”**

---

### 여기서 진짜 중요한 포인트

이건 단순한 대입이 아니다.

**Service와 Controller를 연결하는 순간이다**

---

### 흐름을 보면 이해된다

```text
[스프링]
   ↓
BoardService 객체 생성 (Bean)
   ↓
BoardController 생성할 때 전달
   ↓
this.boardService = boardService
   ↓
Controller 안에 Service가 들어옴
```

---

### 그래서 컨트롤러에서 서비스 사용이 가능해진다

```java
@GetMapping("/boards")
public List<String> getBoards() {
    return boardService.getBoards();
}
```

이 코드가 가능한 이유는 하나다.

**이미 this로 연결되어 있기 때문**

---

### 왜 굳이 이렇게 연결할까?

만약 이게 없으면

* 컨트롤러는 서비스 기능을 못 쓴다
* 객체끼리 완전히 분리됨

그래서

**Controller → Service 연결이 반드시 필요하다**

---

### 스프링이 대신 해주는 부분

여기서 중요한 점 하나 더

```java
public BoardController(BoardService boardService)
```

이건 내가 넣은 게 아니다.

**스프링이 Bean을 꺼내서 넣어준다**

그래서 우리는 new를 안 써도 된다.

---

### 비유로 보면

Controller = 직원
Service = 전문가

* 직원이 혼자 일 못함
* 전문가를 옆에 붙여줌
* 그 연결이 this

---

### 한 줄 결론

**this는 “내 객체 안에 외부 객체를 연결해서 사용할 수 있게 만드는 것”이다**
