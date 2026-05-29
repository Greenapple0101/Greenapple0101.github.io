---
title: "[DOCKER]Docker Compose 실전 구조"
source: "https://velog.io/@yorange50/DOCKERDocker-Compose-실전-구조"
published: "2026-05-14T07:17:49.948Z"
tags: ""
backup_date: "2026-05-29T14:52:52.741819"
---


# [DOCKER] docker-compose.yml은 단순 실행 파일이 아니다

Docker를 처음 배울 때는 보통 `docker run` 명령어로 컨테이너를 실행한다.

```bash
docker run -d -p 5432:5432 postgres:16
```

이렇게 하면 PostgreSQL 컨테이너 하나를 띄울 수 있다.

그런데 실제 개발 환경에서는 컨테이너 하나만 띄우는 경우가 많지 않다.

예를 들어 웹 애플리케이션을 만든다고 하면 보통 이런 것들이 함께 필요하다.

```text
Spring Boot App
PostgreSQL
MySQL
Nginx
Redis
Prometheus
Grafana
```

이걸 전부 `docker run` 명령어로 하나씩 실행하려고 하면 매우 번거롭다.

그래서 사용하는 것이 `docker-compose.yml`이다.

---

## docker-compose.yml은 실행 파일이 아니다

이름 때문에 헷갈릴 수 있지만, `docker-compose.yml`은 단순한 실행 파일이 아니다.

정확히는 **여러 컨테이너를 어떤 구성으로 실행할지 정의하는 설계도**에 가깝다.

```yaml
services:
  postgres:
    image: postgres:16
    ports:
      - "5432:5432"

  nginx:
    image: nginx:latest
    ports:
      - "80:80"

  app:
    build: .
    ports:
      - "8080:8080"
```

이 파일은 이렇게 말하는 것과 같다.

```text
postgres라는 컨테이너를 띄워라
nginx라는 컨테이너를 띄워라
app이라는 컨테이너를 띄워라
각 컨테이너의 포트, 환경변수, 볼륨, 네트워크를 이렇게 설정해라
```

즉, Compose는 단순 실행이 아니라 **개발 환경 전체를 정의하는 도구**다.

---

## service란 무엇인가?

`docker-compose.yml`에서 가장 중요한 단위는 `service`다.

```yaml
services:
  postgres:
    image: postgres:16
```

여기서 `postgres`가 service 이름이다.

service는 쉽게 말하면 **Compose가 관리하는 컨테이너 실행 단위**다.

```text
postgres service → PostgreSQL 컨테이너 실행
nginx service → Nginx 컨테이너 실행
app service → 애플리케이션 컨테이너 실행
```

즉, service는 컨테이너 그 자체라기보다는 **컨테이너를 어떻게 실행할지 정의한 이름 있는 설정 블록**이다.

---

## 여러 컨테이너 orchestration

Docker Compose의 핵심은 여러 컨테이너를 함께 관리하는 것이다.

이걸 어렵게 말하면 orchestration이라고 한다.

orchestration은 여러 구성 요소를 함께 실행하고, 연결하고, 관리하는 것을 말한다.

예를 들어 다음과 같은 구조가 있다고 해보자.

```text
사용자 요청
↓
Nginx
↓
Spring Boot App
↓
PostgreSQL
```

이때 각 요소는 서로 다른 컨테이너로 실행될 수 있다.

```yaml
services:
  nginx:
    image: nginx:latest

  app:
    build: .

  postgres:
    image: postgres:16
```

Compose는 이 컨테이너들을 한 번에 실행할 수 있게 해준다.

```bash
docker compose up -d
```

그러면 `nginx`, `app`, `postgres`가 함께 실행된다.

---

## PostgreSQL, MySQL, Nginx, App을 함께 실행하기

예를 들어 개발 환경에서 PostgreSQL과 Spring Boot 앱을 함께 실행하고 싶다고 해보자.

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"

  app:
    build: .
    ports:
      - "8080:8080"
    depends_on:
      - postgres
```

이렇게 하면 Compose 하나로 DB와 애플리케이션을 같이 실행할 수 있다.

개발자는 매번 PostgreSQL을 따로 설치하고, 앱을 따로 실행하고, 포트를 따로 확인할 필요가 줄어든다.

```bash
docker compose up -d
```

이 명령어 하나로 개발 환경이 올라간다.

---

## Compose의 역할

Docker Compose의 역할은 정리하면 다음과 같다.

```text
여러 컨테이너를 하나의 파일로 정의
컨테이너 간 네트워크 자동 구성
환경변수 설정
볼륨 연결
포트 매핑
실행 순서 일부 제어
개발 환경 재현
```

즉, Compose는 컨테이너 여러 개를 단순히 실행하는 도구가 아니라, **하나의 애플리케이션 환경을 구성하는 도구**다.

---

## 정리

`docker-compose.yml`은 단순 실행 파일이 아니다.

여러 컨테이너를 어떻게 실행하고, 어떻게 연결하고, 어떤 설정으로 관리할지 적어두는 파일이다.

```text
docker run
→ 컨테이너 하나를 실행하는 명령어

docker-compose.yml
→ 여러 컨테이너로 구성된 환경을 정의하는 설계도
```

그래서 Docker Compose를 이해할 때는 “컨테이너 실행”보다 “개발 환경 구성” 관점으로 보는 것이 좋다.

---

# [DOCKER] Docker Compose의 service 이름과 container_name 차이

Docker Compose를 쓰다 보면 헷갈리는 설정이 있다.

```yaml
services:
  postgres:
    image: postgres:16
    container_name: my-postgres
```

여기서 `postgres`와 `my-postgres`는 둘 다 이름처럼 보인다.

그러면 이런 의문이 생긴다.

```text
postgres가 이름인가?
my-postgres가 이름인가?
둘 중 뭘 써야 하지?
depends_on에는 뭘 적어야 하지?
DB 연결 주소에는 뭘 적어야 하지?
```

이 글에서는 Docker Compose에서 `service name`과 `container_name`의 차이를 정리한다.

---

## service name이란?

먼저 service name은 `services` 아래에 적는 이름이다.

```yaml
services:
  postgres:
    image: postgres:16
```

여기서 `postgres`가 service name이다.

service name은 Docker Compose가 해당 서비스를 구분하는 기준이다.

예를 들어 다음 명령어를 실행할 수 있다.

```bash
docker compose up postgres
```

이 명령어는 `postgres` service만 실행하라는 뜻이다.

즉, Compose 명령어에서 기준이 되는 이름은 service name이다.

---

## container_name이란?

`container_name`은 실제 Docker 컨테이너에 붙일 이름이다.

```yaml
services:
  postgres:
    image: postgres:16
    container_name: my-postgres
```

이렇게 하면 실제 컨테이너 이름이 `my-postgres`가 된다.

그래서 다음 명령어에서 보일 수 있다.

```bash
docker ps
```

예상 결과는 이런 식이다.

```text
NAMES
my-postgres
```

즉, `container_name`은 Docker 엔진 레벨에서 보이는 컨테이너 이름이다.

---

## 둘의 차이

정리하면 이렇다.

| 구분             | 의미                    | 예시          |
| -------------- | --------------------- | ----------- |
| service name   | Compose가 서비스를 구분하는 이름 | postgres    |
| container_name | 실제 컨테이너에 붙는 이름        | my-postgres |

둘 다 이름이지만 쓰이는 위치가 다르다.

```text
docker compose 명령어 기준 → service name
실제 컨테이너 이름 기준 → container_name
```

---

## DNS처럼 동작하는 이유

Docker Compose는 기본적으로 하나의 네트워크를 만들어준다.

같은 Compose 네트워크 안에 있는 컨테이너들은 서로를 이름으로 찾을 수 있다.

예를 들어 app 컨테이너와 postgres 컨테이너가 같은 Compose 파일에 있다고 해보자.

```yaml
services:
  app:
    build: .

  postgres:
    image: postgres:16
```

그러면 app 컨테이너 안에서는 PostgreSQL에 이렇게 접근할 수 있다.

```text
postgres:5432
```

여기서 `postgres`는 service name이다.

중요한 점은 컨테이너 내부에서 `localhost`를 쓰면 안 된다는 것이다.

```text
localhost:5432
```

이건 PostgreSQL 컨테이너를 가리키는 게 아니라, app 컨테이너 자기 자신을 가리킨다.

그래서 컨테이너끼리 통신할 때는 같은 네트워크 안에서 service name 또는 container_name을 사용해야 한다. 수업 메모에서도 Java App 컨테이너에서 PostgreSQL 컨테이너로 접근할 때 `localhost`가 아니라 컨테이너 이름이나 서비스명을 사용해야 한다는 흐름이 정리되어 있다. 

---

## depends_on은 왜 service 기준인가?

`depends_on`은 service name을 기준으로 작성한다.

```yaml
services:
  app:
    build: .
    depends_on:
      - postgres

  postgres:
    image: postgres:16
    container_name: my-postgres
```

여기서 `depends_on`에는 `my-postgres`가 아니라 `postgres`를 적는다.

왜냐하면 `depends_on`은 Docker 컨테이너 이름을 보는 것이 아니라, Compose 파일 안의 service 관계를 보기 때문이다.

즉, 다음은 맞다.

```yaml
depends_on:
  - postgres
```

다음은 일반적으로 잘못된 방식이다.

```yaml
depends_on:
  - my-postgres
```

`my-postgres`는 container_name이지 service name이 아니기 때문이다.

---

## 실무에서는 뭘 기준으로 쓰는 게 좋을까?

Compose 내부에서는 service name을 중심으로 생각하는 게 좋다.

```text
명령어 실행 → service name
depends_on → service name
컨테이너 간 통신 → service name 권장
```

`container_name`은 꼭 필요한 경우가 아니면 생략해도 된다.

Compose가 자동으로 컨테이너 이름을 만들어주기 때문이다.

예를 들어 프로젝트명이 `myapp`이고 service name이 `postgres`라면 컨테이너 이름은 보통 이런 식으로 자동 생성된다.

```text
myapp-postgres-1
```

직접 이름을 고정하면 편해 보이지만, 여러 프로젝트를 동시에 띄울 때 이름 충돌이 날 수 있다.

그래서 개발 초기에는 `container_name`을 쓰기도 하지만, Compose 구조를 제대로 이해하려면 service name을 기준으로 보는 게 좋다.

---

## 정리

Docker Compose에서 service name과 container_name은 다르다.

```text
service name
→ Compose가 서비스를 구분하는 이름
→ depends_on, docker compose up 서비스명에서 사용

container_name
→ 실제 Docker 컨테이너 이름
→ docker ps에서 보이는 이름
```

컨테이너끼리 통신할 때는 `localhost`가 아니라 service name을 사용해야 한다.

```text
app 컨테이너에서 DB 접근
localhost:5432       틀림
postgres:5432        맞음
```

Compose를 이해할 때는 컨테이너 이름보다 service 이름을 먼저 보는 습관이 중요하다.

---

# [DOCKER] Docker Compose에서 environment(env)는 뭘까?

Docker Compose 파일을 보면 자주 나오는 설정이 있다.

```yaml
environment:
  POSTGRES_DB: appdb
  POSTGRES_USER: user
  POSTGRES_PASSWORD: password
```

처음 보면 그냥 설정값처럼 보인다.

하지만 이 값들은 단순한 메모가 아니다.

`environment`는 컨테이너 내부 OS에 들어가는 **환경변수**를 설정하는 부분이다.

---

## 환경변수란?

환경변수는 운영체제 안에서 사용할 수 있는 변수다.

예를 들어 Linux나 macOS 터미널에서 이런 명령어를 쳐볼 수 있다.

```bash
echo $PATH
```

`PATH`는 대표적인 환경변수다.

프로그램을 실행할 때 어떤 경로에서 실행 파일을 찾을지 알려준다.

Docker 컨테이너도 작은 Linux 환경처럼 동작한다.

그래서 컨테이너 안에도 환경변수가 있다.

---

## Compose의 environment

Docker Compose에서는 `environment`를 통해 컨테이너 내부에 환경변수를 넣을 수 있다.

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
```

이 설정은 PostgreSQL 컨테이너 안에 다음 환경변수를 넣는다는 뜻이다.

```text
POSTGRES_DB=appdb
POSTGRES_USER=user
POSTGRES_PASSWORD=password
```

컨테이너 안에 들어가서 확인할 수도 있다.

```bash
docker exec -it my-postgres bash
env
```

`env` 명령어는 현재 환경변수 목록을 보여준다.

수업 메모에서도 컨테이너 안에서 `env`를 치면 Compose에 넣은 값들이 컨테이너 OS의 시스템 변수로 들어가 있는 것을 확인할 수 있다고 정리되어 있다. 

---

## PostgreSQL 환경변수

PostgreSQL Docker 이미지는 특정 환경변수를 읽어서 초기 설정을 만든다.

대표적으로 다음 값들이 있다.

```text
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

예를 들어 이렇게 설정하면

```yaml
environment:
  POSTGRES_DB: hellodb
  POSTGRES_USER: hello
  POSTGRES_PASSWORD: hello1234
```

PostgreSQL 컨테이너가 처음 시작될 때 다음과 같은 의미로 처리된다.

```text
hellodb라는 DB 생성
hello라는 사용자 생성
hello1234를 비밀번호로 설정
```

즉, Compose의 `environment`는 단순히 값을 보관하는 것이 아니라, 컨테이너 안에서 실행되는 프로그램의 초기 동작에 영향을 줄 수 있다.

---

## 컨테이너 내부 OS 변수

중요한 점은 `environment`에 적은 값이 호스트 OS에 들어가는 것이 아니라는 점이다.

```text
내 MacBook의 환경변수로 들어가는 것 아님
컨테이너 내부 환경변수로 들어가는 것
```

즉, 다음 구조다.

```text
호스트 OS
└── Docker 컨테이너
    └── 컨테이너 내부 환경변수
```

그래서 컨테이너 안에서 `env`를 치면 보이지만, 내 로컬 터미널에서 무조건 보이는 것은 아니다.

---

## application.yml과 연결

Spring Boot 애플리케이션에서도 환경변수를 사용할 수 있다.

예를 들어 `application.yml`에 이렇게 적을 수 있다.

```yaml
spring:
  datasource:
    url: jdbc:postgresql://${DB_HOST}:5432/${DB_NAME}
    username: ${DB_USER}
    password: ${DB_PASSWORD}
```

그리고 Compose에서 app 컨테이너에 환경변수를 넣는다.

```yaml
services:
  app:
    build: .
    environment:
      DB_HOST: postgres
      DB_NAME: appdb
      DB_USER: user
      DB_PASSWORD: password
    depends_on:
      - postgres

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
```

이렇게 하면 Spring Boot는 실행될 때 환경변수를 읽어서 DB 접속 정보를 구성한다.

즉, 코드 안에 DB 비밀번호를 직접 박아 넣지 않아도 된다.

---

## 왜 environment를 쓸까?

환경변수를 쓰는 이유는 설정을 코드와 분리하기 위해서다.

예를 들어 개발 환경과 운영 환경은 DB 주소가 다를 수 있다.

```text
개발 DB 주소
localhost 또는 postgres

운영 DB 주소
prod-db.company.internal
```

이걸 코드에 직접 적어두면 환경이 바뀔 때마다 코드를 수정해야 한다.

하지만 환경변수로 빼두면 코드는 그대로 두고 설정만 바꿀 수 있다.

```text
코드 = 고정
환경변수 = 환경마다 변경
```

이게 Docker와 서버 운영에서 중요한 사고방식이다.

---

## 정리

Docker Compose의 `environment`는 컨테이너 내부에 환경변수를 넣는 설정이다.

```yaml
environment:
  POSTGRES_DB: appdb
  POSTGRES_USER: user
  POSTGRES_PASSWORD: password
```

이 값들은 컨테이너 안에서 `env` 명령어로 확인할 수 있다.

```bash
env
```

PostgreSQL 같은 이미지는 이 환경변수를 읽어서 DB 이름, 사용자, 비밀번호를 초기화한다.

Spring Boot 같은 애플리케이션도 환경변수를 읽어서 `application.yml`과 연결할 수 있다.

핵심은 이것이다.

```text
환경변수는 코드가 아니라 실행 환경에 주입하는 설정값이다
```

---

# [DOCKER] Docker Compose에서 특정 서비스만 실행하는 방법

Docker Compose를 사용하면 여러 컨테이너를 한 번에 실행할 수 있다.

```bash
docker compose up
```

그런데 항상 모든 서비스를 실행해야 하는 것은 아니다.

가끔은 PostgreSQL만 띄우고 싶을 수도 있고, Nginx만 테스트하고 싶을 수도 있다.

이럴 때는 특정 서비스만 지정해서 실행할 수 있다.

---

## docker compose up

기본 명령어는 다음과 같다.

```bash
docker compose up
```

또는 백그라운드 실행을 위해 `-d` 옵션을 붙인다.

```bash
docker compose up -d
```

이 명령어는 `docker-compose.yml`에 정의된 모든 서비스를 실행한다.

예를 들어 다음 Compose 파일이 있다고 해보자.

```yaml
services:
  postgres:
    image: postgres:16

  nginx:
    image: nginx:latest

  app:
    build: .
```

이 상태에서 다음 명령어를 실행하면

```bash
docker compose up -d
```

세 서비스가 모두 실행된다.

```text
postgres
nginx
app
```

---

## 특정 서비스만 실행하기

특정 서비스만 실행하고 싶다면 뒤에 service name을 붙이면 된다.

```bash
docker compose up postgres
```

백그라운드로 실행하려면 다음처럼 쓴다.

```bash
docker compose up -d postgres
```

이 명령어는 `postgres` service만 실행한다.

```yaml
services:
  postgres:
    image: postgres:16
```

여기서 중요한 점은 뒤에 붙이는 이름이 `container_name`이 아니라 service name이라는 점이다.

```yaml
services:
  postgres:
    image: postgres:16
    container_name: my-postgres
```

이 경우에도 실행 명령어는 보통 다음처럼 쓴다.

```bash
docker compose up -d postgres
```

`my-postgres`가 아니라 `postgres`다.

---

## 왜 부분 실행이 필요할까?

개발할 때는 전체 환경을 매번 다 띄울 필요가 없을 때가 많다.

예를 들어 Spring Boot 앱은 로컬에서 직접 실행하고, DB만 Docker로 띄우고 싶을 수 있다.

```text
Spring Boot App → 로컬에서 실행
PostgreSQL → Docker Compose로 실행
```

이럴 때는 DB만 실행하면 된다.

```bash
docker compose up -d postgres
```

그러면 로컬 Spring Boot 앱에서 Docker PostgreSQL로 접속할 수 있다.

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/appdb
```

단, 이 경우에는 Spring Boot 앱이 호스트에서 실행 중이므로 `localhost:5432`를 사용할 수 있다.

반대로 Spring Boot 앱도 컨테이너 안에서 실행 중이라면 `localhost`가 아니라 `postgres:5432`를 써야 한다.

---

## app만 실행하면 DB도 같이 실행될까?

Compose 파일에 `depends_on`이 있다면, 특정 서비스를 실행할 때 의존 서비스도 함께 실행될 수 있다.

```yaml
services:
  app:
    build: .
    depends_on:
      - postgres

  postgres:
    image: postgres:16
```

이 상태에서 다음 명령어를 실행하면

```bash
docker compose up -d app
```

Compose는 app이 postgres에 의존한다고 보고 postgres도 같이 실행할 수 있다.

하지만 여기서 주의할 점이 있다.

`depends_on`은 실행 순서를 어느 정도 제어할 뿐, PostgreSQL이 완전히 준비될 때까지 기다려주는 것은 아니다.

즉, PostgreSQL 컨테이너가 실행은 됐지만 아직 DB 접속 준비가 안 된 상태일 수 있다.

그래서 실제 운영이나 안정적인 개발 환경에서는 `healthcheck`를 함께 고려해야 한다.

---

## 개발 환경 분리

특정 서비스만 실행하는 기능은 개발 환경을 나눌 때 유용하다.

예를 들어 다음처럼 나눌 수 있다.

```text
DB만 Docker로 실행
앱은 로컬 IDE에서 실행

또는

DB + Redis만 Docker로 실행
앱은 로컬에서 디버깅

또는

전체 환경을 Docker Compose로 실행
```

개발 초기에는 보통 이런 방식이 편하다.

```bash
docker compose up -d postgres
```

그리고 앱은 IntelliJ나 VSCode에서 직접 실행한다.

이렇게 하면 앱 디버깅이 쉽고, DB는 매번 설치하지 않아도 된다.

---

## 자주 쓰는 명령어

특정 서비스 실행:

```bash
docker compose up -d postgres
```

전체 서비스 실행:

```bash
docker compose up -d
```

특정 서비스 로그 보기:

```bash
docker compose logs postgres
```

특정 서비스 중지:

```bash
docker compose stop postgres
```

특정 서비스 재시작:

```bash
docker compose restart postgres
```

특정 서비스 삭제 후 재생성:

```bash
docker compose up -d --force-recreate postgres
```

---

## 정리

Docker Compose는 전체 서비스를 한 번에 실행할 수도 있고, 특정 서비스만 실행할 수도 있다.

```bash
docker compose up -d
```

전체 실행.

```bash
docker compose up -d postgres
```

`postgres` service만 실행.

이때 기준은 `container_name`이 아니라 service name이다.

부분 실행은 개발 환경에서 매우 유용하다.

```text
DB만 Docker로 실행
앱은 로컬에서 실행
Nginx만 따로 테스트
Redis만 먼저 실행
```

Compose를 잘 쓰려면 모든 컨테이너를 무조건 한 번에 띄우는 것보다, 필요한 서비스만 골라 실행하는 흐름도 익숙해져야 한다.
