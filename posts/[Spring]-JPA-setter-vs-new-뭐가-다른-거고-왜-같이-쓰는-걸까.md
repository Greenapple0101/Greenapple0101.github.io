---
title: "[SPRING] [JPA] setter vs new, 뭐가 다른 거고 왜 같이 쓰는 걸까?"
source: "https://velog.io/@yorange50/SPRING-JPA-setter-vs-new-뭐가-다른-거고-왜-같이-쓰는-걸까"
published: "2026-05-06T00:34:58.601Z"
tags: ""
backup_date: "2026-05-29T14:52:52.777655"
---



개발하다 보면 이런 말을 듣는다.

> setter 막 쓰지 말고 new로 객체 만들어서 관리해라

처음 들으면 헷갈린다.
setter랑 new가 서로 반대 개념 같기도 하고, 뭐가 문제인지 감이 안 온다.

결론부터 말하면 **둘은 역할이 완전히 다르고, 같이 쓰는 게 핵심이다.**

---

## setter와 new의 역할

```text
new
= 새로운 객체 생성 (새 상태 만들기)

setter
= 기존 객체 상태 변경
```

예를 들어:

```java
Board board = new Board("제목", "내용"); // new → 객체 생성
board.setTitle("수정 제목");             // setter → 값 변경
```

둘은 경쟁 관계가 아니라 **단계가 다른 개념**이다.

---

## 문제 상황: setter로 바로 덮어쓰기

보통 이렇게 많이 쓴다.

```java
Board board = boardRepository.findById(id).orElseThrow();

board.setTitle(request.getTitle());
board.setContent(request.getContent());
```

겉으로 보면 문제 없어 보인다.

하지만 흐름을 보면:

```text
기존 값 → 바로 사라짐
새 값 → 덮어씀
```

즉, 코드상에서는 이런 정보가 사라진다.

```text
기존 제목이 뭐였는지
새 제목이 뭔지
어디서 바뀌었는지
왜 바뀌었는지
```

그리고 JPA에서는 더 중요한 문제가 있다.

```text
영속 상태 엔티티 + setter
→ 변경 감지
→ 트랜잭션 종료 시 DB 반영
```

즉, **생각 없이 setter 쓰면 DB까지 바로 영향 간다.**

---

## 해결 방법: new로 “새 상태”를 분리

그래서 바로 setter를 쓰는 대신, 먼저 new로 새 값을 따로 만든다.

```java
BoardUpdateData updateData = new BoardUpdateData(
    request.getTitle(),
    request.getContent()
);
```

이렇게 하면 구조가 바뀐다.

```text
board (기존 상태)
updateData (새 상태)
```

이제 비교가 가능하다.

```java
log.info("oldTitle={}, newTitle={}",
        board.getTitle(),
        updateData.getTitle());
```

또는 검증도 가능하다.

```java
if (updateData.getTitle().isBlank()) {
    throw new IllegalArgumentException("제목은 비어 있을 수 없습니다.");
}
```

핵심:

```text
new = 변경될 값을 “보관”
setter = 기존 값을 “덮어씀”
```

---

## 최종 변경은 도메인에서 수행

그럼 언제 값을 바꾸냐?

결국 DB 반영하려면 기존 엔티티는 바뀌어야 한다.

하지만 setter로 직접 바꾸지 않는다.

```java
board.update(updateData);
```

도메인 안에서 처리한다.

```java
public void update(BoardUpdateData updateData) {
    this.title = updateData.getTitle();
    this.content = updateData.getContent();
}
```

차이는 명확하다.

```text
setter 호출
= 값만 바꿈 (의미 없음)

update 호출
= "게시글 수정"이라는 행위 수행
```

---

## 왜 이 방식이 실무에서 중요한가

이 구조를 쓰면 얻는 장점은 명확하다.

```text
1. 기존 값 vs 새 값 비교 가능
2. 로그 추적 쉬움
3. 변경 의도가 코드에 드러남
4. 도메인이 상태 변경을 통제함
5. JPA 변경 감지도 안전하게 활용 가능
```

특히 로그에서 차이가 크다.

```text
[나쁜 예]
board.setTitle(...)

[좋은 예]
oldTitle=기존, newTitle=수정
```

---

## 전체 흐름

```text
1. DB에서 엔티티 조회

2. new로 수정값 객체 생성

3. 기존 값과 비교 / 로그

4. 도메인 메서드 호출

5. 도메인 내부에서 값 변경

6. JPA가 변경 감지 후 DB 반영
```

---

## 한 줄 정리

```text
new
= 변경될 값을 따로 만든다

setter
= 기존 객체를 바꾼다

좋은 구조
= new로 값 분리 → 비교/로그 → 도메인 메서드로 변경
```

---

## 결론

setter를 쓰면 안 되는 게 아니라, **막 쓰면 안 되는 것**이다.

중요한 건 이거다.

```text
기존 상태와 변경 상태를 분리하고,
최종 변경은 도메인이 책임지게 만드는 것
```

이걸 이해하면 setter vs new는 더 이상 헷갈리지 않는다.
