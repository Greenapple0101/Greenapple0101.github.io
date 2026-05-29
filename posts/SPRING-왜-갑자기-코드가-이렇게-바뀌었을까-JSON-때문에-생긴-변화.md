---
title: "[SPRING] 왜 갑자기 코드가 이렇게 바뀌었을까? — JSON 때문에 생긴 변화"
source: "https://velog.io/@yorange50/SPRING-왜-갑자기-코드가-이렇게-바뀌었을까-JSON-때문에-생긴-변화"
published: "2026-04-29T16:11:19.428Z"
tags: ""
backup_date: "2026-05-29T14:52:52.784753"
---

이번에 게시판 코드를 바꾸면서 가장 큰 이유는 하나다.

```text
JSON 구조에 맞추기
```

처음에는 단순하게 `title` 하나만 다루는 코드였는데,
프론트와 연결하면서 상황이 완전히 달라졌다.

---

## 1. 문제 상황

프론트에서 보내는 데이터는 이렇게 생겼다.

```json
{
  "title": "제목",
  "content": "내용",
  "author": "작성자"
}
```

그런데 기존 백엔드 코드는 이렇게 받았다.

```java
@RequestBody Map<String, String> body
String title = body.get("title");
```

이 방식의 문제는 간단하다.

```text
title만 받고 나머지는 다 버림
```

즉 content, author는 아예 저장도 못 한다.

---

## 2. 해결 방법: JSON을 그대로 받자

Spring은 JSON을 Java 객체로 자동 변환해준다.

그래서 이렇게 바꿨다.

```java
@PostMapping("/boards")
public Board createBoard(@RequestBody Board board){
    return boardService.createBoard(board);
}
```

이제 흐름은 이렇게 된다.

```text
JSON → Board 객체로 자동 변환
```

프론트에서 보낸 값이 그대로 Board에 들어간다.

---

## 3. 그래서 Board 클래스도 바뀌었다

기존 Board는 이렇게 생겼다.

```java
private Long id;
private String title;
```

하지만 JSON은 더 많은 데이터를 가지고 있다.

그래서 이렇게 확장했다.

```java
private Long id;
private String title;
private String content;
private String author;
private String createdAt;
private String updatedAt;
```

이유는 간단하다.

```text
JSON 구조 = Board 구조
```

이게 맞아야 자동 변환이 된다.

---

## 4. getter, setter를 추가한 이유

Spring은 JSON을 객체로 바꿀 때 setter를 사용한다.

예를 들어 이런 JSON이 들어오면

```json
{
  "title": "게시글"
}
```

Spring 내부에서는 이렇게 실행된다.

```java
board.setTitle("게시글");
```

그래서 setter가 없으면 값이 안 들어간다.

getter는 반대로 값을 꺼낼 때 사용된다.

---

## 5. Service 코드가 바뀐 이유

기존 코드:

```java
public Board createBoards(String title){
    Board board = new Board(nextId++, title);
    boards.add(board);
    return board;
}
```

문제:

```text
title만 저장 가능
```

그래서 이렇게 바꿨다.

```java
public Board createBoard(Board board) {
    board.setId(nextId++);
    board.setCreatedAt(now);
    board.setUpdatedAt(now);
    boards.add(board);
    return board;
}
```

핵심 기준:

```text
프론트 → title, content, author 보냄
서버 → id, 시간(createdAt, updatedAt) 넣음
```

---

## 6. 수정(update) 로직도 바뀐 이유

기존:

```java
Board updated = new Board(id, title);
boards.remove(board);
boards.add(updated);
```

이건 새 객체로 교체하는 방식이다.

문제:

```text
content, author, createdAt 날아감
```

그래서 이렇게 바꿨다.

```java
board.setTitle(newBoard.getTitle());
board.setContent(newBoard.getContent());
board.setAuthor(newBoard.getAuthor());
```

기준:

```text
기존 데이터 유지 + 필요한 값만 수정
```

---

## 7. 프론트 TypeScript 코드가 바뀐 이유

기존에는 mock 데이터를 사용했다.

```ts
const mockBoards = require('./boards.json');
```

이건 실제 서버가 아니라 **프론트 내부 가짜 데이터**다.

그래서 실제 Spring 서버를 호출하도록 바꿨다.

```ts
fetch(`${API_BASE_URL}/boards`)
```

이제 흐름은 이렇게 된다.

```text
프론트 → fetch 요청
→ Spring Controller
→ Service
→ 데이터 처리
```

---

## 8. 전체 흐름 정리

이번 변경은 단순한 코드 수정이 아니다.

```text
프론트 JSON 구조
→ Controller에서 Board로 받기
→ Service에서 처리
→ 다시 JSON으로 응답
```

이 흐름을 맞춘 것이다.

---

## 9. 한 줄 결론

```text
이번 수정은 "JSON 구조에 맞춰서 프론트와 백엔드를 연결한 것"
```

처음에는 title 하나만 다루는 코드였다면,
이제는 실제 게시글 데이터를 다루는 구조가 된 것이다.
