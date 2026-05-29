---
title: "[SPRING] Controller랑 Service는 왜 나눌까?"
source: "https://velog.io/@yorange50/SPRING-Controller랑-Service는-왜-나눌까"
published: "2026-04-28T10:09:54.123Z"
tags: "Spring"
backup_date: "2026-05-29T14:52:52.787996"
---

![](https://velog.velcdn.com/images/yorange50/post/bedc6599-0cf9-4e47-a522-71e8e327c007/image.png)


스프링을 처음 시작하면 가장 헷갈리는 구조가 바로 **Controller / Service 분리**다
코드를 보면 둘이 연결되어 있는데, 왜 굳이 나누는지 감이 잘 안 온다

오늘은 이걸 아주 단순하게 이해해보자

---

## 전체 흐름부터 보기

스프링에서 요청은 이렇게 흐른다

클라이언트 → Controller → Service → 결과 반환

이 흐름 하나만 기억해도 절반은 이해한 거다

---

## Controller는 뭐하는 애냐

```java
@RestController
@RequestMapping("/boards")
public class BoardController {
```

Controller는 **요청을 받는 입구**다

* URL을 통해 요청을 받는다
* 어떤 API인지 정의한다
* 실제 로직은 안 한다

```java
@GetMapping("/boards")
public List<String> getBoards(){
    return boardService.getBoards();
}
```

여기서 중요한 포인트

Controller는 직접 일을 안 한다
→ 그냥 Service한테 시킨다

---

## Service는 뭐하는 애냐

```java
@Service
public class BoardService {
```

Service는 **진짜 일을 하는 곳**이다

```java
public List<String> getBoards(){
    return List.of("게시글1", "게시글2", "게시글3");
}
```

* 데이터 만들고
* 가공하고
* 계산하고

→ 실제 로직 담당

---

## 둘은 어떻게 연결되냐

```java
private final BoardService boardService;

public BoardController(BoardService boardService){
    this.boardService = boardService;
}
```

이 부분이 핵심이다

스프링이 BoardService를 만들어서
Controller에 자동으로 넣어준다

이걸 **의존성 주입(DI)**라고 한다

---

## this는 뭐냐

```java
this.boardService = boardService;
```

의미는 딱 하나다

내가 가진 boardService 변수에
밖에서 받은 boardService를 넣는다

---

## 왜 굳이 나누냐

이게 제일 중요하다

### 나누지 않으면

* Controller에 로직 다 들어감
* 코드 길어짐
* 수정할 때 다 건드려야 함

### 나누면

* Controller → 요청만 담당
* Service → 로직만 담당

→ 역할이 분리됨
→ 유지보수 쉬움
→ 협업 쉬움

---

## 한 줄 정리

Controller는 요청을 받는 입구
Service는 실제 일을 하는 곳

또는

Controller = 지휘자
Service = 일하는 사람

---

이 구조가 이해되면 다음 단계로 자연스럽게 넘어간다

* POST API 만들기
* DTO 추가하기
* DB 연결하기

여기까지 이어지면 진짜 백엔드 구조가 보이기 시작한다
