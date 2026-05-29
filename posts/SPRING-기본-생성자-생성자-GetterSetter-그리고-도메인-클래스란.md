---
title: "[SPRING] 기본 생성자, 생성자, Getter/Setter, 그리고 도메인 클래스란?"
source: "https://velog.io/@yorange50/SPRING-기본-생성자-생성자-GetterSetter-그리고-도메인-클래스란"
published: "2026-04-30T00:53:01.932Z"
tags: ""
backup_date: "2026-05-29T14:52:52.783301"
---

Spring으로 게시판 API를 만들다 보면 아래처럼 생긴 클래스를 만나게 된다.

```java
public class Board {

    private Long id;
    private String title;
    private String content;
    private String author;
    private String createdAt;
    private String updatedAt;

    public Board() {}

    public Board(Long id, String title, String content, String author, String createdAt, String updatedAt) {
        this.id = id;
        this.title = title;
        this.content = content;
        this.author = author;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    public Long getId() { return id; }
    public String getTitle() { return title; }
}
```

처음 보면 그냥 코드 덩어리처럼 보이지만, 사실 역할이 명확하게 나뉘어 있다.

---

## 1. 생성자란?

```java
public Board(Long id, String title, ...)
```

생성자는 **객체를 만들 때 값을 넣기 위한 함수**다.

```java
Board board = new Board(1L, "제목", "내용", "작성자", "오늘", "오늘");
```

이렇게 하면 객체를 생성하면서 동시에 값을 세팅할 수 있다.

즉, “완성된 객체를 한 번에 만들고 싶을 때” 사용한다.

---

## 2. 기본 생성자란?

```java
public Board() {}
```

아무것도 없는 생성자다.

이건 왜 필요하냐면 **Spring이 내부적으로 객체를 만들 때 사용하기 때문**이다.

Spring은 보통 이렇게 동작한다:

1. `new Board()` 로 빈 객체 생성
2. setter로 값 하나씩 넣음

그래서 기본 생성자가 없으면 Spring이 객체를 못 만들어서 에러가 난다.

즉, **Spring을 쓸 때는 거의 필수라고 보면 된다.**

---

## 3. Getter란?

```java
public String getTitle() {
    return title;
}
```

getter는 **객체 안의 값을 꺼낼 때 사용**한다.

```java
board.getTitle();
```

그리고 중요한 점:

Spring이 JSON으로 응답을 만들 때도 getter를 사용한다.

그래서 getter가 없으면 응답(JSON)이 제대로 안 나올 수 있다.

---

## 4. Setter란?

```java
public void setTitle(String title) {
    this.title = title;
}
```

setter는 **값을 나중에 넣거나 수정할 때 사용**한다.

```java
Board board = new Board();
board.setTitle("제목");
```

또 하나 중요한 역할:

Spring이 JSON 요청을 받을 때 setter를 사용한다.

즉,

* 기본 생성자 → 객체 생성
* setter → 값 주입

이 구조로 동작한다.

---

## 5. 왜 이걸 “도메인 클래스”라고 부를까?

이게 핵심이다.

이 클래스는 단순한 코드가 아니라

**“게시글”이라는 개념 자체를 코드로 표현한 것**이다.

현실에서 게시글은:

* 제목이 있고
* 내용이 있고
* 작성자가 있다

이걸 코드로 옮긴 것이 바로 Board 클래스다.

즉,

> 도메인 = 현실 세계의 개념을 코드로 표현한 것

---

## 6. Controller, Service와의 차이

* Controller → 요청 받는 역할
* Service → 로직 처리
* Domain → 데이터 자체

Board는 “게시글이라는 데이터”이기 때문에 도메인이다.

---

## 정리

* 생성자 → 객체 만들 때 값 넣기
* 기본 생성자 → Spring이 객체 생성할 때 필요
* getter → 값 꺼내기 (응답)
* setter → 값 넣기 (요청)
* 도메인 → 현실 개념(게시글)을 코드로 표현한 것
