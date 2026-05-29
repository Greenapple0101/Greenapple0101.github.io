---
title: "[CI/CD] 도커 빌드 런 메이븐 빌드 런 순서가 어케 되는지"
source: "https://velog.io/@yorange50/CICD-도커-빌드-런-메이븐-빌드-런-순서가-어케-되는지"
published: "2026-05-12T08:07:32.451Z"
tags: ""
backup_date: "2026-05-29T14:52:52.757240"
---


# 1. Maven만 쓸 때 순서

Docker 없이 Spring Boot를 그냥 로컬에서 실행하면 이렇게 간다.

```bash
./mvnw spring-boot:run
```

이건 쉽게 말하면:

```text
Maven이 Spring Boot 앱을 바로 실행함
```

이 경우 jar 파일을 명시적으로 만들지 않아도 된다.

흐름은 이렇다.

```text
소스코드
↓
Maven이 컴파일
↓
Spring Boot 앱 실행
↓
localhost:8080 접속
```

즉 이건 **개발할 때 빠르게 실행하는 방식**이다.

---

# 2. Maven build를 먼저 하는 경우

이번에는 jar 파일을 만들고 싶을 때다.

```bash
./mvnw clean package -DskipTests
```

이 명령은 앱을 실행하는 게 아니라 **jar 파일을 만든다.**

흐름은 이렇다.

```text
소스코드
↓
Maven build
↓
target/*.jar 생성
```

그 다음 jar를 직접 실행할 수 있다.

```bash
java -jar target/*.jar
```

그러면 흐름은 이렇게 된다.

```text
소스코드
↓
Maven build
↓
target/*.jar 생성
↓
java -jar로 실행
↓
localhost:8080 접속
```

여기까지는 Docker가 전혀 없다.

---

# 3. Docker를 섞으면 순서가 두 갈래로 나뉨

Docker를 쓸 때는 방식이 두 개야.

```text
방식 1. 밖에서 Maven build 하고, Docker build 한다
방식 2. Docker build 안에서 Maven build까지 한다
```

여기서부터 헷갈리는 거임.

---

# 4. 방식 1: 밖에서 Maven build 하고 Docker build

이 Dockerfile을 쓰는 경우:

```dockerfile
FROM eclipse-temurin:21-jre

WORKDIR /app

COPY ./target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

이 Dockerfile은 Maven build를 안 한다.

그냥 이미 만들어진 jar를 복사한다.

그래서 순서는 반드시 이렇게 가야 한다.

```bash
./mvnw clean package -DskipTests
```

```bash
docker build -t hello-world:v1 .
```

```bash
docker run -p 8080:8080 hello-world:v1
```

흐름으로 보면:

```text
1. 소스코드 작성

2. Maven build
   ./mvnw clean package -DskipTests

3. target/*.jar 생성

4. Docker build
   docker build -t hello-world:v1 .

5. Docker 이미지 생성

6. Docker run
   docker run -p 8080:8080 hello-world:v1

7. 컨테이너 안에서 java -jar /app/app.jar 실행

8. localhost:8080 접속
```

이 방식에서는 순서가 정확히 이거야.

```text
Maven build
→ Docker build
→ Docker run
```

여기서 `mvn spring-boot:run`은 안 써도 된다.

---

# 5. 방식 1에서 각각의 역할

## Maven build

```bash
./mvnw clean package -DskipTests
```

역할:

```text
Spring 프로젝트를 jar 파일로 포장함
```

결과:

```text
target/프로젝트명.jar
```

## Docker build

```bash
docker build -t hello-world:v1 .
```

역할:

```text
jar 파일을 포함한 Docker 이미지 생성
```

결과:

```text
hello-world:v1 이미지
```

## Docker run

```bash
docker run -p 8080:8080 hello-world:v1
```

역할:

```text
이미지를 컨테이너로 실행
```

결과:

```text
Spring Boot 앱 실행
localhost:8080 접속 가능
```

---

# 6. 방식 2: Docker build 안에서 Maven build까지 하는 경우

이 Dockerfile을 쓰는 경우:

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

이 Dockerfile은 안에서 Maven build를 한다.

그래서 로컬에서 이 명령을 먼저 칠 필요가 없다.

```bash
./mvnw clean package -DskipTests
```

바로 Docker build 하면 된다.

```bash
docker build -t hello-world:v1 .
```

그 다음 실행한다.

```bash
docker run -p 8080:8080 hello-world:v1
```

흐름은 이렇다.

```text
1. 소스코드 작성

2. Docker build 실행
   docker build -t hello-world:v1 .

3. Docker build 안의 Build Stage 시작

4. Maven 이미지 안에서 Maven build 수행
   mvn package

5. target/*.jar 생성

6. Runtime Stage 시작

7. jar만 Runtime 이미지로 복사

8. Docker 이미지 생성

9. Docker run 실행
   docker run -p 8080:8080 hello-world:v1

10. 컨테이너 안에서 java -jar /app/app.jar 실행

11. localhost:8080 접속
```

이 방식에서는 순서가 이거야.

```text
Docker build
  안에서 Maven build 발생
→ Docker run
```

즉 겉으로 치는 명령어는 두 개뿐이다.

```bash
docker build -t hello-world:v1 .
docker run -p 8080:8080 hello-world:v1
```

---

# 7. 제일 중요한 비교

## 방식 1

```text
내가 직접 Maven build 함
그 다음 Docker build 함
그 다음 Docker run 함
```

명령어:

```bash
./mvnw clean package -DskipTests
docker build -t hello-world:v1 .
docker run -p 8080:8080 hello-world:v1
```

흐름:

```text
Maven build
→ Docker build
→ Docker run
```

---

## 방식 2

```text
Docker build가 Maven build까지 대신 함
그 다음 Docker run 함
```

명령어:

```bash
docker build -t hello-world:v1 .
docker run -p 8080:8080 hello-world:v1
```

흐름:

```text
Docker build
  └─ 내부에서 Maven build
→ Docker run
```

---

# 8. Maven run은 언제 쓰는가?

이것도 중요함.

```bash
./mvnw spring-boot:run
```

이건 Docker랑 별개로 **로컬에서 바로 실행할 때** 쓴다.

즉 개발 중에는 이렇게 할 수 있다.

```bash
./mvnw spring-boot:run
```

또는 jar를 만든 뒤 실행할 수도 있다.

```bash
./mvnw clean package -DskipTests
java -jar target/*.jar
```

하지만 Docker 이미지로 실행할 거면 보통 `mvn spring-boot:run`은 안 쓴다.

Docker에서는 컨테이너가 실행될 때 이 명령이 실행된다.

```dockerfile
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

즉 Docker 세계에서는:

```text
mvn spring-boot:run으로 실행하는 게 아니라
docker run이 컨테이너를 띄우고
컨테이너 안에서 java -jar가 실행됨
```

---

# 9. 머릿속에 이렇게 넣으면 됨

제일 깔끔하게는 이렇게 외우면 된다.

```text
Maven build:
jar 만들기

Maven run:
로컬에서 Spring 바로 실행하기

Docker build:
이미지 만들기

Docker run:
이미지로 컨테이너 실행하기
```

그리고 흐름은 세 가지다.

---

## 로컬 개발용

```bash
./mvnw spring-boot:run
```

```text
Maven run
```

---

## jar 직접 실행용

```bash
./mvnw clean package -DskipTests
java -jar target/*.jar
```

```text
Maven build
→ Java run
```

---

## Docker 단일 방식

```bash
./mvnw clean package -DskipTests
docker build -t hello-world:v1 .
docker run -p 8080:8080 hello-world:v1
```

```text
Maven build
→ Docker build
→ Docker run
```

---

## Docker 멀티 스테이지 방식

```bash
docker build -t hello-world:v1 .
docker run -p 8080:8080 hello-world:v1
```

```text
Docker build
  └─ Maven build
→ Docker run
```

---

# 10. 최종 한 줄

네가 지금 헷갈린 부분은 이거 하나로 정리됨.

```text
단일 Dockerfile 방식은 Maven build를 먼저 하고 Docker build를 해야 한다.
멀티 스테이지 Dockerfile 방식은 Docker build 안에서 Maven build가 같이 일어난다.
둘 다 마지막 실행은 Docker run이다.
```

진짜 실무 감각으로 말하면:

```text
개발 중 빠른 확인:
./mvnw spring-boot:run

jar가 잘 만들어지는지 확인:
./mvnw clean package -DskipTests

단순 Docker 이미지 만들기:
Maven build → Docker build → Docker run

실무형 Docker 이미지 만들기:
Docker build 안에서 Maven build → Docker run
```
