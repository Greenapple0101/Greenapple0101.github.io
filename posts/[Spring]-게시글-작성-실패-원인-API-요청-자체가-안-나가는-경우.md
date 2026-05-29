---
title: "[SPRING] 게시글 작성 실패 원인: API 요청 자체가 안 나가는 경우"
source: "https://velog.io/@yorange50/SPRING-게시글-작성-실패-원인-API-요청-자체가-안-나가는-경우"
published: "2026-04-29T16:42:39.920Z"
tags: ""
backup_date: "2026-05-29T14:52:52.783799"
---

![](https://velog.velcdn.com/images/yorange50/post/d5412c4e-51a1-418d-8d76-c5786d01f1c0/image.png)

게시글 작성 버튼을 눌렀는데 실패 alert가 뜨고, Network 탭을 확인해봤다.

결과는 아래와 같았다.

```text
Fetch/XHR 요청 없음
→ /boards POST 요청 자체가 안 보임
```

보이는 건 전부 `websocket`이고, 우리가 기대한 API 호출은 하나도 없다.

---

## 문제의 핵심

```text
프론트에서 백엔드로 요청 자체가 안 나가고 있음
```

즉,

```text
Spring 문제가 아니라
→ 프론트 코드 문제
```

---

## 왜 이런 일이 생기냐

이 상황은 딱 3가지 중 하나다.

---

## 1. 버튼 클릭 이벤트가 안 걸려 있음

가장 흔한 케이스

예를 들어:

```tsx
<button>작성</button>
```

이렇게만 되어 있으면 아무 일도 안 일어난다.

반드시 이벤트가 있어야 한다.

```tsx
<button onClick={handleSubmit}>작성</button>
```

---

## 2. handleSubmit 안에서 fetch를 안 하고 있음

버튼은 눌리는데 실제 API 호출 코드가 없는 경우

```ts
const handleSubmit = () => {
  alert("작성 시도"); // 이건 뜨는데
  // fetch 없음 → Network에 안 찍힘
};
```

---

## 3. fetch 에러 전에 코드가 끊김

예를 들어 이런 경우:

```ts
const handleSubmit = () => {
  if (!title) {
    alert("제목 없음");
    return;
  }

  // 여기 도달 못하면 fetch 안 실행됨
};
```

또는

```ts
try {
  fetch(...);
} catch (e) {
  alert("실패");
}
```

→ fetch 자체는 비동기라 try-catch로 안 잡힘
→ 실제 에러는 `.then / catch`에서 처리해야 함

---

## 지금 상황 결론

```text
백엔드 문제 아님
CORS 문제 아님
JSON 문제 아님

→ 프론트에서 fetch 호출이 안 되고 있음
```

---

## 바로 확인하는 방법 (가장 빠름)

handleSubmit에 이거 넣어봐라

```ts
const handleSubmit = () => {
  console.log("클릭됨");
};
```

→ 콘솔에 안 찍히면: 이벤트 연결 문제
→ 찍히면: 그 다음 fetch 확인

---

## 정상 코드 예시 (최소 형태)

```ts
const handleSubmit = async () => {
  console.log("요청 시작");

  await fetch("http://localhost:8080/boards", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      title: "테스트",
    }),
  });

  console.log("요청 끝");
};
```

이걸 넣고 버튼 누르면

```text
Network 탭에 /boards 생겨야 정상
```

---

## 한 줄 핵심

```text
Network에 요청이 없으면
→ 서버 문제 아니다
→ 100% 프론트 이벤트 or fetch 호출 문제다
```

---

원하면
지금 프론트 코드(handleSubmit, 버튼 부분) 보여주면
딱 어디서 끊기는지 정확하게 찍어줄게
