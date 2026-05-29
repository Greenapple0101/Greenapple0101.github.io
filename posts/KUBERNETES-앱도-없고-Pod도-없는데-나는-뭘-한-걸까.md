---
title: "[KUBERNETES] 앱도 없고 Pod도 없는데 나는 뭘 한 걸까?"
source: "https://velog.io/@yorange50/KUBERNETES-앱도-없고-Pod도-없는데-나는-뭘-한-걸까"
published: "2026-05-13T05:41:42.596Z"
tags: ""
backup_date: "2026-05-29T14:52:52.745772"
---

Ingress 실습을 하다 보면 이런 순간이 온다.

```text
Helm으로 ingress-nginx도 설치했다.
Ingress YAML도 만들었다.
localhost로 접속도 해봤다.
그런데 503이 떴다.
```

처음에는 헷갈린다.

“나는 뭘 만든 거지?”
“앱도 없고 Pod도 없는데 왜 Ingress를 만든 거지?”
“Service에는 앱이 들어가는 건가?”
“Helm으로 설치했으면 다 된 거 아닌가?”

결론부터 말하면, 이 상태는 **앱은 없고, 입구와 라우팅 규칙만 만든 상태**다.

## 내가 실제로 한 것

이번 실습에서 한 작업은 크게 보면 이렇다.

```text
1. k3d 클러스터 생성
2. Helm으로 ingress-nginx Controller 설치
3. Ingress YAML 생성
4. localhost 요청을 nginx Service로 보내라는 규칙 생성
```

즉, 외부 요청을 받을 준비는 했다.

하지만 아직 빠진 것이 있었다.

```text
nginx Service
nginx Pod
실제 nginx 애플리케이션
```

그래서 전체 구조로 보면 이런 상태였다.

```text
브라우저
  ↓
localhost:80
  ↓
ingress-nginx controller   ← 설치함
  ↓
Ingress 규칙               ← 만듦
  ↓
Service                   ← 없거나 연결 안 됨
  ↓
Pod                       ← 없음
  ↓
Application               ← 없음
```

즉, 요청이 들어오는 앞단은 만들었는데, 정작 요청을 처리할 백엔드 앱이 없었던 것이다.

## 비유로 이해하기

건물로 비유하면 이런 상태다.

```text
건물 입구를 만들었다.
안내 데스크를 만들었다.
“손님이 오면 3층 식당으로 보내라”는 안내문도 붙였다.

그런데 3층 식당이 없다.
```

손님은 건물 입구까지 들어올 수 있다.
안내 데스크도 있다.
안내문도 있다.

그런데 최종 목적지인 식당이 없으니 안내 데스크는 손님을 보낼 수 없다.

이때 발생하는 것이 Kubernetes Ingress 실습에서의 `503 Service Temporarily Unavailable`이다.

```text
503 Service Temporarily Unavailable
= 요청은 ingress-nginx까지 왔지만,
  뒤에 연결할 Service 또는 Pod가 없다.
```

## Helm으로 설치한 것은 앱이 아니었다

처음에 실행한 명령어는 이런 형태였다.

```sh
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

이 명령어는 nginx 웹서버 앱을 설치한 것이 아니다.

정확히는 **ingress-nginx Controller**를 설치한 것이다.

```text
ingress-nginx Controller
= Ingress 규칙을 읽고,
  외부 요청을 적절한 Service로 보내주는 역할
```

즉, Helm으로 설치한 것은 “실제 응답할 앱”이 아니라 “요청을 받아서 라우팅해주는 시스템”이다.

Helm Chart는 여러 Kubernetes 리소스를 한 번에 설치한다.

예를 들어 ingress-nginx Chart는 대략 이런 것들을 만든다.

```text
Deployment
Pod
Service
ServiceAccount
ConfigMap
ClusterRole
ClusterRoleBinding
IngressClass
Webhook
```

그래서 Helm을 쓰면 뭔가 많이 설치된다.

하지만 여기서 설치되는 Pod는 **내가 테스트하려는 nginx 웹서버 Pod**가 아니다.
그건 **Ingress를 처리하는 Controller Pod**다.

이 차이가 중요하다.

```text
ingress-nginx controller Pod
= 요청을 라우팅하는 관리자

nginx app Pod
= 실제 웹페이지를 응답하는 애플리케이션
```

둘은 다르다.

## Ingress YAML은 앱을 만드는 게 아니다

그다음 만든 파일이 `nginx-ingress.yaml`이었다.

예를 들어 이런 형태다.

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

이 YAML은 앱을 만드는 파일이 아니다.

여기서 `kind`를 보면 알 수 있다.

```yaml
kind: Ingress
```

즉, 이 파일은 Ingress 리소스를 만든다.

Ingress의 역할은 이거다.

```text
localhost로 들어온 요청을 nginx Service의 80번 포트로 보내라
```

다시 말하면, 이 YAML은 “nginx 앱을 만들어라”가 아니다.

```text
nginx Service로 보내라는 라우팅 규칙을 만들어라
```

라는 뜻이다.

## Service에는 앱이 들어가지 않는다

여기서 또 헷갈릴 수 있다.

“그럼 Service 안에 앱이 들어가나?”

아니다.

Service 안에 앱이 들어가는 것이 아니다.
애플리케이션은 **Pod 안의 Container**에서 실행된다.

```text
Pod
 └── Container
      └── nginx / Spring Boot / FastAPI 같은 앱 실행
```

Service는 앱이 들어있는 공간이 아니라, **Pod로 가는 고정 입구**다.

```text
Service
= Pod를 찾아가는 고정 주소
```

전체 구조는 이렇게 봐야 한다.

```text
Ingress
  ↓
Service
  ↓
Pod
  ↓
Container
  ↓
Application
```

정확히 말하면:

```text
Application
= 실제 프로그램

Container
= 애플리케이션 실행 공간

Pod
= 컨테이너를 감싸는 Kubernetes의 최소 실행 단위

Service
= Pod로 가는 고정 입구

Ingress
= 외부 HTTP 요청을 어느 Service로 보낼지 정하는 규칙
```

## 왜 Service가 필요한가?

Pod는 언제든 죽었다가 다시 만들어질 수 있다.
그러면 Pod의 IP도 바뀔 수 있다.

예를 들어 처음에는 nginx Pod의 IP가 이랬다고 해보자.

```text
nginx-pod-1 → 10.42.0.12
```

그런데 Pod가 재시작되면 새 Pod가 만들어지고 IP가 바뀔 수 있다.

```text
nginx-pod-2 → 10.42.0.19
```

만약 Ingress가 Pod IP를 직접 바라본다면, Pod가 바뀔 때마다 Ingress 설정도 계속 바꿔야 한다.

그래서 중간에 Service를 둔다.

```text
Ingress
  ↓
nginx Service
  ↓
현재 살아있는 nginx Pod
```

Service는 Pod가 바뀌어도 고정된 이름으로 접근할 수 있게 해준다.

```text
nginx Service는 계속 nginx
뒤에 연결된 Pod만 바뀔 수 있음
```

## Service는 Pod를 어떻게 찾을까?

Service는 selector로 Pod를 찾는다.

예를 들어 Pod에 이런 label이 붙어 있다고 하자.

```yaml
labels:
  app: nginx
```

Service에는 이런 selector가 있다.

```yaml
selector:
  app: nginx
```

그러면 Service는 이렇게 판단한다.

```text
app=nginx 라벨이 붙은 Pod를 내 뒤에 연결하면 되겠네
```

즉, Service와 Pod는 이름으로 직접 연결되는 것이 아니라, 보통 label과 selector로 연결된다.

```text
Service selector: app=nginx
        ↓
Pod label: app=nginx
```

이 둘이 맞아야 Service가 Pod를 찾는다.

만약 selector와 label이 안 맞으면 Service는 Pod를 못 찾는다.

이때 `Endpoints`가 비어 있게 된다.

```sh
kubectl describe svc nginx
```

정상이라면:

```text
Endpoints: 10.42.0.12:80
```

문제가 있으면:

```text
Endpoints: <none>
```

`Endpoints: <none>`이면 Service가 연결할 Pod를 못 찾고 있다는 뜻이다.

## 그래서 503이 뜬 이유

이번 상태에서 503이 떴다는 건 이런 뜻이다.

```text
브라우저
  ↓
localhost:80
  ↓
ingress-nginx controller
```

여기까지는 도착했다.

그래서 예전처럼 `ERR_CONNECTION_REFUSED`가 아니라 nginx의 503 페이지가 나온 것이다.

하지만 그 뒤가 문제였다.

```text
ingress-nginx controller
  ↓
Ingress 규칙
  ↓
nginx Service
  ↓
nginx Pod
```

여기서 Service가 없거나, Pod가 없거나, Service가 Pod를 못 찾으면 503이 난다.

즉, 지금 상태는 이것이었다.

```text
Ingress Controller는 있음
Ingress 규칙도 있음
그런데 실제 응답할 앱이 없음
```

한 줄로 말하면:

```text
문지기와 안내문은 있는데, 목적지 방이 없는 상태
```

## 그럼 무엇을 만들어야 했나?

Ingress를 테스트하려면 실제 응답할 애플리케이션이 필요하다.

가장 간단한 테스트용 앱으로 nginx를 만들 수 있다.

```sh
kubectl create deployment nginx --image=nginx
```

이 명령어는 nginx 이미지를 사용하는 Deployment를 만든다.

Deployment는 Pod를 관리한다.

즉, 결과적으로 nginx 컨테이너가 들어있는 Pod가 생성된다.

```text
Deployment
  ↓
ReplicaSet
  ↓
Pod
  ↓
nginx Container
```

그다음 Service를 만들어야 한다.

```sh
kubectl expose deployment nginx --port=80 --target-port=80
```

이 명령어는 nginx Deployment 앞에 Service를 만든다.

의미는 다음과 같다.

```text
nginx Pod로 가는 고정 입구를 만들어라
```

그 다음에야 Ingress가 의미를 가진다.

```sh
kubectl apply -f nginx-ingress.yaml
```

이제 Ingress는 `nginx` Service로 요청을 보낼 수 있고, Service는 실제 nginx Pod로 요청을 넘길 수 있다.

## 올바른 실습 순서

Ingress 실습은 아래 순서로 이해하면 좋다.

```text
1. ingress-nginx Controller 설치
   → Helm 사용

2. nginx 앱 실행
   → Deployment 생성

3. nginx 앱으로 가는 Service 생성
   → Service 생성

4. localhost 요청을 nginx Service로 보내는 Ingress 생성
   → Ingress YAML apply
```

명령어로 보면 이렇게 된다.

```sh
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

```sh
kubectl create deployment nginx --image=nginx
```

```sh
kubectl expose deployment nginx --port=80 --target-port=80
```

```sh
kubectl apply -f nginx-ingress.yaml
```

확인은 이렇게 한다.

```sh
kubectl get pods
kubectl get svc
kubectl get ingress
```

Service가 Pod를 잘 잡고 있는지도 확인할 수 있다.

```sh
kubectl describe svc nginx
```

## 전체 구조 다시 보기

모든 것이 제대로 만들어지면 구조는 이렇게 된다.

```text
브라우저
  ↓
localhost:80
  ↓
k3d LoadBalancer
  ↓
ingress-nginx Controller
  ↓
nginx-ingress
  ↓
nginx Service
  ↓
nginx Pod
  ↓
nginx Container
  ↓
nginx Application
```

각각의 역할은 다음과 같다.

```text
k3d LoadBalancer
= 로컬 localhost:80 요청을 클러스터 안으로 넣어주는 입구

ingress-nginx Controller
= Ingress 규칙을 읽고 요청을 라우팅하는 담당자

nginx-ingress
= localhost 요청을 nginx Service로 보내라는 규칙

nginx Service
= nginx Pod로 가는 고정 입구

nginx Pod
= nginx 컨테이너가 실행되는 공간

nginx Application
= 실제 웹페이지를 응답하는 프로그램
```

이 중 하나라도 빠지면 정상적으로 접속되지 않는다.

## 이번 실습에서 내가 한 일 정리

이번 실습에서 처음에 만든 것은 이쪽이었다.

```text
k3d LoadBalancer
ingress-nginx Controller
Ingress 규칙
```

하지만 아직 이쪽이 없었다.

```text
nginx Service
nginx Pod
nginx Application
```

그래서 이런 상태였다.

```text
브라우저
  ↓
localhost:80
  ↓
ingress-nginx Controller
  ↓
Ingress 규칙
  ↓
nginx Service 없음
  ↓
nginx Pod 없음
  ↓
앱 없음
```

그러니 503이 나는 것이 자연스러운 상황이었다.

## 정리

이번 실습에서 헷갈렸던 핵심은 “Ingress를 만들었다”와 “앱을 만들었다”를 같은 의미로 생각한 데 있었다. Helm으로 설치한 `ingress-nginx`는 실제 웹 애플리케이션이 아니라, Ingress 규칙을 읽고 트래픽을 라우팅하는 Controller다. 그리고 `kubectl apply -f nginx-ingress.yaml`로 만든 Ingress는 앱이 아니라 라우팅 규칙이다. 실제 응답을 하려면 nginx, Spring Boot, FastAPI 같은 애플리케이션이 Pod 안에서 실행되고 있어야 하며, 그 Pod 앞에 Service가 있어야 한다. 즉, Ingress 실습이 정상 동작하려면 `Ingress Controller → Ingress → Service → Pod → Application` 흐름이 모두 연결되어야 한다. 이번 상태는 Controller와 Ingress 규칙은 만들었지만, 뒤쪽의 Service, Pod, Application이 없어서 503이 발생한 것이다.
