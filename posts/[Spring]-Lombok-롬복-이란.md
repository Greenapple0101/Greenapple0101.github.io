---
title: "[SPRING] Lombok(롬복)이란?"
source: "https://velog.io/@yorange50/SPRING-Lombok롬복이란"
published: "2026-04-30T01:05:56.502Z"
tags: ""
backup_date: "2026-05-29T14:52:52.782835"
---

Spring이나 Java 프로젝트를 하다 보면 이런 코드를 자주 보게 된다.

```java
@Getter
@Setter
@RequiredArgsConstructor
```

이런 것들이 바로 **Lombok(롬복)**이다.

---

## 1. Lombok이란?

> **반복적인 코드를 자동으로 생성해주는 라이브러리**

자바는 기본적으로 이런 코드를 많이 써야 한다.

```java
public class Board {

    private String title;

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }
}
```

이건 로직이 아니라 거의 “형식적인 코드”다.

그래서 Lombok을 쓰면:

```java
@Getter
@Setter
public class Board {
    private String title;
}
```

→ getter/setter를 자동으로 만들어준다.

---

## 2. 왜 쓰는가?

핵심 이유는 하나다.

> **코드를 줄이고, 가독성을 높이기 위해**

* 반복 코드 제거
* 실수 줄이기
* 핵심 로직에 집중

특히 도메인 클래스에서 효과가 크다.

---

## 3. 자주 쓰는 Lombok 어노테이션

### 1) @Getter / @Setter

```java
@Getter
@Setter
```

→ getter / setter 자동 생성

---

### 2) @RequiredArgsConstructor

```java
@RequiredArgsConstructor
```

→ final 필드 기준 생성자 자동 생성

---

### 3) @NoArgsConstructor

```java
@NoArgsConstructor
```

→ 기본 생성자 생성

---

### 4) @AllArgsConstructor

```java
@AllArgsConstructor
```

→ 모든 필드를 포함한 생성자 생성

---

## 4. Lombok이 실제로 하는 일

중요한 포인트:

> **Lombok은 컴파일 시점에 코드를 “몰래 추가”해준다**

즉, 실제 실행되는 코드는 아래처럼 된다.

```java
@Getter
public class Board {
    private String title;
}
```

→ 컴파일 후에는 사실상:

```java
public class Board {
    private String title;

    public String getTitle() {
        return title;
    }
}
```

이 상태로 돌아간다.

---

## 5. 주의할 점

* IDE에서 Lombok 플러그인 설치 필요
* 없으면 코드가 깨진 것처럼 보일 수 있음
* 과하게 쓰면 내부 구조 이해가 어려워질 수 있음

---

## 한 줄 정리

> Lombok은 “귀찮은 코드(getter, setter, 생성자 등)를 대신 만들어주는 도구”다

---

지금 단계에서 중요한 건

* Lombok을 “마법”처럼 쓰는 게 아니라
* “원래는 어떤 코드가 생략된 건지” 알고 쓰는 것

이거다.

이 감각만 잡으면 나중에 디버깅이나 설계할 때 훨씬 편해진다.
