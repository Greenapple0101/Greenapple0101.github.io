---
title: "[SPRING] 게시글 작성 실패: 프론트와 백엔드 연결 트러블슈팅"
source: "https://velog.io/@yorange50/SPRING-게시글-작성-실패-프론트와-백엔드-연결-트러블슈팅"
published: "2026-04-29T16:33:47.736Z"
tags: ""
backup_date: "2026-05-29T14:52:52.784074"
---

![](https://velog.velcdn.com/images/yorange50/post/9b7de7eb-bdf0-4112-8e74-ceff56cb0b26/image.png)

게시글 작성 버튼을 눌렀는데 브라우저 alert로 다음 메시지가 떴다.

```text
게시글 작성에 실패했습니다.
```

화면만 보면 단순히 작성이 안 된 것처럼 보이지만, 실제로는 **프론트엔드가 백엔드 API 호출 결과를 실패로 판단한 상태**다.

현재 구조는 다음과 같다.

```text
프론트엔드: localhost:5173
백엔드 Spring Boot: localhost:8080
```

즉, 브라우저에서 작성 버튼을 누르면 프론트엔드가 Spring Boot 서버로 POST 요청을 보내야 한다.

---

## 1. 먼저 Network 탭을 확인해야 한다

이런 에러가 나오면 코드부터 고치기 전에 먼저 브라우저 개발자도구를 열어야 한다.

```text
F12 또는 우클릭 → 검사 → Network 탭
```

그리고 작성 버튼을 다시 누른다.

여기서 확인할 것은 세 가지다.

```text
1. /boards 요청이 실제로 나갔는가
2. 상태 코드가 몇 번인가
3. 응답 메시지가 무엇인가
```

상태 코드별로 의미는 대략 이렇게 볼 수 있다.

```text
400: 프론트에서 보낸 JSON 형식이 백엔드가 기대한 형식과 다름
404: 요청 주소가 틀림
500: 백엔드 내부 코드에서 에러 발생
CORS: 프론트와 백엔드 포트가 달라서 브라우저가 요청을 막음
```

---

## 2. 프론트에서 JSON을 제대로 보내는지 확인

게시글 작성은 보통 POST 요청이다.

프론트에서는 백엔드로 데이터를 보낼 때 반드시 JSON 형식으로 변환해서 보내야 한다.

```js
await fetch("http://localhost:8080/boards", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    title,
    author,
    content,
  }),
});
```

여기서 중요한 부분은 이거다.

```js
headers: {
  "Content-Type": "application/json",
}
```

이게 없으면 Spring Boot가 요청 본문을 JSON으로 해석하지 못할 수 있다.

즉, 프론트에서는 데이터를 보냈다고 생각하지만 백엔드 입장에서는 제대로 읽지 못하는 상황이 생긴다.

---

## 3. 백엔드 컨트롤러가 어떤 데이터를 기대하는지 확인

현재 백엔드 컨트롤러가 이런 식이라면:

```java
@PostMapping("/boards")
public Board createBoard(@RequestBody Map<String, String> body) {
    String title = body.get("title");
    return boardService.createBoards(title);
}
```

백엔드는 최소한 이런 JSON을 기대한다.

```json
{
  "title": "지선"
}
```

그런데 프론트에서 다음처럼 보낼 수도 있다.

```json
{
  "title": "지선",
  "author": "지선",
  "content": "지선"
}
```

이 자체가 문제는 아니다.
다만 백엔드 코드가 `title`만 꺼내고 있다면 `author`, `content`는 무시된다.

게시글에 제목, 작성자, 내용을 모두 저장하려면 백엔드의 Board 객체와 Service 로직도 그에 맞게 바뀌어야 한다.

---

## 4. CORS 문제도 확인해야 한다

현재 프론트와 백엔드는 포트가 다르다.

```text
프론트: localhost:5173
백엔드: localhost:8080
```

브라우저 입장에서는 서로 다른 출처로 본다.

그래서 Spring Boot 쪽에서 CORS를 허용해줘야 한다.

간단히 테스트할 때는 컨트롤러에 다음을 붙일 수 있다.

```java
@CrossOrigin(origins = "http://localhost:5173")
@RestController
public class BoardController {
}
```

이 설정은 `localhost:5173`에서 오는 요청을 허용한다는 뜻이다.

---

## 5. Service 반환 타입도 맞춰야 한다

Controller에서 `Board`를 반환하도록 작성했다면 Service도 `Board`를 반환해야 한다.

예를 들어 Controller가 이렇게 되어 있는데:

```java
public Board createBoard(@RequestBody Map<String, String> body) {
    String title = body.get("title");
    return boardService.createBoards(title);
}
```

Service가 이렇게 되어 있으면 문제가 생긴다.

```java
public String createBoards(String title) {
    return "생성됨: " + title;
}
```

Controller는 `Board`를 기대하는데 Service는 `String`을 반환하고 있기 때문이다.

따라서 Service도 Board 객체를 반환하도록 맞춰야 한다.

```java
public Board createBoards(String title) {
    return new Board(1L, title);
}
```

---

## 정리

게시글 작성 실패는 단순히 버튼이 안 되는 문제가 아니다.

프론트에서 백엔드로 POST 요청을 보내고, 백엔드는 JSON을 받아서 객체로 만들고, 다시 응답을 돌려줘야 한다.

이번 트러블슈팅의 핵심은 다음과 같다.

```text
1. Network 탭에서 실제 요청과 상태 코드를 확인한다.
2. 프론트 fetch에 Content-Type: application/json이 있는지 확인한다.
3. 백엔드 @RequestBody가 기대하는 JSON 구조를 확인한다.
4. 프론트와 백엔드 포트가 다르면 CORS 설정을 확인한다.
5. Controller와 Service의 반환 타입이 맞는지 확인한다.
```

결국 이 에러는 화면의 문제가 아니라, **프론트와 백엔드 사이의 데이터 전달 규칙이 아직 정확히 맞지 않은 상태**라고 볼 수 있다.
