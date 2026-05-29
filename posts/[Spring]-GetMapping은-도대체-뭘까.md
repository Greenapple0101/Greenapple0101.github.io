---
title: "[SPRING] @GetMapping은 도대체 뭘까?"
source: "https://velog.io/@yorange50/SPRING-GetMapping은-도대체-뭘까"
published: "2026-04-28T07:52:57.749Z"
tags: ""
backup_date: "2026-05-29T14:52:52.788484"
---



코드를 보면 이런 게 있다.

```java
@GetMapping("/boards")
public List<String> getBoards() {
    return List.of("게시글1", "게시글2");
}
```

처음 보면 이렇게 생각 든다.

“이건 또 뭐야… 왜 괄호 안에 /boards가 있어?”

---

### @GetMapping은 요청 주소를 연결해주는 역할이다

핵심은 이거다.

**@GetMapping = 이 주소로 요청 오면 이 메서드 실행해라**

---

### 사용자는 이렇게 요청한다

브라우저에서

```
http://localhost:8080/boards
```

이렇게 요청을 보낸다.

---

### 스프링은 이렇게 연결한다

```java
@GetMapping("/boards")
public List<String> getBoards() {
    return List.of("게시글1", "게시글2");
}
```

이 코드는 이렇게 읽으면 된다.

* "/boards"로 요청이 들어오면
* getBoards() 실행하고
* 결과를 반환해라

---

### 그래서 전체 흐름은 이렇게 된다

```
[사용자]
   ↓ GET /boards 요청
[Controller - @GetMapping("/boards")]
   ↓
getBoards() 실행
   ↓
["게시글1", "게시글2"] 반환
```

---

### GET은 뭐냐?

여기서 중요한 포인트 하나 더

**GET = 데이터를 조회할 때 쓰는 요청 방식**

그래서 보통 이렇게 쓴다.

* GET → 조회 (데이터 가져오기)
* POST → 생성
* PUT → 수정
* DELETE → 삭제

---

### 예시로 보면

```java
@GetMapping("/boards")        // 조회
@PostMapping("/boards")       // 생성
@PutMapping("/boards/{id}")   // 수정
@DeleteMapping("/boards/{id}")// 삭제
```

이걸 REST API라고 부른다.

---

### @RequestMapping이랑 뭐가 다르냐?

사실 @GetMapping은 줄여 쓴 거다.

```java
@RequestMapping(value = "/boards", method = RequestMethod.GET)
```

이걸 간단하게 만든 게

```java
@GetMapping("/boards")
```

---

### 경로에 변수 넣는 것도 가능하다

```java
@GetMapping("/boards/{id}")
public String getBoard(@PathVariable int id) {
    return "게시글 " + id;
}
```

요청:

```
/boards/1
```

결과:

```
게시글 1
```

---

### 한 줄 핵심 정리

* @RestController → 입구
* @GetMapping → 어떤 주소로 들어올지 지정

---

### 비유로 보면

컨트롤러 = 건물
@GetMapping = 방 번호

* 건물은 하나 (Controller)
* 방은 여러 개 (@GetMapping)

---

### 한 줄 결론

**@GetMapping은 특정 URL로 들어온 GET 요청을 해당 메서드에 연결해주는 어노테이션이다**
