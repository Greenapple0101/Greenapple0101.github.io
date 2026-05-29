---
title: "[SPRING] ddl-auto: validate에서 테이블이 없으면 왜 부팅이 실패할까?"
source: "https://velog.io/@yorange50/SPRING-ddl-auto-validate에서-테이블이-없으면-왜-부팅이-실패할까"
published: "2026-05-17T09:59:01.622Z"
tags: ""
backup_date: "2026-05-29T14:52:52.736628"
---

Spring Boot 애플리케이션을 EC2 서버에 배포하다가 부팅이 실패한 적이 있다. 처음에는 MySQL 연결 문제인가 싶었다. DB 주소가 틀렸는지, 계정 정보가 잘못됐는지, 포트가 막혔는지부터 확인했다. 그런데 문제의 핵심은 DB 연결 자체가 아니라 **DB 안에 애플리케이션이 기대하는 테이블이 없었다는 것**이었다. 더 정확히 말하면, JPA 설정은 `ddl-auto: validate`였는데 실행 가능한 DDL 파일이나 `schema.sql`은 없고, 테이블 구조는 노션 문서에만 남아 있었다.

## 문제 상황

애플리케이션 설정에는 다음과 같은 JPA 설정이 들어 있었다.

```yaml id="icqwpw"
spring:
  jpa:
    hibernate:
      ddl-auto: validate
```

이 설정을 둔 상태에서 Spring Boot 애플리케이션을 실행했다.

```bash id="c2hpky"
java -jar app.jar
```

그런데 애플리케이션이 정상적으로 뜨지 않고 부팅 단계에서 실패했다.

처음에는 DB 접속 문제라고 생각할 수 있다.

```text id="svlk3z"
MySQL이 안 떠 있나?
DB 계정이 틀렸나?
비밀번호가 틀렸나?
3306 포트가 막혔나?
application.yml 설정이 잘못됐나?
```

하지만 실제 원인은 조금 달랐다.

DB 서버는 떠 있었지만, 애플리케이션이 필요로 하는 테이블이 MySQL 안에 생성되어 있지 않았다.

## ddl-auto: validate란?

Spring Boot에서 JPA와 Hibernate를 사용할 때 `ddl-auto` 설정은 애플리케이션 실행 시 DB 스키마를 어떻게 다룰지 결정한다.

대표적으로 이런 값들이 있다.

```yaml id="zvteob"
spring:
  jpa:
    hibernate:
      ddl-auto: create
```

`create`는 애플리케이션 실행 시 테이블을 새로 만든다. 기존 테이블을 지우고 다시 만들 수 있기 때문에 운영 환경에서는 위험하다.

```yaml id="tzf9f2"
spring:
  jpa:
    hibernate:
      ddl-auto: update
```

`update`는 Entity를 기준으로 DB 스키마를 어느 정도 맞춰준다. 개발 환경에서는 편하지만, 운영 환경에서는 의도치 않은 스키마 변경이 생길 수 있다.

```yaml id="8nj35w"
spring:
  jpa:
    hibernate:
      ddl-auto: validate
```

`validate`는 테이블을 만들거나 수정하지 않는다.
오직 Entity와 DB에 이미 존재하는 테이블 구조가 맞는지만 검사한다.

즉, `validate`의 의미는 이거다.

```text id="ntxcot"
“테이블은 이미 있다고 가정할게.
나는 Entity와 DB 테이블이 맞는지만 확인할게.”
```

그래서 `validate`를 사용하려면 반드시 애플리케이션 실행 전에 DB 테이블이 먼저 만들어져 있어야 한다.

## 왜 테이블이 없으면 부팅이 실패할까?

예를 들어 애플리케이션에 이런 Entity가 있다고 해보자.

```java id="p0o4zl"
@Entity
public class Member {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String email;

    private String name;
}
```

Hibernate는 애플리케이션이 시작될 때 이 Entity를 보고 DB에 `member` 테이블이 있는지 확인한다.

그런데 MySQL에 접속해서 확인했을 때 테이블이 없다면?

```sql id="dsepnk"
SHOW TABLES;
```

결과가 비어 있거나 `member` 테이블이 없다면 Hibernate는 이렇게 판단한다.

```text id="cdk7wn"
Member Entity는 존재함
→ member 테이블이 DB에 있어야 함
→ 그런데 DB에 없음
→ validate 실패
→ 애플리케이션 부팅 실패
```

즉, `ddl-auto: validate`는 DB를 자동으로 만들어주는 설정이 아니다.
이미 만들어져 있는 DB 구조가 코드와 맞는지 검사하는 설정이다.

## 진짜 문제: 테이블 명세는 노션에만 있었다

당시 상황에서 더 큰 문제는 실행 가능한 DDL 파일이 없었다는 점이었다.

테이블 구조 자체가 아예 없었던 것은 아니다.
노션에는 테이블 명세가 정리되어 있었다.

예를 들면 이런 식이다.

```text id="0ik9ti"
member
- id: bigint
- email: varchar(255)
- name: varchar(255)
- created_at: datetime
```

문서로 보면 테이블 구조가 있는 것처럼 보인다.
하지만 MySQL은 노션 문서를 읽어서 테이블을 만들어주지 않는다.

DB에 테이블을 만들려면 실제 SQL이 필요하다.

```sql id="brykk2"
CREATE TABLE member (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at DATETIME
);
```

즉, 문제는 테이블 설계가 없었던 게 아니다.

정확히는 이거였다.

```text id="tyotew"
테이블 명세는 노션에 있었지만,
MySQL에 적용 가능한 DDL 파일이나 schema.sql이 없었다.
```

그래서 서버에 애플리케이션을 올려도 DB에는 아무 테이블이 없었고, `ddl-auto: validate`가 실패하면서 부팅이 멈췄다.

## schema.sql이 있었다면 어땠을까?

Spring Boot에서는 `schema.sql`을 통해 초기 테이블 생성 SQL을 관리할 수 있다.

예를 들어 `src/main/resources/schema.sql`에 다음과 같이 작성할 수 있다.

```sql id="s0o2ds"
CREATE TABLE member (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at DATETIME
);
```

그러면 애플리케이션 실행 시점에 이 SQL을 적용할 수 있다.

다만 Spring Boot 버전이나 설정에 따라 `schema.sql` 실행 여부는 별도로 확인해야 한다. 특히 JPA와 함께 사용할 때는 다음 설정이 필요할 수 있다.

```yaml id="86sbyb"
spring:
  sql:
    init:
      mode: always
```

또는 운영 환경에서는 애플리케이션 실행 시 자동 적용보다, 배포 전에 명시적으로 SQL을 실행하는 방식을 선택할 수도 있다.

중요한 건 이것이다.

```text id="4p6xqd"
validate를 쓰려면
애플리케이션 실행 전에
DB 테이블이 이미 만들어져 있어야 한다.
```

## 해결 방향

이번 문제는 단순히 `ddl-auto`를 `update`로 바꾸면 해결되는 것처럼 보일 수 있다.

```yaml id="ekhhzq"
spring:
  jpa:
    hibernate:
      ddl-auto: update
```

하지만 이건 근본 해결이 아니다.

개발 환경에서는 `update`로 임시 해결할 수 있다.
하지만 운영이나 배포 환경에서 Hibernate가 자동으로 테이블을 바꾸게 두는 것은 위험할 수 있다.

그래서 이번에는 `validate` 설정을 유지하되, 그 전제 조건을 명확히 했다.

```text id="l4hfgj"
1. validate는 테이블을 자동 생성하지 않는다.
2. 실행 전에 DB 테이블이 선생성되어 있어야 한다.
3. 노션 테이블 명세만으로는 부족하다.
4. 실행 가능한 DDL 또는 schema.sql이 필요하다.
5. 배포 전 SHOW TABLES로 테이블 존재 여부를 확인한다.
```

## 검증 절차 고정하기

문제를 해결하기 위해 배포 전 검증 절차를 고정했다.

먼저 MySQL에 접속한다.

```bash id="tov7no"
mysql -u appuser -p
```

사용할 DB를 선택한다.

```sql id="vd914m"
USE appdb;
```

테이블 목록을 확인한다.

```sql id="o2l6xn"
SHOW TABLES;
```

필요한 테이블이 있는지 확인한다.

```text id="zdxz9k"
member
board
comment
...
```

테이블 구조도 확인한다.

```sql id="c7mtcb"
DESC member;
```

또는:

```sql id="nprz1f"
SHOW CREATE TABLE member;
```

이렇게 확인하면 단순히 “DB가 떠 있다”가 아니라, **애플리케이션이 기대하는 스키마가 실제로 존재하는지** 확인할 수 있다.

검증 흐름은 다음과 같이 정리할 수 있다.

```text id="38tqbt"
노션 테이블 명세 확인
→ DDL 또는 schema.sql 작성/확보
→ MySQL에 적용
→ SHOW TABLES로 테이블 존재 확인
→ DESC로 컬럼 구조 확인
→ 애플리케이션 실행
```

## 이 트러블슈팅에서 배운 점

이 문제를 겪으면서 `ddl-auto: validate`의 의미를 명확히 이해하게 됐다.

처음에는 “JPA가 알아서 테이블을 만들어주는 거 아닌가?”라고 생각하기 쉽다.
하지만 그건 `create`나 `update`에 가까운 이야기다.

`validate`는 전혀 다르다.

```text id="dz52ao"
create/update:
Entity를 기준으로 DB를 만들거나 수정하려고 함

validate:
DB가 이미 준비되어 있다고 보고 검사만 함
```

따라서 `validate`를 쓰는 환경에서는 DB 초기화 절차가 반드시 필요하다.

그리고 문서도 중요하지만, 문서만으로는 부족하다.

```text id="7r58t3"
노션 테이블 명세:
사람이 이해하기 위한 설계 문서

DDL/schema.sql:
DB가 실제로 실행할 수 있는 스키마 생성 코드
```

둘은 역할이 다르다.

노션에 테이블이 정리되어 있어도, MySQL 안에 테이블이 만들어져 있지 않으면 애플리케이션은 뜨지 않는다.

## 포트폴리오에 정리한다면

이 경험은 다음처럼 정리할 수 있다.

```text id="jfx8hh"
Spring Boot 애플리케이션 배포 과정에서 ddl-auto: validate 설정으로 인해 DB 테이블이 선생성되지 않은 상태에서는 부팅이 실패하는 문제가 발생했습니다. 당시 테이블 구조는 노션에 명세되어 있었지만, 실행 가능한 DDL 파일이나 schema.sql이 제공되지 않아 MySQL 초기화 상태가 불명확했습니다. validate 설정의 전제 조건을 문서화하고, schema.sql 적용 여부와 SHOW TABLES, DESC 기반 검증 절차를 고정하여 환경 초기화 상태에 따른 장애를 통제했습니다.
```

면접에서는 이렇게 말할 수 있다.

```text id="gumf74"
당시 ddl-auto 설정이 validate였기 때문에 Hibernate가 테이블을 자동 생성하지 않고 기존 DB 스키마와 Entity 매핑만 검증했습니다. 그런데 테이블 구조는 노션에만 있고 실제 DDL이나 schema.sql이 없어서 MySQL에는 테이블이 생성되지 않은 상태였습니다. 그래서 애플리케이션 부팅이 실패했고, 이후 validate의 전제 조건을 정리하고 SHOW TABLES, DESC 명령으로 배포 전 DB 초기화 상태를 확인하는 절차를 만들었습니다.
```

## 정리

`ddl-auto: validate`는 안전한 설정처럼 보이지만, 전제 조건이 있다.

```text id="jz58up"
DB 테이블이 이미 존재해야 한다.
```

이 전제가 만족되지 않으면 애플리케이션은 부팅 단계에서 실패한다.

이번 문제의 핵심은 DB 서버가 죽어 있었던 것이 아니다.
테이블 설계가 아예 없었던 것도 아니다.

문제는 이것이었다.

```text id="f652op"
테이블 명세는 노션에 있었지만,
실제 DB에 적용할 DDL/schema.sql이 없었다.
```

그래서 해결은 단순히 설정을 바꾸는 것이 아니라, `validate`가 요구하는 전제를 명확히 문서화하고, 배포 전 DB 초기화 상태를 검증하는 절차를 만드는 것이었다.

한 줄로 정리하면 다음과 같다.

```text id="egpvmg"
ddl-auto: validate는 테이블을 만들어주는 설정이 아니라, 이미 만들어진 테이블이 Entity와 맞는지 검사하는 설정이다.
```