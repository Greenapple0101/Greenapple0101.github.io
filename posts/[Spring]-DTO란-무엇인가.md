---
title: "[Spring] DTO란 무엇인가"
source: "https://velog.io/@yorange50/Spring-DTO란-무엇인가"
published: "2026-05-06T00:51:05.416Z"
tags: ""
backup_date: "2026-05-29T14:52:52.777123"
---

DTO는 **Data Transfer Object**의 줄임말이다.
이름 그대로 **데이터를 전달하기 위한 객체**다.

---

## 1. 왜 DTO를 쓰냐

보통 처음에는 이렇게 하고 싶어진다.

```java
@PostMapping("/boards")
public void createBoard(@RequestBody Board board) {
    boardRepository.save(board);
}
```

겉으로는 편하다.
하지만 문제가 있다.

```text
Entity를 그대로 외부에 노출
원치 않는 필드까지 들어올 수 있음
도메인 구조가 API에 종속됨
```

그래서 중간에 DTO를 둔다.

---

## 2. DTO의 역할

```text
클라이언트 ↔ 서버 사이 데이터 전달
요청 데이터 담기
응답 데이터 만들기
```

즉, DTO는 “통신용 객체”다.

---

## 3. DTO 기본 예시

### 요청 DTO

```java
public class BoardRequest {

    private String title;
    private String content;

    public String getTitle() {
        return title;
    }

    public String getContent() {
        return content;
    }
}
```

### 응답 DTO

```java
public class BoardResponse {

    private Long id;
    private String title;
    private String content;

    public BoardResponse(Long id, String title, String content) {
        this.id = id;
        this.title = title;
        this.content = content;
    }
}
```

---

## 4. 흐름에서 DTO 위치

```text
Controller → DTO → Service → Entity → DB
```

예:

```java
@PostMapping("/boards")
public void createBoard(@RequestBody BoardRequest request) {
    boardService.createBoard(request);
}
```

Service:

```java
public void createBoard(BoardRequest request) {
    Board board = new Board(request.getTitle(), request.getContent());
    boardRepository.save(board);
}
```

---

## 5. DTO vs Entity 차이

```text
DTO
= 데이터 전달용
= setter 사용 가능
= 비즈니스 로직 없음

Entity
= DB와 연결
= 상태 변경 책임 있음
= setter 지양
```

---

## 6. DTO를 쓰는 이유 정리

```text
Entity 보호
API 구조와 도메인 분리
필요한 데이터만 전달
유효성 검증 위치 확보
```

---

## 7. 한 줄 정리

```text
DTO = 외부와 데이터를 주고받기 위한 전용 객체
```

---

## 8. 감각 잡기

```text
Controller는 DTO만 본다
Service는 DTO → Entity 변환한다
Entity는 자기 상태만 관리한다
```

이 구조를 지키면 설계가 훨씬 깔끔해진다.
