---
title: "[SPRING] JPA Entity를 Controller까지 넘기면 왜 위험할까?"
source: "https://velog.io/@yorange50/SPRING-JPA-Entity를-Controller까지-넘기면-왜-위험할까"
published: "2026-05-07T08:31:09.488Z"
tags: ""
backup_date: "2026-05-29T14:52:52.769976"
---

Spring Boot로 게시판을 만들다 보면 처음에는 이런 식으로 코드를 짜게 된다.

```java
@GetMapping("/{id}")
public Board getBoard(@PathVariable Long id) {
    return boardService.getBoard(id);
}
```

또는 수정 API를 만들 때 이렇게 짤 수도 있다.

```java
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
```

처음 보면 별문제 없어 보인다.

`Board` 객체를 받아서
`Board` 객체를 수정하고
`Board` 객체를 반환한다.

간단하고 직관적이다.

그런데 실무 관점에서는 이 구조가 꽤 위험할 수 있다.

핵심은 이것이다.

> JPA Entity는 단순한 데이터 객체가 아니라, DB와 연결될 수 있는 객체다.

---

# 1. Entity는 그냥 객체가 아니다

JPA에서 `Board` 같은 Entity는 DB 테이블과 매핑되는 객체다.

```java
@Entity
public class Board {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String title;
    private String content;
    private String author;
}
```

겉으로 보면 그냥 자바 클래스다.

하지만 JPA가 관리하는 순간부터는 단순한 객체가 아니다.

```java
Board board = boardRepository.findById(id).orElseThrow();
```

이렇게 Repository를 통해 조회한 `board`는 JPA의 영속성 컨텍스트에서 관리될 수 있다.

쉽게 말하면 JPA가 이 객체를 보고 있다.

그래서 트랜잭션 안에서 이 객체의 값이 바뀌면 JPA는 이렇게 생각한다.

```text
처음 조회한 Board 상태 기억
→ 중간에 값이 바뀜
→ 트랜잭션 종료 시점에 변경 확인
→ UPDATE 쿼리 실행
```

이걸 JPA의 변경 감지, 즉 Dirty Checking이라고 한다.

---

# 2. Controller까지 Entity가 넘어가면 무슨 문제가 생길까?

일반적인 흐름은 이렇다.

```text
Repository
→ Service
→ Controller
```

만약 Repository에서 조회한 `Board Entity`가 Service를 거쳐 Controller까지 그대로 넘어간다면 어떻게 될까?

```text
Repository가 Board Entity 반환
→ Service가 Board Entity 받음
→ Service가 Board Entity 반환
→ Controller가 Board Entity 받음
```

결국 Controller도 DB와 연결될 수 있는 Entity를 직접 다루게 된다.

문제는 여기서 생긴다.

Controller에서 단순히 응답 데이터를 조금 가공하려고 했다고 해보자.

```java
@GetMapping("/{id}")
public Board getBoard(@PathVariable Long id) {
    Board board = boardService.getBoard(id);

    board.setTitle("[공지] " + board.getTitle());

    return board;
}
```

개발자는 단순히 화면에 보여줄 제목 앞에 `[공지]`를 붙이고 싶었을 수도 있다.

그런데 이 `board`가 JPA가 관리하는 Entity라면?

상황에 따라 DB에 실제로 업데이트될 가능성이 생긴다.

```text
Controller에서 board.setTitle()
→ Entity 값 변경
→ JPA 변경 감지
→ DB UPDATE 가능
```

즉, 나는 응답만 바꾸고 싶었는데
DB 데이터가 바뀔 수도 있는 것이다.

이게 위험한 이유다.

---

# 3. “보드보드보드” 구조의 문제

초반에 게시판을 만들다 보면 모든 곳에서 `Board`를 쓰게 된다.

```text
Controller도 Board
Service도 Board
Repository도 Board
Request도 Board
Response도 Board
DB Entity도 Board
```

이렇게 되면 코드가 짧아 보인다.

하지만 시간이 지나면 문제가 생긴다.

이 `Board`가 지금 어떤 역할인지 애매해진다.

```text
이 Board는 요청값인가?
이 Board는 DB Entity인가?
이 Board는 응답값인가?
이 Board는 화면에 보여줄 데이터인가?
```

모든 계층에서 같은 객체를 쓰면 책임이 섞인다.

특히 Entity는 DB와 연결되는 객체이기 때문에 더 조심해야 한다.

---

# 4. 위험한 코드 예시

아래 코드를 보자.

```java
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
```

이 코드는 동작할 수는 있다.

하지만 설계적으로는 불안하다.

문제는 크게 두 가지다.

---

## 1. 요청값을 Entity로 받고 있다

```java
public Board updateBoard(Long id, Board request)
```

`request`는 사용자가 보낸 요청 데이터다.

그런데 타입이 `Board`다.

즉, 외부에서 들어오는 데이터를 DB Entity로 받고 있다.

요청 데이터와 DB Entity는 역할이 다르다.

```text
요청 데이터: 사용자가 보낸 값
Entity: DB와 연결되는 내부 객체
```

이 둘을 같은 객체로 쓰면 위험하다.

---

## 2. 응답도 Entity로 반환하고 있다

```java
return board;
```

수정이 끝난 후 다시 `Board Entity`를 반환한다.

그러면 이 Entity가 Controller까지 넘어간다.

결국 Controller도 Entity를 알게 된다.

```text
Service 내부에서만 다뤄야 할 Entity가
Controller 바깥까지 노출됨
```

이 구조가 반복되면 Entity가 애플리케이션 전체에 퍼진다.

그리고 나중에 어디선가 `set()`을 해버리면 추적하기 어려워진다.

---

# 5. 그래서 DTO를 쓴다

이 문제를 막기 위해 Request DTO와 Response DTO를 따로 둔다.

```text
BoardCreateRequest
BoardUpdateRequest
BoardResponse
Board Entity
```

각 객체의 역할은 다르다.

```text
BoardCreateRequest  : 게시글 생성 요청
BoardUpdateRequest  : 게시글 수정 요청
Board Entity        : DB 저장/수정용 객체
BoardResponse       : 응답으로 내려줄 객체
```

즉, Entity 하나로 모든 걸 처리하지 않고 역할별로 객체를 분리하는 것이다.

---

# 6. 안전한 구조

안전한 흐름은 이렇다.

```text
Controller
→ Request DTO 받음

Service
→ Entity 조회
→ Entity 수정
→ Response DTO로 변환

Controller
→ Response DTO 반환
```

Entity는 Service 안에서만 다룬다.

Controller는 Entity를 직접 모른다.

```text
Controller는 Request/Response DTO만 안다.
Service는 Entity를 다룬다.
Repository는 Entity를 저장하고 조회한다.
```

이렇게 계층별 책임이 나뉜다.

---

# 7. Request DTO 만들기

수정 요청을 받을 DTO를 만든다.

```java
public class BoardUpdateRequest {

    private String title;
    private String content;
    private String author;

    public String getTitle() {
        return title;
    }

    public String getContent() {
        return content;
    }

    public String getAuthor() {
        return author;
    }
}
```

이 객체는 DB와 아무 관련이 없다.

그냥 사용자가 보낸 요청값을 담는 객체다.

```json
{
  "title": "수정된 제목",
  "content": "수정된 내용",
  "author": "홍길동"
}
```

이 JSON이 `BoardUpdateRequest`로 들어오는 것이다.

---

# 8. Response DTO 만들기

응답으로 내려줄 DTO도 따로 만든다.

```java
public class BoardResponse {

    private Long id;
    private String title;
    private String content;
    private String author;

    public BoardResponse(Board board) {
        this.id = board.getId();
        this.title = board.getTitle();
        this.content = board.getContent();
        this.author = board.getAuthor();
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
}
```

여기서 중요한 부분은 생성자다.

```java
public BoardResponse(Board board) {
    this.id = board.getId();
    this.title = board.getTitle();
    this.content = board.getContent();
    this.author = board.getAuthor();
}
```

Entity 값을 Response DTO에 복사한다.

즉, DB와 연결된 Entity를 그대로 반환하지 않고
응답용 객체를 새로 만들어 반환하는 것이다.

---

# 9. Entity는 내부에서만 사용하기

Entity는 이렇게 둔다.

```java
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

    public void update(String title, String content, String author) {
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
}
```

여기서 setter를 열어두지 않는 것이 좋다.

```java
public void update(String title, String content, String author) {
    this.title = title;
    this.content = content;
    this.author = author;
}
```

이렇게 의미 있는 메서드를 만들어두면 코드의 의도가 드러난다.

```java
board.update(title, content, author);
```

이 코드를 보면 “게시글을 수정하는구나”라고 바로 알 수 있다.

반대로 setter를 열어두면 이렇게 된다.

```java
board.setTitle(title);
board.setContent(content);
board.setAuthor(author);
```

각각의 값 변경은 보이지만, 이게 어떤 비즈니스 행위인지는 잘 드러나지 않는다.

---

# 10. Service 코드 개선하기

기존 코드는 이랬다.

```java
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
```

이제 DTO를 적용하면 이렇게 바뀐다.

```java
@Transactional
public BoardResponse updateBoard(Long id, BoardUpdateRequest request) {
    Board board = boardRepository.findById(id)
            .orElseThrow(() -> new IllegalArgumentException("게시글이 없습니다. id=" + id));

    board.update(
            request.getTitle(),
            request.getContent(),
            request.getAuthor()
    );

    return new BoardResponse(board);
}
```

차이를 보면 명확하다.

```java
BoardUpdateRequest request
```

요청은 DTO로 받는다.

```java
Board board = boardRepository.findById(id).orElseThrow();
```

DB에서 조회한 Entity는 Service 안에서만 다룬다.

```java
return new BoardResponse(board);
```

응답은 Entity가 아니라 Response DTO로 반환한다.

이렇게 하면 Entity가 Controller까지 직접 넘어가지 않는다.

---

# 11. Controller 코드

Controller는 이제 Entity를 몰라도 된다.

```java
@PutMapping("/boards/{id}")
public BoardResponse updateBoard(
        @PathVariable Long id,
        @RequestBody BoardUpdateRequest request
) {
    return boardService.updateBoard(id, request);
}
```

Controller의 역할은 단순하다.

```text
요청을 받는다.
Service에 넘긴다.
결과를 응답한다.
```

Controller는 DB Entity를 직접 수정하지 않는다.

이게 중요하다.

---

# 12. 패키지 구조

패키지는 보통 이렇게 나눌 수 있다.

```text
com.example.board
 ├── controller
 │    └── BoardController.java
 │
 ├── service
 │    └── BoardService.java
 │
 ├── repository
 │    └── BoardRepository.java
 │
 ├── entity
 │    └── Board.java
 │
 └── dto
      ├── BoardCreateRequest.java
      ├── BoardUpdateRequest.java
      └── BoardResponse.java
```

조금 더 나누고 싶다면 DTO를 request와 response로 나눌 수도 있다.

```text
dto
 ├── request
 │    ├── BoardCreateRequest.java
 │    └── BoardUpdateRequest.java
 │
 └── response
      └── BoardResponse.java
```

중요한 건 폴더 이름 자체가 아니다.

핵심은 역할 분리다.

```text
Entity는 DB용
Request DTO는 입력용
Response DTO는 출력용
```

---

# 13. “new Board”는 언제 써도 될까?

여기서 헷갈릴 수 있다.

“Service에서 new Board 하면 안 된다”는 말을 들으면
그럼 Entity는 언제 만들지? 라는 생각이 든다.

정리하면 이렇다.

## 생성할 때는 new Board를 쓴다

게시글을 새로 만들 때는 당연히 새 Entity를 만들어야 한다.

```java
@Transactional
public BoardResponse createBoard(BoardCreateRequest request) {
    Board board = new Board(
            request.getTitle(),
            request.getContent(),
            request.getAuthor()
    );

    Board savedBoard = boardRepository.save(board);

    return new BoardResponse(savedBoard);
}
```

생성은 새 데이터를 만드는 것이므로 `new Board()`가 자연스럽다.

---

## 수정할 때는 기존 Entity를 조회해서 바꾼다

수정은 새 객체를 만드는 것이 아니다.

이미 DB에 있는 객체를 찾아서 바꾸는 것이다.

```java
@Transactional
public BoardResponse updateBoard(Long id, BoardUpdateRequest request) {
    Board board = boardRepository.findById(id)
            .orElseThrow(() -> new IllegalArgumentException("게시글이 없습니다. id=" + id));

    board.update(
            request.getTitle(),
            request.getContent(),
            request.getAuthor()
    );

    return new BoardResponse(board);
}
```

수정할 때 갑자기 이렇게 하면 이상해진다.

```java
Board board = new Board(
        request.getTitle(),
        request.getContent(),
        request.getAuthor()
);
```

이건 기존 게시글을 수정하는 게 아니라
새 게시글 객체를 만드는 것에 가깝다.

그래서 정리하면 이렇다.

```text
Create  → new Board()
Update  → findById()로 기존 Board 조회 후 update()
Response → new BoardResponse(board)
```

---

# 14. Deep Copy 이야기는 결국 DTO 이야기다

Entity를 그대로 넘기지 말고 복사해서 넘기라는 말은 결국 DTO를 만들라는 뜻과 비슷하다.

```java
return new BoardResponse(board);
```

이 코드는 Entity의 값을 Response DTO에 복사한다.

즉, 이런 구조가 된다.

```text
Board Entity
→ 값만 꺼냄
→ BoardResponse에 담음
→ Controller에 반환
```

이제 Controller가 받는 것은 DB와 연결된 Entity가 아니다.

그냥 응답용 데이터 객체다.

```text
Board Entity    : DB와 연결될 수 있음
BoardResponse   : 응답용 데이터일 뿐
```

이 차이가 중요하다.

---

# 15. 최종 정리

JPA Entity를 Controller까지 그대로 넘기면 위험하다.

이유는 Entity가 단순한 객체가 아니라 DB와 연결될 수 있는 객체이기 때문이다.

```text
Repository에서 Entity 조회
→ Service가 Entity 반환
→ Controller가 Entity 받음
→ Controller에서 set()
→ JPA 변경 감지
→ DB UPDATE 가능
```

이런 일이 생기면 의도하지 않은 DB 갱신이 발생할 수 있다.

그래서 안전한 구조는 다음과 같다.

```text
Controller
→ Request DTO 받기

Service
→ Entity 조회
→ Entity 수정
→ Response DTO로 변환

Controller
→ Response DTO 반환
```

객체 역할도 이렇게 나눈다.

```text
Request DTO  : 외부에서 들어오는 값
Entity       : DB와 연결되는 내부 객체
Response DTO : 외부로 나가는 값
```

한 줄로 정리하면 이렇다.

> Entity는 DB 내부용 객체로 숨기고, Controller에는 Request/Response DTO만 넘기는 것이 안전하다.

처음에는 DTO를 따로 만드는 게 귀찮아 보일 수 있다.

하지만 프로젝트가 커질수록 이 분리는 굉장히 중요해진다.

요청값, DB 객체, 응답값이 섞이지 않아야 코드가 안전해지고
어디서 데이터가 바뀌는지도 추적하기 쉬워진다.
