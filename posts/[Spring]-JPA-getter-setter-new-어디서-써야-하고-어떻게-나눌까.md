---
title: "[Spring/JPA] getter, setter, new… 어디서 써야 하고 어떻게 나눌까?"
source: "https://velog.io/@yorange50/SpringJPA-getter-setter-new-어디서-써야-하고-어떻게-나눌까"
published: "2026-05-06T00:39:52.256Z"
tags: ""
backup_date: "2026-05-29T14:52:52.777326"
---

Spring + JPA를 처음 적용하면 이런 고민이 생긴다.

> setter는 쓰면 안 된다는데 어디서 쓰는 거지?
> new는 왜 쓰라는 거지?
> 서비스랑 도메인은 뭐가 다른 거지?

이걸 한 번에 정리해보면 **“역할 분리”**로 이해하면 깔끔해진다.

---

# 1. 전체 그림 먼저

```text
Controller
= 요청/응답

Service
= 흐름 제어 (트랜잭션, 조회, 호출)

Domain(Entity)
= 상태 변경 책임

DTO/POJO
= 데이터 전달용 객체
```

그리고 핵심 원칙:

```text
읽기(getter) = 자유

쓰기(setter) = 제한

상태 변경 = 도메인이 책임
```

---

# 2. getter는 어디서 쓰냐

getter는 단순히 값 읽는 거라서 제한 거의 없다.

```java
log.info("title={}", board.getTitle());
return board.getTitle();
```

사용 위치:

```text
Controller
Service
DTO 변환
로그
```

정리:

```text
getter = 어디서든 OK
```

---

# 3. setter는 어디서 쓰냐 (핵심)

## 엔티티에서 setter 남용

```java
board.setTitle(request.getTitle());
board.setContent(request.getContent());
```

이게 문제인 이유:

```text
변경 의도 안 보임
누가 바꿨는지 추적 어려움
도메인 규칙 깨질 수 있음
JPA 변경 감지로 DB 반영됨
```

---

## 엔티티에서는 “행위 메서드” 사용

```java
board.update(request.getTitle(), request.getContent());
```

```java
public void update(String title, String content) {
    this.title = title;
    this.content = content;
}
```

차이:

```text
setter
= 값만 바꿈

update()
= "게시글 수정"이라는 행동
```

---

# 4. setter는 어디서 쓰면 되냐

## DTO에서는 OK

```java
public class BoardRequest {
    private String title;

    public void setTitle(String title) {
        this.title = title;
    }
}
```

이유:

```text
DTO = 데이터 전달용
비즈니스 규칙 없음
```

---

## 초기 생성 단계에서도 OK

```java
Board board = new Board();
board.setTitle("제목");
```

다만 실무에서는 생성자를 더 많이 쓴다.

---

# 5. new는 왜 쓰냐

new는 setter랑 반대 개념이 아니라 **역할이 다르다.**

```text
new
= 새로운 상태를 만든다

setter
= 기존 상태를 덮어쓴다
```

---

## 바로 setter 쓰는 경우

```java
board.setTitle(request.getTitle());
```

→ 기존 값 사라짐

---

## new로 분리하는 경우

```java
BoardUpdateData updateData = new BoardUpdateData(
    request.getTitle(),
    request.getContent()
);
```

구조:

```text
board = 기존 상태
updateData = 새 상태
```

이렇게 하면:

```text
비교 가능
로그 가능
검증 가능
```

---

# 6. 올바른 전체 흐름

```java
@Transactional
public void updateBoard(Long id, BoardRequest request) {

    // 1. 조회
    Board board = boardRepository.findById(id).orElseThrow();

    // 2. new로 새 상태 생성
    BoardUpdateData updateData = new BoardUpdateData(
        request.getTitle(),
        request.getContent()
    );

    // 3. 비교/로그
    log.info("oldTitle={}, newTitle={}",
            board.getTitle(),
            updateData.getTitle());

    // 4. 도메인에게 위임
    board.update(updateData);
}
```

도메인:

```java
public void update(BoardUpdateData data) {
    this.title = data.getTitle();
    this.content = data.getContent();
}
```

---

# 7. @Transactional까지 연결

```text
@Transactional
→ 트랜잭션 시작

엔티티 조회
→ 영속 상태

값 변경
→ JPA가 변경 감지

메서드 종료
→ commit → DB 반영
```

그래서:

```java
board.update(...)
```

만 해도 DB 반영된다.

---

# 8. 최종 정리 (핵심만)

```text
getter
= 어디서든 사용 가능

setter
= DTO에서는 OK
= 엔티티에서는 지양

new
= 변경될 값을 따로 만든다

엔티티 변경
= setter ❌
= update(), changeXxx() ⭕

Service
= 흐름만 담당

Domain(Entity)
= 상태 변경 책임

@Transactional
= 변경 감지 + DB 반영
```

---

# 9. 한 줄 결론

```text
값은 new로 분리하고,
변경은 도메인에게 맡기고,
setter는 함부로 열어두지 않는다
```

이 기준 하나 잡히면
JPA 설계, 서비스/도메인 분리, 트랜잭션 흐름까지 한 번에 정리된다.
