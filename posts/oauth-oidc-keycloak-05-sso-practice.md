---
title: "[OAuth·OIDC·Keycloak 5] 세션 쿠키와 SSO를 구분하고 실습으로 연결하기"
topic: "web"
category: "SECURITY"
published: "2026-10-27"
tags: "OAuth, OIDC, Keycloak, SSO, Spring, 세션"
---

브라우저 앱이 Access Token으로 API를 호출한다면, SSO는 어디에서 유지되는 걸까? 이 질문은 **앱의 로그인 상태와 인증 제공자의 로그인 상태를 나누어 보면** 이해하기 쉽다.

이 시리즈는 학습용 브라우저 앱 FinAccess가 직접 토큰을 받고 Spring Boot API에 제출하는 구조를 기준으로 한다. 이 글의 실습 항목은 앞으로 관찰하고 확인할 대상이며, 구현과 검증을 모두 완료했다는 결과 보고는 아니다.

## 1. 앱의 세션 쿠키와 Keycloak의 로그인 쿠키는 다르다

서버 세션 방식에서는 브라우저가 앱의 세션 식별자를 쿠키로 보내고, 서버가 그 식별자로 로그인 상태를 찾는다. 이번 예시에서는 FinAccess가 Access Token을 보유하고 API 요청에 직접 붙인다.

```http
GET /api/users/me
Authorization: Bearer <access_token>
```

따라서 Spring API가 앱의 로그인 세션 쿠키로 사용자를 찾는 구조는 아니다. 하지만 이것이 Keycloak에도 세션이나 쿠키가 없다는 뜻은 아니다.

| 구분 | 상태를 관리하는 곳 | 역할 |
|---|---|---|
| 앱 서버의 로그인 세션 | 앱 서버 | 세션 식별자로 해당 앱의 로그인 상태를 찾음 |
| 브라우저 앱의 토큰 | FinAccess | 인증 결과를 확인하고 Access Token으로 API 호출 |
| Keycloak의 로그인 세션과 쿠키 | Keycloak | 브라우저의 기존 인증 상태를 확인하고 SSO에 활용 |

**“업무 API가 서버 세션 쿠키에 의존하지 않는다”와 “시스템 전체에서 쿠키를 사용하지 않는다”는 서로 다른 요구다.** 또한 로그인 요청 중 `state`, `nonce`, PKCE 값을 임시로 기억하는 일은 서버 로그인 세션을 모든 API 요청에 사용하는 일과 구분된다. [Keycloak JavaScript adapter](https://www.keycloak.org/securing-apps/javascript-adapter)

Keycloak JavaScript 어댑터는 Access Token과 Refresh Token을 메모리에 보관하고, 이 토큰들을 영구 저장소에 저장하지 않도록 안내한다. 메모리에 둔다고 실행 중인 악성 스크립트의 접근까지 막는 것은 아니므로, 토큰 보관 방식과 함께 XSS 방어도 필요하다. 이 구조는 학습 기준이며 모든 애플리케이션에 적용할 유일한 방식은 아니다. [Keycloak의 토큰 보관 안내](https://www.keycloak.org/securing-apps/javascript-adapter)

## 2. OIDC는 규격이고 SSO는 로그인 경험이다

OIDC는 OAuth 2.0 위에서 사용자 인증 결과를 주고받는 규격이다. SSO는 공통 인증 제공자의 기존 로그인 상태를 여러 연동 앱에서 활용하는 기능이다. 두 개념은 연결되지만 같은 뜻은 아니다. [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html)

FinAccess와 별도의 관리 앱 FinAdmin이 같은 Keycloak Realm에 연동되어 있다고 가정해 보자.

```text
1. FinAccess에서 로그인 시작
2. Keycloak이 사용자를 인증
3. FinAccess용 Code와 토큰 발급

4. 이후 FinAdmin에 접속
5. FinAdmin도 자신의 client_id로 Keycloak에 인증 요청
6. Keycloak이 기존 로그인 상태와 정책 확인
7. 조건이 맞으면 비밀번호 재입력 없이 진행
8. FinAdmin용 Code와 토큰 발급
```

두 앱이 하나의 Access Token을 그대로 공유해야 SSO가 되는 것은 아니다. 각 앱은 자신의 인증 요청을 시작하고, Keycloak의 기존 로그인 상태를 활용한다. 정책에 따라 추가 인증이나 동의가 필요할 수도 있다. [Keycloak의 SSO 세션 설명](https://www.keycloak.org/docs/latest/server_admin/index.html)

브라우저의 추적 방지나 제3자 쿠키 제한은 iframe 기반의 로그인 상태 확인과 silent SSO 등에 영향을 줄 수 있다. 따라서 일반적인 화면 이동 로그인과 백그라운드에서 로그인 상태를 확인하는 동작을 같은 조건으로 단정하면 안 된다. [Keycloak의 최신 브라우저 제한 안내](https://www.keycloak.org/securing-apps/javascript-adapter)

**SSO가 ADMIN 권한을 만들어 주지는 않는다.** FinAdmin에서 신원을 다시 입력하지 않아도, 관리자 API 이용 여부는 토큰의 대상·권한과 업무 정책을 검사해서 결정해야 한다.

## 3. Keycloak 관리 화면의 설정을 역할로 연결한다

| 설정 | 의미 | 이번 예시에서 확인할 점 |
|---|---|---|
| Realm | 사용자·클라이언트·역할을 관리하는 분리된 영역 | `board-realm`을 실습 영역으로 사용 |
| Client | 연동하는 앱 등의 등록 정보 | 브라우저 앱 `finaccess-web` 등록 |
| User | 인증할 사용자 | 실습용 사용자 생성 |
| Role | 사용자나 서비스에 부여할 역할 | USER·ADMIN 역할과 API 정책 연결 |
| Mapper | 사용자 정보나 역할을 토큰 Claim 등에 반영 | 필요한 정보가 어떤 토큰에 담기는지 확인 |
| Valid Redirect URIs | 인증 결과를 돌려보낼 수 있는 주소 | 실제 콜백 주소를 구체적으로 등록 |
| Web Origins | 브라우저의 교차 출처 요청을 허용할 출처 | 실제 앱 출처와 맞게 설정 |

역할을 부여하는 것, 토큰에 역할을 내보내는 것, API가 그 역할을 권한으로 검사하는 것은 각각 확인해야 할 단계다. [Keycloak Server Administration Guide](https://www.keycloak.org/docs/latest/server_admin/index.html)

브라우저 앱은 배포된 코드 안의 고정된 비밀값을 안전하게 숨길 수 없으므로 Public Client로 다룬다. Keycloak JavaScript 연동에서는 `Client authentication`을 끄고, Standard Flow와 PKCE S256을 사용하는 흐름을 확인한다. Redirect URI와 Web Origins는 필요한 주소로 제한한다. Confidential Client는 자격증명을 보호할 수 있는 서버 등의 환경에서 구분해 사용한다. [Keycloak의 클라이언트 설정](https://www.keycloak.org/securing-apps/javascript-adapter)

## 4. 정상 흐름에서 네 장면을 관찰한다

처음에는 게이트웨이 없이 브라우저 앱·Keycloak·Spring API의 연결부터 확인한다. 일반 ID/PW 로그인과 Keycloak 로그인도 비교해 보면, 누가 비밀번호를 받고 누가 사용자 인증을 담당하는지 구분하기 쉽다. 일반 로그인이 자동으로 OAuth Password Grant가 되는 것은 아니다.

| 장면 | 관찰할 요청과 응답 | 설명할 수 있어야 하는 질문 |
|---|---|---|
| 인증 요청 | Authorization Endpoint와 요청 파라미터 | 누가 브라우저를 이동시키고 어떤 값을 보내는가? |
| 콜백 | 앱으로 돌아온 URL과 `code`, `state` | 누가 Code를 받고 요청과 응답을 연결하는가? |
| 토큰 교환 | Token Endpoint의 `code`, `code_verifier` | 누가 Code를 교환하고 Keycloak은 무엇을 검사하는가? |
| API 호출 | `Authorization: Bearer ...`와 응답 | 누가 토큰을 검증하고 권한을 판단하는가? |

브라우저 개발자 도구와 서버의 중단점을 함께 사용해 요청 흐름을 따라간다. Code·토큰·verifier는 실제 자격정보이므로 공개 글이나 저장소에는 실물 값을 남기지 않고 마스킹한 예시를 사용한다.

이 시리즈의 `http://localhost:3000`과 `http://localhost:8085`는 로컬 실습 주소다. 공개 환경의 인증·토큰·API 통신에는 HTTPS를 사용한다. [OAuth Bearer Token 보안 요구](https://www.rfc-editor.org/rfc/rfc6750.html#section-5)

## 5. 조건을 하나씩 바꿔 거부되는 이유를 확인한다

정상 동작을 확인한 뒤에는 한 번에 하나의 조건만 바꾼다. 아래는 실험 계획이며, 실제 응답과 오류 코드는 해당 설정에서 관찰해 기록해야 한다.

| 실험 | 확인하려는 책임 |
|---|---|
| 사용한 Code를 다시 교환 | Code의 일회용 성질과 재사용 거부 |
| 다른 `code_verifier`로 교환 | Code만 가진 요청자의 교환을 PKCE가 거부하는지 |
| 콜백의 `state` 변경 | 클라이언트가 요청과 맞지 않는 응답을 거부하는지 |
| 허용되지 않은 Redirect URI로 인증 요청 | Keycloak이 인증 결과의 전달 주소를 검사하는지 |
| 만료된 Access Token으로 API 요청 | API가 토큰 유효기간을 검사하는지 |
| 다른 API 대상의 토큰 제출 | 해당 API의 Audience 검사가 적용되는지 |
| USER로 ADMIN 전용 API 호출 | 유효한 토큰과 필요한 권한을 별도로 검사하는지 |

잘못된 Client Secret으로 토큰을 요청하는 실험은 **별도의 Confidential Client 환경**에서 다룬다. 이번 Public Client 예시에는 Client Secret이 없다. Implicit과 Password Grant는 과거 방식의 원리를 비교하는 대상으로 두며, 네 가지 Grant를 모두 구현할 필요는 없다. [OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700.html)

API 응답은 일반적으로 유효한 인증 정보가 없으면 401, 인증은 되었지만 권한이 부족하면 403으로 구분한다. 실제 결과는 보안 설정과 오류 처리에도 영향을 받으므로, 상태 코드와 함께 거부된 검증 조건을 확인한다. [Bearer Token 오류 응답](https://www.rfc-editor.org/rfc/rfc6750.html#section-3.1)

## 6. 게이트웨이와 배포는 흐름을 이해한 다음 확장한다

```text
처음 관찰할 구조
FinAccess ↔ Keycloak
FinAccess → Spring Boot API

이후 확장할 구조
FinAccess ↔ Keycloak
FinAccess → API7 Gateway → Spring Boot API

배포 확장
검증한 앱과 서버를 컨테이너·Kubernetes 환경으로 이동
```

API7은 이 예시에서 API 앞에 추가하는 게이트웨이다. 배치한다고 모든 인증과 업무 인가가 자동으로 해결되지는 않는다. 게이트웨이에서 검사할 조건, Spring에서 검사할 조건, Spring API에 직접 접근할 수 있는 경로를 구체적으로 정해야 한다.

## 7. 전체 개념을 하나의 요청에 붙여 본다

| 시점 | 연결되는 개념 |
|---|---|
| 앱이 API 접근 권한을 얻으려 함 | OAuth, Client, Resource Server |
| 사용자 인증 결과까지 표준화함 | OIDC, Keycloak |
| 인증 요청을 시작함 | Scope, Redirect URI, state, nonce, PKCE challenge |
| 인증 후 앱으로 돌아옴 | 리다이렉트, 콜백, Authorization Code |
| Code를 토큰으로 교환함 | Authorization Code Grant, verifier |
| 앱이 인증 결과를 확인함 | ID Token과 Claim 검증 |
| API를 호출함 | Access Token, Bearer |
| API가 토큰을 확인함 | JWT 서명, JWKS, iss·aud·exp 등 검증 |
| 작업을 허용할지 판단함 | 인가, Scope·Role·업무 정책 |
| 토큰을 갱신함 | Refresh Token |
| 다른 앱에서 기존 인증을 활용함 | SSO |

학습의 기준은 다음 질문을 같은 구조 안에서 끝까지 설명하는 것이다.

> 누가 인증하는가 → 누가 Code를 받는가 → 누가 토큰으로 교환하고 보관하는가 → 누가 API에 제출하는가 → 누가 검증하고 권한을 판단하는가.

## 시리즈 함께 읽기

1. [인증·인가와 OAuth의 역할, Grant 이해하기](oauth-oidc-keycloak-01-foundations.html)
2. [Authorization Code와 PKCE로 로그인 흐름 따라가기](oauth-oidc-keycloak-02-code-pkce.html)
3. [토큰의 용도와 JWT·Claim·Scope·Role 구분하기](oauth-oidc-keycloak-03-tokens-jwt.html)
4. [Spring API의 JWT 검증과 JWKS·Discovery 이해하기](oauth-oidc-keycloak-04-resource-server.html)
5. [세션 쿠키와 SSO를 구분하고 실습으로 연결하기](oauth-oidc-keycloak-05-sso-practice.html)
