---
title: "[SPRING] String → 객체로 바꾸기"
source: "https://velog.io/@yorange50/SPRING-String-객체로-바꾸기"
published: "2026-04-29T11:35:26.025Z"
tags: ""
backup_date: "2026-05-29T14:52:52.786099"
---


지금까지 게시판 API는 `String`으로만 데이터를 관리하고 있었다.

```java
List<String> boards;
```

이 방식은 간단하지만 한계가 명확하다.

```text
id 없음
제목만 존재
데이터 구조 확장 어려움
```

실제 서비스에서는 게시글 하나가 단순 문자열이 아니라 여러 정보를 가진다.
그래서 `String`이 아니라 **객체로 관리**해야 한다.

---

## 1. Board 객체 만들기

게시글을 표현하는 클래스를 만든다.

```java
package com.board.api.domain;

public class Board {

    private Long id;
    private String title;

    public Board(Long id, String title) {
        this.id = id;
        this.title = title;
    }

    public Long getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }
}
```

이제 게시글 하나는 다음 형태가 된다.

```text
id + title
```

---

## 2. Service 수정

기존에는 `List<String>`이었다.

```java
private final List<String> boards = new ArrayList<>();
```

이걸 객체 리스트로 변경한다.

```java
private final List<Board> boards = new ArrayList<>();
private Long nextId = 1L;

public List<Board> getBoards(){
    return boards;
}

public Board createBoard(String title){
    Board board = new Board(nextId++, title);
    boards.add(board);
    return board;
}
```

여기서 중요한 부분

```java
nextId++
```

게시글이 생성될 때마다 id를 하나씩 증가시킨다.

---

## 3. Controller 수정

이제 반환 타입도 `String`이 아니라 `Board`로 바뀐다.

```java
@GetMapping("/boards")
public List<Board> getBoards(){
    return boardService.getBoards();
}

@PostMapping("/boards")
public Board createBoard(@RequestBody BoardRequest request){
    return boardService.createBoard(request.getTitle());
}
```

---

## 4. Postman 결과

### POST 요청

```json
{
  "title": "테스트 글"
}
```

응답

```json
{
  "id": 1,
  "title": "테스트 글"
}
```

---

### GET 요청

```json
[
  {
    "id": 1,
    "title": "테스트 글"
  }
]
```

---

## 5. 정리

기존

```text
String 기반 리스트
```

변경 후

```text
Board 객체 기반 리스트
```

차이는 단순하다.

```text
값 → 구조
```

이 단계부터는 단순 테스트 코드가 아니라
실제 서비스와 비슷한 형태로 발전하기 시작한다.

---

## 다음 단계

* PUT → 게시글 수정
* DELETE → 게시글 삭제
* CRUD 완성

여기까지 구현하면 기본적인 게시판 API 구조가 완성된다.
