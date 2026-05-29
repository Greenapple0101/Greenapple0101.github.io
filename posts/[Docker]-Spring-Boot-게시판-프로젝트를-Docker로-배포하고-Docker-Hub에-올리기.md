---
title: "[Docker] Spring Boot 게시판 프로젝트를 Docker로 배포하고 Docker Hub에 올리기"
source: "https://velog.io/@yorange50/Docker-Spring-Boot-게시판-프로젝트를-Docker로-배포하고-Docker-Hub에-올리기"
published: "2026-05-08T04:10:32.469Z"
tags: ""
backup_date: "2026-05-29T14:52:52.768119"
---

![](https://velog.velcdn.com/images/yorange50/post/d710c678-850d-4cb1-bf2d-8641f001537d/image.png)

이번에는 로컬에서 실행하던 게시판 프로젝트를 Docker 컨테이너 환경으로 배포하고, 직접 만든 이미지를 Docker Hub에 push하는 과정을 정리한다.

기존에는 FE, API, DB를 각각 로컬에서 실행했다.

```text
FE 서버 실행
API 서버 실행
PostgreSQL 컨테이너 실행
```

하지만 실제 배포 환경에서는 각 서비스를 컨테이너 단위로 나누고, Docker 이미지로 만들어 어디서든 실행할 수 있게 구성하는 것이 중요하다.

이번 목표는 다음과 같다.

```text
1. FE를 Docker 컨테이너로 실행
2. API를 Docker 컨테이너로 실행
3. DB는 PostgreSQL 컨테이너로 실행
4. docker-compose로 FE / API / DB를 한 번에 실행
5. FE / API 이미지를 Docker Hub에 push
```

---

# 1. 전체 구조

이번 프로젝트는 크게 세 개의 서비스로 구성된다.

```text
board
 ├─ fe
 ├─ api
 └─ db
```

Docker Desktop에서는 최종적으로 다음처럼 세 개의 컨테이너가 실행된다.

```text
board
 ├─ db   → postgres:16-alpine
 ├─ api  → local/board-api:latest
 └─ fe   → local/board-fe:latest
```

포트는 다음과 같이 연결했다.

```text
db   : 5432:5432
api  : 8080:8080
fe   : 8081:8081
```

즉 브라우저에서는 FE에 접속한다.

```text
http://localhost:8081
```

API는 다음 포트에서 확인할 수 있다.

```text
http://localhost:8080
```

DB는 PostgreSQL 컨테이너 내부에서 실행된다.

---

# 2. 왜 Docker로 배포하는가

로컬에서 직접 실행하면 다음과 같은 문제가 생길 수 있다.

```text
Java 버전 차이
Node 버전 차이
DB 설치 여부 차이
환경변수 차이
실행 명령어 차이
운영체제 차이
```

즉 내 컴퓨터에서는 잘 되는데 다른 컴퓨터에서는 안 될 수 있다.

Docker는 이 문제를 줄여준다.

애플리케이션과 실행 환경을 이미지로 묶어두기 때문이다.

```text
board-api 이미지
 ├─ 실행에 필요한 환경
 ├─ 빌드된 애플리케이션 파일
 ├─ 포트 정보
 └─ 실행 명령어
```

그래서 다른 서버에서는 이미지를 받아서 실행만 하면 된다.

```bash
docker pull ubuntu12341/board-api:1.0
docker run -p 8080:8080 ubuntu12341/board-api:1.0
```

---

# 3. Docker Compose로 여러 컨테이너 실행하기

FE, API, DB를 각각 따로 실행할 수도 있지만, 매번 명령어를 여러 개 치는 것은 번거롭다.

그래서 `docker-compose.yml`을 사용한다.

```yaml
services:
  db:
    image: postgres:16-alpine
    container_name: db
    environment:
      POSTGRES_DB: boarddb
      POSTGRES_USER: board
      POSTGRES_PASSWORD: board1234
    ports:
      - "5432:5432"

  api:
    image: local/board-api:latest
    container_name: api
    ports:
      - "8080:8080"
    depends_on:
      - db
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://db:5432/boarddb
      SPRING_DATASOURCE_USERNAME: board
      SPRING_DATASOURCE_PASSWORD: board1234

  fe:
    image: local/board-fe:latest
    container_name: fe
    ports:
      - "8081:8081"
    depends_on:
      - api
```

여기서 중요한 부분은 DB 연결 주소다.

```yaml
SPRING_DATASOURCE_URL: jdbc:postgresql://db:5432/boarddb
```

처음에는 `localhost`를 쓰기 쉽다.

하지만 컨테이너 내부에서 `localhost`는 자기 자신을 의미한다.

즉 API 컨테이너 안에서 `localhost`는 API 컨테이너 자기 자신이다.

DB 컨테이너를 바라보려면 서비스 이름인 `db`를 써야 한다.

```text
잘못된 예:
jdbc:postgresql://localhost:5432/boarddb

올바른 예:
jdbc:postgresql://db:5432/boarddb
```

Docker Compose 내부에서는 서비스 이름이 네트워크 주소처럼 사용된다.

---

# 4. 컨테이너 실행

`docker-compose.yml`이 있는 위치에서 다음 명령어를 실행한다.

```bash
docker compose up -d
```

또는 이미지 빌드까지 함께 해야 한다면 다음 명령어를 사용한다.

```bash
docker compose up --build -d
```

실행 후 Docker Desktop을 확인하면 다음 컨테이너들이 떠야 한다.

```text
db
api
fe
```

Docker Desktop에서 확인한 결과:

```text
db   → postgres:16-alpine
api  → local/board-api:latest
fe   → local/board-fe:latest
```

이렇게 표시되면 FE, API, DB가 모두 컨테이너로 실행 중인 상태다.

---

# 5. 실행 확인

FE는 브라우저에서 확인한다.

```text
http://localhost:8081
```

API는 다음 주소로 확인할 수 있다.

```text
http://localhost:8080
```

예를 들어 게시글 API가 `/boards`라면 다음처럼 접근한다.

```text
http://localhost:8080/boards
```

DB에 실제로 데이터가 들어갔는지 확인하려면 PostgreSQL 컨테이너에 접속한다.

```bash
docker exec -it db psql -U board -d boarddb
```

접속 후 테이블 목록을 확인한다.

```sql
\dt
```

게시글 테이블을 조회한다.

```sql
SELECT * FROM board;
```

브라우저에서 글을 등록한 뒤 `SELECT` 결과에 행이 늘어나면 FE → API → DB 흐름이 정상적으로 연결된 것이다.

---

# 6. Docker Hub에 이미지를 올리는 이유

Docker Hub는 Docker 이미지를 저장하는 원격 저장소다.

GitHub가 소스코드를 저장하는 곳이라면, Docker Hub는 실행 가능한 이미지를 저장하는 곳이라고 보면 된다.

```text
소스코드 → GitHub
Docker 이미지 → Docker Hub
```

로컬에서 만든 이미지는 내 컴퓨터에만 존재한다.

```text
내 노트북
 └─ local/board-api:latest
```

하지만 다른 서버나 다른 컴퓨터에서는 이 이미지를 알 수 없다.

그래서 Docker Hub에 이미지를 push한다.

```text
내 노트북
  └─ docker push
        ↓
Docker Hub
        ↓
다른 서버 / 다른 PC / Kubernetes
  └─ docker pull
```

이렇게 해두면 다른 환경에서도 같은 이미지를 받아 실행할 수 있다.

---

# 7. Docker Hub 로그인

먼저 Docker Hub에 로그인한다.

```bash
docker login
```

기존에 로그인되어 있다면 다음처럼 표시될 수 있다.

```text
Authenticating with existing credentials... [Username: ubuntu12341]
```

이 경우 현재 Docker Hub 계정은 `ubuntu12341`이다.

따라서 이미지를 올릴 때는 이미지 이름 앞에 `ubuntu12341`을 붙인다.

---

# 8. 로컬 이미지 확인

현재 로컬에 있는 이미지를 확인한다.

```bash
docker images
```

이번 경우에는 Docker Desktop에서 다음 이미지들이 확인되었다.

```text
postgres:16-alpine
local/board-api:latest
local/board-fe:latest
```

여기서 올릴 대상은 내가 직접 만든 FE/API 이미지다.

```text
올릴 이미지:
local/board-api:latest
local/board-fe:latest
```

DB 이미지는 공식 PostgreSQL 이미지이므로 따로 올리지 않는다.

```text
올리지 않는 이미지:
postgres:16-alpine
```

---

# 9. 왜 DB 이미지는 안 올리는가

DB는 보통 직접 만든 이미지가 아니라 공식 이미지를 사용한다.

이번 프로젝트의 DB는 다음 이미지다.

```text
postgres:16-alpine
```

이 이미지는 이미 Docker Hub에 존재하는 공식 이미지다.

다른 서버에서도 그냥 다음 명령어로 받을 수 있다.

```bash
docker pull postgres:16-alpine
```

따라서 내가 따로 `ubuntu12341/postgres` 같은 이미지를 만들어서 올릴 필요가 없다.

또 하나 중요한 점은 DB 이미지와 DB 데이터는 다르다는 것이다.

```text
DB 이미지 = PostgreSQL 프로그램
DB 데이터 = 실제 게시글 데이터
```

Docker Hub에는 보통 애플리케이션 실행 이미지를 올린다.

실제 DB 데이터는 Docker Hub에 올리는 대상이 아니다.

DB 데이터는 보통 다음 방식으로 관리한다.

```text
1. Docker volume
2. DB dump 백업
3. RDS 같은 관리형 DB
4. 별도 데이터베이스 서버
```

이번 과제에서는 FE/API 이미지만 Docker Hub에 올리면 된다.

---

# 10. Docker Hub용 태그 붙이기

Docker Hub에 push하려면 이미지 이름이 다음 형식이어야 한다.

```text
도커허브아이디/이미지이름:태그
```

이번 Docker Hub 계정은 `ubuntu12341`이다.

로컬 이미지에 Docker Hub용 이름을 붙인다.

```bash
docker tag local/board-api:latest ubuntu12341/board-api:1.0
docker tag local/board-fe:latest ubuntu12341/board-fe:1.0
```

명령어 구조는 다음과 같다.

```bash
docker tag 현재이미지명:현재태그 도커허브아이디/올릴이미지명:올릴태그
```

즉 이번 명령어는 다음 의미다.

```text
local/board-api:latest
→ ubuntu12341/board-api:1.0

local/board-fe:latest
→ ubuntu12341/board-fe:1.0
```

---

# 11. 태그 확인

태그가 잘 붙었는지 확인한다.

```bash
docker images
```

정상이라면 다음 이미지들이 보인다.

```text
local/board-api          latest
local/board-fe           latest
ubuntu12341/board-api    1.0
ubuntu12341/board-fe     1.0
postgres                 16-alpine
```

여기서 `local/board-api:latest`와 `ubuntu12341/board-api:1.0`은 서로 다른 이미지처럼 보이지만, 실제로는 같은 이미지에 이름표를 하나 더 붙인 것이다.

Docker Hub에 올릴 때는 `ubuntu12341/board-api:1.0` 이름을 사용한다.

---

# 12. Docker Hub에 push

이제 이미지를 Docker Hub에 올린다.

```bash
docker push ubuntu12341/board-api:1.0
docker push ubuntu12341/board-fe:1.0
```

push가 성공하면 Docker Hub의 Repositories 화면에 다음 두 개가 생긴다.

```text
ubuntu12341/board-api
ubuntu12341/board-fe
```

Docker Hub 화면에서도 다음처럼 확인할 수 있다.

```text
board-fe    Last pushed less than a minute ago
board-api   Last pushed less than a minute ago
```

이렇게 보이면 push 성공이다.

---

# 13. 다른 서버에서 이미지 가져오기

이제 다른 서버나 다른 PC에서는 다음 명령어로 이미지를 받을 수 있다.

```bash
docker pull ubuntu12341/board-api:1.0
docker pull ubuntu12341/board-fe:1.0
```

받은 뒤 실행할 수도 있다.

```bash
docker run -p 8080:8080 ubuntu12341/board-api:1.0
docker run -p 8081:8081 ubuntu12341/board-fe:1.0
```

하지만 실제로는 FE, API, DB를 함께 실행해야 하므로 `docker-compose.yml`을 사용하는 것이 더 좋다.

---

# 14. Docker Hub 이미지 기반 docker-compose.yml

로컬에서 직접 빌드하는 방식은 다음과 같다.

```yaml
api:
  build: ./board_api
```

이 방식은 현재 컴퓨터에 소스코드가 있어야 한다.

반면 Docker Hub 이미지를 사용하는 방식은 다음과 같다.

```yaml
api:
  image: ubuntu12341/board-api:1.0
```

이 방식은 소스코드가 없어도 된다.

Docker Hub에서 이미지를 받아 실행하기 때문이다.

최종적으로 다른 서버에서 사용할 수 있는 compose 파일은 다음과 같이 구성할 수 있다.

```yaml
services:
  db:
    image: postgres:16-alpine
    container_name: db
    environment:
      POSTGRES_DB: boarddb
      POSTGRES_USER: board
      POSTGRES_PASSWORD: board1234
    ports:
      - "5432:5432"

  api:
    image: ubuntu12341/board-api:1.0
    container_name: api
    ports:
      - "8080:8080"
    depends_on:
      - db
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://db:5432/boarddb
      SPRING_DATASOURCE_USERNAME: board
      SPRING_DATASOURCE_PASSWORD: board1234

  fe:
    image: ubuntu12341/board-fe:1.0
    container_name: fe
    ports:
      - "8081:8081"
    depends_on:
      - api
```

이제 이 파일만 있으면 다른 환경에서도 다음 명령어로 실행할 수 있다.

```bash
docker compose up -d
```

---

# 15. 최종 명령어 정리

이번에 사용한 핵심 명령어는 다음과 같다.

## 컨테이너 실행

```bash
docker compose up -d
```

또는 빌드까지 함께 실행:

```bash
docker compose up --build -d
```

## 현재 컨테이너 확인

```bash
docker ps
```

전체 컨테이너 확인:

```bash
docker ps -a
```

## 이미지 확인

```bash
docker images
```

## Docker Hub 로그인

```bash
docker login
```

## Docker Hub용 태그 생성

```bash
docker tag local/board-api:latest ubuntu12341/board-api:1.0
docker tag local/board-fe:latest ubuntu12341/board-fe:1.0
```

## Docker Hub에 push

```bash
docker push ubuntu12341/board-api:1.0
docker push ubuntu12341/board-fe:1.0
```

## 다른 환경에서 pull

```bash
docker pull ubuntu12341/board-api:1.0
docker pull ubuntu12341/board-fe:1.0
```

---

# 16. 이번 작업의 의미

이번 작업은 단순히 Docker 명령어 몇 개를 친 것이 아니다.

로컬에서 실행하던 애플리케이션을 컨테이너 단위로 분리했고, Docker Compose로 여러 서비스를 함께 실행했으며, 직접 만든 이미지를 Docker Hub에 올렸다.

즉 다음 흐름을 한 번 경험한 것이다.

```text
소스코드 작성
→ 애플리케이션 빌드
→ Docker 이미지 생성
→ Docker Compose로 컨테이너 실행
→ FE / API / DB 통신 확인
→ Docker Hub에 이미지 push
→ 다른 환경에서 pull 가능
```

실무 배포 흐름으로 보면 다음 단계의 기초를 한 것이다.

```text
Dockerizing
→ Image Registry
→ Remote Server Deploy
→ Kubernetes Deploy
```

이번에는 로컬 노트북에서 실행했지만, Docker Hub에 이미지를 올렸기 때문에 이제 다른 서버에서도 같은 이미지를 받아 실행할 수 있다.

---

# 17. 한 줄 정리

이번 작업은 **로컬에서만 돌아가던 게시판 프로젝트를 FE/API/DB 컨테이너 구조로 분리하고, 직접 만든 FE/API 이미지를 Docker Hub에 올려 어디서든 실행 가능한 형태로 만든 과정**이다.
