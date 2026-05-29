---
title: "[SPRING] getter, setter 도대체 뭐야? (처음 보는 사람 기준)"
source: "https://velog.io/@yorange50/SPRING-getter-setter-도대체-뭐야-처음-보는-사람-기준"
published: "2026-04-29T15:08:59.714Z"
tags: ""
backup_date: "2026-05-29T14:52:52.785113"
---

Spring 공부하다 보면 갑자기 이런 코드가 나온다.

```java
private String title;
```

그리고 밑에 이상한 함수 두 개가 붙는다.

```java
public String getTitle() { ... }
public void setTitle(String title) { ... }
```

이게 바로 **getter, setter**다.

---

## 1. 왜 이런 걸 만드는 걸까?

Java에서는 보통 변수 앞에 `private`를 붙인다.

```java
private String title;
```

이 의미는

```text
"밖에서 직접 건드리지 마라"
```

그래서 이렇게 하면 안 된다.

```java
board.title = "제목"; // ❌ 막힘
```

---

## 2. 그래서 우회 통로를 만든다

직접 못 건드리니까
**함수를 통해서만 접근하게 만든다**

---

## 3. getter (값 꺼내는 통로)

```java
public String getTitle() {
    return title;
}
```

사용:

```java
board.getTitle();
```

→ title 값을 꺼내는 역할

---

## 4. setter (값 바꾸는 통로)

```java
public void setTitle(String title) {
    this.title = title;
}
```

사용:

```java
board.setTitle("새 제목");
```

→ title 값을 바꾸는 역할

---

## 5. 왜 이렇게 귀찮게 하냐?

그냥 변수 공개하면 편한데 굳이 막는 이유는 하나다.

```text
"값을 통제하려고"
```

예를 들어

```java
public void setTitle(String title) {
    if (title.length() > 100) {
        throw new RuntimeException("너무 김");
    }
    this.title = title;
}
```

→ 이상한 데이터 막을 수 있음

---

## 6. Spring에서 왜 중요한가

지금 JSON 쓰고 있잖아

```json
{
  "title": "게시글"
}
```

이걸 Spring이 Java 객체로 바꿀 때

```java
setTitle("게시글")
```

이걸 내부적으로 자동 호출한다.

그리고 응답 보낼 때는

```java
getTitle()
```

을 사용해서 값 꺼낸다.

---

## 7. 핵심 정리

```text
getter = 값 꺼내기
setter = 값 바꾸기
```

그리고 더 중요한 한 줄

```text
Spring은 getter/setter로 JSON ↔ 객체를 변환한다
```

---

## 8. 한 줄 결론

getter, setter는 단순한 함수가 아니라

```text
"데이터를 안전하게 다루기 위한 통로"
```

라고 이해하면 된다.
