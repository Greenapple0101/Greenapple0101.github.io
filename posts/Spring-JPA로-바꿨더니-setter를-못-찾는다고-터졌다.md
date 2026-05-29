---
title: "[Spring] JPA로 바꿨더니 setter를 못 찾는다고 터졌다"
source: "https://velog.io/@yorange50/Spring-JPA로-바꿨더니-setter를-못-찾는다고-터졌다"
published: "2026-05-06T03:54:36.430Z"
tags: ""
backup_date: "2026-05-29T14:52:52.776266"
---



Docker로 PostgreSQL을 띄우고, 기존 board_api를 JPA 기반으로 바꾸는 중에 컴파일 에러가 발생했다.

에러 메시지는 대략 이런 형태였다.

```text id="zsgftv"
cannot find symbol
symbol:   method setId(java.lang.Long)
location: variable board of type com.board.api.domain.Board

cannot find symbol
symbol:   method setCreatedAt(java.lang.String)
location: variable board of type com.board.api.domain.Board

cannot find symbol
symbol:   method setUpdatedAt(java.lang.String)
location: variable board of type com.board.api.domain.Board

cannot find symbol
symbol:   method setTitle(java.lang.String)
location: variable board of type com.board.api.domain.Board

cannot find symbol
symbol:   method setContent(java.lang.String)
location: variable board of type com.board.api.domain.Board

cannot find symbol
symbol:   method getAuthor()
location: variable newBoard of type com.board.api.domain.Board
```

처음에는 PostgreSQL 연결 문제인 줄 알았다.
Docker에서 PostgreSQL 컨테이너를 띄운 직후였고, `pom.xml`에 JPA와 PostgreSQL 의존성도 추가한 상태였기 때문이다.

하지만 이 에러는 DB 연결 문제가 아니었다.
애플리케이션이 실행되기 전에 Java 컴파일 단계에서 막힌 문제였다.

---

## 1. 상황

기존 board_api는 DB 없이 동작하던 구조였다.

```text id="vvx2hq"
Controller
→ Service
→ List 또는 JSON 파일
```

즉 게시글 데이터를 메모리나 JSON 파일에 저장하고 있었다.

그러다가 구조를 다음처럼 바꾸기 시작했다.

```text id="f6g20r"
Controller
→ Service
→ Repository
→ PostgreSQL
```

이를 위해 `Board` 클래스를 JPA 엔티티로 수정했다.

```java id="w1cc34"
@Entity
public class Board {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String title;
    private String content;

    protected Board() {
    }

    public Board(String title, String content) {
        this.title = title;
        this.content = content;
    }

    public void update(String title, String content) {
        this.title = title;
        this.content = content;
    }
}
```

여기서 중요한 점은 setter를 제거했다는 것이다.

이전에는 이런 식으로 값을 바꾸고 있었다.

```java id="ubdb1i"
board.setTitle(request.getTitle());
board.setContent(request.getContent());
```

하지만 JPA 엔티티로 바꾸면서 무분별한 setter 사용을 줄이고,
의미 있는 변경 메서드를 사용하도록 방향을 바꿨다.

```java id="9g0tvm"
board.update(request.getTitle(), request.getContent());
```

---

## 2. 에러 원인

문제는 `Board` 엔티티만 새 방식으로 바꾸고,
`BoardService`는 아직 예전 방식 그대로였다는 점이다.

즉 코드 상태가 이렇게 섞여 있었다.

```text id="cx4kl0"
Board.java
→ JPA 엔티티 방식
→ setter 없음
→ update() 메서드 사용

BoardService.java
→ 기존 JSON/List 방식
→ setId(), setTitle(), setContent(), setUpdatedAt() 호출
```

그래서 컴파일러 입장에서는 이런 상황이 된 것이다.

```java id="efxhw4"
board.setTitle(...);
```

그런데 `Board` 클래스 안에는 `setTitle()`이 없다.

그래서 컴파일러가 이렇게 말한 것이다.

```text id="ajq0fh"
Board 타입에는 setTitle이라는 메서드가 없습니다.
```

즉 핵심 원인은 이거다.

```text id="jhpt1z"
setter를 없앴는데 Service에서는 아직 setter를 호출하고 있었다.
```

---

## 3. 왜 setId()도 문제가 되었나?

에러 중에는 이런 것도 있었다.

```text id="7zcqgj"
cannot find symbol
symbol: method setId(java.lang.Long)
```

기존에는 아마 게시글을 생성할 때 직접 id를 만들어서 넣고 있었을 가능성이 크다.

예를 들어 이런 식이다.

```java id="08e6jz"
board.setId(nextId++);
```

메모리 기반 저장소에서는 이런 코드가 필요할 수 있다.
DB가 없으니 애플리케이션이 직접 id를 관리해야 하기 때문이다.

하지만 JPA + PostgreSQL 구조에서는 다르다.

```java id="bwp4hm"
@Id
@GeneratedValue(strategy = GenerationType.IDENTITY)
private Long id;
```

이렇게 설정하면 id는 DB가 자동으로 생성한다.

그래서 JPA 구조에서는 보통 이런 코드를 직접 작성하지 않는다.

```java id="lztcem"
board.setId(...)
```

id는 개발자가 setter로 넣는 값이 아니라,
DB에 저장될 때 자동으로 부여되는 값이다.

---

## 4. createdAt, updatedAt 문제

에러에는 이런 것도 있었다.

```text id="9c4y4v"
cannot find symbol
symbol: method setCreatedAt(java.lang.String)

cannot find symbol
symbol: method setUpdatedAt(java.lang.String)
```

이것도 같은 원리다.

`BoardService`에서는 여전히 다음과 같은 코드를 호출하고 있었다.

```java id="rx391b"
board.setCreatedAt(...);
board.setUpdatedAt(...);
```

하지만 새로 바꾼 `Board` 엔티티에는 해당 필드나 setter가 없었다.

이 문제는 두 가지 방식으로 해결할 수 있다.

### 방법 1. 일단 시간 필드를 제거한다

처음 JPA 연결 단계에서는 CRUD와 DB 연결이 먼저다.
그래서 `createdAt`, `updatedAt`을 잠시 빼고 단순하게 가져갈 수 있다.

```java id="mkn204"
private String title;
private String content;
private String author;
```

이렇게 하면 구조가 단순해져서 JPA 연결 확인이 쉬워진다.

### 방법 2. 엔티티에 시간 필드를 제대로 추가한다

나중에 시간 필드를 넣고 싶다면 `String`보다는 `LocalDateTime`을 사용하는 것이 자연스럽다.

```java id="lhntqb"
private LocalDateTime createdAt;
private LocalDateTime updatedAt;
```

그리고 JPA 생명주기 콜백을 사용할 수도 있다.

```java id="j5mveq"
@PrePersist
public void prePersist() {
    this.createdAt = LocalDateTime.now();
    this.updatedAt = LocalDateTime.now();
}

@PreUpdate
public void preUpdate() {
    this.updatedAt = LocalDateTime.now();
}
```

하지만 처음 DB 연결 단계에서는 너무 많은 걸 한 번에 바꾸면 에러 지점이 늘어난다.
그래서 처음에는 시간 필드를 빼고, CRUD가 정상 동작한 뒤에 추가하는 편이 좋다.

---

## 5. getAuthor() 문제

에러 중에는 이런 것도 있었다.

```text id="3ryrbz"
cannot find symbol
symbol: method getAuthor()
location: variable newBoard of type Board
```

이건 `BoardService`에서 `newBoard.getAuthor()` 또는 `request.getAuthor()`를 호출하고 있는데,
`Board` 엔티티에는 `author` 필드와 `getAuthor()` 메서드가 없어서 발생한 문제다.

해결 방법은 둘 중 하나다.

### 방법 1. author를 사용할 거면 Board에 추가

```java id="0udmf1"
private String author;

public String getAuthor() {
    return author;
}
```

생성자와 update 메서드에도 포함한다.

```java id="b95nly"
public Board(String title, String content, String author) {
    this.title = title;
    this.content = content;
    this.author = author;
}

public void update(String title, String content, String author) {
    this.title = title;
    this.content = content;
    this.author = author;
}
```

### 방법 2. author를 안 쓸 거면 Service에서 제거

게시글에 작성자가 필요 없다면 `BoardService`에서 `getAuthor()` 호출을 제거하면 된다.

```java id="i2kawk"
Board newBoard = new Board(
        board.getTitle(),
        board.getContent()
);
```

핵심은 `Board.java`와 `BoardService.java`가 같은 필드 기준을 바라봐야 한다는 것이다.

---

## 6. 수정 방향

기존 Service는 이런 방식이었다.

```java id="xey2co"
board.setId(...);
board.setCreatedAt(...);
board.setUpdatedAt(...);
board.setTitle(...);
board.setContent(...);
```

JPA 방식으로 바꾸면 이렇게 가야 한다.

```java id="syl54s"
Board newBoard = new Board(
        request.getTitle(),
        request.getContent(),
        request.getAuthor()
);

boardRepository.save(newBoard);
```

수정할 때는 setter로 값을 하나씩 넣는 것보다,
생성자를 통해 처음부터 유효한 객체를 만드는 쪽이 낫다.

게시글 수정도 마찬가지다.

기존 방식:

```java id="1lfpl6"
board.setTitle(request.getTitle());
board.setContent(request.getContent());
board.setUpdatedAt(...);
```

수정 후:

```java id="d4brza"
board.update(
        request.getTitle(),
        request.getContent(),
        request.getAuthor()
);
```

이렇게 하면 단순히 값을 바꾸는 코드가 아니라,
“게시글을 수정한다”는 의미가 코드에 드러난다.

---

## 7. 수정한 Board 엔티티 예시

```java id="b60m13"
package com.board.api.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class Board {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String title;

    private String content;

    private String author;

    protected Board() {
    }

    public Board(String title, String content, String author) {
        this.title = title;
        this.content = content;
        this.author = author;
    }

    public Long getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public String getContent() {
        return content;
    }

    public String getAuthor() {
        return author;
    }

    public void update(String title, String content, String author) {
        this.title = title;
        this.content = content;
        this.author = author;
    }
}
```

---

## 8. 수정한 BoardService 예시

```java id="qjzqka"
package com.board.api.service;

import com.board.api.domain.Board;
import com.board.api.repository.BoardRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class BoardService {

    private final BoardRepository boardRepository;

    public BoardService(BoardRepository boardRepository) {
        this.boardRepository = boardRepository;
    }

    @Transactional(readOnly = true)
    public List<Board> getBoards() {
        return boardRepository.findAll();
    }

    @Transactional(readOnly = true)
    public Board getBoard(Long id) {
        return boardRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("게시글이 없습니다. id=" + id));
    }

    @Transactional
    public Board createBoard(Board request) {
        Board board = new Board(
                request.getTitle(),
                request.getContent(),
                request.getAuthor()
        );

        return boardRepository.save(board);
    }

    @Transactional
    public Board updateBoard(Long id, Board request) {
        Board board = boardRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("게시글이 없습니다. id=" + id));

        board.update(
                request.getTitle(),
                request.getContent(),
                request.getAuthor()
        );

        return board;
    }

    @Transactional
    public void deleteBoard(Long id) {
        boardRepository.deleteById(id);
    }
}
```

---

## 9. 이번 트러블슈팅에서 배운 것

이번 문제는 PostgreSQL이나 Docker 문제가 아니었다.

Docker에서 PostgreSQL 컨테이너는 정상적으로 떠 있었다.

```text id="q8swbl"
board-postgres
5432:5432
running
```

하지만 Spring Boot 애플리케이션은 실행되기도 전에 컴파일에서 실패했다.

즉 문제 위치는 DB 연결이 아니라 Java 코드였다.

```text id="j49crf"
DB 연결 문제
→ 애플리케이션 실행 후 datasource 연결 단계에서 발생

컴파일 문제
→ 애플리케이션 실행 전 Java 코드 컴파일 단계에서 발생
```

에러 메시지에 `cannot find symbol`이 나오면 보통 다음을 먼저 봐야 한다.

```text id="oxp4is"
메서드 이름이 실제 클래스에 존재하는가?
필드가 있는가?
getter/setter가 있는가?
import가 맞는가?
클래스 구조를 바꿨는데 사용하는 쪽 코드를 안 바꾼 건 아닌가?
```

이번 경우에는 마지막 항목이었다.

```text id="3emrsz"
Board 엔티티 구조를 바꿨는데
BoardService가 아직 예전 구조를 사용하고 있었다.
```

---

## 10. 정리

JPA로 넘어가면서 단순히 DB 연결 설정만 바꾸는 게 아니라,
객체를 다루는 방식도 같이 바뀐다.

기존 방식은 이랬다.

```text id="94dm6u"
직접 id 부여
setter로 값 변경
List 또는 JSON 파일에 저장
```

JPA 방식은 이렇게 바뀐다.

```text id="3uqzg2"
id는 DB가 자동 생성
Repository가 CRUD 담당
엔티티는 의미 있는 생성자와 변경 메서드로 상태 변경
Service는 Repository를 통해 DB에 저장
```

그래서 setter를 없애기로 했다면,
Service에서도 setter를 호출하면 안 된다.

```java id="uq3kgf"
board.setTitle(...)
board.setContent(...)
```

이런 코드는 다음처럼 바꿔야 한다.

```java id="636ocf"
board.update(title, content, author);
```

이번 에러의 핵심은 이 한 줄로 정리할 수 있다.

```text id="9g0ftx"
엔티티는 JPA 방식으로 바꿨는데, Service는 아직 예전 setter 방식이라 컴파일이 실패했다.
```

이후에는 먼저 컴파일이 되는 구조를 만들고,
그다음 PostgreSQL 연결, 테이블 생성, CRUD 요청 테스트 순서로 확인하면 된다.
