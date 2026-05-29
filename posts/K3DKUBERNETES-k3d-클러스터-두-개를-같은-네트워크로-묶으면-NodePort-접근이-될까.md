---
title: "[K3D/KUBERNETES] k3d 클러스터 두 개를 같은 네트워크로 묶으면 NodePort 접근이 될까?"
source: "https://velog.io/@yorange50/K3DKUBERNETES-k3d-클러스터-두-개를-같은-네트워크로-묶으면-NodePort-접근이-될까"
published: "2026-05-19T05:07:26.639Z"
tags: ""
backup_date: "2026-05-29T14:52:52.724693"
---

Kubernetes에서 `NodePort`를 배우면 보통 이렇게 접근한다고 배운다.

```bash
curl http://<NodeIP>:<NodePort>
```

예를 들어 Service가 이렇게 떠 있다고 하자.

```bash
kubectl get svc nginx-svc
```

```text
NAME        TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)
nginx-svc   NodePort   10.43.188.207   <none>        80:30001/TCP
```

여기서 `30001`이 NodePort다.

일반적인 VM이나 AWS 환경이라면 외부 호스트에서 다음처럼 접근할 수 있다.

```bash
curl http://<worker-node-external-ip>:30001
```

그런데 k3d 환경에서는 이게 바로 안 될 수 있다.

왜냐하면 k3d의 Node는 실제 VM이 아니라 Docker 컨테이너이기 때문이다.

---

## 1. k3d에서 Node IP 접근이 헷갈리는 이유

k3d에서 Node를 조회하면 이런 식으로 나온다.

```bash
kubectl get nodes -o wide
```

```text
NAME                      STATUS   ROLES                  INTERNAL-IP
k3d-my-cluster-agent-0    Ready    <none>                 172.19.0.4
k3d-my-cluster-agent-1    Ready    <none>                 172.19.0.5
k3d-my-cluster-server-0   Ready    control-plane,master   172.19.0.3
```

처음 보면 이렇게 생각할 수 있다.

```bash
curl http://172.19.0.3:30001
curl http://172.19.0.4:30001
curl http://172.19.0.5:30001
```

그런데 Mac에서 바로 접근이 안 될 수 있다.

이유는 `172.19.0.x`가 내 Mac이 직접 접근할 수 있는 실제 VM IP가 아니라, Docker 내부 네트워크의 컨테이너 IP이기 때문이다.

구조는 대략 이렇다.

```text
Mac
 |
Docker Desktop
 |
Docker 내부 네트워크
 |
k3d node containers
```

즉, k3d의 Node IP는 Kubernetes Node의 IP이긴 하지만, 동시에 Docker 컨테이너의 내부 IP다.

그래서 일반 VM처럼 외부에서 바로 `NodeIP:NodePort`로 접근하는 느낌과 다르다.

---

## 2. 그래서 k3d에서는 보통 포트 매핑을 한다

k3d에서 Mac host에서 NodePort로 접근하려면 클러스터를 만들 때 포트 매핑을 해준다.

```bash
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "30001:30001@loadbalancer"
```

이 의미는 다음과 같다.

```text
Mac localhost:30001
        ↓
k3d loadbalancer container:30001
        ↓
Kubernetes NodePort 30001
        ↓
nginx-svc
        ↓
nginx Pod
```

그래서 Mac에서는 이렇게 접근할 수 있다.

```bash
curl http://localhost:30001
```

여기서 중요한 점은 이거다.

```text
NodePort 30001은 Kubernetes 내부에서 열린 포트
k3d --port 30001:30001은 Mac에서 그 포트로 들어갈 수 있게 해주는 Docker/k3d 포트 매핑
```

---

## 3. 그러면 외부 클러스터를 하나 더 만들면 되지 않을까?

이런 생각을 해볼 수 있다.

> 외부 클러스터를 하나 더 만들어서, 그 클러스터를 외부 호스트처럼 쓰면 되지 않을까?
> 그 안에서 대상 클러스터의 NodeIP:NodePort로 접속하면 되지 않을까?

발상 자체는 맞다.

다만 핵심은 “클러스터를 하나 더 만들었느냐”가 아니다.

진짜 핵심은 이것이다.

```text
접속하는 쪽에서 대상 클러스터의 Node IP까지 네트워크로 도달할 수 있는가?
```

즉, 외부 클러스터든, 일반 VM이든, EC2든, 내 노트북이든 상관없다.

대상 Node IP로 라우팅이 가능하고, 대상 NodePort가 방화벽에서 열려 있으면 접근할 수 있다.

---

## 4. 그런데 k3d 클러스터 두 개는 기본적으로 네트워크가 분리될 수 있다

예를 들어 k3d 클러스터를 두 개 만든다고 해보자.

```text
target-cluster
outside-cluster
```

그리고 `outside-cluster` 안의 Pod에서 `target-cluster`의 Node IP로 접근하려고 한다.

```text
outside-cluster의 curl-test Pod
        ↓
target-cluster NodeIP:30001
        ↓
target-cluster NodePort Service
```

이론적으로는 가능해 보인다.

하지만 k3d는 클러스터를 만들 때 Docker network를 따로 만들 수 있다.

그러면 구조가 이렇게 된다.

```text
Docker network A
 └─ target-cluster nodes

Docker network B
 └─ outside-cluster nodes
```

이렇게 네트워크가 분리되어 있으면 `outside-cluster`에서 `target-cluster`의 Node IP로 바로 접근하지 못할 수 있다.

즉, 클러스터가 두 개라는 사실보다 더 중요한 건 두 클러스터가 같은 네트워크에 있느냐다.

---

## 5. 두 k3d 클러스터를 같은 Docker network로 묶기

k3d는 클러스터 생성 시 `--network` 옵션으로 기존 Docker network에 붙일 수 있다.

먼저 공용 Docker network를 만든다.

```bash
docker network create k3d-shared-net
```

그다음 대상 클러스터를 만든다.

```bash
k3d cluster create target-cluster \
  --servers 1 \
  --agents 2 \
  --network k3d-shared-net
```

그리고 외부 호스트 역할을 할 두 번째 클러스터를 만든다.

```bash
k3d cluster create outside-cluster \
  --servers 1 \
  --agents 1 \
  --network k3d-shared-net
```

이렇게 하면 두 클러스터의 Node 컨테이너들이 같은 Docker network에 붙는다.

구조는 이렇게 된다.

```text
k3d-shared-net
 |
 +-- target-cluster-server-0
 +-- target-cluster-agent-0
 +-- target-cluster-agent-1
 |
 +-- outside-cluster-server-0
 +-- outside-cluster-agent-0
```

이제 `outside-cluster` 쪽에서 `target-cluster`의 Node IP에 접근할 가능성이 생긴다.

---

## 6. target-cluster에 nginx NodePort 만들기

먼저 context를 target-cluster로 바꾼다.

```bash
kubectl config use-context k3d-target-cluster
```

nginx Deployment를 만든다.

```bash
kubectl create deployment nginx-deployment \
  --image=nginx \
  --replicas=3
```

NodePort Service를 만든다.

```bash
kubectl expose deployment nginx-deployment \
  --name nginx-svc \
  --type NodePort \
  --port 80 \
  --target-port 80
```

Service를 확인한다.

```bash
kubectl get svc nginx-svc
```

예를 들어 이렇게 나올 수 있다.

```text
NAME        TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)
nginx-svc   NodePort   10.43.188.207   <none>        80:30001/TCP
```

만약 NodePort를 꼭 `30001`로 고정하고 싶다면 YAML에서 직접 지정해야 한다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-svc
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30001
```

적용한다.

```bash
kubectl apply -f nginx-svc.yaml
```

---

## 7. target-cluster의 Node IP 확인하기

target-cluster에서 Node IP를 확인한다.

```bash
kubectl get nodes -o wide
```

예를 들어 이런 식으로 나온다고 하자.

```text
NAME                            INTERNAL-IP
k3d-target-cluster-server-0      172.20.0.3
k3d-target-cluster-agent-0       172.20.0.4
k3d-target-cluster-agent-1       172.20.0.5
```

그러면 target-cluster의 NodePort 접근 주소는 다음과 같다.

```bash
curl http://172.20.0.3:30001
curl http://172.20.0.4:30001
curl http://172.20.0.5:30001
```

단, 이걸 Mac에서 바로 치는 게 아니라, 이번 실험에서는 outside-cluster 안에서 쳐볼 것이다.

---

## 8. outside-cluster에서 target-cluster로 접근하기

context를 outside-cluster로 바꾼다.

```bash
kubectl config use-context k3d-outside-cluster
```

curl 테스트용 Pod를 띄운다.

```bash
kubectl run curl-test \
  --image=curlimages/curl \
  -it \
  --rm \
  -- sh
```

이제 나는 `outside-cluster` 안의 Pod에 들어간 상태다.

여기서 target-cluster의 Node IP와 NodePort로 접근해본다.

```bash
curl http://172.20.0.3:30001
```

또는 다른 Node IP로도 시도한다.

```bash
curl http://172.20.0.4:30001
curl http://172.20.0.5:30001
```

성공하면 nginx 응답이 나온다.

```text
Welcome to nginx!
```

이 실험이 성공했다면 이런 구조가 된 것이다.

```text
outside-cluster의 curl-test Pod
        ↓
target-cluster NodeIP:30001
        ↓
target-cluster NodePort Service
        ↓
target-cluster nginx Pod
```

---

## 9. 이 실험에서 중요한 포인트

이 실험은 “Kubernetes 클러스터끼리 원래 자동으로 통신한다”는 뜻이 아니다.

중요한 건 Kubernetes가 아니라 네트워크다.

```text
두 클러스터가 같은 Docker network에 붙어 있다
        ↓
outside-cluster에서 target-cluster의 Node IP로 라우팅 가능
        ↓
NodeIP:NodePort 접근 가능
```

즉, 외부 클러스터를 만들었기 때문에 되는 게 아니라, 두 클러스터를 같은 네트워크에 붙였기 때문에 가능한 것이다.

반대로 두 k3d 클러스터가 서로 다른 Docker network에 있으면 접근이 안 될 수 있다.

```text
target-cluster network
outside-cluster network

서로 분리됨
→ Node IP 접근 실패 가능
```

---

## 10. AWS/VM 환경과 비교하기

AWS나 일반 VM 환경에서는 조금 다르다.

AWS에서 Kubernetes Node는 실제 EC2 인스턴스다.

```text
외부 브라우저
        ↓
worker node external-ip:30001
        ↓
NodePort Service
        ↓
Pod
```

이때는 Docker 포트 매핑이 아니라 AWS 보안그룹을 열어야 한다.

```text
Inbound Rule
Protocol: TCP
Port: 30001
Source: 내 IP 또는 필요한 대역
```

즉 환경별 차이는 이렇게 정리할 수 있다.

| 환경                | Node의 정체    | 외부 접근 방식                 | 필요한 작업                              |
| ----------------- | ----------- | ------------------------ | ----------------------------------- |
| AWS/VM Kubernetes | 실제 VM/EC2   | `Node External IP:30001` | 방화벽/보안그룹 30001 오픈                   |
| k3d 단일 클러스터       | Docker 컨테이너 | `localhost:30001`        | `--port "30001:30001@loadbalancer"` |
| k3d 클러스터 2개       | Docker 컨테이너 | 다른 클러스터에서 `NodeIP:30001` | 두 클러스터를 같은 Docker network에 연결       |

---

## 11. k3d 포트 매핑과 같은 네트워크 연결의 차이

k3d 포트 매핑은 host에서 클러스터 안으로 들어가기 위한 방법이다.

```bash
--port "30001:30001@loadbalancer"
```

구조는 다음과 같다.

```text
Mac localhost:30001
        ↓
k3d loadbalancer:30001
        ↓
NodePort Service
```

반면 같은 Docker network로 묶는 것은 두 k3d 클러스터가 서로의 컨테이너 IP로 접근할 수 있게 만드는 것이다.

```bash
--network k3d-shared-net
```

구조는 다음과 같다.

```text
outside-cluster Pod
        ↓
target-cluster NodeIP:30001
        ↓
target-cluster NodePort Service
```

둘 다 “접근 가능하게 만든다”는 점은 비슷하지만, 목적이 다르다.

```text
k3d --port
= Mac host에서 k3d 클러스터로 들어가기

k3d --network
= 여러 k3d 클러스터를 같은 Docker network에 붙이기
```

---

## 12. 실험 순서 전체 정리

전체 실험 흐름은 다음과 같다.

```bash
docker network create k3d-shared-net
```

```bash
k3d cluster create target-cluster \
  --servers 1 \
  --agents 2 \
  --network k3d-shared-net
```

```bash
k3d cluster create outside-cluster \
  --servers 1 \
  --agents 1 \
  --network k3d-shared-net
```

target-cluster에 nginx 배포:

```bash
kubectl config use-context k3d-target-cluster
```

```bash
kubectl create deployment nginx-deployment \
  --image=nginx \
  --replicas=3
```

```bash
kubectl expose deployment nginx-deployment \
  --name nginx-svc \
  --type NodePort \
  --port 80 \
  --target-port 80
```

Service 확인:

```bash
kubectl get svc nginx-svc
```

Node IP 확인:

```bash
kubectl get nodes -o wide
```

outside-cluster로 이동:

```bash
kubectl config use-context k3d-outside-cluster
```

curl-test Pod 실행:

```bash
kubectl run curl-test \
  --image=curlimages/curl \
  -it \
  --rm \
  -- sh
```

target-cluster NodePort로 접근:

```bash
curl http://<target-cluster-node-ip>:30001
```

---

## 13. 정리

k3d에서 NodePort 접근이 헷갈리는 이유는 k3d의 Node가 실제 VM이 아니라 Docker 컨테이너이기 때문이다.

그래서 Mac에서 k3d Node IP로 바로 접근하려고 하면 안 될 수 있다.

이때 방법은 두 가지다.

첫 번째는 k3d 포트 매핑이다.

```bash
--port "30001:30001@loadbalancer"
```

이 방식은 Mac host에서 `localhost:30001`로 클러스터 안의 NodePort에 접근하기 위한 방법이다.

두 번째는 두 k3d 클러스터를 같은 Docker network에 붙이는 것이다.

```bash
--network k3d-shared-net
```

이 방식은 한 k3d 클러스터 안의 Pod에서 다른 k3d 클러스터의 Node IP로 접근하는 실험을 가능하게 해준다.

한 문장으로 정리하면 다음과 같다.

```text
k3d에서 NodePort 접근의 핵심은 Kubernetes 자체보다 Docker 네트워크 구조이고, 두 클러스터가 같은 Docker network에 붙어 있으면 한 클러스터에서 다른 클러스터의 NodeIP:NodePort로 접근하는 실험을 할 수 있다.
```
