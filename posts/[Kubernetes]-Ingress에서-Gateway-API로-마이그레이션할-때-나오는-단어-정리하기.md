---
title: "[KUBERNETES] Ingress에서 Gateway API로 마이그레이션할 때 나오는 단어 정리하기"
source: "https://velog.io/@yorange50/KUBERNETES-Ingress에서-Gateway-API로-마이그레이션할-때-나오는-단어-정리하기"
published: "2026-05-18T05:31:51.102Z"
tags: ""
backup_date: "2026-05-29T14:52:52.729532"
---

Kubernetes에서 외부 사용자가 애플리케이션에 접근하게 만들 때 자주 나오는 개념이 있다. 바로 `Ingress`, `Gateway API`, `Gateway`, `HTTPRoute`, `TLS`, `Service`, `Pod` 같은 것들이다. 처음 보면 단어가 너무 많아서 헷갈리는데, 사실 흐름은 하나다.

```text
사용자 요청
  ↓
외부 진입점
  ↓
라우팅 규칙
  ↓
Service
  ↓
Pod
```

Ingress 방식에서는 외부 진입점과 라우팅 규칙을 `Ingress` 하나가 많이 담당했다. Gateway API 방식에서는 이 역할을 `Gateway`와 `HTTPRoute`로 나누어 관리한다.

---

# 1. Ingress

`Ingress`는 Kubernetes에서 외부 HTTP/HTTPS 요청을 내부 Service로 보내기 위한 리소스다.

쉽게 말하면 이런 역할이다.

```text
사용자
  ↓
Ingress
  ↓
Service
  ↓
Pod
```

예를 들어 사용자가 아래 주소로 접속한다고 하자.

```bash
https://web.k8s.local
```

Ingress는 이 요청을 받아서 내부의 특정 Service로 보내준다.

```text
https://web.k8s.local
  ↓
web-service:80
```

Ingress가 담당하는 대표 기능은 다음과 같다.

```text
Host 기반 라우팅
Path 기반 라우팅
TLS termination
Service로 트래픽 전달
```

예시 YAML은 이런 식이다.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web
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

여기서 중요한 정보는 다음이다.

```text
Ingress 이름: web
Host: web.k8s.local
TLS Secret: web-tls
Path: /
Backend Service: web-service
Backend Port: 80
```

Gateway API로 마이그레이션할 때는 이 정보들을 그대로 읽어서 옮겨야 한다.

---

# 2. Gateway API

`Gateway API`는 Ingress보다 더 확장성 있게 만들어진 Kubernetes 네트워크 API다.

Ingress가 하나의 리소스 안에 여러 역할을 담고 있었다면, Gateway API는 역할을 나누어 관리한다.

```text
GatewayClass
  ↓
Gateway
  ↓
HTTPRoute
  ↓
Service
  ↓
Pod
```

Ingress와 Gateway API를 비교하면 다음과 같다.

| 구분         | Ingress          | Gateway API            |
| ---------- | ---------------- | ---------------------- |
| 외부 진입점     | Ingress          | Gateway                |
| 라우팅 규칙     | Ingress 안의 rules | HTTPRoute              |
| 사용할 컨트롤러   | IngressClass     | GatewayClass           |
| TLS 설정     | Ingress의 tls     | Gateway의 listener.tls  |
| Backend 연결 | backend.service  | HTTPRoute의 backendRefs |

Gateway API는 Ingress보다 구조가 더 명확하다.

Ingress에서는 하나의 리소스가 너무 많은 일을 했다면, Gateway API에서는 다음처럼 나뉜다.

```text
GatewayClass: 어떤 컨트롤러를 쓸지
Gateway: 어떤 포트와 프로토콜로 받을지
HTTPRoute: 어떤 요청을 어디로 보낼지
Service: 어떤 Pod들로 연결할지
```

---

# 3. API Gateway

문제 설명에 `API Gateway`라는 말이 나오는데, Kubernetes 문맥에서는 보통 `Gateway API`와 연결해서 이해하면 된다.

API Gateway는 클라이언트 요청을 받아서 내부 서비스로 전달하는 진입점이다.

단순 라우팅만 하는 게 아니라, 운영 환경에서는 다음 같은 기능도 붙을 수 있다.

```text
TLS termination
Rate Limiting
Throttle
IP 차단
인증
인가
쿼터 관리
트래픽 분리
요청 정책 적용
```

다만 CKA 문제에서는 너무 복잡하게 생각하면 안 된다.

이 문제에서 중요한 건 이것이다.

```text
기존 Ingress의 설정을 Gateway API 방식으로 옮긴다
```

즉, 실제 시험에서는 Rate Limiting이나 인증 설정을 직접 구현하는 문제가 아니라, `Ingress → Gateway + HTTPRoute`로 바꾸는 문제다.

---

# 4. GatewayClass

`GatewayClass`는 Gateway가 어떤 컨트롤러를 사용할지 지정하는 리소스다.

Ingress에 `IngressClass`가 있다면, Gateway API에는 `GatewayClass`가 있다.

문제에서는 이렇게 주어진다.

```text
A GatewayClass name nginx is installed in the cluster.
```

즉, 클러스터에 이미 `nginx`라는 GatewayClass가 존재한다는 뜻이다.

확인 명령어는 다음과 같다.

```bash
kubectl get gatewayclass
```

출력 예시는 다음과 비슷하다.

```text
NAME    CONTROLLER
nginx   example.com/nginx-gateway-controller
```

Gateway를 만들 때는 이 GatewayClass 이름을 써야 한다.

```yaml
spec:
  gatewayClassName: nginx
```

즉, 이 문제에서는 `gatewayClassName`에 다른 값을 쓰면 안 된다.

```yaml
gatewayClassName: nginx
```

---

# 5. Gateway

`Gateway`는 외부 요청을 실제로 받아들이는 진입점이다.

Ingress로 치면 다음 역할과 비슷하다.

```text
어떤 hostname으로 받을지
어떤 port로 받을지
HTTP인지 HTTPS인지
TLS 인증서를 쓸지
```

예를 들어 문제에서는 Gateway를 이렇게 만들라고 한다.

```text
Gateway name: web-gateway
Hostname: gateway.web.k8s.local
기존 Ingress의 TLS와 listener 설정 유지
```

Gateway YAML은 이런 식이다.

```yaml
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

Gateway에서 핵심은 `listeners`다.

Gateway는 이렇게 말하는 리소스라고 보면 된다.

```text
나는 gateway.web.k8s.local 이라는 hostname으로
443번 포트에서
HTTPS 요청을 받을 거고
TLS 인증서는 web-tls Secret을 사용할 거야
```

---

# 6. Listener

`Listener`는 Gateway가 어떤 요청을 받을지 정의하는 설정이다.

예를 들어 다음 부분이 Listener다.

```yaml
listeners:
- name: https
  protocol: HTTPS
  port: 443
  hostname: gateway.web.k8s.local
```

각 필드의 의미는 다음과 같다.

| 필드         | 의미          |
| ---------- | ----------- |
| `name`     | listener 이름 |
| `protocol` | 받을 프로토콜     |
| `port`     | 열어둘 포트      |
| `hostname` | 받을 도메인 이름   |
| `tls`      | TLS 인증서 설정  |

예를 들어 이런 설정이면:

```yaml
protocol: HTTPS
port: 443
hostname: gateway.web.k8s.local
```

의미는 다음이다.

```text
gateway.web.k8s.local 주소로 들어오는 HTTPS 요청을 443번 포트에서 받겠다
```

---

# 7. HTTPRoute

`HTTPRoute`는 Gateway로 들어온 HTTP/HTTPS 요청을 어떤 Service로 보낼지 정하는 리소스다.

Ingress의 `rules`와 비슷한 역할이다.

Ingress에서는 라우팅 규칙이 이런 식이었다.

```yaml
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

Gateway API에서는 이것을 `HTTPRoute`로 분리한다.

```yaml
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

HTTPRoute는 이렇게 말하는 리소스다.

```text
web-gateway로 들어온 요청 중에서
hostname이 gateway.web.k8s.local이고
path가 / 로 시작하는 요청은
web-service의 80번 포트로 보내라
```

---

# 8. parentRefs

`parentRefs`는 이 HTTPRoute가 어떤 Gateway에 붙을지 지정하는 설정이다.

```yaml
parentRefs:
- name: web-gateway
```

이 의미는 다음이다.

```text
이 HTTPRoute는 web-gateway Gateway에 연결된다
```

즉, Gateway와 HTTPRoute를 연결하는 다리 역할이다.

구조로 보면 이렇게 된다.

```text
Gateway: web-gateway
  ↓ parentRefs
HTTPRoute: web-route
```

만약 `parentRefs`를 잘못 쓰면 HTTPRoute가 Gateway에 붙지 않는다. 그러면 라우팅도 동작하지 않는다.

---

# 9. hostnames

`hostnames`는 HTTPRoute가 처리할 hostname을 의미한다.

```yaml
hostnames:
- gateway.web.k8s.local
```

이 설정은 다음과 같은 뜻이다.

```text
Host 헤더가 gateway.web.k8s.local인 요청만 이 HTTPRoute가 처리한다
```

Gateway에도 `hostname`이 있고, HTTPRoute에도 `hostnames`가 있다.

```yaml
Gateway:
  hostname: gateway.web.k8s.local

HTTPRoute:
  hostnames:
  - gateway.web.k8s.local
```

둘 다 맞아야 요청이 제대로 연결된다.

---

# 10. rules

`rules`는 HTTPRoute의 실제 라우팅 규칙이다.

```yaml
rules:
- matches:
  - path:
      type: PathPrefix
      value: /
  backendRefs:
  - name: web-service
    port: 80
```

이 의미는 다음이다.

```text
/ 로 시작하는 요청을 web-service:80으로 보내라
```

rules 안에는 크게 두 가지가 있다.

```text
matches: 어떤 요청을 잡을지
backendRefs: 어디로 보낼지
```

---

# 11. matches

`matches`는 어떤 요청을 매칭할지 정하는 조건이다.

```yaml
matches:
- path:
    type: PathPrefix
    value: /
```

이 설정은 다음과 같은 뜻이다.

```text
path가 / 로 시작하는 요청을 매칭한다
```

예를 들어 `PathPrefix /`는 다음 요청들을 모두 포함한다.

```text
/
 /login
 /boards
 /api/users
```

다만 실제 YAML에서는 공백 없이 이렇게 이해하면 된다.

```text
/
 /login
 /boards
 /api/users
```

실제 요청 path가 `/boards`여도 `/`로 시작하기 때문에 매칭된다.

---

# 12. PathPrefix

`PathPrefix`는 경로가 특정 값으로 시작하면 매칭하는 방식이다.

```yaml
type: PathPrefix
value: /
```

의미는 다음이다.

```text
/ 로 시작하는 모든 요청
```

Ingress에서는 보통 이렇게 되어 있다.

```yaml
pathType: Prefix
```

Gateway API에서는 이것을 이렇게 바꾼다.

```yaml
type: PathPrefix
```

즉, 매핑하면 다음과 같다.

| Ingress            | Gateway API        |
| ------------------ | ------------------ |
| `pathType: Prefix` | `type: PathPrefix` |

---

# 13. backendRefs

`backendRefs`는 요청을 최종적으로 보낼 Backend를 지정한다.

대부분 Service를 가리킨다.

```yaml
backendRefs:
- name: web-service
  port: 80
```

이 의미는 다음이다.

```text
요청을 web-service의 80번 포트로 보내라
```

중요한 점은 `backendRefs.name`에는 Pod 이름이나 Deployment 이름을 넣는 게 아니라는 것이다.

넣어야 하는 것은 Service 이름이다.

```text
정답: Service 이름
오답: Pod 이름
오답: Deployment 이름
오답: 컨테이너 이름
```

확인 명령어는 다음이다.

```bash
kubectl get svc
```

또는 기존 Ingress에서 backend service 이름을 확인할 수 있다.

```bash
kubectl get ingress web -o jsonpath='{.spec.rules[0].http.paths[0].backend.service.name}'
```

---

# 14. Service

`Service`는 Pod 앞에 있는 고정된 네트워크 진입점이다.

Pod는 생성되고 삭제되면서 IP가 바뀔 수 있다. 그래서 외부에서 Pod IP를 직접 바라보는 방식은 안정적이지 않다.

Service는 이런 문제를 해결한다.

```text
Service
  ↓
Pod 1
Pod 2
Pod 3
```

즉, 사용자는 Service로 요청하고, Service가 뒤에 있는 Pod들로 트래픽을 보내준다.

Gateway API에서도 최종 목적지는 보통 Service다.

```yaml
backendRefs:
- name: web-service
  port: 80
```

이 뜻은 다음이다.

```text
web-service라는 Service로 요청을 전달한다
```

---

# 15. Pod

`Pod`는 Kubernetes에서 애플리케이션이 실제로 실행되는 최소 단위다.

컨테이너는 Pod 안에서 실행된다.

```text
Pod
  └─ Container
```

웹 애플리케이션이 실제로 돌아가는 곳은 Pod다.

하지만 Gateway나 Ingress는 보통 Pod를 직접 바라보지 않는다.

흐름은 보통 이렇게 간다.

```text
Gateway
  ↓
HTTPRoute
  ↓
Service
  ↓
Pod
```

즉, Gateway API는 직접 Pod로 보내는 게 아니라 Service를 통해 Pod로 보낸다.

---

# 16. TLS

`TLS`는 HTTPS 통신을 가능하게 해주는 암호화 기술이다.

우리가 웹사이트에 접속할 때 주소가 `https://`로 시작하면 TLS가 사용된다.

```text
HTTP  = 암호화 없음
HTTPS = HTTP + TLS
```

Kubernetes에서 HTTPS를 쓰려면 인증서가 필요하다.

Ingress에서는 다음처럼 TLS 설정이 들어간다.

```yaml
tls:
- hosts:
  - web.k8s.local
  secretName: web-tls
```

Gateway API에서는 이 설정을 Gateway의 listener 안으로 옮긴다.

```yaml
tls:
  mode: Terminate
  certificateRefs:
  - kind: Secret
    name: web-tls
```

---

# 17. TLS termination

`TLS termination`은 HTTPS 요청을 Gateway나 Ingress에서 복호화한다는 뜻이다.

사용자는 HTTPS로 접속한다.

```text
사용자
  ↓ HTTPS
Gateway
```

Gateway는 TLS 인증서를 사용해서 HTTPS 요청을 풀어낸다.

그 뒤 내부 Service로는 HTTP로 보낼 수도 있다.

```text
사용자
  ↓ HTTPS
Gateway에서 TLS 종료
  ↓ HTTP
Service
  ↓
Pod
```

`tls.mode: Terminate`는 바로 이 의미다.

```yaml
tls:
  mode: Terminate
```

즉, Gateway에서 TLS를 종료하겠다는 뜻이다.

---

# 18. Secret

`Secret`은 Kubernetes에서 민감한 정보를 저장하는 리소스다.

예를 들어 다음 같은 정보를 저장할 수 있다.

```text
TLS 인증서
TLS 개인키
비밀번호
토큰
API Key
```

Ingress에서 HTTPS를 사용하려면 보통 TLS 인증서가 Secret에 들어 있다.

```yaml
secretName: web-tls
```

Gateway API에서는 이 Secret을 `certificateRefs`로 참조한다.

```yaml
certificateRefs:
- kind: Secret
  name: web-tls
```

즉, Ingress에서 쓰던 TLS Secret을 Gateway에서도 그대로 사용하면 된다.

---

# 19. certificateRefs

`certificateRefs`는 Gateway가 사용할 TLS 인증서 Secret을 지정하는 부분이다.

```yaml
certificateRefs:
- kind: Secret
  name: web-tls
```

의미는 다음이다.

```text
TLS 인증서는 web-tls라는 Secret에서 가져와라
```

Ingress에서는 이렇게 썼다.

```yaml
secretName: web-tls
```

Gateway에서는 이렇게 쓴다.

```yaml
certificateRefs:
- kind: Secret
  name: web-tls
```

매핑하면 다음과 같다.

| Ingress               | Gateway                         |
| --------------------- | ------------------------------- |
| `secretName: web-tls` | `certificateRefs.name: web-tls` |

---

# 20. hostname

`hostname`은 요청을 받을 도메인 이름이다.

예를 들어 문제에서는 다음 hostname을 사용한다.

```text
gateway.web.k8s.local
```

Gateway에서는 이렇게 쓴다.

```yaml
hostname: gateway.web.k8s.local
```

HTTPRoute에서는 이렇게 쓴다.

```yaml
hostnames:
- gateway.web.k8s.local
```

주의할 점은 기존 Ingress의 hostname이 `web.k8s.local`이어도, 문제에서 새 hostname을 `gateway.web.k8s.local`로 지정했다면 새 hostname을 써야 한다는 것이다.

---

# 21. protocol

`protocol`은 Gateway listener가 어떤 프로토콜을 받을지 정하는 값이다.

```yaml
protocol: HTTPS
```

이 설정은 다음 뜻이다.

```text
HTTPS 요청을 받겠다
```

자주 볼 수 있는 프로토콜은 다음과 같다.

```text
HTTP
HTTPS
TCP
TLS
UDP
```

이 문제에서는 curl 테스트가 HTTPS이므로 `HTTPS`를 사용한다.

```bash
curl https://gateway.web.k8s.local
```

따라서 Gateway listener도 HTTPS여야 한다.

```yaml
protocol: HTTPS
port: 443
```

---

# 22. port

`port`는 요청을 받을 포트 번호다.

HTTPS의 기본 포트는 443이다.

```yaml
port: 443
```

즉, 다음 요청은 기본적으로 443 포트로 간다.

```bash
curl https://gateway.web.k8s.local
```

반면 HTTP의 기본 포트는 80이다.

```text
HTTP  → 80
HTTPS → 443
```

Gateway에서는 외부 요청을 받을 포트를 설정하고, HTTPRoute의 `backendRefs.port`에서는 Service로 보낼 포트를 설정한다.

```yaml
Gateway listener port: 443
HTTPRoute backendRefs port: 80
```

이 둘은 서로 다를 수 있다.

```text
외부에서는 HTTPS 443으로 받고
내부 Service로는 80으로 전달
```

---

# 23. curl

`curl`은 터미널에서 HTTP/HTTPS 요청을 보내는 명령어다.

이 문제에서는 Gateway API 설정이 잘 되었는지 확인할 때 사용한다.

```bash
curl https://gateway.web.k8s.local
```

인증서 검증 오류가 난다면 `-k` 옵션을 붙여볼 수 있다.

```bash
curl -k https://gateway.web.k8s.local
```

`-k`는 TLS 인증서 검증을 건너뛰는 옵션이다.

실습 환경에서는 self-signed 인증서를 쓰는 경우가 많아서 `-k`가 필요한 경우가 있다.

---

# 24. kubectl

`kubectl`은 Kubernetes 클러스터를 조작하는 CLI 도구다.

리소스를 조회하거나, 생성하거나, 삭제할 때 사용한다.

Ingress 확인:

```bash
kubectl get ingress web -o yaml
```

Gateway 적용:

```bash
kubectl apply -f web-gateway.yaml
```

HTTPRoute 적용:

```bash
kubectl apply -f web-route.yaml
```

Ingress 삭제:

```bash
kubectl delete ingress web
```

줄여서 `k` alias를 쓰기도 한다.

```bash
alias k=kubectl
```

그러면 이렇게 쓸 수 있다.

```bash
k get ingress web -o yaml
```

---

# 25. kubectl get

`kubectl get`은 리소스를 조회하는 명령어다.

```bash
kubectl get ingress
kubectl get gateway
kubectl get httproute
kubectl get svc
```

특정 리소스 하나만 볼 수도 있다.

```bash
kubectl get ingress web
```

YAML 형태로 자세히 보고 싶으면 `-o yaml`을 붙인다.

```bash
kubectl get ingress web -o yaml
```

---

# 26. kubectl apply

`kubectl apply`는 YAML 파일에 적힌 리소스를 클러스터에 반영하는 명령어다.

```bash
kubectl apply -f web-gateway.yaml
kubectl apply -f web-route.yaml
```

`-f`는 file을 의미한다.

```text
-f web-gateway.yaml
= web-gateway.yaml 파일을 적용하겠다
```

---

# 27. kubectl delete

`kubectl delete`는 리소스를 삭제하는 명령어다.

이 문제에서는 Gateway API 설정이 정상 동작하는지 확인한 뒤 기존 Ingress를 삭제해야 한다.

```bash
kubectl delete ingress web
```

주의할 점은 테스트 전에 삭제하면 안 된다는 것이다.

순서는 이렇게 가야 한다.

```text
Gateway 생성
HTTPRoute 생성
curl 테스트
Ingress 삭제
```

---

# 28. YAML

`YAML`은 Kubernetes 리소스를 정의할 때 자주 사용하는 파일 형식이다.

예를 들어 Gateway는 이렇게 YAML로 작성한다.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: web-gateway
spec:
  gatewayClassName: nginx
```

Kubernetes YAML은 보통 네 가지 큰 구조를 가진다.

```text
apiVersion
kind
metadata
spec
```

---

# 29. apiVersion

`apiVersion`은 이 리소스가 어떤 Kubernetes API 버전을 사용할지 나타낸다.

Gateway API에서는 다음을 사용한다.

```yaml
apiVersion: gateway.networking.k8s.io/v1
```

Ingress에서는 보통 다음을 사용한다.

```yaml
apiVersion: networking.k8s.io/v1
```

즉, 리소스 종류에 따라 apiVersion이 다르다.

---

# 30. kind

`kind`는 어떤 종류의 Kubernetes 리소스를 만들지 지정한다.

예를 들어 Gateway를 만들려면:

```yaml
kind: Gateway
```

HTTPRoute를 만들려면:

```yaml
kind: HTTPRoute
```

Ingress를 만들려면:

```yaml
kind: Ingress
```

Service라면:

```yaml
kind: Service
```

---

# 31. metadata

`metadata`는 리소스의 이름, 라벨, 네임스페이스 같은 기본 정보를 담는 부분이다.

```yaml
metadata:
  name: web-gateway
```

여기서 `name`은 리소스 이름이다.

문제에서 Gateway 이름을 `web-gateway`라고 했으므로 이렇게 작성한다.

```yaml
metadata:
  name: web-gateway
```

HTTPRoute 이름은 `web-route`다.

```yaml
metadata:
  name: web-route
```

---

# 32. spec

`spec`은 리소스의 실제 원하는 상태를 적는 부분이다.

예를 들어 Gateway의 spec은 다음과 같다.

```yaml
spec:
  gatewayClassName: nginx
  listeners:
  - name: https
    protocol: HTTPS
    port: 443
```

이 뜻은 다음이다.

```text
nginx GatewayClass를 사용하고
HTTPS 443 포트 listener를 만들겠다
```

Kubernetes에서는 보통 `spec`에 “내가 원하는 상태”를 적는다.

---

# 33. backend

`backend`는 요청을 최종적으로 넘겨줄 대상이다.

Ingress에서는 다음처럼 쓴다.

```yaml
backend:
  service:
    name: web-service
    port:
      number: 80
```

Gateway API의 HTTPRoute에서는 다음처럼 쓴다.

```yaml
backendRefs:
- name: web-service
  port: 80
```

둘 다 의미는 같다.

```text
요청을 web-service의 80번 포트로 보내라
```

---

# 34. Routing Rule

`Routing Rule`은 어떤 요청을 어디로 보낼지 정하는 규칙이다.

예를 들어 이런 규칙이 있다고 하자.

```text
gateway.web.k8s.local/ 로 들어온 요청
→ web-service:80으로 전달
```

이게 라우팅 규칙이다.

Ingress에서는 `rules` 안에 있다.

```yaml
rules:
- host: web.k8s.local
  http:
    paths:
    - path: /
      backend:
        service:
          name: web-service
```

Gateway API에서는 HTTPRoute가 이 역할을 한다.

```yaml
rules:
- matches:
  - path:
      type: PathPrefix
      value: /
  backendRefs:
  - name: web-service
    port: 80
```

---

# 35. Host 기반 라우팅

Host 기반 라우팅은 도메인 이름을 기준으로 요청을 나누는 방식이다.

예를 들어:

```text
api.example.com    → api-service
admin.example.com  → admin-service
web.example.com    → web-service
```

이렇게 hostname에 따라 다른 Service로 보낼 수 있다.

이 문제에서는 hostname이 다음이다.

```text
gateway.web.k8s.local
```

Gateway와 HTTPRoute 모두 이 hostname을 사용한다.

---

# 36. Path 기반 라우팅

Path 기반 라우팅은 URL 경로를 기준으로 요청을 나누는 방식이다.

예를 들어:

```text
/        → frontend-service
/api     → api-service
/admin   → admin-service
```

Ingress에서는 `path`와 `pathType`으로 설정한다.

```yaml
path: /
pathType: Prefix
```

HTTPRoute에서는 `matches.path`로 설정한다.

```yaml
path:
  type: PathPrefix
  value: /
```

---

# 37. Rate Limiting

`Rate Limiting`은 일정 시간 동안 요청 수를 제한하는 기능이다.

예를 들어:

```text
1분에 100번까지만 요청 허용
```

이런 식이다.

너무 많은 요청이 한 번에 들어오면 서버가 터질 수 있다. 그래서 API Gateway나 Ingress Controller에서 Rate Limiting을 설정하기도 한다.

다만 이 문제에서는 직접 Rate Limiting을 구현하지 않는다. Gateway API의 장점 설명으로 알아두면 된다.

---

# 38. Throttle

`Throttle`은 요청 속도를 조절하는 기능이다.

Rate Limiting이 “일정 시간 안에 몇 번까지 허용할 것인가”에 가깝다면, Throttle은 “요청이 너무 빠르게 몰리지 않도록 속도를 늦추는 것”에 가깝다.

예를 들어:

```text
초당 100개 요청까지만 처리
그 이상은 지연 또는 차단
```

운영 환경에서 서버 보호를 위해 사용한다.

---

# 39. IP 차단

`IP 차단`은 특정 IP에서 오는 요청을 막는 기능이다.

예를 들어 악성 요청이 특정 IP에서 계속 들어오면 해당 IP를 차단할 수 있다.

```text
1.2.3.4 → 차단
5.6.7.8 → 허용
```

Gateway API 자체보다는 Gateway Controller나 정책 리소스와 함께 구현되는 경우가 많다.

---

# 40. 인증과 인가

`인증`은 사용자가 누구인지 확인하는 것이다.

```text
너 누구야?
로그인했어?
토큰 있어?
```

`인가`는 그 사용자가 특정 작업을 할 권한이 있는지 확인하는 것이다.

```text
너 이 API 호출할 권한 있어?
너 관리자 페이지 들어갈 수 있어?
```

API Gateway는 이런 인증/인가를 앞단에서 처리할 수도 있다.

하지만 CKA 문제에서는 여기까지 구현하지 않는다.

---

# 41. 쿼터 관리

`쿼터`는 사용량 제한이다.

예를 들어 고객마다 API 호출량을 다르게 제한할 수 있다.

```text
무료 사용자: 하루 1,000회
유료 사용자: 하루 100,000회
관리자: 제한 없음
```

API Gateway에서 자주 언급되는 기능이다.

---

# 42. CKA 문제에서 진짜 중요한 매핑

이 문제는 용어가 많지만, 시험장에서 실제로 중요한 건 매핑이다.

Ingress의 정보를 Gateway API로 옮겨야 한다.

| 기존 Ingress              | Gateway API                                           |
| ----------------------- | ----------------------------------------------------- |
| `spec.tls[].secretName` | `Gateway.spec.listeners[].tls.certificateRefs[].name` |
| `spec.rules[].host`     | `Gateway.listener.hostname`, `HTTPRoute.hostnames`    |
| `path`                  | `HTTPRoute.rules[].matches[].path.value`              |
| `pathType: Prefix`      | `path.type: PathPrefix`                               |
| backend service name    | `HTTPRoute.backendRefs[].name`                        |
| backend service port    | `HTTPRoute.backendRefs[].port`                        |

즉, 외워야 할 흐름은 이것이다.

```text
Ingress의 TLS Secret
  → Gateway의 certificateRefs

Ingress의 Host
  → Gateway hostname / HTTPRoute hostnames

Ingress의 Path
  → HTTPRoute matches.path

Ingress의 Backend Service
  → HTTPRoute backendRefs
```

---

# 43. 최종 구조

마이그레이션 후 구조는 다음과 같다.

```text
사용자
  ↓
https://gateway.web.k8s.local
  ↓
Gateway web-gateway
  ↓
HTTPRoute web-route
  ↓
Service web-service
  ↓
Pod
```

Ingress를 쓰던 구조는 다음과 같았다.

```text
사용자
  ↓
Ingress web
  ↓
Service web-service
  ↓
Pod
```

즉, 마이그레이션 후에는 Ingress가 빠지고 Gateway와 HTTPRoute가 그 역할을 나누어 맡는다.

```text
Before:
Ingress 하나가 외부 진입점 + 라우팅 담당

After:
Gateway가 외부 진입점 담당
HTTPRoute가 라우팅 담당
```

---

# 44. 시험장에서의 풀이 순서

시험에서는 개념을 길게 설명할 필요 없이 순서를 정확히 지키면 된다.

```bash
kubectl get ingress web -o yaml
```

기존 Ingress에서 TLS Secret, path, service name, service port를 확인한다.

Gateway를 만든다.

```yaml
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
        name: <기존 Ingress의 TLS Secret>
```

HTTPRoute를 만든다.

```yaml
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
    - name: <기존 Ingress의 Service 이름>
      port: <기존 Ingress의 Service 포트>
```

적용한다.

```bash
kubectl apply -f web-gateway.yaml
kubectl apply -f web-route.yaml
```

테스트한다.

```bash
curl -k https://gateway.web.k8s.local
```

정상 동작하면 기존 Ingress를 삭제한다.

```bash
kubectl delete ingress web
```

---

# 마무리

Ingress에서 Gateway API로 마이그레이션한다는 말은 기존 웹 애플리케이션을 새로 만드는 게 아니다. 기존 Ingress가 가지고 있던 외부 진입 설정, TLS 설정, 라우팅 규칙, backend service 정보를 Gateway API 구조로 옮기는 것이다.

핵심은 간단하다.

```text
Gateway = 어디서 받을지
HTTPRoute = 어디로 보낼지
Service = 어떤 Pod들로 연결할지
Pod = 실제 애플리케이션 실행 위치
```

Ingress에서는 이 역할이 하나에 모여 있었고, Gateway API에서는 역할이 더 명확하게 분리된다.

그래서 이 문제를 풀 때는 다음 한 문장만 기억하면 된다.

```text
Ingress의 TLS와 routing rule을 Gateway와 HTTPRoute로 나눠서 그대로 옮긴다.
```
