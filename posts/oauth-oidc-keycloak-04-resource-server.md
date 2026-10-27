---
title: "[OAuth·OIDC·Keycloak 4] Spring API의 JWT 검증과 JWKS·Discovery 이해하기"
topic: "web"
category: "SECURITY"
published: "2026-10-27"
tags: "OAuth, OIDC, Keycloak, Spring Security, Resource Server, JWT, JWKS, Discovery, 인가"
---

API가 Access Token을 받았을 때 해야 할 일은 Payload를 읽는 것에서 끝나지 않는다. 신뢰하는 발급자의 토큰인지 검증하고, 요청한 작업에 필요한 권한이 있는지 판단해야 한다. JWKS와 OIDC Discovery는 이 검증에 필요한 공개키와 주소 정보를 제공한다.

이 글에서는 학습용 브라우저 앱 **FinAccess**가 Keycloak에서 받은 Access Token을 **Spring Boot API**에 제출한다고 가정한다. API는 서버 로그인 세션 쿠키 대신 Bearer Token으로 요청을 인증한다. 아래 흐름은 구현을 이해하기 위한 기준이며, 실습 완료 결과는 아니다.

## 1. API 요청을 받은 뒤의 책임

```http
GET /api/users/me
Authorization: Bearer 실제_Access_Token
```

API 관점에서 처리 단계를 나누면 다음과 같다.

```text
Bearer Token 추출
    ↓
JWT 형식·서명·Claim 검증
    ↓
검증된 Claim을 사용자·권한으로 해석
    ↓
URL·메서드·데이터에 대한 인가 규칙 적용
    ↓
허용된 경우 업무 처리
```

여기서 **디코딩은 내용 읽기, 검증은 신뢰 여부 확인, 인가는 작업 허용 여부 판단**이다. 누구나 만들 수 있는 Payload에 `ADMIN`이 쓰여 있다는 이유로 신뢰하면 안 된다.

## 2. JWT 검증에서는 무엇을 확인하는가?

| 확인 대상 | 질문 |
|---|---|
| 서명과 허용 알고리즘 | 신뢰하는 키로 검증되는가? 서버가 허용한 방식인가? |
| `iss` | 내가 신뢰하도록 설정한 발급자인가? |
| `exp` | 만료되지 않았는가? |
| `nbf` | 아직 사용할 수 없는 시점은 아닌가? |
| `aud` | 이 API가 받아들일 수 있는 대상의 토큰인가? |
| 권한 Claim | 요청한 기능에 필요한 Scope·Role을 가지고 있는가? |

Spring Security의 JWT Resource Server는 설정된 Decoder를 통해 서명과 주요 Claim을 검증한다. `issuer-uri`를 사용하는 일반 구성에서는 `iss`, `exp`, `nbf` 검증과 Scope의 권한 변환이 연결된다. **Audience와 사용자 정의 권한 정책은 API에 맞게 명시적으로 구성해야 한다.** 구체적인 설정 방법은 사용하는 Spring Boot·Security 버전의 문서를 따른다. [Spring Security JWT Resource Server](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html)

ID Token과 Access Token을 구분해야 하는 이유도 여기서 드러난다. 클라이언트용 인증 결과와 업무 API용 접근 자격은 수신 대상과 목적이 다르다.

## 3. JWKS는 검증용 공개키 목록이다

비대칭 서명 구성에서는 Keycloak이 개인키로 토큰에 서명하고, API는 대응하는 공개키로 검증한다.

```text
Keycloak의 개인키 → 토큰 서명
Keycloak의 공개키 → API가 서명 검증에 사용
```

JWK는 키를 JSON으로 표현한 형식이고, JWKS는 그 키들을 모은 집합이다. 보통 최상위 `keys` 배열에 여러 키가 들어간다. 토큰 Header의 `kid`는 목록에서 적절한 키를 고를 때 쓰는 식별자다. 키를 선택했다고 검증이 끝난 것은 아니다. 실제 서명 검증이 성공해야 한다. [JWK — RFC 7517](https://www.rfc-editor.org/rfc/rfc7517.html)

**어디서 가져온 공개키인지가 신뢰의 출발점이다.** API에 신뢰할 발급자를 설정하고 그 발급자의 Discovery·JWKS를 사용해야 한다. 요청자가 보낸 토큰에 적힌 임의의 URL을 따라가 공개키를 받아 검증하는 방식으로 이해하면 안 된다. 발급자와 알고리즘 등 검증 규칙도 서버가 통제한다. [JWT Best Current Practices — RFC 8725](https://www.rfc-editor.org/rfc/rfc8725.html)

## 4. Discovery는 Endpoint를 알려주는 안내 문서다

Keycloak의 로컬 학습 예시는 다음과 같다.

```text
http://localhost:8085/realms/board-realm/.well-known/openid-configuration
```

`localhost`의 HTTP 주소는 로컬 실습용 예시다. 공개 환경에서는 HTTPS로 보호된 발급자와 Endpoint를 사용한다.

이 주소는 로그인 화면도, 토큰 그 자체도 아니다. 해당 Realm의 OIDC 설정과 Endpoint를 알려주는 JSON 문서다. [Keycloak — OIDC endpoints](https://www.keycloak.org/securing-apps/oidc-layers)

| 항목 | 알려주는 정보 |
|---|---|
| `issuer` | 인증 제공자의 식별자 |
| `authorization_endpoint` | 브라우저가 인증 요청을 시작할 주소 |
| `token_endpoint` | Code 교환·토큰 갱신을 요청할 주소 |
| `userinfo_endpoint` | Access Token으로 사용자 정보를 요청할 주소 |
| `jwks_uri` | 서명 검증용 키 집합 주소 |

Discovery를 통해 받은 `issuer`도 기대한 발급자와 일치하는지 확인해야 한다. “주소를 자동으로 찾는다”는 편의가 “아무 발급자나 신뢰한다”는 뜻은 아니다. [OIDC Discovery — 설정 검증](https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderConfigurationValidation)

## 5. API가 매번 Keycloak에 물어보는가?

공개키를 조회하고 캐시하면 JWT 서명은 API 쪽에서 검증할 수 있다. 따라서 **API 요청마다 반드시 Keycloak에 토큰의 진위를 물어볼 필요는 없다.** 키 교체 시에는 새로운 키를 받아 검증할 수 있도록 갱신 동작도 고려한다.

```text
신뢰하는 발급자의 설정·공개키 확보
    ↓
공개키 캐시
    ↓
들어오는 JWT를 로컬에서 검증
    ↓
키 교체 등 필요한 때 공개키 갱신
```

이 구성은 로그아웃이나 토큰 폐기를 즉시 알아내는 별도 통신과는 다르다. 서명과 만료만 확인하는 API는 아직 만료되지 않은 토큰을 계속 유효하게 볼 수 있다. 즉시 차단이 필요한 요구에는 토큰 수명과 폐기 확인 전략을 함께 설계해야 한다. Token Introspection은 토큰의 현재 활성 상태 등을 확인하는 별도 방식이다. [OAuth Token Introspection — RFC 7662](https://www.rfc-editor.org/rfc/rfc7662.html)

## 6. Scope와 Keycloak Role의 권한 매핑

Spring의 기본 JWT 권한 변환에서는 Scope를 `SCOPE_` 접두사의 Authority로 표현한다. 예를 들어 `board.read` Scope를 사용하면 인가 규칙에서 `SCOPE_board.read`와 연결할 수 있다.

Keycloak의 Realm Role이나 Client Role이 자동으로 같은 방식의 Spring Role이 되는 것은 아니다. 역할이 담긴 Claim 위치와 구조를 확인하고, 필요한 `JwtAuthenticationConverter` 등으로 API의 권한 체계에 맞게 변환해야 한다. Scope와 Role을 모두 쓴다면 기존 Scope 권한도 필요한지 함께 판단한다. [Spring Security — 권한 추출과 변환](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html#oauth2resourceserver-jwt-authorization-extraction)

```text
Keycloak 역할 부여
→ 토큰의 역할 Claim
→ Spring의 GrantedAuthority로 변환
→ 관리자 API의 인가 규칙과 비교
```

토큰이 유효하더라도 다른 사용자의 게시글을 수정할 권한까지 자동으로 생기지는 않는다. 작성자 여부처럼 데이터에 종속된 조건은 업무 인가 규칙에서 추가로 확인한다.

## 7. 401과 403으로 실패 지점을 구분한다

| 응답 | 보호된 API에서의 일반적인 해석 | 확인할 항목 |
|---|---|---|
| 401 Unauthorized | 유효한 인증 정보가 없음 | 토큰 누락·만료·서명·Issuer·Audience 검증 |
| 403 Forbidden | 인증은 되었지만 요청 권한이 부족함 | 필요한 Scope·Role·업무 규칙과 실제 권한 매핑 |

Bearer 오류 규격은 `invalid_token`과 `insufficient_scope`를 구분한다. 실제 응답 본문과 상태 코드는 서버의 구현·예외 처리 설정에 따라 달라질 수 있으므로, 상태 코드와 서버의 검증 로그를 함께 본다. 토큰 원문을 로그에 남겨 확인하는 방식은 피한다. [Bearer Token 오류 처리 — RFC 6750 §3.1](https://www.rfc-editor.org/rfc/rfc6750.html#section-3.1)

API7 같은 게이트웨이를 추가하면 요청 경로는 `FinAccess → API7 → Spring API`로 확장된다. 이때도 게이트웨이와 API 중 누가 토큰을 검증하고, 누가 업무 권한을 최종 판단하는지 명시해야 한다. 게이트웨이 배치 자체가 인가 정책을 대신하지 않는다.

## 시리즈 이어 읽기

1. [인증·인가와 OAuth의 역할, Grant 이해하기](oauth-oidc-keycloak-01-foundations.html)
2. [Authorization Code와 PKCE로 로그인 흐름 따라가기](oauth-oidc-keycloak-02-code-pkce.html)
3. [토큰의 용도와 JWT·Claim·Scope·Role 구분하기](oauth-oidc-keycloak-03-tokens-jwt.html)
4. [Spring API의 JWT 검증과 JWKS·Discovery 이해하기](oauth-oidc-keycloak-04-resource-server.html)
5. [세션 쿠키·SSO와 Keycloak 실습 체크리스트](oauth-oidc-keycloak-05-sso-practice.html)
