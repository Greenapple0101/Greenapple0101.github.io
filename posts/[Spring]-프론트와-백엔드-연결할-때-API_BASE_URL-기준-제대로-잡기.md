---
title: "[SPRING] 프론트와 백엔드 연결할 때 API_BASE_URL 기준 제대로 잡기"
source: "https://velog.io/@yorange50/SPRING-프론트와-백엔드-연결할-때-APIBASEURL-기준-제대로-잡기"
published: "2026-04-29T14:26:47.349Z"
tags: ""
backup_date: "2026-05-29T14:52:52.785595"
---

Spring Boot로 API를 만들고 프론트에서 연결할 때 가장 많이 헷갈리는 부분이 바로 **API_BASE_URL 설정**이다.
처음에는 단순해 보이는데, 경로가 조금만 바뀌어도 404가 나면서 막히기 쉽다.

이번 글에서는 이 기준을 정확하게 정리한다.

---

## 1. 현재 Spring API 구조

```java
@RestController
@RequestMapping
public class BoardController {

    @GetMapping("/boards")
```

이 경우 실제 API 주소는 다음과 같다.

```
http://localhost:8080/boards
```

---

## 2. 프론트에서 API_BASE_URL 설정

이 구조라면 프론트에서는 이렇게 잡아야 한다.

```ts
const API_BASE_URL = 'http://localhost:8080';
```

그리고 실제 호출은 아래처럼 한다.

```ts
fetch(`${API_BASE_URL}/boards`)
```

---

## 3. 만약 /api prefix가 붙는 경우

Spring 코드가 아래처럼 바뀌면

```java
@RequestMapping("/api")
@GetMapping("/boards")
```

실제 API 주소는 이렇게 된다.

```
http://localhost:8080/api/boards
```

이때는 프론트도 같이 바뀌어야 한다.

```ts
const API_BASE_URL = 'http://localhost:8080/api';
```

```ts
fetch(`${API_BASE_URL}/boards`)
```

---

## 4. 핵심 개념 정리

중요한 기준은 하나다.

* API_BASE_URL → 공통 prefix만 작성
* 실제 API 경로 → fetch에서 붙인다

즉 구조는 항상 이렇게 나뉜다.

```
[BASE_URL] + [/boards]
```

---

## 5. 반드시 확인해야 할 것 (404 방지)

### 1) 브라우저로 직접 확인

```
http://localhost:8080/boards
```

여기서 데이터가 나오면 백엔드는 정상이다.

### 2) 프론트 요청 확인

```ts
fetch('http://localhost:8080/boards')
```

---

## 6. 가장 많이 하는 실수

* API_BASE_URL에 `/boards`까지 포함시킴
* 그리고 fetch에서도 `/boards`를 또 붙임

결과:

```
http://localhost:8080/boards/boards
```

→ 404 발생

---

## 7. 결론

프론트와 백엔드를 연결할 때 중요한 건 단 하나다.

```
BASE_URL은 "공통 경로까지만"
```

이 기준만 정확히 잡으면
경로 문제로 막히는 일은 거의 사라진다.
