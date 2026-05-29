---
title: "[HA] Read Scaling은 왜 필요할까?"
source: "https://velog.io/@yorange50/HA-Read-Scaling은-왜-필요할까"
published: "2026-05-11T15:07:02.867Z"
tags: ""
backup_date: "2026-05-29T14:52:52.759547"
---



서비스를 운영하다 보면 대부분의 시스템은 시간이 갈수록 “읽기(Read)” 요청이 폭발적으로 증가한다.

예를 들어:

* 게시판 글 조회
* 쇼핑몰 상품 조회
* 유튜브 영상 목록 조회
* SNS 피드 조회

같은 작업들은 대부분 `SELECT` 쿼리다.

반면:

* 회원가입
* 게시글 작성
* 댓글 작성

같은 쓰기(Write) 작업은 상대적으로 적은 경우가 많다.

즉 실제 서비스는 보통:

```text
Read >>> Write
```

구조가 된다.

문제는 DB 서버 하나가 모든 읽기 요청까지 혼자 처리하기 시작하면,
점점 병목(Bottleneck)이 발생한다는 점이다.

---

# DB Scale Up의 한계

처음에는 보통 이렇게 생각한다.

> “DB 서버 CPU랑 메모리 더 좋은 걸로 바꾸면 되지 않나?”

이걸 `Scale Up`이라고 한다.

즉:

* CPU 증가
* RAM 증가
* 더 좋은 장비 사용

으로 버티는 방식이다.

하지만 이 방식에는 한계가 있다.

왜냐면:

* 비용이 매우 비싸지고
* 물리적 한계가 존재하며
* 특정 시점부터 성능 증가폭이 작아지기 때문이다.

그래서 대규모 서비스는 결국:

> 읽기 요청 자체를 여러 서버로 분산

하기 시작한다.

이 개념이 바로:

```text
Read Scaling
```

이다.

---

# Read Scaling이란?

Read Scaling은 말 그대로:

> 읽기 처리 성능을 확장하는 전략

이다.

핵심 목표는:

```text
많은 SELECT 요청을 여러 서버가 나눠 처리하게 만드는 것
```

이다.

그리고 가장 대표적인 방법이 바로:

```text
Read Replica
```

구조다.

---

# Read Replica 구조

기본적인 구조는 이렇다.

```text
                ┌─────────────┐
                │  Primary DB │
                └──────┬──────┘
                       │
                 Replication
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌─────────────┐               ┌─────────────┐
│ Replica DB  │               │ Replica DB  │
└─────────────┘               └─────────────┘
```

여기서:

* Primary DB

  * INSERT
  * UPDATE
  * DELETE
  * 실제 원본 데이터 관리

* Replica DB

  * SELECT 전용
  * Primary 데이터를 복제받음

역할을 한다.

즉:

* 쓰기는 Primary
* 읽기는 Replica

로 분리하는 구조다.

---

# 왜 성능이 좋아질까?

예를 들어 사용자 100만 명이 계속 조회만 한다고 가정해보자.

DB 하나만 있으면:

```text
SELECT 요청 전부 → Primary DB
```

로 몰린다.

하지만 Replica를 3개 붙이면:

```text
SELECT 요청 분산
```

이 가능해진다.

즉:

```text
읽기 처리량 증가
```

효과가 생긴다.

이게 Read Scaling의 핵심이다.

---

# Scale Out 개념

Read Scaling은 보통 `Scale Out` 방식이다.

즉:

```text
서버 성능을 키우는 게 아니라
서버 개수를 늘리는 방식
```

이다.

예:

* Replica 1대
* Replica 3대
* Replica 10대

처럼 확장 가능하다.

대규모 서비스들이 이 구조를 매우 많이 사용한다.

예:

* AWS RDS Read Replica
* MySQL Replication
* PostgreSQL Streaming Replication

등.

---

# 하지만 문제도 존재한다

Read Scaling은 매우 강력하지만,
중요한 문제가 하나 있다.

바로:

```text
데이터 동기화 시간 차이
```

이다.

Primary DB에 데이터를 저장했다고 해서,
Replica DB가 완전히 동시에 반영되는 것은 아니다.

즉 이런 상황이 가능하다.

```text
1. 사용자가 글 작성
2. Primary에는 저장 완료
3. Replica는 아직 복제 안 됨
4. 조회 시 최신 데이터가 안 보임
```

이걸:

```text
Replication Lag
```

라고 한다.

---

# 결국 Consistency 문제가 등장한다

여기서 분산 시스템의 핵심 고민이 시작된다.

```text
성능을 높일 것인가?
데이터 일관성을 우선할 것인가?
```

즉:

* 읽기 성능 향상
* 데이터 최신성 보장

사이의 트레이드오프가 발생한다.

그래서 다음 단계에서는:

* Replication
* Consistency
* Eventual Consistency

같은 개념들이 등장하게 된다.

---

# 마무리

Read Scaling은 단순히 “DB 복사” 기술이 아니다.

실제로는:

* 대규모 트래픽 처리
* DB 병목 완화
* 고성능 서비스 운영

을 위한 핵심 전략이다.

그리고 대부분의 현대 서비스는:

```text
Read >>> Write
```

구조를 가지기 때문에,
읽기 확장은 거의 필수적인 설계가 되었다.