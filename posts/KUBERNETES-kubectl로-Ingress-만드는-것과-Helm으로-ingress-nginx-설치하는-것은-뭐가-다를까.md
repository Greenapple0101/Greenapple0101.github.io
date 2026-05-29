---
title: "[KUBERNETES] kubectl로 Ingress 만드는 것과 Helm으로 ingress-nginx 설치하는 것은 뭐가 다를까?"
source: "https://velog.io/@yorange50/KUBERNETES-kubectl로-Ingress-만드는-것과-Helm으로-ingress-nginx-설치하는-것은-뭐가-다를까"
published: "2026-05-13T05:31:36.398Z"
tags: ""
backup_date: "2026-05-29T14:52:52.746646"
---

Kubernetes에서 Ingress를 공부하다 보면 헷갈리는 지점이 있다.

```bash
kubectl apply -f nginx-ingress.yaml
```

이 명령어도 Ingress를 만드는 것 같고,

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx
```

이 명령어도 Ingress 관련 무언가를 설치하는 것 같다.

둘 다 Ingress와 관련되어 있지만, 역할은 완전히 다르다.

결론부터 말하면 이렇다.

```text
kubectl로 Ingress 생성
= 라우팅 규칙 생성

Helm으로 ingress-nginx 설치
= 그 라우팅 규칙을 실제로 처리할 Ingress Controller 설치
```

즉, `kubectl`로 만든 Ingress는 “규칙표”이고, Helm으로 설치한 `ingress-nginx`는 그 규칙표를 읽고 실제 트래픽을 보내주는 “실행 담당자”다.

## Ingress는 무엇인가?

Ingress는 Kubernetes 리소스 중 하나다.

역할은 외부에서 들어온 HTTP/HTTPS 요청을 어떤 Service로 보낼지 정의하는 것이다.

예를 들어 이런 요청이 들어온다고 해보자.

```text
http://localhost/
```

이 요청을 Kubernetes 안의 `nginx` Service로 보내고 싶다면 Ingress를 만든다.

예시 YAML은 다음과 같다.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
spec:
  ingressClassName: nginx
  rules:
    - host: localhost
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: nginx
                port:
                  number: 80
```

이 YAML의 의미는 다음과 같다.

```text
host가 localhost이고
path가 /로 들어오면
nginx Service의 80번 포트로 보내라
```

이 파일을 적용하는 명령어가 바로 이것이다.

```bash
kubectl apply -f nginx-ingress.yaml
```

또는 alias를 쓴다면:

```bash
k apply -f nginx-ingress.yaml
```

이 명령어는 Kubernetes 클러스터 안에 `Ingress` 리소스를 생성한다.

확인하면 이렇게 나온다.

```bash
kubectl get ingress
```

```text
NAME            CLASS   HOSTS       ADDRESS   PORTS   AGE
nginx-ingress   nginx   localhost             80      8s
```

여기까지 하면 Ingress 규칙은 만들어진 것이다.

하지만 여기서 끝이 아니다.

Ingress는 혼자서 트래픽을 처리하지 못한다.

## Ingress는 규칙일 뿐이다

Ingress를 만들었다고 해서 자동으로 브라우저 요청이 Pod까지 전달되는 것은 아니다.

Ingress는 말 그대로 “규칙”이다.

```text
localhost로 들어오면 nginx Service로 보내라
```

하지만 이 규칙을 실제로 읽고 실행하는 프로그램이 필요하다.

그 역할을 하는 것이 **Ingress Controller**다.

구조는 다음과 같다.

```text
브라우저
→ Ingress Controller
→ Ingress 규칙 확인
→ Service
→ Pod
```

여기서 Ingress Controller가 없으면 Ingress 리소스는 존재하지만 실제 트래픽은 처리되지 않는다.

비유하면 이렇다.

```text
Ingress = 교통 규칙표
Ingress Controller = 교통경찰
Service = 목적지 입구
Pod = 실제 가게
```

규칙표만 붙여놓고 교통경찰이 없으면 차들이 어디로 가야 할지 실제로 안내되지 않는다.

## Helm으로 설치한 ingress-nginx는 무엇인가?

이번에 사용한 명령어는 다음과 같다.

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
```

```bash
helm repo update
```

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

이 명령어는 Ingress 리소스를 만드는 명령어가 아니다.

정확히는 **ingress-nginx controller를 설치하는 명령어**다.

즉, Kubernetes 클러스터 안에 다음과 같은 리소스들이 설치된다.

```text
Deployment
Pod
Service
ConfigMap
ServiceAccount
ClusterRole
ClusterRoleBinding
IngressClass
Admission Webhook 관련 리소스
```

이 중 핵심은 `ingress-nginx-controller`다.

확인은 이렇게 할 수 있다.

```bash
kubectl get pods -n ingress-nginx
```

예상 결과는 이런 형태다.

```text
ingress-nginx-controller-xxxxx   Running
```

Service도 확인할 수 있다.

```bash
kubectl get svc -n ingress-nginx
```

예상 결과는 이런 형태다.

```text
ingress-nginx-controller   LoadBalancer   80/TCP,443/TCP
```

즉, Helm은 Ingress 규칙을 만드는 것이 아니라, Ingress 규칙을 처리할 컨트롤러를 설치한다.

## kubectl로 만든 것과 Helm으로 만든 것의 차이

둘의 차이를 표로 정리하면 다음과 같다.

| 구분        | kubectl로 Ingress 생성                   | Helm으로 ingress-nginx 설치                                  |
| --------- | ------------------------------------- | -------------------------------------------------------- |
| 명령어 예시    | `kubectl apply -f nginx-ingress.yaml` | `helm install ingress-nginx ingress-nginx/ingress-nginx` |
| 생성 대상     | Ingress 리소스                           | Ingress Controller                                       |
| 역할        | 라우팅 규칙 정의                             | 라우팅 규칙을 실제로 처리                                           |
| 직접 작성 여부  | YAML 직접 작성                            | Chart로 설치                                                |
| 없으면 어떻게 됨 | 요청을 어디로 보낼지 규칙이 없음                    | 규칙을 처리할 실행자가 없음                                          |
| 비유        | 교통 규칙표                                | 교통경찰                                                     |

핵심은 이거다.

```text
kubectl apply -f nginx-ingress.yaml
= Ingress 규칙 생성

helm install ingress-nginx ...
= Ingress Controller 설치
```

둘은 대체 관계가 아니다.

둘 다 필요하다.

## 요청 흐름으로 보면 더 쉽다

브라우저에서 `localhost`로 접속할 때 흐름은 다음과 같다.

```text
브라우저
→ localhost:80
→ k3d LoadBalancer
→ ingress-nginx controller
→ Ingress 규칙
→ Service
→ Pod
```

여기서 Helm으로 설치한 것은 이 부분이다.

```text
ingress-nginx controller
```

kubectl로 만든 Ingress YAML은 이 부분이다.

```text
Ingress 규칙
```

Service와 Pod는 별도로 있어야 한다.

즉, 전체 구조는 이렇게 완성된다.

```text
[브라우저]
    ↓
[ingress-nginx controller]  ← Helm으로 설치
    ↓
[Ingress]                   ← kubectl apply로 생성
    ↓
[Service]                   ← kubectl expose 등으로 생성
    ↓
[Pod]                       ← Deployment로 생성
```

이 중 하나라도 빠지면 정상 접속이 안 된다.

## 왜 503이 떴을까?

이번 실습에서 `localhost` 접속 시 다음 화면이 나왔다.

```text
503 Service Temporarily Unavailable
nginx
```

이건 중요한 신호다.

처음에 `ERR_CONNECTION_REFUSED`가 떴을 때는 브라우저 요청이 ingress-nginx controller까지 도달하지 못한 상태였다.

하지만 `503 Service Temporarily Unavailable`은 다르다.

```text
nginx가 응답했다
= ingress-nginx controller까지 요청은 도착했다
```

즉, Helm으로 설치한 ingress-nginx controller는 동작하고 있었다는 뜻이다.

그런데 503이 떴다는 것은 controller가 뒤쪽으로 요청을 넘기지 못했다는 뜻이다.

주로 원인은 다음 중 하나다.

```text
Ingress에 적은 Service 이름이 실제 Service 이름과 다름
Ingress에 적은 Service port가 실제 Service port와 다름
Service는 있는데 연결된 Pod가 없음
Service selector와 Pod label이 맞지 않음
Pod가 Running 상태가 아님
```

즉, 503은 보통 Ingress Controller 설치 문제라기보다는 **Ingress → Service → Pod 연결 문제**다.

## 확인 명령어

먼저 Ingress가 어떤 Service로 보내려고 하는지 확인한다.

```bash
kubectl describe ingress nginx-ingress
```

여기서 backend를 확인한다.

```text
Backend:
  Service: nginx:80
```

그다음 실제 Service가 있는지 본다.

```bash
kubectl get svc
```

Pod도 확인한다.

```bash
kubectl get pods
```

전체 리소스를 한 번에 보려면 다음을 쓴다.

```bash
kubectl get all
```

Service가 Pod를 제대로 잡고 있는지 보려면 다음을 확인한다.

```bash
kubectl describe svc nginx
```

여기서 중요한 부분은 `Endpoints`다.

정상이면 이런 식으로 나온다.

```text
Endpoints: 10.42.0.12:80
```

문제가 있으면 이렇게 나온다.

```text
Endpoints: <none>
```

`Endpoints: <none>`이면 Service가 연결할 Pod를 못 찾고 있다는 뜻이다.

이 상태에서는 Ingress가 아무리 잘 만들어져 있어도 503이 날 수 있다.

## 테스트용 nginx까지 포함한 전체 흐름

Ingress 실습을 제대로 하려면 최소한 다음 순서가 필요하다.

먼저 k3d 클러스터를 만들 때 로컬 80번 포트를 LoadBalancer에 연결한다.

```bash
k3d cluster create hello-cluster -p "80:80@loadbalancer"
```

그다음 ingress-nginx controller를 Helm으로 설치한다.

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
```

```bash
helm repo update
```

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

이제 실제 백엔드 앱을 만든다.

```bash
kubectl create deployment nginx --image=nginx
```

Service를 만든다.

```bash
kubectl expose deployment nginx --port=80 --target-port=80
```

Ingress YAML을 적용한다.

```bash
kubectl apply -f nginx-ingress.yaml
```

확인한다.

```bash
kubectl get pods
kubectl get svc
kubectl get ingress
```

이 흐름이 모두 맞아야 브라우저에서 `localhost` 접속이 정상적으로 된다.

## Helm은 왜 쓰고 kubectl은 왜 쓰는가?

여기서 다시 정리하면 Helm과 kubectl의 역할은 다르다.

`kubectl`은 Kubernetes 리소스를 직접 생성하고 수정하는 기본 도구다.

```bash
kubectl apply -f nginx-ingress.yaml
kubectl get pods
kubectl describe svc nginx
```

반면 Helm은 여러 Kubernetes 리소스를 하나의 패키지처럼 설치하고 관리하는 도구다.

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx
helm list -A
helm uninstall ingress-nginx -n ingress-nginx
```

`ingress-nginx`처럼 설치해야 할 리소스가 많은 컴포넌트는 직접 YAML로 다 만들기 복잡하다.

그래서 Helm Chart를 사용한다.

반대로 내가 직접 정의하는 간단한 Ingress 규칙은 YAML 파일로 작성해서 `kubectl apply`로 적용하는 것이 자연스럽다.

즉, 이런 식으로 역할을 나누면 된다.

```text
복잡한 인프라 컴포넌트 설치
→ Helm

내 애플리케이션 리소스 생성/수정
→ kubectl apply
```

물론 내 애플리케이션도 Helm Chart로 만들 수 있다. 실무에서는 애플리케이션 배포도 Helm으로 패키징하는 경우가 많다. 하지만 처음 공부할 때는 역할을 나눠서 이해하는 것이 좋다.

## 헷갈리기 쉬운 포인트

### 1. Helm으로 ingress-nginx를 설치했다고 Ingress가 자동으로 생기는 것은 아니다

Helm으로 controller를 설치해도 내가 원하는 라우팅 규칙은 직접 만들어야 한다.

```bash
kubectl get ingress
```

했을 때 아무것도 안 나올 수 있다.

```text
No resources found in default namespace.
```

이건 ingress-nginx가 안 깔렸다는 뜻이 아니다.

단지 아직 Ingress 규칙을 만들지 않았다는 뜻이다.

### 2. Ingress를 만들었다고 바로 접속되는 것도 아니다

Ingress는 Service와 Pod가 있어야 의미가 있다.

```text
Ingress
→ Service
→ Pod
```

Service가 없거나, Service가 Pod를 못 잡고 있으면 503이 난다.

### 3. nginx라는 이름이 여러 번 나와서 헷갈릴 수 있다

이번 실습에서는 nginx가 여러 의미로 등장한다.

```text
ingress-nginx
= Ingress Controller 이름

nginx-ingress
= 내가 만든 Ingress 리소스 이름

nginx
= 테스트용 웹 서버 Deployment/Service 이름
```

이 셋은 서로 다르다.

```text
ingress-nginx controller
= 트래픽을 받아서 라우팅하는 컨트롤러

nginx-ingress
= localhost 요청을 어디로 보낼지 적은 규칙

nginx Service/Pod
= 실제 웹 페이지를 응답하는 백엔드
```

이걸 구분해야 트러블슈팅이 쉬워진다.

## 정리

`kubectl`로 Ingress를 생성하는 것과 Helm으로 `ingress-nginx`를 설치하는 것은 역할이 다르다. `kubectl apply -f nginx-ingress.yaml`은 `localhost`로 들어온 요청을 어떤 Service로 보낼지 정의하는 Ingress 규칙을 생성하는 명령어다. 반면 `helm install ingress-nginx ingress-nginx/ingress-nginx`는 그 Ingress 규칙을 실제로 읽고 트래픽을 처리하는 ingress-nginx controller를 설치하는 명령어다. Ingress는 규칙이고, Ingress Controller는 그 규칙을 실행하는 주체다. 따라서 브라우저 요청이 정상적으로 Pod까지 도달하려면 ingress-nginx controller, Ingress 리소스, Service, Pod가 모두 필요하다. 503 에러가 뜬다면 보통 controller까지는 요청이 도착했지만, Ingress 뒤쪽의 Service 또는 Pod 연결이 잘못된 상태라고 보면 된다.
