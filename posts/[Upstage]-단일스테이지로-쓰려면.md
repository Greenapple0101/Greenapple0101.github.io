---
title: "[Docker] 단일스테이지로 쓰려면?"
source: "https://velog.io/@yorange50/Docker-단일스테이지로-쓰려면"
published: "2026-05-17T09:21:14.863Z"
tags: ""
backup_date: "2026-05-29T14:52:52.738674"
---

단일 스테이지로 쓰려면 핵심은 **“Dockerfile이 JAR를 복사하기 전에, EC2 호스트에 JAR가 실제로 존재해야 한다”**는 전제를 지키는 것이다.

즉, 단일 스테이지 구조는 보통 이렇게 간다.

```text
EC2에서 소스코드 받음
↓
EC2 호스트에서 Gradle 빌드 실행
↓
build/libs/*.jar 생성 확인
↓
docker build 실행
↓
Dockerfile이 JAR를 이미지 안으로 COPY
↓
컨테이너 실행
```

## 1. 가장 기본적인 단일 스테이지 Dockerfile

```dockerfile
FROM eclipse-temurin:17-jdk

WORKDIR /app

COPY build/libs/*.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
```

이 Dockerfile은 아주 단순하다.

```dockerfile
COPY build/libs/*.jar app.jar
```

이 줄은 **이미 호스트에 만들어져 있는 JAR 파일을 Docker 이미지 안으로 복사**한다.

그래서 Docker 빌드 전에 반드시 이걸 먼저 해야 한다.

```bash
./gradlew clean build -x test
```

그 다음에 Docker 이미지를 만든다.

```bash
docker build -t board-api .
```

그리고 실행한다.

```bash
docker run -d -p 8080:8080 --name board-api board-api
```

## 2. EC2에서 단일 스테이지로 배포하는 실제 순서

EC2에 접속해서 프로젝트 디렉터리로 이동한다.

```bash
cd board_api
```

Gradle 실행 권한이 없으면 권한을 준다.

```bash
chmod +x gradlew
```

JAR를 먼저 만든다.

```bash
./gradlew clean build -x test
```

JAR 파일이 생겼는지 확인한다.

```bash
ls -al build/libs
```

예를 들어 이렇게 보여야 한다.

```text
board-api-0.0.1-SNAPSHOT.jar
board-api-0.0.1-SNAPSHOT-plain.jar
```

그 다음 Docker 이미지를 빌드한다.

```bash
docker build -t board-api .
```

컨테이너 실행한다.

```bash
docker run -d \
  --name board-api \
  -p 8080:8080 \
  board-api
```

로그 확인한다.

```bash
docker logs -f board-api
```

## 3. plain.jar 문제 처리하기

Spring Boot + Gradle에서는 JAR가 2개 생길 수 있다.

```text
board-api-0.0.1-SNAPSHOT.jar
board-api-0.0.1-SNAPSHOT-plain.jar
```

여기서 보통 실행해야 하는 것은 `plain.jar`가 아닌 쪽이다.

그런데 Dockerfile에서 이렇게 쓰면 애매해질 수 있다.

```dockerfile
COPY build/libs/*.jar app.jar
```

`*.jar`에 여러 파일이 걸릴 수 있기 때문이다.

그래서 단일 스테이지에서도 안전하게 하려면 빌드 후 JAR 파일을 하나로 정리해두는 방식이 좋다.

```bash
./gradlew clean build -x test
cp build/libs/*SNAPSHOT.jar app.jar
```

단, 이러면 `plain.jar`까지 같이 걸릴 수 있으니 더 안전하게는 이렇게 한다.

```bash
JAR_FILE=$(find build/libs -name "*.jar" ! -name "*plain.jar" | head -n 1)
cp "$JAR_FILE" app.jar
```

그리고 Dockerfile은 이렇게 바꾼다.

```dockerfile
FROM eclipse-temurin:17-jdk

WORKDIR /app

COPY app.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
```

이러면 Dockerfile이 `build/libs/*.jar`를 직접 뒤지지 않는다.

대신 배포 스크립트에서 실행 가능한 JAR 하나를 `app.jar`로 정리해두고, Dockerfile은 그 파일만 복사한다.

## 4. 단일 스테이지용 배포 스크립트 예시

매번 명령어를 직접 치면 실수하기 쉬우니까 `deploy.sh`로 묶는 게 좋다.

```bash
#!/bin/bash

set -e

echo "1. Gradle 빌드 시작"
chmod +x gradlew
./gradlew clean build -x test

echo "2. 실행 가능한 JAR 선택"
JAR_FILE=$(find build/libs -name "*.jar" ! -name "*plain.jar" | head -n 1)

if [ -z "$JAR_FILE" ]; then
  echo "실행 가능한 JAR 파일을 찾지 못했습니다."
  exit 1
fi

echo "선택된 JAR: $JAR_FILE"

echo "3. app.jar로 복사"
cp "$JAR_FILE" app.jar

echo "4. Docker 이미지 빌드"
docker build -t board-api .

echo "5. 기존 컨테이너 제거"
docker rm -f board-api || true

echo "6. 새 컨테이너 실행"
docker run -d \
  --name board-api \
  -p 8080:8080 \
  board-api

echo "7. 컨테이너 상태 확인"
docker ps | grep board-api
```

실행 권한을 준다.

```bash
chmod +x deploy.sh
```

배포할 때는 이것만 실행한다.

```bash
./deploy.sh
```

## 5. 단일 스테이지 구조의 핵심 Dockerfile

최종적으로는 이 형태가 제일 깔끔하다.

```dockerfile
FROM eclipse-temurin:17-jdk

WORKDIR /app

COPY app.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

그리고 중요한 점은 이것이다.

```text
Dockerfile은 빌드를 하지 않는다.
이미 만들어진 app.jar만 실행 이미지에 넣는다.
```

즉, 책임이 이렇게 나뉜다.

```text
Gradle 빌드 책임: EC2 호스트 또는 Jenkins 또는 GitHub Actions
Docker 이미지 생성 책임: Dockerfile
애플리케이션 실행 책임: 컨테이너
```

## 6. 단일 스테이지를 쓰면 좋은 경우

단일 스테이지도 나쁜 방식은 아니다. 상황에 따라 충분히 쓸 수 있다.

예를 들어 이런 경우에는 괜찮다.

```text
로컬이나 CI에서 이미 JAR를 빌드함
Docker 이미지는 실행만 담당하게 하고 싶음
이미지 빌드 시간을 줄이고 싶음
빌드 환경과 실행 환경을 명확히 분리하고 싶음
Jenkins/GitHub Actions에서 빌드 산출물을 관리함
```

특히 CI/CD에서는 이런 구조도 흔하다.

```text
Jenkins
↓
./gradlew clean build
↓
app.jar 생성
↓
docker build
↓
docker push
↓
EC2에서 docker pull & run
```

이 경우에는 Dockerfile이 굳이 Gradle 빌드까지 할 필요가 없다.

## 7. 단일 스테이지의 단점

대신 단일 스테이지는 반드시 이 단점이 있다.

```text
Docker 빌드 전에 JAR가 없으면 실패
호스트 또는 CI 환경에 Java/Gradle 빌드 환경 필요
배포 순서를 지켜야 함
사람이 수동으로 하면 실수 가능성 있음
```

그래서 단일 스테이지를 쓸 거면 최소한 `deploy.sh` 같은 스크립트로 순서를 고정하는 게 좋다.

## 정리

단일 스테이지로 쓰려면 이렇게 하면 된다.

```text
1. EC2 또는 CI에서 ./gradlew clean build -x test 실행
2. build/libs에서 plain.jar 제외한 실행 JAR 선택
3. app.jar로 복사
4. Dockerfile에서 COPY app.jar app.jar
5. docker build
6. docker run
```

가장 추천하는 단일 스테이지 구성은 이거다.

```dockerfile
FROM eclipse-temurin:17-jdk

WORKDIR /app

COPY app.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

그리고 배포 전에 반드시 이걸 실행한다.

```bash
./gradlew clean build -x test

JAR_FILE=$(find build/libs -name "*.jar" ! -name "*plain.jar" | head -n 1)
cp "$JAR_FILE" app.jar

docker build -t board-api .
```

한 줄로 말하면, **단일 스테이지는 “JAR를 밖에서 미리 만들고, Docker는 그 JAR를 담아서 실행만 하는 구조”**다.