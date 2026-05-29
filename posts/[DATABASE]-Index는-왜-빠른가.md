---
title: "[DATABASE] Index는 왜 빠른가"
source: "https://velog.io/@yorange50/DATABASE-Index는-왜-빠른가"
published: "2026-05-11T14:49:17.924Z"
tags: ""
backup_date: "2026-05-29T14:52:52.760968"
---

DB를 공부하다 보면 꼭 듣는 말이 있다.

```sql id="y5ezpz"
인덱스 걸어라
```

그리고 보통 같이 나온다.

```text id="m0jv9q"
조회 성능
Full Scan
B-Tree
속도 최적화
```

근데 처음엔 의문이 든다.

```text id="r0hn4g"
"그냥 찾으면 되는 거 아닌가?"
```

왜 인덱스를 쓰면 빨라질까?

오늘은 그 원리를 이해해보자.

---

# 1. 인덱스(Index)란?

인덱스는 한마디로:

> 데이터를 빠르게 찾기 위한 목차

다.

책을 생각해보자.

---

## 인덱스 없는 경우

책에서:

```text id="3d4r4x"
"쿠버네티스"
```

찾으려면?

처음부터 끝까지 읽어야 한다.

---

## 인덱스 있는 경우

맨 뒤 목차에서:

```text id="3hyq9v"
쿠버네티스 → 312페이지
```

보고 바로 이동 가능하다.

DB 인덱스도 거의 같은 개념이다.

---

# 2. 인덱스가 없으면 어떻게 찾는가?

예를 들어:

```sql id="g9lm6v"
SELECT * FROM users
WHERE name = 'kim';
```

이 있다고 해보자.

---

# 3. Full Scan

인덱스가 없으면 DB는 보통:

```text id="q3l9f2"
한 줄씩 전부 확인
```

한다.

즉:

```text id="4jlwm5"
kim인가?
아닌가?
kim인가?
아닌가?
```

를 반복한다.

이걸:

```text id="3jlwm6"
Full Table Scan
```

이라고 한다.

---

# 4. 왜 느린가?

데이터가 적으면 괜찮다.

근데:

```text id="0jlwm7"
100만 건
1000만 건
1억 건
```

되면?

전부 순회해야 한다.

즉 시간복잡도 느낌으로 보면:

```text id="mjlwm8"
O(n)
```

에 가깝다.

---

# 5. Index를 만들면?

예를 들어:

```sql id="efp4nm"
CREATE INDEX idx_users_name
ON users(name);
```

를 생성했다고 해보자.

그러면 DB는:

```text id="njlwm9"
name 기준 정렬된 자료구조
```

를 따로 만든다.

---

# 6. 그래서 왜 빨라지는가?

이제 DB는:

```text id="ojlwm0"
처음부터 끝까지 탐색
```

안 해도 된다.

대신:

```text id="pjlwm1"
정렬된 구조에서 빠르게 탐색
```

가능하다.

---

# 7. 보통 B-Tree 사용

대부분 관계형 DB(MySQL/PostgreSQL)는:

```text id="qjlwm2"
B-Tree
```

기반 인덱스를 사용한다.

---

# 8. B-Tree 느낌

대충 이런 느낌이다.

```text id="rjlwm3"
          [M]
        /     \
     [D]      [T]
    /   \     /  \
  ...
```

즉:

```text id="sjlwm4"
정렬된 트리 구조
```

로 데이터를 관리한다.

---

# 9. 왜 빠른가?

예를 들어:

```text id="tjlwm5"
kim
```

을 찾는다고 해보자.

그러면:

```text id="ujlwm6"
절반
→ 절반
→ 절반
```

식으로 범위를 줄여간다.

즉 시간복잡도 느낌으로 보면:

```text id="vjlwm7"
O(log n)
```

수준까지 줄어든다.

---

# 10. 실제 차이

예를 들어:

```text id="wjlwm8"
1억 건 테이블
```

에서:

---

## 인덱스 없음

```text id="xjlwm9"
1억 건 전부 탐색 가능성
```

---

## 인덱스 있음

```text id="yjlwm0"
트리 탐색 몇 번
```

으로 끝날 수 있다.

그래서 성능 차이가 엄청 커진다.

---

# 11. 인덱스는 공짜가 아니다

근데 여기서 중요한 게 있다.

```text id="zjlwm1"
인덱스 많다고 무조건 좋은 건 아님
```

이다.

---

# 12. 왜냐면 추가 저장공간 필요

인덱스는:

```text id="0klwm2"
별도 자료구조
```

를 유지한다.

즉 디스크와 메모리를 더 사용한다.

---

# 13. INSERT가 느려진다

예를 들어:

```sql id="m4g4lj"
INSERT INTO users ...
```

하면:

---

## 원래 데이터 저장

*

## 인덱스도 갱신

해야 한다.

즉:

```text id="1klwm3"
쓰기 비용 증가
```

가 발생한다.

---

# 14. UPDATE/DELETE도 영향

데이터 변경 시:

```text id="2klwm4"
인덱스 재정렬
인덱스 수정
```

이 필요하다.

그래서:

```text id="3klwm5"
읽기 빠름
대신 쓰기 느려짐
```

트레이드오프가 생긴다.

---

# 15. 그래서 아무 컬럼이나 인덱스 걸지 않는다

보통 이런 컬럼에 많이 건다.

---

## WHERE 자주 쓰는 컬럼

```sql id="3f9d1r"
WHERE email = ?
```

---

## JOIN 컬럼

```sql id="52ydar"
user_id
```

---

## ORDER BY 자주 쓰는 컬럼

```sql id="6jlwm7"
created_at
```

---

# 16. 인덱스가 오히려 손해인 경우

예:

```text id="7jlwm8"
성별(M/F)
```

처럼 값 종류가 너무 적으면.

DB 입장에서는:

```text id="8jlwm9"
거의 절반이 M
```

이라 효율이 떨어질 수 있다.

이런 걸:

```text id="9jlwm0"
카디널리티(Cardinality)
```

와 연결해서 설명한다.

---

# 17. Primary Key는 자동 인덱스

예:

```sql id="n6b0me"
id BIGINT PRIMARY KEY
```

면 대부분 DB는 자동으로 인덱스를 생성한다.

왜냐면 PK 조회는 매우 자주 발생하기 때문이다.

---

# 18. DynamoDB에도 Index가 있다

AWS DynamoDB에서도:

```text id="aklwm1"
GSI(Global Secondary Index)
```

개념이 있다.

즉:

```text id="bklwm2"
NoSQL도 결국 빠른 조회를 위해
인덱스 필요
```

하다는 뜻이다.

---

# 19. 실무에서 자주 보는 문제

---

## "조회가 느립니다"

→ 인덱스 확인

---

## "CPU가 높습니다"

→ Full Scan 의심

---

## "INSERT가 너무 느립니다"

→ 인덱스 과다 가능성

---

## "ORDER BY 느립니다"

→ 정렬 컬럼 인덱스 확인

---

# 20. 정리

## Index

빠른 조회를 위한 자료구조

---

## 인덱스 없으면

```text id="cklwm3"
Full Table Scan
```

---

## 인덱스 있으면

```text id="dklwm4"
정렬된 구조 탐색
```

---

## 대표 구조

```text id="eklwm5"
B-Tree
```

---

## 장점

조회 빠름

---

## 단점

```text id="fklwm6"
INSERT
UPDATE
DELETE
```

느려질 수 있음

---

## 핵심 트레이드오프

```text id="gklwm7"
읽기 성능
vs
쓰기 성능
```

---

# 한 줄 핵심

```text id="hklwm8"
인덱스는 데이터를 처음부터 끝까지 찾지 않고,
목차처럼 빠르게 탐색하기 위한 구조다.
```