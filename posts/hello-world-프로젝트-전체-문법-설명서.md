---
title: "hello-world 프로젝트 전체 문법 설명서"
source: "https://velog.io/@yorange50/hello-world-프로젝트-전체-문법-설명서"
published: "2026-05-11T10:41:15.960Z"
tags: ""
backup_date: "2026-05-29T14:52:52.764919"
---


이 문서는 복습 겸 프로젝트의 핵심 파일인 `HelloController`, `HelloService`, `application.properties`, `pom.xml`을 중심으로 **문법 + 동작 원리 + 실무 관점**을 한 번에 설명합니다.

---

## 1) `HelloController` 설명

대상 파일: `src/main/java/com/osckorea/hello_world/controller/HelloController.java`
현재 코드의 실제 package는 `com.osckorea.hello_world`입니다.

### 원문 코드

```java
package com.osckorea.hello_world;

import java.util.Map;
import com.osckorea.hello_world.service.HelloService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    private final HelloService helloService;

    public HelloController(HelloService helloService) {
        this.helloService = helloService;
    }

    @GetMapping("/hello")
    public String hello() {
        return helloService.getHelloMessage();
    }

    @GetMapping("/version")
    public Map<String, String> version() {
        return helloService.getVersionInfo();
    }
}
```

### 문법/구성 요소 설명

- `package ...;`
  - 클래스의 네임스페이스입니다.
  - 폴더 구조와 보통 맞춰서 관리합니다.

- `import ...;`
  - 다른 패키지의 타입을 현재 파일에서 사용하기 위해 가져옵니다.
  - `Map`, `HelloService`, `GetMapping`, `RestController`를 사용 중입니다.

- `@RestController`
  - 스프링 MVC의 컨트롤러임을 나타내는 애노테이션입니다.
  - 메서드 반환값이 기본적으로 HTTP 응답 본문(body)으로 직렬화됩니다.

- `private final HelloService helloService;`
  - 의존성(서비스)을 필드로 보관합니다.
  - `final`은 한 번 주입된 뒤 변경하지 않음을 보장합니다.

- 생성자 주입
  - `public HelloController(HelloService helloService) { ... }`
  - 스프링이 `HelloService` 빈을 찾아 자동 주입합니다.
  - 실무에서 가장 권장되는 DI 방식입니다.

- `@GetMapping("/hello")`
  - HTTP GET `/hello` 요청을 해당 메서드에 매핑합니다.
  - 반환 타입이 `String`이라 plain text 응답으로 나갑니다.

- `@GetMapping("/version")`
  - HTTP GET `/version` 요청을 처리합니다.
  - `Map<String, String>` 반환은 JSON 오브젝트로 직렬화됩니다.

---

## 2) `HelloService` 설명

대상 파일: `src/main/java/com/osckorea/hello_world/service/HelloService.java`

### 원문 코드

```java
package com.osckorea.hello_world.service;

import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class HelloService {

    private final String appName;
    private final String appVersion;

    public HelloService(
            @Value("${app.name:springboot-hello}") String appName,
            @Value("${app.version:1.0.0}") String appVersion) {
        this.appName = appName;
        this.appVersion = appVersion;
    }

    public String getHelloMessage() {
        return "Hello World";
    }

    public Map<String, String> getVersionInfo() {
        return Map.of(
                "app", appName,
                "version", appVersion
        );
    }
}
```

### 문법/구성 요소 설명

- `@Service`
  - 비즈니스 로직 계층 컴포넌트임을 나타냅니다.
  - 스프링 컨테이너가 빈으로 등록합니다.

- `@Value("${app.name:springboot-hello}")`
  - 프로퍼티 값을 주입합니다.
  - 문법: `${키:기본값}`
    - `app.name` 키가 있으면 그 값을 사용
    - 없으면 `springboot-hello`를 기본값으로 사용

- `@Value("${app.version:1.0.0}")`
  - 같은 패턴으로 버전 값 주입.

- `Map.of(...)`
  - 자바 9+ 불변 Map 생성 문법.
  - 현재 응답 JSON의 key-value를 간결하게 구성합니다.

### 실무 포인트

- 설정값을 코드 하드코딩 대신 프로퍼티에서 받아오면 환경(dev/stage/prod) 전환이 쉬워집니다.
- `@Value` 대신 규모가 커지면 `@ConfigurationProperties`로 묶는 방식이 유지보수에 더 유리합니다.

---

## 3) `application.properties` 설명

대상 파일: `src/main/resources/application.properties`

### 원문

```properties
spring.application.name=hello-world
app.name=springboot-hello
app.version=1.0.0
```

### 문법 설명

- 기본 형식: `key=value`
- 스프링은 `application.properties`를 기본 설정 파일로 자동 로드합니다.
- 현재 키 의미:
  - `spring.application.name`
    - 스프링 애플리케이션 이름(로그/액추에이터 등에서 활용 가능)
  - `app.name`
    - 커스텀 키, `HelloService`에서 `@Value`로 사용
  - `app.version`
    - 커스텀 버전 키, `@Value`로 사용

### 자주 쓰는 확장 문법

- 공백 포함 값:
  - `my.message=hello world`
- 프로파일별 파일:
  - `application-dev.properties`
  - `application-prod.properties`
- 환경변수 오버라이드:
  - 예: `APP_NAME=myapp` 형태로 실행 환경에서 덮어쓰기 가능(스프링 relaxed binding 규칙 적용)

---

## 4) `pom.xml` 설명 (Maven 핵심)

대상 파일: `pom.xml`

`pom.xml`은 Maven 프로젝트의 빌드/의존성/플러그인 설정 중심 파일입니다.

### 4-1. 최상위 구조

- `<project ...>`
  - POM 문서 루트
  - XML namespace와 schema 위치를 선언

- `<modelVersion>4.0.0</modelVersion>`
  - POM 모델 버전(거의 고정적으로 4.0.0 사용)

### 4-2. 부모 POM

- `<parent>`
  - `spring-boot-starter-parent`를 부모로 지정
  - 효과:
    - 스프링 부트 권장 dependency/plugin 버전 관리
    - 기본 빌드 설정 상속

### 4-3. 프로젝트 좌표(Artifact Coordinates)

- `<groupId>com.osckorea</groupId>`
- `<artifactId>hello-world</artifactId>`
- `<version>0.0.1-SNAPSHOT</version>`

이 3개가 아티팩트 식별자입니다.
형식: `groupId:artifactId:version`

### 4-4. 메타데이터

- `<name>`, `<description>`, `<url>`, `<licenses>`, `<developers>`, `<scm>`
  - 배포/문서화/오픈소스 관리 시 유용
  - 현재는 빈 값 위주로 초기 템플릿 상태

### 4-5. properties

- `<properties><java.version>21</java.version></properties>`
  - 빌드/플러그인에서 공통으로 참조하는 속성
  - 현재 프로젝트 타겟 자바 버전 21

### 4-6. dependencies

- `spring-boot-starter-webmvc`
  - Spring MVC 웹 애플리케이션 핵심 의존성

- `spring-boot-devtools` (`runtime`, `optional`)
  - 개발 편의(자동 재시작 등)
  - 운영 배포 필수 의존성은 아님

- `lombok` (`optional`)
  - 보일러플레이트 코드 감소용
  - 컴파일 시 annotation processor로 주로 동작

- `spring-boot-starter-webmvc-test` (`test`)
  - 테스트 스코프에서만 사용되는 웹 테스트 의존성

### Maven scope 문법 요약

- `compile` (기본값): 컴파일/실행/테스트 모두 사용
- `runtime`: 실행 시 필요, 컴파일 시는 불필요
- `test`: 테스트 코드에서만 사용
- `provided`: 런타임 제공(예: 서버가 제공), 패키징 제외
- `system`: 로컬 파일 직접 지정(권장되지 않음)

### 4-7. build/plugins

- `spring-boot-maven-plugin`
  - `repackage`로 실행 가능한 fat jar 생성
  - 현재 설정은 lombok을 최종 산출물에서 제외

- `maven-compiler-plugin`
  - 컴파일 단계 제어
  - `executions`로 `compile`, `test-compile` 각각 명시
  - `annotationProcessorPaths`에 lombok 등록하여 애노테이션 처리 가능하게 설정

### plugin execution 문법

- `<executions>` 안에 여러 `<execution>` 정의 가능
- 각 execution은:
  - `<id>`: 식별자
  - `<phase>`: Maven 라이프사이클 단계
  - `<goals>`: 실행할 goal
  - `<configuration>`: 해당 실행의 세부 옵션

---

## 5) 실행 흐름 한 번에 보기

1. 앱 시작 시 `HelloWorldApplication.main()`이 스프링 부트를 부팅
2. 컴포넌트 스캔으로 `HelloController`, `HelloService` 빈 등록
3. `HelloService` 생성 시 `application.properties` 값이 `@Value`로 주입
4. `/hello` 요청 -> `HelloController.hello()` -> `"Hello World"` 반환
5. `/version` 요청 -> `HelloController.version()` -> `app/version` JSON 반환

---

## 6) 자주 물어보는 문법 포인트 정리

- 애노테이션은 클래스/메서드/파라미터에 부가정보를 붙여 프레임워크 동작을 바꾼다.
- `final` 필드는 생성자에서 한 번만 할당 가능해 불변성 관리에 유리하다.
- `Map<String, String>` 제네릭은 key/value 타입을 컴파일 타임에 제한한다.
- 프로퍼티 `${key:default}`는 운영 환경에서 키 누락 시 앱 안정성에 도움이 된다.
- Maven은 `pom.xml` 중심으로 의존성과 빌드 파이프라인을 선언적으로 관리한다.

---

## 7) 실무 개선 제안 (선택)

- 컨트롤러 package를 파일 경로(`...controller`)와 정확히 일치시키기
- `@Value` 다수가 생기면 `@ConfigurationProperties`로 설정 객체 분리
- `pom.xml`의 빈 메타데이터(`description`, `licenses`, `developers`) 채우기
- API 스펙 문서화를 위해 SpringDoc(OpenAPI) 추가 검토