---
title: "[DB] DBeaver로 PostgreSQL 접속하고 테이블 만들어보기\n"
source: "https://velog.io/@yorange50/DB-DBeaver로-PostgreSQL-접속하고-테이블-만들어보기"
published: "2026-05-13T04:11:36.859Z"
tags: ""
backup_date: "2026-05-29T14:52:52.751326"
---

![](https://velog.velcdn.com/images/yorange50/post/add3e436-1ff5-49fd-95fb-1512a69da137/image.png)

처음 데이터베이스를 공부할 때 제일 막히는 지점은 보통 SQL 문법이 아니다.
오히려 “DB에 어떻게 접속하지?”, “테이블은 어디서 보지?”, “내가 실행한 SQL 결과는 어디에 남지?” 같은 도구 사용법에서 많이 막힌다.

이번 글에서는 PostgreSQL을 Docker로 띄워둔 상태에서 DBeaver로 접속하고, 테이블 생성, 데이터 삽입, 조회까지 해보는 흐름을 정리한다.

---

## 1. DBeaver란?

DBeaver는 데이터베이스를 GUI로 다룰 수 있게 해주는 클라이언트 도구다.

쉽게 말하면 데이터베이스용 VSCode나 Postman 같은 느낌이다.

PostgreSQL, MySQL, MariaDB, Oracle, SQLite 같은 여러 DB에 접속할 수 있고, SQL을 직접 작성해서 실행하거나 테이블 구조를 눈으로 확인할 수 있다.

CLI에서는 이런 식으로 접속한다.

```bash
psql -h localhost -p 5432 -U postgres
```

DBeaver를 쓰면 이 접속 정보를 화면에 입력해서 연결할 수 있다.

---

## 2. 현재 화면 상태 보기

올려준 화면을 보면 DBeaver가 PostgreSQL에 정상적으로 연결된 상태다.

왼쪽 Database Navigator에 다음과 같이 보인다.

```text
localhost:5432
└── postgres
    └── Databases
        └── postgres
```

이 말은 로컬 컴퓨터의 5432 포트에 있는 PostgreSQL 서버에 접속했고, 그 안의 `postgres` 데이터베이스를 보고 있다는 뜻이다.

여기서 헷갈리기 쉬운 점이 있다.

```text
postgres 서버
postgres 데이터베이스
postgres 사용자
```

이 셋이 이름이 같을 수 있다.
초기 설정에서 전부 `postgres`로 많이 쓰기 때문에 처음 보면 헷갈린다.

대충 이렇게 보면 된다.

```text
localhost:5432       → PostgreSQL 서버 주소
postgres 사용자      → DB에 로그인하는 계정
postgres 데이터베이스 → 실제 테이블을 만들 공간
public 스키마        → 테이블들이 들어가는 기본 폴더
```

---

## 3. DBeaver 화면 구조

DBeaver에서 자주 보는 영역은 크게 3개다.

```text
왼쪽 Database Navigator
→ DB 서버, 데이터베이스, 스키마, 테이블 목록 확인

가운데 SQL Editor
→ SQL 작성하고 실행하는 곳

아래쪽 Result 탭
→ SELECT 결과나 실행 결과 확인
```

지금 화면에서는 아직 테이블을 펼치지 않은 상태라서 `Databases > postgres`까지만 보인다.

테이블을 보려면 보통 아래 경로로 들어간다.

```text
postgres
└── Databases
    └── postgres
        └── Schemas
            └── public
                └── Tables
```

여기서 `public`은 PostgreSQL의 기본 스키마다.
처음에는 그냥 “테이블이 들어가는 기본 폴더”라고 이해하면 된다.

---

## 4. SQL Editor 열기

SQL을 작성하려면 상단의 `SQL` 버튼을 누르거나, 왼쪽의 데이터베이스를 우클릭해서 SQL Editor를 열면 된다.

현재 화면 아래쪽을 보면 `Script.sql`이 있다.
이미 SQL 스크립트 파일이 열린 상태다.

여기에 SQL을 작성하고 실행하면 된다.

예를 들어 게시판 테이블을 하나 만들어보자.

```sql
CREATE TABLE board (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    content TEXT,
    writer VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

이 SQL의 의미는 다음과 같다.

```text
CREATE TABLE board
→ board라는 테이블 생성

id SERIAL PRIMARY KEY
→ 자동 증가하는 기본키

title VARCHAR(100) NOT NULL
→ 최대 100글자의 제목, 비어 있으면 안 됨

content TEXT
→ 긴 본문 저장

writer VARCHAR(50)
→ 작성자 이름 저장

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
→ 생성 시간을 자동으로 저장
```

---

## 5. SQL 실행하기

SQL을 작성한 뒤 실행하려면 보통 다음 중 하나를 사용한다.

```text
Ctrl + Enter
→ 현재 커서가 있는 SQL 실행

Command + Enter
→ Mac에서 실행 단축키로 동작하는 경우가 많음

상단의 실행 버튼
→ 재생 버튼처럼 생긴 아이콘
```

DBeaver에서는 SQL 끝에 세미콜론을 붙이는 것이 좋다.

```sql
SELECT * FROM board;
```

여러 SQL을 한 파일에 적을 때 세미콜론이 있어야 어디까지가 한 문장인지 구분하기 쉽다.

---

## 6. 데이터 넣기

테이블을 만들었으면 데이터를 넣어본다.

```sql
INSERT INTO board (title, content, writer)
VALUES ('첫 번째 글', 'DBeaver로 PostgreSQL에 데이터를 넣어보는 중입니다.', 'seoyeon');
```

여러 개를 한 번에 넣을 수도 있다.

```sql
INSERT INTO board (title, content, writer)
VALUES 
('두 번째 글', 'Docker Compose로 PostgreSQL을 띄웠습니다.', 'seoyeon'),
('세 번째 글', 'DBeaver에서 테이블을 확인합니다.', 'seoyeon');
```

여기서 `id`와 `created_at`은 직접 넣지 않았다.

왜냐하면 테이블 만들 때 이렇게 설정했기 때문이다.

```sql
id SERIAL
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

즉, `id`는 자동 증가하고, `created_at`은 현재 시간이 자동으로 들어간다.

---

## 7. 데이터 조회하기

데이터가 잘 들어갔는지 확인하려면 `SELECT`를 사용한다.

```sql
SELECT * FROM board;
```

그러면 아래쪽 Result 창에 테이블 형태로 결과가 나온다.

특정 컬럼만 보고 싶으면 이렇게 한다.

```sql
SELECT id, title, writer, created_at
FROM board;
```

최신 글부터 보고 싶으면 정렬을 추가한다.

```sql
SELECT *
FROM board
ORDER BY id DESC;
```

---

## 8. 왼쪽 목록에 테이블이 안 보일 때

SQL로 테이블을 만들었는데 왼쪽 목록에 바로 안 보일 수 있다.

이럴 때는 새로고침을 해야 한다.

왼쪽 Database Navigator에서 다음 위치를 찾는다.

```text
postgres
└── Databases
    └── postgres
        └── Schemas
            └── public
                └── Tables
```

그리고 `Tables`나 `public`에서 우클릭 후 `Refresh`를 누른다.

그러면 방금 만든 `board` 테이블이 보일 것이다.

DBeaver는 DB 상태를 항상 실시간으로 자동 반영하지 않는다.
그래서 SQL로 뭔가 만들었으면 새로고침을 해줘야 하는 경우가 많다.

---

## 9. 테이블 데이터 GUI로 보기

왼쪽에서 테이블을 찾은 뒤 더블클릭하면 테이블 정보를 볼 수 있다.

보통 이런 탭들이 나온다.

```text
Properties
Data
ER Diagram
DDL
```

자주 보는 건 `Data`와 `DDL`이다.

```text
Data
→ 실제 들어있는 데이터 확인

DDL
→ 이 테이블을 만들 때 사용된 CREATE TABLE 문 확인
```

DDL은 테이블 구조를 다시 볼 때 유용하다.

예를 들어 `board` 테이블의 DDL을 보면 대략 이런 구조가 나온다.

```sql
CREATE TABLE public.board (
    id serial4 NOT NULL,
    title varchar(100) NOT NULL,
    content text NULL,
    writer varchar(50) NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT board_pkey PRIMARY KEY (id)
);
```

---

## 10. 데이터 수정하기

SQL로 데이터를 수정할 수도 있다.

```sql
UPDATE board
SET title = '수정된 제목'
WHERE id = 1;
```

주의할 점은 `WHERE`를 꼭 써야 한다는 것이다.

만약 이렇게 쓰면 위험하다.

```sql
UPDATE board
SET title = '수정된 제목';
```

이렇게 하면 모든 행의 제목이 바뀐다.

삭제도 마찬가지다.

```sql
DELETE FROM board
WHERE id = 1;
```

`WHERE` 없는 DELETE는 전체 삭제가 된다.

```sql
DELETE FROM board;
```

그래서 실무에서는 UPDATE, DELETE를 할 때 항상 먼저 SELECT로 대상을 확인하는 습관이 좋다.

```sql
SELECT *
FROM board
WHERE id = 1;
```

확인한 다음에 수정하거나 삭제한다.

---

## 11. Docker Compose와 같이 쓸 때 중요한 점

이번 과제에서 중요한 포인트는 Docker Compose를 내렸다 올려도 데이터가 남아야 한다는 것이다.

PostgreSQL 컨테이너만 만들고 볼륨을 안 붙이면 문제가 생긴다.

```bash
docker compose down
docker compose up -d
```

이렇게 했을 때 데이터가 사라질 수 있다.

그래서 `docker-compose.yml`에 volume을 붙여야 한다.

예시는 다음과 같다.

```yaml
services:
  postgres:
    image: postgres:16
    container_name: postgres-db
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```

핵심은 이 부분이다.

```yaml
volumes:
  - postgres-data:/var/lib/postgresql/data
```

PostgreSQL의 실제 데이터 저장 위치는 컨테이너 안의 `/var/lib/postgresql/data`다.
이 위치를 Docker volume에 연결해두면 컨테이너를 지웠다 다시 만들어도 데이터가 남는다.

---

## 12. DBeaver 접속 정보 정리

Docker Compose를 위처럼 구성했다면 DBeaver에서는 보통 이렇게 접속한다.

```text
Host: localhost
Port: 5432
Database: postgres
Username: postgres
Password: postgres
```

정리하면 다음과 같다.

| 항목       | 값         |
| -------- | --------- |
| Host     | localhost |
| Port     | 5432      |
| Database | postgres  |
| User     | postgres  |
| Password | postgres  |

DBeaver에서 PostgreSQL 연결을 새로 만들 때 이 정보를 입력하면 된다.

---

## 13. 테스트 시나리오

과제 흐름으로 보면 이렇게 하면 된다.

### 1단계. Docker Compose 실행

```bash
docker compose up -d
```

### 2단계. DBeaver 접속

```text
localhost:5432
postgres / postgres
```

### 3단계. 테이블 생성

```sql
CREATE TABLE board (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    content TEXT,
    writer VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4단계. 데이터 삽입

```sql
INSERT INTO board (title, content, writer)
VALUES ('첫 번째 글', 'Docker PostgreSQL 테스트입니다.', 'seoyeon');
```

### 5단계. 조회

```sql
SELECT * FROM board;
```

### 6단계. Compose 내리기

```bash
docker compose down
```

### 7단계. 다시 올리기

```bash
docker compose up -d
```

### 8단계. DBeaver에서 다시 조회

```sql
SELECT * FROM board;
```

데이터가 그대로 보이면 volume 설정이 제대로 된 것이다.

---

## 14. 자주 하는 실수

### 1. 포트가 다름

Docker Compose에서 이렇게 되어 있으면

```yaml
ports:
  - "5433:5432"
```

DBeaver에서는 5432가 아니라 5433으로 접속해야 한다.

```text
Host: localhost
Port: 5433
```

왼쪽은 내 컴퓨터 포트, 오른쪽은 컨테이너 내부 포트다.

```text
5433:5432
내 컴퓨터 포트 : 컨테이너 포트
```

---

### 2. 테이블이 안 보임

SQL 실행 후 왼쪽 목록에 테이블이 안 보이면 Refresh를 누른다.

```text
Schemas > public > Tables > Refresh
```

---

### 3. 다른 데이터베이스에 접속함

PostgreSQL 서버 안에는 여러 데이터베이스가 있을 수 있다.

내가 테이블을 만든 곳이 `postgres` 데이터베이스인지, 다른 데이터베이스인지 확인해야 한다.

현재 화면에서는 `public@postgres`라고 보이므로 `postgres` 데이터베이스의 `public` 스키마를 보고 있는 상태다.

---

### 4. docker compose down -v 사용

주의해야 할 명령어가 있다.

```bash
docker compose down -v
```

여기서 `-v`는 volume까지 삭제한다는 뜻이다.

즉, 데이터 보존 테스트를 할 때는 이걸 쓰면 안 된다.

```bash
docker compose down
```

이렇게만 내려야 volume이 남는다.

---

## 15. 전체 SQL 예제

마지막으로 DBeaver에서 그대로 실행해볼 수 있는 SQL을 정리하면 다음과 같다.

```sql
CREATE TABLE board (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    content TEXT,
    writer VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO board (title, content, writer)
VALUES
('첫 번째 글', 'DBeaver에서 PostgreSQL을 테스트합니다.', 'seoyeon'),
('두 번째 글', 'Docker Compose volume을 확인합니다.', 'seoyeon'),
('세 번째 글', '컨테이너를 내려도 데이터가 남아야 합니다.', 'seoyeon');

SELECT *
FROM board
ORDER BY id DESC;
```

이미 `board` 테이블이 있다면 `CREATE TABLE`에서 에러가 날 수 있다.
그럴 때는 테스트용으로 지우고 다시 만들 수도 있다.

```sql
DROP TABLE IF EXISTS board;

CREATE TABLE board (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    content TEXT,
    writer VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 마무리

DBeaver는 데이터베이스를 눈으로 확인하면서 SQL을 실행할 수 있게 해주는 도구다.
PostgreSQL을 Docker로 띄웠다면 DBeaver에서는 `localhost`, `5432`, `postgres` 계정 정보로 접속하면 된다.

처음에는 다음 흐름만 익히면 충분하다.

```text
Docker Compose로 PostgreSQL 실행
→ DBeaver로 localhost:5432 접속
→ SQL Editor 열기
→ CREATE TABLE 실행
→ INSERT 실행
→ SELECT로 조회
→ docker compose down/up
→ 데이터가 남아있는지 확인
```

이번 과제의 핵심은 단순히 PostgreSQL을 띄우는 것이 아니라, 컨테이너가 내려갔다 올라와도 데이터가 유지되는지 확인하는 것이다.
그래서 DBeaver는 단순 조회 도구가 아니라, 내가 만든 DB 구조와 데이터가 실제로 살아있는지 검증하는 도구로 쓰면 된다.
