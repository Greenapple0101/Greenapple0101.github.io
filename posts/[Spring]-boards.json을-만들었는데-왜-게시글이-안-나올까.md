---
title: "[SPRING] boards.json을 만들었는데 왜 게시글이 안 나올까?"
source: "https://velog.io/@yorange50/SPRING-boards.json을-만들었는데-왜-게시글이-안-나올까"
published: "2026-04-30T01:42:50.869Z"
tags: ""
backup_date: "2026-05-29T14:52:52.781654"
---

게시판 CRUD API를 만들면서 처음에는 데이터를 메모리에 저장했다. `BoardService` 안에 `List<Board>`를 만들고, 게시글을 생성하면 그 리스트에 추가하는 방식이었다.

```java
private final List<Board> boards = new ArrayList<>();
private Long nextId = 1L;
```

이 방식은 구현이 단순해서 처음 CRUD 흐름을 이해하기에는 좋았다. 하지만 문제가 있었다. 서버를 껐다 켜면 데이터가 전부 사라진다.

그래서 DB를 붙이기 전 단계로 `boards.json` 파일에 게시글 데이터를 저장하는 방식으로 바꾸려고 했다.

---

## 1. 문제 상황

`boards.json` 파일을 만들고 게시글 데이터를 넣었다.

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

파일 위치도 `board_api` 프로젝트 안에 두었다.

```text
board/
  board_api/
    boards.json
    build.gradle
    src/
  board_fe/
```

그런데 프론트 화면에서는 계속 이렇게 나왔다.

```text
게시글이 없습니다.
```

처음에는 프론트 문제인가 싶었지만, 먼저 백엔드 API를 직접 확인했다.

```bash
curl http://localhost:8080/boards
```

결과는 다음과 같았다.

```json
[]
```

즉, 프론트 문제가 아니라 백엔드에서 게시글 데이터를 못 읽고 있는 상태였다.

---

## 2. 원인 1: JSON 파일만 만들면 자동으로 읽히는 게 아니다

처음에는 `boards.json` 파일을 만들면 Spring Boot가 알아서 읽어줄 것처럼 생각했다.

하지만 그렇지 않았다.

파일을 만들었다고 해서 자동으로 `List<Board>` 안에 들어가는 것은 아니다. 직접 파일을 읽어서 Java 객체로 바꾸는 코드가 필요하다.

즉, 흐름은 이렇게 되어야 한다.

```text
서버 시작
→ boards.json 파일 찾기
→ JSON 데이터를 List<Board>로 변환
→ boards 변수에 저장
→ GET /boards 요청 시 boards 반환
```

그래서 `BoardService`에 파일 읽기 로직을 추가했다.

```java
private void loadBoards() {
    try {
        if (file.exists()) {
            boards = mapper.readValue(file, new TypeReference<List<Board>>() {});

            nextId = boards.stream()
                    .map(Board::getId)
                    .filter(Objects::nonNull)
                    .mapToLong(Long::longValue)
                    .max()
                    .orElse(0L) + 1;
        }
    } catch (Exception e) {
        throw new RuntimeException("boards.json 읽기 실패", e);
    }
}
```

그리고 서버가 시작될 때 이 메서드가 실행되도록 생성자에서 호출했다.

```java
public BoardService() {
    loadBoards();
}
```

---

## 3. 원인 2: 실행 위치와 파일 위치가 중요하다

`BoardService`에서는 파일을 이렇게 찾도록 했다.

```java
private final File file = new File("boards.json");
```

여기서 `"boards.json"`은 프로젝트 전체에서 무조건 찾는다는 뜻이 아니다.

현재 서버가 실행되는 위치를 기준으로 `boards.json`을 찾는다.

그래서 백엔드는 반드시 `board_api` 폴더에서 실행해야 한다.

```bash
cd board_api
./gradlew bootRun
```

정상 구조는 다음과 같다.

```text
board_api/
  boards.json
  build.gradle
  gradlew
  src/
```

만약 다른 위치에서 실행하면 Java는 엉뚱한 곳에서 `boards.json`을 찾게 된다. 그래서 파일이 있어도 읽지 못할 수 있다.

확인을 위해 로그도 추가했다.

```java
System.out.println("현재 실행 경로: " + new File(".").getAbsolutePath());
System.out.println("boards.json 경로: " + file.getAbsolutePath());
System.out.println("boards.json 존재 여부: " + file.exists());
```

여기서 중요한 것은 이 값이다.

```text
boards.json 존재 여부: true
```

이게 `false`라면 파일 위치와 실행 위치가 맞지 않는 것이다.

---

## 4. 원인 3: VSCode 실행 버튼으로 Java 파일 하나만 실행했다

중간에 이런 오류가 나왔다.

```text
[Running] cd ".../service/" && javac BoardService.java && java BoardService

error: package com.board.api.domain does not exist
error: package org.springframework.stereotype does not exist
error: cannot find symbol
```

처음에는 코드가 잘못된 줄 알았다.

하지만 원인은 실행 방식이었다.

`BoardService.java`는 단독 실행 파일이 아니다. `main()`이 있는 파일도 아니고, Spring Boot 안에서 동작하는 서비스 클래스다.

즉, 이런 식으로 실행하면 안 된다.

```bash
javac BoardService.java
java BoardService
```

이 방식은 Java 파일 하나만 실행하는 것이기 때문에 Spring, Gradle, 외부 라이브러리, 다른 패키지 클래스를 제대로 불러오지 못한다.

Spring Boot 프로젝트는 반드시 Gradle로 실행해야 한다.

```bash
./gradlew bootRun
```

정리하면 다음과 같다.

```text
VSCode 실행 버튼
→ Java 파일 하나만 단독 실행
→ Spring 의존성 못 찾음
→ 에러 발생
```

```text
./gradlew bootRun
→ Spring Boot 프로젝트 전체 실행
→ build.gradle 의존성 반영
→ @Service, @RestController, ObjectMapper 사용 가능
```

---

## 5. 원인 4: Spring Boot 4와 Jackson import 문제

Gradle로 제대로 실행했는데도 다음 오류가 발생했다.

```text
package com.fasterxml.jackson.core.type does not exist
package com.fasterxml.jackson.databind does not exist
```

처음에는 `build.gradle`에 `spring-boot-starter-web`이 없는 줄 알았다.

하지만 `build.gradle`에는 이미 있었다.

```gradle
implementation 'org.springframework.boot:spring-boot-starter-web'
```

문제는 Spring Boot 버전이었다.

```gradle
id 'org.springframework.boot' version '4.0.6'
```

Spring Boot 4에서는 Jackson 버전이 달라지면서 기존 예제에서 많이 쓰던 import가 바로 안 맞을 수 있었다.

기존 코드에서는 이렇게 import하고 있었다.

```java
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
```

하지만 현재 프로젝트에서는 이 패키지를 못 찾았다.

해결 방법은 두 가지였다.

첫 번째는 Spring Boot 4 방식에 맞게 import를 바꾸는 것이다.

```java
import tools.jackson.core.type.TypeReference;
import tools.jackson.databind.ObjectMapper;
```

두 번째는 Spring Boot 버전을 3.x로 낮추는 것이다.

나는 학습과 발표 목적이라 자료가 많은 Spring Boot 3 방식이 더 안정적이라고 판단했다.

```gradle
id 'org.springframework.boot' version '3.4.5'
```

Spring Boot 3을 쓰면 기존 예제처럼 아래 import를 그대로 사용할 수 있다.

```java
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
```

---

## 6. 최종 BoardService 코드

최종적으로 `BoardService`는 다음과 같은 역할을 하게 되었다.

```text
1. 서버 시작 시 boards.json 읽기
2. GET 요청 시 메모리에 올라온 boards 반환
3. POST 요청 시 boards에 추가 후 파일 저장
4. PUT 요청 시 수정 후 파일 저장
5. DELETE 요청 시 삭제 후 파일 저장
```

```java
package com.board.api.service;

import com.board.api.domain.Board;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;

import java.io.File;
import java.time.LocalDateTime;
import java.util.*;

@Service
public class BoardService {

    private final ObjectMapper mapper = new ObjectMapper();
    private final File file = new File("boards.json");

    private List<Board> boards = new ArrayList<>();
    private Long nextId = 1L;

    public BoardService() {
        loadBoards();
    }

    private void loadBoards() {
        try {
            System.out.println("현재 실행 경로: " + new File(".").getAbsolutePath());
            System.out.println("boards.json 경로: " + file.getAbsolutePath());
            System.out.println("boards.json 존재 여부: " + file.exists());

            if (file.exists()) {
                boards = mapper.readValue(file, new TypeReference<List<Board>>() {});

                nextId = boards.stream()
                        .map(Board::getId)
                        .filter(Objects::nonNull)
                        .mapToLong(Long::longValue)
                        .max()
                        .orElse(0L) + 1;
            }
        } catch (Exception e) {
            throw new RuntimeException("boards.json 읽기 실패", e);
        }
    }

    private void saveBoards() {
        try {
            mapper.writerWithDefaultPrettyPrinter().writeValue(file, boards);
        } catch (Exception e) {
            throw new RuntimeException("boards.json 저장 실패", e);
        }
    }

    public List<Board> getBoards() {
        return boards;
    }

    public Board getBoard(Long id) {
        for (Board board : boards) {
            if (board.getId().equals(id)) {
                return board;
            }
        }
        throw new RuntimeException("해당 게시글 없음");
    }

    public Board createBoard(Board board) {
        String now = LocalDateTime.now().toString();

        board.setId(nextId++);
        board.setCreatedAt(now);
        board.setUpdatedAt(now);

        boards.add(board);
        saveBoards();

        return board;
    }

    public Board updateBoard(Long id, Board newBoard) {
        for (Board board : boards) {
            if (board.getId().equals(id)) {
                board.setTitle(newBoard.getTitle());
                board.setContent(newBoard.getContent());
                board.setAuthor(newBoard.getAuthor());
                board.setUpdatedAt(LocalDateTime.now().toString());

                saveBoards();

                return board;
            }
        }

        throw new RuntimeException("해당 게시글 없음");
    }

    public void deleteBoard(Long id) {
        boards.removeIf(board -> board.getId().equals(id));
        saveBoards();
    }
}
```

---

## 7. Board 클래스에서 주의할 점

JSON 데이터를 `Board` 객체로 바꾸려면 `Board` 클래스에 기본 생성자가 필요하다.

```java
public Board() {
}
```

Jackson은 JSON을 객체로 만들 때 먼저 빈 객체를 만들고, setter를 통해 값을 넣는다.

그래서 `Board.java`에는 기본 생성자와 getter/setter가 있어야 한다.

```java
public class Board {

    private Long id;
    private String title;
    private String content;
    private String author;
    private String createdAt;
    private String updatedAt;

    public Board() {
    }

    // getter, setter
}
```

---

## 8. 최종 확인 방법

백엔드 실행:

```bash
cd board_api
./gradlew bootRun
```

API 직접 확인:

```bash
curl http://localhost:8080/boards
```

정상이라면 `boards.json`에 들어 있던 데이터가 나온다.

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

이 상태에서 프론트 화면에도 게시글이 보여야 한다.

---

## 9. 이번 트러블슈팅에서 배운 점

이번 문제는 단순히 `boards.json` 경로 하나의 문제가 아니었다.

여러 문제가 겹쳐 있었다.

```text
1. JSON 파일을 만들었지만 읽는 코드가 없었다.
2. 실행 위치에 따라 boards.json을 찾는 경로가 달라졌다.
3. VSCode 실행 버튼으로 Java 파일 하나만 실행해서 Spring 의존성을 못 찾았다.
4. Spring Boot 4와 Jackson import 방식 차이 때문에 ObjectMapper를 못 찾았다.
5. Board 객체에는 JSON 변환을 위한 기본 생성자가 필요했다.
```

처음에는 프론트 화면에 “게시글이 없습니다”라고 떠서 프론트 문제처럼 보였다.
하지만 `curl http://localhost:8080/boards`로 백엔드 응답을 직접 확인하니 원인이 백엔드 쪽이라는 것을 알 수 있었다.

앞으로는 화면에서 문제가 보이면 바로 프론트부터 의심하기보다, API 응답을 먼저 확인해야겠다.

```bash
curl http://localhost:8080/boards
```

이 한 줄이 프론트 문제인지, 백엔드 문제인지 나누는 기준이 된다.
![](https://velog.velcdn.com/images/yorange50/post/16131d37-64c4-4681-95a1-820be892a8e5/image.png)
