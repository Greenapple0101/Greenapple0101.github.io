---
title: "[Kubernetes] nodeSelector란? Pod를 원하는 노드에 배치하는 가장 단순한 방법"
source: "https://velog.io/@yorange50/Kubernetes-nodeSelector란-Pod를-원하는-노드에-배치하는-가장-단순한-방법"
published: "2026-05-29T05:29:26.296Z"
tags: ""
backup_date: "2026-05-29T14:52:52.699694"
---

쿠버네티스를 공부하다 보면 이런 말을 자주 듣는다.

```text
Pod는 Scheduler가 적절한 Node를 골라서 배치한다.
```

처음에는 이렇게 이해하면 된다.

```text
Pod 생성 요청
   ↓
Scheduler가 Node 선택
   ↓
선택된 Node에서 Pod 실행
```

그런데 여기서 질문이 생긴다.

```text
특정 Pod를 특정 Node에만 띄우고 싶으면 어떻게 하지?
GPU가 있는 노드에만 AI Pod를 띄우고 싶으면?
SSD가 있는 노드에만 DB Pod를 띄우고 싶으면?
운영용 Pod는 운영 노드에만 배치하고 싶으면?
```

이때 가장 단순하게 사용할 수 있는 방법이 바로 **nodeSelector**다.

---

## 1. nodeSelector를 한 줄로 말하면

nodeSelector는 Pod를 특정 라벨이 붙은 Node에만 배치하도록 지정하는 설정이다.

쉽게 말하면 이렇다.

```text
nodeSelector
= 이 Pod는 이런 라벨을 가진 Node에만 띄워줘
```

예를 들어 Node에 이런 라벨이 있다고 하자.

```text
disktype=ssd
```

그러면 Pod YAML에 이렇게 쓸 수 있다.

```yaml
nodeSelector:
  disktype: ssd
```

이 뜻은 이렇다.

```text
이 Pod는 disktype=ssd 라벨이 붙은 Node에만 배치해라.
```

즉 nodeSelector는 Pod가 아무 Node에나 뜨지 않도록 조건을 거는 방법이다.

---

## 2. 기본 Pod 배치는 어떻게 될까?

쿠버네티스에서 Pod를 만들면 Scheduler가 Node를 선택한다.

예를 들어 클러스터에 Node가 3개 있다고 하자.

```text
node-1
node-2
node-3
```

그리고 Pod를 하나 만든다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
    - name: nginx
      image: nginx
```

그러면 Scheduler가 여러 조건을 보고 적절한 Node를 고른다.

```text
Node에 자원이 충분한가?
taint 때문에 배치가 막히지는 않는가?
Pod가 요구하는 조건을 만족하는가?
```

조건이 맞는 Node 중 하나에 Pod가 배치된다.

```text
nginx Pod → node-2
```

그런데 사용자가 “이 Pod는 꼭 node-1에 띄우고 싶다”거나 “SSD Node에만 띄우고 싶다”고 하면 추가 조건이 필요하다.

그때 쓰는 게 nodeSelector다.

---

## 3. Node에 라벨 붙이기

nodeSelector는 Node의 label을 기준으로 동작한다.

그래서 먼저 Node에 라벨이 있어야 한다.

Node 목록을 확인한다.

```bash
kubectl get nodes
```

예를 들어 이런 Node들이 있다고 하자.

```text
worker-1
worker-2
worker-3
```

`worker-1`에 SSD 라벨을 붙이고 싶다면 이렇게 한다.

```bash
kubectl label node worker-1 disktype=ssd
```

확인한다.

```bash
kubectl get nodes --show-labels
```

또는 특정 라벨만 보고 싶다면 이렇게 볼 수도 있다.

```bash
kubectl get nodes -L disktype
```

출력 예시는 이런 식이다.

```text
NAME       STATUS   ROLES    AGE   VERSION   DISKTYPE
worker-1   Ready    <none>   10d   v1.29.0   ssd
worker-2   Ready    <none>   10d   v1.29.0
worker-3   Ready    <none>   10d   v1.29.0
```

이제 `worker-1`에는 `disktype=ssd` 라벨이 붙었다.

---

## 4. nodeSelector 사용 예시

이제 Pod에 nodeSelector를 설정해보자.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-ssd
spec:
  nodeSelector:
    disktype: ssd
  containers:
    - name: nginx
      image: nginx
```

핵심은 이 부분이다.

```yaml
nodeSelector:
  disktype: ssd
```

이 Pod는 `disktype=ssd` 라벨이 붙은 Node에만 배치된다.

즉 방금 라벨을 붙인 `worker-1`에 뜰 수 있다.

적용한다.

```bash
kubectl apply -f nginx-ssd.yaml
```

Pod가 어느 Node에 떴는지 확인한다.

```bash
kubectl get pod -o wide
```

예시:

```text
NAME        READY   STATUS    NODE
nginx-ssd   1/1     Running   worker-1
```

`NODE` 컬럼을 보면 `worker-1`에 배치된 것을 확인할 수 있다.

---

## 5. 라벨이 맞는 Node가 없으면 어떻게 될까?

중요한 점이 있다.

nodeSelector 조건을 만족하는 Node가 없으면 Pod는 실행되지 않는다.

예를 들어 Pod에 이렇게 썼다고 하자.

```yaml
nodeSelector:
  gpu: "true"
```

그런데 클러스터에 `gpu=true` 라벨이 붙은 Node가 하나도 없다.

그러면 Pod는 Pending 상태에 머무른다.

```bash
kubectl get pod
```

```text
NAME       READY   STATUS    RESTARTS
gpu-pod    0/1     Pending   0
```

상세 정보를 보면 원인을 확인할 수 있다.

```bash
kubectl describe pod gpu-pod
```

이런 메시지가 나올 수 있다.

```text
0/3 nodes are available: 3 node(s) didn't match Pod's node affinity/selector.
```

뜻은 이렇다.

```text
Pod가 요구한 nodeSelector 조건을 만족하는 Node가 없다.
그래서 Scheduler가 배치할 수 없다.
```

즉 nodeSelector는 단순하지만 강한 조건이다.

조건이 안 맞으면 그냥 안 뜬다.

---

## 6. nodeSelector는 언제 쓸까?

nodeSelector는 특정 Pod를 특정 종류의 Node에만 배치하고 싶을 때 사용한다.

대표적인 예시는 다음과 같다.

```text
GPU가 있는 Node에만 AI/ML 작업 배치
SSD가 있는 Node에만 DB Pod 배치
특정 zone의 Node에만 Pod 배치
운영용 Pod는 production Node에만 배치
테스트용 Pod는 dev Node에만 배치
특정 하드웨어가 있는 Node에만 배치
```

예를 들어 GPU Node에는 이런 라벨을 붙일 수 있다.

```bash
kubectl label node gpu-worker accelerator=nvidia
```

그리고 AI Pod에는 이렇게 설정한다.

```yaml
nodeSelector:
  accelerator: nvidia
```

그러면 해당 Pod는 GPU 라벨이 붙은 Node에만 배치된다.

---

## 7. 예시: 운영 노드와 개발 노드 나누기

클러스터에 운영용 Node와 개발용 Node가 있다고 하자.

```text
worker-prod-1
worker-prod-2
worker-dev-1
```

운영 Node에는 이런 라벨을 붙인다.

```bash
kubectl label node worker-prod-1 env=prod
kubectl label node worker-prod-2 env=prod
```

개발 Node에는 이런 라벨을 붙인다.

```bash
kubectl label node worker-dev-1 env=dev
```

운영용 애플리케이션 Pod에는 이렇게 쓴다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: prod-app
spec:
  nodeSelector:
    env: prod
  containers:
    - name: app
      image: nginx
```

그러면 이 Pod는 `env=prod` 라벨이 붙은 Node에만 배치된다.

```text
worker-prod-1 또는 worker-prod-2에만 배치 가능
worker-dev-1에는 배치 불가
```

---

## 8. nodeSelector는 Deployment에도 쓸 수 있다

nodeSelector는 Pod spec에 들어가는 설정이다.

그래서 단일 Pod뿐만 아니라 Deployment에도 사용할 수 있다.

Deployment에서는 `template.spec` 아래에 넣는다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-ssd-deploy
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx-ssd
  template:
    metadata:
      labels:
        app: nginx-ssd
    spec:
      nodeSelector:
        disktype: ssd
      containers:
        - name: nginx
          image: nginx
```

핵심 위치는 여기다.

```yaml
spec:
  template:
    spec:
      nodeSelector:
        disktype: ssd
```

Deployment 자체의 `spec` 바로 아래가 아니다.

Pod template 안의 `spec` 아래에 들어간다.

왜냐하면 실제로 Node에 배치되는 것은 Deployment가 아니라 Deployment가 만드는 Pod이기 때문이다.

---

## 9. nodeSelector와 label의 관계

nodeSelector는 Node label을 기준으로 동작한다.

여기서 Pod label과 헷갈리면 안 된다.

```text
Pod label
= Service가 Pod를 찾을 때 자주 사용

Node label
= Scheduler가 Pod를 어느 Node에 배치할지 결정할 때 사용
```

예를 들어 Service selector는 Pod label을 본다.

```yaml
selector:
  app: nginx
```

이건 `app=nginx` 라벨을 가진 Pod를 찾는 것이다.

반면 nodeSelector는 Node label을 본다.

```yaml
nodeSelector:
  disktype: ssd
```

이건 `disktype=ssd` 라벨을 가진 Node를 찾는 것이다.

정리하면 이렇다.

```text
Service selector
→ Pod label을 본다.

nodeSelector
→ Node label을 본다.
```

이 차이가 중요하다.

---

## 10. nodeSelector의 한계

nodeSelector는 단순하고 이해하기 쉽다.

하지만 그만큼 표현력이 제한적이다.

예를 들어 nodeSelector는 기본적으로 이런 조건만 표현한다.

```text
이 라벨이 정확히 있어야 한다.
```

예시:

```yaml
nodeSelector:
  disktype: ssd
  env: prod
```

이 경우 뜻은 이렇다.

```text
disktype=ssd 이면서
env=prod 인 Node에만 배치
```

즉 AND 조건이다.

하지만 이런 복잡한 조건은 표현하기 어렵다.

```text
ssd 또는 nvme인 Node에 배치
gpu 라벨이 존재하는 Node에 배치
zone이 a 또는 b인 Node에 배치
특정 Node는 피하고 싶음
가능하면 이 Node에 배치하되, 없으면 다른 Node도 허용
```

이럴 때는 `nodeAffinity`를 사용한다.

---

## 11. nodeSelector와 nodeAffinity 차이

nodeSelector는 가장 단순한 Node 선택 방법이다.

nodeAffinity는 더 복잡하고 유연한 Node 선택 방법이다.

비교하면 이렇다.

| 구분     | nodeSelector | nodeAffinity |
| ------ | ------------ | ------------ |
| 조건 표현  | 단순 key=value | 복잡한 조건 가능    |
| OR 조건  | 어려움          | 가능           |
| 선호 조건  | 불가능          | 가능           |
| 강제 조건  | 가능           | 가능           |
| 사용 난이도 | 쉬움           | 조금 복잡함       |

nodeSelector는 이런 느낌이다.

```text
무조건 disktype=ssd Node에만 띄워.
```

nodeAffinity는 이런 느낌도 가능하다.

```text
반드시 gpu 라벨이 있는 Node에 띄워.
가능하면 zone=a에 띄워.
ssd 또는 nvme Node 중 하나에 띄워.
```

즉 처음 공부할 때는 nodeSelector부터 잡고, 더 복잡한 조건이 필요해지면 nodeAffinity로 넘어가면 된다.

---

## 12. nodeSelector와 taint/toleration 차이

이것도 자주 헷갈린다.

nodeSelector는 Pod가 특정 Node를 **찾아가는 조건**이다.

```text
이 Pod는 env=prod Node에 가고 싶다.
```

반면 taint/toleration은 Node가 특정 Pod를 **막는 조건**이다.

```text
이 Node는 아무 Pod나 못 들어오게 막는다.
허용증을 가진 Pod만 들어올 수 있다.
```

비유하면 이렇다.

```text
nodeSelector
= Pod가 원하는 Node를 고르는 조건

taint/toleration
= Node가 Pod 입장을 제한하는 조건
```

예를 들어 GPU Node에는 일반 Pod가 오면 안 된다고 하자.

이때는 GPU Node에 taint를 걸 수 있다.

```bash
kubectl taint nodes gpu-worker dedicated=gpu:NoSchedule
```

그리고 GPU 작업 Pod에만 toleration을 준다.

즉 정교한 운영에서는 nodeSelector와 taint/toleration을 같이 쓰는 경우가 많다.

```text
nodeSelector
→ GPU Node를 선택

toleration
→ GPU Node의 taint를 통과
```

---

## 13. 확인 명령어 정리

Node 목록 보기

```bash
kubectl get nodes
```

Node label 확인

```bash
kubectl get nodes --show-labels
```

특정 label 컬럼으로 보기

```bash
kubectl get nodes -L disktype
```

Node에 label 추가

```bash
kubectl label node <node-name> disktype=ssd
```

Node label 변경

```bash
kubectl label node <node-name> disktype=hdd --overwrite
```

Node label 삭제

```bash
kubectl label node <node-name> disktype-
```

Pod가 어느 Node에 떴는지 확인

```bash
kubectl get pod -o wide
```

Pod가 Pending일 때 원인 확인

```bash
kubectl describe pod <pod-name>
```

---

## 14. 자주 나는 실수

### 1. Node label이 없는데 nodeSelector를 씀

Pod에는 이렇게 적었다.

```yaml
nodeSelector:
  disktype: ssd
```

그런데 Node에는 `disktype=ssd` 라벨이 없다.

그러면 Pod는 Pending 상태가 된다.

먼저 Node label을 확인해야 한다.

```bash
kubectl get nodes -L disktype
```

---

### 2. Deployment에서 nodeSelector 위치를 잘못 씀

잘못된 예시는 이런 식이다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  nodeSelector:
    disktype: ssd
```

Deployment에서는 이렇게 쓰면 안 된다.

nodeSelector는 Pod spec에 들어가야 한다.

올바른 위치는 여기다.

```yaml
spec:
  template:
    spec:
      nodeSelector:
        disktype: ssd
```

---

### 3. Pod label과 Node label을 헷갈림

Service selector는 Pod label을 본다.

nodeSelector는 Node label을 본다.

이 둘을 섞으면 안 된다.

```text
Service selector
→ Pod 선택

nodeSelector
→ Node 선택
```

---

## 15. 한 번에 정리

nodeSelector는 Pod를 특정 라벨이 붙은 Node에만 배치하기 위한 설정이다.

핵심만 정리하면 이렇다.

```text
Node label
= Node에 붙이는 이름표

nodeSelector
= 특정 Node label을 가진 Node에만 Pod를 배치하는 조건

Scheduler
= nodeSelector 조건을 만족하는 Node 중에서 Pod를 배치

조건 만족 Node 없음
= Pod Pending
```

사용 흐름은 이렇게 보면 된다.

```text
1. Node에 label을 붙인다.
2. Pod spec에 nodeSelector를 적는다.
3. Scheduler가 해당 label을 가진 Node를 찾는다.
4. 조건을 만족하는 Node에 Pod를 배치한다.
```

예시로 기억하면 쉽다.

```bash
kubectl label node worker-1 disktype=ssd
```

```yaml
nodeSelector:
  disktype: ssd
```

이 말은 결국 이 뜻이다.

```text
이 Pod는 disktype=ssd 라벨이 붙은 Node에만 띄워라.
```

처음에는 이것만 기억하면 된다.

```text
nodeSelector
= Pod가 갈 수 있는 Node를 label로 제한하는 가장 단순한 방법
```
