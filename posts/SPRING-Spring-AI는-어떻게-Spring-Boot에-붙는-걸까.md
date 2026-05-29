---
title: "[SPRING] Spring AI는 어떻게 Spring Boot에 붙는 걸까?"
source: "https://velog.io/@yorange50/SPRING-Spring-AI는-어떻게-Spring-Boot에-붙는-걸까"
published: "2026-05-12T19:44:44.065Z"
tags: ""
backup_date: "2026-05-29T14:52:52.752391"
---


Spring AI를 처음 보면 뭔가 거창해 보인다.
AI 모델을 직접 서버에 올리고, 학습시키고, GPU를 붙이고, 복잡한 인프라를 구성해야 할 것 같지만 꼭 그런 건 아니다.

Spring AI의 핵심은 생각보다 단순하다.

> 외부 AI 모델을 Spring Boot 애플리케이션 안에서 쉽게 호출할 수 있게 해주는 도구

즉, Spring Boot가 AI 모델 자체가 되는 것이 아니라, **AI 모델을 호출하는 백엔드 서버 역할**을 하게 되는 것이다.

---

## 1. Spring AI가 하는 일

일반적인 Spring Boot 애플리케이션은 보통 이런 구조를 가진다.

```text
Controller
  → Service
  → Repository
  → Database
```

사용자가 요청을 보내면 Controller가 받고, Service에서 비즈니스 로직을 처리하고, Repository를 통해 DB에 접근한다.

그런데 AI 기능이 들어가면 구조가 조금 바뀐다.

```text
Controller
  → Service
  → Spring AI
  → AI 모델 API
```

여기서 Spring AI는 OpenAI, Upstage, Ollama 같은 AI 모델을 호출할 수 있도록 도와준다.

개발자가 직접 HTTP 요청을 만들고, API Key를 넣고, JSON을 파싱하는 과정을 줄여주는 것이다.

---

## 2. Spring에 AI를 “이식한다”는 뜻

“Spring에 AI를 이식한다”는 말은 AI 모델을 Spring Boot 안에 직접 넣는다는 뜻이 아니다.

정확히는 이런 의미에 가깝다.

```text
AI 모델 호출 기능을
Spring Boot 서비스 코드 안에
일반 비즈니스 로직처럼 붙인다
```

예를 들어 사용자가 이런 요청을 보낸다고 해보자.

```text
/api/ai/ask?q=스프링 AI가 뭐야?
```

그러면 Spring Boot 서버는 이 질문을 받아서 AI 모델에 전달하고, AI 모델의 답변을 다시 사용자에게 반환한다.

전체 흐름은 다음과 같다.

```text
사용자 요청
  → Spring Controller
  → Spring Service
  → Spring AI ChatClient
  → 외부 AI 모델
  → 응답 반환
```

즉, Spring Boot는 AI 모델과 사용자를 연결해주는 **중간 서버** 역할을 한다.

---

## 3. ChatClient란?

Spring AI에서 가장 기본적으로 많이 쓰는 객체가 `ChatClient`다.

`ChatClient`는 이름 그대로 AI 채팅 모델과 대화하기 위한 클라이언트다.

예를 들어 원래라면 개발자가 직접 이런 일을 해야 한다.

```text
AI API 주소 설정
API Key 설정
요청 body 생성
프롬프트 전달
응답 JSON 파싱
에러 처리
```

그런데 Spring AI를 사용하면 이런 식으로 쓸 수 있다.

```java
chatClient.prompt()
        .user("스프링 AI가 뭐야?")
        .call()
        .content();
```

이 코드의 의미는 단순하다.

```text
AI 모델에게 프롬프트를 보내고
응답 내용을 문자열로 가져온다
```

---

## 4. 의존성 주입으로 사용하는 구조

Spring에서는 필요한 객체를 직접 만들기보다, Spring Container가 관리하는 Bean을 주입받아 사용한다.

Spring AI도 마찬가지다.

```java
@Service
public class AiService {

    private final ChatClient chatClient;

    public AiService(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }

    public String ask(String question) {
        return chatClient.prompt()
                .system("너는 친절한 백엔드 개발 튜터야.")
                .user(question)
                .call()
                .content();
    }
}
```

여기서 중요한 부분은 이 부분이다.

```java
public AiService(ChatClient.Builder builder)
```

`ChatClient.Builder`를 개발자가 직접 만드는 것이 아니라 Spring이 넣어준다.

이것이 **의존성 주입**이다.

쉽게 말하면 이런 느낌이다.

```text
“ChatClient 필요해”
→ Spring이 준비해둔 객체를 넣어줌
→ Service는 그걸 사용함
```

그래서 개발자는 AI 호출에 집중할 수 있다.

---

## 5. Controller로 API 열기

Service에서 AI 호출 로직을 만들었다면, 이제 외부에서 사용할 수 있도록 API를 열어야 한다.

```java
@RestController
@RequestMapping("/api/ai")
public class AiController {

    private final AiService aiService;

    public AiController(AiService aiService) {
        this.aiService = aiService;
    }

    @GetMapping("/ask")
    public String ask(@RequestParam String q) {
        return aiService.ask(q);
    }
}
```

이제 사용자는 다음과 같이 요청할 수 있다.

```bash
curl "http://localhost:8080/api/ai/ask?q=스프링 AI가 뭐야?"
```

그러면 흐름은 이렇게 된다.

```text
사용자 질문
  → AiController
  → AiService
  → ChatClient
  → AI 모델
  → 답변 반환
```

이게 바로 Spring Boot에서 AI 기능을 서빙하는 기본 구조다.

---

## 6. 설정은 application.yml에 둔다

AI 모델을 사용하려면 보통 API Key와 모델명이 필요하다.

이런 설정은 코드에 직접 넣지 않고 `application.yml`에 둔다.

```yaml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
      chat:
        options:
          model: gpt-4o-mini
```

여기서 중요한 부분은 이것이다.

```yaml
api-key: ${OPENAI_API_KEY}
```

API Key를 코드에 직접 쓰지 않고 환경변수로 받는다.

나쁜 예시는 이런 코드다.

```java
String apiKey = "sk-xxxx";
```

이렇게 하면 코드가 GitHub에 올라갔을 때 키가 노출될 수 있다.

좋은 방식은 환경변수를 사용하는 것이다.

```text
코드에는 ${OPENAI_API_KEY}만 작성
실제 키는 실행 환경에서 주입
```

---

## 7. 개발자는 어디까지 만들까?

개발자가 주로 만드는 부분은 다음과 같다.

```text
Controller
Service
AI 호출 로직
프롬프트 구성
응답 가공
설정 파일
```

예를 들면 이런 것들이다.

```text
사용자 질문을 받는 API
AI에게 보낼 프롬프트
AI 응답을 어떤 형태로 반환할지
에러가 났을 때 어떻게 처리할지
API Key를 환경변수로 받을 구조
```

즉, 개발자는 “AI 기능이 있는 백엔드 API”를 만든다.

---

## 8. 인프라 담당자는 뭘 할까?

개발자가 Spring Boot 앱을 만들면, 그 앱은 로컬에서 실행된다.

```text
localhost:8080
```

하지만 실제 서비스에서는 로컬에서만 실행되면 안 된다.

그래서 인프라 담당자는 이 앱을 운영 환경에서 실행 가능하게 만든다.

핵심 작업은 다음과 같다.

```text
애플리케이션 빌드
실행 파일 생성
서버에 배포
환경변수 주입
포트 연결
로그 확인
장애 시 재시작
모니터링 설정
```

즉, 개발자가 만든 AI 기능을 실제 사용자가 접근할 수 있는 서버에 올리는 역할이다.

---

## 9. 배포 흐름을 단순하게 보면

Spring Boot 앱은 보통 빌드하면 `.jar` 파일이 만들어진다.

```bash
./mvnw clean package
```

그러면 `target` 폴더 아래에 실행 가능한 파일이 생긴다.

```text
target/my-ai-service.jar
```

이 파일을 서버에서 실행하면 Spring Boot 앱이 뜬다.

```bash
java -jar my-ai-service.jar
```

운영 환경에서는 여기에 환경변수도 같이 넣는다.

```bash
OPENAI_API_KEY=실제키 java -jar my-ai-service.jar
```

그러면 Spring Boot 앱은 실행될 때 이 값을 읽어서 AI API를 호출할 수 있다.

---

## 10. 전체 역할을 나눠보면

| 구분      | 하는 일                        |
| ------- | --------------------------- |
| 개발자     | Spring AI를 사용해서 AI 호출 로직 구현 |
| 개발자     | Controller로 API 제공          |
| 개발자     | Service에서 프롬프트 구성           |
| 개발자     | API Key를 환경변수로 받을 수 있게 설정   |
| 인프라 담당자 | 애플리케이션을 서버에 배포              |
| 인프라 담당자 | 환경변수 주입                     |
| 인프라 담당자 | 포트, 로그, 모니터링 관리             |
| 인프라 담당자 | 장애 발생 시 재시작 및 운영 관리         |

---

## 11. 핵심은 “AI 모델을 직접 들고 있는 게 아니다”

Spring AI를 쓴다고 해서 Spring Boot가 AI 모델 자체를 품고 있는 것은 아니다.

대부분의 경우 구조는 이렇다.

```text
Spring Boot 서버
  → AI 모델 API 호출
  → 응답 받아서 사용자에게 반환
```

즉, Spring Boot는 AI 모델을 직접 학습하거나 추론하는 서버가 아니라, AI 기능을 서비스에 연결하는 백엔드 서버다.

그래서 Spring AI의 핵심은 다음과 같이 정리할 수 있다.

```text
AI 모델 호출을 Spring 방식으로 쉽게 만들기
```

---

## 12. 한 줄 정리

Spring AI는 AI 모델을 Spring Boot 안에서 쉽게 호출하게 해주는 도구다.
개발자는 `ChatClient`를 Service에 주입받아 AI 호출 로직을 만들고, Controller를 통해 API로 제공한다.
인프라 담당자는 이 Spring Boot 애플리케이션을 서버에 배포하고, API Key 같은 설정값을 안전하게 주입하며, 로그와 장애 대응을 관리한다.

결국 전체 흐름은 이거다.

```text
사용자 요청
  → Spring Boot API
  → Spring AI
  → 외부 AI 모델
  → 응답 반환
```

Spring AI를 이해할 때는 어렵게 생각하지 않아도 된다.

> AI 모델을 Spring Boot 서비스 코드 안에서 일반 API처럼 사용할 수 있게 만든 것

이게 가장 핵심이다.