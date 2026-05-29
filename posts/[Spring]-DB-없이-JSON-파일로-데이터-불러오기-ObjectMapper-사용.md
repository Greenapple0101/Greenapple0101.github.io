---
title: "[SPRING] DB 없이 JSON 파일로 데이터 불러오기 (ObjectMapper 사용)"
source: "https://velog.io/@yorange50/SPRING-DB-없이-JSON-파일로-데이터-불러오기-ObjectMapper-사용"
published: "2026-04-29T14:58:57.566Z"
tags: ""
backup_date: "2026-05-29T14:52:52.785349"
---

DB를 붙이기 전에 CRUD 흐름을 빠르게 만들고 싶다면
Spring에서 JSON 파일을 “임시 DB처럼” 사용하는 방법이 있다.

이번 글에서는 **boards.json 파일을 읽어서 List로 변환하는 과정**을 정리한다.

---

## 1. JSON 파일 준비

먼저 resources 폴더에 JSON 파일을 만든다.

```text
src/main/resources/boards.json
```

예시 데이터:

```json
[
  {
    "id": 1,
    "title": "첫 번째 게시글",
    "content": "내용입니다",
    "author": "관리자",
    "createdAt": "2026-04-29T00:00:00",
    "updatedAt": "2026-04-29T00:00:00"
  }
]
```

---

## 2. Board 클래스 정의

JSON을 Java 객체로 변환하려면 구조가 같아야 한다.

```java
public class Board {

    private Long id;
    private String title;
    private String content;
    private String author;
    private String createdAt;
    private String updatedAt;

    // getter, setter 필요
}
```

---

## 3. ObjectMapper로 JSON 읽기

Spring에서는 Jackson의 `ObjectMapper`를 사용해서 JSON을 읽는다.

```java
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.util.List;

public List<Board> getBoards() throws Exception {
    ObjectMapper mapper = new ObjectMapper();

    File file = new File("src/main/resources/boards.json");

    List<Board> boards = mapper.readValue(
        file,
        new TypeReference<List<Board>>() {}
    );

    return boards;
}
```

---

## 4. 동작 흐름

```text
boards.json → ObjectMapper → List<Board>
```

* JSON 파일을 읽는다
* Board 객체 리스트로 변환한다
* 컨트롤러에서 그대로 반환한다

---

## 5. Controller에서 사용

```java
@GetMapping("/boards")
public List<Board> getBoards() throws Exception {
    return boardService.getBoards();
}
```

---

## 6. 자주 터지는 에러

### 1) 파일 경로 오류

```text
src/main/resources/boards.json
```

실행 위치 기준으로 경로가 다르면 못 읽는다.

---

### 2) 필드명 불일치

JSON:

```json
"title"
```

Java:

```java
private String name;
```

→ 매핑 안 됨

---

### 3) getter/setter 없음

Jackson은 getter/setter 기반으로 동작한다.

---

## 7. 중요한 한계

이 방식은 연습용이다.

* 동시 요청 시 파일 충돌 가능
* 성능 낮음
* 트랜잭션 없음

그래서 실무에서는 DB를 사용한다.

---

## 8. 정리

```text
JSON 파일 생성 → ObjectMapper로 읽기 → List<Board 변환
```

이 흐름만 이해하면
DB 없이도 Spring에서 CRUD 구조를 만들 수 있다.
