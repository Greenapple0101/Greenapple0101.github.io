---
title: "[SPRING] 생성자 에러로 서버 안 뜰 때 — Board 수정 후 터진 컴파일 에러 해결"
source: "https://velog.io/@yorange50/SPRING-생성자-에러로-서버-안-뜰-때-Board-수정-후-터진-컴파일-에러-해결"
published: "2026-04-29T16:27:54.180Z"
tags: ""
backup_date: "2026-05-29T14:52:52.784462"
---

게시판을 만들다가 서버가 갑자기 안 뜨는 상황이 생겼다.

```text
./gradlew bootRun
→ 컴파일 에러 발생
```

로그를 보면 이런 메시지가 나온다.

```text
no suitable constructor found for Board(Long,String)
```

---

## 1. 문제 상황

에러가 난 코드:

```java
Board board = new Board(nextId++, title);
```

이 코드는 `(Long, String)` 형태의 생성자를 찾는다.

하지만 Board 클래스를 확인해보면

```java
public Board() {}

public Board(Long id, String title, String content, String author, String createdAt, String updatedAt) {}
```

이렇게 되어 있다.

즉 현재 존재하는 생성자는

```text
1. 기본 생성자
2. 모든 필드를 받는 생성자
```

뿐이다.

---

## 2. 왜 에러가 발생했을까

핵심 이유는 이거다.

```text
Board 구조는 바꿨는데
Service 코드는 그대로였다
```

처음에는 Board가 이렇게 생겼다.

```java
private Long id;
private String title;
```

그래서 이런 코드가 가능했다.

```java
new Board(id, title);
```

---

그런데 JSON 구조에 맞추기 위해 Board를 이렇게 확장했다.

```java
private Long id;
private String title;
private String content;
private String author;
private String createdAt;
private String updatedAt;
```

이 순간부터는 기존 생성자가 더 이상 맞지 않는다.

---

## 3. 해결 방법

### 방법 1 (권장)

Service 코드를 새로운 구조에 맞게 수정한다.

```java
public Board createBoard(Board board) {
    String now = LocalDateTime.now().toString();

    board.setId(nextId++);
    board.setCreatedAt(now);
    board.setUpdatedAt(now);

    boards.add(board);
    return board;
}
```

핵심 변화:

```text
new Board(...) 생성 방식 제거
→ Board 객체를 그대로 받아서 사용
```

---

### 방법 2 (비추천)

기존 생성자를 다시 추가한다.

```java
public Board(Long id, String title) {
    this.id = id;
    this.title = title;
}
```

이건 임시 해결은 되지만, 현재 JSON 기반 구조와 맞지 않는다.

---

## 4. 왜 방법 1이 맞는가

지금 구조는 이렇게 동작한다.

```text
프론트(JSON)
→ Controller (@RequestBody Board)
→ Service (Board 객체 그대로 사용)
```

즉 이미 Board 객체가 완성된 상태로 들어온다.

그래서 굳이

```java
new Board(...)
```

를 다시 만들 필요가 없다.

---

## 5. 추가로 헷갈렸던 부분

### npm 실행 에러

```text
npm error package.json 없음
```

이유:

```text
board_api = Spring (Java 프로젝트)
board_fe = React (Node 프로젝트)
```

그래서 실행 방법이 다르다.

```bash
# 백엔드
./gradlew bootRun

# 프론트
npm run dev
```

---

### cd~ 에러

```text
zsh: command not found: cd~
```

이건 단순한 문법 문제다.

```bash
cd ~
```

처럼 띄어쓰기 해야 한다.

---

## 6. 한 줄 정리

```text
Board 구조를 JSON에 맞게 바꾸면서
기존 생성자 방식이 깨졌고
Service 코드를 같이 수정해야 했다
```

---

## 7. 결론

이번 트러블은 단순한 문법 문제가 아니라

```text
데이터 구조 변경 → 서비스 로직 미반영
```

에서 발생한 문제였다.

이걸 이해하면 앞으로 구조 바꿀 때
어디까지 같이 고쳐야 하는지 감이 잡힌다.
