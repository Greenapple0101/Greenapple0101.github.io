---
title: "[Docker] Docker 이미지와 커스텀 빌드"
source: "https://velog.io/@yorange50/Docker-Docker-이미지와-커스텀-빌드"
published: "2026-05-14T07:28:31.597Z"
tags: ""
backup_date: "2026-05-29T14:52:52.741178"
---


# [DOCKER IMAGE] Dockerfile로 커스텀 이미지를 만드는 이유

Docker를 쓰다 보면 처음에는 공식 이미지를 그대로 사용한다.

예를 들어 PostgreSQL을 띄울 때는 이렇게 쓴다.

```yaml
services:
  postgres:
    image: postgres:16
```

Nginx를 띄울 때는 이렇게 쓴다.

```yaml
services:
  nginx:
    image: nginx:latest
```

이 방식은 빠르고 편하다.

하지만 어느 순간 이런 상황이 생긴다.

```text
PostgreSQL 설정 파일을 미리 넣고 싶다
Nginx 설정 파일을 이미지 안에 포함하고 싶다
컨테이너 안에 curl을 설치해두고 싶다
JDBC Driver 같은 파일을 이미지에 넣고 싶다
기본 이미지에 없는 라이브러리가 필요하다
```

이때 컨테이너 안에 들어가서 직접 설치하면 안 된다.

```bash
docker exec -it my-container bash
apt install curl
vi postgresql.conf
```

이렇게 하면 현재 컨테이너에는 반영될 수 있지만, 컨테이너를 다시 만들면 사라진다.

그래서 필요한 것이 **Dockerfile로 커스텀 이미지를 만드는 방식**이다.

---

## 이미지와 컨테이너의 차이

먼저 이미지와 컨테이너를 구분해야 한다.

```text
이미지
→ 컨테이너를 만들기 위한 설계도

컨테이너
→ 이미지로부터 생성된 실행 중인 인스턴스
```

예를 들어 `postgres:16` 이미지는 PostgreSQL 컨테이너를 만들기 위한 기본 설계도다.

```text
postgres:16 이미지
↓
PostgreSQL 컨테이너 생성
```

컨테이너 안에서 직접 수정하는 것은 이미지를 바꾸는 게 아니다.

그냥 현재 실행 중인 컨테이너만 바꾸는 것이다.

그래서 컨테이너가 삭제되고 다시 만들어지면 수정 내용은 사라질 수 있다.

---

## Dockerfile이란?

Dockerfile은 이미지를 만드는 방법을 적어두는 파일이다.

예를 들어 기본 PostgreSQL 이미지 위에 설정 파일을 추가하고 싶다면 이렇게 쓸 수 있다.

```dockerfile
FROM postgres:16

COPY ./config/postgresql.conf /etc/postgresql/postgresql.conf
```

이 Dockerfile은 이렇게 해석할 수 있다.

```text
postgres:16 이미지를 기반으로 하고
내 로컬의 postgresql.conf 파일을
이미지 안의 특정 경로로 복사해라
```

이제 이 Dockerfile로 이미지를 빌드하면, 설정 파일이 포함된 PostgreSQL 이미지가 만들어진다.

```bash
docker build -t my-postgres:1.0 .
```

---

## FROM postgres:16

Dockerfile의 첫 줄에는 보통 `FROM`이 온다.

```dockerfile
FROM postgres:16
```

이 뜻은 다음과 같다.

```text
postgres:16 이미지를 기반으로
새로운 이미지를 만들겠다
```

즉, 처음부터 PostgreSQL을 직접 설치하는 것이 아니다.

이미 잘 만들어진 공식 이미지를 가져와서, 그 위에 필요한 설정만 추가하는 것이다.

이걸 base image라고도 한다.

```text
base image
→ 내가 만들 이미지의 출발점이 되는 이미지
```

---

## COPY 설정 파일

설정 파일을 이미지 안에 넣고 싶다면 `COPY`를 사용한다.

```dockerfile
FROM postgres:16

COPY ./config/postgresql.conf /etc/postgresql/postgresql.conf
```

`COPY`는 로컬 파일을 이미지 안으로 복사한다.

```text
로컬 파일
./config/postgresql.conf

이미지 내부 경로
/etc/postgresql/postgresql.conf
```

이렇게 하면 컨테이너가 실행될 때 이미 설정 파일이 들어 있는 상태가 된다.

---

## RUN apt install curl

기본 이미지에 없는 패키지를 설치하고 싶다면 `RUN`을 사용한다.

예를 들어 컨테이너 안에서 `curl` 명령어가 필요하다고 해보자.

컨테이너에 들어가서 직접 설치하면 안 된다.

```bash
apt install curl
```

이렇게 하면 그 컨테이너에서만 설치된다.

올바른 방식은 Dockerfile에 적는 것이다.

```dockerfile
FROM postgres:16

RUN apt-get update && apt-get install -y curl
```

이렇게 하면 `curl`이 포함된 이미지가 만들어진다.

나중에 컨테이너를 다시 생성해도 `curl`은 계속 들어 있다.

---

## 이미지 자체를 커스터마이징한다는 뜻

커스텀 이미지를 만든다는 것은 컨테이너를 직접 고치는 것이 아니다.

컨테이너의 원본이 되는 이미지를 고치는 것이다.

```text
나쁜 방식
컨테이너 실행
→ 컨테이너 안에 들어감
→ vi로 수정
→ apt install
→ 현재 컨테이너만 변경됨

좋은 방식
Dockerfile 작성
→ 이미지 빌드
→ 컨테이너 실행
→ 항상 같은 상태로 실행됨
```

Docker 운영에서 중요한 것은 현재 떠 있는 컨테이너를 아끼는 것이 아니다.

언제든지 컨테이너를 지우고 다시 만들어도 같은 환경이 재현되는 것이다.

---

## docker-compose.yml과 연결

커스텀 이미지는 Compose에서도 사용할 수 있다.

직접 빌드하려면 `build`를 사용한다.

```yaml
services:
  postgres:
    build: .
    container_name: my-postgres
```

또는 미리 빌드한 이미지를 사용할 수도 있다.

```yaml
services:
  postgres:
    image: my-postgres:1.0
```

즉, Compose는 컨테이너 실행 구성을 담당하고, Dockerfile은 이미지 생성 방식을 담당한다.

```text
Dockerfile
→ 이미지 만드는 방법

docker-compose.yml
→ 이미지를 어떤 설정으로 실행할지
```

---

## 정리

Dockerfile로 커스텀 이미지를 만드는 이유는 컨테이너 내부 수정사항을 재현 가능하게 만들기 위해서다.

```text
설정 파일을 포함하고 싶을 때
필요한 패키지를 설치하고 싶을 때
기본 이미지에 없는 라이브러리가 필요할 때
항상 같은 실행 환경을 만들고 싶을 때
```

컨테이너 안에서 직접 수정하면 수정 내용이 사라질 수 있다.

하지만 Dockerfile에 적어두면 다시 빌드할 때마다 같은 이미지가 만들어진다.

핵심은 이것이다.

```text
컨테이너를 고치지 말고,
컨테이너를 만드는 이미지를 고쳐야 한다.
```

---

# [DOCKER IMAGE] PostgreSQL 설정파일을 이미지에 넣는 방법

PostgreSQL을 Docker로 실행할 때 설정 파일을 바꾸고 싶은 경우가 있다.

예를 들어 이런 설정 파일이다.

```text
postgresql.conf
pg_hba.conf
```

이 파일들은 PostgreSQL의 동작 방식에 영향을 준다.

```text
listen_addresses
max_connections
shared_buffers
log_statement
timezone
```

설정을 바꾸는 방법은 여러 가지가 있지만, 그중 하나는 설정 파일을 Docker 이미지 안에 넣는 방식이다.

---

## PostgreSQL 설정 파일

PostgreSQL의 대표적인 설정 파일은 `postgresql.conf`다.

이 파일에는 PostgreSQL 서버의 동작 설정이 들어간다.

예를 들면 다음과 같다.

```conf
listen_addresses = '*'
max_connections = 100
shared_buffers = 128MB
log_statement = 'all'
timezone = 'Asia/Seoul'
```

이 설정 파일을 컨테이너 안에서 직접 수정할 수도 있다.

```bash
docker exec -it my-postgres bash
vi /var/lib/postgresql/data/postgresql.conf
```

하지만 이 방식은 좋지 않다.

컨테이너가 재생성되면 수정 내용이 사라질 수 있고, 변경 이력도 남지 않는다.

그래서 Dockerfile에 설정 파일을 포함시키는 방식을 사용할 수 있다.

---

## COPY로 설정 파일 넣기

프로젝트 구조를 예로 들어보자.

```text
postgres-custom/
├── Dockerfile
└── config/
    └── postgresql.conf
```

Dockerfile은 이렇게 작성할 수 있다.

```dockerfile
FROM postgres:16

COPY ./config/postgresql.conf /etc/postgresql/postgresql.conf
```

이제 이미지를 빌드한다.

```bash
docker build -t my-postgres:1.0 .
```

그리고 Compose에서 사용한다.

```yaml
services:
  postgres:
    image: my-postgres:1.0
    environment:
      POSTGRES_DB: hellodb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
```

이렇게 하면 내가 만든 설정 파일이 포함된 PostgreSQL 이미지를 사용할 수 있다.

---

## 설정 파일 경로 주의

PostgreSQL 공식 Docker 이미지는 데이터 디렉토리와 설정 파일 경로가 실행 방식에 따라 다를 수 있다.

보통 데이터는 다음 경로를 사용한다.

```text
/var/lib/postgresql/data
```

설정 파일도 데이터 디렉토리 안에 생성될 수 있다.

그래서 단순히 파일을 복사하는 것만으로 설정이 자동 적용되지 않을 수 있다.

이럴 때는 PostgreSQL 실행 시 설정 파일 경로를 명시할 수 있다.

```yaml
services:
  postgres:
    image: my-postgres:1.0
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
```

전체 예시는 다음과 같다.

```yaml
services:
  postgres:
    image: my-postgres:1.0
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    environment:
      POSTGRES_DB: hellodb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
```

이렇게 하면 PostgreSQL이 내가 넣은 설정 파일을 사용하도록 지정할 수 있다.

---

## config bake-in 전략

설정 파일을 이미지 안에 넣는 방식을 흔히 “bake-in”이라고 표현할 수 있다.

빵을 구울 때 재료가 안에 박혀서 나오는 것처럼, 설정 파일이 이미지 안에 포함되어 있는 것이다.

```text
Dockerfile
↓
설정 파일 COPY
↓
이미지 빌드
↓
설정이 포함된 이미지 생성
```

이 방식의 장점은 이미지 하나로 같은 설정을 재현할 수 있다는 점이다.

```text
어느 서버에서 실행해도 같은 설정
컨테이너를 다시 만들어도 같은 설정
이미지 태그로 설정 버전 관리 가능
```

예를 들어 다음 이미지는 설정 버전을 포함한 이미지라고 볼 수 있다.

```text
my-postgres:1.0
my-postgres:1.1
my-postgres:prod-20260514
```

---

## volume 방식과 비교

하지만 설정 파일을 이미지에 넣는 방식이 항상 정답은 아니다.

다른 방식으로는 volume 또는 bind mount가 있다.

```yaml
services:
  postgres:
    image: postgres:16
    volumes:
      - ./config/postgresql.conf:/etc/postgresql/postgresql.conf
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
```

이 방식은 설정 파일을 이미지 안에 넣지 않고, 호스트에서 컨테이너 안으로 연결한다.

둘의 차이는 다음과 같다.

```text
Custom Image 방식
→ 설정 파일이 이미지 안에 포함됨
→ 설정 변경 시 이미지 재빌드 필요

Volume 방식
→ 설정 파일이 호스트에 있음
→ 설정 변경 후 컨테이너 재시작으로 반영 가능
```

---

## 언제 이미지에 넣을까?

PostgreSQL 설정 파일을 이미지에 넣는 방식은 이런 경우에 어울린다.

```text
설정이 자주 바뀌지 않을 때
동일한 설정으로 여러 환경에 배포해야 할 때
이미지 버전으로 설정까지 관리하고 싶을 때
운영 환경에서 파일 주입보다 이미지 불변성을 중시할 때
```

반대로 개발 중 자주 설정을 바꿔야 한다면 volume 방식이 더 편하다.

---

## 정리

PostgreSQL 설정 파일은 Dockerfile의 `COPY`로 이미지에 넣을 수 있다.

```dockerfile
FROM postgres:16

COPY ./config/postgresql.conf /etc/postgresql/postgresql.conf
```

그리고 PostgreSQL이 해당 설정 파일을 읽도록 command에서 지정할 수 있다.

```yaml
command: postgres -c config_file=/etc/postgresql/postgresql.conf
```

이 방식은 설정을 이미지 안에 포함하는 bake-in 전략이다.

```text
장점
→ 어느 환경에서도 같은 설정 재현 가능
→ 이미지 태그로 설정 버전 관리 가능

단점
→ 설정 변경 시 이미지 재빌드 필요
```

즉, 설정 변경이 잦은 개발 환경에서는 volume이 편하고, 안정적인 운영 배포에서는 custom image 방식도 고려할 수 있다.

---

# [DOCKER IMAGE] Volume 방식 vs Custom Image 방식

Docker에서 설정 파일을 관리하는 방식은 크게 두 가지로 볼 수 있다.

```text
1. Volume 또는 bind mount로 외부 파일을 연결하는 방식
2. Dockerfile로 설정 파일을 이미지에 포함하는 방식
```

둘 다 컨테이너 안에서 직접 `vi`로 수정하는 것보다 좋은 방식이다.

하지만 목적이 다르다.

---

## Volume 방식

Volume 방식은 호스트에 있는 파일이나 디렉토리를 컨테이너 안으로 연결하는 방식이다.

예를 들어 Nginx 설정 파일을 호스트에서 관리하고 싶다면 이렇게 쓸 수 있다.

```yaml
services:
  nginx:
    image: nginx:latest
    volumes:
      - ./config/default.conf:/etc/nginx/conf.d/default.conf
```

이 구조는 다음과 같다.

```text
호스트
./config/default.conf
↓
컨테이너
/etc/nginx/conf.d/default.conf
```

즉, 설정 파일은 호스트에 있고, 컨테이너는 그 파일을 가져다 쓰는 형태다.

---

## Custom Image 방식

Custom Image 방식은 Dockerfile로 설정 파일을 이미지 안에 넣는 방식이다.

```dockerfile
FROM nginx:latest

COPY ./config/default.conf /etc/nginx/conf.d/default.conf
```

그리고 이미지를 빌드한다.

```bash
docker build -t my-nginx:1.0 .
```

이 구조는 다음과 같다.

```text
Dockerfile
↓
설정 파일 COPY
↓
이미지 빌드
↓
설정 포함 이미지 생성
↓
컨테이너 실행
```

즉, 설정 파일이 이미지 안에 포함된다.

---

## 개발 편의성 비교

개발 환경에서는 Volume 방식이 편하다.

설정 파일을 바꾸고 컨테이너만 재시작하면 되기 때문이다.

```bash
vi ./config/default.conf
docker compose restart nginx
```

이미지를 다시 빌드하지 않아도 된다.

그래서 설정을 자주 바꾸는 개발 단계에서는 Volume 방식이 빠르다.

```text
Volume 방식
→ 수정이 빠름
→ 테스트가 쉬움
→ 로컬 개발에 적합
```

반면 Custom Image 방식은 설정이 바뀔 때마다 이미지를 다시 빌드해야 한다.

```bash
docker build -t my-nginx:1.1 .
docker compose up -d
```

개발 중에는 조금 번거로울 수 있다.

---

## 운영 안정성 비교

운영 환경에서는 Custom Image 방식이 더 안정적인 경우가 있다.

이유는 이미지 안에 설정이 포함되어 있어서, 어느 서버에서 실행해도 같은 설정을 사용할 수 있기 때문이다.

```text
my-nginx:1.0
→ 설정 A 포함

my-nginx:1.1
→ 설정 B 포함
```

이미지 태그를 보면 어떤 설정이 들어간 버전인지 관리할 수 있다.

반대로 Volume 방식은 호스트 파일이 제대로 존재해야 한다.

```text
호스트에 설정 파일이 없음
경로가 다름
권한이 다름
파일 내용이 서버마다 다름
```

이런 문제가 생기면 같은 이미지를 실행해도 서버마다 다르게 동작할 수 있다.

그래서 운영에서는 설정을 어떻게 배포하고 관리할지 기준이 필요하다.

---

## 설정 변경 전략

두 방식은 설정 변경 전략이 다르다.

```text
Volume 방식
설정 파일 수정
→ 컨테이너 재시작
→ 변경 반영

Custom Image 방식
설정 파일 수정
→ 이미지 재빌드
→ 새 이미지 배포
→ 컨테이너 재생성
```

Volume 방식은 빠르게 바꿀 수 있다.

Custom Image 방식은 느리지만 변경이 명확하게 버전으로 남는다.

---

## 언제 Volume을 쓸까?

Volume 방식은 이런 경우에 좋다.

```text
로컬 개발 환경
설정을 자주 바꾸는 단계
Nginx conf를 빠르게 테스트하는 상황
DB 데이터 보존
로그나 업로드 파일처럼 컨테이너 밖에 남겨야 하는 데이터
```

특히 DB 데이터는 보통 이미지에 넣는 것이 아니라 volume으로 분리한다.

```yaml
services:
  postgres:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

DB 데이터는 컨테이너가 지워져도 보존되어야 하기 때문이다.

---

## 언제 Custom Image를 쓸까?

Custom Image 방식은 이런 경우에 좋다.

```text
필요한 패키지를 이미지에 설치해야 할 때
curl, vim, JDBC Driver 같은 도구를 포함해야 할 때
설정 파일을 이미지 버전과 함께 관리하고 싶을 때
운영 배포에서 동일한 실행 환경을 보장하고 싶을 때
여러 서버에서 같은 설정을 재현해야 할 때
```

예를 들어 기본 이미지에 `curl`이 없어서 매번 컨테이너 안에서 설치하고 있다면, 이건 Dockerfile로 빼야 한다.

```dockerfile
FROM eclipse-temurin:21-jre

RUN apt-get update && apt-get install -y curl
```

이렇게 해야 컨테이너를 다시 만들어도 `curl`이 유지된다.

---

## 둘 중 하나만 써야 할까?

꼭 그렇지는 않다.

실제로는 둘을 섞어서 쓰는 경우가 많다.

예를 들어 Java 애플리케이션은 이미지로 만들고, 설정값은 환경변수로 주입할 수 있다.

```dockerfile
FROM eclipse-temurin:21-jre

COPY ./target/app.jar /app/app.jar

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

```yaml
services:
  app:
    image: my-app:1.0
    environment:
      DB_HOST: postgres
      DB_NAME: hellodb
```

이 경우 애플리케이션 실행 파일은 이미지 안에 포함하고, 환경마다 달라지는 DB 주소는 environment로 분리한다.

즉, 고정되는 것은 이미지에 넣고, 환경마다 바뀌는 것은 밖으로 빼는 전략이다.

---

## 정리

Volume 방식과 Custom Image 방식은 둘 다 컨테이너 내부 직접 수정의 대안이다.

```text
Volume 방식
→ 외부 파일을 컨테이너에 연결
→ 개발 편의성 좋음
→ 설정 변경이 빠름

Custom Image 방식
→ 설정이나 패키지를 이미지에 포함
→ 운영 재현성 좋음
→ 변경 이력이 이미지 버전으로 남음
```

기준은 이렇게 잡으면 된다.

```text
자주 바뀌는 설정
→ Volume, bind mount, environment

항상 포함되어야 하는 파일이나 패키지
→ Custom Image

컨테이너가 지워져도 남아야 하는 데이터
→ Volume

어느 환경에서나 동일해야 하는 실행 환경
→ Custom Image
```

핵심은 이것이다.

```text
컨테이너 안에서 직접 수정하지 말고,
변경의 성격에 따라 Volume과 Custom Image를 선택해야 한다.
```

---

# [DOCKER IMAGE] Java 애플리케이션은 Docker 이미지 안에서 어떻게 실행될까?

Java 애플리케이션을 Docker로 실행한다는 것은 무엇일까?

Spring Boot 프로젝트를 예로 들면, 보통 애플리케이션을 빌드하면 `.jar` 파일이 만들어진다.

```text
target/app.jar
```

또는 Gradle 프로젝트라면 다음 위치에 생길 수 있다.

```text
build/libs/app.jar
```

Docker에서는 이 jar 파일을 이미지 안에 넣고, 컨테이너가 실행될 때 Java 명령어로 실행한다.

---

## Java 애플리케이션 실행 흐름

로컬에서는 보통 이렇게 실행한다.

```bash
java -jar app.jar
```

Docker에서도 본질은 같다.

다만 jar 파일이 내 로컬이 아니라 컨테이너 이미지 안에 들어간다.

```text
Spring Boot 프로젝트
↓
Maven 또는 Gradle 빌드
↓
jar 파일 생성
↓
Dockerfile에서 jar 복사
↓
Docker 이미지 빌드
↓
컨테이너 실행
↓
java -jar app.jar 실행
```

---

## FROM jre

Java 애플리케이션을 실행하려면 Java Runtime이 필요하다.

그래서 Dockerfile의 base image로 JRE 이미지나 JDK 이미지를 사용한다.

예를 들어 실행만 할 거라면 JRE 기반 이미지를 사용할 수 있다.

```dockerfile
FROM eclipse-temurin:21-jre
```

이 뜻은 다음과 같다.

```text
Java 21 Runtime이 들어 있는 이미지를 기반으로
내 애플리케이션 이미지를 만들겠다
```

JRE는 Java 애플리케이션을 실행하기 위한 런타임이다.

반면 JDK는 컴파일과 개발 도구까지 포함한다.

```text
JRE
→ Java 실행용

JDK
→ Java 개발/컴파일용
```

이미 jar 파일을 만들어둔 상태라면 실행 이미지에는 JRE만 있어도 된다.

---

## COPY jar

이제 jar 파일을 이미지 안에 넣는다.

```dockerfile
FROM eclipse-temurin:21-jre

WORKDIR /app

COPY ./target/app.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
```

하나씩 보면 다음과 같다.

```dockerfile
WORKDIR /app
```

컨테이너 안의 작업 디렉토리를 `/app`으로 설정한다.

```dockerfile
COPY ./target/app.jar app.jar
```

로컬의 `./target/app.jar`를 이미지 안의 `/app/app.jar`로 복사한다.

```dockerfile
ENTRYPOINT ["java", "-jar", "app.jar"]
```

컨테이너가 실행될 때 `java -jar app.jar` 명령어를 실행한다.

즉, 컨테이너 실행은 결국 Java 애플리케이션 실행으로 이어진다.

---

## docker build와 docker run

Dockerfile을 작성했다면 이미지를 빌드한다.

```bash
docker build -t my-spring-app:1.0 .
```

그리고 컨테이너를 실행한다.

```bash
docker run -d -p 8080:8080 my-spring-app:1.0
```

이 흐름은 다음과 같다.

```text
docker build
→ Dockerfile을 읽어서 이미지 생성

docker run
→ 이미지로부터 컨테이너 생성 및 실행
```

컨테이너가 실행되면 내부에서 다음 명령어가 실행된다.

```bash
java -jar app.jar
```

---

## JDBC Driver 포함

Spring Boot에서 PostgreSQL을 사용한다면 JDBC Driver가 필요하다.

보통은 Dockerfile에서 직접 JDBC Driver를 넣는 것이 아니라, Maven이나 Gradle 의존성에 추가한다.

예를 들어 Maven이라면 `pom.xml`에 다음처럼 들어간다.

```xml
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <scope>runtime</scope>
</dependency>
```

Gradle이라면 다음처럼 들어간다.

```gradle
runtimeOnly 'org.postgresql:postgresql'
```

그러면 jar를 빌드할 때 필요한 의존성이 함께 포함되거나, 실행 가능한 Spring Boot jar 안에서 참조 가능하게 패키징된다.

즉, 일반적인 Spring Boot에서는 JDBC Driver를 Dockerfile에서 따로 복사하기보다 빌드 도구가 관리하게 하는 것이 자연스럽다.

하지만 특수한 경우에는 외부 jar를 이미지 안에 직접 넣을 수도 있다.

```dockerfile
COPY ./libs/postgresql-driver.jar /app/libs/postgresql-driver.jar
```

이 경우에는 실행 classpath 설정까지 함께 고려해야 한다.

---

## curl 설치

운영이나 디버깅 목적으로 컨테이너 안에 `curl`이 필요할 수 있다.

예를 들어 컨테이너 내부에서 다른 API를 호출해보고 싶을 때다.

기본 JRE 이미지에 curl이 없을 수 있다.

그럴 때 컨테이너 안에 들어가서 직접 설치하면 안 된다.

```bash
docker exec -it my-app bash
apt install curl
```

이렇게 하면 현재 컨테이너에만 반영된다.

올바른 방식은 Dockerfile에 적는 것이다.

```dockerfile
FROM eclipse-temurin:21-jre

RUN apt-get update && apt-get install -y curl

WORKDIR /app

COPY ./target/app.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
```

이렇게 하면 curl이 포함된 Java 애플리케이션 이미지가 만들어진다.

---

## runtime image 개념

Java 애플리케이션 이미지를 만들 때 중요한 개념이 runtime image다.

runtime image는 애플리케이션을 실행하는 데 필요한 것만 들어 있는 이미지다.

```text
필요한 것
Java Runtime
app.jar
필수 설정 파일
필수 인증서
필수 라이브러리

불필요한 것
소스 코드 전체
빌드 도구
테스트 파일
개발용 캐시
```

운영 환경에서는 이미지가 작고 단순할수록 좋다.

그래서 빌드는 Maven이나 Gradle이 있는 환경에서 하고, 실행 이미지는 JRE 기반으로 가볍게 만드는 경우가 많다.

예를 들어 로컬에서 먼저 빌드한다.

```bash
./mvnw clean package -DskipTests
```

그 다음 Dockerfile은 jar만 복사한다.

```dockerfile
FROM eclipse-temurin:21-jre

WORKDIR /app

COPY ./target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

이 방식은 실행에 필요한 것만 이미지에 담는 방식이다.

---

## Compose에서 Java App 실행

Java App도 Compose에 넣을 수 있다.

```yaml
services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      DB_HOST: postgres
      DB_NAME: hellodb
      DB_USER: user
      DB_PASSWORD: password
    depends_on:
      - postgres

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: hellodb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
```

이렇게 하면 Compose가 app 이미지도 빌드하고, PostgreSQL도 함께 실행할 수 있다.

단, app 컨테이너에서 DB에 접근할 때는 `localhost`가 아니라 `postgres` service name을 써야 한다.

```yaml
spring:
  datasource:
    url: jdbc:postgresql://postgres:5432/hellodb
```

---

## 정리

Java 애플리케이션을 Docker 이미지 안에서 실행하는 흐름은 단순하다.

```text
Java 프로젝트 빌드
→ jar 파일 생성
→ Dockerfile에서 JRE 이미지 사용
→ jar 파일 COPY
→ ENTRYPOINT로 java -jar 실행
```

대표적인 Dockerfile은 다음과 같다.

```dockerfile
FROM eclipse-temurin:21-jre

WORKDIR /app

COPY ./target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

필요한 도구가 있다면 Dockerfile에 포함한다.

```dockerfile
RUN apt-get update && apt-get install -y curl
```

핵심은 이것이다.

```text
Java 컨테이너는 jar 파일을 들고 있는 작은 실행 환경이다.
```

그리고 Dockerfile은 그 실행 환경을 어떻게 만들지 적어두는 설계도다.
