---
title: "[OAuth·OIDC·Keycloak 2] Authorization Code와 PKCE로 로그인 흐름 따라가기"
topic: "web"
category: "SECURITY"
published: "2026-10-27"
tags: "OAuth, OIDC, Keycloak, Authorization Code, PKCE, state, nonce"
---

Authorization Code 흐름의 중심은 **사용자 인증 → Code 수신 → 토큰 교환 → API 호출**이다. 이를 이해하려면 Code를 받는 주체와 토큰으로 교환하는 주체를 같은 구조 안에서 따라가야 한다.

이 글의 FinAccess는 가상의 브라우저 SPA이며, 직접 토큰을 받아 Spring Boot API에 제출한다. 앱의 서버 로그인 세션 쿠키에 의존하지 않는 학습 예시이다. 주소, Realm, Client ID는 모두 설명용이며, `localhost`의 HTTP 주소는 로컬 실습용이다. 공개 환경에서는 HTTPS를 사용한다.

## 1. 로그인 요청을 준비한다

사용자가 FinAccess의 로그인 버튼을 누르면 로그인 처리 코드나 연동 라이브러리가 이번 인증 요청에 사용할 값을 준비한다.

| 값 | 목적 |
|---|---|
| `state` | 돌아온 인증 응답을 이번 로그인 요청과 연결 |
| `nonce` | ID Token을 이번 인증 요청과 연결 |
| `code_verifier` | 코드 교환 때 제출할 요청별 무작위 비밀값 |
| `code_challenge` | verifier를 S256 방식으로 변환해 인증 요청에 보낼 값 |

이 예시에서는 `nonce`도 사용한다. PKCE의 verifier와 challenge는 로그인 시도마다 새로 준비하며, verifier는 인증 요청 URL에 보내지 않는다. [RFC 7636](https://www.rfc-editor.org/rfc/rfc7636.html), [OpenID Connect 인증 요청](https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest)

## 2. 브라우저를 Keycloak으로 이동시킨다

FinAccess는 브라우저를 Keycloak의 Authorization Endpoint로 이동시킨다. 예시 경로는 다음과 같다.

```text
http://localhost:8085/realms/board-realm/protocol/openid-connect/auth
```

인증 요청에는 다음과 같은 정보가 포함된다.

| 파라미터 | 뜻 |
|---|---|
| `client_id=finaccess-web` | 요청한 Client 식별 |
| `response_type=code` | Authorization Code 요청 |
| `redirect_uri=http://localhost:3000/callback` | 인증 응답을 받을 주소 |
| `scope=openid profile email` | OIDC 인증과 해당 사용자 정보 범주 요청 |
| `state` | 이번 요청과 응답을 연결하는 값 |
| `nonce` | 이번 요청과 ID Token을 연결하는 값 |
| `code_challenge` | PKCE 검증을 위해 보낸 변환값 |
| `code_challenge_method=S256` | challenge 생성 방식 |

첫 화면 이동이 반드시 앱 서버의 302 응답으로 시작해야 하는 것은 아니다. 브라우저 코드나 연동 라이브러리도 이동을 시작할 수 있다. 핵심은 **브라우저가 인증 요청을 가지고 Keycloak으로 이동한다는 점**이다. [OpenID Connect Authorization Code Flow](https://openid.net/specs/openid-connect-core-1_0.html#CodeFlowAuth)

## 3. 사용자가 Keycloak에서 인증받는다

사용자는 Keycloak의 로그인 화면에서 자격증명을 입력한다. FinAccess가 사용자 비밀번호를 받아 대신 전달하는 흐름이 아니다. Keycloak은 사용자 인증과 필요한 동의·접근 정책을 처리한다.

이미 유효한 Keycloak 로그인 상태가 있다면 정책에 따라 비밀번호 입력 없이 진행될 수도 있다. 이것이 다른 앱의 로그인과 연결되는 SSO는 5편에서 다룬다.

## 4. 콜백에서 Code를 받는다

인증과 인가 처리가 끝나면 Keycloak은 브라우저를 등록된 콜백 주소로 돌려보낸다. 기본적인 쿼리 응답 예시는 다음과 같다.

```http
HTTP/1.1 302 Found
Location: http://localhost:3000/callback?code=ABC123&state=XYZ
```

브라우저가 `Location` 주소로 이동하면 FinAccess의 콜백 처리 코드가 `code`와 `state`를 받는다. 이 예시에서 Code는 브라우저의 이동을 통해 앱에 전달된다. **콜백은 Keycloak의 처리가 끝난 뒤 앱이 응답을 받는 지점**이다. [RFC 6749 §4.1.2](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.1.2)

앱은 돌아온 `state`가 자신이 시작한 로그인 시도에 연결되는지 확인해야 한다. 로그인 취소나 오류 응답도 정상적인 처리 대상으로 구분한다.

## 5. Code를 Token으로 교환한다

FinAccess는 응답을 확인한 뒤 Token Endpoint에 Code와 처음 보관한 verifier를 보낸다.

```http
POST /realms/board-realm/protocol/openid-connect/token
Host: localhost:8085
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&client_id=finaccess-web&code=ABC123&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fcallback&code_verifier=INITIAL_RANDOM_VERIFIER
```

이 값들은 요청 구조를 보여주는 자리표시자이다. 실제 요청에서는 유효한 Code와 규격에 맞게 생성한 verifier를 사용한다.

Keycloak은 코드의 유효성, Client와의 연결, Redirect URI, PKCE 등의 조건을 검증한다. **브라우저 Public Client 예시이므로 Client Secret을 넣지 않는다.** 브라우저 앱에는 고정된 Secret을 안전하게 숨길 수 없기 때문이다. [RFC 6749 §4.1.3](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.1.3), [Keycloak Public Client 설정](https://www.keycloak.org/securing-apps/javascript-adapter)

OIDC Code 흐름이 성공하면 Access Token과 ID Token을 받고, 조건에 따라 Refresh Token도 받을 수 있다. 클라이언트는 ID Token 검증을 통해 인증 결과를 확인하고 Access Token은 API 호출에 사용한다. [OpenID Connect Token Response](https://openid.net/specs/openid-connect-core-1_0.html#TokenResponse)

## 6. Access Token으로 API를 호출한다

```http
GET /api/users/me
Authorization: Bearer ACTUAL_ACCESS_TOKEN
```

초기 구조에서는 Spring Boot API에 직접 요청하고, 게이트웨이를 추가한 구조에서는 게이트웨이를 거쳐 요청한다. API에 제출하는 것은 Code가 아니라 Access Token이다.

Bearer Token은 가진 사람이 사용할 수 있는 자격증명이다. 전송과 저장 중 유출되지 않도록 보호해야 한다. [RFC 6750](https://www.rfc-editor.org/rfc/rfc6750.html)

## 7. redirect_uri, state, nonce의 차이

| 요소 | 확인할 질문 | 주로 검증하는 쪽 |
|---|---|---|
| `redirect_uri` | 인증 결과를 돌려보낼 허용된 주소인가? | Keycloak |
| `state` | 내가 시작한 로그인 시도에 연결된 응답인가? | FinAccess |
| `nonce` | 이 ID Token이 이번 인증 요청에 연결되는가? | FinAccess |
| PKCE | Code를 교환하는 쪽이 처음 준비한 verifier를 가지고 있는가? | Keycloak |

### redirect_uri: 응답을 돌려보낼 주소

Keycloak은 등록된 Redirect URI와 요청의 주소를 검증해야 한다. 임의의 주소로 Code를 보낼 수 있으면 공격자의 주소에 응답을 전달할 수 있기 때문이다. 허용 주소는 가능한 한 구체적으로 설정한다. [RFC 9700 §2.1](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.1)

### state: 요청과 응답의 짝 맞추기

```text
로그인 시작 시 무작위 state 생성·보관
→ 인증 요청에 state 전달
→ 콜백에 같은 state가 돌아옴
→ 원래 로그인 시도와 안전하게 연결하여 비교
```

`state`는 원치 않는 사용자가 로그인 페이지에 접근하는 것을 차단하는 값이 아니다. 클라이언트가 돌아온 응답을 검증하는 데 사용하며, 값 자체뿐 아니라 해당 브라우저의 로그인 시도와 안전하게 묶는 것이 중요하다.

### nonce: 인증 요청과 ID Token의 짝 맞추기

인증 요청에 `nonce`를 보냈다면 ID Token에 포함된 값이 원래 요청의 값과 일치하는지 검증해야 한다. `state`는 인증 응답, `nonce`는 ID Token 속 인증 결과와의 연결을 중심으로 이해하면 된다. [OpenID Connect ID Token Validation](https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation)

이 표는 각 값의 주목적을 나눈 것이다. PKCE나 nonce도 조건에 따라 CSRF 방어에 쓰이므로, 각 보안 효과가 완전히 겹치지 않는다고 단정하지 않는다. 실제 처리는 검증된 OIDC 라이브러리와 보안 권고에 맞춘다. [RFC 9700 §4.7](https://www.rfc-editor.org/rfc/rfc9700.html#section-4.7)

## 8. PKCE가 Code 교환을 보호하는 방법

```text
FinAccess: 요청별 무작위 verifier 생성
→ challenge = BASE64URL(SHA256(ASCII(verifier)))
→ 인증 요청에는 challenge와 S256 전달
→ Code를 받은 뒤 Code + verifier 제출

Keycloak: 제출받은 verifier를 같은 방식으로 변환
→ 처음 받은 challenge와 비교
→ 일치하는지 확인하여 코드 교환 검증
```

S256의 Base64url 결과에서는 끝의 `=` 패딩을 제거한다. `code_verifier`는 충분한 엔트로피를 가진 규격상 43~128자의 문자열이며, 매 로그인 요청에 새로 생성한다. [RFC 7636 §4.1·§4.2](https://www.rfc-editor.org/rfc/rfc7636.html#section-4.1)

PKCE는 Code 자체가 복사되는 것을 막는 기술이 아니다. **Code만 탈취한 사람이 토큰으로 교환하는 것을 막는 장치**이다. 별도의 Grant도, 앱 전체가 공유하는 고정된 Client Secret도 아니다.

이 흐름을 따라갈 때 가장 먼저 기억할 구분은 두 가지이다. **Code는 토큰을 얻을 때, Access Token은 보호된 API를 사용할 때 제출한다.**

## 참고 자료

- [RFC 6749 §4.1 — Authorization Code Grant](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.1)
- [RFC 7636 — PKCE](https://www.rfc-editor.org/rfc/rfc7636.html)
- [RFC 9700 — OAuth 보안 권고](https://www.rfc-editor.org/rfc/rfc9700.html)
- [OpenID Connect Core — Authorization Code Flow](https://openid.net/specs/openid-connect-core-1_0.html#CodeFlowAuth)
- [Keycloak OIDC Endpoints](https://www.keycloak.org/securing-apps/oidc-layers)

## 시리즈 이어 읽기

1. [인증·인가와 OAuth의 역할, Grant 이해하기](oauth-oidc-keycloak-01-foundations.html)
2. [Authorization Code와 PKCE로 로그인 흐름 따라가기](oauth-oidc-keycloak-02-code-pkce.html)
3. [Access·ID·Refresh Token과 JWT·Claim·Scope·Role](oauth-oidc-keycloak-03-tokens-jwt.html)
4. [Spring API의 JWT 검증과 JWKS·Discovery](oauth-oidc-keycloak-04-resource-server.html)
5. [세션 쿠키·SSO와 Keycloak 실습 체크리스트](oauth-oidc-keycloak-05-sso-practice.html)
