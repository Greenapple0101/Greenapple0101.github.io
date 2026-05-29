---
title: "[SPRING] JPA와 Hibernate?"
source: "https://velog.io/@yorange50/SPRING-JPA와-Hibernate"
published: "2026-05-03T23:50:25.631Z"
tags: "Spring"
backup_date: "2026-05-29T14:52:52.779850"
---

Spring Boot로 게시판 API를 만들다 보면 처음에는 데이터를 `List`에 저장하게 된다.

```java
private final List<Board> boards = new ArrayList<>();
```

이 방식은 이해하기 쉽다. 게시글을 만들면 리스트에 넣고, 조회하면 리스트에서 찾고, 수정하면 리스트 안의 객체 값을 바꾸고, 삭제하면 리스트에서 제거하면 된다.

하지만 이 방식에는 치명적인 문제가 있다.

**서버를 껐다 켜면 데이터가 전부 사라진다.**

즉, 이건 진짜 저장이 아니라 프로그램이 실행되는 동안만 살아 있는 임시 저장소다. 그래서 실제 서비스처럼 데이터를 보존하려면 DB가 필요하다. 그리고 자바 객체와 DB를 연결해주는 기술이 바로 **JPA**다.

---

## JPA란?

JPA는 **Java Persistence API**의 줄임말이다.

쉽게 말하면 **자바 객체를 DB에 저장하기 위한 표준 규칙**이다.

원래 DB에 데이터를 저장하려면 SQL을 직접 작성해야 한다.

```sql
INSERT INTO board (title, content, author)
VALUES ('제목', '내용', '작성자');
```

조회할 때도 SQL을 직접 작성해야 한다.

```sql
SELECT *
FROM board
WHERE id = 1;
```

그런데 Spring Boot에서 JPA를 사용하면 자바 코드 중심으로 데이터를 다룰 수 있다.

```java
boardRepository.save(board);
```

이렇게 작성하면 게시글 객체가 DB에 저장된다.

조회도 마찬가지다.

```java
boardRepository.findById(id);
```

직접 SQL을 작성하지 않아도, 자바 객체를 기준으로 데이터를 저장하고 조회할 수 있다.

즉, JPA는 다음과 같은 역할을 한다.

```text
자바 객체 ↔ DB 테이블
```

자바에서는 `Board`라는 객체를 사용하고, DB에서는 `board`라는 테이블을 사용한다. JPA는 이 둘을 연결해주는 표준 방식이다.

---

## Entity란?

JPA를 사용하려면 DB 테이블과 연결될 자바 클래스를 만들어야 한다. 이 클래스를 **Entity**라고 한다.

예를 들어 게시판의 게시글을 저장한다면 다음과 같이 작성할 수 있다.

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

여기서 중요한 어노테이션은 세 가지다.

```java
@Entity
```

이 클래스가 DB 테이블과 연결되는 객체라는 뜻이다.

```java
@Id
```

이 필드가 PK, 즉 기본키라는 뜻이다.

```java
@GeneratedValue(strategy = GenerationType.IDENTITY)
```

id 값을 DB가 자동으로 증가시켜준다는 뜻이다.

즉, 위 코드는 대략 이런 테이블과 연결된다고 볼 수 있다.

```sql
CREATE TABLE board (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255),
    content VARCHAR(255),
    author VARCHAR(255)
);
```

---

## Repository란?

기존에는 데이터를 직접 리스트에 저장했다.

```java
private final List<Board> boards = new ArrayList<>();
```

하지만 JPA를 사용하면 Repository를 만든다.

```java
public interface BoardRepository extends JpaRepository<Board, Long> {
}
```

이 코드 한 줄로 기본적인 CRUD 기능을 사용할 수 있다.

```java
boardRepository.findAll();
boardRepository.findById(id);
boardRepository.save(board);
boardRepository.deleteById(id);
```

직접 `for문`으로 리스트를 돌면서 게시글을 찾을 필요가 없다.

기존 방식은 이런 느낌이었다.

```java
public Board getBoard(Long id) {
    for (Board board : boards) {
        if (board.getId().equals(id)) {
            return board;
        }
    }
    throw new RuntimeException("해당 게시글 없음");
}
```

JPA를 사용하면 이렇게 바뀐다.

```java
public Board getBoard(Long id) {
    return boardRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("해당 게시글 없음"));
}
```

훨씬 DB 중심의 코드가 되고, 실제 데이터도 메모리가 아니라 DB에 저장된다.

---

## Hibernate란?

JPA를 공부하다 보면 Hibernate라는 말이 같이 나온다.

처음에는 JPA와 Hibernate가 같은 것처럼 느껴질 수 있다. 하지만 둘은 정확히 다르다.

```text
JPA = 자바 ORM 표준
Hibernate = JPA를 실제로 구현한 대표 라이브러리
```

JPA는 규칙이다.

“자바 객체를 DB에 저장하려면 이런 방식으로 해야 한다”라는 표준이다.

반면 Hibernate는 그 규칙을 실제로 동작하게 해주는 구현체다.

비유하면 다음과 같다.

```text
JPA = 운전면허 규칙
Hibernate = 실제 자동차
Spring Data JPA = 운전 보조 시스템
DB = 목적지
```

JPA만 있다고 해서 실제로 DB에 저장되는 것은 아니다. JPA라는 규칙을 구현한 실제 엔진이 필요하다. 그 대표적인 구현체가 Hibernate다.

Spring Boot에서 `spring-boot-starter-data-jpa`를 추가하면 보통 Hibernate가 기본으로 함께 들어온다. 그래서 우리가 직접 Hibernate를 강하게 의식하지 않아도 내부에서는 Hibernate가 SQL을 만들어 DB와 통신하고 있다.

---

## Hibernate는 실제로 무엇을 할까?

우리가 이런 코드를 작성한다고 해보자.

```java
boardRepository.save(board);
```

겉으로 보기에는 SQL이 없다.

하지만 Hibernate는 내부적으로 이런 SQL을 만들어 실행한다.

```sql
INSERT INTO board (title, content, author)
VALUES (?, ?, ?);
```

조회도 마찬가지다.

```java
boardRepository.findById(1L);
```

Hibernate는 내부적으로 다음과 비슷한 SQL을 실행한다.

```sql
SELECT *
FROM board
WHERE id = 1;
```

그래서 실행 로그를 보면 이런 문장을 볼 수 있다.

```text
Hibernate: insert into board ...
Hibernate: select ...
```

이 말은 내가 직접 SQL을 작성하지 않았지만, Hibernate가 대신 SQL을 생성하고 실행했다는 뜻이다.

---

## ORM이란?

Hibernate는 ORM 프레임워크다.

ORM은 **Object-Relational Mapping**의 줄임말이다.

```text
Object = 자바 객체
Relational = 관계형 DB
Mapping = 연결
```

즉, ORM은 자바 객체와 관계형 DB 테이블을 연결해주는 기술이다.

자바에서는 객체 중심으로 생각한다.

```java
Board board = new Board();
board.setTitle("제목");
board.setContent("내용");
board.setAuthor("작성자");
```

DB에서는 테이블과 행 중심으로 생각한다.

```text
board 테이블

id | title | content | author
1  | 제목  | 내용     | 작성자
```

ORM은 이 두 세계를 연결해준다.

그래서 개발자는 객체를 다루듯이 코드를 작성하고, Hibernate가 그 객체를 DB 테이블에 맞게 저장하거나 조회해준다.

---

## JPA, Hibernate, Spring Data JPA의 관계

처음에는 이 세 개가 헷갈린다.

정리하면 다음과 같다.

```text
JPA
자바에서 ORM을 사용하기 위한 표준 인터페이스

Hibernate
JPA 표준을 실제로 구현한 ORM 프레임워크

Spring Data JPA
Spring에서 JPA를 더 편하게 사용할 수 있게 해주는 기술
```

구조로 보면 이렇다.

```text
Controller
    ↓
Service
    ↓
Repository
    ↓
Spring Data JPA
    ↓
Hibernate
    ↓
DB
```

개발자가 주로 만지는 부분은 Controller, Service, Repository다.

그 아래에서 Spring Data JPA가 Repository 기능을 편하게 제공하고, Hibernate가 실제 SQL을 만들어 DB와 통신한다.

---

## 기존 게시판 코드에서 JPA로 바뀌는 흐름

처음 게시판 API를 만들면 보통 이런 구조다.

```text
Controller
    ↓
Service
    ↓
List<Board>
```

이 방식은 빠르게 CRUD를 연습하기 좋다.

하지만 데이터가 메모리에만 있기 때문에 서버를 재시작하면 사라진다.

JPA를 적용하면 구조가 바뀐다.

```text
Controller
    ↓
Service
    ↓
BoardRepository
    ↓
JPA / Hibernate
    ↓
DB
```

이제 게시글은 메모리 리스트가 아니라 실제 DB 테이블에 저장된다.

---

## JPA를 쓰기 전 코드

예를 들어 게시글 생성 로직이 이렇게 되어 있었다.

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

여기서는 `nextId`도 직접 증가시키고, `boards.add(board)`로 리스트에 직접 넣는다.

하지만 JPA를 사용하면 이렇게 바뀐다.

```java
public Board createBoard(Board board) {
    return boardRepository.save(board);
}
```

저장 로직이 훨씬 단순해진다.

id 증가도 DB가 처리할 수 있고, 저장도 Repository가 처리한다.

---

## JPA를 쓰면 좋은 점

JPA를 사용하면 SQL을 매번 직접 작성하지 않아도 된다.

기본적인 CRUD는 Repository 메서드로 처리할 수 있다.

```java
findAll()
findById()
save()
deleteById()
```

또한 자바 객체 중심으로 개발할 수 있다. 테이블을 먼저 생각하기보다, 도메인 객체를 중심으로 코드를 설계할 수 있다.

그리고 DB가 메모리가 아니라 실제 저장소가 되기 때문에 서버를 껐다 켜도 데이터가 유지된다.

즉, 단순 연습용 API에서 실제 서비스 구조로 넘어가기 위한 중요한 단계다.

---

## 하지만 JPA가 만능은 아니다

JPA를 쓰면 편하지만, 내부에서 SQL이 어떻게 나가는지 모르면 문제가 생겼을 때 디버깅이 어렵다.

예를 들어 이런 문제가 나올 수 있다.

```text
LazyInitializationException
SQLGrammarException
DuplicateMappingException
```

또는 예상보다 SQL이 많이 나가는 N+1 문제도 생길 수 있다.

그래서 JPA를 쓴다고 해서 SQL을 몰라도 되는 것은 아니다.

오히려 실무에서는 JPA를 쓰면서도 Hibernate가 어떤 SQL을 생성하는지 확인할 수 있어야 한다.

즉, JPA는 SQL을 없애주는 기술이라기보다는, **반복적인 SQL 작성을 줄여주고 객체 중심 개발을 가능하게 해주는 기술**이라고 보는 게 맞다.

---

## 정리

JPA와 Hibernate를 한 문장으로 정리하면 다음과 같다.

```text
JPA는 자바 객체를 DB에 저장하기 위한 표준이고,
Hibernate는 그 표준을 실제로 동작하게 해주는 대표 구현체다.
```

게시판 프로젝트 기준으로 보면, 처음에는 `List<Board>`에 데이터를 저장했다.

```java
private final List<Board> boards = new ArrayList<>();
```

하지만 이 방식은 서버를 재시작하면 데이터가 사라진다.

JPA를 적용하면 게시글이 실제 DB에 저장된다.

```java
boardRepository.save(board);
```

그리고 이 코드 뒤에서 Hibernate가 SQL을 생성하고 실행한다.

결국 흐름은 이렇게 정리할 수 있다.

```text
List 저장 방식
메모리에 임시 저장
서버 재시작 시 데이터 삭제

JPA 저장 방식
객체를 DB에 저장
서버 재시작 후에도 데이터 유지

Hibernate
JPA 요청을 실제 SQL로 변환해서 DB와 통신
```

처음에는 JPA, Hibernate, Spring Data JPA가 헷갈릴 수 있다. 하지만 큰 흐름만 잡으면 된다.

```text
JPA = 표준
Hibernate = 구현체
Spring Data JPA = 더 쉽게 쓰게 해주는 Spring 기술
```

즉, JPA와 Hibernate는 단순히 새로운 문법이 아니라, Spring Boot 게시판 API가 **진짜 DB를 사용하는 서비스 구조로 발전하는 핵심 단계**다.
