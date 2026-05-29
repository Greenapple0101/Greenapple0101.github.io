---
title: "[SPRING] Postman 사용법"
source: "https://velog.io/@yorange50/SPRING-Postman-사용법"
published: "2026-04-29T00:41:49.052Z"
tags: ""
backup_date: "2026-05-29T14:52:52.786920"
---

![](https://velog.velcdn.com/images/yorange50/post/39c39da8-bf3b-4bfb-8724-953f515cce97/image.png)
일단 포스트맨을 앱으로 깐다
![](https://velog.velcdn.com/images/yorange50/post/99f3da17-4c4d-45da-92e5-5d0770c76d35/image.png)
my collection + 버튼을 누르고 만들어놓은 api를 대입하면 밑에 성공적인 호출이 생긴다, 반면 밑은 오류 아직 postapi를 안 만들었기 때문이다
![](https://velog.velcdn.com/images/yorange50/post/97cb0db9-850a-4307-aa1d-311b5d98c9c9/image.png)

## 문제 상황

Spring Boot로 간단한 게시판 API를 만들고 Postman으로 테스트를 진행했다.

### GET 요청

```http
GET http://localhost:8080/boards
```

응답 정상

```json
["게시글1","게시글2","게시글3"]
```

---

### POST 요청

```http
POST http://localhost:8080/boards
```

응답

```json
{
  "timestamp": "2026-04-29T00:38:57.413Z",
  "status": 405,
  "error": "Method Not Allowed",
  "path": "/boards"
}
```

---

## 원인 분석

405 에러는 다음 의미를 가진다

* URL은 존재함
* 하지만 해당 HTTP Method는 허용되지 않음

즉

```text
/boards 경로는 있음
하지만 POST 요청을 처리하는 코드가 없음
```

현재 Controller에는 GET만 존재하는 상태

```java
@GetMapping("/boards")
public List<String> getBoards() {
    return List.of("게시글1", "게시글2", "게시글3");
}
```

---

## 해결 방법

POST 요청을 처리하는 API를 추가해야 한다

```java
@PostMapping("/boards")
public String createBoard(@RequestBody Map<String, String> body) {
    String title = body.get("title");
    return "생성됨: " + title;
}
```

---

## 필요한 import

```java
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import java.util.Map;
```

---

## Postman 설정

* Method: POST
* URL: [http://localhost:8080/boards](http://localhost:8080/boards)

### Body 설정

* raw 선택
* JSON 선택

```json
{
  "title": "테스트 글"
}
```

---

## 결과

```text
생성됨: 테스트 글
```

---

## 정리

* 405 에러는 "경로는 맞지만 HTTP Method가 틀린 경우"
* Spring에서는 각 Method마다 별도 매핑이 필요
* GET → @GetMapping
* POST → @PostMapping

---

## 다음 단계

* POST 데이터를 List에 저장하도록 로직 확장
* GET 요청 시 실제 추가된 데이터 반환
* PUT, DELETE까지 확장하여 CRUD 완성

---

이 글 하나로 면접에서 “HTTP 상태코드 이해 + Spring 매핑 구조” 설명 가능하다.
