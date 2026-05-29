---
title: "[SPRING] GET 다음 단계, POST API 추가해서 데이터 생성하기"
source: "https://velog.io/@yorange50/SPRING-GET-다음-단계-POST-API-추가해서-데이터-생성하기"
published: "2026-04-29T01:11:12.860Z"
tags: ""
backup_date: "2026-05-29T14:52:52.786562"
---



Spring Boot로 게시판 API를 만들고 있다. 처음에는 가장 단순한 조회 기능부터 만들었다. 게시글 목록을 반환하는 `GET /boards` API다.
![](https://velog.velcdn.com/images/yorange50/post/5e19228d-bd95-4586-b768-fe991ad0b39e/image.png)


현재 구조는 Controller와 Service로 나누어져 있다.

```text id="i4rqzj"
BoardController.java → 요청을 받는 곳
BoardService.java    → 실제 로직을 처리하는 곳
```

처음 작성한 Service 코드는 다음과 같았다.

```java id="shq4vl"
@Service
public class BoardService {
    
    public List<String> getBoards(){
        return List.of("게시글1", "게시글2", "게시글3");
    }

    public String createBoards(String title){
        return "생성됨:" + title;
    }
}
```

그리고 Controller에서는 Service를 호출해서 게시글 목록을 반환했다.

```java id="jtw55f"
@GetMapping("/boards")
public List<String> getBoards(){
    return boardService.getBoards();
}
```

Postman에서 다음 요청을 보내면 정상적으로 응답이 왔다.

```http id="w1zvw7"
GET http://localhost:8080/boards
```

응답 결과

```json id="1lstsl"
[
  "게시글1",
  "게시글2",
  "게시글3"
]
```

여기까지는 조회만 가능한 상태다. 하지만 게시판이라면 글을 새로 추가하는 기능도 필요하다. 그래서 다음 단계로 `POST /boards`를 추가해야 한다.

---

## POST 요청을 바로 보내면 생기는 문제

Postman에서 Method를 POST로 바꾸고 같은 주소로 요청을 보내면 다음과 같은 에러가 발생한다.

```json id="6vwwf4"
{
  "timestamp": "2026-04-29T00:38:57.413Z",
  "status": 405,
  "error": "Method Not Allowed",
  "path": "/boards"
}
```

`405 Method Not Allowed`는 주소가 틀렸다는 뜻이 아니다.

의미는 다음과 같다.

```text id="v3j28d"
/boards 주소는 존재한다.
하지만 POST 방식으로 처리하는 메서드는 없다.
```

즉, 현재 코드에는 `@GetMapping("/boards")`만 있고 `@PostMapping("/boards")`는 없기 때문에 발생한 에러다.

---

## Service 수정하기

먼저 Service를 수정한다.

기존 코드는 이렇게 되어 있었다.

```java id="bmaw4e"
public List<String> getBoards(){
    return List.of("게시글1", "게시글2", "게시글3");
}
```

이 방식은 호출할 때마다 리스트를 만들어 반환한다. 그리고 `List.of()`로 만든 리스트는 수정할 수 없는 리스트다. 즉, 새로운 게시글을 추가하기 어렵다.

그래서 Service 안에 게시글 목록을 저장할 리스트를 필드로 만든다.

```java id="zr92mg"
package com.board.api.service;

import org.springframework.stereotype.Service;
import java.util.*;

@Service
public class BoardService {

    private final List<String> boards = new ArrayList<>(
        List.of("게시글1", "게시글2", "게시글3")
    );

    public List<String> getBoards(){
        return boards;
    }

    public String createBoards(String title){
        boards.add(title);
        return "생성됨:" + title;
    }
}
```

여기서 중요한 부분은 다음 코드다.

```java id="jz40hg"
private final List<String> boards = new ArrayList<>(
    List.of("게시글1", "게시글2", "게시글3")
);
```

이제 `boards`라는 리스트가 Service 안에서 유지된다.

GET 요청이 오면 이 리스트를 반환하고, POST 요청이 오면 이 리스트에 새 게시글 제목을 추가한다.

---

## Controller에 POST 추가하기

이제 Controller에 POST 요청을 처리하는 메서드를 추가한다.

기존 GET 메서드 아래에 다음 코드를 추가한다.

```java id="nmb261"
@PostMapping("/boards")
public String createBoard(@RequestBody Map<String, String> body){
    String title = body.get("title");
    return boardService.createBoards(title);
}
```

전체 Controller 코드는 다음과 같다.

```java id="fq9oc1"
package com.board.api.controller;

import com.board.api.service.BoardService;
import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
@RequestMapping
public class BoardController {

    private final BoardService boardService;

    public BoardController(BoardService boardService){
        this.boardService = boardService;
    }

    @GetMapping("/boards")
    public List<String> getBoards(){
        return boardService.getBoards();
    }

    @PostMapping("/boards")
    public String createBoard(@RequestBody Map<String, String> body){
        String title = body.get("title");
        return boardService.createBoards(title);
    }
}
```

---

## @RequestBody는 무엇인가

Postman에서 POST 요청을 보낼 때 Body에 JSON 데이터를 넣는다.

```json id="vl37jw"
{
  "title": "테스트 글"
}
```

이 데이터는 HTTP 요청의 본문에 담겨서 서버로 전달된다.

Spring에서 이 요청 본문을 Java 코드에서 사용할 수 있게 꺼내려면 `@RequestBody`를 사용한다.

```java id="j2j4uv"
@RequestBody Map<String, String> body
```

이렇게 작성하면 JSON 데이터가 `Map` 형태로 들어온다.

그리고 다음 코드로 `title` 값을 꺼낼 수 있다.

```java id="ok1wy2"
String title = body.get("title");
```

---

## Postman으로 테스트하기

서버를 다시 실행한다.

```bash id="wsv71o"
./gradlew bootRun
```

이제 Postman에서 POST 요청을 보낸다.

```http id="68o1v8"
POST http://localhost:8080/boards
```

Body 설정은 다음과 같이 한다.

```text id="jfa2vb"
Body → raw → JSON
```

Body 내용

```json id="wic4s6"
{
  "title": "테스트 글"
}
```

응답 결과

```text id="7z428e"
생성됨:테스트 글
```

그 다음 다시 GET 요청을 보내본다.

```http id="0attj7"
GET http://localhost:8080/boards
```

응답 결과

```json id="e2p3we"
[
  "게시글1",
  "게시글2",
  "게시글3",
  "테스트 글"
]
```

POST로 보낸 데이터가 리스트에 추가된 것을 확인할 수 있다.

---
![](https://velog.velcdn.com/images/yorange50/post/fa05ea58-a8ee-43ad-a1b3-000b1731266f/image.png)

## 정리

이번 단계에서 한 일은 단순히 메서드 하나를 추가한 것이 아니다.

처음에는 조회만 가능했다.

```text id="z9hich"
GET /boards → 게시글 목록 조회
```

이제는 데이터를 추가할 수 있게 되었다.

```text id="eoqlpb"
POST /boards → 게시글 생성
```

같은 `/boards` 주소를 사용하더라도 HTTP Method에 따라 다른 동작을 만들 수 있다.

```text id="aaej8e"
GET  /boards → 조회
POST /boards → 생성
```

그리고 중요한 구조도 하나 배웠다.

```text id="ev3ruy"
Controller → 요청을 받음
Service    → 실제 로직을 처리함
```

Controller는 클라이언트의 요청을 받아서 Service에 넘기고, Service는 게시글을 조회하거나 추가하는 실제 동작을 담당한다.

아직 DB는 붙이지 않았다. 하지만 메모리 리스트를 사용해서 GET과 POST의 기본 흐름을 이해했다.

다음 단계에서는 `String` 하나로 게시글을 관리하지 않고, `id`, `title`을 가진 `Board` 객체를 만들어 실제 게시판에 가까운 구조로 바꿔볼 예정이다.
