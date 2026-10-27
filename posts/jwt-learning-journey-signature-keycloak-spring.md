---
title: "[JWT] 구조·변조·서명부터 Keycloak과 Spring Security 검증까지"
topic: "web"
category: "SECURITY"
published: "2026-10-27"
tags: "JWT, Keycloak, Spring Security, Claim, 서명, HMAC, JWKS, 인증, 인가"
---

JWT는 사용자 식별자, 발급자, 만료 시각 같은 정보를 Claim으로 담아 전달하는 형식이다. API 인증에서 중요한 것은 내용을 읽는 데서 끝나지 않고, **신뢰하는 발급자의 토큰인지 검증한 뒤 요청에 필요한 권한을 판단하는 것**이다.

이 글에서는 브라우저 앱 FinAccess가 Keycloak에서 Access Token을 받고 Spring Boot API에 제출하는 구성을 예로 들어, JWT의 구조부터 서명과 키, 공개키 조회, Spring Security의 처리 과정까지 연결한다.

```text
Keycloak이 토큰 발급·서명
→ 브라우저가 Access Token으로 API 호출
→ API가 서명·발급자·대상·만료 등을 검증
→ 검증된 정보로 사용자와 권한 구성
→ 요청한 작업의 허용 여부 판단
```

## 1. JWT와 Access·ID·Refresh Token의 관계

OAuth는 애플리케이션이 접근 권한을 얻고 사용하는 절차를 다루고, OIDC는 그 위에 사용자 인증을 위한 규칙을 추가한다. JWT는 이 과정에서 정보를 표현할 때 사용할 수 있는 형식이다. [OAuth 2.0](https://www.rfc-editor.org/rfc/rfc6749.html), [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html)

| 항목 | 용도 | 사용하는 곳 |
|---|---|---|
| Authorization Code | 토큰으로 교환하는 짧은 수명의 일회용 코드 | 인증 서버의 Token Endpoint |
| Access Token | 보호된 API에 접근 | Resource Server |
| ID Token | 클라이언트가 사용자 인증 결과를 확인 | 로그인한 앱 |
| Refresh Token | 새 Access Token을 요청 | 인증 서버의 Token Endpoint |

Access Token이 반드시 JWT인 것은 아니다. OIDC의 ID Token은 JWT로 정의된다. 두 토큰이 모두 JWT처럼 보이고 사용자 정보를 담더라도 용도가 같아지지는 않는다. 업무 API에는 해당 API가 받아들이도록 발급된 Access Token을 제출한다. [OIDC의 ID Token](https://openid.net/specs/openid-connect-core-1_0.html#IDToken)

## 2. Header·Payload·Signature의 구조

흔히 보는 서명된 JWT의 Compact 표현은 점으로 구분한 세 부분이다.

```text
BASE64URL(Header).BASE64URL(Payload).BASE64URL(Signature)
```

### Header: 알고리즘과 키 선택 정보

```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "realm-key-1"
}
```

`alg`는 서명 또는 MAC 알고리즘, `typ`는 토큰 종류, `kid`는 검증 키를 선택할 때 참고하는 식별자다. Header를 읽었다고 그 값을 신뢰할 수 있는 것은 아니다. 서버는 허용할 알고리즘과 신뢰할 키를 자신의 설정으로 제한해야 한다. 요청자가 적어 보낸 `alg`나 `kid`가 검증 정책을 마음대로 바꾸게 해서는 안 된다. [JWT 보안 권고 — RFC 8725](https://www.rfc-editor.org/rfc/rfc8725.html)

### Payload: Claim을 담는 부분

다음은 구조를 설명하기 위한 Access Token Payload 예시다. 식별자와 시간은 예시 값이다.

```json
{
  "iss": "https://auth.example.com/realms/board-realm",
  "sub": "user-123",
  "aud": "board-api",
  "iat": 1700000000,
  "nbf": 1700000000,
  "exp": 1700000300,
  "scope": "board.read",
  "realm_access": {
    "roles": ["USER"]
  }
}
```

Claim은 JSON 안의 개별 정보 항목이다. 위 예시에는 발급자, 주체, API 대상, 시간, Scope, 역할 정보가 들어 있다. Keycloak의 역할 Claim 위치와 내용은 Mapper와 역할 범위 등 설정에 따라 달라진다. [Keycloak Server Administration Guide](https://www.keycloak.org/docs/latest/server_admin/index.html)

### Signature: 변경 여부를 검증하는 값

서명 또는 MAC의 입력에는 인코딩된 Header와 Payload가 함께 들어간다.

```text
서명 입력 = BASE64URL(Header) + "." + BASE64URL(Payload)
```

발급자는 이 입력에 대해 알고리즘과 키를 사용해 서명 또는 MAC을 생성한다. 검증자는 토큰의 입력과 서명 또는 MAC이 유효한지 확인한다. Payload뿐 아니라 보호된 Header가 바뀌어도 검증에 영향을 준다. [JWS — RFC 7515](https://www.rfc-editor.org/rfc/rfc7515.html)

JWT에는 암호화된 JWE 형태도 있으며 JWE의 Compact 표현은 다섯 부분이다. 따라서 모든 JWT가 항상 세 부분이라고 일반화하지 않는다. [JWT — RFC 7519](https://www.rfc-editor.org/rfc/rfc7519.html)

## 3. 디코딩·검증·인가는 서로 다른 단계다

| 단계 | 하는 일 | 이 단계만으로 알 수 없는 것 |
|---|---|---|
| 디코딩 | Header와 Payload를 읽음 | 내용이 신뢰할 수 있는지 |
| 검증 | 서명·발급자·대상·시간 등 필요한 조건 확인 | 해당 업무 작업까지 허용되는지 |
| 인가 | 검증된 권한과 업무 정책을 요청에 적용 | 다른 요청에서도 무조건 허용되는지 |

Base64url은 인코딩이다. 서명된 JWT의 Payload는 일반적으로 누구나 디코딩해서 읽을 수 있다. **서명은 내용을 숨기는 암호화와 다르다.** 민감한 내용을 담을지는 이 특성과 전송·저장 환경을 고려해야 한다. [RFC 7519](https://www.rfc-editor.org/rfc/rfc7519.html)

토큰이 유효하고 USER 역할이 있어도, 다른 사용자의 게시글을 수정할 수 있는지는 별도 업무 규칙으로 판단한다. 서명 검증과 게시글 작성자 검사는 서로 다른 책임이다.

## 4. 주요 Claim은 왜 검사하는가?

| Claim | 의미 | 검증하거나 해석하는 이유 |
|---|---|---|
| `iss` | 발급자 | 신뢰하도록 설정한 인증 서버의 토큰인지 확인 |
| `sub` | 토큰이 나타내는 주체 | 사용자나 서비스 주체를 업무 데이터와 연결 |
| `aud` | 수신 대상 | 이 API가 받아들일 토큰인지 확인 |
| `exp` | 만료 시각 | 만료된 토큰 사용 거부 |
| `nbf` | 사용 가능 시작 시각 | 사용 가능 시점 이전의 토큰 거부 |
| `iat` | 발급 시각 | 발급 시점을 해석하고 필요한 수명 정책에 활용 |

`exp`, `nbf`, `iat`는 일반적으로 Unix epoch 기준 초 단위의 NumericDate로 표현한다. 예시의 `iat`와 `exp` 차이는 300초, 즉 5분이다. 서버 간 시계 차이는 제한된 허용 오차 정책으로 다룰 수 있다. 모든 Claim이 모든 JWT에 필수인 것은 아니므로 사용하는 토큰 규격과 API 정책에 맞게 필수 조건을 정해야 한다. [RFC 7519 §4.1](https://www.rfc-editor.org/rfc/rfc7519.html#section-4.1)

### sub는 주체, aud는 수신 대상이다

`sub=user-123`은 토큰이 나타내는 주체를 식별한다. 서로 다른 발급자가 같은 `sub` 값을 사용할 수 있으므로 사용자 식별자를 연결할 때는 `iss`의 범위도 고려한다.

`aud=board-api`는 이 토큰의 수신 대상이 `board-api`임을 나타낸다. 다른 API가 서명을 검증할 수 있다고 해서 그 토큰을 받아들여도 된다는 뜻은 아니다. `aud`는 문자열 하나 또는 문자열 배열일 수 있다. [JWT Audience](https://www.rfc-editor.org/rfc/rfc7519.html#section-4.1.3)

ID Token의 Audience에는 인증 결과를 받는 Client가 포함된다. Access Token에서는 접근하려는 API 등 자원의 대상을 고려해야 한다. 같은 Keycloak이 발급했다는 이유로 모든 토큰을 같은 용도로 처리하면 안 된다. [OIDC의 ID Token 검증](https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation)

### Scope·Role·Claim은 같은 말이 아니다

| 개념 | 의미 | 예시 |
|---|---|---|
| Scope | 요청하거나 허용받는 접근·정보 범위 | `board.read`, `openid`, `profile` |
| Role | 사용자나 서비스에 부여한 역할 | `USER`, `ADMIN` |
| Claim | 토큰이나 응답의 개별 정보 항목 | `sub`, `scope`, 역할 정보를 담은 항목 |

역할을 부여하는 것, 그 역할을 토큰에 담는 것, API가 이를 권한으로 해석하는 것은 각각 연결해야 할 단계다. `ADMIN`이라는 문자열이 보인다는 사실만으로 관리자 API가 자동으로 허용되는 것은 아니다.

## 5. Payload를 USER에서 ADMIN으로 바꾸면 어떻게 되는가?

공격자가 토큰의 Payload를 읽고 역할을 바꾼다고 가정하자.

```text
원래 내용: roles = ["USER"]
변경 내용: roles = ["ADMIN"]
```

변경된 JSON을 다시 Base64url로 인코딩할 수는 있다. 하지만 원래 Signature를 그대로 붙이면 변경된 Header·Payload에 대한 유효한 서명이 아니므로 정상적인 검증에서 거부된다.

```text
정상 토큰
원래 Header + 원래 Payload + 그 입력에 대한 유효한 서명
→ 필요한 검증을 통과하면 사용 가능

변조 토큰
원래 Header + 바꾼 Payload + 원래 서명
→ 서명 검증 실패
```

변경된 내용에 대한 유효한 서명이나 MAC을 만들려면 해당 생성 키가 필요하다. 서명 검증을 생략하거나 요청자가 제시한 임의의 키·알고리즘을 신뢰하면 이 보호가 무너질 수 있다. 검증된 라이브러리와 서버가 정한 정책으로 처리해야 한다. [RFC 8725 — 알고리즘과 암호 연산 검증](https://www.rfc-editor.org/rfc/rfc8725.html#section-3.1)

## 6. 대칭 방식과 비대칭 서명은 키의 관계가 다르다

| 구분 | HMAC 방식 | 비대칭 서명 |
|---|---|---|
| 예 | HS256 | RS256, ES256 |
| 생성 | 공유 비밀키로 MAC 생성 | 개인키로 서명 |
| 검증 | 같은 비밀키로 MAC 검증 | 대응하는 공개키로 서명 검증 |
| 검증자가 가진 키로 생성할 수 있는가? | 공유 비밀키가 있으므로 가능 | 공개키만으로는 개인키의 서명을 생성할 수 없음 |

흔히 “대칭 서명”이라고 부르는 HMAC은 정확히는 공유 비밀키 기반의 MAC이다. 발급자와 여러 API가 같은 키를 공유하면 검증을 위해 키를 받은 API도 유효한 MAC을 생성할 수 있다. `JWT_SECRET`이라는 설정명만 보고 모든 JWT 시스템의 키 구성을 같다고 보면 안 된다. [JWS의 전자서명과 MAC 차이](https://www.rfc-editor.org/rfc/rfc7515.html#section-10.5)

비대칭 서명에서는 발급 서버가 개인키를 보관하고 API들은 공개키로 검증할 수 있다. Keycloak이 발급하고 여러 API가 검증하는 구성을 이 관계로 이해하면 된다.

```text
Keycloak: 개인키 보관 → 토큰 서명
Spring API: 공개키 확보 → 토큰 서명 검증
```

공개키를 제공한다고 개인키의 서명을 누구나 만들 수 있는 것은 아니다. 반대로 개인키나 HMAC 비밀키가 노출되면 유효한 토큰 생성에 악용될 수 있으므로 키의 보관과 교체가 중요하다.

## 7. Discovery와 JWKS로 검증용 키를 찾는다

### Discovery: Endpoint 주소를 알려주는 문서

```text
https://auth.example.com/realms/board-realm/.well-known/openid-configuration
```

| 항목 | 의미 |
|---|---|
| `issuer` | 인증 제공자의 식별자 |
| `authorization_endpoint` | 인증 요청을 시작할 주소 |
| `token_endpoint` | Code 교환과 토큰 갱신 등을 요청할 주소 |
| `userinfo_endpoint` | 사용자 정보를 요청할 주소 |
| `jwks_uri` | 검증용 키 집합을 조회할 주소 |

이 문서는 로그인 화면이나 토큰 자체가 아니라 설정 안내서다. 기대한 발급자와 응답의 `issuer`가 일치하는지도 확인해야 한다. [Keycloak OIDC Endpoints](https://www.keycloak.org/securing-apps/oidc-layers), [OIDC Discovery 검증](https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderConfigurationValidation)

### JWKS: 키 집합의 JSON 표현

JWK는 키를 JSON으로 표현한 형식이고 JWKS는 그 키들을 모은 집합이다. 비대칭 서명 구성에서는 발급자의 검증용 공개키를 얻는 데 사용한다. 토큰 Header의 `kid`는 여러 키 중 어떤 키를 사용할지 선택하는 데 참고한다. [RFC 7517 — JWK](https://www.rfc-editor.org/rfc/rfc7517.html)

```text
서버에 신뢰하는 issuer 설정
→ 해당 발급자의 Discovery 확인
→ jwks_uri에서 공개키 목록 확보
→ kid와 허용 알고리즘 등에 맞는 키 선택
→ 서명 검증
→ iss·aud·exp·nbf 등 검증
→ 권한 판단
```

키 선택은 서명 검증의 완료가 아니다. 요청자가 보낸 토큰에 적힌 임의의 URL을 따라가 키를 가져오는 것도 신뢰를 보장하지 않는다. 발급자와 키의 신뢰 관계는 서버 설정이 통제해야 한다. [RFC 8725](https://www.rfc-editor.org/rfc/rfc8725.html)

공개키를 캐시하면 API 요청마다 Keycloak에 토큰의 진위를 물어보지 않고 JWT를 로컬에서 검증할 수 있다. 키 교체 시에는 새 키를 받아 검증할 수 있도록 갱신 동작도 필요하다. Discovery와 키 조회의 구체적인 시점은 라이브러리 버전과 설정에 따라 달라질 수 있다. [Spring JWT Resource Server](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html)

## 8. Bearer 헤더로 API를 호출한다

```http
GET /api/boards
Authorization: Bearer <access_token>
```

Bearer Token은 가진 사람이 사용할 수 있는 자격증명이다. JWT 서명은 토큰 내용의 변경을 검증하지만 유효한 토큰을 그대로 탈취해 사용하는 것까지 막아 주지는 않는다. HTTPS와 적절한 토큰 보관, 노출 방지가 함께 필요하다. [Bearer Token — RFC 6750](https://www.rfc-editor.org/rfc/rfc6750.html)

브라우저 앱이 직접 토큰을 보유하는 구조에서는 API 호출에 Access Token을 붙인다. Keycloak JavaScript 어댑터는 Access Token과 Refresh Token을 메모리에 보관하며 영구 저장을 피하도록 안내한다. 메모리 보관도 실행 중인 악성 스크립트의 접근을 모두 차단하는 것은 아니다. [Keycloak JavaScript Adapter](https://www.keycloak.org/securing-apps/javascript-adapter)

게이트웨이를 추가하면 `브라우저 → 게이트웨이 → Spring API`로 요청 경로가 늘어난다. 어느 계층에서 토큰 검증을 수행하고 어디에서 업무 인가를 판단할지는 명시적으로 구성해야 한다.

## 9. Spring Security는 JWT를 어떻게 처리하는가?

```text
BearerTokenAuthenticationFilter
  → 요청에서 Bearer Token 추출
  → AuthenticationManager에 인증 위임
  → JwtAuthenticationProvider
      → JwtDecoder로 JWT 디코딩·검증
      → JwtAuthenticationConverter로 인증 정보·권한 구성
  → SecurityContext에 인증 결과 연결
  → 요청에 적용되는 인가 규칙 검사
```

| 구성요소 | 책임 |
|---|---|
| `BearerTokenAuthenticationFilter` | Bearer Token을 추출하고 인증 처리를 위임 |
| `JwtDecoder` / `NimbusJwtDecoder` | 서명과 설정된 Claim 검증 수행 |
| `OAuth2TokenValidator` | Audience, 필수 Claim 등 필요한 검증 정책 구성 |
| `JwtAuthenticationConverter` | 검증된 JWT를 Authentication과 Authority로 변환 |
| `requestMatchers` | 인가 규칙을 적용할 요청 경로 등의 조건 선택 |
| `hasRole`, `hasAuthority` 등 | 선택한 요청에 필요한 권한 조건 적용 |

`issuer-uri`를 사용하는 일반적인 구성에서는 신뢰할 발급자의 설정·공개키를 활용하고 `iss`, `exp`, `nbf` 등을 검증한다. Audience와 필요한 추가 조건도 해당 API의 정책에 맞게 구성해야 한다. [Spring JWT 인증 처리 구조](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html#oauth2resourceserver-jwt-architecture)

### Scope와 Role은 별도로 매핑한다

기본 Scope 변환에서는 `board.read` 같은 Scope를 `SCOPE_board.read` Authority로 표현한다. Keycloak의 `realm_access.roles`나 Client Role이 자동으로 Spring의 Role이 되는 것은 아니다.

예를 들어 `hasRole("ADMIN")`을 적용하려면 기본 접두사 기준으로 `ROLE_ADMIN` Authority와 연결되어야 한다. 역할 Claim의 위치와 구조에 맞는 변환을 구성하고 기존 Scope 권한도 함께 필요한지 판단한다. [Spring JWT 권한 추출](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html#oauth2resourceserver-jwt-authorization-extraction), [요청 인가 규칙](https://docs.spring.io/spring-security/reference/servlet/authorization/authorize-http-requests.html)

### STATELESS는 Spring Security의 HTTP 세션 정책이다

`SessionCreationPolicy.STATELESS`는 Spring Security가 인증 상태를 유지하기 위해 HTTP 세션을 생성하거나 기존 세션에서 SecurityContext를 가져오지 않도록 하는 정책이다. 요청마다 제출된 Bearer Token을 바탕으로 인증하는 API 구성에 사용할 수 있다.

이 설정이 시스템 전체의 세션이나 쿠키를 없애는 것은 아니다. Keycloak의 로그인 세션과 SSO 쿠키, 다른 애플리케이션 코드의 세션 사용은 별개다. [Spring Stateless 인증](https://docs.spring.io/spring-security/reference/servlet/authentication/session-management.html#configure-stateless-authentication)

## 10. 만료·권한 부족·로그아웃을 구분한다

| 상황 | 실패하는 지점 | 보호된 API에서의 일반적인 응답 |
|---|---|---|
| 토큰 누락 | 인증 정보 없음 | 401 |
| 변조·잘못된 서명 | 토큰 검증 | 401 |
| 만료·잘못된 발급자·잘못된 대상 | Claim 검증 | 401 |
| 유효한 토큰이지만 권한 부족 | 인가 | 403 |

정확한 응답은 서버의 오류 처리 설정에 따라 달라질 수 있다. Bearer 규격에서도 `invalid_token`과 `insufficient_scope`를 구분한다. [RFC 6750 §3.1](https://www.rfc-editor.org/rfc/rfc6750.html#section-3.1)

### Refresh Token은 갱신에 사용한다

Access Token 갱신이 필요하면 클라이언트는 발급받은 유효한 Refresh Token을 인증 서버에 제출한다. Refresh Token은 항상 발급되는 것도, 영구적으로 유효한 것도 아니다. Public Client에 발급하는 Refresh Token에는 회전 또는 송신자 제한 방식의 보호가 요구된다. [RFC 6749 §6](https://www.rfc-editor.org/rfc/rfc6749.html#section-6), [RFC 9700 §2.2.2](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.2.2)

### 로그아웃이 로컬 JWT 검증에 즉시 반영되는 것은 아니다

API가 공개키로 서명과 만료만 로컬에서 검사한다면 인증 서버에서 로그아웃해도 이미 발급된 Access Token은 만료 시각까지 유효하게 보일 수 있다. Keycloak의 로그인 세션 종료와 모든 API의 토큰 사용 차단을 같은 동작으로 보면 안 된다.

짧은 토큰 수명은 탈취된 토큰을 사용할 수 있는 시간을 줄인다. 만료 전 즉시 차단하려면 API가 확인하는 폐기 목록이나 현재 상태 조회 같은 추가 정책이 필요하다. Token Introspection은 토큰의 활성 상태 등을 조회하는 별도 방식이며 실제 로그아웃·폐기 반영 동작은 인증 서버의 구현과 정책을 확인해야 한다. [OAuth Token Introspection — RFC 7662](https://www.rfc-editor.org/rfc/rfc7662.html)

## 함께 읽기

- [OAuth·OIDC의 역할과 Grant](oauth-oidc-keycloak-01-foundations.html)
- [Authorization Code와 PKCE 로그인 흐름](oauth-oidc-keycloak-02-code-pkce.html)
- [토큰과 JWT·Claim·Scope·Role](oauth-oidc-keycloak-03-tokens-jwt.html)
- [Spring API의 JWT 검증과 JWKS·Discovery](oauth-oidc-keycloak-04-resource-server.html)
- [세션 쿠키·SSO와 Keycloak 실습](oauth-oidc-keycloak-05-sso-practice.html)
