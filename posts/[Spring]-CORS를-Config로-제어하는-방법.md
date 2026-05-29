---
title: "[SPRING] CORS를 Config로 제어하는 방법"
source: "https://velog.io/@yorange50/SPRING-CORS를-Config로-제어하는-방법"
published: "2026-04-30T01:21:33.071Z"
tags: ""
backup_date: "2026-05-29T14:52:52.781953"
---

프론트엔드와 백엔드를 따로 실행하면 CORS 문제가 자주 발생한다.

예를 들어 지금 구조는 이렇게 나뉘어 있다.

```text
프론트엔드: http://localhost:5173
백엔드: http://localhost:8080
```

둘 다 `localhost`이지만 포트가 다르다.

브라우저 입장에서는 서로 다른 출처라고 판단한다.

그래서 프론트에서 백엔드 API를 호출하면 CORS 에러가 발생할 수 있다.

---

## 1. CORS란?

CORS는 쉽게 말하면

> 다른 출처에서 오는 요청을 허용할지 말지 정하는 브라우저 보안 정책

이다.

백엔드 API 서버가 아무 설정도 하지 않으면 브라우저가 요청을 막을 수 있다.

즉, 서버가 죽은 것도 아니고 API 로직이 틀린 것도 아닌데 브라우저에서 차단되는 상황이 생긴다.

---

## 2. 간단한 방법: Controller에 @CrossOrigin 붙이기

가장 간단한 방법은 컨트롤러에 직접 허용하는 것이다.

```java
@CrossOrigin(origins = "http://localhost:5173")
@RestController
public class BoardController {

}
```

이렇게 하면 해당 컨트롤러에 대해서 프론트 주소의 요청을 허용할 수 있다.

하지만 컨트롤러가 많아지면 매번 붙여야 해서 관리가 불편해진다.

---

## 3. 더 깔끔한 방법: Config로 CORS 제어하기

실무에서는 CORS 설정을 따로 Config 클래스로 빼는 경우가 많다.

예를 들어 `config` 패키지를 만들고 `CorsConfig.java` 파일을 만든다.

```text
src/main/java/com/board/api/config/CorsConfig.java
```

---

## 4. CorsConfig 코드

```java
package com.board.api.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class CorsConfig {

    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {

            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/**")
                        .allowedOrigins("http://localhost:5173")
                        .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                        .allowedHeaders("*");
            }
        };
    }
}
```

---

## 5. 코드 해석

### @Configuration

```java
@Configuration
```

이 클래스가 Spring 설정 클래스라는 뜻이다.

즉, 일반 로직 클래스가 아니라 Spring 설정을 담당하는 클래스다.

---

### @Bean

```java
@Bean
public WebMvcConfigurer corsConfigurer()
```

Spring이 이 설정 객체를 관리하도록 등록한다.

---

### addMapping

```java
registry.addMapping("/**")
```

모든 API 경로에 CORS 설정을 적용한다는 뜻이다.

예를 들어 아래 요청들이 모두 포함된다.

```text
/boards
/boards/1
/api/boards
```

---

### allowedOrigins

```java
.allowedOrigins("http://localhost:5173")
```

이 주소에서 오는 요청을 허용한다는 뜻이다.

즉, Vite 프론트 서버에서 오는 요청을 허용한다.

---

### allowedMethods

```java
.allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
```

허용할 HTTP 메서드를 지정한다.

게시판 CRUD에서는 보통 아래 메서드가 필요하다.

```text
GET     조회
POST    생성
PUT     수정
DELETE  삭제
OPTIONS 사전 요청
```

여기서 `OPTIONS`는 브라우저가 실제 요청을 보내기 전에 “이 요청 보내도 되나요?”라고 확인하는 요청이다.

이걸 preflight 요청이라고 한다.

---

### allowedHeaders

```java
.allowedHeaders("*")
```

요청 헤더를 허용한다는 뜻이다.

개발 단계에서는 보통 전체 허용으로 둔다.

---

## 6. Controller에 @CrossOrigin을 붙이는 방식과 차이

### Controller 방식

```java
@CrossOrigin(origins = "http://localhost:5173")
```

장점은 빠르고 간단하다.

단점은 컨트롤러마다 설정이 흩어진다.

---

### Config 방식

```java
@Configuration
public class CorsConfig { ... }
```

장점은 CORS 설정을 한 곳에서 관리할 수 있다.

단점은 처음에는 코드가 조금 더 길어 보인다.

---

## 7. 정리

CORS 설정은 두 가지 방식으로 할 수 있다.

```text
1. @CrossOrigin으로 Controller에서 직접 허용
2. CorsConfig 클래스로 전역 설정
```

작은 테스트에서는 `@CrossOrigin`을 써도 된다.

하지만 API가 많아지고 프론트와 백엔드를 계속 연결해야 한다면 Config로 분리하는 방식이 더 깔끔하다.

이번 게시판 프로젝트에서는 프론트가 `localhost:5173`, 백엔드가 `localhost:8080`에서 실행되기 때문에 Config에서 `http://localhost:5173`을 허용해주면 된다.
