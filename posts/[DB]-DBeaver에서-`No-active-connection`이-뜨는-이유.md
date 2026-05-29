---
title: "[DB] DBeaver에서 `No active connection`이 뜨는 이유"
source: "https://velog.io/@yorange50/DB-DBeaver에서-No-active-connection이-뜨는-이유"
published: "2026-05-13T04:25:32.852Z"
tags: ""
backup_date: "2026-05-29T14:52:52.751029"
---

![](https://velog.velcdn.com/images/yorange50/post/36fb77a2-32f1-4acc-8b56-e8242c6656d2/image.png)


Docker Compose로 PostgreSQL 컨테이너를 띄우고 DBeaver에서 SQL을 실행하려고 했는데, 갑자기 이런 오류가 나왔다.

```text
Cannot obtain session
No active connection
```

처음에는 PostgreSQL 컨테이너가 죽은 줄 알았다. 그런데 터미널에서 확인해보면 컨테이너는 정상적으로 실행 중이었다.

```bash
docker ps
```

결과는 이런 상태였다.

```text
CONTAINER ID   IMAGE         STATUS          PORTS                    NAMES
5e8124fca11c   postgres:16   Up 26 minutes   0.0.0.0:5432->5432/tcp   hello-postgres
```

즉, PostgreSQL 서버 자체는 살아 있다. 문제는 Docker나 PostgreSQL이 아니라, DBeaver의 SQL Editor가 현재 어떤 DB 연결을 사용해야 하는지 모르는 상태였던 것이다.

---

## 1. 현재 상황

DBeaver 화면에서 SQL을 실행하려고 했는데 아래와 같은 팝업이 떴다.

```text
Cannot obtain session
No active connection
```

그리고 SQL Editor 상단을 보면 연결 정보가 이렇게 표시되어 있었다.

```text
<N/A>
```

이게 핵심이다.

`<N/A>`는 현재 SQL 창이 어떤 데이터베이스 연결에도 붙어 있지 않다는 뜻이다.

즉, SQL 문은 작성되어 있지만 DBeaver 입장에서는 이런 상태다.

```text
이 SQL을 어디 DB에 실행해야 하지?
```

그래서 `CREATE TABLE`, `INSERT`, `SELECT`를 실행하려고 해도 세션을 얻을 수 없다고 나온다.

---

## 2. Docker 컨테이너 문제인지 먼저 확인하기

DBeaver에서 연결 문제가 생기면 가장 먼저 PostgreSQL 컨테이너가 살아 있는지 확인해야 한다.

```bash
docker ps
```

여기서 PostgreSQL 컨테이너가 보여야 한다.

```text
postgres:16
0.0.0.0:5432->5432/tcp
hello-postgres
```

이렇게 나오면 컨테이너는 정상 실행 중이다.

특히 이 부분이 중요하다.

```text
0.0.0.0:5432->5432/tcp
```

이 뜻은 내 노트북의 5432 포트가 컨테이너 내부의 5432 포트로 연결되어 있다는 의미다.

즉, DBeaver에서 아래 정보로 접속할 수 있는 상태다.

```text
Host: localhost
Port: 5432
```

컨테이너가 살아 있는데 DBeaver에서 `No active connection`이 뜬다면, 대부분은 SQL Editor가 DB 연결을 잃어버렸거나 연결을 선택하지 않은 상태다.

---

## 3. DBeaver의 SQL Editor는 그냥 SQL 파일일 수도 있다

DBeaver에서 SQL 창을 열었다고 해서 무조건 DB와 연결된 것은 아니다.

SQL Script 창은 단순히 텍스트 편집기처럼 열릴 수 있다. 하지만 SQL을 실행하려면 반드시 실행 대상 DB가 필요하다.

예를 들어 아래 SQL이 있다고 하자.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50)
);

INSERT INTO users (name) VALUES ('kim');
INSERT INTO users (name) VALUES ('lee');

SELECT * FROM users;
```

이 SQL은 문법적으로는 문제가 없다. 하지만 DBeaver가 어느 DB에 이 SQL을 보낼지 모르면 실행할 수 없다.

그래서 SQL Editor 상단에 `<N/A>`가 떠 있으면 실행이 안 된다.

```text
SQL은 있음
DB 연결은 없음
그래서 실행 불가
```

---

## 4. 해결 방법 1: 기존 연결을 다시 연결하기

왼쪽 Database Navigator에서 PostgreSQL 연결을 찾는다.

보통 이런 식으로 보인다.

```text
postgres localhost:5432
```

또는

```text
postgres 2 localhost:5432
```

이 연결을 우클릭한 뒤 아래 메뉴를 선택한다.

```text
Connect
```

또는

```text
Reconnect
```

또는

```text
Invalidate/Reconnect
```

DBeaver 버전에 따라 메뉴 이름은 조금 다를 수 있다.

연결이 정상적으로 되면 왼쪽 트리가 펼쳐진다.

```text
postgres
└── Databases
    └── postgres
        └── Schemas
            └── public
                └── Tables
```

여기까지 보이면 DBeaver와 PostgreSQL 연결은 살아 있는 상태다.

---

## 5. 해결 방법 2: SQL Editor에 연결 지정하기

SQL Editor 상단에 `<N/A>`라고 표시된 부분이 있다.

이 부분을 클릭해서 실행할 DB 연결을 선택해야 한다.

선택지는 보통 이런 식으로 나온다.

```text
postgres
postgres 2
localhost:5432 / postgres
```

여기서 현재 PostgreSQL 연결을 선택한다.

선택 후 상단 표시가 `<N/A>`가 아니라 아래처럼 바뀌어야 한다.

```text
<postgres>
```

또는

```text
postgres
```

이 상태가 되어야 SQL 실행이 가능하다.

---

## 6. 가장 쉬운 해결 방법: 연결에서 새 SQL Editor 열기

기존 SQL 창이 꼬였을 때는 새 SQL Editor를 여는 것이 가장 깔끔하다.

왼쪽 Database Navigator에서 PostgreSQL 연결을 우클릭한다.

```text
postgres localhost:5432
```

그리고 아래 메뉴를 선택한다.

```text
SQL Editor
```

또는

```text
Open SQL Console
```

이렇게 열면 새 SQL 창은 해당 DB 연결을 자동으로 물고 열린다.

그 상태에서 SQL을 실행하면 된다.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50)
);

INSERT INTO users (name) VALUES ('kim');
INSERT INTO users (name) VALUES ('lee');

SELECT * FROM users;
```

실행 후 결과가 나오면 성공이다.

---

## 7. 테이블이 안 보일 때는 Refresh 해야 한다

SQL로 테이블을 만든 뒤에도 DBeaver 왼쪽 트리에 바로 안 보일 수 있다.

예를 들어 테이블을 만들었다.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50)
);
```

그런데 왼쪽에서 여전히 `No items`처럼 보일 수 있다.

이건 DBeaver 화면이 아직 새로고침되지 않았기 때문이다.

왼쪽에서 아래 경로로 이동한다.

```text
Databases
└── postgres
    └── Schemas
        └── public
            └── Tables
```

`Tables`를 우클릭하고 `Refresh`를 누른다.

그러면 `users` 테이블이 나타난다.

---

## 8. `No items`와 `No active connection`은 다르다

DBeaver를 쓰다 보면 비슷하게 헷갈리는 상태가 있다.

### `No items`

```text
No items
```

이건 현재 보고 있는 위치에 객체가 없다는 뜻이다.

예를 들어 `public > Tables`에 들어갔는데 `No items`가 뜬다면, 현재 DB의 public 스키마에 테이블이 없다는 뜻이다.

이 경우는 연결 문제가 아니다.

```text
DB 연결은 됨
근데 테이블이 없음
```

해결 방법은 테이블을 생성하거나, 테이블을 만든 뒤 Refresh 하는 것이다.

---

### `No active connection`

```text
No active connection
```

이건 SQL Editor가 DB 연결을 가지고 있지 않다는 뜻이다.

이 경우는 테이블이 있든 없든 SQL 실행 자체가 안 된다.

```text
SQL 창은 열림
근데 연결된 DB가 없음
```

해결 방법은 연결을 다시 잡거나, 연결에서 새 SQL Editor를 여는 것이다.

---

## 9. 현재 상황 정리

이번 상황은 PostgreSQL 컨테이너는 정상적으로 실행 중이었다.

```bash
docker ps
```

결과에서 다음이 확인되었다.

```text
postgres:16
Up 26 minutes
0.0.0.0:5432->5432/tcp
```

따라서 Docker 컨테이너가 죽은 문제가 아니었다.

진짜 문제는 DBeaver의 SQL Editor가 연결을 잃은 상태였다.

화면 상단에 `<N/A>`가 떠 있었고, SQL 실행 시 다음 오류가 발생했다.

```text
Cannot obtain session
No active connection
```

즉, 해결 방향은 PostgreSQL을 다시 설치하거나 컨테이너를 다시 만드는 것이 아니라, DBeaver에서 연결을 다시 선택하는 것이다.

---

## 10. 최종 해결 순서

문제가 생겼을 때는 이 순서대로 확인하면 된다.

```bash
docker ps
```

PostgreSQL 컨테이너가 살아 있는지 확인한다.

```text
0.0.0.0:5432->5432/tcp
```

포트 매핑이 되어 있는지 확인한다.

DBeaver 왼쪽에서 PostgreSQL 연결을 우클릭한다.

```text
Reconnect
```

또는

```text
Invalidate/Reconnect
```

를 누른다.

SQL Editor 상단에서 `<N/A>`가 아닌 실제 연결을 선택한다.

```text
postgres
```

또는 새로 SQL Editor를 연다.

```text
PostgreSQL 연결 우클릭
→ SQL Editor
→ Open SQL Console
```

그 다음 SQL을 실행한다.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50)
);

INSERT INTO users (name) VALUES ('kim');
INSERT INTO users (name) VALUES ('lee');

SELECT * FROM users;
```

마지막으로 왼쪽 `Tables`를 우클릭해서 Refresh 한다.

---

## 11. 핵심 정리

DBeaver에서 `No active connection`이 뜬다고 해서 PostgreSQL 컨테이너가 무조건 죽은 것은 아니다.

이번 경우처럼 Docker 컨테이너는 정상적으로 살아 있는데, DBeaver의 SQL Editor만 연결을 잃은 상태일 수 있다.

핵심은 이 차이다.

```text
docker ps에서 postgres 컨테이너가 보인다
→ PostgreSQL 서버는 살아 있음
```

```text
DBeaver SQL Editor 상단에 <N/A>가 보인다
→ SQL 창이 DB 연결을 못 잡음
```

```text
public > Tables에서 No items가 보인다
→ 연결은 됐지만 테이블이 아직 없음
```

결국 정리하면 다음과 같다.

```text
No items
= 테이블이 없음

No active connection
= SQL Editor가 DB 연결을 안 물고 있음
```

DBeaver에서 SQL을 실행하려면 SQL 문법뿐만 아니라 “어느 DB 연결로 실행할지”도 반드시 잡혀 있어야 한다. Docker로 DB를 띄운 뒤 DBeaver에서 작업할 때는 컨테이너 상태, 포트 매핑, DBeaver 연결 상태, SQL Editor의 활성 연결을 순서대로 확인하면 된다.
