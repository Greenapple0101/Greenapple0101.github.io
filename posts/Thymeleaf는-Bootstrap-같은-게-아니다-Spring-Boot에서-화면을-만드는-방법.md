---
title: "[Spring] Thymeleaf는 Bootstrap 같은 게 아니다 — Spring Boot에서 화면을 만드는 방법"
source: "https://velog.io/@yorange50/Thymeleaf는-Bootstrap-같은-게-아니다-Spring-Boot에서-화면을-만드는-방법"
published: "2026-05-03T11:03:20.389Z"
tags: "Spring"
backup_date: "2026-05-29T14:52:52.780326"
---

Spring Boot로 게시판 API를 만들다가 “프론트엔드를 Spring Boot에서 하라”, “HTML은 Thymeleaf로 하라”는 말을 들었다. 처음에는 Thymeleaf가 Bootstrap 같은 디자인 프레임워크인가 싶었다. 하지만 Thymeleaf는 Bootstrap과 역할이 완전히 다르다. Bootstrap이 화면을 예쁘게 꾸미는 CSS 프레임워크라면, Thymeleaf는 Spring Boot 서버에서 HTML에 데이터를 넣어 완성된 화면을 만들어주는 서버 사이드 템플릿 엔진이다.

## 1. Thymeleaf와 Bootstrap의 차이

먼저 역할을 구분하면 이해가 쉽다.

```text
Bootstrap = 버튼, 테이블, 카드 같은 화면을 예쁘게 꾸미는 CSS 프레임워크
Thymeleaf = Spring Boot 데이터를 HTML에 넣어주는 템플릿 엔진
React = 브라우저에서 JavaScript로 화면을 동적으로 만드는 프론트엔드 라이브러리
```

예를 들어 Bootstrap은 버튼을 이렇게 예쁘게 만든다.

```html
<button class="btn btn-primary">등록</button>
```

여기서 `btn`, `btn-primary` 같은 클래스가 Bootstrap 문법이다. 즉, Bootstrap은 디자인 담당이다.

반면 Thymeleaf는 서버에서 넘어온 데이터를 HTML에 출력한다.

```html
<p th:text="${board.title}"></p>
```

이 코드는 `board.title` 값을 `<p>` 태그 안에 넣으라는 뜻이다. 즉, Thymeleaf는 데이터 출력 담당이다.

정리하면 Bootstrap은 옷이고, Thymeleaf는 서버 데이터를 HTML에 꽂아주는 도구다.

## 2. Thymeleaf를 쓰는 이유

React를 사용할 때는 보통 이런 구조가 된다.

```text
브라우저에서 React 실행
→ API 호출
→ JSON 데이터 받음
→ React가 화면을 그림
```

하지만 Thymeleaf를 쓰면 구조가 다르다.

```text
브라우저가 페이지 요청
→ Spring Boot Controller 실행
→ 서버에서 데이터를 Model에 담음
→ Thymeleaf HTML에 데이터 삽입
→ 완성된 HTML을 브라우저에 전달
```

즉, React는 브라우저에서 화면을 만들고, Thymeleaf는 서버에서 화면을 만들어서 브라우저에 보내준다.

그래서 “프론트를 Spring Boot에서 하라”는 요구사항은 보통 별도의 React/Vue 프로젝트를 두지 말고, Spring Boot 프로젝트 안에서 HTML 화면까지 처리하라는 의미에 가깝다.

## 3. Spring Boot에서 Thymeleaf 파일 위치

Spring Boot에서 Thymeleaf HTML 파일은 아래 위치에 둔다.

```text
src/main/resources/templates/
```

예를 들어 홈페이지를 만들고 싶다면 다음과 같이 파일을 만든다.

```text
src/main/resources/templates/index.html
```

CSS나 JavaScript 같은 정적 파일은 `templates`가 아니라 `static` 아래에 둔다.

```text
src/main/resources/static/css/style.css
src/main/resources/static/js/board.js
```

즉, 구조는 이렇게 된다.

```text
src/main/resources/
├─ templates/
│  ├─ index.html
│  └─ boards.html
│
└─ static/
   ├─ css/
   │  └─ style.css
   └─ js/
      └─ board.js
```

## 4. Thymeleaf 의존성 추가

Maven 프로젝트라면 `pom.xml`에 Thymeleaf 의존성을 추가해야 한다.

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-thymeleaf</artifactId>
</dependency>
```

이 의존성이 있어야 Spring Boot가 `templates` 폴더 안의 HTML 파일을 Thymeleaf 템플릿으로 처리할 수 있다.

## 5. `@RestController`와 `@Controller`의 차이

Thymeleaf를 쓸 때 가장 헷갈리는 부분이 `@RestController`와 `@Controller`의 차이다.

JSON API를 만들 때는 `@RestController`를 사용한다.

```java
@RestController
public class BoardController {

    @GetMapping("/boards")
    public List<Board> getBoards() {
        return boardService.getBoards();
    }
}
```

이 경우 `/boards`로 요청하면 게시글 목록이 JSON으로 반환된다.

반면 HTML 화면을 보여줄 때는 `@Controller`를 사용한다.

```java
@Controller
public class HomeController {

    @GetMapping("/")
    public String home() {
        return "index";
    }
}
```

여기서 `return "index";`는 문자열 `index`를 브라우저에 그대로 출력하라는 뜻이 아니다. `src/main/resources/templates/index.html` 파일을 찾아서 화면으로 보여주라는 뜻이다.

정리하면 다음과 같다.

```text
@RestController → 데이터를 그대로 반환함. 주로 JSON API용
@Controller → HTML 템플릿 이름을 반환함. 주로 Thymeleaf 화면용
```

## 6. 기본 홈페이지 만들기

먼저 `templates/index.html` 파일을 만든다.

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>Board Home</title>
</head>
<body>

<h1>게시판 홈</h1>
<p>Spring Boot + Thymeleaf로 만든 게시판입니다.</p>

<a th:href="@{/boards-page}">게시글 목록 보기</a>

</body>
</html>
```

그리고 이 HTML을 보여줄 컨트롤러를 만든다.

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

이제 Spring Boot를 실행하고 브라우저에서 아래 주소로 접속하면 된다.

```text
http://localhost:8080/
```

정상적으로 설정되어 있다면 Whitelabel Error Page가 아니라 `index.html` 화면이 보인다.

## 7. Controller에서 HTML로 데이터 넘기기

게시글 목록을 화면에 보여주려면 서버에서 데이터를 HTML로 넘겨야 한다. 이때 사용하는 것이 `Model`이다.

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

여기서 핵심은 이 코드다.

```java
model.addAttribute("boards", boardService.getBoards());
```

이 뜻은 `boardService.getBoards()`로 가져온 게시글 목록을 `boards`라는 이름으로 HTML에서 사용할 수 있게 넘겨준다는 의미다.

그리고 마지막의 `return "boards";`는 `templates/boards.html` 파일을 보여주겠다는 뜻이다.

## 8. HTML에서 서버 데이터 출력하기

이제 `templates/boards.html` 파일을 만든다.

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
    </tr>
    </thead>

    <tbody>
    <tr th:each="board : ${boards}">
        <td th:text="${board.id}"></td>
        <td th:text="${board.title}"></td>
        <td th:text="${board.author}"></td>
    </tr>
    </tbody>
</table>

</body>
</html>
```

여기서 중요한 Thymeleaf 문법은 두 가지다.

### `th:each`

```html
<tr th:each="board : ${boards}">
```

이 코드는 `boards` 목록에서 데이터를 하나씩 꺼내서 `board`라는 이름으로 사용하겠다는 뜻이다.

React로 치면 아래 코드와 비슷하다.

```jsx
boards.map(board => (
  <tr>
    <td>{board.title}</td>
  </tr>
))
```

### `th:text`

```html
<td th:text="${board.title}"></td>
```

이 코드는 `board.title` 값을 해당 태그 안에 출력하라는 뜻이다.

예를 들어 제목이 `첫 번째 글`이면 실제 브라우저에는 아래처럼 렌더링된다.

```html
<td>첫 번째 글</td>
```

## 9. 글 작성 폼 만들기

Thymeleaf에서는 HTML form을 이용해서 서버로 데이터를 보낼 수 있다.

`templates/write.html` 파일을 만든다.

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>글 작성</title>
</head>
<body>

<h1>글 작성</h1>

<form action="/boards-page" method="post">
    <input type="text" name="title" placeholder="제목">
    <input type="text" name="author" placeholder="작성자">
    <textarea name="content" placeholder="내용"></textarea>

    <button type="submit">등록</button>
</form>

</body>
</html>
```

이때 중요한 점은 `name` 속성이다.

```html
<input name="title">
<input name="author">
<textarea name="content"></textarea>
```

이 이름들이 `Board` 클래스의 필드명과 같아야 한다.

```java
private String title;
private String author;
private String content;
```

그러면 Spring이 form 데이터를 자동으로 `Board` 객체에 바인딩해준다.

컨트롤러는 다음과 같이 작성할 수 있다.

```java
@GetMapping("/boards-write")
public String writeForm() {
    return "write";
}

@PostMapping("/boards-page")
public String createBoard(Board board) {
    boardService.createBoard(board);
    return "redirect:/boards-page";
}
```

여기서 `redirect:/boards-page`는 글 작성 후 게시글 목록 페이지로 다시 이동하라는 뜻이다.

## 10. Thymeleaf와 Bootstrap 같이 쓰기

Thymeleaf는 디자인 도구가 아니기 때문에 Bootstrap과 같이 사용할 수 있다. 오히려 빠르게 화면을 만들 때는 `Spring Boot + Thymeleaf + Bootstrap` 조합이 많이 쓰인다.

예를 들어 Bootstrap 테이블 스타일과 Thymeleaf 반복문을 함께 쓸 수 있다.

```html
<table class="table table-striped">
    <tr th:each="board : ${boards}">
        <td th:text="${board.id}"></td>
        <td th:text="${board.title}"></td>
        <td th:text="${board.author}"></td>
    </tr>
</table>
```

여기서 역할은 이렇게 나뉜다.

```text
class="table table-striped" → Bootstrap
th:each, th:text → Thymeleaf
```

즉, Bootstrap은 화면을 꾸미고 Thymeleaf는 데이터를 출력한다.

## 11. React로 만든 BOARD_FE 레포는 어떻게 해야 할까

이미 React로 `BOARD_FE` 레포를 만들었다면 삭제할 필요는 없다. 다만 요구사항이 Spring Boot + Thymeleaf라면 실제 구현은 `board_api` 프로젝트 안에서 진행하는 것이 맞다.

구조는 이렇게 정리할 수 있다.

```text
board_api
├─ Spring Boot REST API
├─ Thymeleaf HTML 화면
└─ static CSS/JS

BOARD_FE
└─ 기존 React 프론트엔드
   → 참고용 / 백업용 / 나중에 SPA 전환용으로 보관
```

React에서 만든 화면 구조, CSS, API 호출 로직은 Thymeleaf 화면으로 옮길 때 참고 자료로 사용할 수 있다.

README에는 다음처럼 남겨둘 수 있다.

```md
# BOARD_FE

React 기반 게시판 프론트엔드 실습 레포지토리입니다.

현재 프로젝트 요구사항이 Spring Boot + Thymeleaf 기반 서버사이드 렌더링 구조로 변경되어,
실제 통합 구현은 `board_api` 레포지토리에서 진행합니다.

이 레포지토리는 React 기반 UI 구현 및 API 연동 로직 참고용으로 보관합니다.
```

## 12. 전체 구조 정리

최종적으로 게시판 프로젝트 구조는 다음과 비슷해진다.

```text
src/main/java/com/board/api/
├─ controller/
│  ├─ BoardController.java       // JSON API용
│  ├─ HomeController.java        // 홈페이지 화면용
│  └─ BoardPageController.java   // 게시글 목록/작성 화면용
│
├─ service/
│  └─ BoardService.java
│
└─ domain/
   └─ Board.java

src/main/resources/
├─ templates/
│  ├─ index.html
│  ├─ boards.html
│  └─ write.html
│
└─ static/
   ├─ css/
   │  └─ style.css
   └─ js/
      └─ board.js
```

## 13. 핵심 요약

Thymeleaf는 Bootstrap 같은 디자인 프레임워크가 아니다. Bootstrap은 화면을 예쁘게 꾸미는 도구이고, Thymeleaf는 Spring Boot 서버 데이터를 HTML에 넣어주는 템플릿 엔진이다. React가 브라우저에서 JavaScript로 화면을 그린다면, Thymeleaf는 Spring Boot 서버에서 완성된 HTML을 만들어 브라우저에 전달한다. 그래서 Spring Boot에서 프론트 화면까지 처리해야 하는 상황이라면 `@Controller`, `Model`, `templates/*.html`, `th:text`, `th:each`를 사용하면 된다. 디자인이 필요하면 Bootstrap을 함께 사용하면 된다.

결국 가장 중요한 흐름은 이것이다.

```text
Controller가 데이터를 Model에 넣는다.
Thymeleaf HTML이 Model 데이터를 꺼내 화면에 출력한다.
브라우저는 완성된 HTML을 받는다.
```

이 흐름만 이해하면 Thymeleaf는 어렵지 않다.
