---
title: "[SPRING] Bean은 도대체 뭘까?"
source: "https://velog.io/@yorange50/SPRING-Bean은-도대체-뭘까"
published: "2026-04-28T06:50:38.882Z"
tags: "Spring"
backup_date: "2026-05-29T14:52:52.788895"
---



스프링을 공부하다 보면 이런 코드가 계속 보인다.

```java
@Service
public class BoardService {
}
```

그리고 이런 말을 듣는다.

“이건 Bean으로 등록된다”

처음 들으면 바로 막힌다.

“Bean이 뭐야?”

---

### Bean은 스프링이 관리하는 객체다

가장 핵심부터 말하면 이거다.

**Bean = 스프링이 대신 만들어서 관리해주는 객체**

---

### 원래 자바에서는 이렇게 객체를 만든다

```java
BoardService boardService = new BoardService();
```

이건 내가 직접 만든 거다.

* 내가 new 한다
* 내가 들고 있다
* 내가 관리한다

---

### 그런데 스프링은 이렇게 말한다

“그거 내가 해줄게”

그래서 이렇게 바뀐다.

```java
@Service
public class BoardService {
}
```

이 한 줄의 의미는 이거다.

**BoardService 객체를 스프링이 대신 생성하고 관리한다**

---

### 그래서 Bean이 되는 순간 벌어지는 일

```java
@Service
public class BoardService {
}
```

이게 실행되면 내부에서는 이런 일이 일어난다.

* 스프링이 BoardService 클래스를 발견함
* 객체를 하나 생성함
* 그 객체를 저장해둠
* 필요할 때 꺼내서 사용함

이 저장된 객체를 Bean이라고 부른다.

---

### 왜 굳이 스프링이 객체를 관리할까?

직접 만들면 이런 문제가 생긴다.

* 어디서 new 했는지 찾기 힘듦
* 같은 객체를 여러 개 만들게 됨
* 객체 간 연결(의존성)이 복잡해짐

그래서 스프링이 대신 관리한다.

---

### 핵심은 “공용으로 쓰는 객체”라는 점이다

Bean은 보통 이런 특징을 가진다.

* 여러 곳에서 같이 씀
* 한 번만 만들어서 계속 씀
* 상태를 공유하거나 로직을 공유함

예를 들어

* BoardService → 게시판 로직
* UserService → 회원 로직
* Repository → DB 접근

이런 애들은 매번 새로 만들 필요가 없다.

그래서 스프링이 하나 만들어놓고 계속 재사용한다.

---

### Bean은 어디에 저장될까?

스프링은 내부에 이런 공간을 가지고 있다.

**ApplicationContext (스프링 컨테이너)**

여기에 Bean들이 들어간다.

```
[스프링 컨테이너]

BoardService Bean
UserService Bean
CommentService Bean
```

필요할 때 여기서 꺼내 쓴다.

---

### 그래서 @Autowired가 등장한다

```java
@Service
public class BoardService {
}
```

```java
@RestController
public class BoardController {

    private final BoardService boardService;

    public BoardController(BoardService boardService) {
        this.boardService = boardService;
    }
}
```

여기서 중요한 포인트

* 내가 new 안 했다
* 근데 BoardService가 들어온다

이유는 하나다.

**스프링이 Bean을 꺼내서 넣어줬기 때문**

---

### 클래스 vs Bean 차이

여기서 헷갈리는 포인트 정리

* 클래스 = 설계도
* 객체 = 실제 만든 것
* Bean = 스프링이 관리하는 객체

---

### 한 번에 정리

* 클래스 → 기능 묶는 상자
* 객체 → 클래스로 만든 실제 인스턴스
* Bean → 스프링이 관리하는 객체

---

### 비유로 보면

클래스 → 레시피
객체 → 직접 만든 요리
Bean → 식당에서 만들어서 계속 쓰는 요리

---

### 한 줄 결론

**Bean은 스프링이 대신 생성하고 관리해주는 객체다**
