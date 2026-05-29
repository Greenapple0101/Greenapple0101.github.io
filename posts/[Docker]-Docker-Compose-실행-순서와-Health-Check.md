---
title: "[DOCKER] Docker Compose 실행 순서와 Health Check"
source: "https://velog.io/@yorange50/DOCKER-Docker-Compose-실행-순서와-Health-Check"
published: "2026-05-14T07:42:01.587Z"
tags: ""
backup_date: "2026-05-29T14:52:52.740838"
---


# [DOCKER COMPOSE] DB가 먼저 떠야 하는 이유

Docker Compose로 애플리케이션과 DB를 함께 실행할 때 자주 나오는 구조가 있다.

```text id="z2dfny"
Spring Boot App
↓
PostgreSQL
```

또는

```text id="qbfho5"
Node.js App
↓
MySQL
```

이 구조에서 애플리케이션은 혼자 동작하지 않는다.

대부분의 백엔드 애플리케이션은 실행될 때 DB에 연결해야 한다.

그래서 DB가 먼저 떠 있어야 한다.

---

## 애플리케이션 의존성

애플리케이션은 실행 과정에서 여러 외부 자원에 의존한다.

```text id="6uwenc"
Database
Redis
Message Queue
Object Storage
External API
```

이 중에서 가장 대표적인 것이 DB다.

Spring Boot 애플리케이션을 예로 들면 실행 시점에 datasource 설정을 읽고 DB 연결을 시도한다.

```yaml id="ja5cc1"
spring:
  datasource:
    url: jdbc:postgresql://postgres:5432/hellodb
    username: user
    password: password
```

이 설정이 있다면 애플리케이션은 `postgres:5432`로 접속하려고 한다.

그런데 이때 PostgreSQL이 아직 준비되지 않았다면 연결에 실패할 수 있다.

---

## JDBC 연결 실패

Java 애플리케이션에서는 DB 연결에 JDBC를 사용한다.

JDBC는 Java에서 DB와 통신하기 위한 표준 인터페이스다.

Spring Boot는 내부적으로 이 JDBC 연결을 사용해서 DB에 접속한다.

DB가 아직 떠 있지 않으면 다음과 같은 문제가 생길 수 있다.

```text id="x3fzgm"
Connection refused
Connection timeout
Could not connect to database
Failed to initialize datasource
```

즉, 애플리케이션 입장에서는 DB가 준비되지 않은 상태에서 문을 두드리는 셈이다.

```text id="6jnbv8"
App: DB야 연결할게
DB: 아직 준비 안 됐는데?
App: 연결 실패
```

---

## startup timing 문제

Compose에서 app과 DB를 함께 실행한다고 해보자.

```yaml id="78j8bh"
services:
  app:
    build: .
    depends_on:
      - postgres

  postgres:
    image: postgres:16
```

겉으로 보면 `depends_on`이 있으니 postgres가 먼저 실행되고 app이 나중에 실행될 것 같다.

실제로 어느 정도 실행 순서는 제어된다.

하지만 문제는 PostgreSQL 컨테이너가 “실행됨” 상태가 되는 것과 PostgreSQL 서버가 “접속 가능함” 상태가 되는 것은 다르다는 점이다.

```text id="is0zc7"
컨테이너 실행됨
≠
DB 접속 준비 완료
```

PostgreSQL 컨테이너가 시작됐다고 해서 바로 5432 포트에서 정상적으로 쿼리를 받을 수 있는 것은 아니다.

초기화 과정이 필요할 수 있다.

```text id="r26vmz"
데이터 디렉토리 초기화
사용자 생성
DB 생성
설정 파일 로딩
WAL 준비
PostgreSQL 서버 기동
```

이 과정이 끝나기 전에 app이 먼저 DB에 붙으려고 하면 실패한다.

---

## 왜 로컬에서는 괜찮았을까?

로컬 개발에서는 이런 문제가 잘 안 보일 수 있다.

왜냐하면 보통 DB를 먼저 켜둔 상태에서 애플리케이션을 나중에 실행하기 때문이다.

```text id="1f99r3"
1. PostgreSQL 이미 실행 중
2. 개발자가 Spring Boot 실행
3. DB 연결 성공
```

하지만 Docker Compose에서는 여러 컨테이너를 동시에 올린다.

```bash id="de6wf6"
docker compose up -d
```

이때 app과 DB가 거의 동시에 시작되면서 타이밍 문제가 생긴다.

```text id="r1sfj1"
PostgreSQL 시작 중
Spring Boot 시작
Spring Boot가 DB 연결 시도
PostgreSQL 아직 준비 안 됨
연결 실패
```

이게 startup timing 문제다.

---

## DB가 먼저 떠야 한다는 말의 정확한 의미

“DB가 먼저 떠야 한다”는 말은 단순히 컨테이너 프로세스가 먼저 시작되어야 한다는 뜻이 아니다.

더 정확히는 다음 뜻이다.

```text id="ve4st8"
DB 컨테이너가 실행되고
DB 서버가 초기화를 끝내고
DB 접속을 받을 수 있는 상태가 된 뒤에
애플리케이션이 연결해야 한다
```

즉, 중요한 것은 실행 순서가 아니라 준비 상태다.

---

## 정리

애플리케이션은 DB에 의존한다.

그래서 DB가 준비되지 않은 상태에서 애플리케이션이 먼저 연결을 시도하면 실패할 수 있다.

```text id="ajvw9v"
애플리케이션 실행
→ datasource 초기화
→ JDBC 연결 시도
→ DB가 아직 준비 안 됨
→ 연결 실패
```

Docker Compose에서는 여러 컨테이너가 동시에 올라가기 때문에 startup timing 문제가 생기기 쉽다.

핵심은 이것이다.

```text id="9doyih"
DB가 먼저 떠야 한다는 말은
DB 컨테이너가 실행되는 것뿐 아니라
DB가 실제로 접속 가능한 상태가 되는 것을 의미한다.
```

그래서 단순 실행 순서보다 health check가 중요해진다.

---

# [DOCKER COMPOSE] depends_on만으로는 부족한 이유

Docker Compose에서 여러 서비스를 함께 실행할 때 `depends_on`을 자주 사용한다.

예를 들어 Spring Boot App이 PostgreSQL에 의존한다면 이렇게 쓴다.

```yaml id="1lk8zs"
services:
  app:
    build: .
    depends_on:
      - postgres

  postgres:
    image: postgres:16
```

처음 보면 이 설정만으로 충분해 보인다.

```text id="svyjqr"
app은 postgres에 의존한다
그러면 postgres가 완전히 뜬 뒤 app이 실행되겠지?
```

하지만 여기서 중요한 함정이 있다.

`depends_on`은 컨테이너 실행 순서를 제어할 뿐, 서비스 준비 완료를 보장하지 않는다.

---

## depends_on이 하는 일

`depends_on`은 Compose에게 서비스 간 의존 관계를 알려준다.

```yaml id="c7v5cn"
depends_on:
  - postgres
```

이 설정은 다음 의미에 가깝다.

```text id="vb99zz"
app을 실행하기 전에 postgres 컨테이너를 먼저 시작해라
```

즉, app 컨테이너보다 postgres 컨테이너를 먼저 실행한다.

하지만 이것은 PostgreSQL 서버가 완전히 준비되었다는 의미가 아니다.

---

## 컨테이너 실행 ≠ 서비스 준비 완료

Docker에서 컨테이너가 실행 중이라는 것은 프로세스가 시작되었다는 뜻에 가깝다.

```text id="f1kpqc"
컨테이너 상태: running
```

하지만 PostgreSQL이 실제로 쿼리를 받을 준비가 됐는지는 별개의 문제다.

```text id="3lvi40"
컨테이너 running
→ PostgreSQL 프로세스 시작 중일 수 있음
→ DB 초기화 중일 수 있음
→ 아직 접속 실패할 수 있음
```

즉, 다음 두 상태는 다르다.

```text id="ab71oa"
postgres 컨테이너가 실행됨
≠
postgres DB가 접속 가능함
```

`depends_on`만 쓰면 앞의 상태까지만 어느 정도 보장한다.

뒤의 상태는 보장하지 않는다.

---

## PostgreSQL startup 시간

PostgreSQL 컨테이너는 처음 실행될 때 여러 작업을 한다.

```text id="i2wqi3"
데이터 디렉토리 확인
초기 DB 생성
사용자 생성
권한 설정
설정 파일 로딩
서버 프로세스 시작
포트 열기
접속 준비 완료
```

특히 처음 실행하는 컨테이너라면 `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` 같은 환경변수를 읽어서 초기 DB와 사용자를 생성한다.

이 과정에는 시간이 걸릴 수 있다.

그런데 app 컨테이너가 너무 빨리 시작되면, PostgreSQL이 아직 준비되기 전에 연결을 시도한다.

결과적으로 이런 오류가 날 수 있다.

```text id="yzrdby"
Connection refused
The connection attempt failed
Database system is starting up
```

---

## race condition

이런 문제를 race condition이라고 볼 수 있다.

race condition은 여러 작업이 동시에 진행될 때, 실행 타이밍에 따라 결과가 달라지는 문제다.

Docker Compose에서 app과 DB를 동시에 올릴 때도 비슷하다.

```text id="xlu4o5"
상황 A
DB 준비 완료 → App 연결 시도 → 성공

상황 B
App 연결 시도 → DB 아직 준비 중 → 실패
```

같은 Compose 파일인데 어떤 날은 되고, 어떤 날은 안 된다.

이런 문제가 생기면 굉장히 헷갈린다.

```text id="h5xnoq"
어제는 됐는데 오늘은 안 됨
내 컴퓨터에서는 되는데 다른 사람 컴퓨터에서는 안 됨
재시작하면 됨
처음 실행할 때만 실패함
```

이런 증상이 나오면 startup timing 문제나 health check 부재를 의심해야 한다.

---

## depends_on의 한계

정리하면 `depends_on`의 한계는 다음과 같다.

```text id="rj4c80"
컨테이너 시작 순서는 제어함
서비스 준비 완료는 보장하지 않음
DB readiness 확인 안 함
포트가 열렸는지 확인 안 함
정상 쿼리 가능 여부 확인 안 함
```

그래서 `depends_on`만으로는 안정적인 실행을 보장하기 어렵다.

특히 DB, Redis, Kafka, Elasticsearch처럼 초기화 시간이 필요한 서비스는 더 그렇다.

---

## 그래도 depends_on은 쓸모가 없을까?

쓸모가 없는 것은 아니다.

`depends_on`은 의존 관계를 표현한다는 점에서 의미가 있다.

```yaml id="2sdlmk"
services:
  app:
    depends_on:
      - postgres
      - redis
```

이 설정을 보면 app이 postgres와 redis에 의존한다는 것을 바로 알 수 있다.

즉, 문서화 효과도 있고, 기본적인 시작 순서 제어도 된다.

다만 이것만으로 충분하다고 생각하면 안 된다.

---

## 정리

`depends_on`은 Docker Compose에서 서비스 간 의존 관계를 표현하는 설정이다.

하지만 `depends_on`은 컨테이너 실행 순서만 어느 정도 제어할 뿐, 서비스가 완전히 준비되었는지는 확인하지 않는다.

```text id="ixbtqz"
depends_on
→ postgres 컨테이너를 먼저 시작

health check
→ postgres가 실제로 접속 가능한지 확인
```

핵심은 이것이다.

```text id="ks5s0p"
컨테이너가 running이라고 해서
서비스가 ready인 것은 아니다.
```

그래서 안정적인 Compose 환경을 만들려면 `depends_on`과 함께 health check를 고려해야 한다.

---

# [DOCKER COMPOSE] Health Check는 왜 필요한가?

Docker Compose에서 app과 DB를 함께 실행할 때 가장 흔한 문제 중 하나는 실행 타이밍이다.

DB 컨테이너는 실행됐지만, DB 서버는 아직 준비되지 않았을 수 있다.

이 상태에서 app이 DB에 연결하려고 하면 실패한다.

그래서 필요한 것이 Health Check다.

---

## Health Check란?

Health Check는 컨테이너 안의 서비스가 정상 상태인지 확인하는 검사다.

단순히 컨테이너가 실행 중인지 보는 것이 아니라, 실제 서비스가 사용할 준비가 되었는지를 확인한다.

```text id="3sowrg"
컨테이너 running
→ 프로세스가 실행 중

서비스 healthy
→ 실제로 사용할 준비가 됨
```

DB라면 다음을 확인해야 한다.

```text id="iuid4k"
PostgreSQL이 접속 가능한가?
사용자 인증이 가능한가?
DB가 쿼리를 받을 수 있는가?
```

---

## PostgreSQL Health Check 예시

PostgreSQL에서는 `pg_isready` 명령어를 사용할 수 있다.

`pg_isready`는 PostgreSQL 서버가 연결을 받을 준비가 되었는지 확인하는 명령어다.

Compose에서는 이렇게 쓸 수 있다.

```yaml id="7ic91m"
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: hellodb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d hellodb"]
      interval: 5s
      timeout: 3s
      retries: 5
```

이 설정은 다음 의미다.

```text id="8r57i7"
5초마다 pg_isready 실행
3초 안에 응답 없으면 실패
5번 실패하면 unhealthy로 판단
```

PostgreSQL이 준비되면 컨테이너 상태가 `healthy`가 된다.

---

## depends_on과 health check 함께 쓰기

Compose에서는 health check 조건을 이용해 app이 DB의 healthy 상태를 기다리게 만들 수 있다.

```yaml id="xxabdj"
services:
  app:
    build: .
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: hellodb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d hellodb"]
      interval: 5s
      timeout: 3s
      retries: 5
```

이렇게 하면 app은 postgres 컨테이너가 단순히 실행되는 것만 기다리는 것이 아니라, postgres가 `healthy` 상태가 되는 것을 기다린다.

```text id="265jsv"
postgres 컨테이너 시작
↓
pg_isready로 준비 상태 확인
↓
healthy 상태
↓
app 컨테이너 시작
```

이 흐름이 더 안정적이다.

---

## DB readiness 확인

Health Check에서 중요한 개념은 readiness다.

readiness는 서비스가 요청을 받을 준비가 되었는지를 뜻한다.

DB readiness는 다음을 의미한다.

```text id="1cv9ne"
DB 프로세스가 떠 있음
포트가 열려 있음
접속 가능함
인증 가능함
쿼리 처리 가능함
```

컨테이너 상태가 running인 것만으로는 readiness를 알 수 없다.

그래서 Health Check가 필요하다.

---

## restart loop

Health Check가 없으면 app 컨테이너가 계속 죽었다 살아나는 상황이 생길 수 있다.

예를 들어 app이 시작되자마자 DB에 연결하려고 한다.

그런데 DB가 아직 준비되지 않았다.

```text id="5h4m9d"
app 시작
DB 연결 실패
app 종료
restart 정책에 의해 재시작
다시 DB 연결 시도
또 실패
```

이런 식으로 반복될 수 있다.

```text id="l2c2kw"
restart loop
```

restart loop는 로그를 지저분하게 만들고, 원인 파악을 어렵게 한다.

겉으로는 컨테이너가 계속 재시작되기 때문에 애플리케이션 문제처럼 보일 수 있지만, 실제 원인은 DB readiness 문제일 수 있다.

---

## production에서 중요한 이유

개발 환경에서는 몇 번 재시작하면 해결될 수도 있다.

하지만 운영 환경에서는 다르다.

운영에서는 컨테이너가 언제든 새로 시작될 수 있다.

```text id="uweqvm"
배포
서버 재부팅
장애 복구
스케일 아웃
컨테이너 재생성
```

이때 의존 서비스가 준비되기 전에 애플리케이션이 먼저 뜨면 장애로 이어질 수 있다.

그래서 production에서는 단순히 “실행됐다”가 아니라 “정상적으로 요청을 처리할 준비가 됐다”를 확인해야 한다.

Health Check는 이 준비 상태를 확인하는 기본 장치다.

---

## Health Check가 모든 문제를 해결할까?

Health Check가 모든 문제를 해결하는 것은 아니다.

예를 들어 DB는 healthy가 되었지만, 이후 네트워크가 끊기거나 DB가 재시작될 수도 있다.

그래서 애플리케이션 자체에도 재시도 로직이 필요하다.

```text id="x01zos"
DB 연결 재시도
timeout 설정
connection pool 설정
장애 시 graceful handling
```

즉, 안정적인 운영을 위해서는 다음이 함께 필요하다.

```text id="u50us4"
Compose healthcheck
애플리케이션 retry
적절한 restart policy
로그와 모니터링
```

Health Check는 그중 첫 번째 방어선이라고 볼 수 있다.

---

## 정리

Health Check는 컨테이너가 단순히 실행 중인지가 아니라, 실제 서비스가 준비되었는지 확인하는 장치다.

PostgreSQL에서는 `pg_isready`를 사용할 수 있다.

```yaml id="m8l0pb"
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U user -d hellodb"]
  interval: 5s
  timeout: 3s
  retries: 5
```

그리고 app은 DB가 healthy 상태가 된 뒤 실행되도록 구성할 수 있다.

```yaml id="ncq3ru"
depends_on:
  postgres:
    condition: service_healthy
```

핵심은 이것이다.

```text id="3cftxl"
컨테이너 실행 상태보다 중요한 것은 서비스 준비 상태다.
```

`depends_on`은 실행 순서를 돕고, Health Check는 실제 준비 상태를 확인한다.

둘을 함께 써야 Docker Compose 환경이 더 안정적으로 동작한다.
