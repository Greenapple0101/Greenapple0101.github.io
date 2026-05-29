---
title: "[NETWORK] RIP, OSPF, BGP 차이 완벽 이해 — IGP/EGP부터 거리벡터까지"
source: "https://velog.io/@yorange50/NETWORK-RIP-OSPF-BGP-차이-완벽-이해-IGPEGP부터-거리벡터까지"
published: "2026-05-11T14:28:27.117Z"
tags: ""
backup_date: "2026-05-29T14:52:52.763462"
---

네트워크가 커지면 문제가 생긴다.

예를 들어 라우터가 수십 대, 수백 대가 되면:“어디로 보내야 가장 빠르지?”
“어느 경로가 죽었지?”
“새로운 네트워크가 생겼네?”
```

이런 걸 사람이 일일이 설정하기 힘들어진다.

그래서 등장한 게:

```plaintext id="j65wry"
Dynamic Routing Protocol
```

즉:

> 라우터끼리 자동으로 길을 학습하는 기술

이다.

대표적으로:

* RIP
* OSPF
* BGP

가 있다.

---

# 1. 먼저 큰 그림부터

라우팅 프로토콜은 크게 두 종류로 나뉜다.

```plaintext id="54yqce"
IGP  → 내부 네트워크용
EGP  → 외부 네트워크용
```

---

# 2. IGP란?

IGP는:

```plaintext id="z9v6hk"
Interior Gateway Protocol
```

즉:

> 하나의 조직 내부에서 사용하는 라우팅 프로토콜

이다.

예:

* 회사 내부망
* AWS 내부 네트워크
* IDC 내부망

대표:

* RIP
* OSPF

---

# 3. EGP란?

EGP는:

```plaintext id="xgmk9w"
Exterior Gateway Protocol
```

즉:

> 서로 다른 조직 간 라우팅

이다.

대표:

* BGP

예:

```plaintext id="8l4pjm"
KT ↔ SKT ↔ AWS ↔ Google
```

인터넷 전체는 사실상 BGP로 연결된다.

---

# 4. RIP, OSPF, BGP 한눈에 보기

| 프로토콜 | 종류  | 방식    | 특징       |
| ---- | --- | ----- | -------- |
| RIP  | IGP | 거리 벡터 | 단순하지만 느림 |
| OSPF | IGP | 링크 상태 | 빠르고 현대적  |
| BGP  | EGP | 경로 벡터 | 인터넷 핵심   |

---

# 5. RIP란?

RIP는:

```plaintext id="8w5sru"
Routing Information Protocol
```

이다.

옛날 라우팅 프로토콜이다.

---

## RIP 동작 방식

RIP는:

> 목적지까지 몇 번 거치는가?

를 기준으로 계산한다.

이걸:

```plaintext id="w9ibx8"
Hop Count
```

라고 한다.

예:

```plaintext id="0n0t8o"
A → B → C
```

이면 Hop 수는 2다.

---

# 6. RIP는 거리 벡터 방식

RIP는:

```plaintext id="d1fgdc"
Distance Vector
```

방식을 사용한다.

뜻은:

```plaintext id="pd87xk"
거리(Distance) + 방향(Vector)
```

즉:

```plaintext id="fkwzlx"
“어디까지 몇 칸이고 어느 방향이야”
```

만 이웃 라우터끼리 주고받는다.

---

# 7. RIP 특징

장점:

* 설정 쉬움
* 가벼움

단점:

* 느림
* 최대 15 Hop 제한
* 대규모 네트워크 부적합

그래서 요즘 실무에서는 거의 잘 안 쓴다.

---

# 8. OSPF란?

OSPF는:

```plaintext id="u2z5o0"
Open Shortest Path First
```

이다.

현대 네트워크에서 매우 많이 사용된다.

---

# 9. OSPF는 링크 상태 방식

OSPF는:

```plaintext id="8pljtt"
Link State
```

방식을 사용한다.

RIP와 다르게:

```plaintext id="czefk0"
네트워크 전체 구조를 이해함
```

---

# 10. OSPF 동작 원리

각 라우터가:

```plaintext id="74eb0o"
“나는 누구랑 연결되어 있어”
```

를 전부 공유한다.

그러면 전체 네트워크 지도가 만들어진다.

그리고:

```plaintext id="e6bxvq"
최단 경로 계산
```

을 수행한다.

이때 사용하는 게:

```plaintext id="klzvvy"
Dijkstra 알고리즘
```

이다.

---

# 11. OSPF 특징

장점:

* 빠름
* 장애 대응 좋음
* 대규모 가능

단점:

* 설정 복잡
* 메모리/CPU 사용량 증가

실무에서:

* 기업망
* IDC
* 클라우드
* 대형 네트워크

에서 매우 많이 사용된다.

---

# 12. BGP란?

BGP는:

```plaintext id="t7b6u8"
Border Gateway Protocol
```

이다.

인터넷의 핵심 프로토콜이다.

---

# 13. BGP는 왜 필요할까?

인터넷은:

```plaintext id="c4is6o"
수많은 회사/통신사/클라우드
```

가 연결된 구조다.

예:

```plaintext id="6d8q4f"
AWS
Google
KT
SKT
Cloudflare
```

이 서로 연결된다.

이 조직들은 각각:

```plaintext id="ot6vgk"
AS(Autonomous System)
```

라는 독립 네트워크를 가진다.

BGP는:

> AS와 AS 사이를 연결

한다.

---

# 14. BGP는 경로 벡터 방식

BGP는:

```plaintext id="xk6i53"
Path Vector
```

방식이다.

즉:

```plaintext id="rq2p9s"
“어떤 경로를 거쳐왔는지”
```

를 저장한다.

예:

```plaintext id="gvjlwm"
KT → AWS → Google
```

이런 경로 자체를 본다.

---

# 15. BGP 특징

장점:

* 인터넷 규모 가능
* 정책 기반 제어 가능
* 매우 유연

단점:

* 설정 어려움
* 복잡함
* 느릴 수 있음

하지만:

```plaintext id="s2gjm5"
인터넷 자체가 BGP 위에서 동작
```

한다고 봐도 된다.

---

# 16. 거리 벡터 vs 링크 상태 vs 경로 벡터

---

## 1) 거리 벡터

대표:

* RIP

방식:

```plaintext id="jlwm4n"
“목적지까지 몇 칸”
```

특징:

* 단순
* 느림

---

## 2) 링크 상태

대표:

* OSPF

방식:

```plaintext id="gzh3s6"
네트워크 전체 지도 생성
```

특징:

* 빠름
* 정확함

---

## 3) 경로 벡터

대표:

* BGP

방식:

```plaintext id="rdr4az"
어떤 AS를 거쳤는지 추적
```

특징:

* 인터넷 규모
* 정책 제어 가능

---

# 17. 쉽게 비유하면

---

## RIP

```plaintext id="c2e3n0"
“몇 정거장 남았어?”
```

---

## OSPF

```plaintext id="u2ahh8"
“전체 지도 보고 최단경로 계산”
```

---

## BGP

```plaintext id="chpuxz"
“어느 나라들을 거쳐가는가?”
```

---

# 18. 실무에서는?

실제로는:

* RIP → 거의 안 씀
* OSPF → 기업 내부망
* BGP → 인터넷/대규모 ISP/클라우드

느낌이다.

특히 클라우드/DevOps 공부하다 보면:

* AWS Direct Connect
* VPN
* Transit Gateway
* Kubernetes CNI
* IDC 네트워크

이런 데서 BGP/OSPF 개념이 계속 등장한다.

---

# 19. 한줄 요약

```plaintext id="vqpss7"
RIP  = 단순 거리 계산
OSPF = 전체 지도 기반 최단경로
BGP  = 인터넷 규모의 경로 관리
```

그리고 인터넷은 결국:

> 수많은 라우터들이 서로 길을 알려주며 움직이는 거대한 네트워크 시스템

이다.