---
title: "[KUBERNETES] Endpoint는 Service가 실제로 바라보는 Pod 목록이다"
source: "https://velog.io/@yorange50/KUBERNETES-Endpoint는-Service가-실제로-바라보는-Pod-목록이다"
published: "2026-05-19T04:21:56.924Z"
tags: ""
backup_date: "2026-05-29T14:52:52.726305"
---

Kubernetes에서 Service를 만들면 우리는 보통 Service IP로 접근한다.

예를 들어 `nginx-svc`라는 Service가 있고, ClusterIP가 `10.43.144.200`이라고 해보자.

```bash
curl http://10.43.144.200
```

그러면 요청은 Service로 들어간다. 그런데 여기서 중요한 질문이 생긴다.

> Service는 실제로 어디로 요청을 보내는 걸까?

Service 자체가 애플리케이션을 실행하는 것은 아니다. 실제 애플리케이션은 Pod 안에서 실행된다. Service는 앞에서 고정된 주소 역할을 하고, 뒤에 있는 Pod들로 요청을 전달한다.

이때 Service 뒤에 실제로 연결된 Pod IP 목록을 보여주는 것이 바로 `Endpoint`다.

## 1. Endpoint를 확인하는 명령어

Endpoint는 다음 명령어로 확인할 수 있다.

```bash
kubectl get endpoints
```

나는 아래처럼 조회했다.

```bash
k get endpoints
```

출력 결과는 다음과 같았다.

```text
Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice

NAME                  ENDPOINTS                                      AGE
kubernetes            172.19.0.3:6443                                3h23m
my-app-loadbalancer   10.42.0.5:8080,10.42.1.5:8080,10.42.2.5:8080   3h8m
my-app-nodeport       10.42.0.5:8080,10.42.1.5:8080,10.42.2.5:8080   160m
nginx-svc             10.42.0.8:80,10.42.1.8:80,10.42.2.7:80         32m
```

처음 보면 IP가 여러 개 나와서 헷갈린다. 하지만 의미는 단순하다.

```text
Service 이름 → 실제 연결된 Pod IP 목록
```

즉, Service가 뒤에서 어떤 Pod들을 바라보고 있는지 보여주는 것이다.

## 2. Service와 Endpoint의 관계

Service는 사용자가 접근하는 고정 주소를 제공한다.

예를 들어 `nginx-svc`라는 Service가 있다고 하자.

```bash
kubectl get svc
```

출력 예시:

```text
NAME        TYPE        CLUSTER-IP      PORT(S)
nginx-svc   ClusterIP   10.43.144.200   80/TCP
```

여기서 `10.43.144.200`은 Service의 ClusterIP다.

즉, 클러스터 내부에서는 이 주소로 nginx 서비스에 접근할 수 있다.

```bash
curl http://10.43.144.200
```

그런데 실제 nginx가 실행되는 곳은 Service가 아니라 Pod다.

Pod IP는 따로 존재한다.

이번 출력에서는 `nginx-svc` 뒤에 이런 Pod IP들이 붙어 있었다.

```text
nginx-svc → 10.42.0.8:80, 10.42.1.8:80, 10.42.2.7:80
```

즉 구조는 이렇게 된다.

```text
curl-test Pod
    |
    | curl http://10.43.144.200
    v
nginx-svc Service
ClusterIP: 10.43.144.200
    |
    +-------------------+-------------------+
    |                   |                   |
    v                   v                   v
10.42.0.8:80       10.42.1.8:80       10.42.2.7:80
nginx Pod 1        nginx Pod 2        nginx Pod 3
```

정리하면 다음과 같다.

```text
ClusterIP = Service의 고정 IP
Endpoint = Service 뒤에 실제로 붙어 있는 Pod IP 목록
```

## 3. 왜 Endpoint가 필요할까?

Pod는 언제든지 사라지고 다시 만들어질 수 있다.

Deployment로 Pod를 3개 띄웠다고 해도, 장애가 나거나 재배포가 일어나면 기존 Pod가 죽고 새로운 Pod가 생길 수 있다.

이때 Pod IP도 바뀐다.

예를 들어 처음에는 이런 Pod들이 있었다고 하자.

```text
10.42.0.8
10.42.1.8
10.42.2.7
```

그런데 어떤 Pod가 재시작되면 새로운 IP를 받을 수 있다.

```text
10.42.2.7 삭제
10.42.2.9 새로 생성
```

만약 사용자가 Pod IP를 직접 바라보고 있었다면 문제가 생긴다.

```text
직접 Pod IP 접근
→ Pod가 죽으면 IP가 바뀜
→ 기존 주소로 접근 불가
```

그래서 Kubernetes에서는 Service를 사용한다.

Service는 고정된 IP를 제공하고, 뒤에 있는 Pod 목록은 Kubernetes가 계속 갱신한다.

```text
Service IP는 유지
Pod IP는 바뀔 수 있음
Endpoint는 현재 살아 있는 Pod 목록으로 갱신
```

즉 Endpoint는 Service가 현재 어느 Pod들에게 요청을 보낼 수 있는지 알려주는 연결 목록이다.

## 4. Service는 어떻게 Pod를 찾을까?

Service가 아무 Pod나 바라보는 것은 아니다.

Service는 `selector`를 기준으로 Pod를 찾는다.

예를 들어 Service YAML이 이렇게 되어 있다고 하자.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-svc
spec:
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 80
  type: ClusterIP
```

여기서 핵심은 이 부분이다.

```yaml
selector:
  app: nginx
```

이 뜻은 다음과 같다.

```text
app=nginx 라벨을 가진 Pod를 찾아라
```

그리고 Deployment에서 Pod에 이런 라벨을 붙이고 있다면:

```yaml
labels:
  app: nginx
```

Service는 이 Pod들을 자신의 대상으로 잡는다.

그 결과가 Endpoint에 나타난다.

```text
nginx-svc → 10.42.0.8:80, 10.42.1.8:80, 10.42.2.7:80
```

즉 Endpoint에 Pod IP가 잘 보인다는 것은 다음을 의미한다.

```text
Service selector가 Pod 라벨과 잘 맞음
Service가 Pod를 정상적으로 찾음
트래픽을 보낼 대상이 존재함
```

반대로 Endpoint가 비어 있으면 문제가 있다는 뜻이다.

```text
nginx-svc   <none>
```

이런 식으로 나오면 Service가 바라볼 Pod를 찾지 못한 것이다.

## 5. Endpoint가 비어 있으면 무엇을 의심해야 할까?

Service는 있는데 Endpoint가 비어 있다면 보통 selector와 label이 맞지 않는 경우가 많다.

예를 들어 Service는 이렇게 찾고 있다.

```yaml
selector:
  app: nginx
```

그런데 Pod 라벨은 이렇게 되어 있다.

```yaml
labels:
  app: my-nginx
```

그러면 Service는 Pod를 찾지 못한다.

```text
Service selector: app=nginx
Pod label: app=my-nginx
```

둘이 다르기 때문이다.

이때 `kubectl get endpoints`를 보면 Endpoint가 비어 있을 수 있다.

```text
NAME        ENDPOINTS
nginx-svc   <none>
```

이럴 때는 다음 명령어로 Pod 라벨을 확인하면 된다.

```bash
kubectl get pod --show-labels
```

그리고 Service의 selector를 확인한다.

```bash
kubectl describe svc nginx-svc
```

확인해야 할 것은 이 두 가지다.

```text
Service selector
Pod label
```

이 둘이 맞아야 Service가 Pod를 찾고 Endpoint가 생성된다.

## 6. 이번 출력 해석하기

이번에 조회한 결과를 다시 보자.

```text
NAME                  ENDPOINTS                                      AGE
my-app-loadbalancer   10.42.0.5:8080,10.42.1.5:8080,10.42.2.5:8080   3h8m
my-app-nodeport       10.42.0.5:8080,10.42.1.5:8080,10.42.2.5:8080   160m
nginx-svc             10.42.0.8:80,10.42.1.8:80,10.42.2.7:80         32m
```

먼저 `my-app-loadbalancer`를 보면:

```text
my-app-loadbalancer → 10.42.0.5:8080, 10.42.1.5:8080, 10.42.2.5:8080
```

이 뜻은 `my-app-loadbalancer` Service가 8080 포트로 떠 있는 Pod 3개를 바라보고 있다는 뜻이다.

다음으로 `my-app-nodeport`도 같은 Pod들을 바라보고 있다.

```text
my-app-nodeport → 10.42.0.5:8080, 10.42.1.5:8080, 10.42.2.5:8080
```

즉 `LoadBalancer` 타입 Service와 `NodePort` 타입 Service가 같은 애플리케이션 Pod 3개를 대상으로 잡고 있는 것이다.

마지막으로 `nginx-svc`는 nginx Pod 3개를 바라보고 있다.

```text
nginx-svc → 10.42.0.8:80, 10.42.1.8:80, 10.42.2.7:80
```

이 상태라면 `nginx-svc`로 요청했을 때 뒤의 세 Pod 중 하나로 요청이 전달될 수 있다.

## 7. Endpoint는 로드밸런싱 대상 목록이다

Service가 로드밸런싱을 한다고 할 때, 그 대상이 되는 Pod 목록이 바로 Endpoint에 표시된다.

예를 들어 `nginx-svc`의 Endpoint가 다음과 같다면:

```text
10.42.0.8:80
10.42.1.8:80
10.42.2.7:80
```

Service는 이 세 개의 주소 중 하나로 요청을 전달한다.

그래서 각 nginx Pod의 index.html을 다르게 바꿔두면 로드밸런싱을 눈으로 확인할 수 있다.

```text
10.42.0.8:80 → nginx-1
10.42.1.8:80 → nginx-2
10.42.2.7:80 → nginx-3
```

그 후 Service IP로 여러 번 curl을 날리면:

```bash
curl http://10.43.144.200
curl http://10.43.144.200
curl http://10.43.144.200
```

응답이 이렇게 바뀔 수 있다.

```text
nginx-1
nginx-3
nginx-2
```

이것은 Service가 Endpoint 목록에 있는 Pod들로 요청을 분산하고 있다는 뜻이다.

## 8. kubernetes Endpoint는 무엇일까?

출력에 이런 줄도 있었다.

```text
kubernetes   172.19.0.3:6443
```

이건 기본으로 존재하는 `kubernetes` Service의 Endpoint다.

Kubernetes 클러스터 안에는 기본적으로 `kubernetes`라는 Service가 있다.

이 Service는 Kubernetes API Server를 가리킨다.

여기서 `6443`은 Kubernetes API Server가 사용하는 포트다.

```text
kubernetes Service
→ API Server
→ 172.19.0.3:6443
```

즉 클러스터 내부의 구성요소들이 Kubernetes API Server와 통신할 수 있도록 기본 Service와 Endpoint가 존재하는 것이다.

## 9. v1 Endpoints deprecated 경고

명령어를 실행했을 때 이런 경고가 나왔다.

```text
Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
```

이 말은 Kubernetes v1.33 이상에서는 기존 `Endpoints` 리소스 대신 `EndpointSlice` 사용을 권장한다는 뜻이다.

예전에는 Service 뒤의 Pod 목록을 `Endpoints`라는 리소스로 관리했다.

하지만 Pod가 많아지면 하나의 Endpoints 객체가 너무 커질 수 있다.

그래서 Kubernetes는 더 효율적인 구조인 `EndpointSlice`를 사용한다.

간단히 비교하면 이렇다.

```text
Endpoints
= Service 뒤의 Pod IP 목록을 한 객체에 담는 기존 방식

EndpointSlice
= Service 뒤의 Pod IP 목록을 여러 조각으로 나누어 관리하는 방식
```

그래서 요즘 버전에서는 아래 명령을 쓰는 것이 더 권장된다.

```bash
kubectl get endpointslice
```

또는 줄여서:

```bash
kubectl get epslice
```

EndpointSlice를 조회하면 Service 뒤에 어떤 Pod들이 붙어 있는지 더 현대적인 방식으로 확인할 수 있다.

## 10. Endpoints와 EndpointSlice의 차이

둘 다 목적은 비슷하다.

```text
Service 뒤에 어떤 Pod IP들이 있는지 보여준다
```

하지만 관리 방식이 다르다.

| 구분    | Endpoints               | EndpointSlice               |
| ----- | ----------------------- | --------------------------- |
| 역할    | Service 뒤의 Pod IP 목록 관리 | Service 뒤의 Pod IP 목록 관리     |
| 방식    | 하나의 객체에 목록 저장           | 여러 Slice로 나누어 저장            |
| 장점    | 단순함                     | 대규모 Pod 환경에서 효율적            |
| 현재 상태 | v1.33+에서 deprecated 경고  | 권장 방식                       |
| 조회 명령 | `kubectl get endpoints` | `kubectl get endpointslice` |

작은 실습에서는 `kubectl get endpoints`를 봐도 이해하기 쉽다. 하지만 최신 Kubernetes에서는 `EndpointSlice`가 권장된다.

## 11. Service, Endpoint, Pod의 전체 관계

전체 관계를 정리하면 다음과 같다.

```text
사용자 또는 다른 Pod
        |
        | curl http://Service-ClusterIP
        v
Service
        |
        | selector로 Pod 탐색
        v
Endpoint / EndpointSlice
        |
        | 실제 Pod IP 목록
        v
Pod 1, Pod 2, Pod 3
```

좀 더 구체적으로 보면:

```text
curl-test Pod
        |
        | curl http://10.43.144.200
        v
nginx-svc Service
        |
        | Endpoint 목록 확인
        v
10.42.0.8:80
10.42.1.8:80
10.42.2.7:80
        |
        v
nginx Pod 1, nginx Pod 2, nginx Pod 3
```

Service는 고정된 입구 역할을 한다. Endpoint는 그 입구 뒤에 실제로 연결된 목적지 목록이다.

## 12. 정리

Endpoint는 Service가 실제로 바라보고 있는 Pod IP 목록이다.

`kubectl get svc`는 Service의 고정 주소를 보여준다.

```text
nginx-svc → ClusterIP 10.43.144.200
```

`kubectl get endpoints`는 Service 뒤에 붙은 실제 Pod 주소를 보여준다.

```text
nginx-svc → 10.42.0.8:80, 10.42.1.8:80, 10.42.2.7:80
```

즉 둘의 차이는 다음과 같다.

```text
Service ClusterIP
= 사용자가 접근하는 고정 주소

Endpoint
= Service가 요청을 전달할 실제 Pod 주소 목록
```

이번 실습에서 `nginx-svc`의 Endpoint가 세 개 보였다는 것은, Service가 nginx Pod 3개를 정상적으로 로드밸런싱 대상으로 잡고 있다는 뜻이다.

한 문장으로 정리하면 다음과 같다.

```text
Endpoint는 Service와 Pod 사이의 실제 연결 목록이며, Service가 어느 Pod로 트래픽을 보낼 수 있는지 확인할 때 보는 리소스다.
```
