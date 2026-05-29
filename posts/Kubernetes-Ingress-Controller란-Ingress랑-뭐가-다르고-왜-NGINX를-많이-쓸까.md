---
title: "[Kubernetes] Ingress Controller란? Ingress랑 뭐가 다르고 왜 NGINX를 많이 쓸까?"
source: "https://velog.io/@yorange50/Kubernetes-Ingress-Controller란-Ingress랑-뭐가-다르고-왜-NGINX를-많이-쓸까"
published: "2026-05-29T00:20:16.165Z"
tags: ""
backup_date: "2026-05-29T14:52:52.700583"
---

쿠버네티스에서 외부 트래픽을 다루다 보면 이런 흐름을 자주 본다.

```text
사용자
  ↓
Ingress
  ↓
Service
  ↓
Pod
```

처음에는 이렇게 이해한다.

> Ingress는 외부에서 들어온 HTTP/HTTPS 요청을
> 클러스터 내부 Service로 보내주는 입구다.

그런데 여기서 헷갈리는 지점이 생긴다.

```text
Ingress가 실제로 트래픽을 받는 건가?
Ingress Controller는 또 뭐지?
Ingress와 Ingress Controller는 같은 건가?
왜 NGINX Ingress Controller를 많이 쓰지?
```

결론부터 말하면 이렇다.

```text
Ingress
= 규칙

Ingress Controller
= 그 규칙을 실제로 동작시키는 실행자
```

이 차이를 잡아야 Ingress가 제대로 이해된다.

---

## 1. Ingress가 필요한 이유

쿠버네티스 안에는 여러 Service가 있을 수 있다.

```text
frontend-service
backend-service
admin-service
payment-service
```

이 Service들을 외부에 노출하려면 `NodePort`나 `LoadBalancer`를 쓸 수 있다.

예를 들어 Service마다 LoadBalancer를 붙이면 이런 구조가 된다.

```text
frontend-service → LoadBalancer 1개
backend-service  → LoadBalancer 1개
admin-service    → LoadBalancer 1개
payment-service  → LoadBalancer 1개
```

동작은 한다.

하지만 서비스가 많아질수록 복잡해진다.

```text
외부 IP가 여러 개 생김
LoadBalancer 비용이 늘어남
도메인별 라우팅이 복잡해짐
HTTPS 인증서 관리가 어려워짐
/api, /admin 같은 경로 기반 라우팅이 애매해짐
```

그래서 보통 HTTP/HTTPS 트래픽은 Ingress를 통해 한 곳으로 모은다.

```text
https://example.com        → frontend-service
https://example.com/api    → backend-service
https://admin.example.com  → admin-service
```

이런 식으로 도메인이나 경로에 따라 내부 Service로 나눠 보내는 역할을 Ingress가 담당한다.

---

## 2. Ingress란?

Ingress는 Kubernetes 리소스다.

즉 YAML로 만드는 객체다.

Ingress는 이런 규칙을 정의한다.

```text
어떤 도메인으로 들어왔는지
어떤 path로 들어왔는지
어느 Service로 보낼지
HTTPS 인증서는 어떤 Secret을 쓸지
```

예시를 보면 이렇다.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
spec:
  ingressClassName: nginx
  rules:
    - host: example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-service
                port:
                  number: 80
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: backend-service
                port:
                  number: 80
```

이 YAML의 의미는 이렇다.

```text
example.com/ 으로 들어오면 frontend-service로 보내라.
example.com/api 로 들어오면 backend-service로 보내라.
```

그런데 중요한 점이 있다.

Ingress 리소스는 **규칙만 가지고 있다.**

Ingress 자체가 실제로 외부 요청을 받아서 Service로 보내는 서버는 아니다.

---

## 3. Ingress Controller란?

Ingress Controller는 Ingress 리소스에 적힌 규칙을 읽고, 실제 외부 트래픽을 처리하는 컴포넌트다.

쉽게 말하면 이렇다.

```text
Ingress
= 교통 표지판에 적힌 규칙

Ingress Controller
= 실제로 차를 보내는 교통 경찰
```

또는 이렇게 볼 수 있다.

```text
Ingress
= 설정 파일

Ingress Controller
= 그 설정을 보고 동작하는 서버
```

Ingress Controller는 API Server를 계속 지켜본다.

```text
Ingress 리소스가 생겼나?
Ingress 규칙이 바뀌었나?
Service가 바뀌었나?
Endpoint가 바뀌었나?
TLS Secret이 바뀌었나?
```

그리고 그 정보를 바탕으로 실제 프록시 설정을 바꾼다.

예를 들어 NGINX Ingress Controller라면 내부적으로 NGINX 설정을 만든다.

```text
Ingress 리소스 감시
   ↓
host/path 규칙 확인
   ↓
Service와 Endpoint 확인
   ↓
NGINX 설정 생성
   ↓
외부 요청을 Service/Pod로 라우팅
```

즉 Ingress Controller는 외부 트래픽의 실제 입구다.

---

## 4. Ingress와 Ingress Controller 차이

가장 중요하니까 표로 정리하면 이렇다.

| 구분        | Ingress         | Ingress Controller                  |
| --------- | --------------- | ----------------------------------- |
| 정체        | Kubernetes 리소스  | 실제 동작하는 컨트롤러/프록시                    |
| 역할        | 라우팅 규칙 정의       | 규칙을 읽고 트래픽 처리                       |
| YAML로 생성  | 맞음              | 보통 Helm/YAML로 설치                    |
| 트래픽 직접 처리 | 안 함             | 함                                   |
| 예시        | `kind: Ingress` | NGINX Ingress Controller, Traefik 등 |
| 비유        | 메뉴판/규칙서         | 실제 요리사/실행자                          |

한 문장으로 정리하면 이렇다.

```text
Ingress는 “어떻게 보낼지”를 적어둔 규칙이고,
Ingress Controller는 그 규칙대로 실제 요청을 보내주는 실행자다.
```

그래서 Ingress 리소스만 만들고 Ingress Controller를 설치하지 않으면 트래픽은 처리되지 않는다.

```text
Ingress만 있음
→ 규칙만 있음
→ 실제 요청을 받아줄 컨트롤러가 없음
→ 외부 접속 안 됨
```

---

## 5. Ingress Controller가 Service들에게 하는 일

Ingress Controller가 Service에게 직접 뭔가를 “명령”하는 건 아니다.

더 정확히 말하면 Ingress Controller는 Service와 Endpoint 정보를 보고, 외부 요청을 적절한 Service 뒤의 Pod로 보내준다.

예를 들어 이런 규칙이 있다고 하자.

```text
example.com/api → backend-service
```

Ingress Controller는 이걸 보고 생각한다.

```text
example.com/api 요청이 들어오면
backend-service로 보내야 하는구나.
backend-service 뒤에는 어떤 Pod들이 있지?
Endpoint를 확인해야겠다.
```

Service는 selector로 Pod를 찾고, Endpoint 또는 EndpointSlice에는 실제 Pod IP 목록이 들어 있다.

```text
backend-service
  ↓
EndpointSlice
  ↓
10.42.0.11
10.42.0.12
10.42.0.13
```

Ingress Controller는 이 정보를 바탕으로 트래픽을 보낸다.

```text
외부 사용자
   ↓
Ingress Controller
   ↓
backend-service
   ↓
backend Pod
```

또는 구현에 따라 Service ClusterIP를 거치거나, Endpoint Pod IP로 직접 프록시할 수도 있다.

중요한 건 이것이다.

```text
Ingress Controller는 Service를 외부에 연결해주는 HTTP/HTTPS 입구 역할을 한다.
```

Ingress Controller가 Service들에게 해주는 일을 정리하면 이렇다.

```text
외부 URL을 Service와 연결
도메인 기반 라우팅
경로 기반 라우팅
HTTPS 인증서 처리
트래픽 로드밸런싱
요청을 내부 Service/Pod로 전달
```

---

## 6. 도메인 기반 라우팅

Ingress Controller는 요청의 Host를 보고 어느 Service로 보낼지 결정할 수 있다.

예를 들어 이런 구조다.

```text
app.example.com   → app-service
api.example.com   → api-service
admin.example.com → admin-service
```

Ingress YAML은 이런 식이다.

```yaml
rules:
  - host: app.example.com
    http:
      paths:
        - path: /
          pathType: Prefix
          backend:
            service:
              name: app-service
              port:
                number: 80

  - host: api.example.com
    http:
      paths:
        - path: /
          pathType: Prefix
          backend:
            service:
              name: api-service
              port:
                number: 80
```

즉 같은 Ingress Controller로 들어와도 도메인에 따라 다른 Service로 보낼 수 있다.

이걸 Virtual Hosting이라고도 한다.

---

## 7. 경로 기반 라우팅

도메인은 같고 path만 다르게 나눌 수도 있다.

```text
example.com/       → frontend-service
example.com/api    → backend-service
example.com/admin  → admin-service
```

예시는 이렇다.

```yaml
rules:
  - host: example.com
    http:
      paths:
        - path: /
          pathType: Prefix
          backend:
            service:
              name: frontend-service
              port:
                number: 80

        - path: /api
          pathType: Prefix
          backend:
            service:
              name: backend-service
              port:
                number: 80
```

이 구조를 쓰면 외부에서는 하나의 도메인처럼 보이지만, 내부에서는 여러 Service로 나눌 수 있다.

```text
사용자 입장
= example.com 하나

쿠버네티스 내부
= frontend-service, backend-service로 분리
```

---

## 8. HTTPS 인증서 처리

Ingress Controller는 HTTPS 인증서도 처리할 수 있다.

보통 인증서는 Kubernetes Secret에 저장한다.

```bash
kubectl create secret tls example-tls \
  --cert=example.crt \
  --key=example.key
```

Ingress에서는 이 Secret을 참조한다.

```yaml
spec:
  tls:
    - hosts:
        - example.com
      secretName: example-tls
```

이 뜻은 이렇다.

```text
example.com으로 HTTPS 요청이 들어오면
example-tls Secret의 인증서와 개인키를 사용해서
TLS 연결을 처리해라.
```

흐름은 보통 이렇게 된다.

```text
사용자
   ↓ HTTPS
Ingress Controller
   ↓ HTTP
Service
   ↓
Pod
```

즉 외부 구간은 HTTPS로 보호하고, Ingress Controller에서 TLS를 종료한 뒤 내부 Service로는 HTTP로 전달할 수 있다.

이걸 **TLS Termination**이라고 한다.

---

## 9. Ingress Controller의 종류

Ingress Controller는 하나만 있는 게 아니다.

대표적인 종류는 다음과 같다.

```text
NGINX Ingress Controller
Traefik
HAProxy Ingress
Contour
Istio Ingress Gateway
Kong Ingress Controller
Ambassador / Emissary
AWS Load Balancer Controller
GCE Ingress Controller
Azure Application Gateway Ingress Controller
```

종류가 많은 이유는 Ingress Controller가 결국 “외부 트래픽을 어떻게 받아서 내부로 보낼 것인가”를 구현하는 방식이기 때문이다.

각 환경마다 원하는 방식이 다르다.

```text
나는 NGINX 기반으로 단순하고 널리 쓰이는 걸 원함
나는 클라우드 로드밸런서와 직접 연동하고 싶음
나는 서비스 메시지와 같이 쓰고 싶음
나는 API Gateway 기능까지 원함
나는 동적 설정이 편한 컨트롤러를 원함
```

그래서 Ingress Controller도 여러 종류가 존재한다.

---

## 10. 대표 Ingress Controller 간단 비교

### NGINX Ingress Controller

가장 많이 접하는 Ingress Controller 중 하나다.

```text
NGINX 기반
자료가 많음
예제가 많음
커뮤니티 사용 사례가 많음
기본 HTTP/HTTPS 라우팅에 적합
```

쿠버네티스를 처음 공부할 때 가장 자주 보게 된다.

---

### Traefik

Traefik은 동적 라우팅과 클라우드 네이티브 환경에 강한 프록시다.

```text
설정 변경 반영이 빠름
Docker, Kubernetes와 잘 어울림
Let’s Encrypt 연동이 편리함
대시보드 제공
```

k3s에서는 Traefik이 기본 Ingress Controller로 설치되는 경우도 있다.

---

### HAProxy Ingress

HAProxy 기반이다.

```text
고성능 L7 프록시
오래된 로드밸런서 기술 기반
세밀한 트래픽 제어 가능
```

전통적인 로드밸런서 성격이 강하다.

---

### AWS Load Balancer Controller

AWS 환경에서 자주 쓴다.

Ingress를 만들면 AWS의 ALB와 연동된다.

```text
Kubernetes Ingress
   ↓
AWS Application Load Balancer 생성/설정
   ↓
외부 트래픽 처리
```

즉 클러스터 안의 NGINX가 트래픽을 받는 구조라기보다, AWS 관리형 로드밸런서를 적극적으로 사용하는 방식이다.

---

### GCE Ingress Controller

GKE에서 자주 쓰는 방식이다.

Google Cloud Load Balancer와 연동된다.

```text
GKE Ingress
   ↓
Google Cloud Load Balancer
   ↓
Service/Pod
```

클라우드 네이티브하게 외부 로드밸런서와 붙는 구조다.

---

### Istio Ingress Gateway

서비스 메시지인 Istio를 사용할 때 많이 나온다.

```text
mTLS
트래픽 정책
카나리 배포
세밀한 라우팅
서비스 메시지 연동
```

단순 Ingress보다 더 복잡한 트래픽 제어가 필요할 때 쓰인다.

---

### Kong Ingress Controller

Kong 기반이다.

API Gateway 성격이 강하다.

```text
인증
인가
Rate Limit
API Gateway 기능
플러그인
```

단순히 라우팅만 하는 게 아니라 API 관리 기능까지 필요할 때 사용한다.

---

## 11. 왜 NGINX Ingress Controller를 많이 쓸까?

처음 공부하거나 일반적인 환경에서는 NGINX Ingress Controller를 정말 많이 본다.

이유는 단순하다.

```text
익숙하다.
자료가 많다.
설치가 쉽다.
예제가 많다.
HTTP/HTTPS 라우팅에 충분하다.
운영 사례가 많다.
```

NGINX 자체가 웹 서버와 리버스 프록시로 오래 사용되어 왔다.

그래서 개발자와 인프라 엔지니어에게 익숙하다.

```text
NGINX
= 웹 서버
= 리버스 프록시
= 로드밸런서
= TLS 처리 가능
```

Ingress Controller가 해야 하는 일도 결국 이것과 비슷하다.

```text
외부 HTTP/HTTPS 요청 받기
Host/path 기준으로 라우팅하기
TLS 인증서 처리하기
백엔드 Service로 프록시하기
```

NGINX가 원래 잘하던 일과 Ingress Controller의 역할이 잘 맞는다.

---

## 12. NGINX를 많이 쓰는 현실적인 이유

### 1. 학습 자료가 많다

쿠버네티스 Ingress 예제를 검색하면 NGINX Ingress Controller 기반 예제가 매우 많다.

처음 공부할 때는 자료가 많은 게 중요하다.

에러가 나도 검색이 잘 된다.

```text
404
default backend
rewrite-target
ingressClassName
TLS secret
pathType
```

이런 문제를 만났을 때 NGINX Ingress 기준으로 자료가 많다.

---

### 2. 기본 기능이 충분하다

대부분의 일반적인 요구사항은 NGINX Ingress Controller로 처리할 수 있다.

```text
도메인 기반 라우팅
경로 기반 라우팅
TLS Termination
리다이렉트
rewrite
로드밸런싱
timeout 설정
body size 제한
```

처음부터 Istio나 Kong처럼 무거운 구성이 필요하지 않다면 NGINX로 충분한 경우가 많다.

---

### 3. NGINX 자체가 익숙하다

많은 서버 환경에서 이미 NGINX를 사용한다.

예를 들어 전통적인 서버 구성에서도 이런 구조가 흔하다.

```text
사용자
  ↓
NGINX
  ↓
Spring Boot / Node.js / Django
```

쿠버네티스에서도 비슷하다.

```text
사용자
  ↓
NGINX Ingress Controller
  ↓
Service
  ↓
Pod
```

이미 익숙한 구조가 쿠버네티스 안으로 들어온 느낌이라 이해하기 쉽다.

---

### 4. 설치와 실습이 쉽다

Helm으로 설치하기도 쉽다.

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  -n ingress-nginx \
  --create-namespace
```

설치 후에는 Controller Pod와 Service를 확인하면 된다.

```bash
kubectl get pod -n ingress-nginx
kubectl get svc -n ingress-nginx
```

실습 환경에서도 많이 쓰기 때문에 CKA나 쿠버네티스 학습 자료에서도 자주 나온다.

---

## 13. 그럼 무조건 NGINX가 정답일까?

그건 아니다.

NGINX Ingress Controller는 범용적으로 좋지만, 모든 상황의 정답은 아니다.

예를 들어 AWS에서 ALB 기능을 적극적으로 쓰고 싶다면 AWS Load Balancer Controller가 더 자연스럽다.

```text
AWS ALB
WAF 연동
ACM 인증서
Target Group
VPC 네트워크 통합
```

서비스 메시지를 쓰면서 세밀한 트래픽 정책이 필요하면 Istio Ingress Gateway가 더 맞을 수 있다.

```text
mTLS
카나리 라우팅
트래픽 미러링
서비스 메시지 정책
```

API Gateway 기능이 중요하면 Kong 같은 선택지도 있다.

```text
API Key
Rate Limit
인증/인가
플러그인
```

즉 선택 기준은 이렇다.

```text
일반적인 HTTP/HTTPS 라우팅과 학습 목적
→ NGINX Ingress Controller

AWS ALB와 강하게 연동
→ AWS Load Balancer Controller

GKE Load Balancer와 연동
→ GCE Ingress

서비스 메시지 기반 트래픽 제어
→ Istio Ingress Gateway

API Gateway 기능 중심
→ Kong Ingress Controller
```

---

## 14. Ingress Controller가 없으면 어떻게 될까?

Ingress 리소스만 만들었다고 해보자.

```bash
kubectl apply -f ingress.yaml
```

하지만 클러스터에 Ingress Controller가 없다면?

```text
Ingress 규칙은 존재함
하지만 그 규칙을 읽고 트래픽을 처리할 실행자가 없음
외부 요청이 Service로 전달되지 않음
```

즉 Ingress는 혼자서는 의미가 없다.

반드시 Ingress Controller가 있어야 한다.

확인 명령어는 보통 이렇게 본다.

```bash
kubectl get ingressclass
kubectl get pod -A | grep ingress
kubectl get svc -A | grep ingress
```

IngressClass도 중요하다.

```yaml
spec:
  ingressClassName: nginx
```

이 설정은 이 Ingress를 어떤 Controller가 처리할지 지정한다.

```text
ingressClassName: nginx
→ nginx Ingress Controller가 이 Ingress를 처리
```

---

## 15. 전체 흐름으로 이해하기

예를 들어 사용자가 이런 주소로 접속한다고 하자.

```text
https://example.com/api/users
```

전체 흐름은 이렇게 된다.

```text
1. 사용자가 https://example.com/api/users 접속
2. DNS가 example.com을 Ingress Controller의 외부 IP로 해석
3. 요청이 Ingress Controller로 들어옴
4. Ingress Controller가 TLS 인증서 처리
5. Host가 example.com인지 확인
6. Path가 /api인지 확인
7. Ingress 규칙에 따라 backend-service 선택
8. backend-service 뒤의 Pod로 요청 전달
```

그림으로 보면 이렇다.

```text
[사용자]
   |
   | HTTPS example.com/api/users
   v
[Ingress Controller]
   |
   | TLS 처리
   | host/path 라우팅
   v
[backend-service]
   |
   v
[backend Pod]
```

Ingress 리소스는 이 규칙을 정의한 것이다.

```text
example.com + /api
→ backend-service
```

Ingress Controller는 이 규칙을 실제로 실행한 것이다.

---

## 16. 한 번에 정리

Ingress와 Ingress Controller는 다르다.

```text
Ingress
= 외부 HTTP/HTTPS 요청을 어떤 Service로 보낼지 적어둔 규칙

Ingress Controller
= 그 규칙을 읽고 실제 트래픽을 처리하는 컴포넌트
```

Ingress Controller가 Service들에게 하는 일은 이렇다.

```text
외부 URL을 내부 Service에 연결
도메인 기반 라우팅
경로 기반 라우팅
HTTPS 인증서 처리
Service 뒤의 Pod로 트래픽 전달
```

Ingress Controller 종류는 많다.

```text
NGINX
Traefik
HAProxy
Contour
Kong
Istio Ingress Gateway
AWS Load Balancer Controller
GCE Ingress Controller
Azure Application Gateway Ingress Controller
```

그중 NGINX를 많이 쓰는 이유는 현실적이다.

```text
자료가 많다.
예제가 많다.
설치가 쉽다.
NGINX 자체가 익숙하다.
일반적인 HTTP/HTTPS 라우팅에 충분하다.
운영 사례가 많다.
```

처음 공부할 때는 이렇게 기억하면 된다.

```text
Ingress는 규칙이다.
Ingress Controller는 실행자다.
NGINX Ingress Controller는 가장 대중적인 실행자 중 하나다.
```

그리고 전체 흐름은 이렇게 잡으면 된다.

```text
사용자
  ↓
Ingress Controller
  ↓
Ingress 규칙 확인
  ↓
Service
  ↓
Pod
```

즉 Ingress Controller는 쿠버네티스에서 외부 HTTP/HTTPS 트래픽을 내부 Service로 안전하게 연결해주는 입구 관리자라고 보면 된다.
