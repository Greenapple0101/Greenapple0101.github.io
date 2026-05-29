---
title: "[DOCKER] 왜 멀티 스테이지 빌드를 쓰고, 왜 JRE만 남길까?"
source: "https://velog.io/@yorange50/DOCKER-왜-멀티-스테이지-빌드를-쓰고-왜-JRE만-남길까"
published: "2026-05-08T07:46:33.447Z"
tags: ""
backup_date: "2026-05-29T14:52:52.767414"
---



도커로 스프링부트를 배포하다 보면 처음엔 이런 생각이 든다.

```text
그냥 jar 넣고 실행하면 되는 거 아닌가?
```

그런데 실제 운영 환경에서는:

* 이미지 용량
* 빌드 속도
* OS 차이
* 캐싱
* CI/CD 환경

같은 문제들이 생긴다.

오늘은:

* Dockerfile 구조
* JDK vs JRE
* 멀티 스테이지 빌드
* target 폴더
* Docker 캐싱
* 환경별 yml 관리

까지 한 번에 정리해본다. 

---

# 1. FE도 환경별 yml이 필요하다

보통 Spring Boot만 profile을 나눈다고 생각하는데 FE도 마찬가지다.

예를 들어:

| 환경    | API 주소               |
| ----- | -------------------- |
| local | localhost:8080       |
| dev   | dev-api.myserver.com |
| prod  | api.myserver.com     |

환경마다 API 주소가 달라진다.

그래서 FE도:

```text
.env.local
.env.dev
.env.prod
```

혹은:

```text
application-local.yml
application-dev.yml
```

처럼 환경별 설정을 나눈다.

즉:

```text
BE만 profile 쓰는 게 아니라
FE도 환경별 설정 분리가 필요하다
```

---

# 2. Dockerfile은 왜 중요한가?

Compose보다 더 중요한 건 사실 Dockerfile이다.

왜냐면 Dockerfile이:

```text
“이 프로젝트를 어떤 방식으로 빌드하고 실행할지”
```

를 정의하기 때문이다.

---

# 3. Docker의 핵심 철학

Docker가 중요한 이유는:

```text
어떤 OS에서 실행하든 동일하게 동작하게 만들기 위해서
```

다.

원래는 OS마다:

* 명령어 다름
* 경로 다름
* 컴파일 환경 다름

문제가 생긴다.

예:

| OS      | 차이     |
| ------- | ------ |
| Windows | `.bat` |
| Linux   | `sh`   |
| Mac     | BSD 계열 |

그런데 Docker를 사용하면:

```text
컨테이너 내부를 표준 Linux 환경으로 통일
```

할 수 있다.

즉:

```text
내 PC에서는 되는데 서버에선 안됨
```

문제를 줄이는 게 Docker의 핵심이다.

---

# 4. Maven Build Stage

예시 Dockerfile:

```dockerfile
# syntax=docker/dockerfile:1

# ---------- Build stage ----------
FROM maven:3.9-eclipse-temurin-21 AS build

WORKDIR /workspace

COPY pom.xml .

RUN mvn -B -q dependency:go-offline

COPY src ./src

RUN mvn -B -q -DskipTests package
```

여기까지가 빌드 단계다.

즉:

```text
소스코드
→ 컴파일
→ jar 생성
```

까지 수행한다.

---

# 5. 왜 Maven 이미지를 쓰는가?

여기서 사용하는 이미지:

```dockerfile
FROM maven:3.9-eclipse-temurin-21
```

에는:

* Maven
* JDK
* Java Compiler

가 전부 들어있다.

왜냐면 빌드에는 컴파일러가 필요하기 때문이다.

---

# 6. JDK vs JRE

자바를 공부하면 자주 헷갈리는 부분이다.

---

## JDK

```text
Java Development Kit
```

개발용.

포함:

* javac (컴파일러)
* JRE
* 개발 도구

즉:

```text
.java
→ .class
```

로 바꾸려면 JDK가 필요하다.

---

## JRE

```text
Java Runtime Environment
```

실행용.

이미 컴파일된 프로그램을 실행만 한다.

즉:

```text
.class 실행
```

만 가능하다.

---

# 7. 왜 Runtime은 JRE만 쓸까?

실제 운영 서버에서는:

```text
컴파일은 끝난 상태
```

다.

즉:

```text
jar 실행만 하면 됨
```

그래서 굳이:

* Maven
* JDK
* Compiler

까지 넣을 필요가 없다.

---

# 8. 그래서 사용하는 게 멀티 스테이지 빌드

```dockerfile
# ---------- Runtime stage ----------
FROM eclipse-temurin:21-jre

WORKDIR /app

COPY --from=build /workspace/target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

핵심:

```dockerfile
COPY --from=build
```

이다.

즉:

```text
빌드 스테이지에서 만든 jar만 복사
```

한다.

---

# 9. 왜 이렇게 나누는가?

이유는 이미지 용량 때문이다.

전부 다 넣으면:

```text
Maven + JDK + Build Cache + Source
```

가 이미지에 포함된다.

그러면:

```text
1GB 이상
```

까지 커질 수 있다.

그래서:

| 방식     | 용량     |
| ------ | ------ |
| JDK 포함 | 매우 큼   |
| JRE만   | 훨씬 가벼움 |

운영에서는 대부분 JRE 기반 Runtime 이미지를 사용한다.

---

# 10. target 폴더는 뭘까?

Maven 빌드를 하면:

```text
target/
```

폴더가 생긴다.

여기에:

```text
jar 파일
class 파일
빌드 산출물
```

이 들어간다.

예:

```text
target/board-api-0.0.1-SNAPSHOT.jar
```

---

# 11. target은 직접 수정하는 폴더가 아니다

중요한 포인트.

```text
target은 프레임워크가 자동 생성하는 빌드 결과물
```

이다.

즉:

```text
직접 수정 X
```

보통 문제 생기면:

```bash
rm -rf target
```

하고 다시 빌드한다.

왜냐면 빌드 캐시나 이전 산출물이 꼬이는 경우가 많기 때문이다.

---

# 12. jar 이름은 어디서 정해질까?

보통:

```text
pom.xml
```

에서 정해진다.

예:

```xml
<artifactId>board-api</artifactId>
<version>0.0.1-SNAPSHOT</version>
```

그러면:

```text
board-api-0.0.1-SNAPSHOT.jar
```

가 생성된다.

---

# 13. SNAPSHOT은 뭘까?

보통 개발 중 버전에 붙는다.

예:

```text
1.0-SNAPSHOT
```

의미:

```text
아직 계속 변경 중인 버전
```

운영 배포 때는:

```text
1.0
```

처럼 SNAPSHOT을 제거하기도 한다.

---

# 14. Docker 캐싱은 왜 중요할까?

Docker는 레이어를 캐싱한다.

예:

```dockerfile
COPY pom.xml .
RUN mvn dependency:go-offline
```

이 부분이 캐싱되면 dependency 다운로드를 다시 안 한다.

즉:

```text
빌드 속도가 빨라짐
```

---

# 15. 그런데 쿠버네티스에서는?

로컬에서는 캐시가 남아있다.

하지만:

* GitHub Runner
* Kubernetes Pod
* CI 서버

환경에서는 컨테이너가 매번 새로 생성된다.

즉:

```text
빌드할 때마다 이미지 다운로드
```

가 발생할 수 있다.

그래서:

* 캐시 전략
* 이미지 경량화
* 레이어 분리

가 중요해진다.

---

# 16. 빌드를 밖에서 하는 경우도 있다

방법은 두 가지다.

---

## 1) 컨테이너 내부에서 빌드

```dockerfile
FROM maven ...
```

장점:

* 환경 통일
* 어디서든 동일 빌드 가능

---

## 2) 밖에서 Maven 빌드 후 jar만 복사

```bash
mvn package
```

후:

```dockerfile
COPY target/*.jar app.jar
```

장점:

* 더 빠를 수 있음
* CI 최적화 가능

---

# 17. 실제 이미지 크기 비교

실제 결과:

```text
board-api: 567MB
board-fe: 495MB
postgres:16-alpine: 395MB
```

alpine 같은 경량 이미지를 쓰면 훨씬 작아진다.

즉:

```text
이미지 최적화 = 배포 속도 + 저장 비용 + 실행 속도
```

와 연결된다.

---

# 마무리

오늘 핵심은:

* FE/BE 모두 환경별 설정 필요
* Docker는 OS 차이를 숨기기 위한 표준 환경
* Build Stage와 Runtime Stage를 분리
* JDK는 컴파일용
* JRE는 실행용
* target은 빌드 산출물
* Docker 캐싱은 빌드 속도와 직결
* 운영에서는 이미지 경량화가 중요

결국 Dockerfile은 단순 실행 파일이 아니라:

```text
“이 프로젝트를 어떤 방식으로 빌드하고 배포할 것인가”
```

를 정의하는 배포 설계서에 가깝다.
