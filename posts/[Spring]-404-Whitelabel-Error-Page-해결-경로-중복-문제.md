---
title: "[SPRING] 404 Whitelabel Error Page 해결 (경로 중복 문제)"
source: "https://velog.io/@yorange50/SPRING-404-Whitelabel-Error-Page-해결-경로-중복-문제"
published: "2026-04-29T00:27:53.029Z"
tags: ""
backup_date: "2026-05-29T14:52:52.787136"
---

![](https://velog.velcdn.com/images/yorange50/post/1fb0a7f2-2ae2-45e5-b49e-2a5bbd339526/image.png)
![](https://velog.velcdn.com/images/yorange50/post/8d13ca36-43c0-4e98-b606-6a89cd49576c/image.png)

스프링 서버를 정상적으로 실행했는데도 아래와 같은 화면이 나온다면 당황하기 쉽다.

```text
Whitelabel Error Page
There was an unexpected error (type=Not Found, status=404)
```

이 에러는 서버가 죽은 게 아니라,
**요청한 URL을 처리할 API가 없다는 의미**다.

---

## 1. 문제 상황

브라우저에서 다음 주소로 요청했다.

```text
http://localhost:8080/boards
```

하지만 404 에러 발생

---

## 2. 코드 확인

Controller 코드:

```java
@RestController
@RequestMapping("/boards")
public class BoardController {

    private final BoardService boardService;

    public BoardController(BoardService boardService){
        this.boardService = boardService;
    }

    @GetMapping("/boards")
    public List<String> getBoards(){
        return boardService.getBoards();
    }
}
```

---

## 3. 문제 원인

스프링은 URL을 다음과 같이 조합한다.

```text
클래스 레벨 @RequestMapping + 메서드 레벨 @GetMapping
```

현재 코드 기준:

```text
"/boards" + "/boards" = "/boards/boards"
```

즉, 실제 API 주소는 다음과 같다.

```text
http://localhost:8080/boards/boards
```

하지만 요청은 `/boards`로 보냈기 때문에
→ 404 (Not Found) 발생

---

## 4. 해결 방법

### 방법 1 (권장)

메서드 매핑을 단순화

```java
@GetMapping
public List<String> getBoards(){
    return boardService.getBoards();
}
```

이렇게 수정하면 실제 URL:

```text
http://localhost:8080/boards
```

---

### 방법 2

코드는 그대로 두고 URL을 맞춘다.

```text
http://localhost:8080/boards/boards
```

---

## 5. 핵심 개념

```text
@RequestMapping("/boards")  ← 공통 경로
@GetMapping("/boards")      ← 추가 경로
```

→ 둘이 합쳐진다

---

## 6. 정리

```text
404 에러는 서버 문제 아니라 “경로 매핑 문제”
스프링은 클래스 + 메서드 경로를 합쳐서 URL을 만든다
```

---

## 한 줄 결론

**/boards + /boards → /boards/boards가 되어 발생한 404 에러**

---

이 문제를 이해하면
스프링의 URL 구조와 라우팅 개념을 제대로 이해한 상태다
