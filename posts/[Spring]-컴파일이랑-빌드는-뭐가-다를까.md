---
title: "[SPRING] 컴파일이랑 빌드는 뭐가 다를까?"
source: "https://velog.io/@yorange50/SPRING-컴파일이랑-빌드는-뭐가-다를까"
published: "2026-05-11T10:55:39.059Z"
tags: ""
backup_date: "2026-05-29T14:52:52.764551"
---

스프링 공부하다 보면 이런 말이 계속 나온다.

```bash
./gradlew build
```

```bash
mvn clean package
```

```bash
javac Main.java
```

근데 보다 보면 헷갈린다.

* 컴파일?
* 빌드?
* 패키징?
* 실행?

다 비슷해 보인다.

하지만 실제로는:

> 컴파일은 빌드의 "한 과정"

이다.

즉:

```text
빌드 > 컴파일
```

관계라고 보면 된다.

---

# 먼저 한 줄 정의

## 컴파일

```text
사람이 작성한 코드를 기계가 이해 가능한 형태로 변환하는 과정
```

---

## 빌드

```text
프로그램 실행 가능 상태로 만드는 전체 과정
```

---

# 스프링 기준으로 이해하기

예를 들어 이런 프로젝트가 있다.

```text
board-api
 ├── src
 │    └── main
 │         └── java
 │              └── BoardController.java
 ├── build.gradle
```

여기서:

```bash
./gradlew build
```

를 실행하면 내부적으로 엄청 많은 일이 일어난다.

---

# build 안에서 실제로 일어나는 것

## 1. 코드 컴파일

```text
.java → .class
```

변환.

예:

```java
public class Hello {
    public static void main(String[] args) {
        System.out.println("hello");
    }
}
```

↓

컴파일 후:

```text
Hello.class
```

생성.

이게 컴파일이다.

---

# 왜 컴파일이 필요한가?

자바 코드는 사람이 읽기 좋은 언어다.

하지만 컴퓨터는 바로 이해 못 한다.

그래서:

```text
Java 코드
↓
ByteCode(.class)
↓
JVM 실행
```

흐름으로 간다.

---

# 그런데 build는 여기서 안 끝난다

스프링 프로젝트는 단순 `.class` 파일 하나만 있으면 실행이 안 된다.

왜냐면:

* Spring Boot 라이브러리
* Tomcat
* Jackson
* JPA
* Logback

같은 의존성이 필요하기 때문이다.

그래서 build는:

```text
컴파일 + 테스트 + 라이브러리 묶기 + 실행파일 생성
```

까지 진행한다.

---

# Gradle build 과정 보기

예를 들어:

```bash
./gradlew build
```

하면 대략 이런 흐름이다.

```text
1. 의존성 다운로드
2. 코드 컴파일
3. 테스트 실행
4. jar 생성
5. 실행 가능한 형태로 패키징
```

---

# 실제 결과물

빌드 후:

```text
build/libs/
```

안에 이런 게 생긴다.

```text
board-api-0.0.1-SNAPSHOT.jar
```

이게 실행 가능한 결과물이다.

---

# 이 jar 안에는 뭐가 들어있을까?

스프링 부트 jar는 그냥 코드만 있는 게 아니다.

안에:

```text
- 내 코드(.class)
- Spring Framework
- 내장 톰캣
- 라이브러리들
```

이 다 들어있다.

그래서:

```bash
java -jar board-api.jar
```

만 해도 서버가 켜지는 것.

---

# 즉 정리하면

## 컴파일

```text
코드 변환 과정
```

예:

```text
.java → .class
```

---

## 빌드

```text
실행 가능한 프로그램 만드는 전체 과정
```

예:

```text
컴파일
+ 테스트
+ 라이브러리 포함
+ jar 생성
```

---

# 스프링에서 특히 중요한 이유

스프링은 의존성이 엄청 많다.

예를 들어:

```gradle
implementation 'org.springframework.boot:spring-boot-starter-web'
```

하나만 넣어도:

* Spring MVC
* Jackson
* Embedded Tomcat
* Logging

등이 줄줄이 들어온다.

그래서 스프링의 build는:

> "프로젝트 전체를 실행 가능한 서버 형태로 만드는 작업"

에 가깝다.

---

# Docker랑 연결하면 더 이해 쉬움

예를 들어 Dockerfile:

```dockerfile
FROM eclipse-temurin:21-jdk

WORKDIR /app

COPY build/libs/app.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
```

여기서 중요한 건:

```text
빌드된 jar
```

이다.

즉 흐름은:

```text
1. Java 코드 작성
2. build 수행
3. jar 생성
4. Docker 이미지 생성
5. 컨테이너 실행
```

이다.

---

# Maven에서도 똑같다

## 컴파일만

```bash
mvn compile
```

↓

`.class` 생성.

---

## 빌드

```bash
mvn package
```

↓

jar 생성까지.

---

# 자주 하는 오해

## "build = compile"

아님.

컴파일은 build 내부의 일부 단계다.

---

## "jar 만들었으니 컴파일 안 한 거 아님?"

아님.

jar 만들기 전에 이미 컴파일이 수행된다.

---

# 실제 현업 느낌

실무에서:

```bash
./gradlew build
```

가 실패했다?

그럼 원인이 여러 개일 수 있다.

## 예시

### 컴파일 실패

```text
세미콜론 빠짐
문법 오류
```

---

### 테스트 실패

```text
contextLoads 실패
DB 연결 실패
```

---

### 패키징 실패

```text
jar 생성 실패
```

즉 build는:

> 프로젝트 전체 검증 과정

에 가깝다.

---

# 한 번에 이해하는 그림

```text
[내가 작성한 Java 코드]

        ↓ 컴파일

[.class 바이트코드]

        ↓ 빌드

[실행 가능한 jar]

        ↓ Docker

[컨테이너 실행]
```

---

# 핵심 요약

## 컴파일

```text
코드를 JVM이 이해 가능한 바이트코드로 변환
```

---

## 빌드

```text
프로그램 실행 가능한 상태로 만드는 전체 과정
```

---

## 스프링에서 build는 보통

```text
의존성 다운로드
→ 컴파일
→ 테스트
→ jar 생성
→ 실행 가능 패키징
```

까지 포함한다.

---

# 결론

스프링에서:

```bash
./gradlew build
```

는 단순히 코드 변환이 아니다.

사실상:

> "이 프로젝트를 배포 가능한 서버 형태로 만들어라"

에 가까운 명령이다.