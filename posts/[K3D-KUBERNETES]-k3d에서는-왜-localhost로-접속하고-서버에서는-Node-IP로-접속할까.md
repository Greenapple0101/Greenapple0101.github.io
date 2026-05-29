---
title: "[K3D/KUBERNETES] k3d에서는 왜 localhost로 접속하고, 서버에서는 Node IP로 접속할까?"
source: "https://velog.io/@yorange50/K3DKUBERNETES-k3d에서는-왜-localhost로-접속하고-서버에서는-Node-IP로-접속할까"
published: "2026-05-19T06:31:41.100Z"
tags: ""
backup_date: "2026-05-29T14:52:52.722363"
---

Kubernetes Service를 실습하다 보면 접속 주소가 계속 헷갈린다.

어떤 글에서는 이렇게 접속하라고 한다.

```bash
curl http://<Node-IP>:30001
```

그런데 k3d에서는 이렇게 접속하라고 한다.

```bash
curl http://localhost:30001
```

또 LoadBalancer Service를 만들면 어떤 환경에서는 LoadBalancer 주소로 들어가고, k3d에서는 `localhost`로 들어간다.

처음에는 이게 다 섞여서 헷갈린다.

결론부터 말하면 이유는 하나다.

```text
k3d의 Node는 실제 서버가 아니라 Docker 컨테이너이기 때문이다.
```

---

## 1. 실제 서버에서 Kubernetes를 띄우는 경우

먼저 일반적인 Kubernetes 환경을 생각해보자.

예를 들어 AWS EC2나 VM 3대 위에 Kubernetes 클러스터를 만들었다고 하자.

```text
Kubernetes Cluster

master-1  = 실제 서버
worker-1  = 실제 서버
worker-2  = 실제 서버
```

이 경우 각 Node는 진짜 서버다.

그래서 Node마다 실제 네트워크 IP가 있다.

```text
master-1  → 172.26.8.74
worker-1  → 172.26.3.104
worker-2  → 172.26.9.60
```

이 IP들은 외부에서 접근 가능한 서버 IP다.

그래서 NodePort Service를 만들면 외부에서 이렇게 접속할 수 있다.

```bash
curl http://172.26.8.74:30001
curl http://172.26.3.104:30001
curl http://172.26.9.60:30001
```

즉 실제 서버 환경에서는:

```text
NodePort
= Node IP + NodePort로 접속
```

이라고 이해하면 된다.

---

## 2. NodePort는 아무 Node IP로 들어가도 된다

NodePort Service가 이렇게 있다고 하자.

```text
nginx-svc   NodePort   10.43.188.207   80:30001/TCP
```

여기서 `30001`이 NodePort다.

이 말은 다음과 같다.

```text
클러스터의 각 Node에 30001번 포트를 열어두고,
그 포트로 들어온 요청을 nginx-svc Service로 보낸다.
```

그래서 외부에서는 아무 Node IP로 들어가도 된다.

```bash
curl http://master-1-ip:30001
curl http://worker-1-ip:30001
curl http://worker-2-ip:30001
```

중요한 점은, 내가 `worker-1:30001`로 들어갔다고 해서 반드시 worker-1에 있는 Pod로만 가는 게 아니라는 것이다.

요청은 Service를 거쳐 Endpoints에 있는 Pod들 중 하나로 전달된다.

```text
외부 사용자
    ↓
worker-1:30001
    ↓
nginx-svc Service
    ↓
Endpoints에 있는 Pod 중 하나
```

즉 더 정확히 말하면:

```text
아무 Node IP로 들어가도 되고,
Service가 실제 Pod로 보내준다.
```

---

## 3. LoadBalancer는 NodePort 앞에 대표 입구를 둔 느낌

LoadBalancer Service는 NodePort와 완전히 다른 구조라기보다, NodePort 앞에 외부 로드밸런서를 하나 더 둔 것처럼 이해하면 쉽다.

NodePort는 사용자가 직접 Node IP와 포트를 알아야 한다.

```text
사용자
  ↓
NodeIP:30001
  ↓
Service
  ↓
Pod
```

LoadBalancer는 사용자가 Node IP를 몰라도 되게 한다.

```text
사용자
  ↓
LoadBalancer 주소
  ↓
Service
  ↓
Pod
```

AWS EKS 같은 환경에서는 LoadBalancer Service를 만들면 AWS Load Balancer가 생성될 수 있다.

그러면 사용자는 이런 주소로 접속한다.

```text
http://abc.elb.amazonaws.com
```

즉 실제 서버나 클라우드 환경에서는 이렇게 정리할 수 있다.

```text
NodePort
→ Node IP:NodePort로 접속

LoadBalancer
→ LoadBalancer 주소로 접속
```

---

## 4. 그런데 k3d는 다르다

k3d는 Kubernetes Node를 실제 VM이나 EC2로 띄우지 않는다.

k3d는 Docker 컨테이너를 Kubernetes Node처럼 사용한다.

즉 구조가 이렇다.

```text
Mac
  ↓
Docker Desktop
  ↓
k3d server container
k3d agent container
k3d loadbalancer container
```

그래서 `kubectl get nodes -o wide`를 하면 Node IP가 보이긴 한다.

예를 들어:

```text
k3d-my-cluster-server-0   172.19.0.3
k3d-my-cluster-agent-0    172.19.0.4
k3d-my-cluster-agent-1    172.19.0.5
```

하지만 여기서 보이는 `172.19.0.x`는 내 Mac이 직접 접근하는 실제 서버 IP가 아니다.

이 IP는 Docker 내부 네트워크에서 컨테이너가 받은 IP다.

그래서 Mac 터미널에서 바로 이렇게 접근하면 안 될 수 있다.

```bash
curl http://172.19.0.3:30001
```

NodePort 개념이 틀린 게 아니다.

문제는 k3d의 Node IP가 Docker 내부 IP라는 점이다.

---

## 5. 그래서 k3d에서는 포트 매핑을 한다

k3d에서 Mac에서 클러스터 안의 Service로 접속하려면, 클러스터를 만들 때 포트 매핑을 해줘야 한다.

예를 들어 NodePort가 `30001`이라면:

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
Service
        ↓
Pod
```

그래서 Mac에서는 Node IP가 아니라 `localhost`로 접속한다.

```bash
curl http://localhost:30001
```

이게 k3d에서 `localhost`를 쓰는 이유다.

---

## 6. LoadBalancer Service도 k3d에서는 포트 매핑이 필요하다

LoadBalancer Service를 만든다고 해도 k3d가 AWS Load Balancer를 만들어주는 것은 아니다.

k3d는 로컬 Docker 기반 환경이기 때문에, 외부에서 들어오는 통로를 직접 열어줘야 한다.

예를 들어 LoadBalancer Service가 80번 포트를 쓴다면 클러스터를 만들 때 이렇게 한다.

```bash
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "80:80@loadbalancer"
```

이 의미는 다음과 같다.

```text
Mac localhost:80
        ↓
k3d loadbalancer container:80
        ↓
LoadBalancer Service:80
        ↓
Pod:80
```

그러면 Mac에서 이렇게 접속할 수 있다.

```bash
curl http://localhost
```

`80`번 포트는 HTTP 기본 포트라서 뒤에 `:80`을 생략할 수 있다.

즉 아래 둘은 같은 의미다.

```bash
curl http://localhost
curl http://localhost:80
```

---

## 7. 외부 포트를 8080으로 매핑하면 어떻게 될까?

만약 클러스터를 이렇게 만들었다고 하자.

```bash
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "8080:80@loadbalancer"
```

이건 다음 뜻이다.

```text
Mac localhost:8080
        ↓
k3d loadbalancer container:80
        ↓
Service:80
        ↓
Pod:80
```

이 경우 접속은 이렇게 해야 한다.

```bash
curl http://localhost:8080
```

`curl http://localhost`로 하면 안 맞다.

왜냐하면 `http://localhost`는 자동으로 80번 포트로 요청을 보내기 때문이다.

하지만 지금 Mac에서 열어둔 포트는 8080이다.

정리하면:

```text
--port "80:80@loadbalancer"
→ curl http://localhost

--port "8080:80@loadbalancer"
→ curl http://localhost:8080

--port "30001:30001@loadbalancer"
→ curl http://localhost:30001
```

포트 매핑에서 앞쪽 포트가 내가 접속하는 포트다.

---

## 8. k3d와 실제 서버 환경 비교

같은 Kubernetes Service라도 실행 환경에 따라 접속 방식이 다르다.

| 환경          | Service 타입   | 접속 방식                             |
| ----------- | ------------ | --------------------------------- |
| 실제 VM / AWS | NodePort     | `curl http://<Node-IP>:30001`     |
| 실제 VM / AWS | LoadBalancer | `curl http://<LoadBalancer주소>`    |
| k3d         | NodePort     | `curl http://localhost:30001`     |
| k3d         | LoadBalancer | `curl http://localhost` 또는 매핑한 포트 |

즉 핵심은 이거다.

```text
실제 서버에서는 Node IP나 LoadBalancer 주소로 접속한다.
k3d에서는 Docker 내부로 들어가기 위해 localhost 포트 매핑으로 접속한다.
```

---

## 9. 클러스터 내부에서 접속할 때는 또 다르다

지금까지는 Mac이나 외부에서 접속하는 경우를 말했다.

그런데 클러스터 내부의 Pod에서 Service에 접속할 때는 NodePort나 LoadBalancer를 신경 쓸 필요가 거의 없다.

테스트용 curl Pod를 띄운다.

```bash
kubectl run curl-test --image=curlimages/curl -it --rm -- sh
```

그 안에서 Service 이름으로 접근할 수 있다.

```bash
curl http://nginx-svc
```

또는 ClusterIP로 접근할 수도 있다.

```bash
curl http://10.43.188.207
```

이건 클러스터 내부 접근이다.

```text
curl-test Pod
    ↓
nginx-svc
    ↓
Pod
```

Service 타입이 NodePort든 LoadBalancer든, 내부에서는 Service 이름이나 ClusterIP로 접근 가능하다.

---

## 10. 최종 정리

k3d는 Kubernetes Node를 실제 VM으로 띄우는 것이 아니라 Docker 컨테이너로 띄운다.

그래서 k3d 클러스터 안의 Node IP는 Mac이 직접 접근하는 서버 IP가 아니라 Docker 내부 네트워크 IP다.

따라서 Mac에서 k3d 안의 Service로 접속하려면, 클러스터 생성 시점에 포트 매핑을 해두고 `localhost`로 접근한다.

반면 실제 서버나 AWS EC2 위에 Kubernetes를 띄운 경우에는 Node가 진짜 서버다.

그래서 NodePort라면:

```bash
curl http://<Node-IP>:<NodePort>
```

LoadBalancer라면:

```bash
curl http://<LoadBalancer주소>
```

로 접속한다.

한 문장으로 정리하면 다음과 같다.

```text
k3d에서는 노드가 Docker 컨테이너라서 localhost 포트 매핑으로 들어가고, 실제 서버나 AWS에서는 NodePort면 Node IP:Port로, LoadBalancer면 LoadBalancer 주소로 들어간다.
```
