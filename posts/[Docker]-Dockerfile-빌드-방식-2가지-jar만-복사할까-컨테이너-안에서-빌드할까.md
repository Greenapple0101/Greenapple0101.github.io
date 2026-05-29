---
title: "[DOCKER] Dockerfile 빌드 방식 2가지: jar만 복사할까, 컨테이너 안에서 빌드할까?"
source: "https://velog.io/@yorange50/DOCKER-Dockerfile-빌드-방식-2가지-jar만-복사할까-컨테이너-안에서-빌드할까"
published: "2026-05-12T08:04:34.723Z"
tags: ""
backup_date: "2026-05-29T14:52:52.757657"
---

Spring Boot 애플리케이션을 Docker 이미지로 만들 때 처음 헷갈리는 지점이 있다.

“jar 파일을 먼저 만들고 Docker 이미지에 넣어야 하나?”
“아니면 Dockerfile 안에서 Maven 빌드까지 해야 하나?”
“둘 중에 어떤 방식이 실무에 더 가까운가?”
“어떤 OS에서도 잘 돌아가는 건 뭐지?”

결론부터 말하면, **간단히 연습할 때는 밖에서 jar를 빌드하고 복사하는 방식도 괜찮다.**
하지만 **팀 개발, 배포, CI/CD, 운영 환경까지 생각하면 멀티 스테이지 빌드 방식이 더 좋다.**

왜 그런지 하나씩 정리해보자.

---

# 1. Spring Boot 애플리케이션을 Docker 이미지로 만든다는 것

Spring Boot 프로젝트를 실행하려면 보통 이런 흐름을 거친다.

```bash
./mvnw clean package -DskipTests
```

그러면 `target` 폴더 아래에 `.jar` 파일이 생긴다.

예를 들면 이런 식이다.

```text
target/hello-world-0.0.1-SNAPSHOT.jar
```

이 jar 파일은 Spring Boot 애플리케이션을 실행할 수 있는 결과물이다.

그래서 로컬에서는 이렇게 실행할 수 있다.

```bash
java -jar target/hello-world-0.0.1-SNAPSHOT.jar
```

Docker 이미지로 만든다는 것은 결국 이 jar 파일을 컨테이너 안에 넣고, 컨테이너가 실행될 때 이 명령어를 대신 실행하게 만드는 것이다.

```bash
java -jar app.jar
```

즉 Dockerfile의 핵심은 단순하다.

```text
1. Java가 있는 이미지를 가져온다.
2. jar 파일을 컨테이너 안에 복사한다.
3. 컨테이너가 실행될 때 java -jar로 실행한다.
```

그런데 여기서 중요한 선택지가 생긴다.

```text
jar를 내 PC에서 먼저 만들 것인가?
아니면 Docker 빌드 과정 안에서 만들 것인가?
```

---

# 2. 방식 1: 밖에서 빌드하고 jar만 복사하기

첫 번째 방식은 로컬에서 먼저 Maven 빌드를 끝내는 방식이다.

```bash
./mvnw clean package -DskipTests
```

이 명령어를 실행하면 `target` 폴더에 jar 파일이 생긴다.

그 다음 Dockerfile은 이렇게 짧게 작성할 수 있다.

```dockerfile
FROM eclipse-temurin:21-jre

WORKDIR /app

COPY ./target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

이 방식의 핵심은 이 부분이다.

```dockerfile
COPY ./target/*.jar app.jar
```

내 로컬 PC에 이미 만들어진 jar 파일을 Docker 이미지 안으로 복사하는 것이다.

즉 이 Dockerfile은 직접 빌드를 하지 않는다.
이미 만들어진 결과물만 가져와서 실행 이미지로 포장한다.

---

# 3. 방식 1의 실행 흐름

전체 흐름은 이렇게 된다.

```text
내 PC에서 Maven 빌드
        ↓
target 폴더에 jar 생성
        ↓
Docker build 실행
        ↓
Docker 이미지 안에 jar 복사
        ↓
컨테이너 실행 시 java -jar app.jar 실행
```

명령어로 보면 다음과 같다.

```bash
./mvnw clean package -DskipTests
```

```bash
docker build -t hello-world:v1 .
```

```bash
docker run -p 8080:8080 hello-world:v1
```

이 방식은 처음 Docker를 배울 때 이해하기 쉽다.

왜냐하면 역할이 명확하기 때문이다.

```text
Maven: jar 만들기
Docker: jar 실행할 환경 만들기
```

처음에는 이게 훨씬 직관적이다.

---

# 4. 방식 1의 장점

이 방식의 장점은 단순함이다.

Dockerfile이 짧다.

```dockerfile
FROM eclipse-temurin:21-jre

WORKDIR /app

COPY ./target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

Spring Boot를 처음 Docker로 띄워볼 때는 이 정도만 알아도 충분히 컨테이너 실행까지 갈 수 있다.

또 하나의 장점은 로컬 Maven 캐시를 활용할 수 있다는 점이다.

내 PC에는 보통 Maven 의존성이 이미 다운로드되어 있다.
그래서 로컬에서 빌드하면 두 번째부터는 비교적 빠르게 빌드된다.

즉, 혼자 개발하면서 빠르게 테스트할 때는 꽤 편하다.

```text
Dockerfile이 짧음
개념이 단순함
처음 배우기 좋음
로컬 Maven 캐시를 활용할 수 있음
```

---

# 5. 방식 1의 단점

하지만 이 방식에는 중요한 단점이 있다.

**로컬 환경에 영향을 받는다.**

이 방식은 Dockerfile 안에서 빌드하지 않는다.
내 PC에서 먼저 jar를 만들어야 한다.

그러려면 내 PC에 Java가 제대로 설치되어 있어야 한다.

```bash
java -version
```

또 Maven Wrapper가 정상적으로 실행되어야 한다.

```bash
./mvnw clean package
```

Windows라면 명령어가 다를 수도 있다.

```powershell
.\mvnw.cmd clean package
```

Mac이나 Linux에서는 실행 권한 문제가 날 수 있다.

```bash
chmod +x mvnw
```

즉, jar를 만들기 전까지는 Docker가 아무것도 해결해주지 않는다.

Docker는 이미 만들어진 jar를 복사할 뿐이다.

그래서 이런 상황이 생길 수 있다.

```text
A 개발자 Mac에서는 빌드 성공
B 개발자 Windows에서는 빌드 실패
CI 서버에서는 Java 버전이 달라서 빌드 실패
내 PC에서는 되는데 다른 사람 PC에서는 안 됨
```

이게 바로 로컬 환경 의존성이다.

---

# 6. “어떤 OS에서도 잘 되는가?”라는 질문

여기서 중요한 질문이 나온다.

```text
어떤 OS에서도 더 잘 되는 방식은 무엇인가?
```

정답은 **멀티 스테이지 빌드 방식**이다.

물론 둘 다 Docker를 사용하긴 한다.
하지만 첫 번째 방식은 jar를 만들기 전 단계가 내 로컬 OS에 의존한다.

즉, Windows, macOS, Linux마다 Java 설치 상태, Maven 실행 방식, 권한, 환경변수가 다를 수 있다.

반면 멀티 스테이지 빌드는 Docker 빌드 과정 안에서 Maven 빌드까지 수행한다.

내 PC에는 Docker만 있으면 된다.
실제 Maven 빌드는 Docker 이미지 안에서 실행된다.

그래서 OS 차이를 훨씬 덜 탄다.

정리하면 이렇게 볼 수 있다.

```text
단일 방식:
내 PC에서 jar를 만들어야 함
그래서 내 PC의 OS, Java, Maven 상태에 영향을 받음

멀티 스테이지 방식:
Docker 안에서 jar를 만듦
그래서 내 PC에는 Docker만 있으면 됨
```

---

# 7. 방식 2: 컨테이너 안에서 빌드하기

두 번째 방식은 Docker 빌드 과정 안에서 Maven 빌드까지 수행하는 방식이다.

Dockerfile은 조금 길어진다.

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

이 방식을 **멀티 스테이지 빌드**라고 한다.

멀티 스테이지라는 말 그대로 Dockerfile 안에 여러 단계가 있다.

여기서는 크게 두 단계다.

```text
1. Build Stage
2. Runtime Stage
```

---

# 8. Build Stage란?

Build Stage는 애플리케이션을 빌드하는 단계다.

```dockerfile
FROM maven:3.9-eclipse-temurin-21 AS build
```

여기서는 `maven:3.9-eclipse-temurin-21` 이미지를 사용한다.

이 이미지 안에는 Maven과 JDK가 들어 있다.

즉, 이 단계에서는 다음 작업이 가능하다.

```text
소스코드 컴파일
의존성 다운로드
테스트 실행
jar 파일 생성
```

이 단계의 작업 디렉토리는 `/workspace`다.

```dockerfile
WORKDIR /workspace
```

먼저 `pom.xml`을 복사한다.

```dockerfile
COPY pom.xml .
```

그리고 의존성을 미리 다운로드한다.

```dockerfile
RUN mvn -B -q dependency:go-offline
```

그 다음 소스코드를 복사한다.

```dockerfile
COPY src ./src
```

마지막으로 Maven 빌드를 실행한다.

```dockerfile
RUN mvn -B -q -DskipTests package
```

이 명령어가 실행되면 컨테이너 안의 `/workspace/target` 경로에 jar 파일이 생성된다.

중요한 점은 이 jar 파일이 내 PC에서 만들어진 게 아니라는 점이다.

Docker build 과정 안에서 만들어진다.

---

# 9. Runtime Stage란?

Runtime Stage는 애플리케이션을 실행하는 단계다.

```dockerfile
FROM eclipse-temurin:21-jre
```

여기서는 JDK가 아니라 JRE 이미지를 사용한다.

JDK는 개발과 빌드에 필요한 도구까지 포함한다.
JRE는 Java 애플리케이션 실행에 필요한 구성만 포함한다.

Spring Boot jar를 실행할 때는 보통 JRE만 있어도 된다.

그래서 Runtime Stage에는 굳이 Maven이나 전체 JDK가 필요하지 않다.

작업 디렉토리는 `/app`이다.

```dockerfile
WORKDIR /app
```

그리고 Build Stage에서 만들어진 jar 파일만 가져온다.

```dockerfile
COPY --from=build /workspace/target/*.jar app.jar
```

이게 멀티 스테이지 빌드의 핵심이다.

```text
빌드는 무거운 이미지에서 하고
실행은 가벼운 이미지에서 한다
```

최종 이미지에는 Maven도 없고, 소스코드도 없고, 빌드 도구도 없다.
실행에 필요한 jar와 JRE만 남는다.

---

# 10. COPY --from=build의 의미

멀티 스테이지 빌드를 처음 보면 이 부분이 가장 낯설다.

```dockerfile
COPY --from=build /workspace/target/*.jar app.jar
```

여기서 `build`는 앞에서 선언한 이름이다.

```dockerfile
FROM maven:3.9-eclipse-temurin-21 AS build
```

즉 `AS build`라고 이름을 붙였기 때문에 뒤에서 `--from=build`로 참조할 수 있다.

의미는 이렇다.

```text
build 단계에 있는 /workspace/target/*.jar 파일을
현재 runtime 단계의 /app/app.jar로 복사하라
```

그러니까 Dockerfile 안에서 이런 일이 일어나는 것이다.

```text
Build Stage:
jar 생성

Runtime Stage:
Build Stage에서 jar만 가져오기
```

이 구조 덕분에 최종 이미지는 훨씬 깔끔해진다.

---

# 11. 왜 굳이 두 단계로 나눌까?

그냥 Maven 이미지에서 빌드하고 그대로 실행하면 안 될까?

예를 들면 이런 식으로 할 수도 있다.

```dockerfile
FROM maven:3.9-eclipse-temurin-21

WORKDIR /app

COPY . .

RUN mvn package -DskipTests

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "target/app.jar"]
```

물론 실행은 될 수 있다.

하지만 이 방식은 최종 이미지 안에 Maven, JDK, 소스코드, 빌드 캐시 등이 그대로 남을 수 있다.

운영 환경에서 애플리케이션을 실행하는 데 Maven은 필요 없다.
소스코드도 필요 없다.
빌드 도구도 필요 없다.

필요한 건 거의 이것뿐이다.

```text
JRE
jar 파일
```

그래서 빌드할 때 필요한 것과 실행할 때 필요한 것을 분리하는 것이다.

```text
빌드할 때 필요한 것:
Maven, JDK, source code, pom.xml

실행할 때 필요한 것:
JRE, jar
```

이걸 분리하면 이미지가 더 작고, 깔끔하고, 배포하기 좋아진다.

---

# 12. 멀티 스테이지 빌드의 장점

멀티 스테이지 빌드의 가장 큰 장점은 재현성이다.

내 PC가 Windows든, macOS든, Linux든 상관없이 Docker만 동작하면 같은 방식으로 빌드할 수 있다.

왜냐하면 Maven 빌드가 내 PC에서 실행되는 것이 아니라 Docker 이미지 안에서 실행되기 때문이다.

즉, 빌드 환경이 고정된다.

```dockerfile
FROM maven:3.9-eclipse-temurin-21 AS build
```

이 한 줄이 빌드 환경을 정해준다.

```text
Maven 3.9
Temurin JDK 21
```

팀원 모두가 같은 Dockerfile로 빌드하면, 같은 Maven/JDK 환경에서 빌드하게 된다.

CI/CD 서버에서도 마찬가지다.

GitHub Actions, Jenkins, GitLab CI 같은 곳에서도 Docker build만 수행하면 된다.

그래서 이런 장점이 생긴다.

```text
OS 차이를 덜 탐
Java 설치 여부에 덜 의존함
Maven 설치 여부에 덜 의존함
CI/CD에 올리기 좋음
팀원 간 환경 차이를 줄일 수 있음
최종 이미지가 깔끔함
빌드 환경과 실행 환경을 분리할 수 있음
```

---

# 13. 단일 방식과 멀티 스테이지 방식 비교

두 방식을 비교하면 이렇게 정리할 수 있다.

| 구분             | 밖에서 빌드 후 jar 복사 | 멀티 스테이지 빌드    |
| -------------- | --------------- | ------------- |
| 빌드 위치          | 내 로컬 PC         | Docker 컨테이너 안 |
| Dockerfile 길이  | 짧음              | 상대적으로 김       |
| 로컬 Java 필요 여부  | 필요              | 거의 불필요        |
| 로컬 Maven 필요 여부 | 필요              | 거의 불필요        |
| OS 영향          | 큼               | 작음            |
| CI/CD 적합성      | 상대적으로 낮음        | 높음            |
| 초보자 이해 난이도     | 쉬움              | 조금 어려움        |
| 실무 배포 친화성      | 낮음              | 높음            |
| 최종 이미지 관리      | 단순하지만 로컬 의존     | 깔끔하고 재현성 좋음   |

여기서 핵심은 이것이다.

```text
단일 방식은 간단하지만 로컬 환경을 탄다.
멀티 스테이지 방식은 조금 길지만 어떤 OS에서도 같은 방식으로 빌드하기 좋다.
```

---

# 14. “어떤 OS에서도 할 수 있는 것”은 멀티다

질문을 다시 보자.

```text
어떤 OS에서도 할 수 있는 게 멀티야 아니면 단일이야?
```

정확히 답하면 이렇다.

```text
둘 다 Docker가 있으면 실행은 가능하다.
하지만 OS 차이를 덜 타고 더 일관되게 빌드할 수 있는 건 멀티 스테이지 빌드다.
```

왜냐하면 단일 방식은 Docker 이전에 로컬 빌드가 먼저 필요하기 때문이다.

```bash
./mvnw clean package -DskipTests
```

이 명령이 내 PC에서 성공해야 한다.

그러려면 내 PC에 Java가 있어야 한다.
Maven Wrapper가 실행되어야 한다.
환경변수도 맞아야 한다.
권한 문제도 없어야 한다.

반면 멀티 스테이지 방식은 Dockerfile 안에서 빌드한다.

```dockerfile
RUN mvn -B -q -DskipTests package
```

이 명령은 내 PC가 아니라 Docker build 과정의 Maven 컨테이너 안에서 실행된다.

그래서 로컬 OS의 차이를 훨씬 덜 탄다.

---

# 15. 실무에서는 왜 멀티 스테이지를 선호할까?

실무에서는 혼자만 개발하지 않는다.

팀원이 여러 명이고, 각자 사용하는 OS도 다를 수 있다.

```text
누군가는 Windows
누군가는 Mac
누군가는 Linux
CI 서버는 Ubuntu
운영 서버는 Kubernetes
```

이런 상황에서 “내 컴퓨터에서는 되는데요”는 가장 피하고 싶은 말이다.

그래서 실무에서는 빌드 환경을 최대한 코드로 고정하려고 한다.

Dockerfile은 그 역할을 한다.

```text
어떤 버전의 Java를 쓸지
어떤 버전의 Maven을 쓸지
어디에서 빌드할지
최종 이미지에는 무엇만 남길지
```

이걸 Dockerfile에 명시하면 팀원과 CI/CD 서버가 같은 기준으로 빌드할 수 있다.

멀티 스테이지 빌드는 이 철학에 잘 맞는다.

```text
빌드 환경도 컨테이너로 고정
실행 환경도 컨테이너로 고정
최종 이미지에는 실행에 필요한 것만 포함
```

그래서 실무적인 배포 흐름에서는 멀티 스테이지 방식이 더 많이 쓰인다.

---

# 16. CI/CD에서의 차이

CI/CD를 생각하면 차이가 더 명확해진다.

단일 방식에서는 CI 서버가 먼저 Maven 빌드를 해야 한다.

```bash
./mvnw clean package -DskipTests
docker build -t my-app:v1 .
```

이 경우 CI 서버에는 Java 환경이 필요하다.
Maven Wrapper 실행 권한도 맞아야 한다.

반면 멀티 스테이지 빌드에서는 CI 서버가 Docker build만 하면 된다.

```bash
docker build -t my-app:v1 .
```

Dockerfile 안에서 Maven 빌드까지 처리하기 때문이다.

물론 CI 서버에 Docker는 필요하다.
하지만 애플리케이션 빌드 환경은 Dockerfile이 책임진다.

이게 운영 관점에서는 훨씬 깔끔하다.

```text
CI 서버에 이것저것 설치하기보다
Dockerfile 안에 빌드 환경을 명시하는 방식
```

이게 재현성 있는 빌드에 더 가깝다.

---

# 17. 그럼 단일 방식은 나쁜 방식인가?

아니다.

단일 방식도 충분히 쓸 수 있다.

특히 처음 배우는 단계에서는 단일 방식이 오히려 좋다.

왜냐하면 흐름을 분리해서 이해할 수 있기 때문이다.

```text
Maven으로 jar를 만든다.
Docker는 jar를 실행한다.
```

이 개념을 먼저 잡는 게 중요하다.

처음부터 멀티 스테이지 빌드를 보면 Dockerfile이 길고 복잡해 보여서 오히려 헷갈릴 수 있다.

그래서 학습 순서는 이렇게 가는 게 좋다.

```text
1단계: 로컬에서 jar 빌드
2단계: jar를 Docker 이미지에 복사
3단계: docker run으로 실행
4단계: 멀티 스테이지 빌드로 전환
5단계: CI/CD에 연결
```

즉, 단일 방식은 학습용으로 좋고, 멀티 스테이지 방식은 실무형으로 좋다.

---

# 18. 두 방식의 핵심 차이 한 문장 정리

첫 번째 방식은 이 문장으로 정리할 수 있다.

```text
내 PC에서 만든 jar를 Docker 이미지에 넣는 방식
```

두 번째 방식은 이 문장으로 정리할 수 있다.

```text
Docker가 직접 jar를 만들고, 최종 이미지에는 jar만 넣는 방식
```

더 짧게 말하면 이렇다.

```text
단일 방식:
밖에서 빌드하고 안에 넣는다.

멀티 스테이지 방식:
안에서 빌드하고 필요한 것만 남긴다.
```

---

# 19. Dockerfile을 읽는 관점

멀티 스테이지 Dockerfile을 다시 보면 이제 구조가 보인다.

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

이걸 문장으로 풀면 이렇다.

```text
먼저 Maven과 JDK가 들어 있는 이미지로 빌드 환경을 만든다.
pom.xml을 복사하고 의존성을 받는다.
src 폴더를 복사하고 Maven package를 실행해서 jar를 만든다.
그 다음 JRE만 있는 가벼운 이미지로 새 단계를 시작한다.
빌드 단계에서 만들어진 jar만 가져온다.
컨테이너가 실행되면 java -jar로 애플리케이션을 실행한다.
```

결국 Dockerfile은 어렵게 생겼지만, 하고 있는 일은 명확하다.

```text
빌드용 컨테이너에서 jar 만들기
실행용 컨테이너에 jar만 복사하기
```

---

# 20. 최종 정리

Spring Boot 애플리케이션을 Docker 이미지로 만드는 방법은 크게 두 가지로 볼 수 있다.

첫 번째는 로컬에서 jar를 먼저 만들고 Docker 이미지에 복사하는 방식이다.

```text
로컬 Maven 빌드
→ target/*.jar 생성
→ Docker 이미지에 jar 복사
→ 컨테이너에서 실행
```

이 방식은 단순하고 이해하기 쉽다.
처음 배우기 좋고, 로컬 테스트용으로도 충분하다.

하지만 로컬 환경에 영향을 받는다.

```text
Java 설치 상태
Maven 실행 여부
OS별 명령어 차이
권한 문제
환경변수 차이
```

두 번째는 Docker 빌드 과정 안에서 Maven 빌드까지 수행하는 멀티 스테이지 빌드 방식이다.

```text
Build Stage에서 jar 생성
→ Runtime Stage에 jar만 복사
→ 컨테이너에서 실행
```

이 방식은 Dockerfile이 조금 길지만 더 실무적이다.

특히 다음 상황에 강하다.

```text
팀원마다 OS가 다를 때
CI/CD에서 자동 빌드할 때
배포 이미지를 깔끔하게 만들고 싶을 때
로컬 Java/Maven 환경 의존성을 줄이고 싶을 때
운영에 가까운 빌드 방식을 만들고 싶을 때
```

결론은 이렇다.

```text
단일 방식은 간단하지만 로컬 환경을 탄다.
멀티 스테이지 방식은 조금 길지만 재현성이 좋다.

학습 초반에는 단일 방식으로 흐름을 이해하고,
실무형 배포로 갈수록 멀티 스테이지 빌드를 사용하는 것이 좋다.
```

가장 중요한 한 줄은 이것이다.

```text
어떤 OS에서도 일관되게 빌드하고 싶다면 멀티 스테이지 빌드가 더 적합하다.
```
