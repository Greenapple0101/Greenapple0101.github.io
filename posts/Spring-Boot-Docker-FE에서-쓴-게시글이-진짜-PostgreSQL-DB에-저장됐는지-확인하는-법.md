---
title: "[Spring Boot + Docker] FE에서 쓴 게시글이 진짜 PostgreSQL DB에 저장됐는지 확인하는 법"
source: "https://velog.io/@yorange50/Spring-Boot-Docker-FE에서-쓴-게시글이-진짜-PostgreSQL-DB에-저장됐는지-확인하는-법"
published: "2026-05-06T05:05:21.393Z"
tags: ""
backup_date: "2026-05-29T14:52:52.775376"
---

![](https://velog.velcdn.com/images/yorange50/post/05648411-fc81-440e-947d-aea5bfc7e904/image.png)

게시판 프로젝트를 다음 구조로 분리했다.

```text
Browser
→ board_fe
→ RestClient
→ board_api
→ JPA
→ Docker PostgreSQL
```

`board_fe`에서 글쓰기 화면을 만들고, `board_api`는 JPA를 통해 PostgreSQL에 저장하도록 구성했다.

그런데 여기서 자연스럽게 드는 의문이 있다.

```text
내가 화면에서 게시글을 등록했는데,
이게 진짜 Docker로 띄운 PostgreSQL DB에 쌓인 걸까?
```

브라우저에서 목록이 보인다고 해서 무조건 DB에 저장됐다고 단정할 수는 없다.
정확히 확인하려면 **PostgreSQL DB에 직접 들어가서 SELECT 해보는 것**이 가장 확실하다.

---

## 1. 현재 구조

현재 게시판 프로젝트는 대략 이런 구조다.

```text
board_fe
→ Spring Boot + Thymeleaf
→ 사용자가 보는 화면 담당

board_api
→ Spring Boot REST API
→ JPA
→ PostgreSQL 저장 담당

PostgreSQL
→ Docker 컨테이너로 로컬 실행
```

즉 사용자가 브라우저에서 글을 등록하면 흐름은 이렇게 간다.

```text
브라우저에서 글 작성
→ board_fe의 form submit
→ board_fe Controller
→ BoardApiClient
→ RestClient
→ board_api의 POST /boards
→ BoardService
→ BoardRepository
→ PostgreSQL
```

그래서 최종적으로 확인해야 하는 곳은 `board_fe`가 아니라 **PostgreSQL DB**다.

---

## 2. Docker PostgreSQL 컨테이너 확인

먼저 PostgreSQL 컨테이너가 떠 있는지 확인한다.

```powershell
docker ps
```

컨테이너가 정상 실행 중이면 이런 식으로 보인다.

```text
CONTAINER ID   IMAGE         PORTS                    NAMES
xxxxxxx        postgres:16   0.0.0.0:5432->5432/tcp   board-postgres
```

여기서 중요한 부분은 이거다.

```text
NAMES = board-postgres
PORTS = 5432:5432
```

즉 내 로컬 PC의 `5432` 포트가 Docker 컨테이너 내부의 PostgreSQL `5432` 포트와 연결되어 있다는 뜻이다.

---

## 3. psql로 Docker PostgreSQL에 직접 접속하기

가장 확실한 확인 방법은 Docker 컨테이너 안의 PostgreSQL에 직접 접속하는 것이다.

컨테이너 이름이 `board-postgres`이고, DB 설정이 다음과 같다고 하자.

```text
DB 이름: boarddb
유저: board
비밀번호: board1234
```

그러면 PowerShell에서 다음 명령어를 실행한다.

```powershell
docker exec -it board-postgres psql -U board -d boarddb
```

명령어를 나눠서 보면 이렇다.

```text
docker exec
→ 실행 중인 컨테이너 안에서 명령어 실행

-it
→ 터미널처럼 직접 입력 가능하게 접속

board-postgres
→ 접속할 컨테이너 이름

psql
→ PostgreSQL CLI 도구

-U board
→ board 유저로 접속

-d boarddb
→ boarddb 데이터베이스에 접속
```

성공하면 이런 프롬프트가 나온다.

```text
boarddb=#
```

이 상태가 되면 PostgreSQL 안에 직접 들어온 것이다.

---

## 4. 테이블 목록 확인하기

PostgreSQL에 접속했으면 먼저 테이블 목록을 확인한다.

```sql
\dt
```

JPA Entity 이름이 `Board`라면 보통 테이블 이름은 `board`로 생성된다.

예상 결과는 이런 느낌이다.

```text
          List of relations
 Schema | Name  | Type  | Owner
--------+-------+-------+-------
 public | board | table | board
```

만약 `board`가 안 보이면 테이블 이름이 다르게 만들어졌을 수도 있다.

예를 들어 엔티티에 `@Table(name = "boards")`를 붙였다면 테이블 이름은 `boards`일 수 있다.

```java
@Entity
@Table(name = "boards")
public class Board {
}
```

이 경우에는 조회할 때도 `boards`를 봐야 한다.

```sql
SELECT * FROM boards;
```

---

## 5. 게시글 데이터 조회하기

테이블 이름이 `board`라면 다음 SQL을 실행한다.

```sql
SELECT * FROM board;
```

처음에는 아무 데이터가 없을 수 있다.

```text
 id | title | content | author
----+-------+---------+--------
(0 rows)
```

이 상태에서 브라우저로 가서 글을 하나 등록한다.

```text
http://localhost:8081/boards/write
```

예를 들어 이렇게 입력한다.

```text
제목: 테스트 제목
작성자: test
내용: Docker PostgreSQL 저장 확인
```

등록 후 다시 PostgreSQL 터미널에서 조회한다.

```sql
SELECT * FROM board;
```

그러면 이런 식으로 데이터가 보여야 한다.

```text
 id |   title    |          content           | author
----+------------+----------------------------+--------
  1 | 테스트 제목 | Docker PostgreSQL 저장 확인 | test
```

이렇게 행이 하나 늘어났다면 성공이다.

```text
FE에서 작성한 게시글이
board_api를 거쳐
Docker PostgreSQL에 실제로 저장된 것
```

---

## 6. 저장 여부 확인 흐름

정리하면 검증 순서는 이렇다.

```text
1. Docker PostgreSQL 컨테이너 실행 확인
2. board_api 실행
3. board_fe 실행
4. board_fe에서 게시글 등록
5. docker exec로 PostgreSQL 접속
6. SELECT * FROM board;
7. 등록한 데이터가 보이면 성공
```

명령어만 다시 정리하면 다음과 같다.

```powershell
docker ps
```

```powershell
docker exec -it board-postgres psql -U board -d boarddb
```

```sql
\dt
```

```sql
SELECT * FROM board;
```

---

## 7. board_api 로그로 간접 확인하기

DB에 직접 들어가는 방법이 가장 확실하지만, `board_api` 로그로도 어느 정도 확인할 수 있다.

`application.properties`에 다음 설정이 있으면:

```properties
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
```

게시글을 저장할 때 콘솔에 SQL이 찍힌다.

예를 들어 저장 요청이 들어오면 이런 로그가 나올 수 있다.

```sql
insert into board
    (author, content, title)
values
    (?, ?, ?)
```

이 로그가 찍힌다는 것은 JPA가 실제로 insert SQL을 만들었다는 뜻이다.

하지만 로그만으로는 최종 저장 결과를 완전히 확인했다고 보긴 어렵다.
그래서 최종 확인은 DB에 직접 들어가서 `SELECT` 하는 것이 가장 안전하다.

```text
로그 확인
→ insert SQL이 실행된 흐름 확인

DB SELECT
→ 실제 데이터 저장 여부 확인
```

---

## 8. DBeaver나 pgAdmin으로 확인하는 방법

CLI가 불편하면 DBeaver나 pgAdmin 같은 DB 툴을 사용해도 된다.

접속 정보는 Docker 실행할 때 설정한 값과 동일하다.

```text
Host: localhost
Port: 5432
Database: boarddb
Username: board
Password: board1234
```

접속 후 `board` 테이블을 열어보면 된다.

또는 SQL Editor에서 직접 실행한다.

```sql
SELECT * FROM board;
```

DBeaver를 쓰면 브라우저나 터미널보다 더 눈으로 보기 편하다.

---

## 9. application.properties도 확인해야 한다

중요한 점은 `board_api`가 진짜 Docker PostgreSQL을 바라보고 있어야 한다는 것이다.

`board_api/src/main/resources/application.properties`가 다음처럼 되어 있어야 한다.

```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/boarddb
spring.datasource.username=board
spring.datasource.password=board1234
```

그리고 Docker 컨테이너도 다음처럼 떠 있어야 한다.

```text
0.0.0.0:5432->5432/tcp
```

즉 연결 관계는 다음과 같다.

```text
board_api
→ jdbc:postgresql://localhost:5432/boarddb
→ Docker port mapping 5432:5432
→ board-postgres container
→ PostgreSQL boarddb
```

이 상태에서 `SELECT * FROM board;`에 데이터가 보이면,
그 데이터는 Docker 로컬 PostgreSQL에 저장된 것이 맞다.

---

## 10. 주의할 점

### 1. `/boards` 화면에 보인다고 무조건 DB 저장은 아니다

화면에 보이는 데이터가 실제 DB에서 온 것인지 확인하려면 흐름을 봐야 한다.

```text
board_fe
→ RestClient
→ board_api
→ JPA
→ PostgreSQL
```

이 구조가 제대로 연결되어 있고, DB에서 SELECT까지 된다면 확실하다.

---

### 2. 테이블 이름이 다를 수 있다

보통 `Board` 엔티티는 `board` 테이블로 만들어진다.

하지만 설정에 따라 이름이 달라질 수 있다.

그래서 바로 `SELECT * FROM board;`가 안 되면 먼저 테이블 목록을 확인한다.

```sql
\dt
```

목록에 나온 실제 테이블 이름으로 조회하면 된다.

---

### 3. 컨테이너를 삭제하면 데이터가 사라질 수 있다

PostgreSQL 컨테이너를 만들 때 볼륨을 안 붙였다면, 컨테이너 삭제 시 데이터가 사라질 수 있다.

개발용으로도 데이터를 유지하고 싶으면 볼륨을 붙여 실행하는 것이 좋다.

```powershell
docker run --name board-postgres `
  -e POSTGRES_USER=board `
  -e POSTGRES_PASSWORD=board1234 `
  -e POSTGRES_DB=boarddb `
  -p 5432:5432 `
  -v board-postgres-data:/var/lib/postgresql/data `
  -d postgres:16
```

중요한 부분은 이거다.

```powershell
-v board-postgres-data:/var/lib/postgresql/data
```

이렇게 하면 컨테이너를 지웠다가 다시 만들어도 데이터를 유지하기 쉬워진다.

---

## 11. 최종 정리

FE에서 등록한 게시글이 Docker PostgreSQL에 진짜 저장됐는지 확인하려면, 브라우저 화면만 보지 말고 DB에 직접 들어가서 조회해야 한다.

가장 확실한 방법은 다음이다.

```powershell
docker exec -it board-postgres psql -U board -d boarddb
```

접속 후:

```sql
\dt
SELECT * FROM board;
```

글을 하나 등록한 뒤 `SELECT` 결과에 행이 늘어나면 성공이다.

```text
board_fe에서 게시글 등록
→ RestClient로 board_api 호출
→ board_api가 JPA Repository로 save
→ PostgreSQL board 테이블에 insert
→ SELECT로 데이터 확인
```

한 줄로 정리하면 이렇다.

```text
쌓였는지는 브라우저가 아니라 PostgreSQL에 직접 접속해서 SELECT 해보면 가장 확실하다.
```
