---
title: "[Docker] 윈도우에서 Docker 쓰려면 WSL이 꼭 필요할까?"
source: "https://velog.io/@yorange50/Docker-윈도우에서-Docker-쓰려면-WSL이-꼭-필요할까"
published: "2026-05-06T03:40:53.981Z"
tags: ""
backup_date: "2026-05-29T14:52:52.776552"
---

윈도우에서 Docker Desktop을 설치하다 보면 WSL이라는 말을 자주 보게 된다.
Docker를 설치하려는 건데 갑자기 WSL, Ubuntu, Linux 같은 단어가 같이 나오니까 처음에는 헷갈린다.

나도 처음에는 이런 생각이 들었다.

```text id="owbqj0"
나는 윈도우 쓰는데 왜 리눅스가 필요하지?
Docker Desktop만 설치하면 되는 거 아닌가?
WSL이랑 Ubuntu까지 꼭 해야 하나?
```

결론부터 말하면, **윈도우에서 Docker Desktop으로 리눅스 컨테이너를 쓰려면 WSL2가 거의 필수**라고 보면 된다.

---

## 1. Docker는 원래 리눅스 기반 기술이다

Docker 컨테이너는 겉으로 보면 그냥 프로그램을 실행하는 것처럼 보인다.

예를 들어 PostgreSQL을 Docker로 실행하면 이렇게 한다.

```powershell id="tf3mzu"
docker run --name board-postgres -e POSTGRES_USER=board -e POSTGRES_PASSWORD=board1234 -e POSTGRES_DB=boarddb -p 5432:5432 -d postgres:16
```

이 명령어를 치면 PostgreSQL이 내 컴퓨터에 설치되는 것처럼 느껴진다.

하지만 실제로는 PostgreSQL이 **컨테이너** 안에서 실행된다.
그리고 이 컨테이너는 기본적으로 리눅스 커널 기능을 사용한다.

대표적으로 이런 기능들이 있다.

```text id="yfbyav"
namespace
cgroup
filesystem isolation
network bridge
```

이 기능들은 리눅스에서 자연스럽게 제공되는 기능이다.
그래서 Docker는 원래 리눅스 서버에서 아주 자연스럽게 동작한다.

```text id="zij3hs"
Linux Server
→ Linux Kernel
→ Docker Engine
→ Container
```

---

## 2. 그런데 윈도우는 리눅스가 아니다

문제는 내가 쓰는 환경이 윈도우라는 점이다.

윈도우는 리눅스 커널을 그대로 쓰지 않는다.
그래서 리눅스 컨테이너를 바로 실행할 수 없다.

그럼 윈도우에서 Docker를 못 쓰냐?

그건 아니다.

중간에 리눅스 환경을 하나 만들어서 그 위에서 Docker 컨테이너를 실행하면 된다.

그 역할을 하는 것이 **WSL2**다.

```text id="rkrral"
Windows
→ WSL2
→ Docker Desktop
→ Linux Container
```

조금 더 구체적으로 보면 이런 느낌이다.

```text id="bsdycb"
내 Windows PC
→ WSL2로 만든 가벼운 Linux 환경
→ Docker Desktop이 그 환경을 사용
→ PostgreSQL 같은 Linux container 실행
```

즉 WSL2는 Docker Desktop이 리눅스 컨테이너를 실행할 수 있게 해주는 기반 환경이다.

---

## 3. WSL이란?

WSL은 Windows Subsystem for Linux의 줄임말이다.

말 그대로 윈도우 안에서 리눅스 환경을 사용할 수 있게 해주는 기능이다.

예전에는 가상머신을 따로 깔아야 리눅스를 쓸 수 있었다.

```text id="umuy4q"
Windows
→ VirtualBox 설치
→ Ubuntu 설치
→ Linux 사용
```

하지만 WSL을 사용하면 윈도우 안에서 비교적 가볍게 리눅스 명령어와 환경을 사용할 수 있다.

```text id="pftw1g"
Windows
→ WSL
→ Ubuntu
```

특히 Docker Desktop은 윈도우에서 보통 **WSL2 backend**를 사용한다.

여기서 중요한 것은 WSL1이 아니라 WSL2라는 점이다.
Docker Desktop은 리눅스 커널 기능이 필요하기 때문에 WSL2 기반이 일반적이다.

---

## 4. Ubuntu도 꼭 필요한가?

여기서 또 헷갈리는 부분이 있다.

```text id="0qyc6j"
WSL이 필요한 건 알겠는데,
Ubuntu도 꼭 써야 하나?
```

정리하면 이렇다.

```text id="j0dkvb"
WSL2는 필요
Ubuntu 터미널을 직접 쓰는 것은 필수는 아님
```

`wsl --install`을 실행하면 보통 Ubuntu가 같이 설치된다.

하지만 Docker Desktop만 사용할 목적이라면 매번 Ubuntu 터미널에 들어가서 작업할 필요는 없다.
PowerShell에서도 Docker 명령어를 사용할 수 있다.

예를 들어 PostgreSQL 컨테이너 실행은 PowerShell에서 해도 된다.

```powershell id="1v0jyz"
docker run --name board-postgres -e POSTGRES_USER=board -e POSTGRES_PASSWORD=board1234 -e POSTGRES_DB=boarddb -p 5432:5432 -d postgres:16
```

즉 Ubuntu는 WSL 환경의 대표 배포판으로 같이 설치되는 경우가 많지만,
Docker 명령어는 PowerShell에서도 충분히 사용할 수 있다.

---

## 5. WSL이 없으면 어떤 문제가 생길까?

WSL2가 제대로 준비되어 있지 않으면 Docker Desktop에서 이런 문제가 생길 수 있다.

```text id="ze16yp"
Docker Desktop이 실행되지 않음
WSL2 backend 관련 에러 발생
Linux containers 실행 불가
docker run postgres 실패
Docker engine이 starting 상태에서 멈춤
```

특히 PostgreSQL, Redis, MySQL, Nginx 같은 이미지는 대부분 리눅스 컨테이너로 사용한다.

그래서 윈도우에서 이런 이미지를 Docker로 띄우려면 WSL2가 필요하다.

```text id="ai5egm"
PostgreSQL container
Redis container
MySQL container
Nginx container
Spring Boot container
```

이런 것들은 실무에서도 대부분 리눅스 컨테이너 기준으로 다룬다.

---

## 6. 내 board 프로젝트 기준으로 보면?

내가 하려는 것은 이 구조다.

```text id="kv4guc"
Windows PC
→ Docker Desktop
→ PostgreSQL container
→ board_api
→ board_fe
```

조금 더 풀어보면 이렇다.

```text id="17xurg"
PostgreSQL은 Docker container로 실행
board_api는 Spring Boot + JPA로 PostgreSQL에 연결
board_fe는 Spring Boot + Thymeleaf로 화면 렌더링
board_fe와 board_api는 RestClient로 통신
```

여기서 PostgreSQL 컨테이너가 리눅스 기반으로 실행되기 때문에
윈도우에서는 Docker Desktop이 WSL2를 사용해야 한다.

그래서 전체 흐름은 이렇게 된다.

```text id="scjssb"
Windows
→ WSL2
→ Docker Desktop
→ PostgreSQL container
→ board_api에서 DB 연결
```

---

## 7. 설치 확인 명령어

관리자 PowerShell에서 WSL 상태를 확인할 수 있다.

```powershell id="5j2fjk"
wsl --status
```

정상적으로 WSL2가 설정되어 있다면 이런 식으로 확인할 수 있다.

```text id="g8ojnt"
Default Version: 2
```

WSL이 설치되어 있지 않다면 다음 명령어를 사용한다.

```powershell id="053bfp"
wsl --install
```

설치 후에는 재부팅이 필요할 수 있다.

재부팅 후 다시 확인한다.

```powershell id="syxhaa"
wsl --status
```

---

## 8. Docker Desktop 설치 후 확인

Docker Desktop 설치가 끝나면 PowerShell에서 Docker 명령어를 확인한다.

```powershell id="liirpp"
docker --version
```

정상적으로 설치되었다면 Docker 버전이 출력된다.

그리고 테스트용 컨테이너를 실행해볼 수 있다.

```powershell id="trd9nc"
docker run hello-world
```

이 명령어가 성공하면 Docker Desktop이 정상적으로 컨테이너를 실행할 수 있다는 뜻이다.

---

## 9. PostgreSQL 컨테이너 실행

Docker가 정상 동작하면 PostgreSQL을 실행할 수 있다.

```powershell id="zpce8i"
docker run --name board-postgres `
  -e POSTGRES_USER=board `
  -e POSTGRES_PASSWORD=board1234 `
  -e POSTGRES_DB=boarddb `
  -p 5432:5432 `
  -d postgres:16
```

PowerShell에서는 줄바꿈을 할 때 `\`가 아니라 백틱을 사용한다.

한 줄로 쓰면 더 간단하다.

```powershell id="odjdaf"
docker run --name board-postgres -e POSTGRES_USER=board -e POSTGRES_PASSWORD=board1234 -e POSTGRES_DB=boarddb -p 5432:5432 -d postgres:16
```

실행 확인은 다음 명령어로 한다.

```powershell id="u2t5t3"
docker ps
```

컨테이너 안의 PostgreSQL에 접속하려면 이렇게 한다.

```powershell id="y510f3"
docker exec -it board-postgres psql -U board -d boarddb
```

성공하면 다음과 같은 프롬프트가 나온다.

```text id="s7v3pt"
boarddb=#
```

---

## 10. 정리

윈도우에서 Docker를 쓸 때 WSL이 나오는 이유는 Docker 컨테이너가 리눅스 기반 기술이기 때문이다.

```text id="cmsly0"
Docker는 리눅스 커널 기능을 사용한다
Windows는 리눅스 커널이 아니다
그래서 중간에 WSL2가 필요하다
Docker Desktop은 WSL2를 기반으로 Linux container를 실행한다
```

Ubuntu를 매번 직접 사용할 필요는 없지만,
Docker Desktop이 리눅스 컨테이너를 실행하기 위한 기반으로 WSL2는 필요하다.

한 줄로 정리하면 이렇다.

```text id="4nm0nl"
윈도우에서 Docker Desktop으로 PostgreSQL 같은 리눅스 컨테이너를 실행하려면 WSL2가 사실상 필수다.
```

그래서 board 프로젝트를 진행할 때도 순서는 이렇게 잡으면 된다.

```text id="kgdbu0"
WSL2 설치
→ Docker Desktop 설치
→ PostgreSQL 컨테이너 실행
→ board_api에서 JPA로 DB 연결
→ board_fe에서 RestClient로 API 호출
```

처음에는 Docker를 설치하는 데만 시간이 걸리는 것처럼 보이지만,
이 과정을 한 번 끝내두면 이후에는 PostgreSQL, Redis, Jenkins, Prometheus 같은 것들도 전부 컨테이너로 쉽게 띄울 수 있다.
