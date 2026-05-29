---
title: "[Docker] Docker 네트워크와 컨테이너 통신"
source: "https://velog.io/@yorange50/Docker-Docker-네트워크와-컨테이너-통신"
published: "2026-05-14T07:26:31.259Z"
tags: ""
backup_date: "2026-05-29T14:52:52.741493"
---

아래 4편은 그대로 벨로그에 나눠 올리면 된다. 오늘 메모 흐름상 `localhost → 같은 네트워크 → host.docker.internal → 외부 DB 접근 방식` 순서가 제일 자연스럽다. 수업 메모에서도 컨테이너 내부의 `localhost`는 자기 컨테이너를 의미하고, 다른 컨테이너나 호스트로 접근하려면 서비스명·컨테이너명·`host.docker.internal`·IP 등을 구분해야 한다는 흐름이 정리되어 있다. 

---

# [DOCKER NETWORK] localhost가 안 되는 이유

Docker로 Spring Boot App과 PostgreSQL을 같이 띄우다 보면 이런 실수를 자주 한다.

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/hellodb
```

로컬에서 PostgreSQL을 직접 설치해서 실행할 때는 이 설정이 잘 된다.

그런데 PostgreSQL도 컨테이너로 띄우고, Spring Boot App도 컨테이너로 띄우면 갑자기 연결이 안 된다.

처음에는 이런 생각이 든다.

```text
PostgreSQL 포트는 5432인데?
localhost:5432면 되는 거 아닌가?
```

하지만 Docker 컨테이너 환경에서는 `localhost`의 의미를 다시 봐야 한다.

---

## localhost의 진짜 의미

`localhost`는 “내 컴퓨터”라는 뜻처럼 보이지만, 더 정확히 말하면 **현재 실행 중인 자기 자신**을 가리킨다.

일반적인 로컬 개발 환경에서는 Spring Boot App과 PostgreSQL이 같은 노트북에서 실행된다.

```text
내 노트북
├── Spring Boot App
└── PostgreSQL
```

이때 Spring Boot App 입장에서 `localhost:5432`는 같은 노트북 안의 PostgreSQL을 의미한다.

그래서 잘 된다.

하지만 Docker로 가면 구조가 달라진다.

---

## 컨테이너 격리

Docker 컨테이너는 서로 격리된 실행 환경이다.

예를 들어 다음과 같은 구조가 있다고 해보자.

```text
내 노트북
├── app 컨테이너
│   └── Spring Boot App
└── postgres 컨테이너
    └── PostgreSQL
```

겉으로 보면 같은 노트북 위에서 실행되고 있지만, 각 컨테이너는 자기만의 네트워크 공간을 가진다.

즉, app 컨테이너 안에서 보는 `localhost`와 postgres 컨테이너 안에서 보는 `localhost`는 다르다.

---

## app 컨테이너에서 localhost란?

app 컨테이너 안에서 다음 주소를 사용한다고 해보자.

```text
localhost:5432
```

이건 PostgreSQL 컨테이너를 가리키는 게 아니다.

app 컨테이너 자기 자신을 가리킨다.

```text
app 컨테이너
└── localhost:5432
```

즉, app 컨테이너 안에 5432 포트로 PostgreSQL이 떠 있어야 연결된다.

하지만 실제 PostgreSQL은 다른 컨테이너에 있다.

```text
postgres 컨테이너
└── PostgreSQL :5432
```

그래서 app 컨테이너에서 `localhost:5432`로 접속하면 실패한다.

---

## 자기 자신을 바라본다는 뜻

핵심은 이것이다.

```text
컨테이너 안의 localhost는 호스트 PC가 아니다.
컨테이너 안의 localhost는 자기 컨테이너 자신이다.
```

그래서 다음 설정은 컨테이너 환경에서는 틀릴 가능성이 높다.

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/hellodb
```

Spring Boot App이 컨테이너 안에서 실행 중이라면, DB 주소는 보통 이렇게 써야 한다.

```yaml
spring:
  datasource:
    url: jdbc:postgresql://postgres:5432/hellodb
```

여기서 `postgres`는 Docker Compose의 service name이다.

---

## 로컬 실행과 컨테이너 실행의 차이

정리하면 이렇게 나뉜다.

```text
Spring Boot App을 로컬에서 실행
PostgreSQL만 Docker로 실행
→ localhost:5432 가능

Spring Boot App도 Docker 컨테이너
PostgreSQL도 Docker 컨테이너
→ localhost:5432 불가능
→ postgres:5432 사용
```

즉, 중요한 기준은 “내 앱이 어디서 실행 중인가?”이다.

앱이 내 노트북에서 실행 중이면 `localhost`는 내 노트북이다.

앱이 컨테이너 안에서 실행 중이면 `localhost`는 그 컨테이너다.

---

## 정리

Docker에서 `localhost`가 안 되는 이유는 컨테이너가 격리되어 있기 때문이다.

```text
로컬에서 localhost
→ 내 노트북

컨테이너 안에서 localhost
→ 그 컨테이너 자기 자신
```

그래서 app 컨테이너에서 DB 컨테이너로 접속할 때는 `localhost`를 쓰면 안 된다.

대신 같은 Docker Network 안에서 service name을 사용해야 한다.

```text
localhost:5432
→ app 컨테이너 자기 자신을 봄

postgres:5432
→ postgres service를 찾아감
```

Docker 네트워크를 이해할 때 가장 먼저 잡아야 하는 개념은 이것이다.

```text
컨테이너 안의 localhost는 내 PC가 아니라 자기 자신이다.
```

---

# [DOCKER NETWORK] 컨테이너끼리는 어떻게 통신할까?

Docker Compose로 여러 컨테이너를 실행하면, 컨테이너끼리 서로 통신해야 하는 경우가 많다.

예를 들어 이런 구조가 있다.

```text
Spring Boot App 컨테이너
↓
PostgreSQL 컨테이너
```

Spring Boot App은 DB에 접속해야 한다.

그런데 이때 `localhost:5432`를 쓰면 안 된다.

그럼 컨테이너끼리는 어떻게 서로를 찾을까?

답은 **Docker Network**다.

---

## Docker Network란?

Docker Network는 컨테이너들이 서로 통신할 수 있게 해주는 가상의 네트워크다.

컨테이너는 기본적으로 격리되어 있다.

하지만 같은 Docker Network에 들어가 있으면 서로 이름으로 접근할 수 있다.

```text
Docker Network
├── app 컨테이너
└── postgres 컨테이너
```

이렇게 같은 네트워크 안에 있으면 app 컨테이너는 postgres 컨테이너를 찾을 수 있다.

---

## Docker Compose는 기본 네트워크를 만든다

Docker Compose를 사용하면 보통 별도로 네트워크를 만들지 않아도 된다.

Compose가 프로젝트 단위로 기본 네트워크를 만들어준다.

예를 들어 다음 파일이 있다고 해보자.

```yaml
services:
  app:
    build: .

  postgres:
    image: postgres:16
```

이 두 service는 같은 Compose 프로젝트 안에 있으므로 기본적으로 같은 네트워크에 들어간다.

그래서 app 컨테이너에서 postgres 컨테이너로 접근할 수 있다.

---

## service name 기반 DNS

Docker Compose에서는 service name이 DNS 이름처럼 동작한다.

```yaml
services:
  postgres:
    image: postgres:16
```

여기서 `postgres`가 service name이다.

같은 네트워크 안의 다른 컨테이너는 이 이름으로 접근할 수 있다.

```text
postgres:5432
```

즉, app 컨테이너에서 DB 접속 주소를 이렇게 쓸 수 있다.

```yaml
spring:
  datasource:
    url: jdbc:postgresql://postgres:5432/hellodb
```

여기서 `postgres`는 IP 주소가 아니다.

Docker 네트워크 안에서 해석되는 이름이다.

---

## DNS처럼 동작한다는 뜻

DNS는 이름을 IP 주소로 바꿔주는 시스템이다.

예를 들어 우리가 웹사이트에 접속할 때 IP를 직접 외우지 않는다.

```text
google.com
naver.com
github.com
```

이런 이름을 사용한다.

Docker Network 안에서도 비슷한 일이 일어난다.

```text
postgres
→ postgres 컨테이너의 내부 IP로 해석
```

그래서 app 컨테이너는 PostgreSQL 컨테이너의 IP를 몰라도 된다.

그냥 service name을 사용하면 된다.

---

## my-postgres:5432 방식

Compose에서 `container_name`을 지정했다면 그 이름으로 접근하는 경우도 있다.

```yaml
services:
  postgres:
    image: postgres:16
    container_name: my-postgres
```

그러면 같은 네트워크 안에서 다음처럼 접근할 수도 있다.

```text
my-postgres:5432
```

하지만 Compose에서는 보통 service name을 기준으로 생각하는 것이 더 좋다.

```text
권장
postgres:5432

가능한 경우 있음
my-postgres:5432
```

왜냐하면 `depends_on`, `docker compose up postgres` 같은 Compose 명령은 service name을 기준으로 동작하기 때문이다.

---

## 같은 네트워크에 있어야 한다

중요한 조건이 있다.

컨테이너끼리 이름으로 통신하려면 같은 Docker Network 안에 있어야 한다.

```text
같은 네트워크
app → postgres 접근 가능

다른 네트워크
app → postgres 이름 해석 실패 가능
```

Compose 파일이 하나라면 보통 같은 네트워크에 들어간다.

하지만 Compose 파일이 여러 개이거나, 컨테이너를 따로 실행했다면 네트워크가 다를 수 있다.

이때는 명시적으로 같은 네트워크에 넣어줘야 한다.

```yaml
services:
  app:
    build: .
    networks:
      - app-network

  postgres:
    image: postgres:16
    networks:
      - app-network

networks:
  app-network:
```

이렇게 하면 두 컨테이너는 `app-network`라는 같은 네트워크 안에 들어간다.

---

## 정리

컨테이너끼리 통신하려면 Docker Network를 이해해야 한다.

```text
컨테이너는 기본적으로 격리됨
같은 Docker Network에 있으면 서로 통신 가능
Docker Compose는 기본 네트워크를 자동 생성
service name이 DNS 이름처럼 동작
```

그래서 app 컨테이너에서 PostgreSQL 컨테이너로 접속할 때는 보통 이렇게 쓴다.

```text
postgres:5432
```

Spring Boot 설정으로 쓰면 다음과 같다.

```yaml
spring:
  datasource:
    url: jdbc:postgresql://postgres:5432/hellodb
```

핵심은 이것이다.

```text
컨테이너끼리는 localhost가 아니라 service name으로 통신한다.
```

---

# [DOCKER NETWORK] host.docker.internal은 무엇인가?

Docker 컨테이너 안에서 호스트 PC로 접근해야 할 때가 있다.

예를 들어 PostgreSQL은 내 MacBook에서 직접 실행 중이고, Spring Boot App만 Docker 컨테이너로 띄운 상황을 생각해보자.

```text
내 MacBook
├── PostgreSQL :5432
└── app 컨테이너
    └── Spring Boot App
```

이때 app 컨테이너에서 PostgreSQL에 접속하려고 `localhost:5432`를 쓰면 안 된다.

왜냐하면 컨테이너 안의 `localhost`는 내 MacBook이 아니라 app 컨테이너 자신이기 때문이다.

이럴 때 사용할 수 있는 특수한 주소가 있다.

```text
host.docker.internal
```

---

## 컨테이너에서 호스트 접근

`host.docker.internal`은 컨테이너 안에서 호스트 PC를 가리키기 위한 특별한 호스트 이름이다.

즉, 컨테이너 안에서 다음처럼 접근할 수 있다.

```text
host.docker.internal:5432
```

이 말은 다음과 같다.

```text
컨테이너 밖으로 나가서
호스트 PC의 5432 포트로 접근해라
```

Spring Boot 설정으로 쓰면 이렇게 된다.

```yaml
spring:
  datasource:
    url: jdbc:postgresql://host.docker.internal:5432/hellodb
```

이 구조는 PostgreSQL이 컨테이너가 아니라 내 PC에서 실행 중일 때 유용하다.

---

## localhost와 차이

`localhost`와 `host.docker.internal`의 차이는 명확하다.

```text
localhost
→ 컨테이너 자기 자신

host.docker.internal
→ 컨테이너를 실행한 호스트 PC
```

예를 들어 app 컨테이너 안에서 다음 주소를 쓴다고 해보자.

```text
localhost:5432
```

이건 app 컨테이너 안의 5432 포트를 찾는다.

하지만 PostgreSQL은 app 컨테이너 안에 없다.

반면 다음 주소는 다르다.

```text
host.docker.internal:5432
```

이건 컨테이너 밖의 호스트 PC로 나가서 5432 포트를 찾는다.

---

## Mac/Windows 전용 특징

`host.docker.internal`은 Docker Desktop 환경에서 주로 사용된다.

즉, Mac이나 Windows에서 Docker Desktop을 사용할 때 자연스럽게 지원된다.

하지만 Linux에서는 기본적으로 동작하지 않는 경우가 있다.

왜냐하면 Mac/Windows의 Docker Desktop은 내부적으로 가상 머신 위에서 Docker Engine을 돌리는 구조이고, 이때 호스트로 돌아가기 위한 특별한 이름을 제공하기 때문이다.

그래서 다음처럼 정리할 수 있다.

```text
Mac Docker Desktop
→ host.docker.internal 사용 가능

Windows Docker Desktop
→ host.docker.internal 사용 가능

Linux Docker Engine
→ 기본 지원이 안 될 수 있음
→ 별도 설정 필요할 수 있음
```

Linux에서는 `--add-host=host.docker.internal:host-gateway` 같은 설정을 추가해서 사용하는 경우가 있다.

Compose에서는 예를 들어 이렇게 쓸 수 있다.

```yaml
services:
  app:
    build: .
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

---

## Docker Engine 내부 동작 느낌

컨테이너는 독립된 네트워크 공간에서 실행된다.

그래서 컨테이너 입장에서 호스트 PC는 그냥 자동으로 `localhost`가 아니다.

Docker Desktop은 이 간극을 줄이기 위해 `host.docker.internal`이라는 특별한 이름을 제공한다.

```text
컨테이너
↓
host.docker.internal
↓
호스트 PC
```

즉, 이 주소는 일반 인터넷 도메인이라기보다 Docker가 제공하는 특수한 내부 이름에 가깝다.

---

## 언제 써야 할까?

`host.docker.internal`은 이런 상황에서 쓴다.

```text
앱은 컨테이너에서 실행
DB는 호스트 PC에서 실행

앱은 컨테이너에서 실행
외부 API 테스트 서버는 호스트 PC에서 실행

컨테이너에서 로컬 개발 서버에 접근
```

예를 들어 Vite 프론트엔드 서버가 내 Mac에서 `5173` 포트로 떠 있고, 백엔드 컨테이너가 거기에 접근해야 한다면 다음처럼 생각할 수 있다.

```text
host.docker.internal:5173
```

---

## 정리

`host.docker.internal`은 컨테이너에서 호스트 PC로 접근할 때 사용하는 특별한 주소다.

```text
localhost
→ 컨테이너 자기 자신

host.docker.internal
→ 컨테이너 밖의 호스트 PC
```

Mac/Windows Docker Desktop에서는 편하게 사용할 수 있다.

Linux에서는 기본 동작이 다를 수 있으므로 별도 설정이 필요할 수 있다.

핵심은 이것이다.

```text
컨테이너 안에서 내 PC를 보고 싶을 때 host.docker.internal을 쓴다.
```

---

# [DOCKER NETWORK] 컨테이너에서 외부 DB로 접속하는 3가지 방법

Docker 컨테이너에서 DB에 접속할 때는 DB가 어디에 있느냐에 따라 주소가 달라진다.

무조건 `localhost:5432`를 쓰면 안 된다.

DB가 같은 Compose 네트워크 안에 있는지, 호스트 PC에 있는지, 아예 외부 서버에 있는지를 구분해야 한다.

대표적인 방법은 세 가지다.

```text
1. service name으로 접근
2. host.docker.internal 사용
3. 실제 IP 또는 DNS 사용
```

---

## 1. service name으로 접근

첫 번째는 같은 Docker Network 안의 컨테이너로 접근하는 방식이다.

예를 들어 Spring Boot App과 PostgreSQL이 같은 `docker-compose.yml` 안에 있다고 해보자.

```yaml
services:
  app:
    build: .
    depends_on:
      - postgres

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: hellodb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
```

이 경우 app 컨테이너에서 PostgreSQL로 접근할 때는 service name을 쓴다.

```text
postgres:5432
```

Spring Boot 설정은 이렇게 된다.

```yaml
spring:
  datasource:
    url: jdbc:postgresql://postgres:5432/hellodb
    username: user
    password: password
```

이 방식은 같은 Compose 네트워크 안에서 가장 자연스러운 방식이다.

---

## 2. host.docker.internal 사용

두 번째는 DB가 호스트 PC에서 실행 중인 경우다.

예를 들어 PostgreSQL은 내 노트북에서 직접 실행 중이고, Spring Boot App만 컨테이너에서 실행 중이라고 해보자.

```text
내 노트북
├── PostgreSQL :5432
└── app 컨테이너
```

이때 app 컨테이너에서 `localhost:5432`를 쓰면 안 된다.

`localhost`는 app 컨테이너 자신을 의미하기 때문이다.

이 경우에는 다음 주소를 쓴다.

```text
host.docker.internal:5432
```

Spring Boot 설정은 이렇게 된다.

```yaml
spring:
  datasource:
    url: jdbc:postgresql://host.docker.internal:5432/hellodb
```

이 방식은 Mac/Windows Docker Desktop 환경에서 특히 자주 사용된다.

---

## 3. 실제 IP 사용

세 번째는 DB가 외부 서버에 있는 경우다.

예를 들어 PostgreSQL이 개발 서버나 클라우드 VM에 떠 있다고 해보자.

```text
app 컨테이너
↓
외부 DB 서버
```

이 경우에는 DB 서버의 실제 IP를 사용할 수 있다.

```text
192.168.0.25:5432
```

또는 클라우드 서버라면 이런 식일 수 있다.

```text
10.0.1.15:5432
```

Spring Boot 설정은 이렇게 된다.

```yaml
spring:
  datasource:
    url: jdbc:postgresql://192.168.0.25:5432/hellodb
```

하지만 실제 IP를 직접 쓰는 방식에는 주의할 점이 있다.

---

## DHCP와 IP 변경 문제

집이나 사무실 네트워크에서는 DHCP를 사용하는 경우가 많다.

DHCP는 기기에 IP를 자동으로 할당해주는 방식이다.

문제는 IP가 고정이 아닐 수 있다는 점이다.

```text
오늘 DB 서버 IP
192.168.0.25

내일 DB 서버 IP
192.168.0.31
```

이렇게 IP가 바뀌면 컨테이너의 DB 접속 설정도 깨진다.

그래서 실제 운영 환경에서는 IP를 직접 박아 넣는 것보다 DNS 이름을 사용하는 편이 좋다.

---

## DNS 개념 연결

DNS는 이름을 IP 주소로 바꿔주는 시스템이다.

예를 들어 DB 서버에 이런 DNS 이름이 있다고 해보자.

```text
dev-postgres.company.internal
```

그러면 애플리케이션 설정은 이렇게 쓸 수 있다.

```yaml
spring:
  datasource:
    url: jdbc:postgresql://dev-postgres.company.internal:5432/hellodb
```

이렇게 하면 실제 IP가 바뀌어도 DNS만 올바르게 관리되면 애플리케이션 설정을 바꾸지 않아도 된다.

Docker Compose 안에서 service name이 DNS처럼 동작하는 것도 이 개념과 연결된다.

```text
Docker Network 내부
postgres → postgres 컨테이너 IP

회사 내부망
dev-postgres.company.internal → DB 서버 IP
```

결국 핵심은 직접 IP를 외우는 것이 아니라, 이름을 통해 대상을 찾는 것이다.

---

## 세 가지 방식 비교

| 상황                     | 사용 주소                       |
| ---------------------- | --------------------------- |
| DB도 같은 Compose 안의 컨테이너 | `postgres:5432`             |
| DB가 내 호스트 PC에서 실행 중    | `host.docker.internal:5432` |
| DB가 외부 서버에 있음          | `실제 IP:5432` 또는 `DNS:5432`  |

---

## 정리

컨테이너에서 DB에 접속할 때는 DB의 위치를 먼저 봐야 한다.

```text
DB가 같은 Docker Network 안에 있다
→ service name 사용

DB가 내 PC에 있다
→ host.docker.internal 사용

DB가 외부 서버에 있다
→ IP 또는 DNS 사용
```

가장 흔한 실수는 컨테이너 안에서 무조건 `localhost`를 쓰는 것이다.

```text
컨테이너 안의 localhost
→ 컨테이너 자기 자신
```

그래서 DB가 다른 곳에 있다면 다른 주소를 써야 한다.

Docker 네트워크를 이해한다는 것은 결국 이 질문에 답할 수 있다는 뜻이다.

```text
내 애플리케이션은 어디에서 실행 중이고,
DB는 어디에서 실행 중인가?
```

이 위치 관계를 이해하면 `localhost`, `postgres`, `host.docker.internal`, 실제 IP, DNS를 상황에 맞게 구분해서 사용할 수 있다.
