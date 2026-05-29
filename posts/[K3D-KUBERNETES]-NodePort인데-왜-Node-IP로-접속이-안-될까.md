---
title: "[K3D/KUBERNETES] NodePort인데 왜 Node IP로 접속이 안 될까?"
source: "https://velog.io/@yorange50/K3DKUBERNETES-NodePort인데-왜-Node-IP로-접속이-안-될까"
published: "2026-05-19T04:42:35.260Z"
tags: ""
backup_date: "2026-05-29T14:52:52.725841"
---

Kubernetes에서 Service 타입 중 `NodePort`를 사용하면 외부에서 다음과 같은 형식으로 접근할 수 있다고 배운다.

```bash
curl <Node-IP>:<NodePort>
```

예를 들어 Service가 이렇게 떠 있다고 하자.

```bash
kubectl get svc nginx-svc
```

```text
NAME        TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
nginx-svc   NodePort   10.43.188.207   <none>        80:30001/TCP   68m
```

여기서 중요한 부분은 이것이다.

```text
TYPE       NodePort
PORT(S)    80:30001/TCP
```

즉, `nginx-svc`는 NodePort 타입이고, 외부에서 접근할 때는 `30001` 포트를 사용할 수 있다는 뜻이다.

그래서 자연스럽게 이런 생각이 든다.

```bash
curl <Node-IP>:30001
```

그런데 k3d 환경에서는 이게 바로 안 될 수 있다.

이번 글에서는 왜 그런지 정리해보려고 한다.

## 1. 현재 Node 정보 확인

먼저 Node 목록을 확인했다.

```bash
kubectl get nodes -o wide
```

출력은 다음과 같았다.

```text
NAME                      STATUS   ROLES                  INTERNAL-IP
k3d-my-cluster-agent-0    Ready    <none>                 172.19.0.4
k3d-my-cluster-agent-1    Ready    <none>                 172.19.0.5
k3d-my-cluster-server-0   Ready    control-plane,master   172.19.0.3
```

이걸 보면 Node IP가 다음처럼 보인다.

```text
server node  → 172.19.0.3
agent-0 node → 172.19.0.4
agent-1 node → 172.19.0.5
```

그리고 Service는 다음과 같다.

```bash
kubectl get svc nginx-svc
```

```text
NAME        TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
nginx-svc   NodePort   10.43.188.207   <none>        80:30001/TCP   68m
```

그러면 이론상 NodePort 접근은 이렇게 생각할 수 있다.

```bash
curl http://172.19.0.3:30001
curl http://172.19.0.4:30001
curl http://172.19.0.5:30001
```

하지만 k3d에서는 이 접근이 안 될 수 있다.

이유는 `172.19.0.x`가 내가 일반적으로 생각하는 VM IP가 아니기 때문이다.

## 2. k3d의 Node는 진짜 VM이 아니라 Docker 컨테이너다

일반적인 Kubernetes 실습에서는 VM 여러 대를 만들고 그 위에 Kubernetes를 설치한다.

예를 들면 이런 구조다.

```text
install-vm
   |
   | 같은 네트워크
   |
master-1  172.26.8.74
worker-1  172.26.3.104
worker-2  172.26.9.60
```

이 경우 Node IP는 진짜 VM의 IP다.

그래서 install-vm에서 다음처럼 접근할 수 있다.

```bash
curl 172.26.8.74:30001
curl 172.26.3.104:30001
curl 172.26.9.60:30001
```

하지만 k3d는 구조가 다르다.

k3d는 Kubernetes Node를 실제 VM으로 띄우는 것이 아니라 Docker 컨테이너로 띄운다.

즉, 내 Mac 안에 Docker Desktop이 있고, 그 Docker 내부에 k3d Node 컨테이너들이 있는 구조다.

```text
Mac
 |
 | Docker Desktop
 v
Docker 내부 네트워크
 |
 +-- k3d-my-cluster-server-0  172.19.0.3
 +-- k3d-my-cluster-agent-0   172.19.0.4
 +-- k3d-my-cluster-agent-1   172.19.0.5
```

여기서 `172.19.0.3`, `172.19.0.4`, `172.19.0.5`는 Mac의 일반 네트워크 IP가 아니라 Docker 내부 네트워크의 컨테이너 IP다.

그래서 Mac 터미널에서 바로 다음처럼 접근하면 안 될 수 있다.

```bash
curl http://172.19.0.3:30001
```

NodePort가 안 열린 것이 아니라, 내 Mac에서 Docker 내부 컨테이너 IP로 직접 라우팅이 안 되는 상황에 가깝다.

## 3. NodePort의 원래 의미

NodePort는 Kubernetes의 각 Node에 특정 포트를 열어주는 방식이다.

예를 들어 Service가 이렇게 되어 있다고 하자.

```text
nginx-svc   NodePort   10.43.188.207   80:30001/TCP
```

이 뜻은 다음과 같다.

```text
Service 내부 포트: 80
외부에서 접근할 NodePort: 30001
```

즉 구조는 이렇다.

```text
외부 사용자
   |
   | NodeIP:30001
   v
Kubernetes Node
   |
   v
NodePort Service
   |
   v
nginx Pod
```

일반 VM 환경에서는 외부에서 Node IP로 접근할 수 있으니 다음이 가능하다.

```bash
curl http://<Node-IP>:30001
```

하지만 k3d에서는 Node 자체가 Docker 컨테이너다.

그래서 NodePort가 열려 있어도, Mac host에서 그 컨테이너 IP로 바로 접근하는 것이 막힐 수 있다.

## 4. k3d에서는 포트를 따로 열어줘야 한다

k3d 환경에서 Mac에서 접근하고 싶다면 클러스터를 만들 때 포트를 열어줘야 한다.

예를 들어 다음처럼 클러스터를 생성한다.

```bash
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "30001:30001@loadbalancer"
```

이 설정의 의미는 다음과 같다.

```text
Mac localhost:30001
        |
        v
k3d loadbalancer container:30001
        |
        v
Kubernetes NodePort 30001
        |
        v
nginx-svc
        |
        v
nginx Pod
```

이렇게 만들면 Mac에서 다음처럼 접근할 수 있다.

```bash
curl http://localhost:30001
```

즉, k3d에서는 Node IP로 직접 들어가기보다 `localhost` 포트를 k3d 쪽으로 열어주는 방식을 사용한다.

## 5. 이걸 포트 포워딩이라고 해도 될까?

넓게 보면 포트 포워딩이라고 말해도 된다.

왜냐하면 내 Mac의 포트 `30001`로 들어온 요청을 k3d 내부의 포트 `30001`로 넘기는 구조이기 때문이다.

하지만 Kubernetes에서 말하는 `kubectl port-forward`와는 다르다.

헷갈리기 쉬운 두 가지를 비교해보자.

## 6. k3d `--port` 방식

```bash
k3d cluster create my-cluster \
  --port "30001:30001@loadbalancer"
```

이건 클러스터 생성 시점에 Docker/k3d 레벨에서 포트를 열어주는 것이다.

구조는 다음과 같다.

```text
Mac localhost:30001
   |
   v
k3d loadbalancer container:30001
   |
   v
Kubernetes NodePort 30001
```

이 방식은 클러스터가 살아 있는 동안 계속 유지된다.

그래서 매번 터미널에서 별도 명령을 실행하지 않아도 된다.

## 7. kubectl port-forward 방식

반면 `kubectl port-forward`는 다음처럼 쓴다.

```bash
kubectl port-forward svc/nginx-svc 8080:80
```

이건 kubectl이 임시 터널을 열어주는 방식이다.

구조는 다음과 같다.

```text
Mac localhost:8080
   |
   v
kubectl port-forward 터널
   |
   v
nginx-svc:80
```

이 방식은 해당 명령어가 실행 중일 때만 유지된다.

터미널을 종료하거나 명령을 끊으면 포트포워딩도 종료된다.

## 8. k3d --port와 kubectl port-forward 비교

| 구분    | k3d `--port`         | `kubectl port-forward`    |
| ----- | -------------------- | ------------------------- |
| 동작 계층 | Docker/k3d 레벨        | Kubernetes API/kubectl 레벨 |
| 설정 시점 | 클러스터 생성 시점           | 필요할 때마다 실행                |
| 접근 방식 | `localhost:NodePort` | `localhost:로컬포트`          |
| 지속성   | 클러스터가 살아 있는 동안 유지    | 명령 실행 중에만 유지              |
| 주 용도  | k3d 외부 접근 테스트        | 임시 디버깅, 로컬 테스트            |

둘 다 넓게는 포트 포워딩이라고 말할 수 있다.

하지만 정확히 구분하면:

```text
k3d --port
= Docker/k3d의 포트 매핑

kubectl port-forward
= kubectl이 만들어주는 임시 터널
```

이렇게 보는 것이 더 정확하다.

## 9. ClusterIP와 NodePort 접근 차이

현재 Service는 다음과 같다.

```text
nginx-svc   NodePort   10.43.188.207   <none>   80:30001/TCP
```

여기서 `10.43.188.207`은 ClusterIP다.

NodePort 타입 Service라고 해서 ClusterIP가 사라지는 것은 아니다.

NodePort Service는 사실 ClusterIP 기능에 외부 포트가 추가된 형태라고 볼 수 있다.

그래서 접근 방식이 두 개다.

```text
클러스터 내부 접근
→ ClusterIP 사용
→ curl http://10.43.188.207

클러스터 외부 접근
→ Node IP + NodePort 사용
→ curl http://<Node-IP>:30001
```

다만 k3d에서는 Node IP가 Docker 내부 IP이기 때문에 Mac에서 직접 접근이 안 될 수 있다.

그래서 Mac에서 접근하려면 다음처럼 포트를 열어준다.

```bash
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "30001:30001@loadbalancer"
```

그 후에는 다음처럼 접근한다.

```bash
curl http://localhost:30001
```

## 10. 클러스터 내부에서 테스트하는 방법

만약 ClusterIP로 테스트하고 싶다면 클러스터 내부에서 요청을 보내면 된다.

예를 들어 curl이 들어 있는 임시 Pod를 띄운다.

```bash
kubectl run curl-test --image=curlimages/curl -it --rm -- sh
```

그 안에서 Service의 ClusterIP로 요청한다.

```bash
curl http://10.43.188.207
```

이 흐름은 다음과 같다.

```text
curl-test Pod
   |
   | curl http://10.43.188.207
   v
nginx-svc ClusterIP
   |
   v
nginx Pod
```

이 방식은 외부 접근이 아니라 클러스터 내부 접근이다.

따라서 k3d의 Docker 네트워크 문제와 상관없이 잘 동작한다.

## 11. 클러스터 외부에서 테스트하는 방법

반대로 Mac에서 직접 접근하고 싶다면 NodePort를 host로 열어야 한다.

클러스터 생성 시:

```bash
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "30001:30001@loadbalancer"
```

그 다음 Mac에서:

```bash
curl http://localhost:30001
```

이 방식은 다음 구조다.

```text
Mac
 |
 | localhost:30001
 v
k3d loadbalancer
 |
 v
NodePort 30001
 |
 v
nginx-svc
 |
 v
nginx Pod
```

## 12. 왜 강의 자료와 내 환경이 다르게 느껴질까?

강의 자료에서는 이런 식으로 되어 있을 수 있다.

```bash
curl 172.26.8.74:30001  # master-1
curl 172.26.3.104:30001 # worker-1
curl 172.26.9.60:30001  # worker-2
```

이건 보통 실제 VM 기반 Kubernetes 실습 환경을 전제로 한다.

즉 Node들이 실제 VM이고, `install-vm`이 그 VM들과 같은 네트워크에 있다.

```text
install-vm
 |
 +-- master-1
 +-- worker-1
 +-- worker-2
```

그래서 install-vm에서 Node IP로 직접 접근할 수 있다.

하지만 내 환경은 k3d다.

```text
Mac
 |
Docker Desktop
 |
k3d node containers
```

여기서 Node IP는 Docker 내부 컨테이너 IP다.

그래서 강의처럼 Node IP로 바로 curl 하는 흐름이 그대로 맞지 않을 수 있다.

이 차이를 이해해야 한다.

## 13. 정리

NodePort는 모든 Node에 외부 접근용 포트를 열어주는 Service 타입이다.

일반적인 VM 기반 Kubernetes에서는 다음처럼 접근할 수 있다.

```bash
curl http://<Node-IP>:<NodePort>
```

하지만 k3d에서는 Node가 실제 VM이 아니라 Docker 컨테이너다.

그래서 `kubectl get nodes -o wide`에 보이는 `172.19.0.x` IP는 Docker 내부 네트워크 IP이고, Mac에서 직접 접근이 안 될 수 있다.

이때는 클러스터 생성 시 k3d 포트 매핑을 추가해야 한다.

```bash
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "30001:30001@loadbalancer"
```

그러면 Mac에서 다음처럼 접근할 수 있다.

```bash
curl http://localhost:30001
```

한 문장으로 정리하면 다음과 같다.

```text
k3d에서 NodePort를 Mac에서 테스트하려면 Node IP로 직접 접근하는 대신, k3d --port 옵션으로 host 포트를 열어 localhost로 접근하는 방식이 안전하다.
```
