---
title: "[OAuth·OIDC·Keycloak 1] 인증·인가와 OAuth의 역할, Grant 이해하기"
topic: "web"
category: "SECURITY"
published: "2026-10-27"
tags: "OAuth, OIDC, Keycloak, 인증, 인가, Grant"
---

OAuth와 OIDC를 공부할 때 먼저 연결해야 할 것은 로그인 버튼부터 API 응답까지의 흐름이다.

```text
사용자 로그인
→ 앱이 토큰을 받음
→ 앱이 토큰으로 API를 호출
→ API가 토큰과 권한을 확인
→ 데이터 응답
```

이 시리즈는 가상의 브라우저 앱 **FinAccess**, 인증 제공자 **Keycloak**, 보호된 API를 제공하는 **Spring Boot**를 예시로 사용한다. FinAccess가 브라우저에서 직접 토큰을 받아 API에 제출하며, API는 애플리케이션의 서버 로그인 세션 쿠키 대신 Bearer Token으로 요청을 인증하는 학습 구조이다.

이 구조는 가능한 설계 중 하나이다. “세션 쿠키를 사용하지 않는다”는 조건만으로 모든 구현 방식이 하나로 결정되는 것은 아니다. 브라우저용 Keycloak 연동에서도 클라이언트가 직접 토큰을 사용하는 방식을 제공한다. [Keycloak JavaScript adapter](https://www.keycloak.org/securing-apps/javascript-adapter)

## 1. OAuth가 필요한 이유

사진 인화 앱이 사용자의 사진 저장 서비스에서 사진을 가져와야 한다고 생각해 보자.

인화 앱에 사진 서비스의 비밀번호를 알려주면 앱이 사용자 계정으로 너무 많은 일을 할 수 있다. 대신 사진 서비스가 **사진을 읽을 수 있는 제한된 권한**을 나타내는 Access Token을 발급하면, 인화 앱은 그 토큰으로 허용된 API를 이용할 수 있다.

OAuth 2.0은 애플리케이션이 사용자 대신, 또는 자신의 자격으로 제한된 서비스 접근 권한을 얻는 **인가 프레임워크**이다. 비밀번호 자체를 공유하는 대신 허용된 범위의 접근 권한을 전달한다는 관점이 출발점이다. [RFC 6749](https://www.rfc-editor.org/rfc/rfc6749.html)

## 2. 인증과 인가는 다른 질문이다

| 구분 | 확인하는 질문 | 예시 |
|---|---|---|
| 인증 — Authentication | 누구인가? | Keycloak에서 사용자 신원 확인 |
| 인가 — Authorization | 이 작업을 해도 되는가? | USER가 관리자 API를 사용할 수 있는지 확인 |

로그인에 성공한 사용자가 모든 API를 사용할 수 있는 것은 아니다. 일반 사용자가 인증을 마쳤더라도 관리자 API에 필요한 권한이 없다면 요청은 거부되어야 한다.

OAuth 자체를 곧바로 로그인 규격으로 외우면 Access Token과 인증 결과를 혼동하기 쉽다. **OAuth 2.0 위에 사용자 인증을 위한 규칙을 추가한 것이 OIDC, 즉 OpenID Connect이다.** OIDC는 클라이언트가 인증 결과를 확인할 수 있도록 ID Token 등을 정의한다. 이 시리즈의 Keycloak 로그인은 OIDC 로그인으로 이해한다. [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html)

## 3. OAuth의 네 가지 역할

| 역할 | 하는 일 | 학습 예시 |
|---|---|---|
| Resource Owner | 보호된 자원의 접근을 허용할 수 있는 주체 | 사용자 |
| Client | 토큰을 얻고 보호된 API를 이용하는 앱 | FinAccess 브라우저 앱 |
| Authorization Server | 인증·인가 절차를 거쳐 토큰을 발급하는 서버 | Keycloak |
| Resource Server | 토큰으로 보호된 자원과 기능을 제공하는 서버 | Spring Boot API |

Client는 반드시 백엔드 서버를 뜻하지 않는다. OAuth에서 어떤 역할을 수행하는지 나타내는 용어이며, 브라우저 앱이나 서버 앱 모두 Client가 될 수 있다. 이번 예시에서는 **브라우저 안에서 실행되는 FinAccess 코드가 Client**이다. [RFC 6749 §1.1](https://www.rfc-editor.org/rfc/rfc6749.html#section-1.1)

OIDC 관점에서 Keycloak은 인증 제공자인 OpenID Provider 역할도 맡는다. 흔히 말하는 IdP, 즉 Identity Provider는 사용자의 신원을 확인하는 인증 제공자를 가리키는 표현이다.

### Keycloak, 게이트웨이, Spring Boot의 책임

```text
FinAccess ↔ Keycloak
FinAccess → Spring Boot API
```

처음에는 이 구조로 토큰 발급과 API 호출을 분리해 이해한다.

Keycloak은 사용자 인증과 토큰 발급을 담당한다. Spring Boot는 보호된 API를 제공하고 요청의 토큰과 업무 권한을 확인한다. **토큰을 받는 상대와 그 토큰으로 서비스를 이용하는 상대가 다르다.**

게이트웨이를 추가하는 학습 단계에서는 다음과 같이 확장할 수 있다.

```text
FinAccess ↔ Keycloak
FinAccess → API7 같은 API 게이트웨이 → Spring Boot API
```

이때 게이트웨이가 요청 검사와 전달 중 어떤 책임을 맡을지는 별도로 정하는 설계 사항이다. API 게이트웨이는 OAuth의 기본 네 역할에 추가로 배치할 수 있는 구성요소이며, OAuth를 사용하기 위한 필수 요소는 아니다.

## 4. Grant는 Access Token을 얻는 방식이다

Grant를 처음 공부할 때는 “어떤 방식으로 Access Token을 얻는가?”라는 질문으로 접근하면 쉽다.

아래 네 가지는 원래 OAuth 2.0 표준에서 다룬 대표적인 Grant이다. 네 단계를 차례대로 수행한다는 뜻이 아니며, 확장 방식도 있으므로 모든 Grant가 네 종류뿐이라는 뜻도 아니다. [RFC 6749](https://www.rfc-editor.org/rfc/rfc6749.html)

| Grant | 흐름 | 핵심 차이 |
|---|---|---|
| Authorization Code | 사용자 인증 → Code → Token | Code를 별도로 토큰으로 교환 |
| Implicit | 사용자 인증 → 브라우저로 Token 직접 전달 | 최초 토큰 발급에서 Code 교환이 없음 |
| Resource Owner Password Credentials | Client가 사용자 ID/PW를 받아 Token Endpoint에 전달 | Client가 사용자 비밀번호를 직접 취급 |
| Client Credentials | 클라이언트가 자신의 자격증명으로 인증 → Token | 사용자 대신이 아니라 자신의 자격으로 접근 |

### Authorization Code

사용자가 인증받으면 Client가 먼저 짧은 수명의 Code를 받고, 이를 Token Endpoint에서 토큰으로 교환한다. 브라우저 Public Client에서는 PKCE를 함께 사용한다.

```text
브라우저를 통해 Code 수신
→ Code와 PKCE verifier로 토큰 요청
→ Access Token으로 API 호출
```

이 시리즈에서 실제 요청을 따라가는 중심 흐름이다.

### Implicit

Implicit에서는 `#access_token=...`처럼 URL Fragment에 토큰이 포함되는 형태를 볼 수 있다. `#` 뒤의 Fragment는 브라우저가 처리하며, 해당 URL로 보내는 HTTP 요청에 그대로 포함되는 부분은 아니다. [RFC 6749 §4.2](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.2)

### Password Grant

Password Grant는 Client가 사용자 자격증명을 받아 OAuth 토큰 발급 요청에 사용하는 특정 방식이다. **Spring Boot가 자체 DB의 비밀번호를 확인하는 일반 로그인이 자동으로 Password Grant가 되는 것은 아니다.** 비밀번호를 쓴다는 공통점만으로 두 흐름을 같은 것으로 볼 수 없다.

### Client Credentials

여기서 사용하는 자격증명은 사용자의 ID/PW가 아니다. 서버 애플리케이션의 Client ID와 Client Secret 같은 클라이언트 자격증명이다. 토큰에 부여되는 권한도 해당 클라이언트에 허용된 범위이며, 무조건 관리자 권한을 얻는 것이 아니다. [RFC 6749 §4.4](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.4)

## 5. 과거 방식의 이해와 새 구현의 선택

네 가지 Grant를 비교하는 목적은 원리를 구분하기 위해서이다. 모두를 새 서비스에 구현해야 한다는 뜻은 아니다.

OAuth 보안 권고인 RFC 9700은 다음과 같이 정리한다.

- Public Client의 Authorization Code 흐름에는 PKCE를 사용해야 한다.
- Implicit 방식은 사용하지 않는 방향을 권고한다.
- Resource Owner Password Credentials Grant는 사용해서는 안 된다.

브라우저 앱 예시에서는 **Authorization Code + PKCE**를 중심으로 학습한다. [RFC 9700 §2.1.1·§2.1.2·§2.4](https://www.rfc-editor.org/rfc/rfc9700.html#section-2)

다음 글에서는 로그인 요청을 시작하는 순간부터 Code를 받는 콜백, 토큰 교환, API 호출까지 누가 무엇을 보내는지 순서대로 살펴본다.

## 참고 자료

- [RFC 6749 — OAuth 2.0](https://www.rfc-editor.org/rfc/rfc6749.html)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [RFC 9700 — OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700.html)
- [Keycloak JavaScript adapter](https://www.keycloak.org/securing-apps/javascript-adapter)

## 시리즈 이어 읽기

1. [인증·인가와 OAuth의 역할, Grant 이해하기](oauth-oidc-keycloak-01-foundations.html)
2. [Authorization Code와 PKCE로 로그인 흐름 따라가기](oauth-oidc-keycloak-02-code-pkce.html)
3. [Access·ID·Refresh Token과 JWT·Claim·Scope·Role](oauth-oidc-keycloak-03-tokens-jwt.html)
4. [Spring API의 JWT 검증과 JWKS·Discovery](oauth-oidc-keycloak-04-resource-server.html)
5. [세션 쿠키·SSO와 Keycloak 실습 체크리스트](oauth-oidc-keycloak-05-sso-practice.html)
