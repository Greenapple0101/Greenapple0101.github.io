---
title: "[Spring] 브라우저 → FE → API → DB 흐름으로 이해하는 서버 구조"
source: "https://velog.io/@yorange50/Spring-브라우저-FE-API-DB-흐름으로-이해하는-서버-구조"
published: "2026-05-07T09:08:05.002Z"
tags: ""
backup_date: "2026-05-29T14:52:52.769099"
---

이번에 정리할 핵심은 이것이다.

```text
브라우저는 board_fe를 본다.
board_fe는 board_api를 호출한다.
board_api는 DB를 다룬다.
```

즉, 사용자가 브라우저에서 접속하는 서버와 실제 데이터를 처리하는 서버가 분리되어 있다.

```text
브라우저
→ board_fe : 화면 담당
→ board_api : CRUD API 담당
→ DB : 데이터 저장
```

처음에는 이 구조가 복잡해 보일 수 있다.
그냥 하나의 Spring Boot 프로젝트에서 화면도 띄우고 DB도 붙이면 되지 않나 싶다.

하지만 FE 서버와 API 서버를 나누면 역할이 명확해진다.

---

# 1. 전체 구조

현재 구조는 이렇게 볼 수 있다.

```text
브라우저
  ↓
board_fe 서버
  ↓ JSON 통신
board_api 서버
  ↓
DB
```

각각의 역할은 다르다.

```text
브라우저
사용자가 보는 화면

board_fe
HTML 화면 반환
사용자 입력 받기
API 서버 호출

board_api
게시글 CRUD 처리
비즈니스 로직 처리
DB 접근

DB
게시글 데이터 저장
```

즉, 브라우저 입장에서는 `board_fe`가 서비스의 입구다.

---

# 2. 브라우저 입장에서 8081은 보이고, 8080은 안 보인다

예를 들어 서버가 이렇게 떠 있다고 하자.

```properties
board_fe  = http://localhost:8081
board_api = http://localhost:8080
```

브라우저 사용자는 보통 `8081`로 접속한다.

```text
http://localhost:8081/boards
```

그러면 `board_fe`가 HTML 화면을 내려준다.

하지만 브라우저가 직접 `8080` API 서버에 접근하는 구조는 아니다.

```text
브라우저
→ 8081 board_fe
→ 8080 board_api
```

이렇게 되면 장점이 있다.

```text
API 서버를 브라우저에 직접 노출하지 않아도 된다.
화면 흐름은 FE 서버가 관리한다.
데이터 처리는 API 서버가 담당한다.
```

즉, 브라우저 입장에서는 FE 서버만 보이고, API 서버는 뒤에서 조용히 일하는 구조가 된다.

---

# 3. FE와 API 사이에서는 JSON으로 통신한다

`board_fe`는 HTML을 담당한다.

예를 들어 목록 페이지를 요청하면 FE Controller가 이런 식으로 처리한다.

```java
@GetMapping("/boards")
public String list(Model model) {
    model.addAttribute("boards", boardService.findAll());
    return "list";
}
```

여기서 `boardService.findAll()`은 결국 `board_api`를 호출한다.

```text
board_fe Controller
→ board_fe Service
→ BoardApiClient
→ board_api GET /boards
```

`board_api`는 게시글 목록을 JSON으로 응답한다.

```json
[
  {
    "id": 1,
    "title": "첫 번째 글",
    "author": "kim",
    "content": "내용"
  }
]
```

그러면 `board_fe`는 이 JSON을 받아서 Thymeleaf 화면에 넣는다.

```html
<tr th:each="board : ${boards}">
    <td th:text="${board.id}"></td>
    <td th:text="${board.title}"></td>
    <td th:text="${board.author}"></td>
</tr>
```

즉, 흐름은 이렇다.

```text
API는 JSON을 준다.
FE는 JSON을 받아 HTML로 보여준다.
```

---

# 4. CRUD는 API 서버가 담당한다

게시판의 CRUD는 `board_api`가 담당한다.

```text
Create : 게시글 생성
Read   : 게시글 조회
Update : 게시글 수정
Delete : 게시글 삭제
```

즉, 실제 데이터 처리의 주인은 API 서버다.

FE 서버는 사용자의 요청을 받아서 API 서버에 전달한다.

예를 들어 사용자가 글쓰기 화면에서 글을 등록하면:

```text
브라우저에서 글쓰기 폼 제출
→ board_fe Controller
→ board_fe Service
→ BoardApiClient
→ board_api POST /boards
→ DB 저장
```

사용자가 보기에는 FE 서버에서 글을 등록한 것처럼 보인다.

하지만 실제 DB 저장은 API 서버가 한다.

---

# 5. DB 스키마는 직접 만든 게 아니라 Entity를 보고 만들어짐

현재 JPA를 쓰고 있다면 DB 테이블은 직접 SQL로 만든 것이 아닐 수 있다.

예를 들어 Entity가 이렇게 있다.

```java
@Entity
public class Board {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String title;
    private String author;
    private String content;
}
```

그리고 설정에 이런 값이 있으면,

```properties
spring.jpa.hibernate.ddl-auto=update
```

또는 개발 환경에서 `create`, `create-drop` 같은 옵션이 있으면, Hibernate가 Entity를 보고 테이블을 자동으로 만들 수 있다.

즉, 흐름은 이렇다.

```text
Board Entity 작성
→ JPA/Hibernate가 Entity 분석
→ board 테이블 자동 생성 또는 갱신
```

그래서 “내가 DB 스키마를 직접 만든 게 아니라 Entity 보고 만들어졌다”는 말이 맞다.

개발 초반에는 편하다.

하지만 실무에서는 자동 생성만 믿고 가면 위험할 수 있다.

---

# 6. H2 기반 설정은 정리해야 한다

처음 개발할 때는 H2를 많이 쓴다.

```xml
<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>runtime</scope>
</dependency>
```

H2는 가볍고 빠르기 때문에 테스트용으로 좋다.

하지만 실제로 Docker Postgres나 MySQL 같은 DB로 넘어가려면 H2 기반 설정은 정리해야 한다.

예를 들어 `pom.xml`에 H2가 남아 있고, `application.properties`에도 H2 설정이 남아 있으면 헷갈린다.

```properties
spring.datasource.url=jdbc:h2:mem:boarddb
spring.h2.console.enabled=true
```

이런 설정이 남아 있으면 지금 내가 H2를 쓰는지, Postgres를 쓰는지 혼란이 생긴다.

그래서 DB를 전환할 때는 브랜치를 따서 정리하는 게 낫다.

```text
main
└── feature/db-migration-postgres
```

그리고 그 브랜치에서 H2 관련 설정을 제거하고, 실제 DB 설정으로 바꾸는 식이다.

---

# 7. FE 서버가 여러 API를 호출할 수 있다

FE 서버의 장점은 하나의 API만 호출하는 게 아니라 여러 API를 조합할 수 있다는 점이다.

예를 들어 서비스가 이렇게 나뉘어 있다고 하자.

```text
board_api   : 게시판 담당
member_api  : 회원 담당
order_api   : 주문 담당
```

브라우저에서 마이페이지를 보여줘야 한다면 여러 데이터가 필요할 수 있다.

```text
회원 정보
내가 쓴 게시글
주문 내역
알림 목록
```

이때 FE 서버가 각각의 API를 호출해서 화면을 구성할 수 있다.

```text
board_fe
→ member_api
→ board_api
→ order_api
```

즉, FE 서버는 사용자 화면을 만들기 위해 필요한 데이터를 여러 API에서 가져올 수 있다.

---

# 8. 왜 board_api가 order_api나 member_api를 막 호출하면 안 될까?

중요한 건 역할이다.

`board_api`는 게시판을 관리하는 서버다.

```text
board_api의 역할
게시글 생성
게시글 조회
게시글 수정
게시글 삭제
댓글 처리
게시글 검색
```

그런데 갑자기 `board_api`가 회원 정보도 가져오고, 주문 정보도 가져오고, 로그인도 처리하면 어떻게 될까?

```text
board_api
→ 게시판 처리
→ 회원 처리
→ 주문 처리
→ 로그인 처리
```

이러면 board_api의 역할이 모호해진다.

“너는 게시판 서버야, 회원 서버야, 주문 서버야?”가 된다.

이게 좋지 않은 구조다.

각 API는 자기 책임을 가져야 한다.

```text
board_api
→ 게시판 업무만 담당

member_api
→ 회원 업무만 담당

order_api
→ 주문 업무만 담당
```

이렇게 나누면 각 서버의 책임이 명확해진다.

---

# 9. UX 때문에 여러 데이터가 필요하면 FE가 조합하는 게 맞다

사용자가 어떤 화면을 본다는 것은 결국 UX 문제다.

예를 들어 게시글 상세 페이지에서 작성자 정보도 보여주고 싶다고 하자.

```text
게시글 제목
게시글 내용
작성자 닉네임
작성자 프로필 이미지
작성자의 다른 글
```

이건 “게시글 데이터 자체”만의 문제가 아니다.

화면에서 뭘 보여줄지의 문제다.

즉, UX 요구사항이다.

이럴 때는 FE 서버가 필요한 API들을 조합하는 게 자연스럽다.

```text
board_fe
→ board_api에서 게시글 조회
→ member_api에서 작성자 정보 조회
→ 화면에 합쳐서 보여줌
```

반대로 `board_api`가 member_api까지 호출해서 모든 걸 다 가져오게 만들면 board_api가 너무 많은 책임을 갖게 된다.

---

# 10. API가 API를 호출해도 되는 경우

그렇다고 API끼리 절대 호출하면 안 되는 건 아니다.

연관성이 강한 업무라면 API가 다른 API를 호출할 수 있다.

예를 들어 주문을 생성할 때 재고 확인이 필요하다고 하자.

```text
order_api
→ inventory_api 재고 확인
→ 결제 진행
→ 주문 생성
```

이건 주문이라는 업무를 처리하기 위해 필요한 흐름이다.

이런 경우는 API 간 호출이 자연스럽다.

하지만 게시글 목록 화면에 회원 닉네임을 보여주기 위해 `board_api`가 회원 API를 호출하는 것은 애매할 수 있다.

왜냐하면 그 요구는 “게시판 업무”라기보다는 “화면 구성”에 가깝기 때문이다.

정리하면 이렇다.

```text
업무적으로 강하게 연결된 호출
→ API가 API를 호출해도 됨

화면 구성을 위한 데이터 조합
→ FE가 여러 API를 호출하는 게 자연스러움
```

---

# 11. 로그인은 어디에 만들까?

로그인 페이지는 FE에 만든다.

사용자가 보는 화면이기 때문이다.

```text
GET /login
→ board_fe가 login.html 반환
```

사용자가 아이디와 비밀번호를 입력하면 FE 서버가 API 서버에 전달한다.

```text
브라우저
→ board_fe 로그인 폼 제출
→ board_fe
→ member_api 또는 auth_api
→ DB에서 회원 정보 확인
```

즉, 로그인 화면은 FE가 담당하고, 실제 인증 데이터 확인은 API가 담당한다.

```text
FE
로그인 화면
입력값 전달
세션/쿠키 처리 또는 토큰 처리

API
회원 조회
비밀번호 검증
토큰 발급 또는 인증 결과 반환
```

물론 구조에 따라 인증을 API 중심으로 만들 수도 있지만, 화면 자체는 FE의 책임으로 보는 게 자연스럽다.

---

# 12. 현재 구조를 한 번에 정리하면

```text
브라우저
→ 사용자는 8081 board_fe에 접속

board_fe
→ index, list, detail, write, edit 같은 HTML 반환
→ 사용자 입력 받음
→ board_api로 JSON 요청 보냄
→ API 응답을 받아 Model에 담음
→ Thymeleaf로 화면 렌더링

board_api
→ 게시판 CRUD API 제공
→ Service에서 비즈니스 로직 처리
→ Repository로 DB 접근
→ Entity 기준으로 DB 데이터 관리

DB
→ 게시글 데이터 저장
```

전체 요청 흐름은 이렇다.

```text
글 목록 보기

브라우저
→ GET http://localhost:8081/boards
→ board_fe Controller
→ board_fe Service
→ BoardApiClient
→ GET http://localhost:8080/boards
→ board_api Controller
→ board_api Service
→ board_api Repository
→ DB
→ JSON 응답
→ board_fe가 Model에 담음
→ list.html 렌더링
→ 브라우저에 HTML 응답
```

---

# 13. 최종 정리

이번 지적의 핵심은 단순히 포트 번호나 설정 문제가 아니다.

전체 구조를 이해해야 한다.

```text
브라우저는 FE 서버를 본다.
FE 서버는 화면을 담당한다.
API 서버는 데이터를 담당한다.
DB는 API 서버 뒤에 있다.
FE와 API 사이는 JSON으로 통신한다.
```

그리고 역할 분리도 중요하다.

```text
board_fe
→ UX와 화면 흐름 담당
→ 여러 API를 호출해서 화면 구성 가능

board_api
→ 게시판 업무 담당
→ 게시판 CRUD 처리
→ DB 접근

member_api
→ 회원 업무 담당

order_api
→ 주문 업무 담당
```

한 줄로 정리하면 이렇다.

> 브라우저에서 발생한 화면 요구사항은 FE가 대응하고, API는 자기 도메인의 업무만 담당하는 구조가 유지보수하기 좋다.

그래서 “왜 보드를 통해 다른 API를 호출하냐, FE에서 호출하는 게 맞다”는 말은 결국 이 뜻이다.

```text
게시판 API는 게시판 업무만 해야 한다.
화면을 위해 여러 데이터를 조합하는 일은 FE의 책임이다.
```
