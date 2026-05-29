---
title: "[SPRING] @RestController는 도대체 뭘까?"
source: "https://velog.io/@yorange50/SPRING-RestController는-도대체-뭘까"
published: "2026-04-28T07:20:56.250Z"
tags: ""
backup_date: "2026-05-29T14:52:52.788689"
---

스프링을 하다 보면 이런 코드가 나온다.

```java
@RestController
public class BoardController {

    @GetMapping("/boards")
    public List<String> getBoards() {
        return List.of("게시글1", "게시글2");
    }
}
```

그리고 이런 말을 듣는다.

“이건 컨트롤러야”

바로 막힌다.

“컨트롤러가 뭐야?”

---

### 컨트롤러는 요청을 받는 입구다

핵심부터 말하면 이거다.

**@RestController = 외부 요청을 받는 입구**

---

### 우리가 만든 서비스는 그냥 내부 로직이다

```java
@Service
public class BoardService {

    public List<String> getBoards() {
        return List.of("게시글1", "게시글2");
    }
}
```

이건 그냥 기능이다.

문제는 이거다.

“이걸 누가 호출하지?”

---

### 사용자는 이렇게 요청한다

브라우저에서

```
http://localhost:8080/boards
```

이렇게 요청을 보낸다.

---

### 이걸 받아주는 게 컨트롤러다

```java
@RestController
public class BoardController {

    @GetMapping("/boards")
    public List<String> getBoards() {
        return List.of("게시글1", "게시글2");
    }
}
```

이 코드는 이렇게 읽으면 된다.

* /boards 요청이 오면
* getBoards() 실행해라
* 결과를 그대로 반환해라

---

### 그래서 흐름은 이렇게 된다

```
[사용자]
   ↓ 요청 (/boards)
[Controller]
   ↓
[Service]
   ↓
[결과 반환]
```

---

### @RestController의 진짜 의미

이건 사실 두 개가 합쳐진 거다.

```
@Controller + @ResponseBody
```

뜻은 이거다.

* @Controller → 요청 받는 클래스
* @ResponseBody → 결과를 JSON으로 반환

그래서 @RestController는

**“요청 받고, 결과를 JSON으로 바로 내려주는 클래스”**

---

### 왜 JSON으로 주냐?

웹/앱은 보통 데이터만 필요하다.

```json
["게시글1", "게시글2"]
```

이걸 프론트엔드가 받아서 화면에 뿌린다.

---

### @GetMapping은 뭐냐

```java
@GetMapping("/boards")
```

이건 이렇게 읽으면 된다.

* GET 요청이
* /boards로 들어오면
* 이 메서드를 실행해라

---

### 컨트롤러는 로직을 하면 안 된다

여기서 중요한 포인트

```java
@RestController
public class BoardController {

    public List<String> getBoards() {
        // ❌ 여기서 로직 다 하면 안됨
    }
}
```

컨트롤러 역할은 딱 하나다.

* 요청 받기
* 서비스 호출
* 결과 반환

그래서 이렇게 쓴다.

```java
@RestController
public class BoardController {

    private final BoardService boardService;

    public BoardController(BoardService boardService) {
        this.boardService = boardService;
    }

    @GetMapping("/boards")
    public List<String> getBoards() {
        return boardService.getBoards();
    }
}
```

---

### 역할 정리

* Controller → 입구
* Service → 로직
* Repository → 데이터

---

### 비유로 보면

컨트롤러 = 주문 받는 직원
서비스 = 요리사

* 손님이 주문한다 (요청)
* 직원이 주문을 받는다 (Controller)
* 요리사에게 전달한다 (Service)
* 음식이 나온다 (응답)

---

### 한 줄 결론

**@RestController는 외부 요청을 받아서 처리 결과를 JSON으로 내려주는 스프링의 입구다**
