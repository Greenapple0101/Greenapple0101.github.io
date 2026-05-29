---
title: "[Spring] 프론트도 백엔드처럼 Controller-Service 구조로 맞춰야 하는 이유"
source: "https://velog.io/@yorange50/Spring-프론트도-백엔드처럼-Controller-Service-구조로-맞춰야-하는-이유"
published: "2026-05-07T09:01:05.924Z"
tags: ""
backup_date: "2026-05-29T14:52:52.769403"
---

이번에 지적받은 핵심은 단순히 “코드 스타일이 별로다”가 아니었다. 구조 자체가 백엔드와 맞지 않았다는 점이었다.

처음에는 `board_fe`를 단순히 화면을 띄우는 프로젝트처럼 생각했다. 그래서 Controller에서 바로 API Client를 호출하고, 폼 데이터도 `@RequestParam`으로 하나씩 받아서 넘겼다.

그런데 이 방식은 프로젝트가 커질수록 유지보수가 어려워진다.

핵심은 이거다.

```text
프론트 서버도 Spring Boot 애플리케이션이면
백엔드처럼 Controller - Service - Domain/DTO 구조를 맞추는 게 좋다.
```

---

# 1. 기존 구조의 문제

기존 코드는 대략 이런 흐름이었다.

```java
@PostMapping("/boards")
public String create(@RequestParam String title,
                     @RequestParam String author,
                     @RequestParam String content) {
    boardApiClient.create(title, author, content);
    return "redirect:/boards";
}
```

겉으로 보면 동작은 한다.

하지만 문제가 있다.

```text
Controller가 직접 boardApiClient를 호출함
요청 데이터를 개별 파라미터로 받음
Service 계층이 없음
객체로 데이터를 묶지 않음
```

즉, Controller가 너무 많은 일을 하고 있다.

Controller는 원래 이런 역할에 집중해야 한다.

```text
요청 받기
Model에 데이터 담기
HTML 뷰 이름 반환하기
redirect 처리하기
```

그런데 기존 구조에서는 Controller가 API 호출까지 직접 처리하고 있었다.

```text
Controller
→ boardApiClient 직접 호출
→ 외부 API 요청
```

이렇게 되면 Controller가 화면 처리와 통신 로직을 동시에 가지게 된다.

---

# 2. 프론트 서버에도 Service가 필요하다

Spring Boot로 만든 프론트 서버라면, 프론트라고 해서 구조를 대충 가져가면 안 된다.

백엔드가 이렇게 되어 있다면,

```text
Controller
→ Service
→ Repository
→ DB
```

프론트 서버는 이렇게 가는 게 자연스럽다.

```text
Controller
→ Service
→ ApiClient
→ board_api
```

즉, `Repository` 대신 외부 백엔드 API를 호출하는 `ApiClient`가 들어간다고 보면 된다.

프론트 서버에서는 DB에 직접 접근하지 않는다.
대신 `board_api` 서버에 REST 요청을 보낸다.

그래서 구조는 이렇게 맞추는 게 좋다.

```text
board_fe
 ├── controller
 │    └── BoardPageController.java
 │
 ├── service
 │    └── BoardService.java
 │
 ├── client
 │    └── BoardApiClient.java
 │
 ├── dto
 │    ├── BoardCreateRequest.java
 │    ├── BoardUpdateRequest.java
 │    └── BoardResponse.java
 │
 └── templates
      ├── index.html
      ├── list.html
      ├── detail.html
      ├── write.html
      └── edit.html
```

이렇게 두면 역할이 명확해진다.

---

# 3. Controller가 Client를 바로 호출하면 안 좋은 이유

기존 구조는 이런 느낌이다.

```text
Controller
→ BoardApiClient
→ board_api
```

하지만 더 좋은 구조는 이거다.

```text
Controller
→ BoardService
→ BoardApiClient
→ board_api
```

왜 굳이 Service를 하나 더 두냐면, Controller는 화면 흐름에 집중해야 하기 때문이다.

예를 들어 게시글 등록을 한다고 해보자.

Controller는 이런 것만 담당하면 된다.

```text
폼 요청 받기
Service에 등록 요청하기
등록 후 목록 페이지로 redirect
```

실제 API 호출은 Service 아래에서 처리한다.

---

# 4. 개선된 Controller 예시

기존에는 Controller에서 바로 Client를 호출했다.

```java
@PostMapping("/boards")
public String create(@RequestParam String title,
                     @RequestParam String author,
                     @RequestParam String content) {
    boardApiClient.create(title, author, content);
    return "redirect:/boards";
}
```

개선하면 이렇게 된다.

```java
@Controller
public class BoardPageController {

    private final BoardService boardService;

    public BoardPageController(BoardService boardService) {
        this.boardService = boardService;
    }

    @GetMapping("/")
    public String index() {
        return "index";
    }

    @GetMapping("/boards")
    public String list(Model model) {
        model.addAttribute("boards", boardService.findAll());
        return "list";
    }

    @GetMapping("/boards/write")
    public String writeForm(Model model) {
        model.addAttribute("boardCreateRequest", new BoardCreateRequest());
        return "write";
    }

    @PostMapping("/boards")
    public String create(@ModelAttribute BoardCreateRequest request) {
        boardService.create(request);
        return "redirect:/boards";
    }

    @GetMapping("/boards/{id}")
    public String detail(@PathVariable Long id, Model model) {
        model.addAttribute("board", boardService.findById(id));
        return "detail";
    }

    @GetMapping("/boards/{id}/edit")
    public String editForm(@PathVariable Long id, Model model) {
        model.addAttribute("board", boardService.findById(id));
        return "edit";
    }

    @PostMapping("/boards/{id}/edit")
    public String update(@PathVariable Long id,
                         @ModelAttribute BoardUpdateRequest request) {
        boardService.update(id, request);
        return "redirect:/boards/" + id;
    }

    @PostMapping("/boards/{id}/delete")
    public String delete(@PathVariable Long id) {
        boardService.delete(id);
        return "redirect:/boards";
    }
}
```

이제 Controller는 `BoardApiClient`를 모른다.

Controller는 오직 `BoardService`만 호출한다.

```text
Controller는 Service만 안다.
Service가 Client를 안다.
Client가 board_api를 호출한다.
```

이 구조가 훨씬 깔끔하다.

---

# 5. @RequestParam으로 여러 개 받는 게 왜 별로인가

기존 코드는 이렇게 되어 있었다.

```java
@PostMapping("/boards")
public String create(@RequestParam String title,
                     @RequestParam String author,
                     @RequestParam String content) {
    boardApiClient.create(title, author, content);
    return "redirect:/boards";
}
```

필드가 3개면 아직 괜찮아 보인다.

그런데 게시글에 필드가 늘어난다고 해보자.

```text
title
author
content
category
password
isNotice
createdBy
tags
thumbnailUrl
```

그러면 메서드가 이렇게 길어진다.

```java
public String create(@RequestParam String title,
                     @RequestParam String author,
                     @RequestParam String content,
                     @RequestParam String category,
                     @RequestParam String password,
                     @RequestParam Boolean isNotice,
                     @RequestParam String createdBy,
                     @RequestParam String tags,
                     @RequestParam String thumbnailUrl) {
}
```

이건 좋지 않다.

필드가 늘어날 때마다 메서드 시그니처를 계속 바꿔야 한다.

그래서 자바에서는 보통 객체로 묶어서 받는다.

```java
@PostMapping("/boards")
public String create(@ModelAttribute BoardCreateRequest request) {
    boardService.create(request);
    return "redirect:/boards";
}
```

이렇게 하면 필드가 늘어나도 Controller 메서드는 그대로다.

```java
public String create(@ModelAttribute BoardCreateRequest request)
```

변경은 DTO 클래스에서 처리하면 된다.

---

# 6. 폼 전송이면 @RequestBody가 아니라 @ModelAttribute가 맞다

여기서 헷갈리기 쉬운 부분이 있다.

HTML form에서 전송하는 데이터는 보통 이런 형태다.

```html
<form action="/boards" method="post">
    <input name="title">
    <input name="author">
    <textarea name="content"></textarea>
    <button type="submit">등록</button>
</form>
```

이 방식은 JSON 요청이 아니다.

일반적인 form submit이다.

이럴 때는 보통 `@ModelAttribute`로 받는다.

```java
@PostMapping("/boards")
public String create(@ModelAttribute BoardCreateRequest request) {
    boardService.create(request);
    return "redirect:/boards";
}
```

반대로 `@RequestBody`는 JSON 요청을 받을 때 주로 쓴다.

```java
@PostMapping("/api/boards")
public BoardResponse create(@RequestBody BoardCreateRequest request) {
    return boardService.create(request);
}
```

정리하면 이렇다.

```text
HTML form submit
→ @ModelAttribute

JSON API 요청
→ @RequestBody
```

Thymeleaf 기반 프론트 서버라면 보통 `@ModelAttribute`가 더 자연스럽다.

---

# 7. DTO로 받는 구조

`@RequestParam` 대신 DTO를 만든다.

```java
public class BoardCreateRequest {

    private String title;
    private String author;
    private String content;

    public String getTitle() {
        return title;
    }

    public String getAuthor() {
        return author;
    }

    public String getContent() {
        return content;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public void setAuthor(String author) {
        this.author = author;
    }

    public void setContent(String content) {
        this.content = content;
    }
}
```

수정용 DTO도 따로 둔다.

```java
public class BoardUpdateRequest {

    private String title;
    private String author;
    private String content;

    public String getTitle() {
        return title;
    }

    public String getAuthor() {
        return author;
    }

    public String getContent() {
        return content;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public void setAuthor(String author) {
        this.author = author;
    }

    public void setContent(String content) {
        this.content = content;
    }
}
```

form에서 넘어오는 값은 setter를 통해 객체에 바인딩된다.

그래서 HTML의 `name`과 DTO 필드명이 맞아야 한다.

```html
<input name="title">
<input name="author">
<textarea name="content"></textarea>
```

```java
private String title;
private String author;
private String content;
```

이름이 맞으면 Spring이 자동으로 값을 넣어준다.

---

# 8. Model은 View에 데이터를 연결해주는 역할

목록 페이지 코드를 보자.

```java
@GetMapping("/boards")
public String list(Model model) {
    model.addAttribute("boards", boardService.findAll());
    return "list";
}
```

여기서 `Model`은 Controller에서 View로 데이터를 넘겨주는 상자다.

```java
model.addAttribute("boards", boardService.findAll());
```

이 코드는 이런 의미다.

```text
boards라는 이름으로 게시글 목록을 View에 넘긴다.
```

그러면 `list.html`에서 이 값을 사용할 수 있다.

```html
<tr th:each="board : ${boards}">
    <td th:text="${board.id}"></td>
    <td th:text="${board.title}"></td>
    <td th:text="${board.author}"></td>
</tr>
```

즉, Controller에서 Model에 담으면 Thymeleaf가 그 값을 집어서 화면에 뿌려준다.

네가 말한 “모델이 뷰에 연결해주면 찝게 되어있음”이 이 뜻이다.

---

# 9. @GetMapping("/boards/{id:\d+}")는 왜 이상했나

이런 코드가 있었다고 하자.

```java
@GetMapping("/boards/{id:\\d+}")
public String detail(@PathVariable Long id, Model model) {
    model.addAttribute("board", boardService.findById(id));
    return "detail";
}
```

`{id:\\d+}`는 숫자만 받겠다는 의미다.

즉, `/boards/1`, `/boards/2` 같은 요청만 이 메서드가 처리한다.

기술적으로 틀린 건 아니다.

하지만 현재 흐름에서 굳이 이렇게 복잡하게 만들 필요가 없었다는 지적이다.

일반적으로는 이렇게 둬도 충분하다.

```java
@GetMapping("/boards/{id}")
public String detail(@PathVariable Long id, Model model) {
    model.addAttribute("board", boardService.findById(id));
    return "detail";
}
```

그리고 “선택하고 누른 건데 왜 플러스가 되냐”는 문제는 보통 링크나 form action이 잘못 잡혔을 가능성이 크다.

예를 들어 상세 페이지로 가야 하는데 등록 페이지로 가는 URL을 호출했을 수 있다.

```html
<!-- 상세 페이지로 가야 함 -->
<a th:href="@{/boards/{id}(id=${board.id})}">상세보기</a>
```

그런데 실수로 이런 식이면 문제가 된다.

```html
<!-- 글쓰기 페이지나 생성 요청으로 잘못 연결될 수 있음 -->
<a th:href="@{/boards/write}">상세보기</a>
```

또는 버튼이 form 내부에 있어서 의도치 않게 submit이 발생했을 수도 있다.

---

# 10. 설정값은 application.properties에서 받기

프론트 서버는 8081 포트로 실행하고, 백엔드 API 서버는 8080으로 실행한다고 하자.

`application.properties`는 이렇게 둔다.

```properties
spring.application.name=board_fe
server.port=8081

board.api.base-url=http://localhost:8080
```

여기서 중요한 설정은 이것이다.

```properties
board.api.base-url=http://localhost:8080
```

이 값은 `BoardApiClient`가 백엔드 API를 호출할 때 사용한다.

즉, URL을 코드에 직접 박아두는 대신 설정 파일에서 가져온다.

나쁜 예시는 이거다.

```java
private final String baseUrl = "http://localhost:8080";
```

좋은 예시는 설정값을 주입받는 방식이다.

```java
@Component
public class BoardApiClient {

    private final RestClient restClient;

    public BoardApiClient(
            RestClient.Builder builder,
            @Value("${board.api.base-url}") String baseUrl
    ) {
        this.restClient = builder
                .baseUrl(baseUrl)
                .build();
    }
}
```

이렇게 하면 나중에 API 서버 주소가 바뀌어도 코드 수정 없이 설정만 바꾸면 된다.

---

# 11. BoardService가 BoardApiClient를 호출하는 구조

`BoardApiClient`는 실제 HTTP 요청을 담당한다.

```java
@Component
public class BoardApiClient {

    private final RestClient restClient;

    public BoardApiClient(
            RestClient.Builder builder,
            @Value("${board.api.base-url}") String baseUrl
    ) {
        this.restClient = builder.baseUrl(baseUrl).build();
    }

    public List<BoardResponse> findAll() {
        return restClient.get()
                .uri("/boards")
                .retrieve()
                .body(new ParameterizedTypeReference<List<BoardResponse>>() {});
    }

    public BoardResponse findById(Long id) {
        return restClient.get()
                .uri("/boards/{id}", id)
                .retrieve()
                .body(BoardResponse.class);
    }

    public void create(BoardCreateRequest request) {
        restClient.post()
                .uri("/boards")
                .body(request)
                .retrieve()
                .toBodilessEntity();
    }

    public void update(Long id, BoardUpdateRequest request) {
        restClient.put()
                .uri("/boards/{id}", id)
                .body(request)
                .retrieve()
                .toBodilessEntity();
    }

    public void delete(Long id) {
        restClient.delete()
                .uri("/boards/{id}", id)
                .retrieve()
                .toBodilessEntity();
    }
}
```

그리고 Service는 이 Client를 감싼다.

```java
@Service
public class BoardService {

    private final BoardApiClient boardApiClient;

    public BoardService(BoardApiClient boardApiClient) {
        this.boardApiClient = boardApiClient;
    }

    public List<BoardResponse> findAll() {
        return boardApiClient.findAll();
    }

    public BoardResponse findById(Long id) {
        return boardApiClient.findById(id);
    }

    public void create(BoardCreateRequest request) {
        boardApiClient.create(request);
    }

    public void update(Long id, BoardUpdateRequest request) {
        boardApiClient.update(id, request);
    }

    public void delete(Long id) {
        boardApiClient.delete(id);
    }
}
```

지금은 Service가 단순히 Client를 호출하는 것처럼 보인다.

그래도 이 계층을 두는 게 좋다.

나중에 검증, 예외 처리, 데이터 가공, 권한 체크 같은 로직이 들어갈 자리가 되기 때문이다.

---

# 12. 최종 흐름

전체 흐름은 이렇게 가야 한다.

```text
사용자 브라우저
→ board_fe Controller
→ board_fe Service
→ board_fe BoardApiClient
→ board_api Controller
→ board_api Service
→ board_api Repository
→ DB
```

즉, 프론트 서버와 백엔드 서버 모두 구조가 있다.

```text
board_fe
Controller → Service → Client → board_api 호출

board_api
Controller → Service → Repository → DB
```

이렇게 맞춰야 나중에 코드를 읽을 때 흐름이 자연스럽다.

---

# 13. 이번 지적의 핵심 정리

이번에 지적받은 부분은 이렇게 정리할 수 있다.

```text
1. 프론트 서버도 Spring Boot면 구조를 맞춰야 한다.
2. Controller에서 Client를 직접 호출하지 말고 Service를 거쳐야 한다.
3. @RequestParam으로 여러 필드를 하나씩 받지 말고 DTO 객체로 받아야 한다.
4. HTML form 요청이면 보통 @ModelAttribute가 맞다.
5. JSON 요청이면 @RequestBody를 쓴다.
6. Model은 Controller 데이터를 Thymeleaf View에 연결해주는 역할이다.
7. 설정값은 application.properties에 두고 @Value로 주입받는 게 좋다.
8. BoardApiClient는 외부 board_api 호출만 담당해야 한다.
9. Controller는 index, list, detail, write, edit 같은 HTML View 반환에 집중해야 한다.
```

한 줄로 정리하면 이거다.

> board_fe도 단순 화면 프로젝트가 아니라 Spring Boot 애플리케이션이므로, Controller-Service-Client-DTO 구조로 역할을 나눠야 한다.

이번 문제는 “문법을 몰랐다”보다 “계층 구조를 맞추지 않았다”에 가깝다.

앞으로는 프론트 서버도 백엔드처럼 구조를 먼저 잡고 들어가는 게 맞다.
