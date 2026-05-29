---
title: "[SPRING] PUT과 DELETE — 게시글 수정과 삭제"
source: "https://velog.io/@yorange50/SPRING-PUT과-DELETE-게시글-수정과-삭제"
published: "2026-04-29T13:25:31.537Z"
tags: ""
backup_date: "2026-05-29T14:52:52.785864"
---

게시판 API를 만들면서 GET, POST까지는 자연스럽게 이해가 됐는데
그 다음 단계에서 등장하는 게 바로 **PUT과 DELETE**다.

이번 글에서는
"게시글 수정"과 "게시글 삭제"를 기준으로
PUT과 DELETE가 실제로 어떻게 쓰이는지 정리해봤다.

---

## PUT — 게시글 수정

PUT은 **기존 데이터를 수정할 때 사용하는 HTTP 메서드**다.

예를 들어,
이미 존재하는 게시글의 제목을 바꾸고 싶다면 PUT을 사용한다.

### 요청 구조

* URL: `/boards/{id}`
* Method: `PUT`
* Body: 수정할 데이터(JSON)

### 코드

```java
@PutMapping("/boards/{id}")
public Board updateBoard(@PathVariable Long id,
                         @RequestBody Map<String, String> body){
    String title = body.get("title");
    return boardService.updateBoard(id, title);
}
```

### 흐름

1. 클라이언트가 `/boards/1` 같은 URL로 요청을 보냄
2. `@PathVariable`로 id를 가져옴
3. `@RequestBody`로 수정할 데이터(title)를 받음
4. 서비스에서 해당 id의 게시글을 찾아 수정

### 핵심 포인트

* PUT은 **"이미 존재하는 데이터"를 수정**
* URL에 **id를 포함**해서 어떤 데이터를 수정할지 명확하게 지정
* 요청 body에 **변경할 값 포함**

---

## DELETE — 게시글 삭제

DELETE는 말 그대로 **데이터를 삭제할 때 사용하는 HTTP 메서드**다.

### 요청 구조

* URL: `/boards/{id}`
* Method: `DELETE`

### 코드

```java
@DeleteMapping("/boards/{id}")
public String deleteBoard(@PathVariable Long id){
    boardService.deleteBoard(id);
    return "삭제됨: " + id;
}
```

### 흐름

1. `/boards/1`로 DELETE 요청
2. `@PathVariable`로 id 추출
3. 해당 id의 게시글 삭제

### 핵심 포인트

* DELETE는 **데이터 제거**
* 보통 body 없이 **id만으로 처리**
* 성공 시 간단한 메시지나 상태 코드 반환

---

## PUT vs DELETE 한눈에 비교

| 구분   | PUT          | DELETE       |
| ---- | ------------ | ------------ |
| 목적   | 데이터 수정       | 데이터 삭제       |
| 대상   | 이미 존재하는 데이터  | 이미 존재하는 데이터  |
| URL  | /boards/{id} | /boards/{id} |
| Body | 있음 (수정값)     | 없음 (보통)      |

---

## 실제로 해보면서 느낀 점

GET, POST는 단순히 가져오고 만드는 느낌이었다면
PUT과 DELETE는 "데이터를 관리한다"는 느낌이 강했다.

특히 id를 기준으로
**정확히 어떤 데이터를 건드리는지 명확하게 지정하는 게 핵심**이었다.

---

## 마무리

CRUD에서

* GET → 조회
* POST → 생성
* PUT → 수정
* DELETE → 삭제

이렇게 흐름이 완성된다.

이제 단순히 API를 만든 게 아니라
**데이터를 다루는 기본 구조를 이해한 단계**라고 보면 될 것 같다.
