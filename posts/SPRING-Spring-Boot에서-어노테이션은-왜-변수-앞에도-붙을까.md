---
title: "[SPRING] Spring Boot에서 어노테이션은 왜 변수 앞에도 붙을까?"
source: "https://velog.io/@yorange50/SPRING-Spring-Boot에서-어노테이션은-왜-변수-앞에도-붙을까"
published: "2026-05-04T00:58:03.559Z"
tags: "Spring"
backup_date: "2026-05-29T14:52:52.779539"
---

Spring Boot로 게시판 API를 만들다 보면 처음에는 어노테이션이 낯설게 느껴진다. 클래스 위에 붙는 것도 있고, 메서드 위에 붙는 것도 있고, 심지어 변수처럼 보이는 곳 앞에도 붙는다.

예를 들어 이런 코드가 있다.

```java id="mk0pwi"
@GetMapping("/{id}")
public Board getBoard(@PathVariable Long id){
    return boardService.getBoard(id);
}
```

처음 보면 이런 생각이 든다.

“`@GetMapping`은 메서드 위에 붙는 건 알겠는데, `@PathVariable`은 왜 변수 선언 앞에 있지?”

그런데 정확히 말하면 `@PathVariable`은 일반 변수 앞에 붙은 것이 아니라 **메서드 파라미터에 붙은 어노테이션**이다.

---

## 어노테이션이란?

어노테이션은 자바 코드에 붙이는 **설명 표시**라고 볼 수 있다.

자바 코드 자체의 흐름을 바꾸는 일반 명령문이라기보다는, Spring에게 특정 정보를 알려주는 표시다.

예를 들어 다음 코드를 보자.

```java id="og05u5"
@GetMapping("/{id}")
```

이 코드는 Spring에게 이렇게 알려준다.

```text id="arrp9t"
이 메서드는 GET 요청을 처리한다.
그리고 URL은 /{id} 형태다.
```

즉, 어노테이션은 Spring이 코드를 해석할 수 있도록 붙이는 메타 정보다.

---

## @GetMapping("/{id}")의 의미

게시글 하나를 조회하는 API를 만든다고 해보자.

보통 게시글 목록은 다음과 같이 요청한다.

```text id="uyoxlo"
GET /boards
```

게시글 하나를 조회할 때는 id를 붙여서 요청한다.

```text id="b60t4m"
GET /boards/1
GET /boards/2
GET /boards/3
```

이때 컨트롤러에 공통 주소가 `/boards`로 잡혀 있다면, 메서드에서는 그 뒤에 붙는 id 부분만 받으면 된다.

```java id="ws1mlm"
@GetMapping("/{id}")
public Board getBoard(@PathVariable Long id){
    return boardService.getBoard(id);
}
```

여기서

```java id="84oogv"
@GetMapping("/{id}")
```

는 URL 경로에서 어떤 값 하나가 들어올 수 있다는 뜻이다.

예를 들어 요청이 이렇게 들어오면,

```text id="sww1eg"
GET /boards/3
```

Spring은 URL을 이렇게 해석한다.

```text id="tbixg0"
/boards/{id}
        ↓
        3
```

즉, `{id}` 자리에 들어온 값은 `3`이다.

---

## @PathVariable Long id의 의미

그럼 URL에서 꺼낸 `3`을 자바 코드 안에서는 어떻게 사용할까?

이때 사용하는 것이 `@PathVariable`이다.

```java id="lod7yp"
@PathVariable Long id
```

이 코드는 Spring에게 이렇게 알려준다.

```text id="tbg0si"
URL 경로에 있는 id 값을
Long 타입 변수 id에 넣어라.
```

즉, 다음 요청이 들어오면,

```text id="77qzkp"
GET /boards/3
```

Spring은 내부적으로 이런 식으로 처리한다.

```text id="0q53uv"
{id} = 3
Long id = 3L
boardService.getBoard(3L)
```

그래서 전체 코드는 이렇게 해석할 수 있다.

```java id="n79f89"
@GetMapping("/{id}")
public Board getBoard(@PathVariable Long id){
    return boardService.getBoard(id);
}
```

의미:

```text id="30mh7z"
GET /boards/3 요청이 들어오면
URL의 3을 id 변수에 넣고
boardService.getBoard(id)를 실행한다.
```

---

## 왜 그냥 Long id라고 쓰면 안 될까?

처음에는 이렇게 생각할 수 있다.

```java id="5l2r73"
@GetMapping("/{id}")
public Board getBoard(Long id){
    return boardService.getBoard(id);
}
```

“어차피 URL에도 id가 있고, 변수 이름도 id인데 Spring이 알아서 넣어주면 안 되나?”

하지만 Spring 입장에서는 메서드 파라미터가 어디에서 온 값인지 알아야 한다.

HTTP 요청에는 값을 보낼 수 있는 위치가 여러 개 있다.

```text id="zy9b72"
URL 경로
쿼리 파라미터
요청 본문
헤더
쿠키
```

예를 들어 `id`라는 값이 URL 경로에 있을 수도 있고,

```text id="vn6bdc"
/boards/3
```

쿼리 파라미터에 있을 수도 있다.

```text id="upnnvn"
/boards?id=3
```

JSON 요청 본문 안에 있을 수도 있다.

```json id="sbuf3r"
{
  "id": 3
}
```

그래서 Spring에게 명확하게 알려줘야 한다.

```java id="4swqv0"
@PathVariable Long id
```

이 말은:

```text id="iqhxgd"
이 id는 URL 경로에서 꺼내라.
```

라는 뜻이다.

---

## @PathVariable 이름과 URL 변수 이름

보통은 URL에 적은 이름과 파라미터 이름을 같게 쓴다.

```java id="mb8f2u"
@GetMapping("/{id}")
public Board getBoard(@PathVariable Long id){
    return boardService.getBoard(id);
}
```

여기서는 둘 다 `id`다.

```text id="i1x2w8"
URL 변수 이름: {id}
자바 파라미터 이름: id
```

그래서 Spring이 자연스럽게 연결할 수 있다.

만약 이름을 다르게 쓰고 싶다면 이렇게 명시할 수 있다.

```java id="gvj5aj"
@GetMapping("/{id}")
public Board getBoard(@PathVariable("id") Long boardId){
    return boardService.getBoard(boardId);
}
```

여기서는 URL에서는 `{id}`라고 받고, 자바 코드에서는 `boardId`라는 이름으로 사용한다.

```text id="pwz0po"
GET /boards/3
{id} = 3
Long boardId = 3L
```

---

## 비슷한 어노테이션들

Spring Controller에서는 요청 데이터를 꺼내기 위해 여러 어노테이션을 사용한다.

대표적으로 다음 세 가지가 자주 나온다.

---

## 1. @PathVariable

`@PathVariable`은 URL 경로에서 값을 꺼낸다.

```java id="y4e2cr"
@GetMapping("/boards/{id}")
public Board getBoard(@PathVariable Long id){
    return boardService.getBoard(id);
}
```

요청:

```text id="nt4zfm"
GET /boards/1
```

의미:

```text id="cwtfa6"
URL 경로의 1을 id에 넣는다.
```

보통 특정 게시글, 특정 회원, 특정 상품처럼 **하나의 자원을 id로 조회할 때** 많이 사용한다.

```text id="8o848k"
/boards/1
/users/10
/products/7
```

---

## 2. @RequestParam

`@RequestParam`은 쿼리 파라미터에서 값을 꺼낸다.

```java id="y4n1pd"
@GetMapping("/boards")
public List<Board> searchBoards(@RequestParam String author){
    return boardService.searchByAuthor(author);
}
```

요청:

```text id="su718n"
GET /boards?author=kim
```

의미:

```text id="8ho33r"
author=kim 값을 String author 변수에 넣는다.
```

보통 검색, 필터링, 정렬, 페이지 번호처럼 선택 조건을 보낼 때 사용한다.

```text id="st8z7u"
/boards?author=kim
/boards?page=1
/boards?keyword=spring
/products?category=book
```

---

## 3. @RequestBody

`@RequestBody`는 요청 본문에 담긴 JSON 데이터를 객체로 바꿔준다.

```java id="miu4jy"
@PostMapping("/boards")
public Board createBoard(@RequestBody Board board){
    return boardService.createBoard(board);
}
```

요청 본문:

```json id="enri96"
{
  "title": "제목",
  "content": "내용",
  "author": "작성자"
}
```

의미:

```text id="40pdvb"
JSON 데이터를 Board 객체로 변환해서 board 변수에 넣는다.
```

보통 게시글 생성, 회원가입, 로그인, 수정 요청처럼 여러 값을 한 번에 보낼 때 사용한다.

---

## 셋의 차이 정리

```text id="6ba1l6"
@PathVariable
URL 경로에서 값을 꺼낸다.
예: /boards/1

@RequestParam
URL 뒤의 쿼리 문자열에서 값을 꺼낸다.
예: /boards?author=kim

@RequestBody
요청 본문 JSON에서 값을 꺼낸다.
예: {"title": "제목", "content": "내용"}
```

게시판 API에 적용하면 이렇게 볼 수 있다.

```java id="pf4mcz"
@GetMapping("/boards/{id}")
public Board getBoard(@PathVariable Long id)
```

특정 게시글 조회

```java id="dx3ktj"
@GetMapping("/boards?author=kim")
```

작성자 기준 검색

```java id="qy7qye"
@PostMapping("/boards")
public Board createBoard(@RequestBody Board board)
```

게시글 생성

---

## 전체 흐름으로 이해하기

게시글 상세 조회 API를 다시 보면 다음과 같다.

```java id="dd9jad"
@GetMapping("/{id}")
public Board getBoard(@PathVariable Long id){
    return boardService.getBoard(id);
}
```

이 코드는 단순히 메서드 하나가 아니다.

HTTP 요청이 들어오면 Spring이 다음 순서로 처리한다.

```text id="oy5ryk"
1. 사용자가 GET /boards/3 요청을 보낸다.

2. Spring이 /boards/{id}와 매칭되는 메서드를 찾는다.

3. {id} 자리에 들어온 3을 꺼낸다.

4. @PathVariable Long id에 3을 넣는다.

5. getBoard(3L) 메서드를 실행한다.

6. boardService.getBoard(3L)을 호출한다.

7. id가 3인 게시글을 찾아서 반환한다.
```

그래서 `@PathVariable Long id`는 단순한 변수 선언이 아니라, HTTP 요청의 값을 자바 메서드 안으로 가져오는 연결 지점이다.

---

## 정리

처음에는 어노테이션이 변수 앞에 붙어 있어서 어색해 보일 수 있다.

하지만 정확히 보면 `@PathVariable`은 변수 앞에 붙은 것이 아니라, **메서드 파라미터에 붙은 어노테이션**이다.

```java id="e0j2rx"
public Board getBoard(@PathVariable Long id)
```

이 코드는 Spring에게 이렇게 말한다.

```text id="s0mvay"
URL 경로에 있는 id 값을
Long 타입 id 파라미터에 넣어줘.
```

`@GetMapping("/{id}")`는 요청 주소를 정하고, `@PathVariable Long id`는 그 주소 안의 값을 자바 변수로 받아온다.

한 줄로 정리하면 다음과 같다.

```text id="w51hhb"
@GetMapping("/{id}") = /boards/3 같은 요청을 받는 문
@PathVariable Long id = 그 3을 꺼내서 id 변수에 넣는 통로
```

Spring Boot에서 어노테이션은 단순 장식이 아니다.
Spring이 HTTP 요청을 자바 코드와 연결할 수 있게 도와주는 중요한 표시다.
