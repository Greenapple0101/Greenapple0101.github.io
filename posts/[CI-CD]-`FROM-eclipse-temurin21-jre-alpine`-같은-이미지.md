---
title: "[CI/CD]`FROM eclipse-temurin:21-jre-alpine` 같은 이미지"
source: "https://velog.io/@yorange50/CICDFROM-eclipse-temurin21-jre-alpine-같은-이미지"
published: "2026-05-12T08:10:27.648Z"
tags: ""
backup_date: "2026-05-29T14:52:52.756929"
---

`FROM eclipse-temurin:21-jre-alpine` 같은 이미지는 종류가 엄청 많아 보이는데, 사실 태그를 쪼개서 보면 별거 아님.

```dockerfile
FROM eclipse-temurin:21-jre-alpine
```

이건 이렇게 읽으면 된다.

```text
eclipse-temurin : 이미지 이름
21              : Java 버전
jre             : JRE만 포함
alpine          : Alpine Linux 기반
```

즉 한 줄로 말하면:

```text
Java 21 실행환경만 들어 있고, Alpine Linux 기반인 가벼운 이미지
```

---

# 1. eclipse-temurin이 뭐냐

`eclipse-temurin`은 OpenJDK 배포판 중 하나다.

Java는 언어/플랫폼이고, 실제로 설치해서 쓰는 JDK 배포판은 여러 개가 있다.

예를 들면:

```text
Oracle JDK
OpenJDK
Amazon Corretto
Eclipse Temurin
Azul Zulu
```

그중 `eclipse-temurin`은 Docker에서 많이 쓰는 OpenJDK 계열 이미지라고 보면 된다.

Spring Boot 컨테이너 만들 때 흔히 이런 걸 쓴다.

```dockerfile
FROM eclipse-temurin:21-jre
```

또는:

```dockerfile
FROM eclipse-temurin:21-jdk
```

---

# 2. jdk랑 jre 차이

여기서 제일 중요한 구분은 `jdk`와 `jre`다.

## JDK

```dockerfile
FROM eclipse-temurin:21-jdk
```

JDK는 Java Development Kit이다.

즉 개발 도구까지 들어 있다.

```text
java 실행 가능
javac 컴파일 가능
개발/빌드 도구 포함
```

그래서 소스코드를 컴파일하거나 빌드할 때 필요하다.

예를 들어 멀티 스테이지 빌드의 Build Stage에서는 JDK가 필요하다.

```dockerfile
FROM maven:3.9-eclipse-temurin-21 AS build
```

여기에는 Maven과 JDK가 들어 있다.

---

## JRE

```dockerfile
FROM eclipse-temurin:21-jre
```

JRE는 Java Runtime Environment이다.

즉 실행 환경만 들어 있다.

```text
java 실행 가능
javac 컴파일은 불가능
```

이미 만들어진 jar 파일을 실행할 때는 JRE만 있어도 된다.

Spring Boot jar를 실행할 때는 보통 이렇게 한다.

```dockerfile
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

이건 컴파일이 아니라 실행이다.

그래서 Runtime Stage에서는 JRE를 많이 쓴다.

---

# 3. 그럼 Spring Boot Dockerfile에서는 뭘 써야 하나?

상황별로 보면 된다.

## 밖에서 jar를 이미 만들었다면

```dockerfile
FROM eclipse-temurin:21-jre
```

또는

```dockerfile
FROM eclipse-temurin:21-jre-alpine
```

이유는 간단하다.

이미 jar가 있으니까 컨테이너 안에서 컴파일할 필요가 없다.

```text
필요한 것:
java 실행 환경

필요 없는 것:
javac
Maven
Gradle
빌드 도구
```

그래서 JRE면 충분하다.

---

## Dockerfile 안에서 직접 빌드한다면

멀티 스테이지 빌드에서는 보통 이렇게 간다.

```dockerfile
FROM maven:3.9-eclipse-temurin-21 AS build
```

여기서는 Maven으로 빌드해야 하니까 JDK가 필요하다.

그리고 최종 실행 단계에서는:

```dockerfile
FROM eclipse-temurin:21-jre
```

또는:

```dockerfile
FROM eclipse-temurin:21-jre-alpine
```

이렇게 JRE만 둔다.

즉 구조는 이거다.

```text
빌드 단계:
Maven + JDK 필요

실행 단계:
JRE만 있으면 됨
```

---

# 4. alpine은 뭐냐

`alpine`은 Alpine Linux 기반이라는 뜻이다.

```dockerfile
FROM eclipse-temurin:21-jre-alpine
```

Alpine Linux는 아주 가벼운 리눅스 배포판이다.

그래서 Alpine 기반 이미지는 보통 크기가 작다.

장점:

```text
이미지 크기가 작음
다운로드 빠름
배포할 때 가벼움
불필요한 패키지가 적음
```

단점도 있다.

```text
일부 라이브러리 호환성 문제가 날 수 있음
디버깅 도구가 부족함
기본 명령어가 적음
glibc가 아니라 musl libc 기반이라 특정 네이티브 라이브러리에서 문제 가능
```

Spring Boot의 일반적인 웹 애플리케이션은 `alpine`으로도 잘 돌아가는 경우가 많다.

하지만 네이티브 라이브러리, 이미지 처리, 폰트, PDF, 암호화 라이브러리, JNI 같은 걸 쓰면 Alpine에서 예상치 못한 문제가 날 수 있다.

그래서 실무에서는 무조건 alpine이 정답은 아니다.

---

# 5. alpine 없는 버전은 뭐냐

예를 들어:

```dockerfile
FROM eclipse-temurin:21-jre
```

이건 보통 Ubuntu/Debian 계열 기반 이미지라고 보면 된다.

Alpine보다 이미지 크기는 클 수 있다.

대신 일반적인 리눅스 환경과 더 비슷해서 호환성이 좋다.

장점:

```text
호환성이 좋음
디버깅하기 쉬움
패키지 설치가 익숙함
실무에서 문제 원인 찾기 쉬움
```

단점:

```text
alpine보다 이미지가 큼
```

그래서 선택 기준은 이렇게 잡으면 된다.

```text
크기 최우선:
alpine

호환성/안정성/디버깅 우선:
alpine 없는 일반 jre
```

초반 학습이나 회사 과제에서는 개인적으로 이걸 추천한다.

```dockerfile
FROM eclipse-temurin:21-jre
```

익숙해진 뒤에 이미지 크기를 줄이고 싶으면:

```dockerfile
FROM eclipse-temurin:21-jre-alpine
```

으로 바꿔보면 된다.

---

# 6. 21-jre-alpine을 읽는 법

```dockerfile
FROM eclipse-temurin:21-jre-alpine
```

이걸 다시 쪼개면:

```text
21      : Java 21
jre     : 실행용 Java 환경
alpine  : 가벼운 Alpine Linux 기반
```

그래서 뜻은:

```text
Java 21로 만들어진 jar 파일을 실행하기 위한,
Alpine 기반의 가벼운 런타임 이미지
```

이 이미지에는 Maven이 없다.

그래서 이런 명령은 안 된다.

```bash
mvn package
```

또 javac도 없을 수 있다.

왜냐하면 JRE니까.

하지만 이건 된다.

```bash
java -jar app.jar
```

---

# 7. 많이 보이는 태그 예시

대충 이런 식으로 종류가 많다.

```dockerfile
FROM eclipse-temurin:21
```

```text
Java 21 기본 이미지
보통 JDK 계열일 가능성이 큼
```

```dockerfile
FROM eclipse-temurin:21-jdk
```

```text
Java 21 JDK 포함
컴파일/빌드 가능
```

```dockerfile
FROM eclipse-temurin:21-jre
```

```text
Java 21 JRE 포함
실행만 가능
```

```dockerfile
FROM eclipse-temurin:21-jdk-alpine
```

```text
Java 21 JDK 포함
Alpine 기반
가볍지만 빌드 가능
```

```dockerfile
FROM eclipse-temurin:21-jre-alpine
```

```text
Java 21 JRE 포함
Alpine 기반
가벼운 실행용 이미지
```

---

# 8. 네 Spring Boot Dockerfile에서는 뭐가 맞나

네가 지금 쓰는 Dockerfile이 이거라면:

```dockerfile
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

COPY ./target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

이건 의미가 정확히 이거다.

```text
내 로컬에서 이미 jar를 만들었다.
컨테이너에는 실행 환경만 있으면 된다.
그래서 JRE 이미지를 쓴다.
이미지 크기를 줄이고 싶어서 Alpine 기반을 쓴다.
```

이 방식에서는 먼저 이걸 해야 한다.

```bash
./mvnw clean package -DskipTests
```

그 다음:

```bash
docker build -t hello-world:v1 .
```

그리고:

```bash
docker run -p 8080:8080 hello-world:v1
```

즉 `21-jre-alpine`은 **빌드용 이미지가 아니라 실행용 이미지**라고 보면 된다.

---

# 9. 멀티 스테이지에서는 이렇게 쓰면 됨

멀티 스테이지에서는 보통 이렇게 잡으면 된다.

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

조금 더 가볍게 가고 싶으면 마지막만 이렇게 바꿀 수 있다.

```dockerfile
FROM eclipse-temurin:21-jre-alpine
```

즉:

```text
Build Stage:
maven:3.9-eclipse-temurin-21

Runtime Stage:
eclipse-temurin:21-jre
또는
eclipse-temurin:21-jre-alpine
```

---

# 10. 최종 선택 기준

초반 학습용이면 이걸 추천한다.

```dockerfile
FROM eclipse-temurin:21-jre
```

이유:

```text
호환성 좋음
문제 났을 때 디버깅 쉬움
Spring Boot 기본 실행에 안정적
```

이미지 크기 줄이는 것까지 보고 싶으면 이걸 써도 된다.

```dockerfile
FROM eclipse-temurin:21-jre-alpine
```

다만 문제가 생기면 Alpine 특성 때문일 수도 있다고 의심해야 한다.

빌드까지 해야 하면 JRE가 아니라 JDK나 Maven 이미지가 필요하다.

```dockerfile
FROM eclipse-temurin:21-jdk
```

또는:

```dockerfile
FROM maven:3.9-eclipse-temurin-21
```

---

# 한 줄 결론

```text
eclipse-temurin:21-jre-alpine은
Java 21 애플리케이션을 실행하기 위한 가벼운 런타임 이미지다.
이미 jar가 있을 때 쓰는 이미지이고,
컨테이너 안에서 Maven 빌드까지 하려면 JRE가 아니라 JDK/Maven 이미지가 필요하다.
```

지금 네 Spring Boot 과제 기준으로는 이렇게 외우면 됨.

```text
로컬에서 jar 만들고 Docker에 넣기:
eclipse-temurin:21-jre 또는 21-jre-alpine

Docker 안에서 jar까지 만들기:
maven:3.9-eclipse-temurin-21 + eclipse-temurin:21-jre
```
