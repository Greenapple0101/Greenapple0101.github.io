---
title: "[DOCKER] EC2에서 Docker 빌드할 때 JAR 파일이 없어서 COPY가 실패한 문제"
source: "https://velog.io/@yorange50/DOCKER-EC2에서-Docker-빌드할-때-JAR-파일이-없어서-COPY가-실패한-문제"
published: "2026-05-17T09:01:08.643Z"
tags: ""
backup_date: "2026-05-29T14:52:52.739080"
---

Spring Boot 애플리케이션을 EC2 서버에 배포하다 보면, 로컬에서는 잘 되던 Docker 빌드가 서버에서는 갑자기 실패하는 경우가 있다. 그중 대표적인 문제가 바로 `JAR 파일 누락으로 인한 COPY 실패`다. 이번 글에서는 EC2 환경에서 Docker 이미지를 빌드하던 중 `build/libs/*.jar` 파일을 찾지 못해 빌드가 실패했던 문제와, 이를 멀티스테이지 빌드로 해결한 과정을 정리한다.

## 1. 문제 상황

Spring Boot 프로젝트를 Docker 이미지로 만들기 위해 처음에는 다음과 비슷한 Dockerfile을 사용했다.

```dockerfile
FROM eclipse-temurin:17-jdk

WORKDIR /app

COPY build/libs/*.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
```

이 Dockerfile의 의도는 단순하다.

먼저 Spring Boot 프로젝트를 Gradle로 빌드하면 `build/libs` 디렉터리 아래에 `.jar` 파일이 생성된다. 그리고 Docker 빌드 과정에서 그 JAR 파일을 이미지 안으로 복사한 뒤, 컨테이너 실행 시 `java -jar app.jar`로 애플리케이션을 실행하는 구조다.

로컬에서는 이미 `./gradlew build`를 실행해둔 상태였기 때문에 `build/libs/*.jar` 파일이 존재했고, Docker 빌드도 정상적으로 성공했다.

하지만 EC2 서버에서 Docker 빌드를 실행하자 다음과 같은 문제가 발생했다.

```bash
COPY failed: no source files were specified
```

또는 BuildKit 환경에서는 다음과 비슷한 에러가 나올 수 있다.

```bash
failed to calculate checksum of ref:
"/build/libs": not found
```

핵심은 Docker가 복사하려는 `build/libs/*.jar` 파일을 찾지 못했다는 것이다.

## 2. 원인 분석

문제의 원인은 Dockerfile 자체보다도 빌드 방식에 있었다.

기존 Dockerfile은 이미 JAR 파일이 만들어져 있다는 전제를 가지고 있었다.

```dockerfile
COPY build/libs/*.jar app.jar
```

즉, Docker 이미지를 만들기 전에 호스트 환경에서 미리 다음 명령어가 실행되어 있어야 했다.

```bash
./gradlew build
```

로컬 개발 환경에서는 이 흐름이 자연스럽게 맞아떨어질 수 있다.

개발자가 직접 Gradle 빌드를 실행하고, 그 결과로 생성된 JAR 파일을 Docker 이미지 안에 복사하면 되기 때문이다.

하지만 EC2 서버에서는 상황이 다르다.

EC2에 프로젝트 소스만 올려놓고 바로 Docker 빌드를 실행하면, 아직 `build/libs` 디렉터리가 없을 수 있다. 또는 `.gitignore` 때문에 `build` 디렉터리는 Git에 포함되지 않아 서버에 올라가지 않았을 수도 있다.

보통 Spring Boot 프로젝트에서는 `build/` 디렉터리를 Git에 올리지 않는다.

```gitignore
build/
```

따라서 EC2 서버에서 소스코드를 clone한 직후에는 다음 파일이 존재하지 않는다.

```bash
build/libs/*.jar
```

그 상태에서 Dockerfile이 이 파일을 복사하려고 하니 실패하는 것이다.

정리하면 문제 구조는 다음과 같다.

```text
Dockerfile은 build/libs/*.jar를 복사하려고 함
↓
하지만 EC2에는 아직 JAR 파일이 없음
↓
COPY build/libs/*.jar app.jar 실패
↓
Docker 이미지 빌드 실패
```

이 문제의 본질은 “Docker 빌드가 호스트에서 미리 생성된 산출물에 의존하고 있었다”는 점이다.

## 3. 왜 이 방식이 위험한가

처음 방식은 단순해 보이지만 운영 환경에서는 몇 가지 문제가 있다.

첫째, 배포 전에 반드시 호스트에서 Gradle 빌드를 먼저 해야 한다.

```bash
./gradlew build
docker build -t my-app .
```

이 순서를 지키지 않으면 Docker 빌드가 실패한다.

둘째, 호스트 환경에 Gradle, Java 버전, 권한, 캐시 상태 등이 모두 영향을 준다.

예를 들어 로컬에서는 Java 21로 빌드했는데 서버에서는 Java 17만 설치되어 있거나, 서버에 Gradle이 없거나, `./gradlew` 실행 권한이 없으면 배포 과정이 흔들릴 수 있다.

셋째, Docker 이미지가 “소스코드만 있으면 어디서든 동일하게 만들어지는 구조”가 아니게 된다.

Docker를 사용하는 이유 중 하나는 실행 환경을 이미지로 고정해서 재현성을 확보하기 위해서다. 그런데 이미지 빌드 전에 호스트에서 따로 JAR를 만들어야 한다면, Docker 빌드가 완전히 독립적이지 않다.

즉, 기존 방식은 다음과 같은 문제가 있었다.

```text
호스트 선빌드 필요
Gradle/JDK 환경에 의존
build/libs 산출물 누락 시 실패
배포 재현성 낮음
CI/CD 자동화에 불리함
```

## 4. 해결 방향: 멀티스테이지 빌드로 전환

이 문제를 해결하기 위해 Dockerfile을 멀티스테이지 빌드 방식으로 변경했다.

멀티스테이지 빌드는 Docker 이미지 빌드 과정 안에서 “빌드 단계”와 “실행 단계”를 분리하는 방식이다.

구조는 다음과 같다.

```text
1단계: Gradle 이미지에서 소스코드를 빌드해서 JAR 생성
2단계: JDK/JRE 이미지에 생성된 JAR만 복사해서 실행
```

즉, EC2 호스트에서 미리 `./gradlew build`를 실행하지 않아도 된다.

Docker 빌드 과정 안에서 Gradle 빌드가 수행되고, 그 결과물인 JAR 파일을 최종 실행 이미지로 복사한다.

## 5. 개선된 Dockerfile 예시

예시는 다음과 같다.

```dockerfile
# 1단계: 빌드 스테이지
FROM gradle:8.7-jdk17 AS builder

WORKDIR /app

COPY . .

RUN gradle clean build -x test

# 2단계: 실행 스테이지
FROM eclipse-temurin:17-jdk

WORKDIR /app

COPY --from=builder /app/build/libs/*.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
```

이제 Docker 빌드 명령어만 실행하면 된다.

```bash
docker build -t board-api .
```

기존에는 EC2에서 먼저 JAR 파일을 만들어야 했지만, 이제는 Docker가 알아서 컨테이너 내부에서 Gradle 빌드까지 수행한다.

```text
docker build 실행
↓
Gradle 빌드용 컨테이너에서 소스코드 빌드
↓
build/libs/*.jar 생성
↓
최종 실행 이미지에 JAR 복사
↓
Spring Boot 컨테이너 실행 가능
```

## 6. 그런데 build/libs/*.jar도 조심해야 한다

Spring Boot + Gradle 프로젝트에서는 `build/libs` 아래에 JAR 파일이 여러 개 생길 수 있다.

예를 들면 다음과 같다.

```text
build/libs/
├── board-api-0.0.1-SNAPSHOT.jar
└── board-api-0.0.1-SNAPSHOT-plain.jar
```

여기서 중요한 것은 `plain.jar`는 보통 실행 가능한 Spring Boot JAR가 아니라는 점이다.

Spring Boot 애플리케이션을 실행하려면 일반적으로 Boot 플러그인이 만든 실행 가능한 JAR를 사용해야 한다.

그런데 Dockerfile에서 단순히 이렇게 쓰면 문제가 생길 수 있다.

```dockerfile
COPY --from=builder /app/build/libs/*.jar app.jar
```

`*.jar`에 여러 파일이 걸리면 Docker의 COPY 동작이 기대와 다르게 실패하거나, 의도하지 않은 JAR가 복사될 수 있다.

따라서 더 안전하게 처리하려면 `plain.jar`를 제외하고 실행 가능한 JAR만 복사하도록 빌드 단계에서 파일명을 정리하는 방식이 좋다.

## 7. 다중 산출물 안전 처리

다음처럼 빌드 스테이지에서 실행 가능한 JAR만 골라 `app.jar`라는 이름으로 복사해둘 수 있다.

```dockerfile
FROM gradle:8.7-jdk17 AS builder

WORKDIR /app

COPY . .

RUN gradle clean build -x test

RUN JAR_FILE=$(find build/libs -name "*.jar" ! -name "*plain.jar" | head -n 1) && \
    cp "$JAR_FILE" app.jar

FROM eclipse-temurin:17-jdk

WORKDIR /app

COPY --from=builder /app/app.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
```

이 방식의 장점은 최종 실행 스테이지에서 더 이상 와일드카드에 의존하지 않는다는 것이다.

```dockerfile
COPY --from=builder /app/app.jar app.jar
```

빌드 스테이지에서 이미 실행할 JAR를 명확하게 하나로 정리했기 때문에, 최종 이미지는 항상 `/app/app.jar` 하나만 복사하면 된다.

흐름은 다음과 같다.

```text
Gradle 빌드 실행
↓
build/libs 아래에 여러 JAR 생성 가능
↓
plain.jar 제외
↓
실행 가능한 JAR 하나를 app.jar로 복사
↓
최종 이미지에는 app.jar만 포함
```

## 8. 조치 전후 비교

기존 방식은 다음과 같았다.

```text
EC2 호스트에서 ./gradlew build 필요
↓
build/libs/*.jar 생성
↓
docker build 실행
↓
JAR 복사
```

개선 후 방식은 다음과 같다.

```text
docker build 실행
↓
컨테이너 내부에서 Gradle 빌드
↓
JAR 생성
↓
실행 가능한 JAR만 app.jar로 정리
↓
최종 이미지 생성
```

비교하면 다음과 같다.

| 구분                | 기존 방식   | 개선 방식             |
| ----------------- | ------- | ----------------- |
| JAR 생성 위치         | EC2 호스트 | Docker 빌드 컨테이너 내부 |
| 사전 빌드 필요 여부       | 필요      | 불필요               |
| Gradle/JDK 호스트 의존 | 높음      | 낮음                |
| build/libs 누락 위험  | 있음      | 낮음                |
| 재현성               | 낮음      | 높음                |
| CI/CD 적용성         | 불안정     | 안정적               |

## 9. 성과

이번 조치의 핵심 성과는 “호스트 선빌드 의존 제거”와 “배포 재현성 확보”다.

이전에는 EC2 서버에서 Docker 이미지를 만들기 전에 반드시 JAR 파일이 존재해야 했다. 그래서 누군가 배포 순서를 잘못 실행하거나, 서버에 `build/libs`가 없는 상태에서 Docker 빌드를 하면 바로 실패했다.

하지만 멀티스테이지 빌드로 바꾼 뒤에는 Docker 빌드 과정 안에서 Gradle 빌드가 함께 수행된다.

즉, 소스코드와 Dockerfile만 있으면 어디서든 같은 방식으로 이미지를 만들 수 있다.

```text
소스코드 + Dockerfile
↓
docker build
↓
항상 동일한 방식으로 JAR 빌드
↓
항상 동일한 방식으로 이미지 생성
```

또한 `build/libs/*.jar`에 여러 산출물이 생기는 문제도 안전하게 처리했다. `plain.jar` 같은 실행 대상이 아닌 파일을 제외하고, 실제 실행 가능한 JAR만 `app.jar`로 정리함으로써 배포 안정성을 높였다.

## 10. 이 트러블슈팅의 의미

이 문제는 단순히 `COPY failed` 에러 하나를 고친 것이 아니다.

더 중요한 포인트는 배포 구조를 바꾼 것이다.

처음에는 Docker 이미지가 호스트에서 만들어진 JAR 파일에 의존했다.

```text
호스트에서 잘 빌드되어 있어야 Docker도 성공
```

하지만 개선 후에는 Docker 빌드 자체가 애플리케이션 빌드까지 책임지게 되었다.

```text
Docker 빌드만 실행하면 애플리케이션 빌드와 이미지 생성이 함께 완료
```

이 차이는 운영 환경에서 매우 크다.

운영 배포는 사람이 매번 순서를 기억해서 맞추는 방식보다, 명령어 하나를 실행하면 일관되게 결과가 나오는 구조가 좋다. 특히 EC2, Jenkins, GitHub Actions 같은 환경에서 자동 배포를 구성할 때는 더 그렇다.

결국 이번 트러블슈팅은 다음 문제를 해결한 사례라고 볼 수 있다.

```text
문제:
EC2 Docker 빌드 시 build/libs/*.jar 파일이 없어 COPY 실패

원인:
Dockerfile이 호스트에서 미리 생성된 JAR 파일에 의존

조치:
멀티스테이지 빌드로 전환하여 컨테이너 내부에서 Gradle 빌드 수행
build/libs/*.jar 다중 산출물 문제를 고려해 실행 가능한 JAR만 app.jar로 정리

성과:
호스트 선빌드 의존 제거
배포 재현성 확보
Docker 빌드 안정성 향상
CI/CD 적용에 적합한 구조로 개선
```

## 마무리

EC2에서 Docker 빌드가 실패했을 때 에러 메시지만 보면 단순히 “JAR 파일이 없네?” 정도로 보일 수 있다.

하지만 실제 원인은 배포 프로세스가 호스트 환경에 지나치게 의존하고 있었기 때문이다.

Docker를 사용하는 목적은 단순히 애플리케이션을 컨테이너로 감싸는 것이 아니라, 빌드와 실행 환경을 최대한 일관되게 만드는 데 있다.

이번 문제를 멀티스테이지 빌드로 해결하면서, 단순한 에러 수정이 아니라 배포 구조 자체를 더 안정적으로 개선할 수 있었다.
