---
title: "[DATABASE] Consistency는 왜 어려운가"
source: "https://velog.io/@yorange50/DATABASE-Consistency는-왜-어려운가"
published: "2026-05-11T14:50:59.204Z"
tags: ""
backup_date: "2026-05-29T14:52:52.760234"
---

분산 시스템을 공부하다 보면 꼭 나오는 단어가 있다.

```text id="k1v9pj"
Consistency
```

그리고 같이 나온다.

```text id="m7x3qe"
Eventually Consistent
Strong Consistency
Replication
CAP 이론
```

처음엔 되게 추상적이다.

근데 사실 핵심 질문은 단순하다.

> “모든 서버가 항상 완전히 같은 데이터를 가질 수 있는가?”

오늘은 그 문제를 이해해보자.

---

# 1. Consistency란?

Consistency는:

> 어디서 데이터를 읽든 같은 결과가 보장되는 성질

이다.

예를 들어:

```text id="g5m2yt"
사용자 이름 = kim
```

으로 수정했는데.

---

## 서버 A

```text id="a0n4cw"
kim
```

---

## 서버 B

```text id="d7x8qp"
park
```

를 보여주면?

데이터가 서로 다르다.

즉:

```text id="n3v7lk"
Consistency 깨짐
```

상태다.

---

# 2. 왜 이런 문제가 생길까?

서버가 하나면 쉽다.

```text id="h8z2rp"
App
↓
DB
```

끝이다.

근데 서비스가 커지면:

```text id="v5c0jn"
Replica
분산 DB
캐시
멀티 리전
```

등이 등장한다.

즉:

```text id="m2t6dw"
데이터 복사본이 여러 개
```

생긴다.

---

# 3. Replication과 연결

예를 들어:

```text id="u1e9zk"
Primary DB
↓
Replica DB
```

구조가 있다고 해보자.

---

## 문제

Primary에서 수정한 데이터가:

```text id="x6p1cv"
즉시 Replica로 전달 안 될 수도 있음
```

이다.

---

# 4. 예시

사용자가 닉네임 변경:

```text id="q9r2ml"
kim → park
```

---

## Primary

```text id="t5d7bx"
park
```

---

## Replica

아직:

```text id="j1n8qa"
kim
```

일 수도 있다.

즉:

```text id="s0w4fz"
서버마다 데이터 다름
```

상황 가능.

---

# 5. 왜 즉시 동기화 안 하는가?

여기서 현실 문제가 등장한다.

즉시 완벽 동기화를 하려면:

```text id="c3v6hm"
모든 서버 확인
네트워크 통신
복제 완료 대기
```

가 필요하다.

즉:

```text id="r8p2jt"
속도가 느려짐
```

이다.

---

# 6. 결국 트레이드오프

분산 시스템은 항상 고민한다.

```text id="f4z7xk"
정확성
vs
성능
```

---

# 7. Strong Consistency란?

Strong Consistency는:

> 데이터를 쓰면 즉시 모든 곳에서 동일하게 보이는 상태

다.

즉:

```text id="n6t9qc"
쓰기 직후
어디서 읽어도 최신 데이터
```

보장.

---

# 8. 장점

개발자가 이해하기 쉽다.

예:

```text id="l0x2gv"
방금 수정했는데
조회하면 바로 보여야 함
```

같은 요구에 적합.

---

# 9. 단점

느리다.

왜냐면:

```text id="m8c1yp"
모든 노드 동기화 완료까지 대기
```

해야 하기 때문이다.

특히:

* 글로벌 서비스
* 멀티 리전

에서는 더 어렵다.

---

# 10. Eventually Consistency란?

Eventually Consistency는:

> 지금은 다를 수 있지만,
> 결국에는 같아지는 상태

다.

---

# 11. 예시

```text id="k4d8rn"
지금 Replica:
old data

몇 초 뒤:
new data
```

즉:

```text id="w9m3qe"
잠깐 불일치 허용
```

하는 것이다.

---

# 12. 왜 많이 사용하는가?

엄청 빠르기 때문이다.

분산 시스템에서는:

```text id="a5j2xt"
성능
확장성
가용성
```

이 매우 중요하다.

그래서 많은 시스템이:

```text id="p7y0lm"
Eventually Consistent
```

전략을 선택한다.

---

# 13. DynamoDB도 기본은 Eventually Consistent

AWS DynamoDB도 기본 조회는:

```text id="u3q4wc"
Eventually Consistent Read
```

다.

즉:

```text id="d1m9fp"
조금 오래된 데이터 가능
```

대신:

```text id="m5v8jr"
엄청난 성능과 확장성
```

을 얻는다.

---

# 14. Strongly Consistent Read도 가능

DynamoDB는 옵션으로:

```text id="n2r6yt"
Strongly Consistent Read
```

도 지원한다.

하지만:

```text id="x7w1kp"
더 느리고 비용 증가 가능
```

하다.

---

# 15. 왜 분산 시스템에서 어려운가?

핵심은:

```text id="j0q5ev"
네트워크는 완벽하지 않다
```

이다.

예:

* 지연
* 패킷 손실
* 서버 장애
* 지역 간 거리

등.

즉:

```text id="b6p3zk"
모든 서버를 항상 즉시 동일하게 유지
```

하는 건 생각보다 어렵다.

---

# 16. CAP 이론

여기서 유명한 게:

```text id="v9x8wn"
CAP Theorem
```

이다.

---

# 17. CAP이란?

분산 시스템은 동시에:

```text id="m3c6jp"
Consistency
Availability
Partition Tolerance
```

를 전부 완벽하게 만족하기 어렵다는 이론.

---

# 18. 각각 의미

---

## Consistency

모든 노드 데이터 동일.

---

## Availability

항상 응답 가능.

---

## Partition Tolerance

네트워크 장애 상황 버팀.

---

# 19. 현실에서는?

현실 분산 시스템은:

```text id="f1v9km"
네트워크 장애는 반드시 발생
```

한다고 본다.

즉:

```text id="w8r2qy"
Partition Tolerance
```

는 거의 필수.

그래서 결국:

```text id="y0m4ze"
Consistency
vs
Availability
```

중 어느 쪽을 더 우선할지 고민한다.

---

# 20. 예시

---

## 은행 시스템

```text id="g7p5xt"
Strong Consistency 선호
```

잔액 틀리면 큰일.

---

## SNS 좋아요 수

```text id="v2q8kc"
Eventually Consistency 허용 가능
```

좋아요 숫자 몇 초 늦어도 큰 문제 아님.

---

# 21. 실무에서 자주 보는 상황

---

## "글 작성했는데 바로 안 보입니다"

→ Replication Delay

---

## "지역마다 데이터 조금 다릅니다"

→ Eventually Consistent 가능성

---

## "왜 Strong Consistency 안 쓰나요?"

→ 성능/확장성 비용 때문

---

## "왜 DynamoDB가 빠른가요?"

→ Eventually Consistency 기반 설계

---

# 22. 정리

## Consistency

어디서 읽든 같은 데이터 보장

---

## Strong Consistency

즉시 최신 데이터 보장

---

## Eventually Consistency

잠깐 다를 수 있지만 결국 같아짐

---

## Strong 장점

정확성 높음

---

## Strong 단점

느림

---

## Eventual 장점

빠름
확장성 좋음

---

## Eventual 단점

잠시 데이터 불일치 가능

---

## 핵심 트레이드오프

```text id="r5j1mx"
정확성
vs
성능/확장성
```

---

# 한 줄 핵심

```text id="h4z8vc"
분산 시스템에서는
모든 서버의 데이터를 항상 완벽히 동일하게 유지하는 것이 어렵기 때문에,
Consistency와 성능 사이의 선택이 필요하다.
```