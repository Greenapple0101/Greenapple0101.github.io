---
title: "[SPRING] Postman이 코드를 바꾸는 걸까?"
source: "https://velog.io/@yorange50/SPRING-POST-요청에서-null이-나온-이유는-뭘까"
published: "2026-04-29T01:58:47.799Z"
tags: ""
backup_date: "2026-05-29T14:52:52.786316"
---

![](https://velog.velcdn.com/images/yorange50/post/80e2a306-f8db-452d-b3a4-4c61bf89947c/image.png)
json 포스트맨에서 고치고
![](https://velog.velcdn.com/images/yorange50/post/5a33af42-3139-4c9f-a61a-8e929f2cd125/image.png)


GET 요청으로 게시글 목록을 조회하는 것까지는 성공했다.

POST API를 테스트하면서 한 가지 헷갈리는 순간이 있었다.

Postman에서 JSON을 바꾸니까 결과가 달라졌다.

예를 들어 처음에는 이런 요청을 보냈다.

```json
{
  "name": "테스트"
}
```

응답은 이렇게 나왔다.

```text
생성됨:null
```

그런데 JSON을 이렇게 바꾸니까

```json
{
  "title": "테스트 글"
}
```

응답이 정상으로 바뀌었다.

```text
생성됨:테스트 글
```

이 순간 이런 생각이 들 수 있다.

```text
Postman이 코드를 바꾼 건가?
```

---

## 결론부터

Postman은 코드를 절대 바꾸지 않는다.

---

## 역할 구분

백엔드에서는 역할이 명확하게 나뉜다.

### 1. Spring 코드

```java
@PostMapping("/boards")
public String createBoard(@RequestBody Map<String, String> body){
    String title = body.get("title");
    return boardService.createBoards(title);
}
```

이 코드는 서버가 어떤 데이터를 받을지 정의한다.

```text
"title"이라는 키를 가진 값을 받아라
```

---

### 2. Postman

Postman은 단순히 데이터를 보내는 역할이다.

```json
{
  "title": "테스트 글"
}
```

이건 서버에 전달되는 요청일 뿐이다.

---

## 왜 결과가 달라졌을까

핵심은 이 한 줄이다.

```java
body.get("title");
```

서버는 `"title"`이라는 키를 찾는다.

---

### 잘못된 요청

```json
{
  "name": "테스트"
}
```

```text
"title"이 없음 → null
```

---

### 올바른 요청

```json
{
  "title": "테스트 글"
}
```

```text
"title" 있음 → 정상 값
```

---

## 흐름 정리

```text
코드 → 어떤 데이터를 받을지 정의
Postman → 실제 데이터를 보냄
서버 → 그 데이터를 읽어서 처리
```

즉,

```text
코드는 그대로
↓
보내는 데이터만 바뀜
↓
결과가 달라짐
```

---

## 한 줄 정리

Postman은 코드를 바꾸는 도구가 아니라,
코드가 제대로 동작하는지 확인하는 테스트 도구다.

---

이걸 이해하면

```text
요청(Request) ↔ 서버 처리 ↔ 응답(Response)
```

이 흐름이 명확해진다.

이 단계가 잡히면 이후 API 설계가 훨씬 쉬워진다.
