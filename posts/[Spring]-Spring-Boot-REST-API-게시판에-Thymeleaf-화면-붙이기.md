---
title: "[Spring] Spring Boot REST API 게시판에 Thymeleaf 화면 붙이기"
source: "https://velog.io/@yorange50/Spring-Boot-REST-API-게시판에-Thymeleaf-화면-붙이기"
published: "2026-05-03T12:20:21.904Z"
tags: ""
backup_date: "2026-05-29T14:52:52.780076"
---

처음에는 Spring Boot로 게시판 REST API를 만들고, 프론트엔드는 React로 따로 구성하는 방식으로 생각하고 있었다. 구조는 단순했다.

```text
BOARD_FE  → React 프론트엔드
board_api → Spring Boot REST API
```

React 화면에서 Spring Boot API를 호출하고, Spring Boot는 게시글 데이터를 JSON으로 반환하는 전형적인 프론트엔드/백엔드 분리 구조였다.

하지만 중간에 요구사항이 바뀌었다.

> 프론트엔드를 Spring Boot에서 한다.
> 프론트 Spring Boot에서 API를 호출해야 한다.
> HTML은 Thymeleaf로 한다.

처음에는 이 말이 조금 헷갈렸다. 이미 React 프론트 레포를 만들어둔 상태였고, Thymeleaf가 Bootstrap 같은 디자인 도구인지도 명확하지 않았다. 이번 작업은 이 요구사항을 이해하고, 기존 REST API 게시판에 Thymeleaf 기반 화면을 붙이는 과정이었다.

---

## 1. Thymeleaf는 Bootstrap이 아니었다

처음에 가장 헷갈렸던 부분은 Thymeleaf의 역할이었다.

정리하면 다음과 같다.

```text
Bootstrap  → 화면을 예쁘게 꾸미는 CSS 프레임워크
Thymeleaf  → Spring Boot 데이터를 HTML에 넣어주는 템플릿 엔진
React      → 브라우저에서 화면을 동적으로 만드는 프론트엔드 라이브러리
```

Bootstrap은 버튼, 테이블, 카드 같은 UI를 예쁘게 꾸미는 도구다.

```html
<button class="btn btn-primary">등록</button>
```

반면 Thymeleaf는 서버에서 전달한 데이터를 HTML 안에 출력하는 도구다.

```html
<p th:text="${board.title}"></p>
```

즉 Thymeleaf는 디자인 프레임워크가 아니라, **Spring Boot 서버에서 HTML을 렌더링하기 위한 서버 사이드 템플릿 엔진**이다.

---

## 2. 기존 REST API 구조

기존에는 게시판 CRUD를 처리하는 REST API 컨트롤러가 있었다.

```java
package com.board.api.controller;

import com.board.api.domain.Board;
import com.board.api.service.BoardService;
import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
@RequestMapping("/boards")
@CrossOrigin(origins = "http://localhost:5173")
public class BoardController {

    private final BoardService boardService;

    public BoardController(BoardService boardService){
        this.boardService = boardService;
    }

    @GetMapping
    public List<Board> getBoards(){
        return boardService.getBoards();
    }

    @GetMapping("/{id}")
    public Board getBoard(@PathVariable Long id){
        return boardService.getBoard(id);
    }

    @PostMapping
    public Board createBoard(@RequestBody Board board){
        return boardService.createBoard(board);
    }

    @PutMapping("/{id}")
    public Board updateBoard(@PathVariable Long id, @RequestBody Board board){
        return boardService.updateBoard(id, board);
    }

    @DeleteMapping("/{id}")
    public String deleteBoard(@PathVariable Long id){
        boardService.deleteBoard(id);
        return "삭제됨: " + id;
    }
}
```

이 컨트롤러는 다음 API를 담당한다.

```text
GET    /boards       → 게시글 전체 조회
GET    /boards/{id}  → 게시글 단건 조회
POST   /boards       → 게시글 작성
PUT    /boards/{id}  → 게시글 수정
DELETE /boards/{id}  → 게시글 삭제
```

여기서 중요한 점은, Thymeleaf를 도입한다고 해서 이 REST API 컨트롤러를 삭제하면 안 된다는 것이다. 이 컨트롤러는 여전히 게시판 데이터 처리의 핵심이다.

---

## 3. REST API 컨트롤러와 화면 컨트롤러 분리

Thymeleaf를 붙이면서 가장 먼저 정리한 것은 컨트롤러의 역할 분리였다.

```text
BoardController.java      → REST API 담당
HomeController.java       → Thymeleaf 홈 화면 담당
BoardPageController.java  → Thymeleaf 게시판 화면 담당
```

즉 URL 역할은 이렇게 나뉜다.

```text
/boards       → JSON API
/             → Thymeleaf 홈 화면
/boards-page  → Thymeleaf 게시글 목록 화면
```

`@RestController`와 `@Controller`의 차이도 여기서 확실히 이해했다.

```text
@RestController → return 값을 HTTP 응답 본문으로 그대로 반환
@Controller     → return 값을 Thymeleaf 템플릿 이름으로 해석
```

예를 들어 `@RestController`에서 `return "index";`를 하면 브라우저에는 문자열 `index`가 그대로 출력된다.

하지만 `@Controller`에서 `return "index";`를 하면 Spring Boot는 아래 파일을 찾아 화면으로 렌더링한다.

```text
src/main/resources/templates/index.html
```

---

## 4. Thymeleaf 의존성 추가

Spring Boot에서 Thymeleaf를 사용하기 위해 `pom.xml`에 의존성을 추가했다.

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-thymeleaf</artifactId>
</dependency>
```

이 의존성을 추가하면 Spring Boot는 기본적으로 아래 경로에 있는 HTML 파일을 Thymeleaf 템플릿으로 인식한다.

```text
src/main/resources/templates/
```

---

## 5. 첫 Thymeleaf 홈페이지 구현

먼저 홈 화면을 만들었다.

파일 위치는 다음과 같다.

```text
src/main/resources/templates/index.html
```

내용은 간단하게 구성했다.

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>Board Home</title>
</head>
<body>
    <h1>게시판 홈</h1>
    <p>Spring Boot + Thymeleaf 홈페이지입니다.</p>

    <a th:href="@{/boards-page}">게시글 목록 보기</a>
</body>
</html>
```

그리고 `/` 요청을 처리할 `HomeController`를 만들었다.

```java
package com.board.api.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class HomeController {

    @GetMapping("/")
    public String home() {
        return "index";
    }
}
```

여기서 `return "index";`는 문자열을 반환하는 것이 아니라, `templates/index.html`을 렌더링하라는 의미다.

브라우저에서 아래 주소로 접속했다.

```text
http://localhost:8080/
```

결과적으로 Thymeleaf 홈 화면이 정상적으로 렌더링되었다.

```text
게시판 홈
Spring Boot + Thymeleaf 홈페이지입니다.
게시글 목록 보기
```

이 시점에서 확인한 것은 다음과 같다.

```text
Spring Boot 실행 성공
Thymeleaf 의존성 적용 성공
HomeController 매핑 성공
index.html 렌더링 성공
```

---

## 6. 게시글 목록 화면 구현

다음으로 `/boards-page`에서 게시글 목록을 보여주도록 구현했다.

`BoardPageController`를 생성했다.

```java
package com.board.api.controller;

import com.board.api.service.BoardService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class BoardPageController {

    private final BoardService boardService;

    public BoardPageController(BoardService boardService) {
        this.boardService = boardService;
    }

    @GetMapping("/boards-page")
    public String boardsPage(Model model) {
        model.addAttribute("boards", boardService.getBoards());
        return "boards";
    }
}
```

여기서 핵심은 이 부분이다.

```java
model.addAttribute("boards", boardService.getBoards());
```

`boardService.getBoards()`로 가져온 게시글 목록을 `boards`라는 이름으로 HTML에서 사용할 수 있게 넘겨주는 코드다.

그리고 `return "boards";`는 아래 파일을 렌더링한다는 의미다.

```text
src/main/resources/templates/boards.html
```

---

## 7. `boards.html`에서 목록 출력하기

게시글 목록 화면에서는 Thymeleaf 반복문을 사용했다.

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>게시글 목록</title>
</head>
<body>

<h1>게시글 목록</h1>

<a th:href="@{/}">홈으로</a>
<a th:href="@{/boards-write}">글 작성</a>

<table border="1">
    <thead>
    <tr>
        <th>ID</th>
        <th>제목</th>
        <th>작성자</th>
        <th>작성일</th>
        <th>관리</th>
    </tr>
    </thead>

    <tbody>
    <tr th:each="board : ${boards}">
        <td th:text="${board.id}"></td>

        <td>
            <a th:href="@{/boards-page/{id}(id=${board.id})}"
               th:text="${board.title}">
            </a>
        </td>

        <td th:text="${board.author}"></td>
        <td th:text="${board.createdAt}"></td>

        <td>
            <a th:href="@{/boards-edit/{id}(id=${board.id})}">수정</a>

            <form th:action="@{/boards-delete/{id}(id=${board.id})}"
                  method="post"
                  style="display:inline;">
                <button type="submit">삭제</button>
            </form>
        </td>
    </tr>
    </tbody>
</table>

</body>
</html>
```

여기서 사용한 Thymeleaf 문법은 다음과 같다.

```text
th:each → 리스트 반복
th:text → 값 출력
th:href → 링크 생성
```

React에서 `boards.map(board => ...)`를 사용하던 것과 비슷하게, Thymeleaf에서는 `th:each`로 리스트를 반복한다.

---

## 8. 브라우저 주소창에서는 GET만 된다

구현 중에 “왜 읽기만 되는 것처럼 보이지?”라는 문제가 있었다.

이유는 간단했다.

```text
브라우저 주소창은 기본적으로 GET 요청만 보낼 수 있다.
```

따라서 `/boards`에 접속하면 전체 조회는 가능하지만, 주소창만으로는 `POST`, `PUT`, `DELETE`를 테스트할 수 없다.

REST API 자체는 다음 순서로 테스트할 수 있다.

```text
1. GET    /boards       → 전체 조회
2. POST   /boards       → 게시글 작성
3. GET    /boards       → 작성 결과 확인
4. GET    /boards/{id}  → 단건 조회
5. PUT    /boards/{id}  → 게시글 수정
6. DELETE /boards/{id}  → 게시글 삭제
7. GET    /boards       → 삭제 결과 확인
```

하지만 브라우저 화면에서 직접 작성, 수정, 삭제를 하려면 Thymeleaf form을 만들어야 한다.

---

## 9. 글 작성 화면 추가

글 작성 화면을 위해 다음 파일을 만들었다.

```text
src/main/resources/templates/board-write.html
```

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>게시글 작성</title>
</head>
<body>

<h1>게시글 작성</h1>

<form th:action="@{/boards-page}" method="post">
    <div>
        <label>제목</label>
        <input type="text" name="title">
    </div>

    <div>
        <label>작성자</label>
        <input type="text" name="author">
    </div>

    <div>
        <label>내용</label>
        <textarea name="content"></textarea>
    </div>

    <button type="submit">등록</button>
</form>

<a th:href="@{/boards-page}">목록으로</a>

</body>
</html>
```

컨트롤러에는 작성 화면과 작성 처리 메서드를 추가했다.

```java
@GetMapping("/boards-write")
public String writeForm() {
    return "board-write";
}

@PostMapping("/boards-page")
public String createBoard(@ModelAttribute Board board) {
    boardService.createBoard(board);
    return "redirect:/boards-page";
}
```

여기서 REST API와 Thymeleaf form의 차이를 알게 되었다.

```text
REST API에서는 @RequestBody 사용
Thymeleaf form에서는 @ModelAttribute 사용
```

REST API는 JSON을 보낸다.

```json
{
  "title": "제목",
  "content": "내용",
  "author": "작성자"
}
```

반면 HTML form은 다음과 같은 form 데이터를 보낸다.

```text
title=제목&content=내용&author=작성자
```

그래서 Thymeleaf form에서는 `@RequestBody`가 아니라 `@ModelAttribute`로 받는 것이 자연스럽다.

---

## 10. 상세 화면 추가

게시글 제목을 클릭하면 상세 페이지로 이동하도록 만들었다.

컨트롤러에는 단건 조회 화면을 추가했다.

```java
@GetMapping("/boards-page/{id}")
public String boardDetail(@PathVariable Long id, Model model) {
    model.addAttribute("board", boardService.getBoard(id));
    return "board-detail";
}
```

파일은 다음 위치에 만들었다.

```text
src/main/resources/templates/board-detail.html
```

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>게시글 상세</title>
</head>
<body>

<h1>게시글 상세</h1>

<p>ID: <span th:text="${board.id}"></span></p>
<p>제목: <span th:text="${board.title}"></span></p>
<p>작성자: <span th:text="${board.author}"></span></p>
<p>내용: <span th:text="${board.content}"></span></p>
<p>작성일: <span th:text="${board.createdAt}"></span></p>
<p>수정일: <span th:text="${board.updatedAt}"></span></p>

<a th:href="@{/boards-page}">목록으로</a>
<a th:href="@{/boards-edit/{id}(id=${board.id})}">수정</a>

<form th:action="@{/boards-delete/{id}(id=${board.id})}"
      method="post"
      style="display:inline;">
    <button type="submit">삭제</button>
</form>

</body>
</html>
```

---

## 11. 수정 화면 추가

수정 기능을 화면에서 처리하기 위해 수정 페이지를 추가했다.

```text
src/main/resources/templates/board-edit.html
```

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>게시글 수정</title>
</head>
<body>

<h1>게시글 수정</h1>

<form th:action="@{/boards-edit/{id}(id=${board.id})}" method="post">
    <div>
        <label>제목</label>
        <input type="text" name="title" th:value="${board.title}">
    </div>

    <div>
        <label>작성자</label>
        <input type="text" name="author" th:value="${board.author}">
    </div>

    <div>
        <label>내용</label>
        <textarea name="content" th:text="${board.content}"></textarea>
    </div>

    <button type="submit">수정 완료</button>
</form>

<a th:href="@{/boards-page/{id}(id=${board.id})}">상세로</a>
<a th:href="@{/boards-page}">목록으로</a>

</body>
</html>
```

컨트롤러에는 수정 화면과 수정 처리 메서드를 추가했다.

```java
@GetMapping("/boards-edit/{id}")
public String editForm(@PathVariable Long id, Model model) {
    model.addAttribute("board", boardService.getBoard(id));
    return "board-edit";
}

@PostMapping("/boards-edit/{id}")
public String updateBoard(@PathVariable Long id, @ModelAttribute Board board) {
    boardService.updateBoard(id, board);
    return "redirect:/boards-page/" + id;
}
```

여기서도 HTML form의 제약을 고려했다.

HTML form은 기본적으로 `GET`과 `POST`만 지원한다. 그래서 화면에서는 `PUT` 대신 `POST`로 수정 처리를 했다.

```text
REST API 기준 수정 → PUT /boards/{id}
화면 기준 수정    → POST /boards-edit/{id}
```

---

## 12. 삭제 기능 추가

삭제도 HTML form으로 처리했다.

컨트롤러에는 삭제 처리 메서드를 추가했다.

```java
@PostMapping("/boards-delete/{id}")
public String deleteBoard(@PathVariable Long id) {
    boardService.deleteBoard(id);
    return "redirect:/boards-page";
}
```

목록 화면이나 상세 화면에서는 다음과 같이 form으로 삭제 요청을 보낸다.

```html
<form th:action="@{/boards-delete/{id}(id=${board.id})}" method="post">
    <button type="submit">삭제</button>
</form>
```

정리하면 다음과 같다.

```text
REST API 기준 삭제 → DELETE /boards/{id}
화면 기준 삭제    → POST /boards-delete/{id}
```

REST API에서는 `DELETE` 메서드를 유지하고, Thymeleaf 화면에서는 HTML form 제약에 맞춰 `POST`로 삭제 처리했다.

---

## 13. 최종 `BoardPageController`

최종적으로 Thymeleaf 화면용 컨트롤러는 다음과 같은 구조가 되었다.

```java
package com.board.api.controller;

import com.board.api.domain.Board;
import com.board.api.service.BoardService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
public class BoardPageController {

    private final BoardService boardService;

    public BoardPageController(BoardService boardService) {
        this.boardService = boardService;
    }

    // 게시글 목록 화면
    @GetMapping("/boards-page")
    public String boardsPage(Model model) {
        model.addAttribute("boards", boardService.getBoards());
        return "boards";
    }

    // 게시글 상세 화면
    @GetMapping("/boards-page/{id}")
    public String boardDetail(@PathVariable Long id, Model model) {
        model.addAttribute("board", boardService.getBoard(id));
        return "board-detail";
    }

    // 게시글 작성 화면
    @GetMapping("/boards-write")
    public String writeForm() {
        return "board-write";
    }

    // 게시글 작성 처리
    @PostMapping("/boards-page")
    public String createBoard(@ModelAttribute Board board) {
        boardService.createBoard(board);
        return "redirect:/boards-page";
    }

    // 게시글 수정 화면
    @GetMapping("/boards-edit/{id}")
    public String editForm(@PathVariable Long id, Model model) {
        model.addAttribute("board", boardService.getBoard(id));
        return "board-edit";
    }

    // 게시글 수정 처리
    @PostMapping("/boards-edit/{id}")
    public String updateBoard(@PathVariable Long id, @ModelAttribute Board board) {
        boardService.updateBoard(id, board);
        return "redirect:/boards-page/" + id;
    }

    // 게시글 삭제 처리
    @PostMapping("/boards-delete/{id}")
    public String deleteBoard(@PathVariable Long id) {
        boardService.deleteBoard(id);
        return "redirect:/boards-page";
    }
}
```

---

## 14. 최종 Thymeleaf 화면 흐름

최종적으로 화면 흐름은 다음과 같다.

```text
GET  /                  → 홈 화면
GET  /boards-page       → 게시글 목록 화면
GET  /boards-write      → 게시글 작성 화면
POST /boards-page       → 게시글 작성 처리

GET  /boards-page/{id}  → 게시글 상세 화면
GET  /boards-edit/{id}  → 게시글 수정 화면
POST /boards-edit/{id}  → 게시글 수정 처리

POST /boards-delete/{id} → 게시글 삭제 처리
```

이제 브라우저에서 단순 조회뿐 아니라 작성, 상세 조회, 수정, 삭제까지 처리할 수 있게 되었다.

---

## 15. 실행 방식 차이: Run 버튼과 Maven 명령어

작업 중에 VSCode의 Run 버튼과 Maven 명령어 실행 결과가 다르게 나오는 문제도 겪었다.

정리하면 다음과 같다.

```text
Run 버튼 실행
→ VSCode Java Extension이 main() 메서드를 직접 실행

mvn spring-boot:run
→ Maven이 pom.xml 기준으로 앱을 실행
```

Run 버튼은 빠르고 편하지만, VSCode의 Java 캐시나 classpath 상태에 영향을 받을 수 있다.

반면 `mvn spring-boot:run`은 `pom.xml` 기준으로 의존성과 빌드를 반영해서 실행하기 때문에 더 안정적이었다.

실제로 Run 버튼에서는 이전 상태처럼 보이거나 빈 화면이 나왔고, `mvn spring-boot:run`으로 실행했을 때는 최신 Thymeleaf 화면이 정상적으로 렌더링되었다.

그래서 현재 기준으로는 Maven 방식으로 실행했다.

```bash
mvn clean package
mvn spring-boot:run
```

---

## 16. 최종 프로젝트 구조

현재 프로젝트 구조는 다음과 같이 정리할 수 있다.

```text
src/main/java/com/board/api/
├─ BoardApiApplication.java
│
├─ controller/
│  ├─ BoardController.java       // REST API용
│  ├─ HomeController.java        // 홈 화면용
│  └─ BoardPageController.java   // Thymeleaf 화면 CRUD용
│
├─ service/
│  └─ BoardService.java
│
└─ domain/
   └─ Board.java
```

```text
src/main/resources/
├─ templates/
│  ├─ index.html
│  ├─ boards.html
│  ├─ board-detail.html
│  ├─ board-write.html
│  └─ board-edit.html
│
└─ static/
   └─ 필요 시 css/js 추가 가능
```

---

## 17. 현재까지 완료한 기능

이번 작업을 통해 완료한 기능은 다음과 같다.

```text
1. Spring Boot REST API CRUD 구현
2. Thymeleaf 의존성 추가
3. / 경로 홈페이지 렌더링
4. /boards-page 게시글 목록 화면 구현
5. Model을 이용해 BoardService 데이터 전달
6. th:each, th:text, th:href 사용
7. 글 작성 화면 구현
8. 글 작성 form 처리 구현
9. 상세 화면 구현
10. 수정 화면 구현
11. 수정 form 처리 구현
12. 삭제 form 처리 구현
13. REST API 컨트롤러와 화면 컨트롤러 역할 분리
14. Maven 실행 방식과 VSCode Run 실행 방식 차이 확인
```

---

## 18. 회고

이번 작업을 통해 REST API와 서버 사이드 렌더링의 역할 차이를 직접 이해할 수 있었다.

처음에는 Thymeleaf를 Bootstrap 같은 디자인 도구로 오해했지만, 실제로는 Spring Boot 서버 데이터를 HTML에 주입하는 템플릿 엔진이라는 점을 알게 되었다.

또한 `@RestController`는 JSON API 반환용이고, `@Controller`는 HTML 템플릿 렌더링용이라는 차이를 직접 구현하면서 이해했다.

브라우저 주소창에서는 GET 요청만 가능하기 때문에, POST, PUT, DELETE 같은 요청은 curl/Postman 같은 도구나 HTML form을 사용해야 한다는 점도 확인했다.

마지막으로 VSCode Run 버튼과 `mvn spring-boot:run`의 실행 기준이 다르다는 점을 경험했다. 의존성이나 빌드 반영까지 확실하게 확인하려면 Maven 실행이 더 안정적이라는 것도 알게 되었다.

이번 작업은 단순히 HTML 화면을 하나 띄운 것이 아니라, 기존 REST API 게시판 프로젝트에 Thymeleaf 기반 서버 사이드 화면을 추가하고, 브라우저에서 CRUD 흐름을 처리할 수 있도록 확장한 경험이었다.

---

## 한 줄 요약

```text
기존 Spring Boot REST API 게시판 프로젝트에 Thymeleaf 기반 서버 사이드 화면을 추가하고, 목록 조회부터 작성·상세·수정·삭제까지 브라우저에서 처리할 수 있도록 확장했다.
```
