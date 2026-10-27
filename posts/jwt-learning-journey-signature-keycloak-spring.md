---
title: "[JWT 학습 회고] 구조를 읽는 것에서 API의 검증과 인가까지"
topic: "web"
category: "SECURITY"
published: "2026-10-27"
tags: "JWT, 학습 회고, Keycloak, Spring Security, 서명, JWKS, 인증, 인가"
---

JWT를 처음부터 교재 순서대로 공부한 것은 아니었다. 프로젝트에서 JWT를 먼저 접했고, 연동 흐름을 이해하다 막히면 토큰 자체의 구조와 서명 원리로 돌아갔다. 그다음 다시 Keycloak과 API가 토큰을 발급하고 검증하는 과정에 연결했다.

```text
프로젝트에서 JWT를 접함
→ Header·Payload·Signature 구조로 돌아감
→ 변조·서명·키의 의미를 질문함
→ Keycloak과 API의 검증 과정에 다시 연결함
```

이 글은 학습 회고에 정리한 날짜와 질문을 바탕으로 그 흐름을 기록한 것이다. 개념을 공부한 것, 코드·설정과 연결한 것, 직접 실행해 검증한 결과는 구분한다.

## 1. 실제로 공부한 순서

| 시기 | 질문과 학습 내용 | 공부의 초점 |
|---|---|---|
| 2025년 11월 | “JWT 토큰이 뭐야?”라는 질문으로 시작했다. Django 구현 맥락에서 JWT를 접하고, 배포 설정의 `JWT_SECRET`, 만료시간, 프런트엔드와 백엔드 사이의 전달 위치를 질문했다. | JWT가 무엇이고 실제 서비스의 어디에 사용되는가 |
| 2026년 9월 15일 | JWT를 Keycloak·OIDC·SAML과 함께 학습 주제로 다뤘다. | 인증 시스템에서 JWT가 맡는 역할 |
| 2026년 10월 1일 | FinLab 프로젝트를 기준으로 인증·인가, OAuth/OIDC, PKCE, Access Token/JWT, `iss`·`sub`·`aud`, Keycloak 설정과 API 검증을 연결했다. | 전체 시스템에서 토큰이 발급되고 사용되는 위치 |
| 2026년 10월 14일 | “JWT에 대한 모든 것”을 공부하면서 게이트웨이와 Keycloak을 잠시 빼고 JWT 자체부터 살펴봤다. “변조?”라고 다시 질문하고 실무 사례도 함께 봤다. | 구조·Claim·변조·서명의 의미 |
| 2026년 10월 15일 | Keycloak의 토큰 발급을 질문하고 대칭·비대칭 방식과 JWKS로 범위를 넓혔다. | 누가 어떤 키로 생성하고 검증하는가 |
| 이후 OAuth 복습 | 세션 쿠키 없이 API를 이용하는 구조를 질문하며 토큰 보관과 전달을 다시 정리했다. | 브라우저가 받은 Access Token을 API에 제출하는 방법 |

특히 10월 14~15일에는 전체 연동 설명에서 잠시 벗어나 JWT의 구조와 서명을 집중적으로 공부했다. 시스템의 큰 흐름을 먼저 보고, 이해되지 않는 개념을 더 작은 단위로 분리해 다시 연결한 셈이다.

## 2. 긴 문자열을 세 부분으로 나누어 읽었다

처음에는 JWT가 하나의 긴 문자열처럼 보였다. 이를 나누어 보면서 각 부분이 무엇을 담는지 공부했다.

```text
Header.Payload.Signature
```

| 부분 | 공부한 내용 |
|---|---|
| Header | 알고리즘과 키 식별자 등 토큰 처리에 관한 정보 |
| Payload | 사용자·발급자·만료·권한 등 개별 Claim |
| Signature | 내용의 무결성과 서명 검증에 사용하는 값 |

여기서 다룬 것은 흔히 보는 **서명된 JWT의 Compact 표현**이다. JWT에는 암호화된 JWE 형태도 있으므로 모든 JWT가 언제나 세 부분이라고 일반화하지 않는다. [RFC 7519 — JWT](https://www.rfc-editor.org/rfc/rfc7519.html)

이 단계에서 배우려던 것은 “토큰 안에 무엇이 적혀 있는가?”였다. 다음 단계에서는 그 내용을 읽는 것과 믿는 것이 어떻게 다른지 질문하게 됐다.

## 3. Claim 이름을 API의 검증 이유와 연결했다

Payload에 사용자 정보가 있다는 설명만으로는 요청 흐름이 충분히 이해되지 않았다. 각 Claim이 무엇을 뜻하고, API가 왜 이를 검사해야 하는지 연결해서 살펴봤다.

| Claim | 이해한 의미 | 프로젝트 흐름에서 연결한 질문 |
|---|---|---|
| `iss` | 발급자 | 신뢰하는 Keycloak Realm에서 발급했는가? |
| `sub` | 토큰이 나타내는 주체 | 이 사용자를 업무 시스템의 사용자와 어떻게 연결할 것인가? |
| `aud` | 토큰의 수신 대상 | 이 토큰은 어느 클라이언트나 API를 대상으로 발급됐는가? |
| `exp` | 만료 시각 | 현재도 사용할 수 있는가? |
| `iat` | 발급 시각 | 언제 발급됐는가? |
| `nbf` | 사용 가능 시작 시각 | 아직 받아들이면 안 되는 시점은 아닌가? |
| 역할 Claim | 부여된 역할 정보 | 이 API의 작업에 필요한 권한으로 어떻게 해석할 것인가? |

특히 `sub`와 `aud`는 구분해야 했다. `sub`는 주체이고 `aud`는 수신 대상이다. 사용자 식별자를 업무 데이터와 연결할 때는 발급자 `iss`의 범위도 함께 고려한다. [RFC 7519 §4.1](https://www.rfc-editor.org/rfc/rfc7519.html#section-4.1)

`aud`를 단순히 “FinAccess용인가, FinAdmin용인가?”로만 기억하는 것도 부족했다. **ID Token에서는 인증 결과를 받는 Client가 대상이고, Access Token에서는 접근하려는 API 등 자원의 대상이 중요하다.** 같은 발급자의 토큰이라고 모든 API에서 받아들이는 것은 아니다. [OIDC의 ID Token 정의](https://openid.net/specs/openid-connect-core-1_0.html#IDToken), [JWT Audience](https://www.rfc-editor.org/rfc/rfc7519.html#section-4.1.3)

Claim 이름을 외우는 데서 “우리 API가 이 값을 왜 검사해야 하지?”로 질문이 바뀌었다.

## 4. “변조하면?”이라는 질문으로 서명을 이해했다

Payload의 역할 정보를 USER에서 ADMIN으로 바꾸면 어떻게 될까? 이 사례를 통해 다음 두 가지를 구분했다.

```text
토큰 내용을 읽거나 바꾸는 것
≠
서버가 그 토큰을 유효하다고 받아들이는 것
```

서명된 JWT의 Payload는 일반적으로 디코딩해서 읽을 수 있다. 이것은 내용을 암호화해 숨기는 것과 다르다. Payload를 바꾼 뒤 다시 인코딩할 수도 있지만, 원래 서명을 그대로 붙이면 변경된 내용과 서명이 맞지 않는다. 올바르게 검증하는 서버는 이를 받아들이지 않아야 한다. [RFC 7519](https://www.rfc-editor.org/rfc/rfc7519.html), [JWS — RFC 7515](https://www.rfc-editor.org/rfc/rfc7515.html)

그래서 **서명을 검증하기 전의 Payload를 신뢰해서 권한을 판단하면 안 된다.** 토큰을 디코딩해 ADMIN이 보인다는 사실과, 신뢰하는 키로 검증된 권한 정보라는 사실은 다르다.

이 시점부터 공부의 초점이 “무슨 내용이 적혀 있는가?”에서 “왜 그 내용을 믿을 수 있는가?”로 옮겨갔다. 다만 변조 사례의 원리를 공부한 것과, 실제 토큰을 변조해 API의 거절 응답까지 확인한 실행 결과는 구분해서 기록한다.

## 5. 대칭·비대칭 방식과 JWKS로 연결했다

서명이 필요하다는 점을 이해한 다음에는 “누가 만들고, 누가 어떤 키로 검증하는가?”를 질문했다.

| 방식 | 생성과 검증 | 키를 가진 주체의 차이 |
|---|---|---|
| 공유 비밀키를 사용하는 HMAC | 같은 비밀키로 MAC을 생성하고 검증 | 검증용 비밀키를 가진 서버도 MAC을 생성할 수 있음 |
| 비대칭 서명 | 개인키로 서명하고 대응하는 공개키로 검증 | 검증자는 공개키만으로 개인키의 서명을 만들 수 없음 |

학습에서 흔히 “대칭 서명”이라고 부르는 방식은 정확히는 공유 비밀키 기반의 MAC이다. 처음 접한 `JWT_SECRET` 설정도 어떤 알고리즘과 라이브러리에서 사용하는지 확인해야 하며, 모든 JWT 시스템이 같은 공유 비밀키를 쓰는 것은 아니다. [JWS의 서명·MAC 설명](https://www.rfc-editor.org/rfc/rfc7515.html)

Keycloak의 비대칭 서명 구성을 기준으로 연결한 흐름은 다음과 같다.

```text
Keycloak
  → 개인키로 토큰 서명

검증하도록 구성한 게이트웨이 / Spring Boot API
  → 신뢰하는 발급자의 공개키로 서명 검증

JWKS
  → 서명 검증에 사용할 공개키 목록 제공
```

JWKS는 키 집합의 JSON 표현이다. 이 비대칭 서명 구성에서는 검증용 공개키를 얻는 데 사용한다. 공개키를 가져왔다는 사실만으로 끝나는 것은 아니며, 신뢰하는 발급자의 키인지 확인하고 서명·만료·대상 등 필요한 조건을 검사해야 한다. [RFC 7517 — JWK](https://www.rfc-editor.org/rfc/rfc7517.html), [Spring JWT Resource Server](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html)

프로젝트 학습 메모에서는 게이트웨이를 APISIX로, 관련 대화에서는 API7이라는 이름으로 다뤘다. 회고에서는 이를 같은 명칭으로 합치지 않고 구분한다. 실제 제품·설정과 누가 어느 검증을 수행하는지는 해당 구현을 확인해야 한다.

이 단계에서 JWT의 서명을 토큰 내부의 한 부분으로만 보던 관점이, **발급 서버와 검증 서버 사이의 키와 신뢰 관계**로 넓어졌다.

## 6. 다시 API 요청과 Spring Security로 돌아왔다

토큰 자체를 공부한 뒤에는 다시 요청 흐름에 붙여 봤다.

```text
브라우저가 Access Token 보유
    ↓
Authorization: Bearer ... 로 API 요청
    ↓
게이트웨이와 백엔드가 각자의 설정에 따라 토큰 검증
    ↓
검증된 주체와 권한 확인
    ↓
업무 인가 규칙에 따라 요청 처리
```

업무 API에는 Access Token을 보내고, ID Token은 클라이언트가 인증 결과를 확인하는 데 사용한다. Refresh Token은 새 Access Token을 요청하는 용도로 구분했다. [OIDC Core](https://openid.net/specs/openid-connect-core-1_0.html), [OAuth 2.0 — RFC 6749](https://www.rfc-editor.org/rfc/rfc6749.html)

Spring 쪽에서는 다음 구성요소를 각 책임에 연결했다. 이 표는 학습한 역할을 정리한 것이며 내부 호출 단계를 모두 나열한 것은 아니다.

| 구성 | 연결해서 공부한 역할 |
|---|---|
| `BearerTokenAuthenticationFilter` | 요청에서 Bearer Token을 추출하고 인증 처리를 위임 |
| `JwtDecoder` / `NimbusJwtDecoder` | JWT를 디코딩하고 설정된 서명·Claim 검증 수행 |
| `OAuth2TokenValidator` | Audience와 필수 Claim 등 필요한 검증 조건 구성 |
| `JwtAuthenticationConverter` | 검증된 JWT를 인증 정보와 Authority로 변환 |
| `requestMatchers` | 인가 규칙을 적용할 요청 경로 등의 조건 선택 |
| `hasRole` 등 | 선택된 요청에 필요한 권한 조건 적용 |
| `SessionCreationPolicy.STATELESS` | Spring Security가 인증 상태를 HTTP 세션에 저장·조회하지 않도록 구성 |

Keycloak의 역할 Claim이 자동으로 Spring의 Role과 같아지는 것은 아니다. Claim의 구조와 API의 인가 규칙에 맞는 권한 변환이 필요하다. 또한 서명·주요 Claim의 검증이 성공했다는 것과 해당 사용자가 그 게시글을 수정할 수 있다는 것은 별도의 판단이다. [Spring Security의 JWT 인증·권한 변환](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html)

`STATELESS`도 시스템 전체에서 쿠키와 세션을 없애는 뜻은 아니다. Spring Security의 HTTP 세션 사용 정책이며, Keycloak의 로그인 세션이나 SSO에 쓰는 쿠키는 별도로 이해해야 한다. [Spring Security의 Stateless 인증](https://docs.spring.io/spring-security/reference/servlet/authentication/session-management.html#configure-stateless-authentication)

## 7. 공부하면서 반복한 방식

**큰 구조를 먼저 보고, 막히는 개념을 분리했다.** FinLab·Keycloak·게이트웨이 흐름을 먼저 접했지만, 이해되지 않는 부분은 주변 시스템을 잠시 빼고 JWT 자체부터 다시 공부했다.

**정의 다음에는 상황을 물었다.** Payload를 바꾸면 어떻게 되는지, 공개키로 무엇을 검증하는지, 이미 토큰이 있는데 세션 쿠키가 왜 필요한지 질문했다. 용어를 외우는 것보다 동작 사이의 연결을 이해하려 했다.

**설명이 이어지지 않으면 더 작은 단위로 돌아갔다.** 더 쉬운 비유, 요청 흐름, 시퀀스 다이어그램 등으로 표현을 바꾸면서 누가 무엇을 보내고 검증하는지 확인했다.

개념 설명과 프로젝트 맥락을 오가며, 질문으로 이해되지 않는 연결을 좁혀 간 과정이었다.

## 8. 학습한 내용과 실행한 결과를 나누어 기록한다

현재 회고에 담을 수 있는 학습 내용은 다음과 같다.

> JWT의 Header·Payload·Signature 구조와 주요 Claim인 `iss`, `sub`, `aud`, `exp`를 학습했다. Payload 변조 사례를 통해 디코딩과 서명 검증의 차이를 살펴보고, 공유 비밀키 기반 HMAC과 비대칭 서명, Keycloak의 공개키·JWKS를 이용한 검증 흐름을 공부했다. 이후 Access Token·ID Token·Refresh Token의 용도를 구분하고, Bearer 헤더를 통한 API 호출과 Spring Security의 JWT 검증·권한 처리 과정에 연결해 정리했다.

회고에 정리된 범위에서는 코드와 설정의 연결을 공부했다는 것과, 모든 항목을 독립적으로 구현하고 재실행했다는 것은 다르다. **토큰 변조·만료·권한 오류 테스트를 직접 수행해 모두 검증했다고 기록하지 않는다.** 자동 갱신, 토큰 즉시 무효화, Refresh Token Rotation도 이번 학습 회고에서 구현 완료 항목으로 다루지 않는다.

직접 수행한 실험은 이후 요청·응답과 확인한 조건을 남겨 별도의 실행 기록으로 추가할 수 있다. 지금까지 이어 온 질문의 축은 다음과 같다.

```text
내용을 읽는 법
→ 내용을 신뢰하는 법
→ 그 신뢰를 API 접근 판단에 사용하는 법
```

## 함께 읽기

- [OAuth·OIDC의 역할과 Grant](oauth-oidc-keycloak-01-foundations.html)
- [Authorization Code와 PKCE 로그인 흐름](oauth-oidc-keycloak-02-code-pkce.html)
- [토큰과 JWT·Claim·Scope·Role](oauth-oidc-keycloak-03-tokens-jwt.html)
- [Spring API의 JWT 검증과 JWKS·Discovery](oauth-oidc-keycloak-04-resource-server.html)
- [세션 쿠키·SSO와 Keycloak 실습](oauth-oidc-keycloak-05-sso-practice.html)
