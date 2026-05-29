---
title: "[Spring] board_api 정리부터 board_fe Thymeleaf 화면 서버 구성까지"
source: "https://velog.io/@yorange50/Spring-boardapi-정리부터-boardfe-Thymeleaf-화면-서버-구성까지"
published: "2026-05-06T04:26:41.047Z"
tags: ""
backup_date: "2026-05-29T14:52:52.776010"
---

이번 작업의 목표는 단순히 게시판 CRUD를 만드는 것이 아니었다.
기존에 하나의 Spring Boot 프로젝트 안에서 화면과 API가 섞여 있던 구조를 정리하고, 역할을 분리하는 것이 핵심이었다.

최종 목표는 다음과 같았다.

```text
board_api
→ REST API 서버
→ JPA
→ PostgreSQL
→ JSON 응답

board_fe
→ Spring Boot 화면 서버
→ Thymeleaf
→ RestClient
→ board_api 호출
```

즉 브라우저가 직접 `board_api`를 보는 것이 아니라,
사용자는 `board_fe`에 접속하고 `board_fe`가 내부적으로 `board_api`를 호출하는 구조다.

```text
Browser
→ board_fe
→ RestClient
→ board_api
→ JPA
→ PostgreSQL
```

---

## 1. 기존 구조의 문제

처음에는 `board_api` 안에 API용 컨트롤러와 화면용 컨트롤러가 같이 있었다.

예를 들면 이런 파일들이 있었다.

```text
controller
├── BoardController.java
├── BoardPageController.java
└── HomeController.java
```

여기서 `BoardController`는 REST API 역할을 하고,
`BoardPageController`, `HomeController`는 Thymeleaf 화면을 반환하는 역할이었다.

처음에는 작은 프로젝트라 이렇게 해도 동작은 한다.

하지만 이번 목표는 `board_api`와 `board_fe`를 나누는 것이었기 때문에,
`board_api` 안에 화면 관련 코드가 남아 있으면 역할이 애매해진다.

그래서 기준을 다시 잡았다.

```text
board_api는 JSON만 반환한다.
board_fe는 HTML 화면만 담당한다.
```

---

## 2. board_api에서 화면 코드 제거

먼저 `board_api`를 REST API 서버로 정리했다.

삭제하거나 이동해야 하는 파일은 다음과 같았다.

```text
BoardPageController.java
HomeController.java
templates 폴더
static 폴더
boards.json
```

`BoardPageController.java`와 `HomeController.java`는 보통 이런 형태의 코드였다.

```java
@Controller
public class HomeController {

    @GetMapping("/")
    public String home() {
        return "home";
    }
}
```

또는:

```java
@Controller
public class BoardPageController {

    @GetMapping("/boards-page")
    public String boardsPage(Model model) {
        return "boards";
    }
}
```

이런 코드는 HTML 파일 이름을 반환한다.

```java
return "home";
return "boards/list";
```

즉 API 서버의 역할이 아니라 화면 서버의 역할이다.

그래서 `board_api`에서는 제거하고,
화면 관련 코드는 `board_fe`에서 다시 구성하기로 했다.

---

## 3. board_api 최종 구조

정리 후 `board_api`는 다음 구조로 가져갔다.

```text
board_api
└── src
    └── main
        ├── java
        │   └── com
        │       └── board
        │           └── api
        │               ├── BoardApiApplication.java
        │               ├── controller
        │               │   └── BoardController.java
        │               ├── domain
        │               │   └── Board.java
        │               ├── repository
        │               │   └── BoardRepository.java
        │               └── service
        │                   └── BoardService.java
        │
        └── resources
            └── application.properties
```

각 파일의 역할은 다음과 같다.

```text
BoardApiApplication.java
→ Spring Boot 실행 클래스

BoardController.java
→ REST API 요청 처리

Board.java
→ JPA Entity

BoardRepository.java
→ PostgreSQL 접근

BoardService.java
→ 게시글 비즈니스 로직

application.properties
→ DB 연결 설정
```

---

## 4. board_api는 @RestController만 남긴다

`board_api`의 컨트롤러는 `@Controller`가 아니라 `@RestController` 중심으로 정리했다.

```java
@RestController
@RequestMapping("/boards")
public class BoardController {

    private final BoardService boardService;

    public BoardController(BoardService boardService) {
        this.boardService = boardService;
    }

    @GetMapping
    public List<Board> getBoards() {
        return boardService.getBoards();
    }

    @GetMapping("/{id}")
    public Board getBoard(@PathVariable Long id) {
        return boardService.getBoard(id);
    }

    @PostMapping
    public Board createBoard(@RequestBody Board board) {
        return boardService.createBoard(board);
    }

    @PutMapping("/{id}")
    public Board updateBoard(@PathVariable Long id, @RequestBody Board board) {
        return boardService.updateBoard(id, board);
    }

    @DeleteMapping("/{id}")
    public void deleteBoard(@PathVariable Long id) {
        boardService.deleteBoard(id);
    }
}
```

이제 `board_api`는 화면을 반환하지 않는다.

브라우저에서 다음 주소에 접근하면:

```text
http://localhost:8080/boards
```

HTML 화면이 아니라 JSON 데이터가 나와야 한다.

```json
[
  {
    "id": 1,
    "title": "첫 게시글",
    "content": "내용",
    "author": "작성자"
  }
]
```

데이터가 없으면 다음처럼 나올 수 있다.

```json
[]
```

이것도 정상이다.
API 서버가 정상적으로 JSON 응답을 주고 있다는 뜻이다.

---

## 5. board_api와 PostgreSQL 연결

`board_api`는 JPA를 통해 PostgreSQL과 연결되도록 구성했다.

`pom.xml`에는 JPA와 PostgreSQL 의존성을 추가했다.

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>

<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <scope>runtime</scope>
</dependency>
```

`application.properties`에는 DB 연결 정보를 설정했다.

```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/boarddb
spring.datasource.username=board
spring.datasource.password=board1234

spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
```

PostgreSQL은 Docker로 로컬에 띄웠다.

```powershell
docker run --name board-postgres -e POSTGRES_USER=board -e POSTGRES_PASSWORD=board1234 -e POSTGRES_DB=boarddb -p 5432:5432 -d postgres:16
```

즉 현재 로컬 구조는 다음과 같다.

```text
board_api
→ JPA
→ localhost:5432
→ Docker PostgreSQL
```

---

## 6. Board 엔티티 정리

JPA를 적용하면서 `Board`는 엔티티로 정리했다.

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

여기서 의식한 부분은 setter를 무분별하게 열어두지 않는 것이었다.

기존 방식은 다음과 같았다.

```java
board.setTitle(request.getTitle());
board.setContent(request.getContent());
```

하지만 이렇게 되면 객체 상태가 어디서든 쉽게 바뀔 수 있다.

그래서 수정은 `update()` 메서드로 제한했다.

```java
board.update(
        request.getTitle(),
        request.getContent(),
        request.getAuthor()
);
```

즉 단순히 필드를 바꾸는 것이 아니라,
“게시글을 수정한다”는 의미를 가진 메서드로 변경을 처리했다.

---

## 7. BoardRepository 추가

JPA를 사용하기 위해 Repository를 만들었다.

```java
package com.board.api.repository;

import com.board.api.domain.Board;
import org.springframework.data.jpa.repository.JpaRepository;

public interface BoardRepository extends JpaRepository<Board, Long> {
}
```

`JpaRepository<Board, Long>`의 의미는 다음과 같다.

```text
Board 엔티티를 대상으로 한다.
Board의 id 타입은 Long이다.
```

이렇게만 작성해도 기본 CRUD 메서드를 사용할 수 있다.

```text
findAll()
findById()
save()
deleteById()
```

---

## 8. BoardService를 JPA 기반으로 변경

기존에는 Service에서 직접 List나 JSON 파일을 다루었다.

변경 후에는 Repository를 통해 DB에 접근하도록 바꿨다.

```java
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

이제 데이터 흐름은 다음처럼 정리된다.

```text
Controller
→ Service
→ Repository
→ PostgreSQL
```

---

## 9. board_fe 생성 목적

`board_api` 정리가 끝난 뒤에는 `board_fe`를 만들었다.

`board_fe`의 목적은 화면을 담당하는 것이다.

중요한 기준은 다음과 같다.

```text
board_fe는 DB에 직접 접근하지 않는다.
board_fe는 board_api를 RestClient로 호출한다.
board_fe는 Thymeleaf로 HTML을 렌더링한다.
```

즉 `board_fe`는 데이터베이스를 모른다.
DB 접근은 오직 `board_api`만 담당한다.

```text
Browser
→ board_fe
→ RestClient
→ board_api
→ PostgreSQL
```

---

## 10. board_fe 최종 구조

`board_fe`는 다음 구조로 정리했다.

```text
board_fe
└── src
    └── main
        ├── java
        │   └── com
        │       └── board
        │           └── fe
        │               ├── BoardFeApplication.java
        │               ├── config
        │               │   └── RestClientConfig.java
        │               ├── client
        │               │   └── BoardApiClient.java
        │               ├── controller
        │               │   └── BoardPageController.java
        │               └── dto
        │                   ├── BoardResponse.java
        │                   ├── BoardCreateRequest.java
        │                   └── BoardUpdateRequest.java
        │
        └── resources
            ├── application.properties
            └── templates
                └── boards
                    ├── list.html
                    ├── detail.html
                    ├── write.html
                    └── edit.html
```

각 역할은 다음과 같다.

```text
config
→ RestClient 설정

client
→ board_api 호출 담당

controller
→ 화면 요청 처리

dto
→ API와 주고받는 데이터 형식

templates
→ Thymeleaf HTML 화면
```

---

## 11. board_fe 포트 분리

`board_api`는 8080 포트를 사용하고,
`board_fe`는 8081 포트를 사용하도록 설정했다.

`board_fe/src/main/resources/application.properties`

```properties
server.port=8081

board.api.base-url=http://localhost:8080
```

이제 접속 주소는 다음처럼 나뉜다.

```text
board_api
→ http://localhost:8080/boards
→ JSON 응답

board_fe
→ http://localhost:8081/boards
→ HTML 화면
```

---

## 12. RestClient 설정

`board_fe`에서 `board_api`를 호출하기 위해 `RestClient`를 설정했다.

```java
@Configuration
public class RestClientConfig {

    @Bean
    public RestClient restClient(@Value("${board.api.base-url}") String baseUrl) {
        return RestClient.builder()
                .baseUrl(baseUrl)
                .build();
    }
}
```

여기서 `board.api.base-url`은 `application.properties`에 정의한 값이다.

```properties
board.api.base-url=http://localhost:8080
```

즉 `board_fe`는 이 주소를 기준으로 `board_api`를 호출한다.

---

## 13. BoardApiClient 만들기

컨트롤러에서 직접 RestClient를 호출하지 않고,
API 호출 전담 클래스를 따로 만들었다.

```java
@Component
public class BoardApiClient {

    private final RestClient restClient;

    public BoardApiClient(RestClient restClient) {
        this.restClient = restClient;
    }

    public List<BoardResponse> getBoards() {
        return restClient.get()
                .uri("/boards")
                .retrieve()
                .body(new ParameterizedTypeReference<List<BoardResponse>>() {});
    }

    public BoardResponse getBoard(Long id) {
        return restClient.get()
                .uri("/boards/{id}", id)
                .retrieve()
                .body(BoardResponse.class);
    }

    public void createBoard(BoardCreateRequest request) {
        restClient.post()
                .uri("/boards")
                .body(request)
                .retrieve()
                .toBodilessEntity();
    }

    public void updateBoard(Long id, BoardUpdateRequest request) {
        restClient.put()
                .uri("/boards/{id}", id)
                .body(request)
                .retrieve()
                .toBodilessEntity();
    }

    public void deleteBoard(Long id) {
        restClient.delete()
                .uri("/boards/{id}", id)
                .retrieve()
                .toBodilessEntity();
    }
}
```

이렇게 분리하면 컨트롤러가 깔끔해진다.

```text
Controller
→ 화면 흐름 담당

BoardApiClient
→ API 통신 담당
```

---

## 14. BoardPageController 만들기

`board_fe`의 컨트롤러는 화면을 반환한다.

```java
@Controller
@RequestMapping("/boards")
public class BoardPageController {

    private final BoardApiClient boardApiClient;

    public BoardPageController(BoardApiClient boardApiClient) {
        this.boardApiClient = boardApiClient;
    }

    @GetMapping
    public String list(Model model) {
        List<BoardResponse> boards = boardApiClient.getBoards();
        model.addAttribute("boards", boards);
        return "boards/list";
    }

    @GetMapping("/{id}")
    public String detail(@PathVariable Long id, Model model) {
        BoardResponse board = boardApiClient.getBoard(id);
        model.addAttribute("board", board);
        return "boards/detail";
    }

    @GetMapping("/write")
    public String writeForm() {
        return "boards/write";
    }

    @PostMapping
    public String create(
            @RequestParam String title,
            @RequestParam String content,
            @RequestParam String author
    ) {
        BoardCreateRequest request = new BoardCreateRequest(title, content, author);
        boardApiClient.createBoard(request);
        return "redirect:/boards";
    }

    @GetMapping("/{id}/edit")
    public String editForm(@PathVariable Long id, Model model) {
        BoardResponse board = boardApiClient.getBoard(id);
        model.addAttribute("board", board);
        return "boards/edit";
    }

    @PostMapping("/{id}/edit")
    public String update(
            @PathVariable Long id,
            @RequestParam String title,
            @RequestParam String content,
            @RequestParam String author
    ) {
        BoardUpdateRequest request = new BoardUpdateRequest(title, content, author);
        boardApiClient.updateBoard(id, request);
        return "redirect:/boards/" + id;
    }

    @PostMapping("/{id}/delete")
    public String delete(@PathVariable Long id) {
        boardApiClient.deleteBoard(id);
        return "redirect:/boards";
    }
}
```

`board_fe`의 컨트롤러는 HTML 파일 이름을 반환한다.

```java
return "boards/list";
return "boards/detail";
return "boards/write";
return "boards/edit";
```

그래서 실제 파일 위치는 다음과 같아야 한다.

```text
templates/boards/list.html
templates/boards/detail.html
templates/boards/write.html
templates/boards/edit.html
```

---

## 15. Thymeleaf 템플릿 구성

화면은 최소 CRUD 기준으로 네 개를 만들었다.

```text
list.html
→ 게시글 목록

detail.html
→ 게시글 상세

write.html
→ 게시글 작성

edit.html
→ 게시글 수정
```

예를 들어 목록 화면은 다음과 같은 방식으로 작성했다.

```html
<tr th:each="board : ${boards}">
    <td th:text="${board.id}">1</td>
    <td th:text="${board.title}">제목</td>
    <td th:text="${board.author}">작성자</td>
    <td>
        <a th:href="@{/boards/{id}(id=${board.id})}">상세보기</a>
    </td>
</tr>
```

여기서 `boards`는 컨트롤러에서 Model에 담은 값이다.

```java
model.addAttribute("boards", boards);
```

즉 흐름은 다음과 같다.

```text
board_fe Controller
→ BoardApiClient로 board_api 호출
→ 응답 데이터를 Model에 담음
→ Thymeleaf가 HTML로 렌더링
```

---

## 16. 실행 순서

실행 순서도 중요했다.

먼저 PostgreSQL 컨테이너가 떠 있어야 한다.

```powershell
docker ps
```

그다음 `board_api`를 실행한다.

```powershell
cd C:\Users\oscbs\OneDrive\Desktop\board\board_api
mvn spring-boot:run
```

`board_api`가 정상 실행되면 다음 주소에서 JSON 응답을 확인한다.

```text
http://localhost:8080/boards
```

그다음 `board_fe`를 실행한다.

```powershell
cd C:\Users\oscbs\OneDrive\Desktop\board\board_fe
mvn spring-boot:run
```

브라우저에서 다음 주소로 접속한다.

```text
http://localhost:8081/boards
```

이때 게시판 HTML 화면이 보이면 성공이다.

---

## 17. 이번 작업에서 배운 점

이번 작업의 핵심은 단순히 Thymeleaf 화면을 붙이는 것이 아니었다.

더 중요한 것은 서버의 역할을 분리하는 것이었다.

기존에는 하나의 프로젝트에서 화면도 처리하고 API도 처리했다.

```text
Spring Boot 하나
→ Controller
→ Service
→ 데이터
→ HTML 또는 JSON
```

하지만 이번에는 다음처럼 나누었다.

```text
board_api
→ 데이터와 API 담당

board_fe
→ 화면과 사용자 요청 흐름 담당
```

이 구조로 나누면 각각의 책임이 명확해진다.

```text
DB 연결 문제
→ board_api에서 확인

화면 렌더링 문제
→ board_fe에서 확인

API 통신 문제
→ board_fe의 RestClient 또는 board_api endpoint 확인
```

---

## 18. 최종 정리

이번 작업은 기존 게시판 프로젝트를 다음 단계로 발전시키는 과정이었다.

```text
1. board_api에서 화면 관련 파일 제거
2. board_api를 REST API 서버로 정리
3. PostgreSQL Docker 컨테이너와 JPA 연결
4. Board 엔티티, Repository, Service 구조 정리
5. board_fe를 별도 Spring Boot 프로젝트로 구성
6. board_fe에 Thymeleaf 템플릿 추가
7. board_fe에서 RestClient로 board_api 호출
8. 브라우저에서는 board_fe에 접속해서 HTML 화면 확인
```

최종 구조는 다음과 같다.

```text
Browser
→ board_fe(Spring Boot + Thymeleaf)
→ RestClient
→ board_api(Spring Boot REST API + JPA)
→ PostgreSQL(Docker)
```

한 줄로 정리하면 이렇다.

```text
기존에 섞여 있던 게시판 프로젝트를 API 서버와 화면 서버로 분리하고, DB 접근은 board_api에만 두고 board_fe는 RestClient로 데이터를 받아 Thymeleaf 화면을 렌더링하도록 정리했다.
```
