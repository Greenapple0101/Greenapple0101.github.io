---
title: "[DATABASE] DynamoDB는 왜 쓰는가"
source: "https://velog.io/@yorange50/DATABASE-DynamoDB는-왜-쓰는가"
published: "2026-05-11T14:57:21.674Z"
tags: ""
backup_date: "2026-05-29T14:52:52.759894"
---

AWS를 공부하다 보면 꼭 등장하는 DB가 있다.

```text id="p2x8vk"
DynamoDB
```

그리고 보통 같이 나온다.

```text id="q7m1zr"
NoSQL
Auto Scaling
고가용성
Partition Key
Eventually Consistent
```

처음엔 이런 생각이 든다.

```text id="r4v9jt"
"MySQL 쓰면 되는 거 아닌가?"
```

근데 대규모 서비스에서는 관계형 DB만으로 버티기 어려운 상황이 자주 나온다.

오늘은:

> 왜 DynamoDB 같은 NoSQL이 등장했는가

를 흐름으로 이해해보자.

---

# 1. 관계형 DB(RDB)의 장점

우리가 흔히 쓰는 DB:

* MySQL
* PostgreSQL
* Oracle

등은 관계형 DB다.

---

## 장점

```text id="s1k6pw"
정확한 데이터 관리
JOIN
트랜잭션
강한 정합성
```

이 매우 좋다.

---

# 2. 근데 문제가 생긴다

서비스가 엄청 커지면:

```text id="t8m3qx"
수억 사용자
엄청난 트래픽
전 세계 요청
```

을 처리해야 한다.

이때 관계형 DB는 점점 어려워진다.

---

# 3. 왜 어려운가?

대표적으로:

```text id="u5n0zr"
Scale Out 어려움
```

이다.

---

# 4. 관계형 DB는 보통 Scale Up 중심

예를 들어:

```text id="v2q7xt"
CPU 증가
RAM 증가
```

로 버틴다.

근데 결국:

```text id="w9m4pk"
장비 한계
비용 폭증
```

문제가 생긴다.

---

# 5. 그래서 등장한 게 NoSQL

NoSQL은:

> 대규모 분산 환경에 맞게 설계된 DB 계열

이다.

즉:

```text id="x6n1qv"
확장성 우선
```

철학이 강하다.

---

# 6. DynamoDB란?

DynamoDB는 AWS의:

```text id="y3m8zr"
완전관리형(NoSQL) DB
```

다.

AWS가 서버 관리까지 해준다.

즉 사용자는:

```text id="z0q5xt"
DB 서버 운영
패치
백업
샤딩
```

등을 직접 덜 신경 써도 된다.

---

# 7. DynamoDB 핵심 특징

핵심은 크게:

```text id="a7n2qv"
1. 엄청난 확장성
2. 고가용성
3. 빠른 응답
```

이다.

---

# 8. 관계형 DB와 가장 큰 차이

RDB는 보통:

```text id="b4m9zr"
테이블 관계
JOIN
정규화
```

중심이다.

---

## DynamoDB는?

DynamoDB는:

```text id="c1q6xt"
Key-Value 기반
```

철학이 강하다.

즉:

```text id="d8n3qv"
빠른 조회
```

를 매우 중요하게 본다.

---

# 9. DynamoDB 기본 구조

예:

```text id="e5m0zr"
UserID → 사용자 데이터
```

형태.

즉:

```text id="f2q7xt"
Key 기반 조회
```

에 매우 최적화되어 있다.

---

# 10. Partition Key란?

DynamoDB에서 가장 중요한 개념 중 하나.

---

## 역할

데이터를:

```text id="g9n4qv"
어느 서버(파티션)에 저장할지 결정
```

한다.

---

# 11. 왜 중요할까?

DynamoDB는 내부적으로:

```text id="h6m1zr"
수많은 서버에 데이터 분산 저장
```

한다.

즉:

```text id="i3q8xt"
Partition Key
↓
데이터 위치 결정
```

구조다.

---

# 12. 그래서 잘못 설계하면?

예를 들어 모든 요청이:

```text id="j0n5qv"
같은 Partition Key
```

로 몰리면?

한 서버만 과부하된다.

이걸:

```text id="k7m2zr"
Hot Partition
```

문제라고 한다.

---

# 13. DynamoDB가 빠른 이유

핵심은:

```text id="l4q9xt"
분산 구조
```

다.

즉 데이터를 여러 서버에 나눠 저장해서:

```text id="m1n6qv"
병렬 처리
```

가능하다.

---

# 14. Auto Scaling

DynamoDB는 자동 확장도 지원한다.

예:

```text id="n8m3zr"
트래픽 증가
↓
자동으로 처리량 증가
```

즉 운영자가 직접:

```text id="o5q0xt"
DB 서버 추가
샤딩
```

같은 걸 덜 신경 써도 된다.

---

# 15. 고가용성(HA)

DynamoDB는 기본적으로:

```text id="p2n7qv"
여러 AZ(가용영역)
```

에 데이터를 복제한다.

즉 서버 일부가 죽어도:

```text id="q9m4zr"
서비스 계속 가능
```

하다.

---

# 16. Consistency 문제

근데 여기서 중요한 트레이드오프가 나온다.

---

# 17. DynamoDB 기본은 Eventually Consistent

즉:

```text id="r6q1xt"
쓰기 직후
잠깐 오래된 데이터 조회 가능
```

하다.

---

# 18. 왜 이런 선택을 할까?

이유는:

```text id="s3n8qv"
성능
확장성
가용성
```

때문이다.

분산 시스템에서:

```text id="t0m5zr"
Strong Consistency
```

를 항상 유지하려면 비용이 크다.

---

# 19. Strongly Consistent Read도 가능

옵션으로:

```text id="u7q2xt"
Strongly Consistent Read
```

도 가능.

하지만:

```text id="v4n9qv"
더 느리고 비용 증가
```

가능성이 있다.

---

# 20. DynamoDB가 잘 맞는 서비스

예:

* 게임 랭킹
* 세션 저장
* 사용자 프로필
* IoT 데이터
* 대규모 API

같이:

```text id="w1m6zr"
엄청난 트래픽
```

을 처리하는 서비스.

---

# 21. DynamoDB가 애매한 경우

반대로:

```text id="x8q3xt"
복잡한 JOIN
강한 트랜잭션
복잡한 관계형 데이터
```

가 중요하면 RDB가 더 적합할 수 있다.

---

# 22. 실무에서 자주 나오는 질문

---

## "왜 DynamoDB를 쓰나요?"

→ 확장성 + 운영 편의성

---

## "왜 빠른가요?"

→ 분산 구조 + Key 기반 조회

---

## "왜 Eventually Consistent 기본인가요?"

→ 성능/확장성 때문

---

## "왜 Partition Key가 중요하죠?"

→ 데이터 분산 결정

---

# 23. RDB vs DynamoDB 느낌 비교

| 항목   | RDB      | DynamoDB  |
| ---- | -------- | --------- |
| 구조   | 관계형      | Key-Value |
| 강점   | 정합성      | 확장성       |
| JOIN | 강함       | 제한적       |
| 확장   | 어려움      | 쉬움        |
| 운영   | 직접 관리 많음 | AWS 관리형   |

---

# 24. 정리

## DynamoDB

AWS의 NoSQL DB

---

## 핵심 특징

```text id="y5n0qv"
확장성
고가용성
빠른 조회
```

---

## Partition Key

데이터 분산 기준

---

## 기본 Consistency

```text id="z2m7zr"
Eventually Consistent
```

---

## 장점

```text id="a9q4xt"
Auto Scaling
운영 편의성
분산 처리
```

---

## 단점

```text id="b6n1qv"
복잡한 관계형 처리 어려움
```

---

## 핵심 철학

```text id="c3m8zr"
정합성 일부를 양보하고,
엄청난 확장성을 얻는다.
```

---

# 한 줄 핵심

```text id="d0q5xt"
DynamoDB는 대규모 트래픽을 빠르게 처리하기 위해,
분산과 확장성에 최적화된 AWS NoSQL 데이터베이스다.
```