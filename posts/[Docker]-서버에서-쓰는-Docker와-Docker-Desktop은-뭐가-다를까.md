---
title: "[Docker] 서버에서 쓰는 Docker와 Docker Desktop은 뭐가 다를까?"
source: "https://velog.io/@yorange50/Docker-서버에서-쓰는-Docker와-Docker-Desktop은-뭐가-다를까"
published: "2026-05-06T01:37:29.616Z"
tags: ""
backup_date: "2026-05-29T14:52:52.776841"
---

Docker를 처음 설치하려고 하면 가장 헷갈리는 지점이 있다.
분명 Docker를 쓰려는 건 똑같은데, 어떤 글에서는 `Docker Desktop`을 설치하라고 하고, 어떤 글에서는 서버에 `docker engine`을 설치하라고 한다.
둘 다 Docker는 맞지만, 사용 목적과 환경이 다르다.

이번 글에서는 **개발자 로컬 PC에서 쓰는 Docker Desktop**과 **리눅스 서버에서 쓰는 Docker Engine**의 차이를 정리한다.

---

## 1. Docker는 원래 리눅스 기술에 가깝다

Docker 컨테이너는 기본적으로 리눅스 커널의 기능을 사용한다.

대표적으로 이런 기능들이 쓰인다.

```text
namespace
cgroup
overlay filesystem
network bridge
```

그래서 리눅스 서버에서는 Docker가 비교적 자연스럽게 동작한다.

```text
리눅스 서버
→ 리눅스 커널
→ Docker Engine
→ 컨테이너 실행
```

하지만 윈도우나 맥은 리눅스 커널이 아니다.
그래서 로컬 PC에서 Docker를 쓰려면 중간에 리눅스 환경이 필요하다.

그 역할을 해주는 것이 Docker Desktop이다.

```text
Windows / macOS
→ Docker Desktop
→ 내부 Linux VM 또는 WSL2
→ Docker Engine
→ 컨테이너 실행
```

---

## 2. Docker Desktop이란?

Docker Desktop은 개인 PC에서 Docker를 쉽게 쓰도록 만든 통합 프로그램이다.

윈도우나 맥에서 Docker를 바로 쓸 수 있게 다음 기능들을 묶어서 제공한다.

```text
Docker Engine
Docker CLI
Docker Compose
GUI 화면
이미지/컨테이너 관리 기능
Windows에서는 WSL2 연동
macOS에서는 내부 Linux VM
```

즉 Docker Desktop은 단순히 Docker 하나만 설치하는 게 아니라,
로컬 개발자가 편하게 Docker를 사용할 수 있도록 필요한 것들을 한 번에 설치해주는 패키지다.

예를 들어 윈도우에서 Docker Desktop을 설치하면 PowerShell에서 바로 이런 명령어를 쓸 수 있다.

```powershell
docker ps
docker run hello-world
docker compose up -d
```

그리고 Docker Desktop 앱 화면에서 컨테이너 상태를 눈으로 확인할 수 있다.

---

## 3. 서버에서 쓰는 Docker는 보통 Docker Engine이다

반면 리눅스 서버에서는 보통 Docker Desktop을 설치하지 않는다.

서버에는 GUI가 없는 경우가 많고, Docker를 백그라운드 서비스로 돌리는 게 목적이기 때문이다.

리눅스 서버에서는 보통 이런 식으로 설치한다.

```bash
sudo apt update
sudo apt install docker.io
```

또는 Docker 공식 저장소를 등록해서 설치한다.

설치 후에는 Docker 데몬이 systemd 서비스로 실행된다.

```bash
sudo systemctl status docker
sudo systemctl start docker
sudo systemctl enable docker
```

서버에서 Docker 구조는 대략 이렇다.

```text
Linux Server
→ systemd
→ docker daemon
→ container
```

사용자는 SSH로 서버에 접속해서 CLI 명령어로 컨테이너를 관리한다.

```bash
docker ps
docker logs app
docker stop app
docker compose up -d
```

---

## 4. 둘 다 결국 docker 명령어를 쓴다

중요한 점은 Docker Desktop이든 서버 Docker든,
실제로 사용하는 명령어는 거의 비슷하다는 것이다.

예를 들어 PostgreSQL 컨테이너를 실행하는 명령어는 로컬에서도 서버에서도 거의 같다.

```bash
docker run --name board-postgres \
  -e POSTGRES_USER=board \
  -e POSTGRES_PASSWORD=board1234 \
  -e POSTGRES_DB=boarddb \
  -p 5432:5432 \
  -d postgres:16
```

차이는 이 명령어가 어디에서 실행되느냐다.

```text
내 노트북 PowerShell에서 실행
→ 내 노트북 안의 Docker Desktop이 컨테이너 실행

리눅스 서버 SSH에서 실행
→ 서버의 Docker Engine이 컨테이너 실행
```

명령어는 비슷하지만 컨테이너가 떠 있는 위치가 달라진다.

---

## 5. 포트 접근 방식 차이

로컬 Docker Desktop에서 PostgreSQL을 띄우면 보통 이렇게 접근한다.

```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/boarddb
```

왜냐하면 Spring Boot 애플리케이션도 내 PC에서 실행되고, PostgreSQL 컨테이너도 내 PC의 Docker Desktop 안에서 실행되기 때문이다.

```text
내 PC의 Spring Boot
→ localhost:5432
→ 내 PC의 Docker Desktop PostgreSQL
```

반면 서버에서 PostgreSQL 컨테이너를 띄우면 상황이 달라진다.

내 PC에서 서버 DB에 접속하려면 `localhost`가 아니라 서버 IP를 사용해야 한다.

```properties
spring.datasource.url=jdbc:postgresql://서버IP:5432/boarddb
```

하지만 서버 안에서 Spring Boot도 같이 Docker 컨테이너로 띄운다면 보통 컨테이너 이름으로 통신한다.

```properties
spring.datasource.url=jdbc:postgresql://postgres:5432/boarddb
```

예를 들어 Docker Compose에서는 이런 구조가 가능하다.

```text
app container
→ postgres:5432
→ postgres container
```

이때 `postgres`는 컨테이너 이름 또는 서비스 이름이다.

---

## 6. Docker Desktop은 개발용에 가깝다

Docker Desktop은 로컬 개발 환경에 좋다.

예를 들면 이런 상황이다.

```text
내 PC에서 PostgreSQL 테스트용으로 띄우기
Spring Boot와 DB 연결 연습하기
개발용 Redis 실행하기
Dockerfile 빌드 테스트하기
docker compose 연습하기
컨테이너 로그를 GUI로 보기
```

즉 Docker Desktop은 “내 컴퓨터에서 서버 비슷한 환경을 흉내 내는 도구”에 가깝다.

특히 윈도우에서는 Docker Desktop이 WSL2를 이용해서 리눅스 컨테이너를 실행해준다.

```text
Windows
→ Docker Desktop
→ WSL2
→ Linux container
```

그래서 윈도우 개발자가 Docker를 배우거나 로컬 DB를 띄울 때는 Docker Desktop이 가장 접근성이 좋다.

---

## 7. 서버 Docker는 운영 환경에 가깝다

서버 Docker는 실제 애플리케이션을 배포하거나 운영하는 데 많이 사용한다.

예를 들면 이런 상황이다.

```text
EC2 서버에 Spring Boot 애플리케이션 배포
Nginx 컨테이너 실행
PostgreSQL 컨테이너 운영
Prometheus, Grafana 모니터링 구성
Jenkins에서 docker build 후 서버에 배포
docker compose로 여러 서비스 관리
```

서버에서는 GUI보다 안정성과 자동화가 더 중요하다.

그래서 보통 이런 방식으로 관리한다.

```text
SSH 접속
systemctl로 Docker 데몬 관리
docker compose로 서비스 실행
로그 확인
재시작 정책 설정
방화벽/보안그룹 설정
볼륨 마운트로 데이터 보존
```

---

## 8. 데이터 저장 방식도 신경 써야 한다

Docker 컨테이너는 삭제되면 내부 데이터도 사라질 수 있다.

그래서 PostgreSQL 같은 DB를 Docker로 띄울 때는 볼륨을 사용하는 것이 좋다.

로컬 개발에서는 간단히 이렇게 실행할 수 있다.

```bash
docker run --name board-postgres \
  -e POSTGRES_USER=board \
  -e POSTGRES_PASSWORD=board1234 \
  -e POSTGRES_DB=boarddb \
  -p 5432:5432 \
  -v board-postgres-data:/var/lib/postgresql/data \
  -d postgres:16
```

여기서 중요한 부분은 이거다.

```bash
-v board-postgres-data:/var/lib/postgresql/data
```

이렇게 하면 컨테이너를 삭제해도 DB 데이터가 Docker volume에 남는다.

서버에서는 이 부분이 더 중요하다.

```text
컨테이너는 언제든 다시 만들 수 있음
하지만 DB 데이터는 사라지면 안 됨
그래서 volume 또는 외부 디스크 마운트 필요
```

운영 환경에서는 DB를 컨테이너로 직접 운영하기보다 RDS 같은 관리형 DB를 쓰는 경우도 많다.
하지만 학습용, 개발용, 내부 서비스용으로는 Docker 기반 DB도 많이 사용한다.

---

## 9. Docker Desktop과 서버 Docker 비교

| 구분     | Docker Desktop               | 서버 Docker Engine           |
| ------ | ---------------------------- | -------------------------- |
| 사용 환경  | Windows, macOS 로컬 PC         | Linux 서버                   |
| 목적     | 개발, 테스트, 학습                  | 배포, 운영, 자동화                |
| 실행 방식  | GUI + CLI                    | CLI 중심                     |
| 내부 구조  | WSL2 또는 Linux VM 사용          | 리눅스 커널 위에서 직접 실행           |
| 설치 대상  | 개발자 개인 PC                    | EC2, 온프레미스 서버, VM          |
| 관리 방식  | Docker Desktop 앱, PowerShell | SSH, systemctl, docker CLI |
| 포트 접근  | 보통 localhost                 | 서버 IP, 도메인, 내부 네트워크        |
| 데이터 보존 | volume 사용 권장                 | volume/디스크/백업 필수           |
| 실무 위치  | 로컬 개발환경                      | 운영 또는 배포환경                 |

---

## 10. 내 board 프로젝트에 적용하면?

현재 board 프로젝트 기준으로 보면 이렇게 나눌 수 있다.

### 로컬 개발 환경

```text
Windows PC
→ Docker Desktop
→ PostgreSQL 컨테이너
→ board_api 실행
→ board_fe 실행
```

이때 DB 연결 설정은 보통 이거다.

```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/boarddb
```

즉 내 컴퓨터에서 Spring Boot를 실행하고,
내 컴퓨터 Docker Desktop 안에 있는 PostgreSQL에 붙는다.

---

### 서버 배포 환경

나중에 EC2 같은 리눅스 서버에 올리면 구조가 달라질 수 있다.

```text
EC2 Linux Server
→ Docker Engine
→ PostgreSQL container
→ board_api container
→ board_fe container
```

이 경우에는 Docker Compose를 써서 한 번에 띄울 수 있다.

```text
docker compose up -d
```

그리고 컨테이너끼리는 `localhost`가 아니라 서비스 이름으로 통신한다.

```properties
spring.datasource.url=jdbc:postgresql://postgres:5432/boarddb
```

---

## 11. 정리

Docker Desktop과 서버 Docker는 완전히 다른 기술이라기보다,
**Docker를 어느 환경에서 어떻게 쓰느냐의 차이**에 가깝다.

```text
Docker Desktop
→ 내 PC에서 Docker를 쉽게 쓰게 해주는 개발용 도구

Docker Engine on Linux Server
→ 실제 서버에서 컨테이너를 실행하고 운영하는 도구
```

명령어는 비슷하다.

```bash
docker ps
docker run
docker logs
docker stop
docker compose up -d
```

하지만 실행 위치와 목적이 다르다.

```text
내 PC에서 실행하면 로컬 개발환경
서버에서 실행하면 배포/운영환경
```

그래서 처음에는 Docker Desktop으로 로컬에서 PostgreSQL을 띄우고,
Spring Boot와 연결해보는 것이 좋다.

이후 서버 배포 단계에서는 같은 개념을 리눅스 서버의 Docker Engine으로 옮겨가면 된다.

한 줄로 정리하면 이렇다.

```text
Docker Desktop은 개발자 PC용 Docker 환경이고,
서버 Docker는 리눅스 서버에서 실제 서비스를 돌리기 위한 Docker 환경이다.
```
