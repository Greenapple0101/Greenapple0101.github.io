---
title: "[DOCKER] 컨테이너에서 localhost가 안 먹히는 이유: host.docker.internal과 Profile 분리"
source: "https://velog.io/@yorange50/DOCKER-컨테이너에서-localhost가-안-먹히는-이유-host.docker.internal과-Profile-분리"
published: "2026-05-08T07:52:12.834Z"
tags: ""
backup_date: "2026-05-29T14:52:52.766795"
---

이번에 겪은 문제는 단순히 DB URL 하나가 틀린 문제가 아니었다.

핵심은 이거였다.

```text
내 노트북 안의 PostgreSQL
컨테이너 안의 PostgreSQL
Docker Compose 안의 PostgreSQL
```

이 셋은 같은 것처럼 보여도 네트워크 기준에서는 완전히 다르다.

---

# 1. 문제 상황

처음에는 Spring Boot API가 PostgreSQL을 바라보도록 설정했다.

```yml
spring:
  datasource:
    url: ${SPRING_DATASOURCE_URL:jdbc:postgresql://db:5432/boarddb}
```

Docker Compose에서는 이게 잘 된다.

왜냐하면 Compose 안에서는 `db`라는 이름이 서비스 이름으로 동작하기 때문이다.

```yml
services:
  db:
    image: postgres:16-alpine

  api:
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://db:5432/boarddb
```

즉 Compose 내부에서는:

```text
api 컨테이너 → db:5432 → db 컨테이너
```

로 연결된다.

---

# 2. 그런데 Compose를 끄면 문제가 생긴다

Compose를 끄고 API 컨테이너만 따로 실행하면 상황이 달라진다.

```bash
docker run -p 8080:8080 ubuntu12341/board-api:v0.0.6
```

이때 컨테이너 안에서 `db`라는 이름을 찾으려고 하면 실패할 수 있다.

왜냐하면 `db`는 Docker Compose 네트워크 안에서만 의미 있는 서비스 이름이기 때문이다.

Compose 없이 단독 `docker run`을 하면 `db`라는 별칭을 모른다.

---

# 3. 컨테이너 안의 `localhost`는 내 노트북이 아니다

처음 헷갈리는 부분이 이거다.

컨테이너 안에서:

```text
localhost
```

라고 하면 내 노트북을 의미하는 게 아니다.

컨테이너 자기 자신을 의미한다.

즉 API 컨테이너 안에서:

```yml
url: jdbc:postgresql://localhost:5432/boarddb
```

라고 쓰면 이 뜻이다.

```text
API 컨테이너 자기 자신 안의 5432 포트를 찾아라
```

그런데 API 컨테이너 안에는 PostgreSQL이 없다.

그래서 연결이 안 된다.

---

# 4. 노트북에 설치된 PostgreSQL로 가려면?

이때 사용하는 특별한 도메인이 있다.

```text
host.docker.internal
```

이건 Docker Desktop이 제공하는 특수한 주소다.

의미는:

```text
컨테이너 안에서 호스트 PC로 나가라
```

즉 API 컨테이너가 내 노트북의 PostgreSQL을 바라보게 하려면 이렇게 쓴다.

```yml
spring:
  datasource:
    url: jdbc:postgresql://host.docker.internal:5432/boarddb
```

흐름은 이렇게 된다.

```text
API 컨테이너
→ host.docker.internal
→ 내 노트북
→ 5432번 PostgreSQL
```

---

# 5. 단, Windows/Mac 기준이다

`host.docker.internal`은 Docker Desktop에서 제공하는 기능이다.

그래서 보통:

```text
Windows 가능
Mac 가능
Linux는 환경에 따라 별도 설정 필요
```

Linux에서는 기본으로 안 되는 경우가 많고, bridge gateway IP를 직접 쓰거나 별도 옵션을 줘야 할 수 있다.

이번 로컬 개발 환경은 Windows Docker Desktop이므로 `host.docker.internal`을 쓰는 게 맞다.

---

# 6. FE도 같은 문제가 생긴다

FE 쪽 설정도 마찬가지였다.

```properties
spring.application.name=board_fe
server.port=${SERVER_PORT:8081}

board.api.base-url=${BOARD_API_BASE_URL:http://localhost:8080}
```

로컬에서 FE를 직접 실행하면:

```text
localhost:8080
```

은 내 노트북에서 실행 중인 API를 의미한다.

하지만 FE도 컨테이너 안에서 실행되면 이야기가 달라진다.

FE 컨테이너 안에서 `localhost:8080`은 FE 컨테이너 자기 자신이다.

그래서 FE 컨테이너가 노트북에서 실행 중인 API를 호출해야 한다면:

```properties
board.api.base-url=${BOARD_API_BASE_URL:http://host.docker.internal:8080}
```

처럼 가야 한다.

또는 Compose 안에서 FE와 API를 같이 띄우는 경우라면:

```yaml
BOARD_API_BASE_URL: http://api:8080
```

처럼 서비스 이름을 쓰면 된다.

---

# 7. 결국 환경이 세 개로 나뉜다

이번에 정리한 환경은 크게 세 가지다.

| 환경                | API가 바라보는 DB 주소             |
| ----------------- | --------------------------- |
| 로컬 직접 실행          | `localhost:5432`            |
| Docker 단독 실행      | `host.docker.internal:5432` |
| Docker Compose 실행 | `db:5432`                   |

이걸 하나의 `application.yml`에 계속 바꿔가며 넣으면 너무 귀찮다.

그래서 Profile을 나누는 게 맞다.

---

# 8. local profile

로컬에서 Spring Boot를 직접 실행할 때는 노트북의 PostgreSQL을 바라보면 된다.

```yml
server:
  port: 8080

spring:
  application:
    name: board_api

  datasource:
    url: ${SPRING_DATASOURCE_URL:jdbc:postgresql://localhost:5432/boarddb}
    username: ${SPRING_DATASOURCE_USERNAME:board}
    password: ${SPRING_DATASOURCE_PASSWORD:board1234}

  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    properties:
      hibernate:
        format_sql: true
```

이건 로컬 개발용이다.

```text
Spring Boot 직접 실행
→ localhost:5432
→ 내 노트북 PostgreSQL
```

---

# 9. docker profile

API를 컨테이너로 실행하되 DB는 내 노트북 PostgreSQL을 쓰고 싶으면 `host.docker.internal`을 사용한다.

```yml
server:
  port: 8080

spring:
  application:
    name: board_api

  datasource:
    url: ${SPRING_DATASOURCE_URL:jdbc:postgresql://host.docker.internal:5432/boarddb}
    username: ${SPRING_DATASOURCE_USERNAME:board}
    password: ${SPRING_DATASOURCE_PASSWORD:board1234}

  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    properties:
      hibernate:
        format_sql: true
```

이건 Docker 단독 실행용이다.

```text
API 컨테이너
→ host.docker.internal:5432
→ 내 노트북 PostgreSQL
```

---

# 10. compose 환경

Compose로 API와 DB를 같이 띄우면 `db`를 쓴다.

```yaml
api:
  environment:
    SPRING_DATASOURCE_URL: jdbc:postgresql://db:5432/boarddb
    SPRING_DATASOURCE_USERNAME: board
    SPRING_DATASOURCE_PASSWORD: board1234
```

이때는:

```text
API 컨테이너
→ db:5432
→ DB 컨테이너
```

로 간다.

즉 `host.docker.internal`이 아니라 Compose 서비스 이름인 `db`를 쓰는 게 맞다.

---

# 11. 설정 파일을 계속 바꾸면 안 되는 이유

처음에는 DB URL을 직접 바꿨다.

```yml
jdbc:postgresql://db:5432/boarddb
```

였다가

```yml
jdbc:postgresql://host.docker.internal:5432/boarddb
```

로 바꾸고, 다시 빌드했다.

문제는 Java 프로젝트는 설정이 바뀌면 다시 빌드해야 한다는 점이다.

```text
application.yml 변경
→ Maven 빌드
→ jar 재생성
→ Docker 이미지 재빌드
→ Docker Hub push
→ 다시 run
```

이 과정을 매번 반복하면 너무 비효율적이다.

---

# 12. 그래서 Profile로 분리한다

환경별로 설정 파일을 따로 만든다.

예:

```text
src/main/resources/config/application-local.yml
src/main/resources/config/application-docker.yml
src/main/resources/config/application-compose.yml
```

그러면 코드를 계속 바꾸는 대신 실행 시점에 어떤 설정을 쓸지만 정하면 된다.

---

# 13. 실행할 때 Profile 지정하기

PowerShell에서 로컬 실행 전에 지정할 수 있다.

```powershell
$env:SPRING_PROFILES_ACTIVE="docker"
```

Docker 실행 시에는 `-e` 옵션으로 넘긴다.

```bash
docker run -p 8080:8080 \
  -e SPRING_PROFILES_ACTIVE=docker \
  ubuntu12341/board-api:v0.0.6
```

Windows PowerShell에서는 한 줄로 이렇게 쓰면 된다.

```powershell
docker run -p 8080:8080 -e SPRING_PROFILES_ACTIVE=docker ubuntu12341/board-api:v0.0.6
```

그러면 Spring Boot가 `application-docker.yml`을 읽는다.

---

# 14. 이번 성공 흐름

최종적으로 성공한 흐름은 이거다.

```text
1. Docker용 profile 파일 생성
2. datasource URL을 host.docker.internal로 설정
3. jar 다시 빌드
4. Docker 이미지 다시 빌드
5. docker run 실행 시 SPRING_PROFILES_ACTIVE=docker 주입
6. API 컨테이너가 노트북 PostgreSQL로 연결 성공
```

핵심 명령어는 이거다.

```powershell
docker run -p 8080:8080 -e SPRING_PROFILES_ACTIVE=docker ubuntu12341/board-api:v0.0.6
```

---

# 15. 정리: 언제 뭘 써야 하나?

| 상황                         | 써야 하는 주소                           |
| -------------------------- | ---------------------------------- |
| Spring Boot를 내 PC에서 직접 실행  | `localhost`                        |
| 컨테이너가 내 PC 서비스를 호출         | `host.docker.internal`             |
| Compose 컨테이너끼리 통신          | 서비스 이름, 예: `db`, `api`             |
| FE 컨테이너가 Compose 안의 API 호출 | `http://api:8080`                  |
| FE 컨테이너가 내 PC API 호출       | `http://host.docker.internal:8080` |

---

# 마무리

이번 에러의 본질은 DB 문제가 아니라 네트워크 기준점 문제였다.

```text
localhost가 누구 기준의 localhost인가?
```

이걸 이해해야 한다.

정리하면:

```text
로컬 실행의 localhost = 내 노트북
컨테이너 안의 localhost = 컨테이너 자기 자신
Compose의 db = Compose 네트워크 안의 DB 서비스
host.docker.internal = 컨테이너에서 호스트 PC로 가는 특수 주소
```

결국 Docker에서 중요한 건 단순히 실행이 아니라:

```text
어느 환경에서 실행되고,
그 환경 기준으로 어떤 주소를 바라보는지
```

를 정확히 구분하는 것이다.
