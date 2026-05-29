---
title: "[Spring Boot] Whitelabel 404: URL 매핑 불일치 때문에 /boards가 안 뜬 문제"
source: "https://velog.io/@yorange50/Spring-Boot-Whitelabel-404-URL-매핑-불일치-때문에-boards가-안-뜬-문제"
published: "2026-05-06T04:55:11.381Z"
tags: ""
backup_date: "2026-05-29T14:52:52.775708"
---

Spring Boot로 `board_fe`를 만들고 Thymeleaf 템플릿까지 채웠는데, 브라우저에서 `/boards`에 접속하자 Whitelabel Error Page가 떴다.

에러 화면은 이런 내용이었다.

```text id="yien6n"
Whitelabel Error Page
This application has no explicit mapping for /error, so you are seeing this as a fallback.

There was an unexpected error (type=Not Found, status=404).
```

처음에는 Thymeleaf 템플릿을 못 찾는 문제인가 싶었다.
하지만 원인은 템플릿 문제가 아니라 **URL 매핑 불일치 문제**였다.

---

## 1. 상황

프로젝트 구조는 다음과 같이 나뉘어 있었다.

```text id="a42vdp"
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

`board_api`는 이미 정상적으로 실행되고 있었다.

```text id="jsyzxl"
http://localhost:8080/boards
```

여기서는 JSON 응답이 나와야 한다.

`board_fe`는 다음 주소로 화면을 보여주는 역할이었다.

```text id="a9i3iz"
http://localhost:8081/boards
```

그런데 `/boards`에 접속하자 404가 발생했다.

---

## 2. 404가 의미하는 것

Spring Boot에서 404는 보통 다음 의미다.

```text id="0fp0i8"
서버는 떠 있다.
하지만 해당 URL을 처리할 Controller 매핑이 없다.
```

즉 서버 자체가 죽은 것은 아니다.
포트도 열려 있고 애플리케이션도 실행 중인데, 내가 요청한 주소를 받을 메서드가 없는 것이다.

예를 들어 브라우저에서 다음 주소로 요청했다고 하자.

```text id="eeqbb9"
GET /boards
```

그러면 Spring은 Controller 안에서 `/boards`를 처리할 메서드를 찾는다.

```java id="drxz41"
@GetMapping("/boards")
```

또는:

```java id="ehos06"
@RequestMapping("/boards")
@GetMapping
```

그런데 이런 매핑이 없으면 404가 난다.

---

## 3. 실제 원인

문제는 컨트롤러와 템플릿의 URL 기준이 달랐다는 점이었다.

템플릿에서는 `/boards` 기준으로 링크를 작성했다.

```html id="mxn1du"
<a href="/boards/write">글쓰기</a>
```

상세 페이지도 `/boards/{id}` 기준이었다.

```html id="89ceoo"
<a th:href="@{/boards/{id}(id=${board.id})}">상세보기</a>
```

그런데 컨트롤러는 `/boards-page` 기준으로 등록되어 있었다.

```java id="5y2dlu"
@GetMapping("/boards-page")
public String boardsPage(Model model) {
    return "boards/list";
}
```

즉 실제 상태는 이랬다.

```text id="sc68xc"
템플릿 URL
→ /boards
→ /boards/write
→ /boards/{id}

컨트롤러 매핑
→ /boards-page
```

브라우저는 `/boards`로 요청했는데,
서버에는 `/boards-page`만 등록되어 있으니 당연히 404가 발생한 것이다.

핵심 원인은 이거다.

```text id="706x5u"
HTML에서 사용하는 URL과 Controller에서 받는 URL이 서로 달랐다.
```

---

## 4. 잘못된 구조

기존 컨트롤러가 이런 식이었다고 보자.

```java id="67sbkj"
@Controller
public class BoardPageController {

    @GetMapping("/boards-page")
    public String boardsPage(Model model) {
        return "boards/list";
    }

    @GetMapping("/boards-page/{id}")
    public String boardDetail(@PathVariable Long id, Model model) {
        return "boards/detail";
    }
}
```

이 경우 실제로 가능한 주소는 다음과 같다.

```text id="c2kqgo"
/boards-page
/boards-page/1
```

하지만 템플릿은 이렇게 되어 있었다.

```text id="h728wv"
/boards
/boards/1
/boards/write
```

그러면 아무리 `list.html`을 잘 만들어도 `/boards`로는 접근할 수 없다.

---

## 5. 해결 방향

해결 방법은 간단하다.

컨트롤러의 기준 URL을 템플릿과 맞추면 된다.

나는 템플릿을 `/boards` 기준으로 만들었기 때문에,
컨트롤러도 `/boards` 기준으로 수정했다.

```java id="tv53ld"
@Controller
@RequestMapping("/boards")
public class BoardPageController {
}
```

이렇게 하면 이 컨트롤러 안의 모든 메서드는 `/boards` 아래에 묶인다.

```java id="nhnspv"
@GetMapping
public String list() {
    return "boards/list";
}
```

이 메서드는 다음 URL을 처리한다.

```text id="y376xa"
GET /boards
```

```java id="nvzjss"
@GetMapping("/write")
public String writeForm() {
    return "boards/write";
}
```

이 메서드는 다음 URL을 처리한다.

```text id="iyw3sl"
GET /boards/write
```

---

## 6. 수정한 BoardPageController

최종적으로 `board_fe`의 `BoardPageController`는 다음처럼 정리했다.

```java id="2lahma"
package com.board.fe.controller;

import com.board.fe.client.BoardApiClient;
import com.board.fe.dto.BoardCreateRequest;
import com.board.fe.dto.BoardResponse;
import com.board.fe.dto.BoardUpdateRequest;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Controller
@RequestMapping("/boards")
public class BoardPageController {

    private final BoardApiClient boardApiClient;

    public BoardPageController(BoardPageController boardApiClient) {
        this.boardApiClient = boardApiClient;
    }

    @GetMapping
    public String list(Model model) {
        List<BoardResponse> boards = boardApiClient.getBoards();
        model.addAttribute("boards", boards);
        return "boards/list";
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

    @GetMapping("/{id:\\d+}")
    public String detail(@PathVariable Long id, Model model) {
        BoardResponse board = boardApiClient.getBoard(id);
        model.addAttribute("board", board);
        return "boards/detail";
    }

    @GetMapping("/{id:\\d+}/edit")
    public String editForm(@PathVariable Long id, Model model) {
        BoardResponse board = boardApiClient.getBoard(id);
        model.addAttribute("board", board);
        return "boards/edit";
    }

    @PostMapping("/{id:\\d+}/edit")
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

    @PostMapping("/{id:\\d+}/delete")
    public String delete(@PathVariable Long id) {
        boardApiClient.deleteBoard(id);
        return "redirect:/boards";
    }
}
```

다만 위 코드에서 생성자는 실제 코드에서는 이렇게 되어야 한다.

```java id="wpl5r3"
public BoardPageController(BoardApiClient boardApiClient) {
    this.boardApiClient = boardApiClient;
}
```

즉 `BoardPageController`가 아니라 `BoardApiClient`를 주입받아야 한다.

---

## 7. 왜 `{id:\\d+}`를 썼나?

처음에는 상세 페이지를 이렇게 작성할 수도 있다.

```java id="7zxwrq"
@GetMapping("/{id}")
public String detail(@PathVariable Long id, Model model) {
    return "boards/detail";
}
```

이렇게 해도 보통은 동작한다.

하지만 `/boards/write` 같은 경로가 있을 때,
Spring이 `write`를 `{id}`로 해석하려고 시도할 수 있다.

즉 이런 문제가 생길 수 있다.

```text id="fdxjxh"
/boards/write
→ writeForm()으로 가야 함

그런데
/boards/{id}
→ id = "write"로 해석될 가능성 있음
```

물론 메서드 순서나 매핑 우선순위에 따라 괜찮을 수도 있지만,
처음부터 숫자 id만 받도록 제한하는 것이 더 안전하다.

그래서 다음처럼 작성했다.

```java id="2shlx6"
@GetMapping("/{id:\\d+}")
```

의미는 다음과 같다.

```text id="v9p7pq"
{id:\\d+}
→ id 자리에 숫자만 허용
→ /boards/1 가능
→ /boards/10 가능
→ /boards/write 불가능
```

그래서 URL 충돌을 줄일 수 있다.

---

## 8. 템플릿 위치도 확인해야 한다

URL 매핑을 고친 뒤에도 템플릿 위치가 틀리면 또 다른 에러가 난다.

컨트롤러에서 다음처럼 반환한다면:

```java id="cdvjxu"
return "boards/list";
```

Spring Boot + Thymeleaf는 기본적으로 다음 위치에서 파일을 찾는다.

```text id="olcpzu"
src/main/resources/templates/boards/list.html
```

따라서 템플릿은 반드시 다음 위치에 있어야 한다.

```text id="v4yfz2"
board_fe/src/main/resources/templates/boards/list.html
board_fe/src/main/resources/templates/boards/detail.html
board_fe/src/main/resources/templates/boards/write.html
board_fe/src/main/resources/templates/boards/edit.html
```

반환값과 파일 위치의 관계는 다음과 같다.

```text id="lsn2u7"
return "boards/list"
→ templates/boards/list.html

return "boards/detail"
→ templates/boards/detail.html

return "boards/write"
→ templates/boards/write.html

return "boards/edit"
→ templates/boards/edit.html
```

---

## 9. 템플릿 URL도 컨트롤러와 맞춰야 한다

컨트롤러만 `/boards`로 바꿔도, 템플릿 링크가 여전히 `/boards-page`를 보고 있으면 또 꼬인다.

그래서 템플릿에서도 모든 링크를 `/boards` 기준으로 맞췄다.

목록에서 글쓰기 링크:

```html id="bk7esd"
<a href="/boards/write">글쓰기</a>
```

상세보기 링크:

```html id="jbi71p"
<a th:href="@{/boards/{id}(id=${board.id})}">상세보기</a>
```

상세 페이지에서 수정 링크:

```html id="oxk7lj"
<a th:href="@{/boards/{id}/edit(id=${board.id})}">수정</a>
```

삭제 요청:

```html id="lrmu14"
<form th:action="@{/boards/{id}/delete(id=${board.id})}" method="post">
    <button type="submit">삭제</button>
</form>
```

즉 컨트롤러와 템플릿이 같은 URL 체계를 사용해야 한다.

```text id="pmrty5"
Controller
→ /boards 기준

Template
→ /boards 기준
```

---

## 10. 이번 문제를 구분하는 방법

이번 에러는 다음처럼 구분할 수 있다.

### 404 Not Found

```text id="lwylav"
해당 URL을 처리할 Controller 매핑이 없음
```

확인할 것:

```text id="13wpe1"
내가 접속한 주소
@Controller 또는 @RestController의 @RequestMapping
@GetMapping, @PostMapping 경로
템플릿 내부 링크
```

### TemplateInputException

```text id="8eo3qh"
Controller는 찾았지만 반환한 HTML 파일을 못 찾음
```

확인할 것:

```text id="7jg9xk"
return "boards/list";
templates/boards/list.html 파일 존재 여부
파일명 오타
templates 폴더 위치
```

즉 이번 문제는 템플릿 파일이 비어서 생긴 문제가 아니라,
컨트롤러 매핑 자체가 `/boards`에 없어서 생긴 문제였다.

---

## 11. 실행 확인

먼저 `board_api`를 실행한다.

```powershell id="nx2m14"
cd C:\Users\oscbs\OneDrive\Desktop\board\board_api
mvn spring-boot:run
```

`board_api`는 8080에서 실행된다.

```text id="c5vw0g"
http://localhost:8080/boards
```

그다음 `board_fe`를 실행한다.

```powershell id="u1if9g"
cd C:\Users\oscbs\OneDrive\Desktop\board\board_fe
mvn spring-boot:run
```

`board_fe`는 8081에서 실행된다.

```text id="03rd78"
http://localhost:8081/boards
```

이 주소에서 게시글 목록 화면이 나오면 성공이다.

---

## 12. 정리

이번 문제의 핵심은 URL 매핑 불일치였다.

```text id="ih7hep"
템플릿은 /boards로 이동하려고 함
컨트롤러는 /boards-page만 받고 있었음
결과적으로 /boards 요청을 처리할 매핑이 없어 404 발생
```

해결은 다음과 같이 했다.

```text id="sy4nj7"
1. BoardPageController의 기준 경로를 /boards로 수정
2. list, detail, write, edit 경로를 /boards 기준으로 정리
3. {id} 경로는 숫자만 받도록 /{id:\d+} 사용
4. Thymeleaf 템플릿을 src/main/resources/templates/boards 아래에 배치
5. 템플릿 내부 링크도 /boards 기준으로 통일
```

이번 트러블슈팅을 통해 다시 확인한 점은 이거다.

```text id="bs1d7i"
Spring MVC에서는 Controller의 매핑과 템플릿의 URL이 반드시 같은 약속을 바라봐야 한다.
```

한 줄로 정리하면 다음과 같다.

```text id="2iiswx"
Whitelabel 404는 서버가 죽은 것이 아니라, 내가 요청한 URL을 받을 Controller 매핑이 없다는 신호였다.
```
