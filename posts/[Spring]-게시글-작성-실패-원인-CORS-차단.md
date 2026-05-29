---
title: "[SPRING] 게시글 작성 실패 원인: CORS 차단"
source: "https://velog.io/@yorange50/SPRING-게시글-작성-실패-원인-CORS-차단"
published: "2026-04-29T16:50:00.396Z"
tags: ""
backup_date: "2026-05-29T14:52:52.783565"
---

![](https://velog.velcdn.com/images/yorange50/post/0fcf5a63-c1f9-41fc-a2c2-3e6d53ae107f/image.png)

게시글 작성 버튼을 눌렀을 때 프론트에서는 다음 alert가 떴다.

```text
게시글 작성에 실패했습니다.
```

처음에는 백엔드 작성 로직 문제라고 생각할 수 있지만, 확인 결과 원인은 **브라우저의 CORS 차단**이었다.

현재 구조는 다음과 같다.

```text
프론트엔드: http://localhost:5173
백엔드: http://localhost:8080
```

둘 다 localhost이지만 포트가 다르다. 브라우저 기준으로는 서로 다른 출처다.

```text
localhost:5173
localhost:8080
```

포트가 다르면 브라우저는 이를 교차 출처 요청으로 판단한다.

---

## 확인한 내용

백엔드 서버 자체는 정상적으로 떠 있었다.

```text
8080 포트 리슨 확인
```

그리고 서버에 직접 요청했을 때도 정상 응답이 왔다.

```text
GET /boards 정상
POST /boards 정상
POST /boards 응답: 200 + JSON
```

즉, Spring Boot의 게시글 작성 로직 자체가 실패한 것은 아니었다.

문제는 브라우저에서 프론트가 백엔드로 요청을 보낼 때 발생했다.

---

## CORS가 문제였던 이유

브라우저는 다른 출처로 요청을 보낼 때, 백엔드가 해당 요청을 허용하는지 확인한다.

이때 백엔드 응답 헤더에 다음과 같은 값이 있어야 한다.

```text
Access-Control-Allow-Origin
```

그런데 현재 백엔드 응답에는 이 헤더가 없었다.

또한 POST 요청 전에 브라우저가 먼저 보내는 확인 요청인 `OPTIONS /boards`, 즉 preflight 요청도 응답은 200이었지만 CORS 허용 헤더가 없었다.

그래서 브라우저가 실제 요청을 막았다.

정리하면 다음과 같다.

```text
프론트에서 POST 요청 시도
→ 브라우저가 OPTIONS /boards preflight 요청
→ 백엔드는 200 응답
→ 하지만 Access-Control-Allow-Origin 헤더 없음
→ 브라우저가 CORS 정책 위반으로 차단
→ 프론트에서는 게시글 작성 실패 처리
```

---

## 중요한 점

CORS 에러는 서버가 완전히 죽었을 때 나는 에러가 아니다.

이번 경우 백엔드는 살아 있었다.

서버에 직접 요청하면 정상이다.

하지만 브라우저는 보안 정책 때문에 요청을 막는다.

그래서 터미널이나 Postman에서는 성공하는데, 프론트 화면에서는 실패할 수 있다.

---

## 시점에 따라 에러가 섞여 보인 이유

아까는 백엔드 서버가 안 떠 있던 상태도 있었다.

그때는 연결 자체가 실패했을 가능성이 있다.

이후 백엔드를 다시 띄운 상태에서는 서버 직접 호출은 정상인데, 브라우저에서만 실패했다.

즉 이번 문제는 두 가지가 시간차로 섞여 보였을 수 있다.

```text
1차: 백엔드 서버 미실행으로 연결 실패
2차: 백엔드 실행 후 CORS 차단
```

---

## 결론

이번 게시글 작성 실패의 핵심 원인은 백엔드 작성 로직이 아니라 **브라우저 CORS 차단**이었다.

```text
서버는 정상
GET /boards 정상
POST /boards 정상
하지만 브라우저 요청은 CORS 정책 때문에 차단
```

따라서 해결 방향은 Spring Boot에서 `localhost:5173` 출처를 허용하도록 CORS 설정을 추가하는 것이다.
![](https://velog.velcdn.com/images/yorange50/post/7dc9651b-c5f6-4768-b1ea-7f89962f6e7c/image.png)
어노테이션 추가함