---
title: "[SPRING] DTO는 왜 쓰고, Profile은 왜 나눌까?"
source: "https://velog.io/@yorange50/SPRING-DTO는-왜-쓰고-Profile은-왜-나눌까"
published: "2026-05-08T07:44:30.305Z"
tags: ""
backup_date: "2026-05-29T14:52:52.767782"
---

# [SPRING BOOT] DTO는 왜 쓰고, Profile은 왜 나눌까?

스프링부트를 공부하다 보면 자주 듣는 말이 있다.

```text
“엔티티 이름 명확하게 지어라”
“DTO 써라”
“환경별로 profile 나눠라”
```

처음엔 그냥 규칙처럼 보이는데, 실제로는 전부 유지보수와 배포를 위한 구조다.

오늘은:

* 엔티티 네이밍
* DTO vs Entity
* Profile 기반 환경 분리

이 흐름을 한 번에 정리해본다.

---

# 1. 엔티티 이름은 왜 중요할까?

서비스를 만들다 보면 결국 URL과 도메인이 연결된다.

예를 들어 게시판 서비스라면:

```text
/boards
```

같은 URL이 생긴다.

그리고 내부 코드도 전부 “보드” 중심으로 연결된다.

```java
BoardEntity
BoardController
BoardService
BoardRepository
```

이때 이름이 애매하면 프로젝트가 커질수록 헷갈린다.

예:

```java
Data
Info
Item
Object
```

이런 이름은 나중에 보면 무슨 역할인지 알기 어렵다.

그래서 보통은:

```java
Board
User
Order
Product
```

처럼 도메인을 명확하게 드러내는 이름을 사용한다.

핵심은:

```text
도메인 이름 = 서비스의 언어
```

라는 점이다.

---

# 2. 엔티티만 써도 될까?

처음 스프링을 배우면 보통 이렇게 작성한다.

```java
@PostMapping
public Board create(@RequestBody Board board) {
    return boardRepository.save(board);
}
```

엔티티 하나로:

* 요청 받고
* 저장하고
* 응답까지 한다.

사실 작은 프로젝트에서는 이렇게 해도 동작은 한다.

---

# 3. 그런데 왜 DTO를 쓰라고 할까?

실무에서는 보통 DTO를 따로 둔다.

예:

```java
BoardRequest
BoardResponse
```

이유는 엔티티는 DB와 직접 연결된 객체이기 때문이다.

즉:

```text
엔티티 수정
→ DB 상태 영향 가능
```

이 구조가 된다.

또 엔티티를 그대로 API로 노출하면 문제가 생긴다.

예를 들어 DB 컬럼 구조가 바뀌면:

```text
DB 구조 변경
→ API 응답 변경
```

까지 이어질 수 있다.

그래서 DTO로 중간 레이어를 둔다.

```text
클라이언트 ↔ DTO ↔ Service ↔ Entity ↔ DB
```

이렇게 되면:

* API 스펙 보호 가능
* 계층 분리 가능
* 유지보수 쉬움
* 보안 관리 쉬움

같은 장점이 생긴다.

---

# 4. 그런데 DTO가 무조건 정답일까?

현실은 조금 다르다.

실제로는:

* Entity 직접 쓰는 팀
* DTO 쓰는 팀
* Map 기반 처리하는 팀

다 존재한다.

예:

```java
@PostMapping
public void create(@RequestBody Map<String, Object> body) {
}
```

빠르게 개발해야 하는 서비스는 DTO를 전부 만들기 어려울 수도 있다.

그래서 현실에서는:

```text
원칙은 DTO
현실은 상황 따라 타협
```

이 되는 경우가 많다.

하지만 구조적으로 가장 안정적인 건 DTO 방식이다.

---

# 5. Spring Boot의 설정 파일: application.yml

스프링부트는 보통 설정을 여기서 관리한다.

```text
src/main/resources/application.yml
```

예:

```yml
server:
  port: 8080
```

그런데 문제는 환경이 달라질 때다.

---

# 6. 환경마다 설정이 달라진다

예를 들어:

| 환경    | 포트   | DB        |
| ----- | ---- | --------- |
| local | 8080 | localhost |
| dev   | 8081 | 개발 DB     |
| prod  | 80   | 운영 DB     |

환경마다:

* 포트 다름
* 도메인 다름
* DB 주소 다름

즉 설정을 분리해야 한다.

---

# 7. 그래서 사용하는 게 Profile

스프링부트의 핵심 개념 중 하나다.

```text
Profile = 환경별 설정 묶음
```

보통 이렇게 나눈다.

```text
application.yml
application-local.yml
application-dev.yml
application-prod.yml
```

---

# 8. application.yml은 공통 설정

공통으로 쓰는 값들을 둔다.

```yml
spring:
  application:
    name: board-api
```

그리고 현재 어떤 환경을 사용할지 지정한다.

```yml
spring:
  profiles:
    active: local
```

즉 기본 실행은 local 환경이라는 뜻이다.

---

# 9. local/dev/prod 설정 분리

예:

## application-local.yml

```yml
server:
  port: 8080
```

## application-dev.yml

```yml
server:
  port: 8081
```

## application-prod.yml

```yml
server:
  port: 80
```

실행할 때:

```bash
SPRING_PROFILES_ACTIVE=dev
```

라고 주면 Spring Boot가:

```text
application-dev.yml
```

을 읽는다.

---

# 10. config 폴더를 따로 둘 수도 있다

설정 파일이 많아지면 보통 이렇게 분리한다.

```text
resources/config
```

예:

```text
src/main/resources/config/application.yml
```

Spring Boot는 config 폴더도 자동으로 탐색한다.

---

# 11. “여러 개 있으면 뭘 읽는지 모른다”를 해결하는 법

그래서 공통 파일을 하나 두고:

```text
application.yml
```

환경별 설정은:

```text
application-dev.yml
application-prod.yml
```

처럼 나눈다.

그리고 실행 시:

```bash
SPRING_PROFILES_ACTIVE=dev
```

처럼 현재 환경을 명시한다.

즉:

```text
공통 설정 + 환경별 오버라이드
```

구조다.

---

# 12. DBeaver는 왜 필요할까?

개발하다 보면:

```text
진짜 DB에 저장됐나?
```

를 확인해야 한다.

이때 사용하는 대표 툴이 DBeaver다.

할 수 있는 것:

* 테이블 확인
* 데이터 조회
* SQL 테스트
* 엔티티 매핑 검증

예:

```sql
SELECT * FROM board;
```

특히 local/dev/prod DB가 나뉘면:

```text
어느 DB에 붙었는지
```

확인하는 습관이 중요하다.

---

# 마무리

스프링부트에서 중요한 건 단순 문법보다 구조다.

오늘 핵심은:

* 도메인 이름은 명확하게
* 엔티티와 DTO 역할 분리
* 환경은 Profile로 분리
* 설정은 공통 + 환경별 구조
* DB는 직접 확인하는 습관

결국 이 모든 건:

```text
“서비스가 커져도 유지보수 가능하게 만들기”
```

위한 구조라고 볼 수 있다.
