---
title: "[Kubernetes] Kubernetes Namespace와 Ingress"
source: "https://velog.io/@yorange50/Kubernetes-Kubernetes-Namespace와-Ingress"
published: "2026-05-14T07:51:43.497Z"
tags: ""
backup_date: "2026-05-29T14:52:52.740175"
---

Kubernetes를 처음 만지면 Pod, Deployment, Service까지는 어느 정도 감이 온다. 그런데 조금만 더 들어가면 바로 헷갈리는 개념이 나온다.

```text
Namespace
Ingress
Ingress Controller
ingress-nginx
ingress-nginx-controller
Traefik
```

특히 `ingress-nginx`와 `ingress-nginx-controller`는 이름이 비슷해서 거의 같은 것으로 착각하기 쉽다. 하지만 Kubernetes에서는 **선언하는 리소스**와 **실제로 동작하는 주체**를 구분해서 봐야 한다. 이 차이를 이해하면 Ingress도 훨씬 쉽게 잡힌다. 실습 메모에서도 Namespace, ingress-nginx, Traefik, 포트 충돌, Ingress Controller가 함께 언급되어 있어 이 흐름으로 정리하면 좋다. 

---

# [KUBERNETES] Namespace는 왜 필요할까?

## 1. Namespace란?

Namespace는 Kubernetes 클러스터 안에서 리소스를 **논리적으로 분리하는 공간**이다.

쉽게 말하면 하나의 Kubernetes 클러스터 안에 여러 개의 작업 공간을 나누는 개념이다.

```text
Kubernetes Cluster
 ├── default namespace
 │    ├── Pod
 │    ├── Service
 │    └── Deployment
 │
 ├── kube-system namespace
 │    ├── CoreDNS
 │    ├── kube-proxy
 │    └── 기타 쿠버네티스 시스템 컴포넌트
 │
 └── ingress-nginx namespace
      ├── Ingress Controller Pod
      └── 관련 Service
```

즉, Namespace는 물리적으로 클러스터를 나누는 것이 아니라, **하나의 클러스터 안에서 리소스를 구역별로 구분하는 방식**이다.

---

## 2. 왜 Namespace가 필요할까?

처음 Kubernetes를 배울 때는 대부분 `default` namespace만 사용한다.

```bash
kubectl get pods
```

이 명령어를 치면 기본적으로 `default` namespace 안의 Pod를 보여준다.

하지만 실제 환경에서는 모든 리소스를 `default`에 몰아넣으면 관리가 어려워진다.

예를 들어 다음과 같은 리소스가 모두 한 공간에 있다고 생각해보자.

```text
개발용 애플리케이션
운영용 애플리케이션
테스트용 애플리케이션
모니터링 도구
Ingress Controller
Kubernetes 시스템 컴포넌트
```

전부 `default`에 있으면 어떤 Pod가 어떤 목적의 Pod인지 헷갈린다.

그래서 Namespace로 나눈다.

```text
dev namespace
= 개발 환경

staging namespace
= 검증 환경

prod namespace
= 운영 환경

monitoring namespace
= Prometheus, Grafana 같은 모니터링 도구

ingress-nginx namespace
= Ingress Controller 관련 리소스
```

Namespace는 리소스를 보기 좋게 나누기 위한 폴더 같은 역할을 한다.

---

## 3. default namespace란?

`default` namespace는 사용자가 별도로 namespace를 지정하지 않았을 때 리소스가 생성되는 기본 공간이다.

예를 들어 다음 명령어를 실행하면,

```bash
kubectl create deployment nginx --image=nginx
```

namespace를 따로 지정하지 않았기 때문에 `default` namespace에 Deployment가 생성된다.

확인할 때도 이렇게 보면 된다.

```bash
kubectl get deployments
```

이 명령어는 사실상 아래 명령어와 비슷하다.

```bash
kubectl get deployments -n default
```

즉, `-n` 옵션을 생략하면 기본적으로 `default` namespace를 바라본다.

---

## 4. kube-system namespace란?

`kube-system` namespace는 Kubernetes 자체를 운영하기 위한 시스템 리소스들이 들어있는 공간이다.

예를 들어 다음 명령어를 쳐보면 된다.

```bash
kubectl get pods -n kube-system
```

그러면 일반 애플리케이션 Pod가 아니라 Kubernetes 내부 동작에 필요한 Pod들이 보인다.

대표적으로 이런 것들이 있다.

```text
CoreDNS
= 클러스터 내부 DNS 담당

kube-proxy
= Service 네트워크 처리 담당

metrics-server
= 리소스 사용량 수집 담당

coredns
= 서비스 이름으로 Pod를 찾을 수 있게 해주는 DNS 역할
```

즉, `kube-system`은 내가 만든 애플리케이션을 넣는 공간이라기보다, Kubernetes 자체가 돌아가기 위한 시스템 공간이라고 보면 된다.

그래서 초보자가 실습 중에 `kube-system` 안의 리소스를 함부로 지우면 클러스터가 이상해질 수 있다.

---

## 5. Namespace 조회 명령어

Namespace 목록은 이렇게 확인한다.

```bash
kubectl get namespaces
```

짧게는 이렇게도 가능하다.

```bash
kubectl get ns
```

특정 namespace 안의 Pod를 보려면 이렇게 한다.

```bash
kubectl get pods -n kube-system
```

전체 namespace의 Pod를 한 번에 보고 싶으면 이렇게 한다.

```bash
kubectl get pods -A
```

여기서 `-A`는 all namespaces라는 뜻이다.

```text
kubectl get pods
= default namespace의 Pod 조회

kubectl get pods -n kube-system
= kube-system namespace의 Pod 조회

kubectl get pods -A
= 전체 namespace의 Pod 조회
```

---

## 6. 운영 환경에서 Namespace를 나누는 이유

운영 환경에서는 Namespace가 단순 정리용을 넘어서 중요한 관리 단위가 된다.

예를 들어 하나의 클러스터 안에 개발, 스테이징, 운영 환경이 같이 있을 수 있다.

```text
dev namespace
staging namespace
prod namespace
```

이렇게 나누면 환경별로 리소스를 분리할 수 있다.

또한 권한도 namespace 단위로 나눌 수 있다.

```text
개발자는 dev namespace 접근 가능
운영자는 prod namespace 접근 가능
모니터링 팀은 monitoring namespace 접근 가능
```

리소스 제한도 namespace 단위로 걸 수 있다.

```text
dev namespace는 CPU 2개까지만 사용
prod namespace는 CPU 20개까지 사용
monitoring namespace는 메모리 4Gi까지 사용
```

즉, Namespace는 단순히 이름표가 아니라 운영 환경에서 **분리, 권한, 리소스 관리**의 기준이 된다.

---

# [KUBERNETES] Ingress란 무엇인가?

## 1. Ingress의 뜻

Ingress는 영어로 “들어옴”, “진입”이라는 뜻이다.

Kubernetes에서 Ingress는 **외부 HTTP/HTTPS 요청이 클러스터 안으로 들어오는 규칙**을 정의하는 리소스다.

쉽게 말하면 이런 역할이다.

```text
외부 사용자 요청
      ↓
Ingress
      ↓
Service
      ↓
Pod
```

즉, Ingress는 외부 요청을 어떤 Service로 보낼지 정하는 입구 역할을 한다.

---

## 2. Service만 있으면 안 되나?

Kubernetes에서 Pod는 직접 외부에 노출하지 않는다. 보통 Service를 통해 접근한다.

예를 들어 nginx Pod가 있고, 이를 Service로 노출했다고 하자.

```text
nginx Pod
   ↑
nginx Service
```

Service는 Pod 앞에 있는 고정 입구다.

하지만 Service만으로 여러 도메인과 경로를 세밀하게 라우팅하기에는 부족하다.

예를 들어 이런 요청이 있다고 하자.

```text
example.com/
example.com/api
admin.example.com/
```

이 요청들을 각각 다른 서비스로 보내고 싶을 수 있다.

```text
example.com/        → frontend-service
example.com/api     → api-service
admin.example.com/  → admin-service
```

이런 HTTP 기반 라우팅을 담당하는 것이 Ingress다.

---

## 3. Ingress는 HTTP 라우팅 규칙이다

Ingress는 실제 프록시 서버 그 자체가 아니다.

Ingress는 “어떤 요청을 어디로 보낼지”에 대한 규칙이다.

예를 들어 이런 식이다.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-service
            port:
              number: 80
```

이 YAML의 의미는 다음과 같다.

```text
example.com으로 들어온 HTTP 요청 중
/ 경로로 들어온 요청은
nginx-service의 80번 포트로 보내라.
```

즉, Ingress는 외부 요청을 Service로 연결하는 HTTP 라우팅 규칙이다.

---

## 4. Ingress와 Service의 관계

Ingress와 Service는 역할이 다르다.

```text
Ingress
= 외부 HTTP 요청을 어떤 Service로 보낼지 정하는 규칙

Service
= Pod로 가는 고정 내부 입구

Pod
= 실제 애플리케이션 컨테이너가 실행되는 곳
```

흐름으로 보면 이렇다.

```text
사용자 브라우저
      ↓
Ingress
      ↓
Service
      ↓
Pod
```

예를 들어 사용자가 브라우저에서 `example.com`에 접속하면 Ingress 규칙이 요청을 받아서 적절한 Service로 보낸다. Service는 다시 해당 Label을 가진 Pod로 요청을 전달한다.

---

## 5. Ingress는 “들어오는 트래픽”을 다룬다

Ingress는 이름 그대로 들어오는 트래픽을 다룬다.

여기서 중요한 것은 Ingress가 주로 HTTP/HTTPS 레벨의 요청을 다룬다는 점이다.

```text
도메인 기반 라우팅
경로 기반 라우팅
TLS 인증서 적용
HTTP/HTTPS 요청 처리
```

예를 들어 다음과 같은 설정이 가능하다.

```text
shop.example.com      → shop-service
blog.example.com      → blog-service
example.com/api       → api-service
example.com/admin     → admin-service
```

이런 식으로 Ingress는 클러스터 외부에서 들어온 웹 요청을 내부 서비스로 연결해준다.

---

# [KUBERNETES] ingress-nginx와 ingress-nginx-controller는 왜 다른가?

## 1. 가장 헷갈리는 지점

Kubernetes를 공부하다 보면 이런 이름이 나온다.

```text
Ingress
ingress-nginx
ingress-nginx-controller
nginx-ingress
```

이름이 비슷해서 다 같은 것처럼 보인다.

하지만 정확히 구분해야 한다.

```text
Ingress
= Kubernetes 리소스
= 라우팅 규칙

Ingress Controller
= Ingress 규칙을 실제로 읽고 동작시키는 프로그램

ingress-nginx
= NGINX 기반 Ingress Controller 구현체 또는 설치 chart 이름으로 자주 쓰임

ingress-nginx-controller
= 실제로 클러스터 안에서 실행되는 Controller Pod/Deployment 이름으로 자주 보임
```

핵심은 이것이다.

```text
Ingress는 선언
Ingress Controller는 실행 주체
```

---

## 2. Ingress 리소스란?

Ingress 리소스는 Kubernetes에 저장되는 설정이다.

예를 들어 이런 YAML이 Ingress 리소스다.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-service
            port:
              number: 80
```

이 리소스는 이렇게 말하는 것이다.

```text
example.com으로 들어온 요청을 nginx-service로 보내라.
```

하지만 이것만 있다고 실제 요청이 처리되는 것은 아니다.

왜냐하면 Ingress는 그냥 규칙이기 때문이다.

이 규칙을 읽고 실제로 요청을 받아서 프록시해주는 프로그램이 필요하다.

그게 Ingress Controller다.

---

## 3. Ingress Controller란?

Ingress Controller는 Ingress 리소스를 감시하다가, 거기에 적힌 규칙대로 실제 HTTP 트래픽을 처리하는 프로그램이다.

쉽게 말하면 이런 역할이다.

```text
1. Kubernetes API Server에서 Ingress 리소스를 감시
2. 새 Ingress 규칙이 생겼는지 확인
3. 규칙에 맞게 NGINX 설정 생성
4. 외부 HTTP 요청을 받아서 Service로 전달
```

Ingress Controller가 없으면 Ingress 리소스를 만들어도 아무 일도 일어나지 않는다.

이게 초보자가 가장 많이 헷갈리는 부분이다.

```text
Ingress YAML 만들었는데 왜 접속이 안 되지?
```

이 경우 실제로는 Ingress Controller가 설치되어 있지 않거나, 외부에서 Controller로 들어오는 경로가 없을 수 있다.

---

## 4. 선언 vs 실제 동작 주체

Kubernetes에서는 선언과 실행 주체를 나눠서 보는 게 중요하다.

```text
Deployment YAML
= 원하는 Pod 상태를 선언

Deployment Controller
= 그 상태를 맞추기 위해 실제로 Pod 생성

Ingress YAML
= 원하는 라우팅 규칙을 선언

Ingress Controller
= 그 규칙을 보고 실제로 트래픽 라우팅
```

즉, Ingress는 “이렇게 라우팅하고 싶다”는 선언이고, Ingress Controller는 “그 선언대로 실제 요청을 처리하는 애”다.

이 관점으로 보면 `ingress-nginx`와 `ingress-nginx-controller`도 덜 헷갈린다.

---

## 5. ingress-nginx란?

`ingress-nginx`는 보통 NGINX 기반 Ingress Controller를 의미한다.

Helm으로 설치할 때도 이런 식으로 많이 설치한다.

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

여기서 `ingress-nginx`라는 이름이 여러 번 나온다.

```text
Helm release name
Chart 이름
Namespace 이름
Controller 관련 리소스 이름
```

그래서 더 헷갈린다.

하지만 핵심은 이거다.

```text
ingress-nginx
= NGINX를 이용해서 Ingress Controller 역할을 하도록 만든 구현체
```

---

## 6. ingress-nginx-controller란?

`ingress-nginx-controller`는 실제로 클러스터 안에서 실행되는 Controller 리소스 이름으로 자주 보인다.

예를 들어 설치 후 확인하면 이런 리소스가 있을 수 있다.

```bash
kubectl get pods -n ingress-nginx
```

출력 예시는 이런 느낌이다.

```text
NAME                                        READY   STATUS    RESTARTS
ingress-nginx-controller-xxxxxx             1/1     Running   0
```

여기서 `ingress-nginx-controller`는 실제로 요청을 받고, Ingress 규칙을 읽고, Service로 트래픽을 보내는 Controller Pod다.

즉, 구분하면 이렇게 된다.

```text
Ingress
= 라우팅 규칙

ingress-nginx
= NGINX 기반 Ingress Controller 프로젝트/구현체/설치 이름

ingress-nginx-controller
= 실제로 실행 중인 Controller Pod 또는 Deployment
```

---

## 7. 왜 헷갈릴까?

헷갈리는 이유는 이름이 너무 비슷하기 때문이다.

예를 들어 사용자가 직접 만드는 Ingress 이름을 이렇게 지을 수도 있다.

```yaml
metadata:
  name: nginx-ingress
```

그런데 Helm으로 설치한 Controller 이름은 이렇게 보일 수 있다.

```text
ingress-nginx-controller
```

그러면 처음 보는 사람은 이렇게 생각한다.

```text
nginx-ingress랑 ingress-nginx-controller가 같은 건가?
```

하지만 아니다.

```text
nginx-ingress
= 사용자가 만든 Ingress 리소스 이름일 수 있음

ingress-nginx-controller
= Ingress를 실제 처리하는 Controller일 수 있음
```

이름보다 `kind`를 봐야 한다.

```bash
kubectl get ingress
```

이건 Ingress 리소스를 보는 것이다.

```bash
kubectl get pods -n ingress-nginx
```

이건 Ingress Controller Pod를 보는 것이다.

---

# [KUBERNETES] Traefik도 Ingress Controller일까?

## 1. Traefik이란?

Traefik도 Ingress Controller가 될 수 있다.

Traefik은 동적 라우팅과 클라우드 네이티브 환경에 강점을 가진 프록시/로드밸런서다. Kubernetes에서는 Ingress Controller 역할을 할 수 있다.

즉, Ingress Controller는 반드시 NGINX만 가능한 것이 아니다.

대표적인 Ingress Controller에는 이런 것들이 있다.

```text
ingress-nginx
Traefik
HAProxy Ingress
Contour
AWS Load Balancer Controller
GCE Ingress Controller
```

이 중에서 `ingress-nginx`는 NGINX 기반이고, Traefik은 Traefik 기반이다.

---

## 2. Traefik도 Ingress 리소스를 처리할 수 있다

Ingress 리소스는 Kubernetes의 표준 리소스다.

그리고 Ingress Controller는 그 리소스를 읽고 처리하는 구현체다.

따라서 Traefik도 Ingress Controller로 설치되어 있다면 Ingress 리소스를 감시하고, 요청을 내부 Service로 보낼 수 있다.

흐름은 같다.

```text
사용자 요청
      ↓
Traefik Ingress Controller
      ↓
Ingress 규칙 확인
      ↓
Service
      ↓
Pod
```

즉, Traefik도 Ingress Controller다.

---

## 3. ingress-nginx와 Traefik 비교

둘 다 Ingress Controller 역할을 할 수 있다.

차이는 구현체가 다르다는 것이다.

```text
ingress-nginx
= NGINX 기반
= 많이 쓰이고 자료가 많음
= Kubernetes Ingress 실습에서 자주 등장

Traefik
= Traefik 기반
= 동적 설정과 클라우드 네이티브 환경에 친화적
= K3s에서 기본 Ingress Controller로 자주 사용됨
```

특히 K3s에서는 Traefik이 기본으로 설치되는 경우가 많다.

그래서 K3d나 K3s 실습을 하다 보면 이미 Traefik이 떠 있는 경우가 있다.

이 상태에서 ingress-nginx를 또 설치하려고 하면 포트 충돌이 날 수 있다.

---

## 4. 포트 충돌 문제

Ingress Controller는 외부 요청을 받아야 한다.

그래서 보통 80번, 443번 포트를 사용한다.

```text
HTTP  = 80
HTTPS = 443
```

그런데 Traefik이 이미 80번 포트를 사용하고 있는데, ingress-nginx도 80번 포트를 쓰려고 하면 충돌이 날 수 있다.

```text
Traefik
= 80번 포트 사용 중

ingress-nginx
= 나도 80번 포트 쓰고 싶음

결과
= 포트 충돌
```

실습 중에 이런 느낌의 문제가 생길 수 있다.

```text
이미 80번 포트를 누가 쓰고 있어서 ingress-nginx가 제대로 안 뜸
```

이때는 현재 어떤 Ingress Controller가 설치되어 있는지 확인해야 한다.

```bash
kubectl get pods -A
```

또는 namespace를 확인한다.

```bash
kubectl get ns
```

Traefik이 있다면 보통 `kube-system` namespace 쪽에 있을 수 있다.

```bash
kubectl get pods -n kube-system
```

ingress-nginx를 설치했다면 보통 `ingress-nginx` namespace를 확인한다.

```bash
kubectl get pods -n ingress-nginx
```

---

## 5. 여러 Ingress Controller가 공존할 수 있을까?

가능은 하다.

하지만 아무 설정 없이 여러 Ingress Controller를 설치하면 서로 같은 Ingress 리소스를 처리하려고 하거나, 같은 포트를 잡으려고 해서 문제가 생길 수 있다.

그래서 여러 Ingress Controller를 같이 쓸 때는 보통 `IngressClass`를 사용한다.

예를 들어 이런 식이다.

```text
nginx용 IngressClass
traefik용 IngressClass
```

Ingress 리소스에서 어떤 Controller가 처리할지 지정할 수 있다.

```yaml
spec:
  ingressClassName: nginx
```

이렇게 하면 해당 Ingress는 nginx Ingress Controller가 처리하도록 지정할 수 있다.

반대로 Traefik용으로 지정할 수도 있다.

```yaml
spec:
  ingressClassName: traefik
```

즉, 여러 Ingress Controller를 공존시킬 수는 있지만, 초보 실습 단계에서는 하나만 명확하게 쓰는 게 좋다.

---

# 전체 흐름으로 다시 보기

Namespace와 Ingress를 하나의 흐름으로 보면 이렇게 된다.

```text
1. Namespace
   Kubernetes 리소스를 논리적으로 나누는 공간

2. default namespace
   별도 지정이 없으면 리소스가 생성되는 기본 공간

3. kube-system namespace
   Kubernetes 시스템 리소스가 들어있는 공간

4. Ingress
   외부 HTTP 요청을 내부 Service로 보내는 라우팅 규칙

5. Ingress Controller
   Ingress 규칙을 실제로 읽고 트래픽을 처리하는 실행 주체

6. ingress-nginx
   NGINX 기반 Ingress Controller 구현체

7. ingress-nginx-controller
   실제로 실행되는 Controller Pod/Deployment 이름으로 자주 보이는 리소스

8. Traefik
   ingress-nginx와 마찬가지로 Ingress Controller 역할을 할 수 있는 프록시
```

---

# 실습할 때 보는 명령어 정리

Namespace 확인:

```bash
kubectl get ns
```

전체 namespace의 Pod 확인:

```bash
kubectl get pods -A
```

default namespace의 Pod 확인:

```bash
kubectl get pods
```

kube-system namespace 확인:

```bash
kubectl get pods -n kube-system
```

ingress-nginx namespace 확인:

```bash
kubectl get pods -n ingress-nginx
```

Ingress 리소스 확인:

```bash
kubectl get ingress
```

Ingress 상세 확인:

```bash
kubectl describe ingress <ingress-name>
```

Service 확인:

```bash
kubectl get svc
```

Ingress Controller가 떠 있는지 확인:

```bash
kubectl get pods -A | grep ingress
```

Traefik 확인:

```bash
kubectl get pods -A | grep traefik
```

---

# 정리

Namespace는 Kubernetes 클러스터 안에서 리소스를 논리적으로 나누기 위한 공간이다. `default`는 기본 작업 공간이고, `kube-system`은 Kubernetes 시스템 컴포넌트들이 들어있는 공간이다. 운영 환경에서는 `dev`, `staging`, `prod`, `monitoring`, `ingress-nginx`처럼 목적에 따라 Namespace를 나눠 관리한다.

Ingress는 외부에서 들어오는 HTTP/HTTPS 요청을 내부 Service로 보내기 위한 라우팅 규칙이다. 하지만 Ingress 리소스만 만든다고 실제 요청이 처리되는 것은 아니다. Ingress 규칙을 읽고 실제로 트래픽을 처리하는 Ingress Controller가 필요하다.

`ingress-nginx`는 NGINX 기반 Ingress Controller 구현체이고, `ingress-nginx-controller`는 실제로 클러스터 안에서 실행되는 Controller Pod나 Deployment 이름으로 자주 보인다. 즉, Ingress는 선언이고, Ingress Controller는 실제 동작 주체다.

Traefik도 Ingress Controller가 될 수 있다. 특히 K3s/K3d 환경에서는 Traefik이 기본으로 설치되어 있는 경우가 있어, ingress-nginx를 추가로 설치할 때 80번, 443번 포트 충돌이 날 수 있다. 그래서 실습할 때는 현재 어떤 Ingress Controller가 떠 있는지 먼저 확인하는 습관이 중요하다.

핵심은 이 한 줄이다.

```text
Ingress는 “어디로 보낼지”를 선언하고,
Ingress Controller는 “실제로 요청을 받아서 보내는” 역할을 한다.
```
