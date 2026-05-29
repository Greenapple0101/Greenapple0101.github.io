---
title: "[DOCKER] docker run 옵션 정리: -d, -p, -f, -a는 무슨 뜻일까?"
source: "https://velog.io/@yorange50/DOCKER-docker-run-옵션-정리-d-p-f-a는-무슨-뜻일까"
published: "2026-05-12T08:17:21.738Z"
tags: ""
backup_date: "2026-05-29T14:52:52.756600"
---

Docker 명령어를 보다 보면 이런 옵션들이 자주 나온다.

```bash
docker run -d -p 8080:8080 --name my-app hello-world:v1
```

또 로그를 볼 때는 이런 명령어도 나온다.

```bash
docker logs -f my-app
```

컨테이너에 붙을 때는 이런 것도 나온다.

```bash
docker attach my-app
```

처음 보면 `-d`, `-p`, `-f`, `-a` 같은 옵션들이 다 비슷해 보인다.

하지만 각각의 역할은 완전히 다르다.

핵심부터 정리하면 이렇다.

```text
-d : detached mode, 백그라운드 실행
-p : port mapping, 포트 연결
-f : follow, 로그 계속 따라보기
-a : attach 관련 옵션, 표준 입출력 연결
```

이 글에서는 Docker를 처음 다룰 때 자주 만나는 옵션들을 하나씩 정리해본다.

---

# 1. docker run 기본 구조

먼저 `docker run`의 기본 구조부터 보자.

```bash
docker run 이미지이름
```

예를 들어 Spring Boot 이미지를 실행한다면 이런 식이다.

```bash
docker run hello-world:v1
```

이 명령어는 `hello-world:v1` 이미지를 기반으로 컨테이너를 실행한다.

하지만 실제로는 이것만 쓰는 경우가 거의 없다.

보통은 포트를 연결해야 하고, 백그라운드로 실행해야 하고, 이름도 붙이고 싶다.

그래서 옵션을 붙인다.

```bash
docker run -d -p 8080:8080 --name hello-app hello-world:v1
```

이 명령어를 풀면 다음과 같다.

```text
-d
컨테이너를 백그라운드에서 실행

-p 8080:8080
내 PC의 8080 포트와 컨테이너의 8080 포트를 연결

--name hello-app
컨테이너 이름을 hello-app으로 지정

hello-world:v1
실행할 이미지
```

이제 옵션을 하나씩 보자.

---

# 2. -d: detached mode

`-d`는 detached mode의 줄임말이다.

```bash
docker run -d hello-world:v1
```

뜻은 간단하다.

```text
컨테이너를 백그라운드에서 실행하라
```

Docker 컨테이너를 실행하면 보통 컨테이너의 로그가 터미널에 바로 출력된다.

예를 들어 Spring Boot 앱을 이렇게 실행하면:

```bash
docker run -p 8080:8080 hello-world:v1
```

터미널에 Spring Boot 로그가 계속 찍힌다.

```text
Tomcat started on port 8080
Started HelloWorldApplication
```

이 상태에서는 터미널이 컨테이너에 붙잡힌다.
다른 명령어를 치기 어렵고, `Ctrl + C`를 누르면 컨테이너가 같이 종료될 수 있다.

반면 `-d`를 붙이면:

```bash
docker run -d -p 8080:8080 hello-world:v1
```

컨테이너는 뒤에서 계속 실행되고, 터미널은 바로 다시 사용할 수 있다.

실행하면 긴 컨테이너 ID가 출력된다.

```text
a7f3c9b1d8e2...
```

즉 `-d`는 이런 상황에서 쓴다.

```text
컨테이너를 계속 켜두고 싶을 때
터미널을 다른 작업에 계속 쓰고 싶을 때
서버처럼 백그라운드에서 실행하고 싶을 때
```

Spring Boot 앱, DB 컨테이너, Nginx 컨테이너처럼 계속 떠 있어야 하는 서비스는 보통 `-d`를 붙여 실행한다.

---

# 3. -d 없이 실행하면 어떻게 될까?

`-d` 없이 실행하면 foreground 모드로 실행된다.

```bash
docker run -p 8080:8080 hello-world:v1
```

이 경우 터미널에 로그가 바로 보인다.

장점도 있다.

```text
로그를 바로 볼 수 있음
앱이 왜 안 뜨는지 확인하기 쉬움
처음 디버깅할 때 편함
```

하지만 단점도 있다.

```text
터미널이 컨테이너에 붙잡힘
터미널을 닫으면 컨테이너도 종료될 수 있음
Ctrl + C 하면 컨테이너가 종료될 수 있음
```

그래서 처음 실행해서 로그를 보고 싶을 때는 `-d` 없이 실행해도 괜찮다.

하지만 정상 동작을 확인한 뒤에는 보통 `-d`로 실행한다.

```bash
docker run -d -p 8080:8080 --name hello-app hello-world:v1
```

---

# 4. -p: 포트 연결

`-p`는 port mapping의 의미다.

```bash
docker run -p 8080:8080 hello-world:v1
```

Docker 컨테이너는 기본적으로 격리된 환경에서 실행된다.

컨테이너 안에서 Spring Boot 앱이 8080 포트로 떠 있어도, 내 PC 브라우저에서 바로 접근할 수 있는 것은 아니다.

그래서 내 PC의 포트와 컨테이너의 포트를 연결해야 한다.

그때 쓰는 옵션이 `-p`다.

```bash
-p 내PC포트:컨테이너포트
```

예를 들어:

```bash
docker run -p 8080:8080 hello-world:v1
```

이건 이렇게 읽는다.

```text
내 PC의 8080 포트로 들어온 요청을
컨테이너 내부의 8080 포트로 보내라
```

Spring Boot가 컨테이너 안에서 8080으로 뜨고 있다면, 내 브라우저에서 이렇게 접속할 수 있다.

```text
http://localhost:8080
```

---

# 5. 8080:8080은 왜 두 번 쓰는가?

처음 Docker를 배우면 이 부분이 가장 헷갈린다.

```bash
-p 8080:8080
```

왼쪽과 오른쪽의 의미가 다르다.

```text
왼쪽 8080  = 내 PC 포트
오른쪽 8080 = 컨테이너 내부 포트
```

즉 다음과 같다.

```text
localhost:8080
        ↓
내 PC 8080 포트
        ↓
Docker가 컨테이너 8080 포트로 전달
        ↓
Spring Boot 앱
```

만약 이렇게 실행하면:

```bash
docker run -p 9090:8080 hello-world:v1
```

의미는 이렇다.

```text
내 PC의 9090 포트로 들어온 요청을
컨테이너 내부의 8080 포트로 보내라
```

그러면 브라우저에서는 이렇게 접속해야 한다.

```text
http://localhost:9090
```

하지만 컨테이너 안의 Spring Boot는 여전히 8080 포트로 떠 있다.

즉 중요한 건 이것이다.

```text
-p 앞쪽은 내가 접속할 포트
-p 뒤쪽은 컨테이너 안에서 앱이 실제로 쓰는 포트
```

---

# 6. -p를 안 붙이면 어떻게 될까?

Spring Boot 앱이 컨테이너 안에서 정상 실행되어도 `-p`를 안 붙이면 내 브라우저에서 접근이 안 될 수 있다.

예를 들어:

```bash
docker run hello-world:v1
```

컨테이너 안에서는 앱이 8080으로 떠 있을 수 있다.

하지만 내 PC의 8080 포트와 연결하지 않았기 때문에:

```text
http://localhost:8080
```

로 접속해도 안 될 수 있다.

그래서 웹 서버, API 서버, DB처럼 외부에서 접근해야 하는 컨테이너는 보통 `-p`를 붙인다.

```bash
docker run -p 8080:8080 hello-world:v1
```

---

# 7. -f: follow

`-f`는 보통 `docker logs`에서 자주 본다.

```bash
docker logs -f hello-app
```

여기서 `-f`는 follow의 의미다.

```text
로그를 한 번만 보여주지 말고 계속 따라가면서 보여달라
```

`docker logs`만 치면 현재까지 쌓인 로그를 출력하고 끝난다.

```bash
docker logs hello-app
```

하지만 `-f`를 붙이면 실시간으로 로그를 계속 보여준다.

```bash
docker logs -f hello-app
```

Spring Boot 앱을 백그라운드로 실행했을 때 특히 자주 쓴다.

```bash
docker run -d -p 8080:8080 --name hello-app hello-world:v1
```

이렇게 `-d`로 실행하면 터미널에 로그가 안 보인다.

그럴 때 로그를 확인하려면:

```bash
docker logs hello-app
```

실시간으로 계속 보고 싶으면:

```bash
docker logs -f hello-app
```

즉 `-d`와 `-f`는 자주 같이 등장한다.

```text
-d
컨테이너를 백그라운드로 실행

logs -f
백그라운드에서 실행 중인 컨테이너 로그를 실시간으로 보기
```

---

# 8. -f는 force일 때도 있다

여기서 조심할 점이 있다.

`-f`는 명령어에 따라 의미가 달라질 수 있다.

예를 들어 `docker logs -f`에서는 follow다.

```bash
docker logs -f hello-app
```

하지만 `docker rm -f`에서는 force다.

```bash
docker rm -f hello-app
```

이때는 뜻이 다르다.

```text
강제로 삭제하라
```

컨테이너가 실행 중이면 원래는 바로 삭제되지 않는다.

```bash
docker rm hello-app
```

실행 중인 컨테이너를 삭제하려 하면 에러가 날 수 있다.

그럴 때 `-f`를 붙이면 실행 중인 컨테이너를 강제로 중지하고 삭제한다.

```bash
docker rm -f hello-app
```

따라서 `-f`는 무조건 하나의 뜻만 있는 게 아니다.

```text
docker logs -f
-f = follow, 실시간으로 따라보기

docker rm -f
-f = force, 강제로 삭제

docker rmi -f
-f = force, 이미지 강제 삭제
```

옵션은 항상 어느 명령어에 붙었는지 같이 봐야 한다.

---

# 9. -a: attach 또는 all

`-a`도 명령어에 따라 의미가 달라진다.

대표적으로 두 가지로 많이 본다.

```text
docker ps -a
-a = all, 모든 컨테이너 보기

docker start -a
-a = attach, 실행하면서 터미널에 붙기
```

먼저 가장 자주 쓰는 건 `docker ps -a`다.

```bash
docker ps -a
```

`docker ps`는 현재 실행 중인 컨테이너만 보여준다.

```bash
docker ps
```

하지만 종료된 컨테이너까지 보고 싶으면 `-a`를 붙인다.

```bash
docker ps -a
```

여기서 `-a`는 all이다.

```text
실행 중인 컨테이너뿐 아니라
종료된 컨테이너까지 모두 보여달라
```

Docker를 공부할 때 가장 많이 쓰는 명령어 중 하나다.

---

# 10. docker ps와 docker ps -a 차이

예를 들어 컨테이너를 실행했다가 종료됐다고 하자.

```bash
docker run hello-world
```

이 컨테이너는 실행 후 바로 종료된다.

이때:

```bash
docker ps
```

를 치면 아무것도 안 보일 수 있다.

왜냐하면 현재 실행 중인 컨테이너가 없기 때문이다.

하지만:

```bash
docker ps -a
```

를 치면 종료된 컨테이너까지 보인다.

```text
CONTAINER ID   IMAGE         STATUS
abc123         hello-world   Exited
```

즉 정리하면:

```text
docker ps
현재 실행 중인 컨테이너만 보기

docker ps -a
종료된 컨테이너까지 전부 보기
```

Docker를 쓰다 보면 종료된 컨테이너가 계속 쌓인다.

그걸 확인할 때 `docker ps -a`를 쓴다.

---

# 11. attach로서의 -a

`-a`가 attach 의미로 쓰이는 경우도 있다.

예를 들어:

```bash
docker start -a hello-app
```

이 명령어는 정지된 컨테이너를 다시 시작하면서 터미널을 컨테이너에 붙인다.

```text
start
정지된 컨테이너 시작

-a
attach, 컨테이너의 출력에 붙기
```

다만 처음 배울 때는 `docker start -a`보다 아래 명령어들을 더 자주 쓴다.

```bash
docker run -d ...
docker logs -f 컨테이너명
docker ps -a
```

그래서 `-a`는 우선 이렇게 기억해도 충분하다.

```text
docker ps -a의 -a는 all
docker start -a의 -a는 attach
```

---

# 12. --name: 컨테이너 이름 지정

짧은 옵션은 아니지만 Docker에서 정말 자주 쓰는 옵션이 있다.

```bash
--name
```

예를 들어:

```bash
docker run -d -p 8080:8080 --name hello-app hello-world:v1
```

이건 컨테이너 이름을 `hello-app`으로 지정한다.

이름을 지정하지 않으면 Docker가 랜덤한 이름을 만든다.

예를 들면:

```text
sleepy_brown
angry_turing
friendly_morse
```

이런 이름이 자동으로 붙을 수 있다.

하지만 실무나 학습에서는 이름을 직접 지정하는 게 편하다.

```bash
docker logs hello-app
docker stop hello-app
docker rm hello-app
```

컨테이너 ID를 매번 복사하지 않아도 되기 때문이다.

그래서 Spring Boot 컨테이너를 실행할 때는 보통 이렇게 쓴다.

```bash
docker run -d -p 8080:8080 --name hello-app hello-world:v1
```

---

# 13. -e: 환경변수 전달

Spring Boot 앱을 Docker로 실행하다 보면 환경변수를 넘겨야 할 때가 있다.

이때 쓰는 옵션이 `-e`다.

```bash
docker run -e SPRING_PROFILES_ACTIVE=docker hello-world:v1
```

뜻은 이렇다.

```text
컨테이너 안에 SPRING_PROFILES_ACTIVE=docker 환경변수를 넣어라
```

Spring Boot에서는 프로필을 바꿀 때 자주 쓴다.

```bash
docker run -d \
  -p 8080:8080 \
  -e SPRING_PROFILES_ACTIVE=docker \
  --name hello-app \
  hello-world:v1
```

만약 DB 접속 정보도 환경변수로 넘긴다면 이렇게 쓸 수 있다.

```bash
docker run -d \
  -p 8080:8080 \
  -e SPRING_DATASOURCE_URL=jdbc:postgresql://host.docker.internal:5432/boarddb \
  -e SPRING_DATASOURCE_USERNAME=board \
  -e SPRING_DATASOURCE_PASSWORD=board1234 \
  --name board-api \
  ubuntu12341/board-api:v1
```

이렇게 하면 application.yml에서 환경변수를 읽을 수 있다.

```yaml
spring:
  datasource:
    url: ${SPRING_DATASOURCE_URL}
    username: ${SPRING_DATASOURCE_USERNAME}
    password: ${SPRING_DATASOURCE_PASSWORD}
```

---

# 14. --rm: 컨테이너 자동 삭제

`--rm`은 컨테이너가 종료되면 자동으로 삭제하라는 옵션이다.

```bash
docker run --rm hello-world
```

일회성 테스트를 할 때 좋다.

예를 들어 컨테이너를 잠깐 실행하고 결과만 보고 싶을 때:

```bash
docker run --rm alpine echo hello
```

이 컨테이너는 실행이 끝나면 자동으로 삭제된다.

장점은 종료된 컨테이너가 쌓이지 않는다는 것이다.

하지만 서버처럼 계속 띄워야 하는 컨테이너에는 보통 잘 안 쓴다.

Spring Boot 앱을 학습용으로 잠깐 실행한다면 가능하다.

```bash
docker run --rm -p 8080:8080 hello-world:v1
```

하지만 백그라운드로 계속 관리하고 싶다면 보통 이렇게 쓴다.

```bash
docker run -d -p 8080:8080 --name hello-app hello-world:v1
```

---

# 15. -it: 터미널 접속

`-it`는 보통 컨테이너 내부 쉘에 들어갈 때 쓴다.

```bash
docker run -it ubuntu bash
```

여기서 `-i`와 `-t`가 합쳐진 것이다.

```text
-i
interactive, 표준 입력을 열어둠

-t
tty, 터미널처럼 사용할 수 있게 함
```

둘을 같이 써서 `-it`라고 많이 쓴다.

예를 들어 Ubuntu 컨테이너 안에 들어가고 싶으면:

```bash
docker run -it ubuntu bash
```

실행 중인 컨테이너 안에 들어갈 때는 보통 `docker exec`와 같이 쓴다.

```bash
docker exec -it hello-app sh
```

또는 bash가 있는 이미지라면:

```bash
docker exec -it hello-app bash
```

Alpine 기반 이미지는 bash가 없을 수 있어서 보통 `sh`를 쓴다.

```bash
docker exec -it hello-app sh
```

---

# 16. 자주 쓰는 Docker 명령어 흐름

Spring Boot 앱을 Docker로 실행하는 기본 흐름은 다음과 같다.

## 1단계. 이미지 빌드

```bash
docker build -t hello-world:v1 .
```

뜻:

```text
현재 폴더의 Dockerfile을 사용해서
hello-world:v1이라는 이미지를 만든다
```

## 2단계. 컨테이너 실행

```bash
docker run -d -p 8080:8080 --name hello-app hello-world:v1
```

뜻:

```text
hello-world:v1 이미지를 컨테이너로 실행한다
백그라운드로 실행한다
내 PC 8080 포트와 컨테이너 8080 포트를 연결한다
컨테이너 이름은 hello-app으로 한다
```

## 3단계. 실행 중인지 확인

```bash
docker ps
```

## 4단계. 로그 확인

```bash
docker logs hello-app
```

실시간 로그 확인:

```bash
docker logs -f hello-app
```

## 5단계. 컨테이너 중지

```bash
docker stop hello-app
```

## 6단계. 종료된 컨테이너까지 확인

```bash
docker ps -a
```

## 7단계. 컨테이너 삭제

```bash
docker rm hello-app
```

강제 삭제:

```bash
docker rm -f hello-app
```

---

# 17. 자주 쓰는 옵션 표

| 옵션       | 주로 쓰는 명령어                   | 의미              |
| -------- | --------------------------- | --------------- |
| `-d`     | `docker run`                | 백그라운드 실행        |
| `-p`     | `docker run`                | 포트 연결           |
| `-f`     | `docker logs`               | 로그 실시간 따라보기     |
| `-f`     | `docker rm`, `docker rmi`   | 강제 삭제           |
| `-a`     | `docker ps`                 | 모든 컨테이너 보기      |
| `-a`     | `docker start`              | 컨테이너에 attach    |
| `--name` | `docker run`                | 컨테이너 이름 지정      |
| `-e`     | `docker run`                | 환경변수 전달         |
| `--rm`   | `docker run`                | 종료 후 컨테이너 자동 삭제 |
| `-it`    | `docker run`, `docker exec` | 터미널로 상호작용       |

옵션은 글자 하나만 보고 외우면 위험하다.

특히 `-f`, `-a`는 명령어에 따라 의미가 바뀐다.

```text
docker logs -f
-f = follow

docker rm -f
-f = force

docker ps -a
-a = all

docker start -a
-a = attach
```

그래서 옵션은 항상 이렇게 봐야 한다.

```text
어떤 명령어에 붙었는가?
```

---

# 18. Spring Boot 기준 추천 명령어

Spring Boot 앱을 Docker로 실행할 때 가장 무난한 명령어는 이거다.

```bash
docker run -d -p 8080:8080 --name spring-app hello-world:v1
```

여기서 각각의 의미는 다음과 같다.

```text
docker run
이미지를 컨테이너로 실행

-d
백그라운드 실행

-p 8080:8080
내 PC 8080 포트와 컨테이너 8080 포트를 연결

--name spring-app
컨테이너 이름 지정

hello-world:v1
실행할 이미지
```

실행 확인:

```bash
docker ps
```

로그 확인:

```bash
docker logs -f spring-app
```

중지:

```bash
docker stop spring-app
```

삭제:

```bash
docker rm spring-app
```

다시 실행하고 싶으면:

```bash
docker start spring-app
```

로그에 붙어서 보고 싶으면:

```bash
docker logs -f spring-app
```

---

# 19. 포트 충돌이 날 때

이미 내 PC의 8080 포트를 다른 프로그램이 쓰고 있으면 이런 문제가 날 수 있다.

```text
Bind for 0.0.0.0:8080 failed: port is already allocated
```

이럴 때는 왼쪽 포트를 바꾸면 된다.

```bash
docker run -d -p 9090:8080 --name spring-app hello-world:v1
```

이 명령어의 뜻은 이렇다.

```text
내 PC의 9090 포트로 들어온 요청을
컨테이너 내부의 8080 포트로 보낸다
```

그러면 접속 주소는 다음과 같다.

```text
http://localhost:9090
```

컨테이너 안의 Spring Boot는 여전히 8080에서 실행 중이다.

바뀐 건 내 PC에서 접속하는 포트뿐이다.

---

# 20. 최종 정리

Docker 옵션은 처음 보면 외계어처럼 보인다.

하지만 자주 쓰는 것부터 역할을 나눠서 보면 어렵지 않다.

```text
-d
백그라운드 실행

-p
내 PC 포트와 컨테이너 포트 연결

-f
logs에서는 실시간 로그 보기
rm에서는 강제 삭제

-a
ps에서는 전체 컨테이너 보기
start에서는 attach

--name
컨테이너 이름 지정

-e
환경변수 전달

--rm
종료 후 컨테이너 자동 삭제

-it
컨테이너 터미널 접속
```

Spring Boot 앱을 Docker로 실행할 때 가장 많이 쓰는 조합은 다음과 같다.

```bash
docker run -d -p 8080:8080 --name spring-app hello-world:v1
```

그리고 실행 상태와 로그는 이렇게 확인한다.

```bash
docker ps
docker logs -f spring-app
```

중지와 삭제는 이렇게 한다.

```bash
docker stop spring-app
docker rm spring-app
```

마지막으로 제일 중요한 감각은 이것이다.

```text
docker build는 이미지를 만드는 명령어다.
docker run은 이미지를 컨테이너로 실행하는 명령어다.

-d는 뒤에서 실행하라는 뜻이고,
-p는 포트를 연결하라는 뜻이다.

컨테이너가 안 보이면 docker ps -a,
로그가 안 보이면 docker logs -f,
지우고 싶으면 docker rm,
강제로 지우고 싶으면 docker rm -f를 쓴다.
```

Docker 옵션은 한 번에 다 외우는 게 아니라, 실제로 컨테이너를 띄우고 멈추고 지우면서 몸에 붙는 명령어에 가깝다.
