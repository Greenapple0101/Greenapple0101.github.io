---
title: "[HA] Failover란 무엇인가?"
source: "https://velog.io/@yorange50/HA-Failover란-무엇인가"
published: "2026-05-11T15:07:50.186Z"
tags: ""
backup_date: "2026-05-29T14:52:52.759212"
---

서비스를 운영하다 보면 언젠가는 서버가 죽는다.

이건 거의 피할 수 없는 문제다.

예를 들어:

* DB 프로세스 종료
* 서버 다운
* 네트워크 장애
* 클라우드 장애
* 디스크 손상

같은 상황은 실제 운영 환경에서 계속 발생한다.

문제는 DB 하나만 사용하는 구조에서는:

```text id="m7i5fj"
DB 장애 = 서비스 전체 장애
```

가 되어버린다는 점이다.

즉 사용자는:

* 로그인 불가
* 게시글 조회 불가
* 결제 실패
* API 오류

같은 문제를 겪게 된다.

그래서 등장한 개념이 바로:

```text id="m5sjxq"
Failover
```

다.

---

# Failover란?

Failover는 말 그대로:

```text id="fyl9s9"
장애가 발생했을 때
대기 중인 다른 서버로 자동 전환하는 것
```

이다.

핵심 목표는:

```text id="8j6i0d"
서비스를 최대한 안 멈추게 만드는 것
```

이다.

---

# 가장 기본적인 구조

보통 이런 구조를 사용한다.

```text id="0lv3gd"
         ┌─────────────┐
         │ Primary DB  │
         └──────┬──────┘
                │
          Replication
                │
         ┌──────▼──────┐
         │ Standby DB  │
         └─────────────┘
```

여기서:

* Primary DB

  * 실제 서비스 처리
  * 쓰기/읽기 담당

* Standby DB

  * 대기 상태
  * Primary 데이터를 계속 복제받음

역할을 한다.

---

# 장애가 발생하면?

만약 Primary DB가 죽으면:

```text id="40bsg2"
서비스 불가능 상태
```

가 된다.

그래서 시스템은:

```text id="ifhjif"
Standby DB를 새로운 Primary로 승격(Promotion)
```

시킨다.

즉:

```text id="g5jg0k"
장애 서버 대신 다른 서버가 즉시 역할 수행
```

하는 것이다.

이 과정 전체가 Failover다.

---

# 자동 Failover

실제 운영에서는 사람이 직접 바꾸면 늦다.

그래서 대부분:

```text id="gmkc5v"
자동 Failover
```

를 사용한다.

동작 흐름은 보통 이렇다.

```text id="8cnlfm"
1. Health Check 수행
2. Primary 장애 감지
3. Standby 승격
4. 트래픽 재연결
5. 서비스 복구
```

예:

* AWS RDS Multi-AZ
* Aurora Failover
* Kubernetes Self-Healing

등도 비슷한 철학을 가진다.

---

# Health Check란?

자동 Failover의 핵심은:

```text id="7ry8a8"
서버가 살아있는지 계속 감시하는 것
```

이다.

이를 `Health Check`라고 한다.

예:

* DB 연결 가능 여부
* 응답 시간
* TCP 포트 확인
* 특정 API 응답 검사

등을 계속 확인한다.

그리고 일정 조건 이상 실패하면:

```text id="95c2qh"
“이 서버 죽었다”
```

고 판단한다.

---

# Active-Standby 구조

Failover는 보통:

```text id="pp1hpn"
Active-Standby
```

구조를 많이 사용한다.

즉:

* Active

  * 현재 서비스 처리 중

* Standby

  * 대기 중
  * 장애 시 즉시 전환

구조다.

이 방식의 장점은:

* 안정성 높음
* 구조 단순
* 장애 대응 쉬움

이다.

반면:

```text id="gg2j5s"
Standby 서버가 평소엔 놀고 있음
```

이라는 단점도 존재한다.

---

# Split Brain 문제

Failover는 생각보다 어렵다.

대표적인 문제 중 하나가:

```text id="wzkb75"
Split Brain
```

이다.

예를 들어 네트워크 문제로 인해:

* Primary도 살아있다고 생각
* Standby도 자기가 Primary라고 생각

하면:

```text id="o91x1x"
Primary가 2개 생김
```

상황이 발생한다.

그러면 데이터 충돌이 발생할 수 있다.

그래서 실제 HA 시스템은:

* Quorum
* Leader Election
* Consensus

같은 복잡한 기술까지 사용한다.

---

# Failover와 High Availability의 관계

중요한 점은:

```text id="5rmp2j"
Failover 자체가 목적은 아니다
```

라는 것이다.

Failover는 결국:

```text id="7xj7lb"
High Availability(고가용성)
```

을 달성하기 위한 방법 중 하나다.

즉:

* 장애가 나도
* 최대한 서비스가 계속 동작하도록 만드는 것

이 최종 목표다.

---

# 마무리

Failover는 단순히 “백업 서버” 개념이 아니다.

실제로는:

* 장애 감지
* 자동 전환
* 서비스 복구
* 데이터 안정성

까지 포함하는 핵심 운영 기술이다.

현대 서비스에서는:

```text id="1e7hzt"
“서버는 언젠가 죽는다”
```

를 전제로 시스템을 설계한다.

그리고 Failover는 그 현실을 버티기 위한 가장 중요한 전략 중 하나다.