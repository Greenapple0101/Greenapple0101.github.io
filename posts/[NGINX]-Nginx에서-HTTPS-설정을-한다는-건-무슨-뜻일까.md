---
title: "[NGINX] Nginx에서 HTTPS 설정을 한다는 건 무슨 뜻일까?"
source: "https://velog.io/@yorange50/NGINX-Nginx에서-HTTPS-설정을-한다는-건-무슨-뜻일까"
published: "2026-05-18T04:57:30.299Z"
tags: ""
backup_date: "2026-05-29T14:52:52.729976"
---

Nginx에서 HTTPS 설정을 한다는 말은 단순히 “주소 앞에 `https://`를 붙인다”는 뜻이 아니다.

정확히 말하면, **클라이언트와 서버 사이의 통신을 암호화하고, Nginx가 그 HTTPS 요청을 받아 처리할 수 있도록 설정한다는 의미**다.

즉 사용자가 브라우저에서 다음처럼 접속했을 때,

```bash
https://example.com
```

브라우저와 서버 사이에 오가는 데이터가 평문이 아니라 암호화된 상태로 전달되도록 만드는 것이다.

---

## 1. HTTP와 HTTPS의 차이

먼저 HTTP는 기본적으로 암호화되지 않은 통신이다.

```text
사용자 브라우저
  ↓ HTTP 요청
서버
```

HTTP에서는 로그인 정보, 쿠키, 요청 데이터 등이 네트워크 중간에서 그대로 보일 수 있다.

예를 들어 사용자가 로그인 요청을 보낸다고 하면,

```text
id=hello
password=1234
```

같은 데이터가 암호화되지 않은 상태로 이동할 수 있다.

반면 HTTPS는 HTTP 위에 TLS 암호화 계층이 추가된 방식이다.

```text
사용자 브라우저
  ↓ HTTPS 요청
TLS 암호화
  ↓
서버
```

그래서 중간에서 누가 패킷을 훔쳐보더라도 실제 내용을 알아보기 어렵다.

정리하면 다음과 같다.

| 구분    | HTTP      | HTTPS      |
| ----- | --------- | ---------- |
| 기본 포트 | 80        | 443        |
| 암호화   | 없음        | 있음         |
| 주소    | `http://` | `https://` |
| 인증서   | 필요 없음     | 필요         |
| 보안성   | 낮음        | 높음         |

---

## 2. Nginx에서 HTTPS 설정을 한다는 의미

Nginx에서 HTTPS 설정을 한다는 것은 보통 다음 설정들을 해준다는 뜻이다.

```text
1. 443 포트로 요청을 받는다
2. TLS 인증서를 연결한다
3. TLS 프로토콜 버전을 지정한다
4. 암호화 방식(cipher)을 설정한다
5. 들어온 HTTPS 요청을 내부 애플리케이션으로 전달한다
```

즉 Nginx는 클라이언트의 HTTPS 요청을 가장 앞단에서 받아주는 역할을 한다.

```text
사용자
  ↓ HTTPS
Nginx
  ↓ HTTP 또는 HTTPS
Backend Server
```

운영 환경에서는 Nginx가 TLS 처리를 담당하고, 내부 서버로는 HTTP로 넘기는 구조도 많이 사용한다.

이걸 **TLS termination**이라고 한다.

---

## 3. TLS termination이란?

TLS termination은 말 그대로 **TLS 암호화 통신을 Nginx에서 끝낸다**는 뜻이다.

예를 들어 사용자가 HTTPS로 접속한다.

```text
사용자 브라우저
  ↓ HTTPS
Nginx
```

Nginx는 인증서를 이용해 HTTPS 요청을 복호화한다.

그 다음 내부 애플리케이션 서버로 요청을 전달한다.

```text
Nginx
  ↓ HTTP
Spring Boot / FastAPI / Node.js
```

전체 흐름은 다음과 같다.

```text
사용자 브라우저
  ↓ HTTPS 암호화 통신
Nginx
  ↓ HTTP 내부 통신
애플리케이션 서버
```

이 구조에서 HTTPS 처리는 Nginx가 담당한다.

그래서 Spring Boot, FastAPI, Node.js 같은 백엔드 애플리케이션은 직접 인증서를 들고 있을 필요가 없다.

---

## 4. 왜 Nginx에서 HTTPS를 처리할까?

백엔드 애플리케이션에서도 HTTPS 설정을 할 수는 있다.

하지만 운영 환경에서는 보통 Nginx 같은 웹 서버나 로드밸런서에서 HTTPS를 처리한다.

이유는 다음과 같다.

---

## 5. 첫 번째 이유: 인증서 관리를 한 곳에서 하기 위해

서비스가 커지면 내부 서버가 여러 개가 될 수 있다.

```text
Frontend Server
Backend Server
API Server
Admin Server
```

각 서버마다 HTTPS 인증서를 따로 설정하면 관리가 복잡해진다.

하지만 Nginx가 앞단에 있으면 인증서를 Nginx 한 곳에서 관리할 수 있다.

```text
사용자
  ↓ HTTPS
Nginx
  ├─ Frontend
  ├─ Backend
  └─ Admin
```

이렇게 하면 인증서 갱신, TLS 버전 설정, 보안 정책 변경을 한 곳에서 처리할 수 있다.

---

## 6. 두 번째 이유: 내부 서버를 숨기기 위해

사용자는 Nginx만 바라본다.

```text
https://example.com
```

하지만 실제 내부에는 여러 서버가 있을 수 있다.

```text
Nginx
  ├─ frontend:3000
  ├─ backend:8080
  └─ admin:9000
```

사용자는 `3000`, `8080`, `9000` 같은 내부 포트를 직접 알 필요가 없다.

외부에는 Nginx의 443 포트만 열어두고, 내부 서버들은 외부에 노출하지 않는 방식으로 보안을 높일 수 있다.

---

## 7. 세 번째 이유: Reverse Proxy 역할과 잘 맞기 때문

Nginx는 Reverse Proxy로 자주 사용된다.

Reverse Proxy는 클라이언트 요청을 대신 받아서 내부 서버로 전달하는 역할이다.

```text
사용자
  ↓
Nginx
  ↓
Backend Server
```

HTTPS 설정까지 Nginx가 담당하면 다음과 같은 구조가 된다.

```text
사용자
  ↓ HTTPS
Nginx
  ↓ HTTP
Backend Server
```

즉 Nginx는 다음 역할을 동시에 수행한다.

```text
HTTPS 처리
인증서 관리
요청 라우팅
로드밸런싱
정적 파일 서빙
Reverse Proxy
```

그래서 운영 환경에서 Nginx는 단순한 웹 서버라기보다 **외부 요청을 받는 입구** 역할을 한다.

---

## 8. Nginx HTTPS 설정 예시

Nginx에서 HTTPS를 설정하면 보통 이런 형태가 된다.

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/nginx/certs/example.crt;
    ssl_certificate_key /etc/nginx/certs/example.key;

    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://backend:8080;
    }
}
```

하나씩 보면 다음과 같다.

---

## 9. `listen 443 ssl`

```nginx
listen 443 ssl;
```

이 설정은 Nginx가 443 포트에서 HTTPS 요청을 받겠다는 뜻이다.

HTTP는 보통 80 포트, HTTPS는 보통 443 포트를 사용한다.

```text
HTTP  → 80
HTTPS → 443
```

`ssl` 옵션이 붙어 있기 때문에 이 서버 블록은 TLS/SSL 암호화 통신을 처리한다.

---

## 10. `server_name`

```nginx
server_name example.com;
```

이 설정은 어떤 도메인으로 들어온 요청을 이 server 블록에서 처리할지 정하는 부분이다.

예를 들어 사용자가 다음 주소로 접속하면,

```text
https://example.com
```

Nginx는 `server_name example.com;`에 해당하는 설정을 찾아 요청을 처리한다.

---

## 11. `ssl_certificate`

```nginx
ssl_certificate /etc/nginx/certs/example.crt;
```

이건 공개 인증서 파일 경로다.

브라우저는 이 인증서를 보고 다음을 확인한다.

```text
이 서버가 정말 example.com 서버가 맞는가?
신뢰할 수 있는 인증기관이 발급한 인증서인가?
인증서가 만료되지 않았는가?
```

---

## 12. `ssl_certificate_key`

```nginx
ssl_certificate_key /etc/nginx/certs/example.key;
```

이건 인증서에 대응되는 개인 키 파일이다.

개인 키는 절대 외부에 노출되면 안 된다.

인증서는 공개되어도 되지만, 개인 키는 서버 안에서 안전하게 보관해야 한다.

---

## 13. `ssl_protocols`

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
```

이 설정은 어떤 TLS 버전을 허용할지 정한다.

예전에는 TLSv1.0, TLSv1.1도 사용했지만 지금은 보안상 권장되지 않는다.

운영 환경에서는 보통 TLSv1.2 이상, 더 강하게는 TLSv1.3만 허용하기도 한다.

예를 들어 CKA 스타일 문제에서 “TLSv1.3만 허용하라”고 하면 다음처럼 설정하면 된다.

```nginx
ssl_protocols TLSv1.3;
```

이렇게 설정하면 TLSv1.2 이하로 접속하려는 클라이언트는 연결이 실패한다.

테스트는 이런 식으로 할 수 있다.

```bash
curl --tls-max 1.2 https://web.k8s.local
```

이 명령어는 “TLS 1.2까지만 사용해서 접속해봐”라는 뜻이다.

그런데 서버가 TLSv1.3만 허용하도록 설정되어 있다면, 이 요청은 실패해야 정상이다.

---

## 14. `proxy_pass`

```nginx
location / {
    proxy_pass http://backend:8080;
}
```

이 설정은 사용자가 `/` 경로로 들어왔을 때 내부 백엔드 서버로 요청을 넘기겠다는 뜻이다.

즉 외부 사용자는 HTTPS로 Nginx에 접속하지만,

```text
사용자
  ↓ HTTPS
Nginx
```

Nginx 뒤쪽에서는 내부 서버로 HTTP 요청을 보낼 수 있다.

```text
Nginx
  ↓ HTTP
backend:8080
```

그래서 전체 흐름은 다음과 같다.

```text
사용자 브라우저
  ↓ https://example.com
Nginx:443
  ↓ http://backend:8080
Backend Application
```

---

## 15. HTTP를 HTTPS로 리다이렉트하기

운영 환경에서는 사용자가 실수로 HTTP로 접속해도 HTTPS로 보내는 설정을 자주 한다.

```nginx
server {
    listen 80;
    server_name example.com;

    return 301 https://$host$request_uri;
}
```

이 설정은 80 포트로 들어온 HTTP 요청을 HTTPS 주소로 리다이렉트한다.

예를 들어 사용자가 이렇게 접속해도,

```text
http://example.com/login
```

자동으로 다음 주소로 이동한다.

```text
https://example.com/login
```

정리하면 다음 구조다.

```text
HTTP 요청
  ↓
Nginx:80
  ↓ 301 Redirect
HTTPS 주소로 이동
  ↓
Nginx:443
```

---

## 16. HTTPS 설정에서 인증서가 중요한 이유

HTTPS는 단순히 암호화만 하는 것이 아니다.

HTTPS에는 크게 두 가지 의미가 있다.

```text
1. 암호화
2. 서버 신원 확인
```

암호화는 중간에서 내용을 훔쳐보지 못하게 하는 것이고, 서버 신원 확인은 사용자가 접속한 서버가 진짜 서버인지 확인하는 것이다.

예를 들어 사용자가 은행 사이트에 접속한다고 해보자.

브라우저는 인증서를 확인해서 이 사이트가 진짜 은행 사이트인지 검증한다.

```text
사용자: 은행 사이트 접속
브라우저: 인증서 확인
인증기관: 신뢰 가능한 인증서인지 검증
```

그래서 HTTPS 설정에는 인증서가 반드시 필요하다.

---

## 17. Nginx HTTPS 설정과 Kubernetes ConfigMap

쿠버네티스 환경에서는 Nginx 설정을 ConfigMap으로 관리하는 경우가 많다.

예를 들어 `nginx-config`라는 ConfigMap에 Nginx 설정이 들어있을 수 있다.

```bash
kubectl edit configmap nginx-config -n nginx-static
```

또는 YAML로 수정 후 적용할 수도 있다.

```bash
kubectl apply -f nginx-config.yaml
```

ConfigMap을 수정했다고 해서 항상 Nginx가 바로 새 설정을 읽는 것은 아니다.

그래서 문제에서 이런 말이 자주 나온다.

```text
re-create, restart, or scale resources as necessary
```

즉 설정을 바꾼 뒤 필요하면 Pod를 재시작하거나 Deployment를 rollout restart 하라는 뜻이다.

예를 들어 Deployment가 `nginx-static`이라면 다음처럼 재시작할 수 있다.

```bash
kubectl rollout restart deployment nginx-static -n nginx-static
```

그 후 상태를 확인한다.

```bash
kubectl rollout status deployment nginx-static -n nginx-static
```

---

## 18. HTTPS 설정 확인 방법

설정이 제대로 적용됐는지 확인하려면 `curl`을 사용할 수 있다.

기본 HTTPS 요청 확인:

```bash
curl -k https://web.k8s.local
```

여기서 `-k`는 인증서 검증을 건너뛰겠다는 뜻이다.

테스트 환경에서는 자체 서명 인증서나 신뢰되지 않은 인증서를 쓰는 경우가 많아서 `-k`를 붙이는 경우가 있다.

TLSv1.2 이하 차단 확인:

```bash
curl --tls-max 1.2 https://web.k8s.local
```

TLSv1.3만 허용했다면 이 요청은 실패해야 한다.

TLSv1.3 접속 확인:

```bash
curl --tlsv1.3 https://web.k8s.local
```

이 요청은 성공해야 한다.

---

## 19. 정리

Nginx에서 HTTPS 설정을 한다는 것은 Nginx가 클라이언트의 암호화된 요청을 받을 수 있도록 만드는 것이다.

핵심은 다음과 같다.

```text
Nginx가 443 포트에서 HTTPS 요청을 받음
TLS 인증서를 사용함
허용할 TLS 버전을 설정함
암호화된 요청을 복호화함
내부 애플리케이션 서버로 요청을 전달함
```

운영 구조로 보면 이렇게 이해하면 된다.

```text
사용자
  ↓ HTTPS
Nginx
  ↓ HTTP 또는 HTTPS
Backend Server
```

즉 Nginx는 외부 요청의 입구이자, HTTPS 보안 처리를 담당하는 앞단 서버다.

그래서 HTTPS 설정은 단순히 보안 옵션 하나를 켜는 것이 아니라, **서비스의 외부 통신 방식을 안전하게 만드는 운영 설정**이라고 볼 수 있다.
