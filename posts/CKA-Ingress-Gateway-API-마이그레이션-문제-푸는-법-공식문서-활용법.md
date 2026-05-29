---
title: "[CKA] Ingress → Gateway API 마이그레이션 문제 푸는 법 + 공식문서 활용법\n"
source: "https://velog.io/@yorange50/CKA-Ingress-Gateway-API-마이그레이션-문제-푸는-법-공식문서-활용법"
published: "2026-05-20T07:24:19.658Z"
tags: ""
backup_date: "2026-05-29T14:52:52.717292"
---

문제는 이거다.

```text id="2rsyau"
기존 Ingress web이 있다.
이걸 Gateway API로 마이그레이션해라.

GatewayClass 이름은 nginx다.

Gateway 이름은 web-gateway
hostname은 gateway.web.k8s.local

HTTPRoute 이름은 web-route
기존 Ingress web의 TLS/listener/routing rule을 유지해야 한다.

마지막에 curl 성공 확인 후 기존 Ingress web 삭제
```

처음 보면 YAML을 새로 만들어야 해서 어렵게 느껴진다.

근데 이 문제의 핵심은 YAML 암기가 아니다.

```text id="u9nx8j"
기존 Ingress를 읽고
그 안에 있는 값을
Gateway와 HTTPRoute로 옮기는 문제
```

다.

---

# 1. 문제 해석

문제에서 이미 알려준 값이 있다.

```text id="dop5fy"
GatewayClass name: nginx
Gateway name: web-gateway
Gateway hostname: gateway.web.k8s.local
HTTPRoute name: web-route
기존 Ingress name: web
```

그리고 기존 Ingress에서 뽑아와야 하는 값이 있다.

```text id="sltz7z"
TLS secret 이름
기존 path
기존 backend Service 이름
기존 backend Service port
```

즉 바로 YAML부터 쓰면 안 된다.

먼저 기존 Ingress를 확인해야 한다.

```bash id="9yf1ba"
kubectl get ingress web -o yaml
```

공식 kubectl Quick Reference에도 특정 리소스를 YAML로 보는 예시가 나온다. 예를 들어 `kubectl get pod my-pod -o yaml`처럼 `-o yaml`은 현재 리소스 설정을 YAML 형태로 확인할 때 쓰는 기본 패턴이다. 

---

# 2. 기존 Ingress에서 봐야 하는 부분

Ingress YAML에서 봐야 할 건 크게 두 군데다.

```yaml id="2b95cz"
spec:
  tls:
  - hosts:
    - web.k8s.local
    secretName: web-tls
  rules:
  - host: web.k8s.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

여기서 옮길 값은 이거다.

| Ingress 위치                       | Gateway API에서 들어갈 위치                             |
| -------------------------------- | ------------------------------------------------ |
| `spec.tls[].secretName`          | Gateway `listeners[].tls.certificateRefs[].name` |
| `spec.rules[].host`              | 문제에서는 `gateway.web.k8s.local`로 변경                |
| `spec.rules[].http.paths[].path` | HTTPRoute `rules[].matches[].path.value`         |
| `pathType: Prefix`               | HTTPRoute `PathPrefix`                           |
| `backend.service.name`           | HTTPRoute `backendRefs[].name`                   |
| `backend.service.port.number`    | HTTPRoute `backendRefs[].port`                   |

즉 Ingress를 Gateway API로 바꿀 때는 이렇게 생각하면 된다.

```text id="65hmo8"
Ingress의 TLS/도메인 입구 부분
→ Gateway

Ingress의 path/backend 라우팅 부분
→ HTTPRoute
```

---

# 3. Gateway API 구조 먼저 이해하기

Gateway API는 역할이 나뉜다.

공식문서에서는 Gateway API가 동적 인프라 프로비저닝과 고급 트래픽 라우팅을 위한 API 종류들의 모음이라고 설명하고, 대표적으로 `GatewayClass`, `Gateway`, `HTTPRoute` 같은 리소스를 사용한다고 정리한다. ([Kubernetes][1])

간단히 말하면:

```text id="vnqsyi"
GatewayClass
→ 어떤 Gateway Controller를 쓸지

Gateway
→ 외부에서 들어오는 입구, listener, hostname, TLS

HTTPRoute
→ Gateway로 들어온 HTTP 요청을 어느 Service로 보낼지
```

흐름은 이렇게 보면 된다.

```text id="y55a5t"
Client
  ↓
GatewayClass nginx가 관리하는 Gateway
  ↓
Gateway listener HTTPS 443
  ↓
HTTPRoute
  ↓
Service
  ↓
Pod
```

---

# 4. 공식문서에서는 어디를 봐야 하나

공식문서 검색창에서 이렇게 찾으면 된다.

```text id="xuhkqc"
Gateway API
```

또는

```text id="ufx2ju"
HTTPRoute
```

또는

```text id="if2afd"
Gateway
```

공식문서 경로는 보통 이쪽이다.

```text id="5izklh"
Documentation
  → Concepts
  → Services, Load Balancing, and Networking
  → Gateway API
```

들어간 뒤 페이지 안에서 `Ctrl + F`로 찾을 키워드는 이거다.

```text id="bzgpvm"
Gateway
HTTPRoute
listeners
certificateRefs
backendRefs
PathPrefix
Migrating from Ingress
```

Gateway API 공식문서에는 `GatewayClass`, `Gateway`, `HTTPRoute`의 관계가 설명되어 있고, HTTPRoute는 Gateway listener에서 backend endpoint, 보통 Service로 HTTP 트래픽을 매핑하는 규칙이라고 설명한다. ([Kubernetes][1])

즉 문서에서 복사해야 하는 YAML은 보통 두 종류다.

```text id="hmdvtu"
kind: Gateway
kind: HTTPRoute
```

---

# 5. Gateway YAML 작성

문제 조건:

```text id="c71ztc"
Gateway 이름: web-gateway
GatewayClass 이름: nginx
hostname: gateway.web.k8s.local
기존 Ingress의 TLS secret 유지
HTTPS 443 listener 유지
```

예시 YAML:

```yaml id="axxi01"
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: web-gateway
spec:
  gatewayClassName: nginx
  listeners:
  - name: https
    protocol: HTTPS
    port: 443
    hostname: gateway.web.k8s.local
    tls:
      mode: Terminate
      certificateRefs:
      - kind: Secret
        name: web-tls
```

여기서 `web-tls`는 예시다.

실제 시험에서는 반드시 기존 Ingress에서 확인한 값을 넣어야 한다.

```bash id="uqpovx"
kubectl get ingress web -o yaml
```

에서:

```yaml id="brh1uz"
spec:
  tls:
  - secretName: web-tls
```

이렇게 나온 값을 Gateway의 certificateRefs에 넣는다.

---

# 6. HTTPRoute YAML 작성

문제 조건:

```text id="vyma0t"
HTTPRoute 이름: web-route
hostname: gateway.web.k8s.local
기존 Ingress의 routing rule 유지
```

예시 YAML:

```yaml id="7z0z18"
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: web-route
spec:
  parentRefs:
  - name: web-gateway
  hostnames:
  - gateway.web.k8s.local
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /
    backendRefs:
    - name: web-service
      port: 80
```

여기서 중요한 건 세 가지다.

```text id="a9irqk"
parentRefs.name
→ 어느 Gateway에 붙을지

hostnames
→ 어떤 hostname 요청을 처리할지

backendRefs
→ 어느 Service로 보낼지
```

`web-service`와 `80`도 예시다.

반드시 기존 Ingress의 backend service를 보고 넣어야 한다.

---

# 7. 전체 풀이 순서

실전에서는 이렇게 간다.

## 1단계. GatewayClass 확인

문제에서 `nginx`가 있다고 했지만, 그래도 확인 가능하다.

```bash id="dh6kcn"
kubectl get gatewayclass
```

---

## 2단계. 기존 Ingress 확인

```bash id="kxfe42"
kubectl get ingress web -o yaml
```

여기서 확인할 것:

```text id="ufd4cj"
tls.secretName
rules.host
paths.path
paths.pathType
backend.service.name
backend.service.port.number
```

---

## 3단계. Gateway YAML 작성

```bash id="cd27v4"
vi web-gateway.yaml
```

```yaml id="wsbeml"
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: web-gateway
spec:
  gatewayClassName: nginx
  listeners:
  - name: https
    protocol: HTTPS
    port: 443
    hostname: gateway.web.k8s.local
    tls:
      mode: Terminate
      certificateRefs:
      - kind: Secret
        name: <기존 Ingress의 TLS secret 이름>
```

---

## 4단계. HTTPRoute YAML 작성

```bash id="xoitn6"
vi web-route.yaml
```

```yaml id="ucg8z6"
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: web-route
spec:
  parentRefs:
  - name: web-gateway
  hostnames:
  - gateway.web.k8s.local
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: <기존 Ingress의 path>
    backendRefs:
    - name: <기존 Ingress의 backend service 이름>
      port: <기존 Ingress의 backend service port>
```

---

## 5단계. 적용

```bash id="gcv3jo"
kubectl apply -f web-gateway.yaml
kubectl apply -f web-route.yaml
```

공식 kubectl 문서에서도 `kubectl apply -f ./my-manifest.yaml`은 manifest 파일로 리소스를 생성하거나 업데이트하는 기본 명령으로 나온다. 

---

## 6단계. 생성 확인

```bash id="h5q2w0"
kubectl get gateway
kubectl get httproute
```

더 자세히:

```bash id="qohs04"
kubectl describe gateway web-gateway
kubectl describe httproute web-route
```

---

## 7단계. curl 테스트

문제에서 준 명령어:

```bash id="3o58l0"
curl https://gateway.web.k8s.local
```

주의할 점은 문제에 적힌:

```text id="4ctyhv"
curl https: //gateway.web.k8s.local
```

이건 띄어쓰기 때문에 실제 명령어로는 틀리다.

실제는 붙여서 써야 한다.

```bash id="iymvrr"
curl https://gateway.web.k8s.local
```

---

## 8단계. 기존 Ingress 삭제

테스트 성공 후 삭제한다.

```bash id="azl54w"
kubectl delete ingress web
```

공식 kubectl Quick Reference에도 `kubectl delete -f`, `kubectl delete pod,service`처럼 리소스를 삭제하는 기본 패턴이 정리되어 있다. 

---

# 8. 이 문제에서 문서 활용하는 법

시험장에서 공식문서를 열면 이렇게 움직이면 된다.

```text id="9o29x2"
1. 검색창에 Gateway API 검색
2. Gateway API 문서 진입
3. Ctrl + F로 Gateway 검색
4. kind: Gateway 예시 확인
5. Ctrl + F로 HTTPRoute 검색
6. kind: HTTPRoute 예시 확인
7. 필요한 필드만 문제 조건에 맞게 수정
```

페이지 안에서 특히 찾을 키워드:

```text id="den7cv"
gatewayClassName
listeners
protocol
hostname
tls
certificateRefs
parentRefs
hostnames
matches
backendRefs
```

그리고 터미널에서는 이걸 같이 쓴다.

```bash id="xz3ewj"
kubectl explain gateway.spec
kubectl explain gateway.spec.listeners
kubectl explain httproute.spec
kubectl explain httproute.spec.rules
```

이렇게 하면 필드 구조가 헷갈릴 때 바로 확인 가능하다.

---

# 9. Ingress와 Gateway API 매핑표

이 문제는 이 표를 기억하면 거의 풀린다.

| 기존 Ingress                    | Gateway API                                          |
| ----------------------------- | ---------------------------------------------------- |
| `spec.ingressClassName`       | `GatewayClass` / `gatewayClassName`                  |
| `spec.tls.secretName`         | `Gateway.spec.listeners.tls.certificateRefs.name`    |
| `spec.rules.host`             | `Gateway.listener.hostname` 또는 `HTTPRoute.hostnames` |
| `spec.rules.http.paths.path`  | `HTTPRoute.rules.matches.path.value`                 |
| `pathType: Prefix`            | `type: PathPrefix`                                   |
| `backend.service.name`        | `HTTPRoute.backendRefs.name`                         |
| `backend.service.port.number` | `HTTPRoute.backendRefs.port`                         |

---

# 10. 왜 Gateway와 HTTPRoute를 나눌까

Ingress에서는 한 파일 안에 이런 것들이 섞여 있었다.

```text id="5zbisb"
TLS 설정
hostname
path routing
backend service
```

Gateway API는 이걸 나눈다.

```text id="8yslec"
Gateway
→ 입구 설정
→ listener
→ hostname
→ TLS

HTTPRoute
→ 라우팅 설정
→ path
→ backend service
```

그래서 문제를 풀 때도 이렇게 나눠 생각하면 된다.

```text id="v8lmoa"
HTTPS 443, TLS, hostname
→ Gateway에 작성

path, backend service, service port
→ HTTPRoute에 작성
```

---

# 11. 최종 템플릿

실전에서 빈칸만 채우면 되는 형태로 보면 이거다.

## Gateway

```yaml id="evk1m9"
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: web-gateway
spec:
  gatewayClassName: nginx
  listeners:
  - name: https
    protocol: HTTPS
    port: 443
    hostname: gateway.web.k8s.local
    tls:
      mode: Terminate
      certificateRefs:
      - kind: Secret
        name: <tls-secret-name>
```

## HTTPRoute

```yaml id="wf3nvd"
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: web-route
spec:
  parentRefs:
  - name: web-gateway
  hostnames:
  - gateway.web.k8s.local
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: <path>
    backendRefs:
    - name: <service-name>
      port: <service-port>
```

## 적용 및 검증

```bash id="pc59s0"
kubectl apply -f web-gateway.yaml
kubectl apply -f web-route.yaml

kubectl get gateway
kubectl get httproute

curl https://gateway.web.k8s.local

kubectl delete ingress web
```

---

# 마무리

이 문제는 외워서 푸는 문제가 아니다.

핵심은 이 흐름이다.

```text id="iyv0jr"
기존 Ingress 확인
→ TLS secret 확인
→ backend Service 확인
→ Gateway 작성
→ HTTPRoute 작성
→ curl 성공 확인
→ 기존 Ingress 삭제
```

그리고 문서 활용은 이렇게 하면 된다.

```text id="admon7"
Gateway API 문서에서 Gateway / HTTPRoute 예시 찾기
→ Ctrl + F로 certificateRefs, backendRefs 찾기
→ 기존 Ingress의 값을 옮겨 넣기
```

즉 이 문제의 본질은:

```text id="wj38ev"
Ingress YAML을 읽고
Gateway API의 두 리소스 구조로 분리해서 다시 쓰는 것
```

이다.

[1]: https://kubernetes.io/docs/concepts/services-networking/gateway/?utm_source=chatgpt.com "Gateway API"
