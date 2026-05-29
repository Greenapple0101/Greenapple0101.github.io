---
title: "[DOCKER] Maven 빌드, `.m2` 캐시, Dockerfile 방식 비교 정리"
source: "https://velog.io/@yorange50/DOCKER-Maven-빌드-.m2-캐시-Dockerfile-방식-비교-정리"
published: "2026-05-08T07:50:22.528Z"
tags: ""
backup_date: "2026-05-29T14:52:52.767112"
---


스프링부트 프로젝트를 Docker로 올리다 보면 단순히 `docker run`만 문제가 아니다.

실제로는 그 전에:

```text
소스코드 작성
→ Maven 빌드
→ jar 생성
→ Docker 이미지 생성
→ 컨테이너 실행
```

이라는 흐름을 이해해야 한다.

이번에는 Maven 빌드, `.m2` 저장소, Dockerfile 두 가지 방식, 그리고 Compose에서 환경변수를 넘기는 구조까지 정리한다. 

---

# 1. “런이 된다”는 건 클래스가 만들어졌다는 뜻

자바 프로젝트는 `.java` 파일을 그대로 실행하는 게 아니다.

먼저 컴파일을 거친다.

```text
.java
→ .class
```

그리고 이 `.class` 파일들이 모여서 최종적으로 `jar` 파일이 된다.

즉, 스프링부트 프로젝트에서 실행이 된다는 건 내부적으로:

```text
자바 소스가 컴파일됨
→ 클래스 파일 생성됨
→ jar 실행됨
```

이라는 뜻이다.

---

# 2. Maven Wrapper: Maven을 안 깔아도 되는 이유

프로젝트에 보통 이런 파일이 있다.

```text
mvnw
mvnw.cmd
```

이걸 Maven Wrapper라고 한다.

그래서 내 PC에 Maven이 직접 설치되어 있지 않아도 프로젝트 안에서 Maven 명령을 실행할 수 있다.

Windows PowerShell 기준:

```powershell
./mvnw package
```

이 명령은 프로젝트를 빌드해서 `target` 폴더에 jar 파일을 만든다.

---

# 3. 그런데 왜 테스트 에러가 날까?

그냥 빌드하면 테스트까지 같이 돈다.

```powershell
./mvnw package
```

문제는 스프링부트 테스트가 ApplicationContext 전체를 띄우는 경우가 있다는 점이다.

예를 들어 JPA 설정이 들어가 있으면 테스트 중에 DB 연결까지 확인하려고 한다.

이때 PostgreSQL Driver가 없거나 DB 설정이 안 맞으면 이런 에러가 난다.

```text
Failed to load driver class org.postgresql.Driver
```

즉, 단순 컴파일 에러가 아니라:

```text
테스트 실행 중
→ Spring Context 로딩
→ DataSource 생성 시도
→ PostgreSQL Driver 없음
→ 테스트 실패
```

흐름이다.

---

# 4. 그래서 테스트를 건너뛰고 빌드한다

개발 중에 일단 jar만 만들고 싶으면 테스트를 건너뛸 수 있다.

```powershell
./mvnw package -DskipTests
```

또는 clean까지 포함하면:

```powershell
./mvnw clean package -DskipTests
```

여기서 주의할 점:

```text
-DskipTests
```

가 맞다.

```text
-DskipTest
```

처럼 `s`가 빠지면 의도대로 동작하지 않을 수 있다.

---

# 5. `.m2` 폴더는 뭐냐?

Maven은 필요한 라이브러리를 매번 인터넷에서 새로 받지 않는다.

한 번 받은 의존성은 사용자 홈 디렉터리 아래에 저장한다.

Windows 기준:

```text
C:\Users\oscbs\.m2\repository
```

예를 들어 Spring Boot Starter는 이런 식으로 저장된다.

```text
C:\Users\oscbs\.m2\repository\org\springframework\boot\spring-boot-starter
```

즉 `.m2`는 Maven 의존성 캐시 저장소다.

---

# 6. 왜 한 번 받으면 다음에는 빠를까?

처음 빌드할 때는 Maven이 의존성을 다운로드한다.

```text
spring-boot-starter
jpa
web
postgresql driver
lombok
```

이런 것들이 `.m2/repository`에 저장된다.

그 다음 빌드부터는:

```text
이미 .m2에 있음
→ 다시 다운로드 안 함
→ 빌드 빨라짐
```

이 된다.

---

# 7. target 폴더는 빌드 산출물이다

Maven 빌드를 하면 생기는 폴더가 있다.

```text
target/
```

여기에는:

```text
class 파일
jar 파일
테스트 리포트
빌드 결과물
```

이 들어간다.

예:

```text
target/board-api-0.0.1-SNAPSHOT.jar
```

중요한 점은 `target`은 직접 수정하는 폴더가 아니라는 것이다.

```text
target = Maven이 자동으로 만드는 결과물
```

문제가 생기면 보통 삭제 후 다시 빌드한다.

```powershell
./mvnw clean package -DskipTests
```

---

# 8. 그런데 clean이 실패할 수도 있다

Windows에서 이런 에러가 날 수 있다.

```text
Failed to delete target/classes/...
```

이건 대부분 Java 프로세스가 해당 파일을 잡고 있어서 생긴다.

즉:

```text
Spring Boot 앱 실행 중
→ target/classes 파일 사용 중
→ Maven clean이 삭제 못함
```

이럴 때는 Java 프로세스를 확인한다.

```powershell
ps | findstr java
```

그리고 종료한다.

```powershell
taskkill /IM java.exe /F
```

그 다음 다시 빌드하면 된다.

```powershell
./mvnw clean package -DskipTests
```

---

# 9. Dockerfile 방식 1: 밖에서 빌드하고 jar만 복사

첫 번째 방식은 로컬에서 먼저 Maven 빌드를 끝내는 방식이다.

```powershell
./mvnw clean package -DskipTests
```

그 다음 Dockerfile은 짧아진다.

```dockerfile
FROM eclipse-temurin:21-jre

WORKDIR /app

COPY ./target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

이 방식은 이미 로컬에 `target/*.jar`가 있다는 전제다.

장점:

```text
Dockerfile이 짧음
이미지 빌드가 단순함
로컬 .m2 캐시를 활용할 수 있음
```

단점:

```text
로컬에서 먼저 빌드해야 함
로컬 환경에 영향을 받음
```

즉, 내 PC에 Java가 제대로 있어야 하고 Maven Wrapper 빌드가 성공해야 한다.

---

# 10. Dockerfile 방식 2: 컨테이너 안에서 빌드

두 번째 방식은 Docker 빌드 과정 안에서 Maven 빌드까지 수행하는 방식이다.

```dockerfile
# syntax=docker/dockerfile:1

# ---------- Build stage ----------
FROM maven:3.9-eclipse-temurin-21 AS build

WORKDIR /workspace

COPY pom.xml .

RUN mvn -B -q dependency:go-offline

COPY src ./src

RUN mvn -B -q -DskipTests package

# ---------- Runtime stage ----------
FROM eclipse-temurin:21-jre

WORKDIR /app

COPY --from=build /workspace/target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

이걸 멀티 스테이지 빌드라고 한다.

---

# 11. 멀티 스테이지 빌드 구조

위 Dockerfile은 두 단계로 나뉜다.

## Build Stage

```dockerfile
FROM maven:3.9-eclipse-temurin-21 AS build
```

여기에는 Maven과 JDK가 들어 있다.

그래서:

```text
소스코드 컴파일
의존성 다운로드
jar 생성
```

이 가능하다.

## Runtime Stage

```dockerfile
FROM eclipse-temurin:21-jre
```

여기에는 실행에 필요한 JRE만 둔다.

그리고 빌드 단계에서 만든 jar만 복사한다.

```dockerfile
COPY --from=build /workspace/target/*.jar app.jar
```

즉:

```text
빌드는 무거운 이미지에서 하고
실행은 가벼운 이미지에서 한다
```

---

# 12. JDK와 JRE 차이

## JDK

```text
Java Development Kit
```

개발과 컴파일에 필요하다.

포함:

```text
javac
JRE
개발 도구
```

## JRE

```text
Java Runtime Environment
```

실행에 필요하다.

이미 만들어진 jar를 실행할 때 사용한다.

정리하면:

```text
빌드할 때는 JDK 필요
실행할 때는 JRE면 충분
```

---

# 13. 두 Dockerfile 방식 비교

| 방식             | 특징                        | 장점      | 단점             |
| -------------- | ------------------------- | ------- | -------------- |
| 로컬 빌드 후 jar 복사 | `COPY target/*.jar`       | 빠르고 단순함 | 로컬 환경 의존       |
| 컨테이너 내부 빌드     | `FROM maven ... AS build` | 환경 통일   | 매번 의존성 다운로드 가능 |

둘 중 하나가 무조건 정답은 아니다.

로컬 개발에서는 짧은 Dockerfile이 편할 수 있다.

하지만 CI/CD나 Jenkins, Kubernetes 환경에서는 컨테이너 내부 빌드 방식이 더 안정적일 수 있다.

---

# 14. Jenkins가 Kubernetes에서 돌면 왜 고민이 생길까?

Jenkins도 Kubernetes 위에서 돌아갈 수 있다.

이 경우 빌드할 때마다:

```text
Pod 생성
→ 컨테이너 생성
→ 빌드 수행
→ Pod 삭제
```

흐름이 된다.

문제는 컨테이너가 사라지면 그 안에 다운로드된 Maven 의존성도 같이 사라질 수 있다는 점이다.

즉:

```text
매번 Maven dependency 다운로드
→ 빌드 느려짐
```

그래서 CI/CD에서는:

```text
Maven 캐시
Docker layer cache
이미지 경량화
```

가 중요해진다.

---

# 15. Docker Compose에서 환경변수를 넘기는 이유

FE 설정 파일에 이런 값이 있다고 하자.

```properties
spring.application.name=board_fe
server.port=${SERVER_PORT:8081}

board.api.base-url=${BOARD_API_BASE_URL:http://localhost:8080}
```

여기서 중요한 건 `${...}` 구조다.

```properties
${SERVER_PORT:8081}
```

의 의미는:

```text
SERVER_PORT 환경변수가 있으면 그 값을 쓰고
없으면 기본값 8081을 쓴다
```

그리고:

```properties
${BOARD_API_BASE_URL:http://localhost:8080}
```

의 의미는:

```text
BOARD_API_BASE_URL 환경변수가 있으면 그 값을 쓰고
없으면 http://localhost:8080을 쓴다
```

---

# 16. Compose에서는 이렇게 넘긴다

```yaml
fe:
  environment:
    BOARD_API_BASE_URL: http://api:8080
    SERVER_PORT: 8081
```

이렇게 하면 FE 컨테이너 안에서는:

```text
BOARD_API_BASE_URL=http://api:8080
SERVER_PORT=8081
```

이 값이 주입된다.

그래서 FE는 `localhost:8080`이 아니라 Compose 네트워크 안의 API 서비스 이름인 `api`를 바라본다.

---

# 17. 왜 `http://api:8080`인가?

Docker Compose에서는 서비스 이름이 DNS 이름처럼 동작한다.

```yaml
services:
  api:
```

이렇게 되어 있으면 같은 Compose 네트워크 안에서 FE 컨테이너는 API를 이렇게 부를 수 있다.

```text
http://api:8080
```

즉:

```text
FE 컨테이너 → api:8080 → API 컨테이너
```

흐름이다.

컨테이너 안에서 `localhost`는 내 PC가 아니라 자기 자신이다.

그래서 컨테이너끼리 통신할 때는 보통 서비스 이름을 쓴다.

---

# 18. DB도 마찬가지다

API 설정도 Compose에서 환경변수로 넘긴다.

```yaml
api:
  environment:
    SPRING_DATASOURCE_URL: jdbc:postgresql://db:5432/boarddb
    SPRING_DATASOURCE_USERNAME: board
    SPRING_DATASOURCE_PASSWORD: board1234
```

여기서 `db`는 Compose 서비스 이름이다.

```yaml
services:
  db:
```

그래서 API 컨테이너는 DB를 이렇게 찾는다.

```text
jdbc:postgresql://db:5432/boarddb
```

---

# 19. depends_on과 healthcheck

Compose에 이런 설정이 있다.

```yaml
depends_on:
  db:
    condition: service_healthy
```

이 의미는:

```text
db 컨테이너가 healthy 상태가 된 다음 api 실행
```

이다.

DB는 컨테이너가 켜졌다고 바로 접속 가능한 게 아니다.

초기화 시간이 필요하다.

그래서 healthcheck로 실제 접속 가능 상태를 확인한다.

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U board -d boarddb"]
```

---

# 20. docker run으로 각각 띄우면 직접 넘겨야 한다

Compose를 쓰면 environment를 자동으로 넘겨준다.

하지만 `docker run`으로 따로 실행하면 직접 넘겨야 한다.

예:

```powershell
docker run -p 8080:8080 ubuntu12341/board-api:v0.0.1
```

이렇게만 하면 환경변수가 하나도 안 넘어간다.

DB 설정이 필요하다면 이렇게 줘야 한다.

```powershell
docker run -p 8080:8080 `
  -e SPRING_DATASOURCE_URL=jdbc:postgresql://host.docker.internal:5432/boarddb `
  -e SPRING_DATASOURCE_USERNAME=board `
  -e SPRING_DATASOURCE_PASSWORD=board1234 `
  ubuntu12341/board-api:v0.0.1
```

즉:

```text
Compose는 변수 주입을 대신 해주고
docker run은 직접 -e로 넘겨야 한다
```

---

# 21. “DB가 없는데 왜 에러가 안 나지?”의 이유

만약 `application.properties`가 이렇게만 되어 있다면:

```properties
spring.application.name=board-api
```

DB 설정이 없으니 DataSource를 만들려고 하지 않을 수 있다.

그래서 DB가 없어도 에러가 안 날 수 있다.

반대로 JPA나 datasource 설정이 들어가 있으면 Spring Boot가 DataSource를 만들려고 한다.

그때 PostgreSQL Driver가 없거나 DB 접속 정보가 잘못되면 에러가 난다.

```text
Failed to load driver class org.postgresql.Driver
```

---

# 22. 지금 에러의 핵심

로그 핵심은 이거다.

```text
ClassNotFoundException: org.postgresql.Driver
```

즉, PostgreSQL JDBC Driver가 클래스패스에 없다는 뜻이다.

해결은 `pom.xml`에 PostgreSQL Driver 의존성을 넣는 것이다.

```xml
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <scope>runtime</scope>
</dependency>
```

그 후 다시 빌드한다.

```powershell
./mvnw clean package -DskipTests
```

---

# 23. 전체 흐름 정리

이번에 배운 흐름은 이거다.

```text
1. ./mvnw package
2. 테스트 에러 발생
3. ./mvnw package -DskipTests
4. target에 jar 생성
5. Dockerfile에서 jar 복사
6. docker build
7. docker run 또는 docker compose up
8. Compose environment로 DB/API 주소 주입
```

---

# 마무리

이번 내용의 핵심은 명확하다.

```text
빌드와 실행은 다르다.
로컬 실행과 컨테이너 실행도 다르다.
Compose 실행과 docker run 실행도 다르다.
```

정리하면:

* `mvnw`가 있으면 Maven 설치 없이 빌드 가능
* `.m2`는 Maven 의존성 캐시
* `target`은 Maven 빌드 산출물
* 테스트가 DB/JPA 때문에 실패하면 `-DskipTests`로 jar 빌드 가능
* `target` 삭제 실패는 Java 프로세스가 잡고 있을 가능성이 큼
* Dockerfile은 로컬 빌드 방식과 컨테이너 빌드 방식이 있음
* Compose는 환경변수를 컨테이너에 주입해줌
* `localhost`는 컨테이너 안에서는 자기 자신
* 컨테이너끼리는 서비스 이름으로 통신
* PostgreSQL Driver 에러는 `pom.xml` 의존성 문제일 가능성이 큼

결국 Docker 배포에서 중요한 건 단순히 컨테이너를 띄우는 게 아니라:

```text
빌드 산출물이 어떻게 만들어지고,
그 산출물이 어떤 환경변수와 함께 실행되는지 이해하는 것
```

이다.
