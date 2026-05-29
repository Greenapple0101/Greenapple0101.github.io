---
title: "[DB] 터미널에서는 테이블이 보이는데 DBeaver에서는 `No items`가 뜨는 이유"
source: "https://velog.io/@yorange50/DB-터미널에서는-테이블이-보이는데-DBeaver에서는-No-items가-뜨는-이유"
published: "2026-05-13T04:35:35.037Z"
tags: ""
backup_date: "2026-05-29T14:52:52.750649"
---

![](https://velog.velcdn.com/images/yorange50/post/e66b1eb5-0740-430d-8719-e6509f57e637/image.png)


Docker로 PostgreSQL을 띄우고 터미널에서 `psql`로 접속했을 때는 테이블이 잘 보였다.

```bash id="khvy4s"
docker exec -it hello-postgres psql -U hellouser -d hellodb
```

그리고 SQL을 실행하면 데이터도 정상적으로 조회됐다.

```sql id="utuxv9"
SELECT * FROM users;
```

결과도 잘 나왔다.

```text id="z94o9p"
 id | name
----+------
  1 | kim
  2 | lee
```

그런데 DBeaver에서는 계속 `No items`가 보였다.

처음에는 DBeaver가 이상한 줄 알았다. 또는 Docker volume이 안 먹은 줄 알았다. 하지만 실제 원인은 단순했다.

> 터미널과 DBeaver가 서로 다른 데이터베이스를 보고 있었다.

---

## 1. 터미널은 어느 DB를 보고 있었나?

터미널에서 실행한 명령어를 보면 답이 나온다.

```bash id="oiiyji"
docker exec -it hello-postgres psql -U hellouser -d hellodb
```

여기서 중요한 부분은 두 개다.

```bash id="buj6ow"
-U hellouser
-d hellodb
```

`-U`는 PostgreSQL 사용자 이름이다.

```text id="9678v5"
-U hellouser
```

즉, `hellouser`라는 사용자로 접속했다는 뜻이다.

`-d`는 접속할 데이터베이스 이름이다.

```text id="5qfkr6"
-d hellodb
```

즉, `hellodb`라는 데이터베이스에 접속했다는 뜻이다.

정리하면 터미널에서는 다음 상태였다.

```text id="jd27rl"
사용자: hellouser
데이터베이스: hellodb
```

그래서 `SELECT * FROM users;`를 실행했을 때 `hellodb` 안에 있는 `users` 테이블이 조회된 것이다.

---

## 2. DBeaver는 어느 DB를 보고 있었나?

DBeaver 화면을 보면 왼쪽 트리에 이런 구조가 보였다.

```text id="8gvf5c"
Databases
└── postgres
    └── Schemas
        └── public
            └── Tables
```

즉, DBeaver는 현재 `hellodb`가 아니라 `postgres` 데이터베이스를 보고 있었다.

DBeaver 상단에도 이런 식으로 표시되어 있었다.

```text id="7lh3qt"
public@postgres
```

이 말은 현재 보고 있는 스키마가 `postgres` 데이터베이스의 `public` 스키마라는 뜻이다.

그래서 `Tables`를 눌렀을 때 `No items`가 나온 것이다.

테이블이 없는 게 아니라, 내가 테이블을 만든 DB와 DBeaver가 보고 있는 DB가 달랐던 것이다.

---

## 3. PostgreSQL 서버와 데이터베이스는 다르다

여기서 중요한 개념이 하나 있다.

PostgreSQL 서버 하나 안에는 여러 데이터베이스가 있을 수 있다.

예를 들면 이런 구조다.

```text id="o7kije"
PostgreSQL 서버
├── postgres DB
│   └── public schema
│       └── Tables 없음
│
└── hellodb DB
    └── public schema
        └── users 테이블 있음
```

`localhost:5432`는 PostgreSQL 서버 주소다.

하지만 서버에 접속한다고 해서 모든 DB를 한 번에 보는 것은 아니다. PostgreSQL에서는 특정 데이터베이스 하나를 선택해서 접속한다.

터미널에서는 `hellodb`를 선택했다.

```bash id="w7sq5f"
-d hellodb
```

DBeaver에서는 `postgres`를 보고 있었다.

```text id="q3atsy"
Databases > postgres
```

그래서 서로 결과가 달랐다.

---

## 4. 같은 서버인데 왜 결과가 다를까?

두 화면은 같은 PostgreSQL 서버를 바라보고 있었다.

```text id="gkq9nu"
localhost:5432
```

하지만 접속한 데이터베이스가 달랐다.

```text id="30ccyr"
터미널: localhost:5432 / hellodb
DBeaver: localhost:5432 / postgres
```

그래서 터미널에서는 `users` 테이블이 보이고, DBeaver에서는 보이지 않았다.

이건 Docker volume 문제도 아니고, PostgreSQL 데이터가 날아간 것도 아니다.

그냥 조회하고 있는 위치가 다른 것이다.

비유하면 같은 건물에 들어갔지만 서로 다른 방을 보고 있는 상황이다.

```text id="l6ynsh"
PostgreSQL 서버 = 건물
Database = 방
Table = 방 안에 있는 물건
```

터미널은 `hellodb`라는 방에 들어갔다.

DBeaver는 `postgres`라는 방을 보고 있었다.

그래서 `hellodb` 방에 있는 `users` 테이블이 DBeaver의 `postgres` 방에서는 안 보였던 것이다.

---

## 5. 해결 방법: DBeaver 연결 DB를 `hellodb`로 바꾸기

해결 방법은 DBeaver에서 접속 데이터베이스를 `hellodb`로 바꾸는 것이다.

왼쪽 Database Navigator에서 PostgreSQL 연결을 우클릭한다.

```text id="x174mk"
postgres localhost:5432
```

그리고 아래 메뉴로 들어간다.

```text id="6pp5fg"
Edit Connection
```

접속 정보를 다음처럼 맞춘다.

```text id="xgvsoy"
Host: localhost
Port: 5432
Database: hellodb
Username: hellouser
Password: docker-compose.yml에 적은 비밀번호
```

여기서 가장 중요한 것은 `Database` 값이다.

기존에는 아마 이렇게 되어 있었을 가능성이 크다.

```text id="x295e5"
Database: postgres
```

이걸 다음처럼 바꿔야 한다.

```text id="mxxpx3"
Database: hellodb
```

그 다음 `Test Connection`을 눌러 연결이 성공하는지 확인한다.

성공하면 저장하고 다시 연결한다.

---

## 6. DBeaver에서 정상적으로 보여야 하는 구조

연결을 `hellodb`로 바꾸면 DBeaver에서는 다음 구조를 봐야 한다.

```text id="qk3u75"
Databases
└── hellodb
    └── Schemas
        └── public
            └── Tables
                └── users
```

만약 바로 보이지 않으면 `Tables`를 우클릭해서 `Refresh`를 누르면 된다.

```text id="sggizv"
public
└── Tables
    └── Refresh
```

DBeaver는 화면 정보를 캐싱하고 있을 수 있어서, SQL로 테이블을 만든 직후에는 새로고침이 필요할 수 있다.

---

## 7. 현재 연결된 DB 확인하기

헷갈릴 때는 SQL로 현재 접속한 DB를 확인하면 된다.

DBeaver나 `psql`에서 아래 SQL을 실행한다.

```sql id="l3rd69"
SELECT current_database();
```

결과가 이렇게 나오면 `postgres` DB를 보고 있는 것이다.

```text id="cog7s6"
postgres
```

결과가 이렇게 나와야 이번 실습 데이터와 맞다.

```text id="0fnqzi"
hellodb
```

현재 사용자도 확인할 수 있다.

```sql id="mnu0ke"
SELECT current_user;
```

결과가 다음처럼 나오면 `hellouser`로 접속 중인 것이다.

```text id="ce6bf3"
hellouser
```

즉, 확인용 SQL은 이렇게 두 개만 기억해도 좋다.

```sql id="c7lh4s"
SELECT current_database();
SELECT current_user;
```

---

## 8. Docker Compose 설정과 연결 정보 맞추기

Docker Compose에서 PostgreSQL을 띄울 때 보통 이런 환경변수를 설정한다.

```yaml id="dxz03s"
services:
  postgres:
    image: postgres:16
    container_name: hello-postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: hellouser
      POSTGRES_PASSWORD: hellopass
      POSTGRES_DB: hellodb
```

이 설정의 의미는 다음과 같다.

```text id="6knq5x"
POSTGRES_USER=hellouser
→ 기본 사용자 생성

POSTGRES_PASSWORD=hellopass
→ 해당 사용자의 비밀번호

POSTGRES_DB=hellodb
→ 기본 데이터베이스 생성
```

그러면 DBeaver 연결 정보도 이 값과 맞춰야 한다.

```text id="lwhenu"
Host: localhost
Port: 5432
Database: hellodb
Username: hellouser
Password: hellopass
```

터미널에서도 동일하게 접속해야 한다.

```bash id="0fd9j5"
docker exec -it hello-postgres psql -U hellouser -d hellodb
```

이렇게 터미널과 DBeaver가 같은 DB를 보고 있어야 결과가 일치한다.

---

## 9. `postgres` DB는 뭐고 `hellodb`는 뭘까?

PostgreSQL을 처음 보면 `postgres`라는 데이터베이스가 기본으로 보인다.

`postgres`는 PostgreSQL에서 기본적으로 자주 존재하는 관리용 또는 기본 접속용 데이터베이스라고 보면 된다.

반면 `hellodb`는 내가 Docker Compose에서 만든 애플리케이션용 데이터베이스다.

```yaml id="79io3d"
POSTGRES_DB: hellodb
```

Spring Boot 앱이나 실습용 테이블은 보통 이 `hellodb`에 만든다.

그래서 테이블을 만들 때도, DBeaver로 볼 때도, Spring Boot에서 연결할 때도 같은 DB 이름을 사용해야 한다.

```text id="68on1x"
터미널 psql: hellodb
DBeaver: hellodb
Spring Boot application.properties: hellodb
```

이 세 개가 맞아야 헷갈리지 않는다.

---

## 10. Spring Boot 설정도 같은 DB를 봐야 한다

만약 Spring Boot 앱에서도 이 PostgreSQL을 사용한다면 `application.properties` 또는 `application.yml`도 같은 DB를 바라봐야 한다.

예를 들어 `application.properties`라면 다음처럼 설정한다.

```properties id="xm3tl6"
spring.datasource.url=jdbc:postgresql://localhost:5432/hellodb
spring.datasource.username=hellouser
spring.datasource.password=hellopass
spring.datasource.driver-class-name=org.postgresql.Driver
```

여기서 중요한 부분은 URL의 마지막이다.

```properties id="cm2pxr"
jdbc:postgresql://localhost:5432/hellodb
```

이건 Spring Boot가 `localhost:5432`의 PostgreSQL 서버 안에 있는 `hellodb` 데이터베이스에 접속한다는 뜻이다.

만약 여기를 실수로 이렇게 쓰면

```properties id="cv6mh7"
jdbc:postgresql://localhost:5432/postgres
```

Spring Boot는 `hellodb`가 아니라 `postgres` DB를 보게 된다.

그러면 DBeaver, 터미널, Spring Boot가 서로 다른 DB를 보면서 계속 헷갈릴 수 있다.

---

## 11. 문제 상황 정리

이번 문제는 이렇게 정리할 수 있다.

터미널에서는 다음 명령어로 접속했다.

```bash id="ju3kfi"
docker exec -it hello-postgres psql -U hellouser -d hellodb
```

그래서 터미널은 `hellodb`를 보고 있었다.

```text id="23z1wo"
hellodb
└── public
    └── users
```

DBeaver에서는 왼쪽 트리에서 `postgres` DB를 보고 있었다.

```text id="ias9hv"
postgres
└── public
    └── Tables
        └── No items
```

따라서 둘의 결과가 달랐다.

정확한 구조는 이렇다.

```text id="ok760o"
PostgreSQL 서버 localhost:5432
├── postgres DB
│   └── public schema
│       └── 테이블 없음
│
└── hellodb DB
    └── public schema
        └── users 테이블 있음
```

---

## 12. 최종 정리

DBeaver에서 `No items`가 뜬다고 해서 데이터가 사라진 것은 아니다.

먼저 내가 어느 데이터베이스를 보고 있는지 확인해야 한다.

터미널에서 아래처럼 접속했다면

```bash id="l9j6if"
psql -U hellouser -d hellodb
```

DBeaver도 반드시 같은 데이터베이스를 봐야 한다.

```text id="t0kkbs"
Database: hellodb
Username: hellouser
```

헷갈릴 때는 이 SQL을 실행한다.

```sql id="toc70u"
SELECT current_database();
SELECT current_user;
```

그리고 결과를 확인한다.

```text id="zz0cc8"
current_database = hellodb
current_user = hellouser
```

결국 핵심은 이거다.

```text id="ljkzn1"
PostgreSQL 서버는 하나여도,
그 안의 데이터베이스는 여러 개일 수 있다.

터미널과 DBeaver가 같은 서버에 붙어 있어도,
서로 다른 데이터베이스를 보고 있으면 결과가 다르게 나온다.
```

이번 경우에는 터미널은 `hellodb`를 보고 있었고, DBeaver는 `postgres`를 보고 있었다. 그래서 터미널에서는 `users` 테이블이 보였지만, DBeaver에서는 `No items`가 떴던 것이다.
