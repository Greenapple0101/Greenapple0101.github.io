---
title: "[KUBERNETES] NodePort는 아무 워커 노드로 들어가도 다른 노드의 Pod에 접속될까?"
source: "https://velog.io/@yorange50/KUBERNETES-NodePort는-아무-워커-노드로-들어가도-다른-노드의-Pod에-접속될까"
published: "2026-05-19T06:25:11.767Z"
tags: ""
backup_date: "2026-05-29T14:52:52.722824"
---

Kubernetes에서 `NodePort` Service를 배우다 보면 이런 의문이 생긴다.

```text
nginx Pod가 worker-1에 떠 있는데,
내가 master-1의 NodePort로 접속하면 될까?

또는 worker-2에 Pod가 없는데,
worker-2의 NodePort로 들어가도 접속될까?
```

결론부터 말하면 **된다.**

NodePort는 특정 Pod가 떠 있는 노드에서만 열리는 포트가 아니다. Kubernetes 클러스터의 각 Node에 같은 포트를 열어두고, 그 포트로 들어온 요청을 Service가 뒤의 Pod들로 전달한다.

---

## 1. 현재 상황 예시

nginx Pod가 3개 떠 있다고 하자.

```bash
kubectl get pod -o wide
```

예시 출력:

```text
NAME                                  IP           NODE
nginx-deployment-7456645bf-4rts6      10.42.0.8    master-1
nginx-deployment-7456645bf-kglgv      10.42.1.8    worker-1
nginx-deployment-7456645bf-lgzv5      10.42.2.7    worker-2
```

그리고 NodePort Service가 있다.

```bash
kubectl get svc nginx-svc
```

예시 출력:

```text
NAME        TYPE       CLUSTER-IP      PORT(S)
nginx-svc   NodePort   10.43.188.207   80:30001/TCP
```

여기서 중요한 부분은 이것이다.

```text
80:30001/TCP
```

의미는 다음과 같다.

```text
Service 내부 포트 = 80
외부에서 들어갈 NodePort = 30001
```

즉 외부에서는 `NodeIP:30001`로 접속할 수 있다.

---

## 2. NodePort는 어느 노드로 들어가도 된다

Node IP가 다음과 같다고 하자.

```text
master-1  = 172.26.8.74
worker-1  = 172.26.3.104
worker-2  = 172.26.9.60
```

그러면 외부에서는 이렇게 접속할 수 있다.

```bash
curl http://172.26.8.74:30001
curl http://172.26.3.104:30001
curl http://172.26.9.60:30001
```

여기서 중요한 점은 **nginx Pod가 어느 노드에 떠 있는지와 상관없이, 아무 Node IP로 들어가도 된다는 것**이다.

예를 들어 요청을 `master-1:30001`로 보냈다고 하자.

```text
외부 사용자
    ↓
master-1:30001
```

그런데 실제 nginx Pod가 worker-2에 있을 수도 있다.

그래도 Kubernetes는 요청을 Service 뒤의 Pod로 전달할 수 있다.

```text
외부 사용자
    ↓
master-1:30001
    ↓
nginx-svc Service
    ↓
worker-2에 있는 nginx Pod
```

즉, 내가 접속한 노드와 실제 Pod가 떠 있는 노드가 달라도 된다.

---

## 3. 왜 아무 노드로 들어가도 될까?

NodePort Service를 만들면 Kubernetes는 각 Node에 같은 포트를 열어둔다.

예를 들어 NodePort가 `30001`이면, 클러스터의 모든 Node에 `30001`번 포트가 열린다.

```text
master-1:30001
worker-1:30001
worker-2:30001
```

외부 요청은 이 중 아무 곳으로 들어갈 수 있다.

```text
외부 사용자
    ↓
worker-1:30001
```

그러면 Kubernetes는 이 요청을 Service로 연결하고, Service는 Endpoints에 등록된 Pod들 중 하나로 요청을 보낸다.

```text
worker-1:30001
    ↓
nginx-svc
    ↓
10.42.0.8:80
10.42.1.8:80
10.42.2.7:80
```

즉 NodePort는 단순히 “그 노드 안의 Pod로만 보내는 포트”가 아니다.

```text
NodePort = 각 Node에 열린 외부 입구
Service = 그 입구로 들어온 요청을 Pod로 보내는 중간 관리자
```

---

## 4. Endpoints를 보면 실제 목적지를 알 수 있다

Service가 실제로 어떤 Pod들을 바라보고 있는지는 Endpoints에서 확인할 수 있다.

```bash
kubectl get endpoints nginx-svc
```

또는:

```bash
kubectl describe svc nginx-svc
```

예시:

```text
Endpoints: 10.42.1.8:80,10.42.2.7:80,10.42.0.8:80
```

이 뜻은 다음과 같다.

```text
nginx-svc Service가
10.42.1.8:80
10.42.2.7:80
10.42.0.8:80

이 세 개의 Pod를 목적지로 알고 있다
```

따라서 외부에서 어느 Node의 `30001`로 들어오든, 최종적으로는 이 Endpoints 중 하나로 요청이 전달된다.

---

## 5. 그림으로 이해하기

예를 들어 외부에서 `worker-1:30001`로 접속했다고 하자.

```text
외부 사용자
    ↓
worker-1:30001
    ↓
NodePort Service
    ↓
nginx-svc
    ↓
Pod 1 / Pod 2 / Pod 3
```

이번에는 `master-1:30001`로 접속했다고 하자.

```text
외부 사용자
    ↓
master-1:30001
    ↓
NodePort Service
    ↓
nginx-svc
    ↓
Pod 1 / Pod 2 / Pod 3
```

이번에는 `worker-2:30001`로 접속했다고 하자.

```text
외부 사용자
    ↓
worker-2:30001
    ↓
NodePort Service
    ↓
nginx-svc
    ↓
Pod 1 / Pod 2 / Pod 3
```

들어가는 Node는 달라도, 최종적으로는 같은 Service를 거쳐 Pod들로 전달된다.

---

## 6. 그러면 worker-2에 Pod가 없어도 될까?

된다.

예를 들어 nginx Pod가 worker-1에만 떠 있다고 해보자.

```text
master-1  → nginx Pod 없음
worker-1  → nginx Pod 있음
worker-2  → nginx Pod 없음
```

그래도 외부에서 이렇게 접속할 수 있다.

```bash
curl http://master-1-ip:30001
curl http://worker-2-ip:30001
```

왜냐하면 NodePort는 모든 Node에 열린 입구이고, 요청을 받은 Node가 Service를 통해 실제 Pod가 있는 노드로 전달할 수 있기 때문이다.

즉 구조는 이렇게 된다.

```text
외부 사용자
    ↓
worker-2:30001
    ↓
nginx-svc
    ↓
worker-1에 있는 nginx Pod
```

그래서 “그 노드에 Pod가 있어야만 접속된다”가 아니다.

---

## 7. 단, 조건이 있다

아무 Node로 들어가도 된다고 했지만, 조건이 있다.

첫 번째, Service의 Endpoints가 정상이어야 한다.

```bash
kubectl get endpoints nginx-svc
```

여기서 Pod IP가 보여야 한다.

```text
nginx-svc   10.42.0.8:80,10.42.1.8:80,10.42.2.7:80
```

만약 이렇게 나오면 문제다.

```text
nginx-svc   <none>
```

이 경우 Service가 Pod를 못 찾고 있는 것이다. 보통 Service의 `selector`와 Pod의 `label`이 안 맞을 때 발생한다.

두 번째, 외부에서 Node IP에 접근 가능해야 한다.

일반 VM이나 AWS 환경에서는 방화벽이나 보안그룹에서 NodePort 포트를 열어야 한다.

```text
TCP 30001 허용
```

AWS라면 보안그룹 인바운드 규칙에서 `30001`을 열어야 외부 브라우저나 curl로 접근할 수 있다.

세 번째, k3d 환경에서는 Node IP로 바로 접근이 안 될 수 있다.

k3d의 Node는 실제 VM이 아니라 Docker 컨테이너다. 그래서 Mac에서 `172.19.x.x:30001` 같은 Node IP로 바로 접근이 안 될 수 있다.

이 경우 클러스터 생성 시 포트 매핑이 필요하다.

```bash
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "30001:30001@loadbalancer"
```

그러면 Mac에서는 이렇게 접속한다.

```bash
curl http://localhost:30001
```

---

## 8. NodePort와 로드밸런싱

NodePort로 들어온 요청도 결국 Service를 거친다.

Service는 Endpoints에 등록된 Pod들 중 하나로 요청을 보낸다.

```text
NodeIP:30001
    ↓
Service
    ↓
Pod 1 / Pod 2 / Pod 3
```

그래서 여러 번 curl을 날리면 서로 다른 Pod의 응답을 받을 수 있다.

예를 들어 각 Pod의 응답을 다르게 설정해두었다고 하자.

```text
Pod 1 → nginx-1
Pod 2 → nginx-2
Pod 3 → nginx-3
```

그다음 NodePort로 여러 번 요청한다.

```bash
curl http://172.26.8.74:30001
curl http://172.26.8.74:30001
curl http://172.26.8.74:30001
```

응답이 이렇게 바뀔 수 있다.

```text
nginx-2
nginx-1
nginx-3
```

이것은 NodePort로 들어온 요청이 Service 뒤의 Pod들로 분산되고 있다는 뜻이다.

---

## 9. 한 번에 정리

NodePort Service가 있으면 외부에서는 이렇게 접속한다.

```bash
curl http://<Node-IP>:<NodePort>
```

예를 들어:

```bash
curl http://172.26.8.74:30001
curl http://172.26.3.104:30001
curl http://172.26.9.60:30001
```

이때 중요한 점은 이것이다.

```text
아무 Node IP로 들어가도 된다.
그 Node에 Pod가 꼭 떠 있어야 하는 것은 아니다.
```

왜냐하면 NodePort는 모든 Node에 같은 포트를 열고, 들어온 요청을 Service를 통해 Endpoints의 Pod들로 전달하기 때문이다.

---

## 10. 결론

NodePort는 특정 Pod가 떠 있는 Node에만 접속하는 방식이 아니다.

NodePort는 Kubernetes 클러스터의 각 Node에 동일한 포트를 열어두고, 어느 Node로 들어온 요청이든 Service를 통해 실제 Pod로 전달한다.

그래서 `master-1:30001`, `worker-1:30001`, `worker-2:30001` 중 어디로 들어가도 Service 뒤의 Pod에 접근할 수 있다.

단, 네트워크와 방화벽이 허용되어 있어야 한다.

한 문장으로 정리하면 다음과 같다.

```text
NodePort는 모든 Node에 같은 외부 포트를 열어두기 때문에, 아무 NodeIP:NodePort로 접속해도 Service가 Endpoints에 있는 Pod들 중 하나로 요청을 전달한다.
```
