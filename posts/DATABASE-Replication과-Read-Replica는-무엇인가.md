---
title: "[DATABASE] Replication과 Read Replica는 무엇인가\n"
source: "https://velog.io/@yorange50/DATABASE-Replication과-Read-Replica는-무엇인가"
published: "2026-05-11T14:50:27.116Z"
tags: ""
backup_date: "2026-05-29T14:52:52.760617"
---

서비스를 운영하다 보면 어느 순간 문제가 생긴다.

```text id="ep8j2x"
DB가 느리다
```

처음엔 서버 문제 같지만,
실제로는 DB가 병목인 경우가 많다.

특히:

* 조회 요청 폭증
* 사용자 증가
* 트래픽 증가

상황에서 많이 터진다.

이때 자주 등장하는 개념이 있다.

```text id="9a5x3f"
Replication
Read Replica
```

오늘은 이 흐름을 이해해보자.

---

# 1. DB 서버 하나로 충분하지 않은 이유

처음 서비스는 보통 이렇다.

```text id="d5q8gm"
Application
    ↓
Database
```

간단하다.

근데 사용자가 많아지면:

```text id="4e0m8m"
SELECT 요청 폭증
```

이 일어난다.

예:

* 게시글 조회
* 댓글 조회
* 검색
* 피드 조회

등.

---

# 2. 읽기가 훨씬 많다

대부분 서비스는:

```text id="y5m2ra"
읽기(Read) >> 쓰기(Write)
```

다.

예를 들어 SNS라면:

```text id="d1qz9e"
글 1번 작성
조회 10000번
```

이 가능하다.

즉 DB는 보통:

```text id="v8d5ln"
읽기 부하
```

가 훨씬 크다.

---

# 3. 그래서 등장한 게 Replication

Replication은:

> DB 데이터를 다른 DB에 복제하는 것

이다.

---

# 4. 구조

보통 이런 형태다.

```text id="z4g2cp"
Primary DB
    ↓ 복제
Replica DB
```

---

# 5. Primary DB란?

Primary(Main) DB는:

```text id="f2r5wj"
쓰기 담당
```

이다.

즉:

```sql id="l4q3sy"
INSERT
UPDATE
DELETE
```

가 여기서 발생한다.

---

# 6. Replica DB란?

Replica는:

```text id="8r9vqm"
복제본 DB
```

다.

Primary 데이터를 복사해둔다.

보통:

```text id="j7m8pe"
읽기 전용(Read Only)
```

으로 사용한다.

---

# 7. Replication 흐름

예를 들어:

```sql id="kgc02p"
INSERT INTO users ...
```

가 Primary에서 실행되면.

---

## 이후

변경 내용이 Replica로 전달된다.

즉:

```text id="w3z1xl"
Primary
↓
복제
↓
Replica
```

구조다.

---

# 8. Read Replica란?

Read Replica는:

> 읽기 요청을 처리하기 위한 복제 DB

다.

즉:

```text id="1m0djk"
조회 트래픽 분산용
```

이다.

---

# 9. 왜 필요한가?

예를 들어:

```text id="l0g2xq"
사용자 100만명
```

이 동시에 조회하면?

DB 하나가 버티기 어렵다.

그래서:

```text id="6n8jcm"
읽기 요청을 여러 Replica로 분산
```

한다.

---

# 10. 구조 예시

```text id="3e4vzt"
           App
         /  |  \
        /   |   \
 Primary Replica Replica
```

---

## 쓰기

```text id="s5m2ny"
Primary
```

로 감.

---

## 읽기

```text id="5u1vqp"
Replica
```

들로 분산 가능.

---

# 11. 장점

가장 큰 장점은:

```text id="9h0vzn"
읽기 성능 확장
```

이다.

즉:

```text id="y7n2ea"
Scale Out
```

가능.

---

# 12. 고가용성(HA)에도 도움

Replica가 있으면:

```text id="m6g9dt"
Primary 장애
```

시 Replica 승격 가능.

즉 장애 대응에도 사용된다.

---

# 13. 근데 문제도 있다

Replication은 공짜가 아니다.

---

# 14. Replication Delay

Primary 변경사항이:

```text id="q8e1vm"
즉시 Replica에 반영 안 될 수도 있음
```

이다.

즉:

```text id="c1r4zy"
복제 지연
```

이 발생 가능.

---

# 15. 예시

사용자가 글 작성:

```sql id="sk0vlu"
INSERT post
```

직후 조회했는데:

```text id="z2n1wd"
Replica엔 아직 반영 안 됨
```

가능하다.

즉:

```text id="l6d0po"
쓴 직후 조회했는데 안 보임
```

상황 가능.

---

# 16. 왜 발생하는가?

Replication도 결국:

```text id="d4x7cw"
네트워크 전송
로그 복사
동기화 작업
```

이 필요하다.

즉 약간의 시간 차이가 생긴다.

---

# 17. Consistency와 연결

이게 바로:

```text id="a0m2jl"
Consistency
```

문제로 연결된다.

---

## Strong Consistency

항상 최신 데이터 보장.

---

## Eventual Consistency

조금 늦더라도 결국 동일해짐.

Replica 구조는 보통:

```text id="p9q7vg"
Eventually Consistent
```

성향이 강하다.

---

# 18. 그래서 실무에서는 보통 분리한다

---

## 쓰기 직후 조회 중요

→ Primary 조회

---

## 일반 조회

→ Replica 조회

---

예:

```text id="x8r5nj"
내 프로필 수정 직후
→ Primary

게시글 목록 조회
→ Replica
```

---

# 19. Scaling과 연결

Read Replica는:

```text id="w5t2ce"
DB Scale Out 전략
```

중 하나다.

---

## Scale Up

```text id="b7y1ka"
DB 서버 성능 증가
```

---

## Scale Out

```text id="g3e9xt"
DB 서버 수 증가
```

Read Replica는 보통:

```text id="r2n8wm"
읽기 Scale Out
```

전략이다.

---

# 20. AWS에서도 매우 많이 사용

AWS RDS에서도:

```text id="q5v0sl"
Read Replica
```

기능을 제공한다.

예:

```text id="h8u7ce"
RDS MySQL
→ Read Replica 추가
```

하면 자동 복제 가능.

---

# 21. DynamoDB와 차이

DynamoDB는 구조 자체가:

```text id="m9d6ra"
분산 기반
```

이라 자동으로 확장되도록 설계되었다.

반면 관계형 DB는:

```text id="f0v5xn"
Replica 전략
```

을 자주 사용한다.

---

# 22. 실무에서 자주 보는 상황

---

## "조회 느립니다"

→ Read Replica 고려

---

## "DB CPU 100%"

→ 읽기 부하 의심

---

## "데이터가 바로 안 보입니다"

→ Replication Delay 가능성

---

## "장애 대비 필요"

→ Replica 구성

---

# 23. 정리

## Replication

DB 데이터를 다른 DB로 복제

---

## Primary DB

쓰기 담당

---

## Replica DB

복제본 DB

---

## Read Replica

읽기 요청 처리용 Replica

---

## 장점

```text id="w1n2av"
읽기 성능 향상
고가용성
```

---

## 단점

```text id="d6z4qp"
복제 지연
정합성 문제
```

가능성

---

## 핵심 흐름

```text id="f3k9uj"
쓰기:
Primary

읽기:
Replica
```

---

# 한 줄 핵심

```text id="y2q7mc"
Read Replica는
읽기 요청을 분산해서,
DB 트래픽을 버티기 위한 복제 전략이다.
```