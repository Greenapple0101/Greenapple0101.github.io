---
title: "[Kubernetes] 클러스터 네트워킹 구성: Docker 네트워크부터 kube-proxy까지"
source: ""
published: "2026-05-30T17:17:56.000Z"
---

쿠버네티스 네트워킹을 이해하려면 바로 Service, Ingress부터 외우기보다 먼저 **컨테이너가 네트워크를 어떻게 갖는지**를 봐야 한다. 이번 강의의 핵심은 크게 두 가지다.

```text
1. 도커 컨테이너 네트워킹
2. kube-proxy
```

즉, 먼저 단일 호스트와 멀티 호스트에서 컨테이너 네트워크가 어떻게 만들어지는지 보고, 그다음 쿠버네티스 Service가 실제로 어떻게 Pod들에게 트래픽을 보내는지 보는 흐름이다. 

---

## 1. 컨테이너 네트워킹을 왜 알아야 할까?

쿠버네티스에서 Pod는 각각 IP를 가진다.

```bash
kubectl get pods -o wide
```

이 명령어를 치면 Pod마다 IP가 보인다.

```text
NAME        READY   STATUS    IP          NODE
web-xxx     1/1     Running   10.40.0.1   node1
web-yyy     1/1     Running   10.32.0.2   node2
web-zzz     1/1     Running   10.46.0.2   node3
```

그런데 여기서 궁금해진다.

```text
이 IP는 누가 주는 걸까?

Pod가 다른 Node에 있어도 어떻게 통신할까?

Service IP로 요청했는데 실제 Pod까지는 어떻게 갈까?
```

이 질문에 답하려면 컨테이너 네트워킹, CNI, kube-proxy를 같이 봐야 한다.

---

## 2. Docker 컨테이너 네트워킹

도커는 기본적으로 컨테이너 네트워크를 만들 때 `docker0`라는 브리지를 사용한다.

```text
docker0
→ Docker가 기본으로 만드는 virtual ethernet bridge
```

강의에서는 Docker의 기본 네트워크 대역을 다음처럼 설명한다.

```text
docker0 bridge: 172.17.0.1
container IP: 172.17.X.Y
network: 172.17.0.0/16
```

즉, 컨테이너가 실행되면 Docker는 컨테이너에 IP를 하나 할당한다.

```text
mysql container      → 172.17.0.2
wordpress container  → 172.17.0.3
docker0 bridge       → 172.17.0.1
host eth0            → 172.27.20.50
```

구조로 보면 이렇다.

```text
Host
 ├── eth0
 │    └── 172.27.20.50
 │
 ├── docker0 bridge
 │    └── 172.17.0.1
 │
 ├── mysql container
 │    └── 172.17.0.2
 │
 └── wordpress container
      └── 172.17.0.3
```

컨테이너들은 직접 외부 네트워크에 붙는 것이 아니라, 보통 `docker0` 브리지를 통해 통신한다.

---

## 3. veth 인터페이스

컨테이너가 생성될 때는 `veth` 인터페이스가 함께 만들어진다.

`veth`는 virtual ethernet pair라고 보면 된다.
두 개의 가상 네트워크 인터페이스가 쌍으로 만들어지고, 한쪽은 컨테이너 안에, 다른 한쪽은 호스트 쪽 브리지에 연결된다.

```text
container
  └── eth0
       ↕
     veth pair
       ↕
docker0 bridge
```

조금 더 풀면 이렇다.

```text
Container 내부 eth0
        ↓
veth pair
        ↓
Host의 docker0 bridge
        ↓
Host eth0
        ↓
외부 네트워크
```

그래서 컨테이너는 자기 안에서는 그냥 `eth0`을 쓰는 것처럼 보이지만, 실제로는 호스트의 브리지 네트워크를 통해 외부와 통신한다.

---

## 4. 단일 호스트 컨테이너 네트워킹

단일 호스트에서는 구조가 비교적 단순하다.

```text
host1
 ├── docker0 bridge: 172.17.0.1
 ├── container A: 172.17.0.2
 └── container B: 172.17.0.3
```

같은 호스트 안에 있는 컨테이너들은 같은 `docker0` 브리지에 연결되어 있다.

그래서 서로 통신할 수 있다.

```text
container A
  → docker0 bridge
  → container B
```

즉, 단일 호스트에서는 `docker0` 브리지가 컨테이너들을 이어주는 스위치처럼 동작한다.

---

## 5. 멀티 호스트 컨테이너 네트워킹의 문제

문제는 여러 호스트가 있을 때다.

예를 들어 host1과 host2가 있다고 하자.

```text
host1
 ├── eth0: 172.27.20.50
 ├── docker0: 172.17.0.1
 ├── container A: 172.17.0.2
 └── container B: 172.17.0.3

host2
 ├── eth0: 172.27.20.51
 ├── docker0: 172.17.0.1
 ├── container C: 172.17.0.2
 └── container D: 172.17.0.3
```

여기서 문제가 생긴다.

```text
host1의 container A: 172.17.0.2
host2의 container C: 172.17.0.2
```

IP가 겹칠 수 있다.

단일 Docker 호스트 기준으로는 문제가 없지만, 여러 호스트를 하나의 클러스터처럼 운영하려면 이 구조만으로는 부족하다.

쿠버네티스에서는 여러 Node에 있는 Pod들이 서로 통신할 수 있어야 한다.

```text
Node1의 Pod
  ↔
Node2의 Pod
```

이걸 해결하기 위해 필요한 것이 CNI다.

---

## 6. CNI란?

`CNI`는 Container Network Interface의 약자다.

쿠버네티스에서 Pod 네트워크를 실제로 구성해주는 플러그인 규격이다.

쿠버네티스는 이런 네트워크 모델을 요구한다.

```text
모든 Pod는 고유한 IP를 가져야 한다.

Pod끼리는 NAT 없이 통신할 수 있어야 한다.

Node는 모든 Pod와 통신할 수 있어야 한다.
```

하지만 쿠버네티스 자체가 이 네트워크를 직접 구현하지는 않는다.
실제 구현은 CNI 플러그인이 담당한다.

대표적인 CNI는 다음과 같다.

```text
Flannel
Calico
Cilium
Weave Net
Canal
Antrea
```

CNI가 하는 일은 대략 이렇다.

```text
Pod에 IP 할당

Pod용 네트워크 인터페이스 생성

veth pair 구성

브리지 또는 라우팅 구성

Node 간 Pod 통신 설정

필요하면 iptables, route, overlay network 설정
```

---

## 7. CNI가 구성하는 Pod 네트워크 예시

강의에서는 Node별로 Pod 네트워크 대역을 나누는 그림이 나온다.

예를 들어 이런 식이다.

```text
host1
 ├── eth0: 172.27.20.50
 ├── Pod network: 10.244.1.0/24
 ├── bridge: 10.244.1.1
 ├── container: 10.244.1.2
 └── container: 10.244.1.3

host2
 ├── eth0: 172.27.20.51
 ├── Pod network: 10.244.2.0/24
 ├── bridge: 10.244.2.1
 ├── container: 10.244.2.2
 └── container: 10.244.2.3
```

이렇게 Node마다 다른 Pod CIDR을 받으면 IP가 겹치지 않는다.

```text
host1 Pod 대역: 10.244.1.0/24
host2 Pod 대역: 10.244.2.0/24
```

그리고 라우팅 테이블에는 이런 식으로 경로가 잡힐 수 있다.

```text
10.244.1.0/24 → 172.27.20.50
10.244.2.0/24 → 172.27.20.51
```

즉, 어떤 Pod IP가 어느 Node 뒤에 있는지 알 수 있게 만든다.

---

## 8. Pod 네트워크 흐름

Node1의 Pod가 Node2의 Pod로 통신한다고 해보자.

```text
Pod A: 10.244.1.2
Pod B: 10.244.2.2
```

흐름은 대략 이렇다.

```text
Pod A
  ↓
Node1의 Pod bridge
  ↓
Node1 eth0
  ↓
Node 간 네트워크
  ↓
Node2 eth0
  ↓
Node2의 Pod bridge
  ↓
Pod B
```

즉, Pod끼리 통신하는 것처럼 보이지만 실제로는 Node 네트워크, 라우팅, CNI 설정이 함께 동작한다.

---

## 9. 쿠버네티스 Service가 필요한 이유

Pod는 IP를 가진다.

하지만 Pod IP는 안정적이지 않다.

```text
Pod 삭제
Pod 재생성
Pod 스케일 아웃
Pod 스케일 인
Pod 다른 Node로 이동
```

이 과정에서 Pod IP는 바뀔 수 있다.

예를 들어 `web` Deployment가 Pod 3개를 만든다고 하자.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webui
  template:
    metadata:
      labels:
        app: webui
    spec:
      containers:
        - name: nginx-container
          image: nginx:1.14
```

생성된 Pod들은 이런 IP를 가질 수 있다.

```text
app: webui → 10.40.0.1
app: webui → 10.32.0.2
app: webui → 10.46.0.2
```

그런데 클라이언트가 이 Pod IP들을 직접 알 필요는 없다.

쿠버네티스에서는 Service를 만들어서 Pod들을 하나의 고정된 접근 지점으로 묶는다.

---

## 10. Service 예시

강의 예시에서는 `webui-svc`라는 Service를 만든다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: webui-svc
spec:
  clusterIP: 10.96.100.100
  selector:
    app: webui
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```

이 Service는 이렇게 동작한다.

```text
Service 이름: webui-svc
Service IP: 10.96.100.100
selector: app=webui
port: 80
targetPort: 80
```

즉, `app=webui` 라벨을 가진 Pod들을 찾아서 하나의 Service 뒤에 묶는다.

```text
webui-svc: 10.96.100.100
        ↓
Pod 1: 10.40.0.1
Pod 2: 10.32.0.2
Pod 3: 10.46.0.2
```

클라이언트는 Pod IP를 직접 몰라도 된다.

```text
클라이언트
  ↓
10.96.100.100:80
  ↓
webui Pod 중 하나
```

---

## 11. kube-proxy란?

Service를 만들면 궁금해진다.

```text
Service IP 10.96.100.100으로 요청했는데
어떻게 실제 Pod IP 10.40.0.1, 10.32.0.2, 10.46.0.2로 전달될까?
```

이때 등장하는 것이 `kube-proxy`다.

`kube-proxy`는 각 Worker Node에서 실행되며, Service 트래픽이 실제 Pod로 전달되도록 네트워크 규칙을 구성한다.

```text
kube-proxy
→ Service IP로 들어온 트래픽을 실제 Pod IP로 보내는 규칙을 만든다
```

강의에서는 kube-proxy의 기본 mode가 `iptables`라고 설명한다.

즉, kube-proxy는 각 Node에 iptables rule을 만들어서 Service IP와 Pod IP 사이의 트래픽 전달을 처리한다.

---

## 12. kube-proxy와 iptables

Service가 만들어지면 kube-proxy는 API Server를 통해 Service와 Endpoint 정보를 감시한다.

```text
API Server
  ↓
Service 정보
Endpoint 정보
  ↓
각 Node의 kube-proxy
  ↓
iptables rule 생성
```

예를 들어 Service가 다음 Pod들을 바라본다고 하자.

```text
Service IP: 10.96.100.100

Endpoints:
- 10.46.0.2
- 10.32.0.2
- 10.40.0.1
```

각 Node의 kube-proxy는 이 정보를 기반으로 iptables rule을 만든다.

```text
Node1 kube-proxy → iptables rule
Node2 kube-proxy → iptables rule
Node3 kube-proxy → iptables rule
```

그래서 어떤 Node에서 Service IP로 접근하더라도, 실제 Pod 중 하나로 트래픽이 전달될 수 있다.

---

## 13. kube-proxy 동작 방식 3가지

kube-proxy에는 대표적으로 세 가지 동작 방식이 있다.

```text
1. User space mode
2. iptables mode
3. IPVS mode
```

---

## 14. User space mode

초기 방식이다.

트래픽이 kube-proxy 프로세스를 직접 거쳐서 backend Pod로 전달된다.

```text
Client
  ↓
Service IP
  ↓
kube-proxy
  ↓
Backend Pod
```

구조가 직관적이지만, 트래픽이 사용자 공간의 kube-proxy 프로세스를 거치기 때문에 성능상 불리할 수 있다.

요즘 실무에서는 기본적으로 자주 쓰는 방식은 아니다.

---

## 15. iptables mode

iptables mode는 kube-proxy의 기본적인 대표 방식이다.

kube-proxy가 직접 트래픽을 프록시하는 것이 아니라, 커널의 iptables NAT 규칙을 만들어둔다.

```text
Client
  ↓
Service IP
  ↓
iptables rule
  ↓
Backend Pod
```

즉, kube-proxy는 계속 트래픽을 중계하는 것이 아니라, 규칙을 만들어주는 역할에 가깝다.

```text
kube-proxy
→ Service/Endpoint 감시
→ iptables rule 생성/수정
```

강의에서 강조한 기본 mode가 바로 이 iptables mode다.

---

## 16. IPVS mode

IPVS mode는 Linux IPVS 기능을 사용하는 방식이다.

IPVS는 L4 로드밸런싱 기능을 제공한다.

구조는 이렇게 볼 수 있다.

```text
Client
  ↓
ClusterIP Virtual Server
  ↓
Real Server, Backend Pod
```

IPVS mode는 대규모 Service 환경에서 iptables보다 더 효율적인 로드밸런싱을 제공할 수 있다.

```text
iptables mode
→ 규칙 기반 NAT 처리

IPVS mode
→ 커널 레벨 L4 로드밸런서 방식
```

---

## 17. Service와 kube-proxy의 관계

Service는 “개념적 리소스”다.

```text
Service
→ app=webui Pod들을 하나의 IP로 묶어줘
```

kube-proxy는 그 Service가 실제로 동작하도록 Node에 네트워크 규칙을 만든다.

```text
kube-proxy
→ Service IP로 들어온 요청을 Pod IP로 보내는 규칙 생성
```

즉, 둘의 관계는 이렇게 정리할 수 있다.

```text
Service
→ 어떤 Pod들을 하나로 묶을지 정의

Endpoint
→ Service 뒤에 실제로 연결된 Pod IP 목록

kube-proxy
→ Service IP에서 Endpoint IP로 가는 네트워크 규칙 생성
```

---

## 18. 실습 흐름

강의에서는 Service와 kube-proxy 동작을 확인하는 실습 흐름도 나온다.

### 1단계. Deployment와 Service 생성

```bash
cat deployment.yaml
cat svc.yaml

kubectl apply -f deployment.yaml
kubectl apply -f svc.yaml

kubectl get all
```

이 단계에서는 `webui` Deployment와 `webui-svc` Service를 만든다.

---

### 2단계. kube-proxy 확인

Worker Node에서 kube-proxy가 실행 중인지 확인한다.

```bash
kubectl get pod -n kube-system -o wide | grep kube-proxy
```

kube-proxy는 보통 각 Node마다 하나씩 떠 있는 DaemonSet 형태로 동작한다.

---

### 3단계. iptables rule 확인

Worker Node에 접속해서 iptables NAT 규칙을 확인한다.

```bash
iptables -t nat -S | grep 80
```

또는 Service IP를 기준으로 확인할 수도 있다.

```bash
iptables -t nat -S | grep 10.96.100.100
```

여기서 Service 포트와 관련된 NAT 규칙을 볼 수 있다.

---

### 4단계. 리소스 삭제

실습이 끝나면 Deployment와 Service를 삭제한다.

```bash
kubectl delete deployments.apps webui
kubectl delete svc webui-svc
```

삭제 후에는 kube-proxy가 관련 iptables rule도 정리한다.

---

## 19. 전체 흐름 한 번에 정리

쿠버네티스 클러스터 네트워킹 흐름은 이렇게 정리할 수 있다.

```text
1. 컨테이너가 생성된다.
2. veth 인터페이스가 만들어진다.
3. CNI가 Pod IP를 할당한다.
4. Node별 Pod 네트워크가 구성된다.
5. Pod들은 서로 통신할 수 있다.
6. Deployment가 여러 Pod를 만든다.
7. Service가 Pod들을 하나의 ClusterIP로 묶는다.
8. kube-proxy가 Service IP → Pod IP 규칙을 만든다.
9. 클라이언트는 Service IP 또는 Service 이름으로 접근한다.
10. 트래픽은 실제 Pod 중 하나로 전달된다.
```

그림처럼 보면 이렇다.

```text
Client
  ↓
Service ClusterIP
  ↓
iptables / IPVS rule
  ↓
Endpoint Pod IP
  ↓
Pod Container
```

---

## 20. 헷갈리는 포인트 정리

### docker0와 CNI의 차이

```text
docker0
→ Docker 단일 호스트 컨테이너 네트워크에서 기본 브리지 역할

CNI
→ Kubernetes Pod 네트워크를 구성하는 플러그인 규격
```

Docker 단일 호스트에서는 docker0만 봐도 되지만, 쿠버네티스처럼 여러 Node에 걸친 Pod 통신에서는 CNI가 중요하다.

---

### Pod IP와 Service IP의 차이

```text
Pod IP
→ 실제 Pod에 할당되는 IP
→ Pod 재생성 시 바뀔 수 있음

Service IP
→ Pod들을 묶는 고정 가상 IP
→ 클라이언트가 안정적으로 접근하는 주소
```

Pod IP를 직접 쓰는 것은 불안정하다.
보통은 Service를 통해 접근한다.

---

### Service와 kube-proxy의 차이

```text
Service
→ 어떤 Pod들을 하나로 묶을지 선언하는 Kubernetes 리소스

kube-proxy
→ 그 Service가 실제 네트워크에서 동작하도록 Node에 규칙을 만드는 컴포넌트
```

Service만 만든다고 마법처럼 되는 것이 아니라, 각 Node의 kube-proxy가 iptables 또는 IPVS 규칙을 구성해준다.

---

### Endpoint란?

Service는 selector로 Pod를 찾는다.

```yaml
selector:
  app: webui
```

이 selector와 일치하는 Pod들이 Endpoint가 된다.

```text
Service: webui-svc
Endpoints:
- 10.46.0.2
- 10.32.0.2
- 10.40.0.1
```

확인은 이렇게 한다.

```bash
kubectl get endpoints
```

또는

```bash
kubectl describe svc webui-svc
```

---

## 21. 장애 확인 순서

Service 통신이 안 될 때는 무작정 Pod만 보지 말고 순서대로 확인하는 게 좋다.

```bash
kubectl get pods -o wide
```

Pod IP와 Node 위치를 확인한다.

```bash
kubectl get svc
```

Service가 생성됐는지 확인한다.

```bash
kubectl get endpoints
```

Service 뒤에 실제 Pod IP가 붙었는지 확인한다.

```bash
kubectl describe svc webui-svc
```

selector와 endpoint를 확인한다.

```bash
kubectl get pod -n kube-system -o wide | grep kube-proxy
```

kube-proxy가 각 Node에서 동작 중인지 확인한다.

```bash
iptables -t nat -S | grep <service-port>
```

Worker Node에서 실제 NAT rule이 만들어졌는지 확인한다.

---

## 22. 정리

이번 클러스터 네트워킹 구성의 핵심은 두 가지다.

```text
도커 컨테이너 네트워킹
→ docker0, veth, bridge, 단일 호스트 통신 구조 이해

쿠버네티스 네트워킹
→ CNI, Pod IP, Service IP, kube-proxy, iptables/IPVS 이해
```

최종적으로 이렇게 기억하면 된다.

```text
컨테이너는 veth를 통해 브리지에 연결된다.

쿠버네티스에서는 CNI가 Pod 네트워크를 구성한다.

Pod IP는 실제 Pod에 붙는 IP다.

Service IP는 여러 Pod를 묶는 안정적인 가상 IP다.

kube-proxy는 Service IP로 들어온 트래픽을 실제 Pod IP로 보내기 위한 규칙을 만든다.

기본적으로 kube-proxy는 iptables mode를 많이 사용한다.
```

한 줄로 요약하면 이렇다.

> 쿠버네티스 클러스터 네트워킹은 “각 Pod에 IP를 주고, 여러 Node에 흩어진 Pod들이 통신하게 만들고, Service와 kube-proxy로 Pod 집합에 안정적인 접근 경로를 제공하는 구조”다.
