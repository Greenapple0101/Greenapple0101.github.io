---
title: "[DB] PostgreSQL에서 스키마가 `hello`랑 `public` 두 개 보이는 이유"
source: "https://velog.io/@yorange50/DB-PostgreSQL에서-스키마가-hello랑-public-두-개-보이는-이유"
published: "2026-05-13T04:38:37.173Z"
tags: ""
backup_date: "2026-05-29T14:52:52.749401"
---

![](https://velog.velcdn.com/images/yorange50/post/01404878-9a94-45ac-a55d-cd34602097bc/image.png)

![](https://velog.velcdn.com/images/yorange50/post/08bb43df-fdc7-4d2c-96c4-3215322576e8/image.png)


PostgreSQL을 Docker로 띄우고 DBeaver에서 확인하다 보면 이런 구조를 볼 수 있다.

```text
hellodb
└── Schemas
    ├── hello
    └── public
```

처음 보면 헷갈린다.

> 왜 스키마가 두 개지?
> public은 뭐고 hello는 뭐지?
> 테이블은 어디에 만들어지는 거지?

결론부터 말하면 이상한 상황이 아니다.

`public`은 PostgreSQL이 기본으로 가지고 있는 스키마이고, `hello`는 내가 직접 만든 스키마다.

---

## 1. PostgreSQL 구조 먼저 보기

PostgreSQL은 대충 이런 구조로 생각하면 된다.

```text
PostgreSQL 서버
└── Database
    └── Schema
        └── Table
```

예를 들어 지금 상황은 이런 느낌이다.

```text
PostgreSQL 서버
└── hellodb
    └── Schemas
        ├── public
        │   └── tables
        │
        └── hello
            └── tables
```

즉, `hellodb`라는 데이터베이스 안에 `public` 스키마와 `hello` 스키마가 같이 존재하는 것이다.

---

## 2. `public` 스키마는 기본 스키마다

PostgreSQL에서 데이터베이스를 만들면 기본적으로 `public` 스키마가 존재한다.

```text
hellodb
└── public
```

`public`은 말 그대로 기본 작업 공간 같은 역할을 한다.

내가 따로 스키마를 지정하지 않고 테이블을 만들면 보통 `public` 스키마에 테이블이 생성된다.

예를 들어 아래처럼 테이블을 만들었다고 하자.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50)
);
```

이 SQL에는 스키마 이름이 없다.

```sql
CREATE TABLE users
```

그러면 PostgreSQL은 현재 설정된 `search_path`를 보고 어디에 만들지 결정한다. 일반적인 기본 설정에서는 `public.users`로 만들어진다.

```text
hellodb
└── public
    └── users
```

그래서 DBeaver에서 보면 이런 위치에 보인다.

```text
Databases
└── hellodb
    └── Schemas
        └── public
            └── Tables
                └── users
```

---

## 3. `hello` 스키마는 직접 만든 스키마다

반면 `hello` 스키마는 PostgreSQL이 기본으로 만든 것이 아니다.

보통 이런 SQL을 실행했을 때 생긴다.

```sql
CREATE SCHEMA IF NOT EXISTS hello;
```

이 SQL의 뜻은 다음과 같다.

```text
hello라는 스키마가 없으면 만들어라.
이미 있으면 넘어가라.
```

이걸 실행하면 데이터베이스 안에 `hello`라는 스키마가 하나 추가된다.

```text
hellodb
├── public
└── hello
```

즉, `hello`는 내가 앱 전용 공간으로 따로 만든 스키마라고 보면 된다.

---

## 4. 스키마는 DB 안의 폴더 같은 개념이다

스키마는 쉽게 말하면 데이터베이스 안에서 테이블을 분류하는 폴더 같은 개념이다.

예를 들어 모든 테이블을 `public`에 넣으면 이렇게 된다.

```text
hellodb
└── public
    ├── users
    ├── posts
    ├── comments
    ├── app_config
    └── greetings
```

작은 실습에서는 괜찮다.

하지만 앱이 커지거나 여러 기능이 섞이면 테이블이 많아진다. 이때 스키마를 나누면 정리하기 좋다.

```text
hellodb
├── public
│   └── 기본 공간
│
└── hello
    ├── app_config
    └── greetings
```

이렇게 하면 `hello-world` 앱에서 사용하는 테이블을 `hello` 스키마에 따로 모아둘 수 있다.

---

## 5. 내가 실행한 SQL 때문에 `hello` 스키마가 생겼을 가능성

만약 예전에 이런 SQL을 실행했다면 `hello` 스키마가 생긴다.

```sql
CREATE SCHEMA IF NOT EXISTS hello;

SET search_path TO hello, public;
```

첫 번째 줄은 `hello` 스키마를 만든다.

```sql
CREATE SCHEMA IF NOT EXISTS hello;
```

두 번째 줄은 PostgreSQL이 테이블을 찾거나 만들 때 참고하는 순서를 정한다.

```sql
SET search_path TO hello, public;
```

이 설정은 이렇게 해석하면 된다.

```text
테이블 이름만 쓰면 먼저 hello 스키마에서 찾고,
없으면 public 스키마에서 찾아라.
```

---

## 6. `search_path`가 뭐지?

PostgreSQL에서 테이블을 조회할 때 보통 이렇게 쓴다.

```sql
SELECT * FROM users;
```

그런데 사실 테이블의 정확한 이름은 스키마까지 포함하면 이런 형태다.

```sql
SELECT * FROM public.users;
```

또는

```sql
SELECT * FROM hello.users;
```

그럼 `SELECT * FROM users;`처럼 스키마 이름을 생략하면 PostgreSQL은 어떻게 찾을까?

이때 사용하는 것이 `search_path`다.

현재 `search_path`가 이렇게 되어 있다고 해보자.

```sql
SET search_path TO hello, public;
```

그러면 PostgreSQL은 `users`를 찾을 때 이런 순서로 찾는다.

```text
1. hello.users 찾기
2. 없으면 public.users 찾기
```

즉, `search_path`는 스키마를 생략했을 때 PostgreSQL이 탐색하는 순서다.

---

## 7. 테이블이 어느 스키마에 있는지 확인하는 법

헷갈릴 때는 직접 SQL로 확인하면 된다.

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_name = 'users';
```

결과가 이렇게 나오면 `users`는 `public` 스키마에 있는 것이다.

```text
table_schema | table_name
-------------+-----------
public       | users
```

결과가 이렇게 나오면 `users`는 `hello` 스키마에 있는 것이다.

```text
table_schema | table_name
-------------+-----------
hello        | users
```

전체 테이블 목록을 보고 싶으면 이렇게 확인할 수 있다.

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name;
```

이 SQL은 시스템 테이블을 제외하고 내가 만든 테이블 위주로 보여준다.

---

## 8. 스키마를 명시해서 조회하면 헷갈리지 않는다

스키마가 여러 개 있을 때는 테이블 이름 앞에 스키마 이름을 붙이면 가장 확실하다.

`public` 스키마의 `users`를 조회하려면 이렇게 쓴다.

```sql
SELECT * FROM public.users;
```

`hello` 스키마의 `users`를 조회하려면 이렇게 쓴다.

```sql
SELECT * FROM hello.users;
```

만약 두 스키마에 같은 이름의 테이블이 있어도 스키마를 명시하면 정확히 조회할 수 있다.

```text
hellodb
├── public
│   └── users
│
└── hello
    └── users
```

이런 구조에서도 아래 두 SQL은 서로 다른 테이블을 조회한다.

```sql
SELECT * FROM public.users;
```

```sql
SELECT * FROM hello.users;
```

---

## 9. 그럼 실습에서는 `public`을 써도 될까?

단순 실습이면 `public`만 써도 된다.

예를 들어 Docker로 PostgreSQL 연결 확인하고, DBeaver로 테이블 생성하고, Spring Boot에서 DB 연결하는 정도라면 `public` 스키마만 써도 충분하다.

```text
hellodb
└── public
    └── users
```

이게 가장 단순하다.

하지만 앱 전용 테이블을 구분하고 싶다면 `hello` 같은 스키마를 만들어도 된다.

```text
hellodb
└── hello
    ├── app_config
    └── greetings
```

실무에서는 서비스별, 도메인별, 모듈별로 스키마를 나누기도 한다.

```text
appdb
├── user_service
├── order_service
├── payment_service
└── public
```

이렇게 나누면 테이블을 관리하기 편해진다.

---

## 10. Spring Boot에서는 어떤 스키마를 볼까?

Spring Boot가 PostgreSQL에 연결할 때도 결국 특정 데이터베이스에 접속한다.

예를 들어:

```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/hellodb
spring.datasource.username=hellouser
spring.datasource.password=hellopass
```

이 설정은 `hellodb` 데이터베이스에 접속한다는 뜻이다.

하지만 이 설정만으로는 `hello` 스키마를 쓸지, `public` 스키마를 쓸지 명확하지 않을 수 있다.

JPA를 사용한다면 기본 스키마를 지정할 수도 있다.

```properties
spring.jpa.properties.hibernate.default_schema=hello
```

이렇게 하면 Hibernate가 기본적으로 `hello` 스키마를 사용하게 할 수 있다.

반대로 단순 실습이고 스키마 구분이 필요 없다면 이 설정 없이 `public`을 사용해도 된다.

---

## 11. 현재 상황 정리

현재 DBeaver에서 스키마가 두 개 보이는 이유는 다음과 같다.

```text
public
= PostgreSQL 데이터베이스에 기본으로 있는 스키마

hello
= 내가 직접 CREATE SCHEMA로 만든 스키마
```

구조로 보면 이렇게 된다.

```text
hellodb
├── public
│   └── 기본 스키마
│
└── hello
    └── 앱 전용으로 만든 스키마
```

두 개가 같이 보이는 것은 오류가 아니다. PostgreSQL에서는 하나의 데이터베이스 안에 여러 스키마를 둘 수 있다.

---

## 12. 최종 정리

PostgreSQL에서 스키마는 데이터베이스 안에서 테이블을 분리하는 공간이다.

`public`은 기본 스키마다. 내가 아무것도 설정하지 않고 테이블을 만들면 보통 `public`에 만들어진다.

`hello`는 내가 직접 만든 스키마다.

```sql
CREATE SCHEMA IF NOT EXISTS hello;
```

이 SQL을 실행했기 때문에 `hello` 스키마가 생긴 것이다.

그리고 `SET search_path TO hello, public;`을 사용하면 PostgreSQL은 테이블 이름만 적었을 때 먼저 `hello`에서 찾고, 없으면 `public`에서 찾는다.

헷갈릴 때는 이 SQL로 확인하면 된다.

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name;
```

핵심은 이거다.

```text
Database는 큰 방
Schema는 그 안의 구역
Table은 구역 안에 있는 실제 데이터 저장소
```

따라서 `hello`와 `public`이 같이 보이는 건 문제가 아니라, 하나의 데이터베이스 안에 기본 스키마와 내가 만든 스키마가 함께 존재하는 정상적인 상태다.
