---
title: "[Docker] 이미지를 jdk로 할건지 jre로 할건지"
source: "https://velog.io/@yorange50/Docker-이미지를-jdk로-할건지-jre로-할건지"
published: "2026-05-17T09:23:19.316Z"
tags: ""
backup_date: "2026-05-29T14:52:52.738244"
---

맞아. **운영 실행용 이미지는 JDK보다 JRE가 더 적절한 경우가 많다.**
내가 예시에서 `eclipse-temurin:17-jdk`를 쓴 건 “일단 무조건 실행되는 안전한 예시”에 가깝고, 실제 운영 이미지 최적화 관점에서는 더 가벼운 런타임 이미지를 쓰는 게 맞다.

## JDK와 JRE 차이

간단히 말하면 이거다.

```text
JDK = 개발 + 빌드 + 실행 도구 포함
JRE = 실행에 필요한 런타임만 포함
```

JDK에는 이런 것들이 들어 있다.

```text
javac
javadoc
jar
jlink
개발/컴파일 관련 도구
Java 실행 런타임
```

JRE 또는 runtime 이미지에는 보통 실행에 필요한 것만 있다.

```text
java 명령어
JVM
기본 런타임 라이브러리
```

Spring Boot JAR를 이미 만들어둔 상태라면 컨테이너 안에서 컴파일할 필요가 없다.

그래서 실행 단계에서는 JDK가 아니라 JRE 계열 이미지를 쓰는 게 더 자연스럽다.

## 단일 스테이지라면 이렇게 쓰는 게 더 좋음

이미 EC2나 Jenkins에서 JAR를 빌드한 뒤 `app.jar`로 만들어둔 구조라면 Dockerfile은 이렇게 가면 된다.

```dockerfile
FROM eclipse-temurin:17-jre

WORKDIR /app

COPY app.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

이게 더 맞는 구조다.

```text
빌드: EC2 호스트 / Jenkins / GitHub Actions
실행: Docker 컨테이너
```

컨테이너는 이미 완성된 JAR만 실행하니까 JDK까지 필요 없다.

## 멀티스테이지에서도 실행 단계는 JRE가 좋음

멀티스테이지 빌드라면 빌드 단계에서는 JDK가 필요하다.

```dockerfile
FROM gradle:8.7-jdk17 AS builder
```

Gradle로 Java 코드를 컴파일해야 하니까 여기서는 JDK가 필요하다.

하지만 최종 실행 단계는 JRE로 충분하다.

```dockerfile
FROM eclipse-temurin:17-jre

WORKDIR /app

COPY --from=builder /app/app.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

전체로 보면 이런 식이다.

```dockerfile
FROM gradle:8.7-jdk17 AS builder

WORKDIR /app

COPY . .

RUN gradle clean build -x test

RUN JAR_FILE=$(find build/libs -name "*.jar" ! -name "*plain.jar" | head -n 1) && \
    cp "$JAR_FILE" app.jar


FROM eclipse-temurin:17-jre

WORKDIR /app

COPY --from=builder /app/app.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

이 구조가 더 깔끔하다.

```text
builder stage: JDK 필요
runtime stage: JRE면 충분
```

## 그럼 왜 사람들이 JDK 이미지를 쓰기도 하냐

운영에서는 JRE가 더 가볍고 좋지만, JDK 이미지를 쓰는 경우도 있다.

첫째, 디버깅 도구가 필요할 때다.

JDK 이미지에는 `jcmd`, `jstack`, `jmap`, `jstat` 같은 진단 도구가 들어 있는 경우가 많다. 운영 중 JVM 문제를 깊게 분석해야 할 때는 JDK 이미지가 편할 수 있다.

둘째, 이미지 선택을 단순화하고 싶을 때다.

개발, 테스트, 운영을 모두 같은 JDK 베이스로 맞추면 버전 차이 문제를 줄일 수 있다. 대신 이미지가 무거워진다.

셋째, JRE 태그가 없는 배포판을 쓰는 경우도 있다.

Java 9 이후로 전통적인 의미의 JRE 배포가 줄어들면서, 이미지 제공 방식이 배포판마다 조금씩 다르다. 그래서 어떤 팀은 그냥 `jdk`나 `jre`, 또는 `runtime`, `alpine`, `slim` 중에서 안정적으로 제공되는 걸 고른다.

## 운영 기준 추천

Spring Boot 애플리케이션을 Docker로 실행만 한다면 추천은 이거다.

```dockerfile
FROM eclipse-temurin:17-jre
```

또는 더 줄이고 싶으면 이런 계열도 고려할 수 있다.

```dockerfile
FROM eclipse-temurin:17-jre-alpine
```

다만 `alpine`은 musl libc 기반이라서 일부 네이티브 라이브러리, 폰트, 타임존, 인증서, 모니터링 에이전트 쪽에서 예상치 못한 문제가 날 수 있다. 그래서 무조건 alpine이 정답은 아니다.

무난한 운영 선택지는 보통 이쪽이다.

```dockerfile
FROM eclipse-temurin:17-jre
```

또는 Debian 기반의 slim 계열이 있으면:

```dockerfile
FROM eclipse-temurin:17-jre-jammy
```

## 결론

네 말이 맞다.

```text
JAR를 이미 빌드해둔 단일 스테이지 실행 이미지라면 JDK보다 JRE가 더 적절함
```

그래서 단일 스테이지 Dockerfile은 이렇게 고치는 게 좋다.

```dockerfile
FROM eclipse-temurin:17-jre

WORKDIR /app

COPY app.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

그리고 멀티스테이지라면 이렇게 생각하면 된다.

```text
빌드 단계 = JDK
실행 단계 = JRE
```

내가 앞에서 `jdk`로 든 건 실행 안정성을 우선한 단순 예시였고, 네가 지적한 것처럼 **운영 이미지 최적화 관점에서는 JRE가 더 맞다.**