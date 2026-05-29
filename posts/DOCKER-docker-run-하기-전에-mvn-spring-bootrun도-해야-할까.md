---
title: "[DOCKER] docker run 하기 전에 mvn spring-boot:run도 해야 할까?"
source: "https://velog.io/@yorange50/DOCKER-docker-run-하기-전에-mvn-spring-bootrun도-해야-할까"
published: "2026-05-12T08:43:45.474Z"
tags: ""
backup_date: "2026-05-29T14:52:52.756248"
---

Spring Boot 애플리케이션을 Docker로 실행하다 보면 처음에 이런 생각이 든다.

```text
docker run -p 8080:8080으로 테스트하려면
그전에 Maven run을 해서 Spring Boot 앱을 먼저 띄워야 하는 거 아닌가?
```

나도 이 부분이 처음에는 헷갈렸다.

왜냐하면 둘 다 결국 `localhost:8080`으로 접속하기 때문이다.

```bash
./mvnw spring-boot:run
```

이렇게 실행해도 `localhost:8080`으로 접속하고,

```bash
docker run -p 8080:8080 hello-world:v1
```

이렇게 실행해도 `localhost:8080`으로 접속한다.

그래서 마치 Docker로 테스트하기 전에 Maven으로 먼저 앱을 띄워야 할 것처럼 느껴진다.

하지만 결론부터 말하면 아니다.

```text
Docker로 테스트할 때는 Maven run을 따로 하지 않아도 된다.
```

정확히는 이렇게 이해해야 한다.

```text
Maven run은 내 로컬 PC에서 Spring Boot를 실행하는 것

Docker run은 컨테이너 안에서 Spring Boot를 실행하는 것
```

둘은 같은 앱을 실행하는 서로 다른 방법이다.
둘 다 동시에 할 필요는 없다.

---

# 1. Maven run이 하는 일

먼저 Maven run부터 보자.

Spring Boot 프로젝트에서 이런 명령어를 자주 쓴다.

```bash
./mvnw spring-boot:run
```

Windows에서는 보통 이렇게 쓴다.

```powershell
.\mvnw.cmd spring-boot:run
```

이 명령어는 내 로컬 PC에서 Spring Boot 애플리케이션을 바로 실행한다.

흐름은 다음과 같다.

```text
내 PC
↓
Maven 실행
↓
Spring Boot 애플리케이션 실행
↓
내 PC의 8080 포트 사용
↓
localhost:8080 접속
```

즉 Maven run은 Docker와 상관없이 로컬 개발 환경에서 앱을 실행하는 방식이다.

예를 들어 내가 Mac에서 이 명령어를 치면, Mac 위에서 Spring Boot 앱이 실행된다.

```bash
./mvnw spring-boot:run
```

그러면 브라우저에서 다음 주소로 접근할 수 있다.

```text
http://localhost:8080
```

이때 8080 포트는 내 PC의 8080 포트다.

---

# 2. Docker run이 하는 일

이번에는 Docker run을 보자.

예를 들어 이미지를 이렇게 실행한다고 하자.

```bash
docker run -p 8080:8080 hello-world:v1
```

이 명령어는 Docker 이미지를 컨테이너로 실행한다.

흐름은 다음과 같다.

```text
내 PC
↓
Docker 실행
↓
컨테이너 생성
↓
컨테이너 안에서 Spring Boot 애플리케이션 실행
↓
컨테이너 내부 8080 포트 사용
↓
내 PC 8080 포트와 컨테이너 8080 포트 연결
↓
localhost:8080 접속
```

즉 Docker run은 내 로컬 PC에서 Spring Boot를 직접 실행하는 게 아니다.

Spring Boot는 컨테이너 안에서 실행된다.

내 PC는 그 컨테이너에 포트로 접근할 뿐이다.

---

# 3. 그럼 Docker 안에서 Spring Boot는 누가 실행할까?

여기서 중요한 질문이 나온다.

```text
Maven run을 안 하면 Spring Boot 앱은 누가 실행하지?
```

정답은 Dockerfile의 `ENTRYPOINT`다.

예를 들어 Dockerfile이 이렇게 되어 있다고 하자.

```dockerfile
FROM eclipse-temurin:21-jre

WORKDIR /app

COPY ./target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

여기서 마지막 줄이 핵심이다.

```dockerfile
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

이 의미는 다음과 같다.

```text
이 컨테이너가 실행될 때
java -jar /app/app.jar 명령어를 실행하라
```

즉 내가 아래 명령어를 치면:

```bash
docker run -p 8080:8080 hello-world:v1
```

Docker는 컨테이너를 만들고, 컨테이너 안에서 자동으로 이 명령을 실행한다.

```bash
java -jar /app/app.jar
```

그래서 Maven run을 따로 하지 않아도 Spring Boot 앱이 실행된다.

정리하면 다음과 같다.

```text
docker run
↓
컨테이너 생성
↓
ENTRYPOINT 실행
↓
java -jar /app/app.jar 실행
↓
Spring Boot 앱 실행
```

---

# 4. -p 8080:8080은 앱을 실행하는 옵션이 아니다

여기서 또 하나 중요한 점이 있다.

```bash
-p 8080:8080
```

이 옵션은 Spring Boot 앱을 실행하는 옵션이 아니다.

`-p`는 포트 연결 옵션이다.

```text
-p 내PC포트:컨테이너포트
```

예를 들어:

```bash
docker run -p 8080:8080 hello-world:v1
```

이건 이렇게 읽는다.

```text
내 PC의 8080 포트로 들어온 요청을
컨테이너 내부의 8080 포트로 보내라
```

즉 `-p`는 길을 뚫어주는 역할이다.

Spring Boot 앱을 실행하는 역할은 `ENTRYPOINT`가 한다.

둘의 역할을 나누면 이렇게 된다.

```text
ENTRYPOINT
컨테이너 안에서 Spring Boot 앱 실행

-p 8080:8080
내 PC와 컨테이너 사이의 포트 연결
```

그래서 `-p 8080:8080`만 있다고 앱이 자동으로 생기는 건 아니다.

이미지 안에 실행 가능한 jar가 있어야 하고, Dockerfile에 실행 명령이 있어야 한다.

---

# 5. Maven run과 Docker run은 둘 중 하나만 하면 된다

처음에는 이렇게 생각하기 쉽다.

```text
1. ./mvnw spring-boot:run으로 앱을 띄운다.
2. docker run -p 8080:8080으로 Docker 테스트를 한다.
```

하지만 이건 보통 틀린 흐름이다.

왜냐하면 둘 다 Spring Boot 앱을 실행하는 방법이기 때문이다.

Maven run은 로컬에서 실행한다.

```bash
./mvnw spring-boot:run
```

Docker run은 컨테이너에서 실행한다.

```bash
docker run -p 8080:8080 hello-world:v1
```

둘 다 실행하면 같은 앱이 두 군데에서 실행되려고 한다.

```text
로컬 PC에서 Spring Boot 실행
컨테이너 안에서도 Spring Boot 실행
```

특히 둘 다 8080 포트를 쓰려고 하면 문제가 생길 수 있다.

---

# 6. 둘 다 실행하면 포트 충돌이 날 수 있다

만약 먼저 Maven run을 실행했다고 하자.

```bash
./mvnw spring-boot:run
```

그러면 내 PC의 8080 포트는 이미 사용 중이다.

이 상태에서 Docker를 이렇게 실행하면:

```bash
docker run -p 8080:8080 hello-world:v1
```

Docker도 내 PC의 8080 포트를 사용하려고 한다.

하지만 이미 Maven으로 실행한 Spring Boot 앱이 8080을 쓰고 있다.

그러면 이런 에러가 날 수 있다.

```text
Bind for 0.0.0.0:8080 failed: port is already allocated
```

또는 비슷하게 이런 메시지를 볼 수 있다.

```text
port is already allocated
```

이 뜻은 간단하다.

```text
내 PC의 8080 포트는 이미 다른 프로세스가 쓰고 있다.
그래서 Docker가 8080 포트를 사용할 수 없다.
```

즉 Docker로 테스트하려면 Maven run으로 띄운 앱을 꺼야 한다.

또는 Docker 쪽의 내 PC 포트를 바꿔야 한다.

예를 들어:

```bash
docker run -p 9090:8080 hello-world:v1
```

이렇게 하면 내 PC의 9090 포트를 컨테이너 8080 포트에 연결한다.

그러면 접속 주소는 다음과 같다.

```text
http://localhost:9090
```

---

# 7. Maven build와 Maven run을 구분해야 한다

여기서 제일 중요한 개념이 있다.

```text
Maven build와 Maven run은 다르다.
```

Maven run은 앱을 실행하는 것이다.

```bash
./mvnw spring-boot:run
```

Maven build는 jar 파일을 만드는 것이다.

```bash
./mvnw clean package -DskipTests
```

둘은 역할이 다르다.

```text
Maven run
로컬에서 Spring Boot 앱 실행

Maven build
Spring Boot 앱을 jar 파일로 패키징
```

Docker를 사용할 때 필요한 것은 상황에 따라 다르다.

단일 Dockerfile 방식에서는 Docker build 전에 Maven build가 필요하다.

하지만 Maven run은 필요하지 않다.

---

# 8. 단일 Dockerfile 방식의 순서

예를 들어 Dockerfile이 이렇게 생겼다고 하자.

```dockerfile
FROM eclipse-temurin:21-jre

WORKDIR /app

COPY ./target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

이 Dockerfile은 직접 Maven build를 하지 않는다.

그냥 이미 만들어진 jar 파일을 복사한다.

```dockerfile
COPY ./target/*.jar app.jar
```

즉 이 방식에서는 먼저 jar 파일을 만들어야 한다.

그래서 순서는 다음과 같다.

```bash
./mvnw clean package -DskipTests
```

```bash
docker build -t hello-world:v1 .
```

```bash
docker run -p 8080:8080 hello-world:v1
```

흐름으로 보면 이렇게 된다.

```text
1. Maven build
   jar 파일 생성

2. Docker build
   jar 파일을 이미지 안에 복사

3. Docker run
   컨테이너 안에서 java -jar 실행
```

여기서 필요한 것은 Maven run이 아니라 Maven build다.

```text
필요한 것:
./mvnw clean package -DskipTests

필요 없는 것:
./mvnw spring-boot:run
```

---

# 9. 멀티 스테이지 Dockerfile 방식의 순서

이번에는 멀티 스테이지 Dockerfile을 보자.

```dockerfile
FROM maven:3.9-eclipse-temurin-21 AS build

WORKDIR /workspace

COPY pom.xml .

RUN mvn -B -q dependency:go-offline

COPY src ./src

RUN mvn -B -q -DskipTests package

FROM eclipse-temurin:21-jre

WORKDIR /app

COPY --from=build /workspace/target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

이 방식은 Docker build 안에서 Maven build를 수행한다.

이 부분이 그 역할을 한다.

```dockerfile
RUN mvn -B -q -DskipTests package
```

그래서 로컬에서 따로 Maven build를 할 필요가 없다.

바로 Docker build를 하면 된다.

```bash
docker build -t hello-world:v1 .
```

그 다음 실행한다.

```bash
docker run -p 8080:8080 hello-world:v1
```

흐름은 다음과 같다.

```text
1. Docker build 실행

2. Docker build 내부에서 Maven build 수행

3. jar 파일 생성

4. Runtime 이미지에 jar만 복사

5. Docker 이미지 생성

6. Docker run 실행

7. 컨테이너 안에서 java -jar 실행
```

이 방식에서도 Maven run은 필요 없다.

```text
멀티 스테이지 방식:
Docker build 안에서 Maven build
Docker run으로 컨테이너 실행
Maven run은 필요 없음
```

---

# 10. 상황별 명령어 정리

이제 상황별로 정리해보자.

## 1. 로컬에서 그냥 Spring Boot 실행하고 싶을 때

```bash
./mvnw spring-boot:run
```

이건 Docker를 쓰지 않는다.

흐름은 다음과 같다.

```text
로컬 PC에서 Spring Boot 실행
localhost:8080 접속
```

---

## 2. jar 파일을 만들어서 직접 실행하고 싶을 때

```bash
./mvnw clean package -DskipTests
```

```bash
java -jar target/*.jar
```

흐름은 다음과 같다.

```text
Maven build
jar 생성
java -jar로 로컬 실행
localhost:8080 접속
```

---

## 3. 단일 Dockerfile 방식으로 실행하고 싶을 때

Dockerfile:

```dockerfile
FROM eclipse-temurin:21-jre

WORKDIR /app

COPY ./target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

명령어:

```bash
./mvnw clean package -DskipTests
```

```bash
docker build -t hello-world:v1 .
```

```bash
docker run -p 8080:8080 hello-world:v1
```

흐름:

```text
Maven build
→ Docker build
→ Docker run
```

여기서 Maven run은 안 한다.

---

## 4. 멀티 스테이지 Dockerfile 방식으로 실행하고 싶을 때

Dockerfile:

```dockerfile
FROM maven:3.9-eclipse-temurin-21 AS build

WORKDIR /workspace

COPY pom.xml .

RUN mvn -B -q dependency:go-offline

COPY src ./src

RUN mvn -B -q -DskipTests package

FROM eclipse-temurin:21-jre

WORKDIR /app

COPY --from=build /workspace/target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

명령어:

```bash
docker build -t hello-world:v1 .
```

```bash
docker run -p 8080:8080 hello-world:v1
```

흐름:

```text
Docker build
  └─ 내부에서 Maven build
→ Docker run
```

여기서도 Maven run은 안 한다.

---

# 11. localhost:8080은 같지만 실행 위치가 다르다

헷갈리는 이유는 둘 다 접속 주소가 같기 때문이다.

Maven run을 해도:

```text
http://localhost:8080
```

Docker run을 해도:

```text
http://localhost:8080
```

하지만 내부 구조는 다르다.

## Maven run

```text
브라우저
↓
localhost:8080
↓
내 PC에서 실행 중인 Spring Boot
```

## Docker run

```text
브라우저
↓
localhost:8080
↓
내 PC 8080 포트
↓
Docker 포트 매핑
↓
컨테이너 내부 8080 포트
↓
컨테이너 안에서 실행 중인 Spring Boot
```

즉 주소는 같아 보여도 실행 위치가 다르다.

```text
Maven run:
내 PC에서 실행

Docker run:
컨테이너 안에서 실행
```

---

# 12. 그럼 언제 Maven run을 쓰고 언제 Docker run을 쓸까?

개발 초반에는 Maven run이 편하다.

코드를 고치고 바로 실행하기 쉽기 때문이다.

```bash
./mvnw spring-boot:run
```

하지만 Docker 이미지로 잘 실행되는지 확인하려면 Docker run을 해야 한다.

```bash
docker run -p 8080:8080 hello-world:v1
```

각각의 목적은 다르다.

```text
Maven run:
로컬 개발 중 빠른 실행

Docker run:
컨테이너 환경에서 실행 검증

Maven build:
jar 생성 검증

Docker build:
이미지 생성 검증
```

실무 흐름으로 가면 보통 이렇게 생각한다.

```text
개발 중:
Maven run으로 빠르게 확인

배포 전:
Maven build 또는 Docker build로 패키징 확인

컨테이너 검증:
Docker run으로 실제 컨테이너 실행 확인
```

---

# 13. 실수하기 쉬운 흐름

처음에는 이런 식으로 실행하기 쉽다.

```bash
./mvnw spring-boot:run
docker run -p 8080:8080 hello-world:v1
```

하지만 이건 보통 필요 없다.

오히려 포트 충돌을 만든다.

잘못된 흐름:

```text
Maven run으로 로컬 앱 실행
Docker run으로 컨테이너 앱 실행
둘 다 8080 사용
포트 충돌
```

올바른 흐름은 둘 중 하나다.

로컬 테스트만 할 거면:

```bash
./mvnw spring-boot:run
```

Docker 테스트를 할 거면:

```bash
docker run -p 8080:8080 hello-world:v1
```

단, 단일 Dockerfile 방식에서는 Docker run 전에 jar를 만들어야 하므로 Maven build는 해야 한다.

```bash
./mvnw clean package -DskipTests
docker build -t hello-world:v1 .
docker run -p 8080:8080 hello-world:v1
```

---

# 14. 머릿속에 이렇게 넣으면 된다

가장 깔끔한 정리는 이것이다.

```text
Maven build = jar 만들기
Maven run = 로컬에서 Spring Boot 실행하기

Docker build = 이미지 만들기
Docker run = 컨테이너에서 Spring Boot 실행하기
```

그래서 `docker run -p 8080:8080`을 테스트할 때 필요한 건 Maven run이 아니다.

Dockerfile 방식에 따라 Maven build가 필요할 수 있을 뿐이다.

```text
단일 Dockerfile:
Maven build 필요
Maven run 불필요

멀티 스테이지 Dockerfile:
Maven build도 Docker 안에서 함
Maven run 불필요
```

---

# 15. 최종 정리

Docker로 Spring Boot 앱을 테스트할 때는 Maven run을 먼저 할 필요가 없다.

Maven run은 내 로컬 PC에서 Spring Boot 앱을 실행하는 명령어다.

```bash
./mvnw spring-boot:run
```

Docker run은 Docker 컨테이너 안에서 Spring Boot 앱을 실행하는 명령어다.

```bash
docker run -p 8080:8080 hello-world:v1
```

이 둘은 같은 앱을 실행하는 서로 다른 방식이다.

둘 다 동시에 실행하면 오히려 8080 포트 충돌이 날 수 있다.

중요한 것은 `-p 8080:8080`의 의미다.

```text
내 PC의 8080 포트와
컨테이너 내부의 8080 포트를 연결한다
```

그리고 컨테이너 안에서 실제로 Spring Boot 앱을 실행하는 것은 Dockerfile의 `ENTRYPOINT`다.

```dockerfile
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

따라서 Docker 실행 흐름은 다음과 같다.

```text
docker run
↓
컨테이너 생성
↓
ENTRYPOINT 실행
↓
java -jar /app/app.jar 실행
↓
Spring Boot 앱이 컨테이너 내부 8080에서 실행
↓
-p 8080:8080에 의해 내 PC localhost:8080으로 접근 가능
```

한 줄로 정리하면 이렇다.

```text
Docker로 테스트할 때 Maven run은 필요 없다.
Docker run이 컨테이너 안에서 Spring Boot 앱을 실행한다.
단, jar만 복사하는 Dockerfile이라면 Docker build 전에 Maven build는 필요하다.
```
