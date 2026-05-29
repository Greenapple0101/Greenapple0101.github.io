---
title: "[NGINX] /api/api 중복과 WebSocket 101 실패를 해결하며 프록시 경로를 정리한 이야기"
source: "https://velog.io/@yorange50/NGINX-apiapi-중복과-WebSocket-101-실패를-해결하며-프록시-경로를-정리한-이야기"
published: "2026-05-17T10:09:56.622Z"
tags: ""
backup_date: "2026-05-29T14:52:52.735321"
---

서비스를 배포하다 보면 로컬에서는 잘 되던 API 요청이 운영 서버에서는 실패하는 경우가 있다. 처음에는 백엔드 문제처럼 보인다. API 서버가 죽었는지, 포트가 막혔는지, CORS 문제인지부터 의심하게 된다. 그런데 실제 원인은 프론트엔드 요청 URL과 Nginx 프록시 경로가 서로 다르게 조합되면서 발생한 **경로 불일치 문제**였다. 여기에 실시간 기능을 위한 WebSocket 요청까지 포함되면서, 단순 HTTP 요청뿐 아니라 `Upgrade`, `Connection` 헤더까지 명시해야 하는 상황이 생겼다.

## 문제 상황

운영 환경에서 프론트엔드가 백엔드 API를 호출할 때 경로가 이상하게 만들어졌다.

예를 들어 원래 기대한 요청은 이거였다.

```text
/api/users
/api/posts
/api/chat
```

그런데 실제 브라우저 네트워크 탭에서 확인해보면 이런 요청이 나가고 있었다.

```text
/api/api/users
/api/api/posts
/api/api/chat
```

즉, `/api`가 두 번 붙었다.

이런 경우 백엔드에는 `/api/users` 엔드포인트만 있는데, 실제 요청은 `/api/api/users`로 들어가기 때문에 404가 발생할 수 있다.

```text
프론트엔드 요청 URL
→ /api/api/users

백엔드 실제 매핑
→ /api/users

결과
→ 경로 불일치
→ 404 또는 요청 실패
```

처음에는 백엔드 컨트롤러 매핑 문제처럼 보일 수 있다.
하지만 실제로는 프론트엔드와 Nginx가 각각 `/api`를 붙이면서 경로가 중복된 것이었다.

## 왜 /api/api가 생겼을까?

보통 운영 환경에서는 프론트엔드에서 API base URL을 이렇게 잡는다.

```js
const API_BASE_URL = "/api";
```

그리고 요청을 만들 때 이렇게 호출한다.

```js
fetch(`${API_BASE_URL}/users`);
```

그러면 최종 요청은 이렇게 된다.

```text
/api/users
```

여기까지는 정상이다.

그런데 Nginx에서도 프록시 경로를 잘못 잡으면 문제가 생긴다.

예를 들어 이런 설정이 있다고 해보자.

```nginx
location /api/ {
    proxy_pass http://backend:8080/api/;
}
```

이 설정은 들어온 `/api/users` 요청을 백엔드의 `/api/users`로 넘길 수도 있지만, 프론트에서 이미 `/api`를 붙이고 Nginx에서도 다시 `/api`를 붙이는 식으로 설정이 꼬이면 `/api/api/users` 같은 중복 경로가 발생할 수 있다.

즉, 핵심은 이거다.

```text
프론트엔드도 /api를 붙임
Nginx도 /api를 붙임
백엔드도 /api를 기준으로 매핑함

결과
/api/api 중복 발생
```

## 경로 규칙을 먼저 정해야 한다

이 문제를 해결하려면 먼저 기준을 정해야 한다.

```text
외부에서 보이는 API 경로는 /api로 통일한다.
Nginx는 /api 요청을 백엔드로 넘긴다.
백엔드가 /api를 포함해서 받을지, 제거된 경로를 받을지 결정한다.
프론트엔드는 정해진 규칙에 맞춰 URL을 조합한다.
```

예를 들어 가장 단순한 규칙은 이거다.

```text
브라우저 요청:
GET /api/users

Nginx:
location /api/ 로 받고 backend:8080으로 전달

백엔드:
@RequestMapping("/api/users") 또는 /api prefix 포함
```

이 경우 Nginx는 경로를 불필요하게 바꾸지 않는 쪽이 안전하다.

```nginx
location /api/ {
    proxy_pass http://backend:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

이렇게 하면 `/api/users` 요청이 백엔드에도 `/api/users`로 전달된다.

반대로 백엔드가 `/users`만 받는 구조라면 Nginx에서 `/api`를 제거해서 넘겨야 한다.

```nginx
location /api/ {
    proxy_pass http://backend:8080/;
}
```

이 경우 `/api/users`가 백엔드로는 `/users`처럼 전달될 수 있다.

중요한 건 둘 중 하나로 명확히 정하는 것이다.

```text
방식 A:
프론트 /api/users
→ Nginx /api/users 그대로 전달
→ 백엔드 /api/users

방식 B:
프론트 /api/users
→ Nginx가 /api 제거
→ 백엔드 /users
```

둘이 섞이면 `/api/api` 문제가 생긴다.

## WebSocket 101 실패란?

이번 문제에는 WebSocket도 있었다.

WebSocket 연결은 일반 HTTP 요청과 다르다.
처음에는 HTTP 요청처럼 시작하지만, 서버와 클라이언트가 연결을 업그레이드한다.

정상적으로 업그레이드되면 응답 코드가 `101 Switching Protocols`로 나온다.

```text
HTTP 요청
→ WebSocket 연결로 Upgrade
→ 101 Switching Protocols
→ 실시간 양방향 통신 시작
```

그런데 Nginx에서 WebSocket 프록시 설정이 빠져 있으면 이 업그레이드가 실패할 수 있다.

브라우저 네트워크 탭에서는 WebSocket 연결이 실패하거나, 400/404/502로 보일 수 있다.
또는 기대한 `101 Switching Protocols`가 나오지 않는다.

## WebSocket 프록시에는 Upgrade 헤더가 필요하다

WebSocket을 Nginx 뒤로 넘길 때는 아래 헤더가 중요하다.

```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

이 헤더들은 클라이언트가 요청한 HTTP 연결을 WebSocket 연결로 바꿔달라는 의미를 백엔드에 전달한다.

예를 들어 `/ws` 경로로 WebSocket을 사용한다면 Nginx 설정은 이런 식이 된다.

```nginx
location /ws/ {
    proxy_pass http://backend:8080;
    proxy_http_version 1.1;

    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

여기서 중요한 부분은 세 가지다.

```text
proxy_http_version 1.1
Upgrade 헤더
Connection upgrade 헤더
```

이 설정이 없으면 WebSocket 연결이 일반 HTTP 요청처럼 처리되거나, 업그레이드가 백엔드까지 전달되지 않아 실패할 수 있다.

## /api와 /ws 경로를 분리한 이유

API 요청과 WebSocket 요청은 성격이 다르다.

```text
/api
일반 HTTP API 요청

/ws
WebSocket 실시간 연결
```

그래서 Nginx에서도 경로를 분리하는 것이 좋다.

```nginx
location /api/ {
    proxy_pass http://backend:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

location /ws/ {
    proxy_pass http://backend:8080;
    proxy_http_version 1.1;

    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

이렇게 하면 일반 API와 실시간 연결을 각각 맞는 방식으로 프록시할 수 있다.

## 프론트엔드 URL 조합 규칙도 같이 정리해야 한다

Nginx만 고쳐서는 부족하다.
프론트엔드에서도 URL 조합 규칙을 정해야 한다.

예를 들어 API 요청은 이렇게 통일한다.

```js
const API_BASE_URL = "/api";

fetch(`${API_BASE_URL}/users`);
```

WebSocket은 이렇게 통일한다.

```js
const WS_BASE_URL = `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/ws`;
```

그러면 운영 환경에서는 같은 도메인 기준으로 요청이 나간다.

```text
API:
https://example.com/api/users

WebSocket:
wss://example.com/ws
```

개발 환경에서는 별도 환경변수로 나눌 수도 있다.

```env
VITE_API_BASE_URL=/api
VITE_WS_BASE_URL=/ws
```

중요한 건 프론트엔드에서 `/api`를 붙일지, Nginx에서 붙일지, 백엔드가 `/api`를 받을지 기준을 하나로 맞추는 것이다.

## 배포 후 검증 절차

이 문제를 겪고 나서는 배포 후 스모크 테스트 절차를 고정하는 것이 중요해졌다.

먼저 서버에서 API가 정상 응답하는지 확인한다.

```bash
curl -i http://localhost:8080/api/health
```

Nginx를 거친 외부 경로도 확인한다.

```bash
curl -i http://EC2_PUBLIC_IP/api/health
```

여기서 확인할 것은 단순히 200 여부만이 아니다.

```text
요청 경로가 /api/api로 중복되지 않는지
Nginx가 backend로 제대로 넘기는지
404가 아닌지
502가 아닌지
응답 헤더와 상태 코드가 정상인지
```

WebSocket은 브라우저 네트워크 탭에서 확인한다.

```text
Network 탭
→ WS 필터
→ 연결 상태 확인
→ Status Code 101 확인
```

정상이라면 WebSocket 요청은 `101 Switching Protocols`로 표시된다.

## 이 트러블슈팅의 핵심

이 문제는 단순히 “Nginx 설정 하나 고친 것”이 아니다.

핵심은 프론트엔드, Nginx, 백엔드가 모두 같은 경로 규칙을 공유해야 한다는 점이다.

```text
프론트엔드:
어떤 URL로 요청할지 결정

Nginx:
그 요청을 어떤 upstream으로 넘길지 결정

백엔드:
어떤 path를 매핑할지 결정
```

이 세 개 중 하나라도 어긋나면 문제가 생긴다.

```text
프론트는 /api/users 호출
Nginx는 /api를 또 붙임
백엔드는 /api/users만 받음

결과:
/api/api/users 발생
요청 실패
```

WebSocket도 마찬가지다.

```text
브라우저는 WebSocket Upgrade 요청
Nginx가 Upgrade 헤더 전달 안 함
백엔드는 WebSocket 연결로 인식 못 함

결과:
101 Switching Protocols 실패
실시간 기능 장애
```

## 포트폴리오 문장

이 경험은 이렇게 정리할 수 있다.

```text
운영 배포 환경에서 프론트엔드 API URL 조합 규칙과 Nginx 프록시 경로가 불일치하여 /api/api 중복 경로가 발생하고, WebSocket 연결에서 101 Switching Protocols 응답이 실패하는 문제가 있었습니다. 프론트엔드의 API/WS base URL 규칙과 Nginx의 /api, /ws 프록시 설정을 정렬하고, WebSocket 프록시를 위해 proxy_http_version 1.1 및 Upgrade/Connection 헤더를 명시했습니다. 이후 curl과 브라우저 Network 탭 기반의 배포 후 스모크 테스트 절차를 고정하여 실시간 기능을 포함한 운영 경로 안정성을 확보했습니다.
```

짧게 쓰면:

```text
FE URL 조합 규칙과 Nginx 프록시 경로 불일치로 /api/api 중복 및 WebSocket 101 실패가 발생했습니다. /api, /ws 경로를 정렬하고 Upgrade/Connection 헤더를 명시해 실시간 기능 포함 운영 경로를 안정화했으며, curl/브라우저 Network 탭 기반 스모크 테스트를 배포 검증 절차로 고정했습니다.
```

## 면접 답변 버전

면접에서는 이렇게 말하면 좋다.

```text
운영 환경에서 프론트엔드가 /api를 붙여 요청하고, Nginx 프록시 설정에서도 /api를 다시 붙이는 식으로 경로 규칙이 어긋나 /api/api 중복 경로가 발생했습니다. 그래서 프론트엔드의 base URL 조합 규칙과 Nginx의 location /api 설정을 맞췄습니다. 또 WebSocket은 일반 HTTP 프록시와 달리 Upgrade 과정이 필요해서 proxy_http_version 1.1, Upgrade, Connection 헤더를 명시했고, 배포 후 curl과 브라우저 Network 탭에서 API 응답과 WebSocket 101 상태를 확인하는 절차를 만들었습니다.
```

## 정리

이번 트러블슈팅은 Nginx가 왜 필요한지 설명하기 좋은 사례다.

Nginx는 단순히 앞단에 있는 웹서버가 아니라, 운영 환경에서 외부 요청을 받아 프론트와 백엔드로 정확히 넘겨주는 진입점이다.

```text
사용자
→ Nginx
→ /api 요청은 백엔드로 프록시
→ /ws 요청은 WebSocket 업그레이드 포함해서 백엔드로 프록시
→ 그 외 요청은 프론트 정적 파일 서빙
```

문제의 핵심은 이것이었다.

```text
프론트엔드 URL 조합 규칙
Nginx 프록시 경로
백엔드 라우팅 경로
WebSocket Upgrade 헤더
```

이 네 가지가 맞지 않으면 운영 배포 후 API나 실시간 기능이 깨질 수 있다.

한 줄로 정리하면 다음과 같다.

```text
/api/api 중복과 WebSocket 101 실패는 백엔드 로직 문제가 아니라, 프론트엔드 URL 조합과 Nginx 프록시 경로, WebSocket 업그레이드 설정이 정렬되지 않아 발생한 운영 경로 문제였다.
```