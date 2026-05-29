---
title: "[SPRING] ddl-auto: validate에서 init.sql을 직접 만들며 DB 스키마를 맞춘 이야기"
source: "https://velog.io/@yorange50/SPRING-ddl-auto-validate에서-init.sql을-직접-만들며-DB-스키마를-맞춘-이야기"
published: "2026-05-17T10:02:47.545Z"
tags: ""
backup_date: "2026-05-29T14:52:52.736213"
---

Spring Boot 애플리케이션을 EC2에 배포하다가 부팅이 실패한 적이 있다. 처음에는 단순히 MySQL 연결 문제라고 생각했다. DB 주소가 잘못됐는지, 계정 정보가 틀렸는지, 포트가 막혔는지부터 확인했다. 그런데 실제 원인은 DB 연결 자체가 아니라 **애플리케이션이 기대하는 테이블이 MySQL 안에 존재하지 않았다는 것**이었다. 더 정확히는 JPA 설정이 `ddl-auto: validate`였고, 테이블 구조는 노션에만 남아 있었으며, 실행 가능한 정식 DDL이나 `schema.sql`은 따로 정리되어 있지 않은 상태였다. 그래서 노션에 남아 있던 테이블 명세를 기준으로 `init.sql`을 직접 만들고 수정하면서 DB 스키마를 맞춰야 했다.

## 문제 상황

Spring Boot 애플리케이션 설정에는 다음과 같은 값이 들어 있었다.

```yaml id="4giyrf"
spring:
  jpa:
    hibernate:
      ddl-auto: validate
```

이 설정을 둔 상태에서 애플리케이션을 실행했다.

```bash id="l8mjkn"
java -jar app.jar
```

그런데 애플리케이션이 정상적으로 뜨지 않았다. MySQL은 실행 중이었고, DB 접속 정보도 어느 정도 맞는 것처럼 보였다. 그런데 Spring Boot가 부팅되는 과정에서 Hibernate validation 단계에서 실패했다.

원인은 간단했다.

```text id="h5d5of"
Entity는 테이블이 있다고 기대함
하지만 MySQL에는 해당 테이블이 없음
ddl-auto는 validate
따라서 테이블을 자동 생성하지 않음
결과적으로 부팅 실패
```

즉, DB 서버가 죽어 있던 게 아니라 **DB 초기화 상태가 애플리케이션 설정의 전제와 맞지 않았던 것**이다.

## ddl-auto: validate는 테이블을 만들어주지 않는다

Spring Boot와 JPA를 사용할 때 `ddl-auto` 설정은 Hibernate가 DB 스키마를 어떻게 다룰지 결정한다.

개발할 때는 종종 이런 설정을 사용한다.

```yaml id="7dmmi2"
spring:
  jpa:
    hibernate:
      ddl-auto: update
```

`update`는 Entity를 기준으로 DB 스키마를 어느 정도 자동으로 맞춰준다. 개발 초기에는 편하다. 테이블이 없으면 만들어주고, 컬럼이 부족하면 추가해주기도 한다.

하지만 `validate`는 다르다.

```yaml id="cy5zne"
spring:
  jpa:
    hibernate:
      ddl-auto: validate
```

`validate`는 DB를 만들거나 수정하지 않는다.
오직 Entity와 실제 DB 테이블 구조가 맞는지만 검사한다.

즉, 의미는 이렇다.

```text id="32majz"
“테이블은 이미 만들어져 있다고 가정할게.
나는 Entity와 DB 테이블이 일치하는지만 확인할게.”
```

그래서 `ddl-auto: validate`를 쓰려면 반드시 애플리케이션 실행 전에 DB 테이블이 먼저 만들어져 있어야 한다.

## 테이블 명세는 노션에만 있었다

당시 문제는 테이블 구조가 아예 없었던 것은 아니었다.
노션에는 테이블 명세가 남아 있었다.

예를 들면 이런 식이다.

```text id="tt241p"
user
- id
- email
- password
- nickname
- created_at

board
- id
- title
- content
- user_id
- created_at
```

사람이 보기에는 충분히 테이블 구조가 있는 것처럼 보인다.
하지만 MySQL은 노션 문서를 읽고 테이블을 만들어주지 않는다.

실제로 DB에 테이블을 만들려면 실행 가능한 SQL이 필요하다.

```sql id="r2fy67"
CREATE TABLE user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    created_at DATETIME
);
```

즉, 문제는 이렇게 정리할 수 있다.

```text id="ge7o0e"
설계 문서:
노션에 존재

실행 가능한 DDL:
없음

DB 상태:
테이블 미생성

JPA 설정:
validate

결과:
부팅 실패
```

테이블 명세와 DDL은 다르다.
노션 명세는 사람이 이해하기 위한 문서이고, DDL은 DB가 실행할 수 있는 코드다.

## init.sql을 직접 만들기 시작했다

정식으로 제공된 `schema.sql`이나 DDL 파일이 없었기 때문에, 노션의 테이블 명세를 보고 직접 `init.sql`을 만들었다.

처음에는 아마 이런 식으로 단순하게 시작했을 수 있다.

```sql id="8sxopm"
CREATE TABLE user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    created_at DATETIME
);

CREATE TABLE board (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    user_id BIGINT,
    created_at DATETIME
);
```

하지만 한 번에 맞지는 않는다.

Entity에는 있는데 SQL에는 없는 컬럼이 있을 수 있고, 타입이 다를 수도 있고, 테이블명이나 컬럼명이 JPA naming strategy 때문에 예상과 다를 수도 있다.

예를 들어 Java Entity에서는 `createdAt`인데 DB에서는 `created_at`이어야 할 수 있다.

```java id="0zljdw"
private LocalDateTime createdAt;
```

DB 컬럼은 보통 이렇게 만들어진다.

```sql id="1zog56"
created_at DATETIME
```

이런 차이를 맞추지 않으면 `validate`에서 또 실패한다.

그래서 `init.sql`을 한 번 만들고 끝나는 게 아니라, 계속 수정하면서 맞춰야 했다.

```text id="70sda3"
init.sql
init_v2.sql
init_final.sql
init_real_final.sql
```

이런 식으로 SQL 파일을 여러 번 만들고 수정하는 상황이 생긴다.

## init.sql을 MySQL에 적용하기

작성한 `init.sql`은 실제 MySQL에 적용해야 한다.

로컬에서 만든 파일을 EC2에 보냈다면 이런 식으로 전송할 수 있다.

```bash id="g55wv6"
scp -i key.pem init.sql ubuntu@EC2_PUBLIC_IP:/home/ubuntu/init.sql
```

그다음 EC2에 접속한다.

```bash id="ry403l"
ssh -i key.pem ubuntu@EC2_PUBLIC_IP
```

MySQL에 SQL 파일을 적용한다.

```bash id="jd8f68"
mysql -u appuser -p appdb < /home/ubuntu/init.sql
```

또는 MySQL 콘솔에 들어가서 직접 실행할 수도 있다.

```bash id="zdyxcp"
mysql -u appuser -p
```

```sql id="m8agxv"
USE appdb;
SOURCE /home/ubuntu/init.sql;
```

이렇게 해야 노션에만 있던 테이블 명세가 실제 MySQL 테이블로 만들어진다.

## SHOW TABLES로 확인하기

SQL을 실행했다고 끝이 아니다.
정말 테이블이 만들어졌는지 확인해야 한다.

먼저 사용할 DB를 선택한다.

```sql id="6rkuda"
USE appdb;
```

테이블 목록을 확인한다.

```sql id="rvolxn"
SHOW TABLES;
```

기대하는 테이블이 나와야 한다.

```text id="ih3k04"
+-----------------+
| Tables_in_appdb |
+-----------------+
| user            |
| board           |
| comment         |
+-----------------+
```

그다음 테이블 구조도 확인한다.

```sql id="yn60w6"
DESC user;
```

또는:

```sql id="03x31w"
SHOW CREATE TABLE user;
```

단순히 테이블이 있는지만 보는 게 아니라, 컬럼명과 타입이 Entity와 맞는지도 확인해야 한다.

```text id="htk28u"
테이블명 확인
컬럼명 확인
컬럼 타입 확인
PK 확인
FK 확인
nullable 여부 확인
```

이 검증을 하지 않으면 테이블은 있는데도 validate에서 또 실패할 수 있다.

## validate 실패를 보면서 SQL을 맞추는 과정

`ddl-auto: validate`에서 실패하면 보통 Hibernate가 어떤 테이블이나 컬럼이 문제인지 로그에 남긴다.

예를 들어 이런 식이다.

```text id="off16a"
Schema-validation: missing table [board]
```

이 경우에는 `board` 테이블이 없다는 뜻이다.

또는 이런 식일 수 있다.

```text id="kal36g"
Schema-validation: missing column [created_at] in table [board]
```

이 경우에는 `board` 테이블은 있지만 `created_at` 컬럼이 없다는 뜻이다.

이 로그를 보고 `init.sql`을 수정한다.

```sql id="bsoekt"
ALTER TABLE board ADD COLUMN created_at DATETIME;
```

또는 처음부터 `CREATE TABLE` 문을 다시 수정한다.

이렇게 반복한다.

```text id="2ln5sc"
애플리케이션 실행
→ validate 실패 로그 확인
→ 누락된 테이블/컬럼 파악
→ init.sql 수정
→ MySQL에 다시 적용
→ SHOW TABLES/DESC 확인
→ 애플리케이션 재실행
```

이 과정은 번거롭지만, 덕분에 `validate`가 실제로 무엇을 검사하는지 이해할 수 있었다.

## 왜 그냥 ddl-auto를 update로 바꾸지 않았나?

사실 가장 쉬운 방법은 이거다.

```yaml id="dlt6nf"
spring:
  jpa:
    hibernate:
      ddl-auto: update
```

이렇게 바꾸면 Hibernate가 테이블을 자동으로 맞춰주기 때문에 당장 부팅은 성공할 수도 있다.

하지만 이건 근본 해결이라고 보기 어렵다.

특히 운영이나 배포 환경에서는 애플리케이션이 DB 스키마를 마음대로 변경하게 두는 것이 위험할 수 있다.

```text id="j9v0cx"
의도치 않은 컬럼 추가
스키마 변경 이력 추적 어려움
환경별 DB 상태 불일치
운영 데이터에 영향 가능성
```

그래서 `validate`를 유지하려면, 그에 맞는 절차가 필요하다.

```text id="sg97g8"
DB 스키마는 사람이 명시적으로 준비한다.
애플리케이션은 그 스키마가 Entity와 맞는지 검증한다.
```

이게 `validate`를 사용하는 이유다.

## 이 문제의 핵심은 DB 연결 문제가 아니었다

처음에는 DB 연결 문제처럼 보였지만, 실제 문제는 초기화 절차 문제였다.

```text id="5t0hh1"
DB 서버 실행 여부
→ 정상

DB 계정/비밀번호
→ 확인 필요

DB 테이블 존재 여부
→ 문제

DDL/init.sql 관리 여부
→ 문제

ddl-auto 설정 전제
→ validate라서 테이블 선생성 필요
```

즉, 장애의 본질은 이거였다.

```text id="84zpsi"
애플리케이션 설정은 “이미 테이블이 있다”고 가정했는데,
실제 DB는 초기화되지 않은 상태였다.
```

그래서 해결도 단순히 설정 하나를 바꾸는 게 아니라, DB 초기화 전제를 문서화하고 검증하는 방향으로 갔다.

## 최종적으로 고정한 절차

이후에는 다음 절차를 고정했다.

```text id="0d5asb"
1. 노션 테이블 명세 확인
2. init.sql 작성 또는 수정
3. EC2/MySQL에 init.sql 적용
4. SHOW TABLES로 테이블 생성 확인
5. DESC 또는 SHOW CREATE TABLE로 컬럼 구조 확인
6. 애플리케이션 실행
7. validate 통과 여부 확인
```

명령어로 정리하면 다음과 같다.

```bash id="t8m9ee"
scp -i key.pem init.sql ubuntu@EC2_PUBLIC_IP:/home/ubuntu/init.sql
```

```bash id="lbkem8"
ssh -i key.pem ubuntu@EC2_PUBLIC_IP
```

```bash id="pa5tww"
mysql -u appuser -p appdb < /home/ubuntu/init.sql
```

```sql id="cdh292"
USE appdb;
SHOW TABLES;
DESC user;
DESC board;
```

```bash id="r2k2ti"
java -jar app.jar
```

이렇게 하면서 “DB가 떠 있다”가 아니라 “애플리케이션이 기대하는 스키마가 실제로 존재한다”를 확인하는 절차가 생겼다.

## 포트폴리오에 쓴다면

이 경험은 다음처럼 정리할 수 있다.

```text id="5ym3rx"
Spring Boot 애플리케이션 배포 과정에서 ddl-auto: validate 설정으로 인해 DB 테이블이 선생성되지 않은 상태에서는 부팅이 실패하는 문제가 발생했습니다. 당시 테이블 구조는 노션에만 명세되어 있었고, 정식 DDL/schema.sql 파일이 제공되지 않아 노션 명세를 기반으로 init.sql 형태의 SQL 파일을 작성·수정하며 MySQL 스키마를 수동으로 구성했습니다. 이후 해당 SQL이 실제 DB에 적용되었는지 SHOW TABLES와 DESC 명령으로 확인하는 검증 절차를 고정하여, 환경 초기화 상태에 따른 장애를 통제했습니다.
```

면접에서는 이렇게 말할 수 있다.

```text id="6fc7y5"
당시 ddl-auto가 validate로 설정되어 있어서 Hibernate가 테이블을 자동 생성하지 않고, 이미 존재하는 DB 스키마와 Entity 매핑만 검증하는 구조였습니다. 그런데 실행 가능한 DDL 파일이 정리되어 있지 않았고, 테이블 명세가 노션에만 있었습니다. 그래서 노션 명세를 기반으로 init.sql을 직접 작성하고 여러 번 수정하면서 MySQL에 적용했고, SHOW TABLES와 DESC로 실제 테이블 생성 여부를 확인하는 절차를 만들었습니다.
```

## 정리

이번 문제는 단순한 SQL 작성 문제가 아니었다.

핵심은 `ddl-auto: validate`의 전제 조건을 이해하는 것이었다.

```text id="himqcx"
validate는 테이블을 만들어주지 않는다.
이미 만들어진 테이블이 Entity와 맞는지만 검사한다.
```

그런데 당시에는 테이블 명세가 노션에만 있었고, 실제 MySQL에 적용할 정식 DDL이나 `schema.sql`은 없었다. 그래서 `init.sql`을 직접 만들고 수정하면서 DB 스키마를 맞췄고, `SHOW TABLES`, `DESC` 명령으로 검증 절차를 고정했다.

이 경험을 통해 배운 점은 분명하다.

```text id="k1mwkp"
DB 설계 문서와 실제 DB 스키마는 다르다.
노션에 테이블이 있다고 해서 MySQL에 테이블이 있는 것은 아니다.
```

그리고 `ddl-auto: validate`를 사용하는 환경에서는 반드시 이 전제를 확인해야 한다.

```text id="cl0ynp"
애플리케이션 실행 전에 DB 테이블이 이미 생성되어 있어야 한다.
```

한 줄로 정리하면 다음과 같다.

```text id="fwnw48"
ddl-auto: validate에서 부팅 실패가 발생한 이유는 코드 문제가 아니라, 노션 명세를 실제 DB 스키마로 반영하는 초기화 절차가 빠져 있었기 때문이다.
```