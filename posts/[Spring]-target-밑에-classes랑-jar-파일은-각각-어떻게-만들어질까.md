---
title: "[SPRING] target 밑에 classes랑 jar 파일은 각각 어떻게 만들어질까?"
source: "https://velog.io/@yorange50/SPRING-target-밑에-classes랑-jar-파일은-각각-어떻게-만들어질까"
published: "2026-05-12T09:09:05.249Z"
tags: ""
backup_date: "2026-05-29T14:52:52.755880"
---

스프링 프로젝트를 Maven으로 빌드하다 보면 `target` 폴더 밑에 여러 파일이 생긴다. 처음 보면 조금 어지럽다. 특히 눈에 띄는 게 있다.

```text
target
├── classes
│   ├── com
│   └── application.properties
├── generated-sources
├── generated-test-sources
├── maven-archiver
├── maven-status
├── surefire-reports
├── test-classes
├── hello-world-0.0.1-SNAPSHOT.jar
└── hello-world-0.0.1-SNAPSHOT.jar.original
```

여기서 핵심은 두 개다.

```text
target/classes
```

그리고

```text
target/hello-world-0.0.1-SNAPSHOT.jar
```

둘 다 빌드 결과물이긴 한데, 역할이 다르다.

`classes`는 “컴파일된 중간 결과물”이고, `jar`는 “실행하거나 배포하기 좋게 묶은 최종 결과물”이다.

---

## 1. target 폴더는 언제 생길까?

Maven 프로젝트에서 빌드를 하면 `target` 폴더가 생긴다.

예를 들어 이런 명령어를 치면 된다.

```bash
./mvnw compile
```

또는

```bash
./mvnw package
```

윈도우라면 보통 이렇게 칠 수 있다.

```bash
mvnw.cmd compile
```

또는

```bash
mvnw.cmd package
```

`target` 폴더는 Maven이 빌드하면서 만든 결과물을 모아두는 곳이다.

소스코드는 보통 여기에 있다.

```text
src/main/java
src/main/resources
src/test/java
```

빌드 결과물은 여기에 생긴다.

```text
target
```

즉, `src`는 내가 작성한 원본이고, `target`은 Maven이 만들어낸 결과물이다.

---

## 2. classes 폴더는 뭘까?

`target/classes`는 자바 코드가 컴파일된 결과물이 들어가는 폴더다.

예를 들어 내가 이런 파일을 만들었다고 하자.

```text
src/main/java/com/example/helloworld/HelloWorldApplication.java
```

이 파일은 사람이 읽는 자바 코드다.

```java
public class HelloWorldApplication {
    public static void main(String[] args) {
        System.out.println("Hello World");
    }
}
```

그런데 컴퓨터는 `.java` 파일을 그대로 실행하지 않는다.

자바 코드는 먼저 컴파일되어야 한다.

컴파일을 하면 `.java` 파일이 `.class` 파일로 바뀐다.

```text
HelloWorldApplication.java
```

이게 컴파일되면

```text
HelloWorldApplication.class
```

가 된다.

그리고 그 결과물이 들어가는 곳이 바로 `target/classes`다.

---

## 3. classes 폴더 안에 com 폴더가 있는 이유

스크린샷을 보면 `classes` 밑에 `com` 폴더가 있다.

```text
target/classes/com
```

이건 패키지 구조 때문이다.

예를 들어 자바 파일 위에 이런 패키지 선언이 있었다고 하자.

```java
package com.example.helloworld;
```

그러면 컴파일 결과도 이 패키지 구조를 따라간다.

```text
target/classes/com/example/helloworld/HelloWorldApplication.class
```

즉, 원래 소스 구조가 이랬다면

```text
src/main/java/com/example/helloworld/HelloWorldApplication.java
```

컴파일 후에는 이렇게 된다.

```text
target/classes/com/example/helloworld/HelloWorldApplication.class
```

정리하면 이렇다.

```text
src/main/java 안의 .java 파일
        ↓ 컴파일
target/classes 안의 .class 파일
```

---

## 4. application.properties는 왜 classes 밑에 있을까?

스크린샷을 보면 `classes` 밑에 `application.properties`도 있다.

```text
target/classes/application.properties
```

이 파일은 원래 보통 여기에 있다.

```text
src/main/resources/application.properties
```

`resources` 폴더에 있는 파일은 자바 코드처럼 컴파일되지는 않는다.

대신 빌드할 때 `target/classes`로 복사된다.

즉, 이런 흐름이다.

```text
src/main/resources/application.properties
        ↓ 복사
target/classes/application.properties
```

왜 `classes` 밑으로 복사될까?

스프링 부트 애플리케이션이 실행될 때 `application.properties` 같은 설정 파일을 클래스패스에서 찾기 때문이다.

여기서 클래스패스란 간단히 말하면 “자바 애플리케이션이 실행될 때 참고하는 파일 경로”다.

`target/classes`는 실행 시 클래스패스에 포함된다.

그래서 `.class` 파일뿐만 아니라 설정 파일도 같이 들어간다.

---

## 5. 그러면 classes 폴더만 있으면 실행할 수 있나?

이론적으로는 가능하다.

컴파일된 `.class` 파일과 필요한 리소스가 `target/classes`에 있으니까, 이걸 기준으로 실행할 수도 있다.

하지만 실무에서는 보통 `classes` 폴더를 직접 들고 다니지 않는다.

왜냐하면 실행에 필요한 파일이 여러 군데 흩어져 있기 때문이다.

스프링 부트 프로젝트는 내 코드만 필요한 게 아니다.

예를 들어 이런 라이브러리들이 필요하다.

```text
spring-boot
spring-web
tomcat
jackson
logging
```

내가 만든 `.class` 파일만 있다고 해서 애플리케이션이 완전히 실행되는 게 아니다.

그래서 필요한 것들을 하나로 묶은 파일이 필요하다.

그게 바로 `jar` 파일이다.

---

## 6. jar 파일은 뭘까?

`jar`는 Java Archive의 줄임말이다.

쉽게 말하면 자바 애플리케이션을 실행하거나 배포하기 위해 파일들을 하나로 묶은 압축 파일이다.

스크린샷에 이런 파일이 있다.

```text
hello-world-0.0.1-SNAPSHOT.jar
```

이 파일은 Maven의 `package` 단계에서 만들어진다.

명령어로는 보통 이렇게 만든다.

```bash
./mvnw package
```

윈도우라면

```bash
mvnw.cmd package
```

이 명령어를 실행하면 Maven은 대략 이런 일을 한다.

```text
1. src/main/java 컴파일
2. target/classes 생성
3. src/main/resources 파일 복사
4. 테스트 코드 컴파일
5. 테스트 실행
6. 컴파일 결과물과 리소스를 jar로 묶음
```

즉, `jar`는 `classes`보다 나중에 만들어진다.

---

## 7. compile과 package의 차이

여기서 중요한 차이가 있다.

```bash
./mvnw compile
```

을 하면 보통 `target/classes`까지 만들어진다.

하지만 jar 파일은 아직 안 만들어질 수 있다.

반면

```bash
./mvnw package
```

를 하면 `classes`도 만들고, 최종적으로 `jar` 파일까지 만든다.

흐름으로 보면 이렇다.

```text
mvn compile
    ↓
target/classes 생성

mvn package
    ↓
target/classes 생성
    ↓
target/*.jar 생성
```

즉, `compile`은 중간 결과물까지 만드는 단계이고, `package`는 실행 가능한 패키지까지 만드는 단계다.

---

## 8. Spring Boot의 jar는 그냥 jar랑 조금 다르다

일반 자바 프로젝트의 jar는 단순히 `.class` 파일과 리소스를 묶은 파일일 수 있다.

그런데 스프링 부트의 jar는 보통 실행 가능한 jar다.

즉, 이렇게 실행할 수 있다.

```bash
java -jar target/hello-world-0.0.1-SNAPSHOT.jar
```

그러면 스프링 부트 애플리케이션이 실행된다.

```text
Tomcat started on port 8080
Started HelloWorldApplication
```

스프링 부트 jar 안에는 내 코드뿐만 아니라 실행에 필요한 구조가 같이 들어간다.

대략 이런 식이다.

```text
hello-world-0.0.1-SNAPSHOT.jar
├── BOOT-INF
│   ├── classes
│   │   ├── com
│   │   └── application.properties
│   └── lib
│       ├── spring-boot-*.jar
│       ├── spring-web-*.jar
│       └── ...
├── META-INF
└── org/springframework/boot/loader
```

여기서 중요한 부분은 이거다.

```text
BOOT-INF/classes
```

여기에 내 애플리케이션의 컴파일 결과물이 들어간다.

그리고

```text
BOOT-INF/lib
```

여기에 필요한 라이브러리들이 들어간다.

즉, 스프링 부트 jar는 단순히 내 코드만 묶은 게 아니라, 애플리케이션 실행에 필요한 것들을 꽤 많이 포함하고 있다.

그래서 `java -jar`로 바로 실행할 수 있다.

---

## 9. jar.original은 뭘까?

스크린샷을 보면 이런 파일도 보인다.

```text
hello-world-0.0.1-SNAPSHOT.jar.original
```

이건 스프링 부트 Maven 플러그인이 jar를 다시 패키징하면서 생기는 파일이다.

조금 더 풀어서 보면 이렇다.

Maven이 먼저 일반 jar를 만든다.

```text
hello-world-0.0.1-SNAPSHOT.jar
```

그런데 스프링 부트는 이 jar를 실행 가능한 jar로 바꿔야 한다.

그래서 기존 jar를 백업해두고

```text
hello-world-0.0.1-SNAPSHOT.jar.original
```

새로운 실행 가능한 jar를 만든다.

```text
hello-world-0.0.1-SNAPSHOT.jar
```

즉, 최종적으로 우리가 실행할 파일은 보통 이거다.

```bash
java -jar target/hello-world-0.0.1-SNAPSHOT.jar
```

`.jar.original`은 보통 직접 실행하지 않는다.

---

## 10. 전체 흐름 정리

스프링 프로젝트에서 내가 작성한 파일은 보통 여기에 있다.

```text
src/main/java
src/main/resources
```

Maven 빌드를 하면 먼저 자바 코드가 컴파일된다.

```text
src/main/java/com/example/HelloWorldApplication.java
        ↓
target/classes/com/example/HelloWorldApplication.class
```

그리고 리소스 파일이 복사된다.

```text
src/main/resources/application.properties
        ↓
target/classes/application.properties
```

그다음 `package` 단계에서 이것들을 jar로 묶는다.

```text
target/classes
        ↓
target/hello-world-0.0.1-SNAPSHOT.jar
```

최종 실행은 이렇게 한다.

```bash
java -jar target/hello-world-0.0.1-SNAPSHOT.jar
```

---

## 11. Dockerfile에서 jar를 복사하는 이유

Dockerfile을 보면 이런 코드가 자주 나온다.

```dockerfile
FROM eclipse-temurin:21-jre

WORKDIR /app

COPY target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

여기서 이 부분이 중요하다.

```dockerfile
COPY target/*.jar app.jar
```

도커 이미지 안에 `target/classes`를 복사하는 게 아니라 `jar` 파일을 복사한다.

왜냐하면 jar 파일이 실행에 필요한 것들을 하나로 묶은 최종 결과물이기 때문이다.

즉, 로컬에서 Maven 빌드를 먼저 한다.

```bash
./mvnw package
```

그러면 jar가 생긴다.

```text
target/hello-world-0.0.1-SNAPSHOT.jar
```

그 다음 Docker build를 한다.

```bash
docker build -t hello-world:v1 .
```

Dockerfile은 `target/*.jar`를 이미지 안으로 복사한다.

그리고 컨테이너가 실행될 때 이 명령어가 실행된다.

```bash
java -jar app.jar
```

정리하면 이렇다.

```text
Maven package
    ↓
target/classes 생성
    ↓
target/*.jar 생성
    ↓
Docker build
    ↓
jar를 이미지 안으로 복사
    ↓
Docker run
    ↓
컨테이너 안에서 java -jar app.jar 실행
```

---

## 12. classes와 jar의 차이 한 번에 정리

| 항목          | target/classes            | target/*.jar                     |
| ----------- | ------------------------- | -------------------------------- |
| 역할          | 컴파일된 중간 결과물               | 실행/배포용 최종 결과물                    |
| 생성 시점       | `mvn compile`부터 생성        | `mvn package`에서 생성               |
| 들어있는 것      | `.class` 파일, resources 파일 | classes, resources, 라이브러리, 실행 구조 |
| 직접 실행       | 가능은 하지만 번거로움              | `java -jar`로 실행 가능               |
| Docker에서 사용 | 보통 직접 복사하지 않음             | 보통 이 파일을 이미지에 복사                 |
| 실무 관점       | 빌드 중간 산출물                 | 배포 산출물                           |

---

## 13. 결론

`target/classes`는 Maven이 자바 코드를 컴파일해서 만든 중간 결과물이다.

```text
.java → .class
```

그리고 `src/main/resources`에 있던 설정 파일도 이곳으로 복사된다.

```text
application.properties → target/classes/application.properties
```

반면 `target/*.jar`는 애플리케이션을 실행하거나 배포하기 위해 최종적으로 묶은 파일이다.

```text
target/classes + 필요한 라이브러리 + 실행 구조 → jar
```

그래서 개발 중에는 `classes` 폴더를 보면서 “아, 컴파일 결과물이 여기 생기는구나”라고 이해하면 되고, 실제 실행이나 Docker 이미지 생성에서는 보통 `jar` 파일을 사용하면 된다.

한 줄로 정리하면 이렇다.

```text
classes는 컴파일 결과물이고, jar는 그 결과물을 실행 가능하게 묶은 배포 파일이다.
```
