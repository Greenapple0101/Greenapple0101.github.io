---
title: "[Kubernetes] Daemon이란? DaemonSet을 이해하기 전에 알아야 할 기본 개념"
source: "https://velog.io/@yorange50/Kubernetes-Daemon이란-DaemonSet을-이해하기-전에-알아야-할-기본-개념"
published: "2026-05-28T23:57:43.670Z"
tags: ""
backup_date: "2026-05-29T14:52:52.703694"
---


쿠버네티스에서 `DaemonSet`을 공부하다 보면 자연스럽게 이런 질문이 생긴다.

```text
Daemon이 뭐야?
왜 이름이 DaemonSet이야?
Deployment랑 뭐가 다른데?
```

`DaemonSet`을 이해하려면 먼저 **Daemon**이라는 개념부터 잡고 가는 게 좋다.

---

## 1. Daemon이란?

Daemon은 백그라운드에서 계속 실행되는 프로그램이다.

일반 프로그램은 사용자가 직접 실행하고, 필요 없으면 직접 종료한다.

하지만 Daemon은 시스템 뒤쪽에서 조용히 떠 있으면서 특정 일을 계속 처리한다.

쉽게 말하면 이런 느낌이다.

```text
Daemon
= 시스템 뒤에서 계속 실행되는 백그라운드 프로그램
= 사용자가 직접 조작하지 않아도 계속 동작하는 프로그램
= 특정 요청이나 상태 변화를 기다리는 프로그램
```

대표적인 예시는 다음과 같다.

```text
sshd
→ SSH 접속을 받아주는 데몬

dockerd
→ Docker 명령을 실제로 처리하는 Docker 데몬

kubelet
→ 각 노드에서 Pod를 관리하는 쿠버네티스 데몬

containerd
→ 컨테이너 실행을 담당하는 런타임 데몬
```

즉 Daemon은 겉으로는 잘 안 보이지만, 시스템이 정상적으로 동작하도록 뒤에서 계속 일하는 프로그램이다.

---

## 2. 일반 프로그램과 Daemon의 차이

우리가 직접 실행하는 일반 프로그램은 보통 이런 느낌이다.

```bash
python app.py
```

내가 실행하고, 필요 없으면 직접 끈다.

```text
Ctrl + C
```

반면 Daemon은 보통 시스템이 켜질 때 자동으로 실행되고, 계속 살아 있다.

예를 들어 SSH 데몬을 생각해보자.

```bash
systemctl status ssh
```

SSH 데몬이 떠 있기 때문에 우리는 서버에 접속할 수 있다.

```bash
ssh ubuntu@1.2.3.4
```

만약 SSH 데몬이 꺼져 있다면 어떻게 될까?

서버 자체는 살아 있어도 SSH 접속이 안 된다.

```text
서버는 켜져 있음
하지만 sshd가 죽어 있음
↓
SSH 접속 불가
```

즉 Daemon은 시스템의 기능을 유지하는 뒤쪽 관리자에 가깝다.

---

## 3. Daemon은 왜 계속 떠 있어야 할까?

Daemon은 보통 **언제 요청이 올지 모르는 일**을 처리한다.

예를 들어 `sshd`는 누가 언제 SSH로 접속할지 모른다.

그래서 항상 켜져 있어야 한다.

```text
사용자: SSH 접속 요청
sshd: 기다리고 있다가 요청을 받음
```

Docker도 비슷하다.

우리가 이런 명령어를 입력한다고 하자.

```bash
docker ps
docker run nginx
```

겉으로 보면 `docker` 명령어가 일하는 것처럼 보인다.

하지만 실제 컨테이너 생성과 관리는 뒤에서 떠 있는 `dockerd`가 처리한다.

```text
docker CLI
   ↓
dockerd
   ↓
containerd
   ↓
컨테이너 실행
```

그래서 Docker 데몬이 죽어 있으면 이런 에러가 날 수 있다.

```text
Cannot connect to the Docker daemon
```

이 말은 결국 이 뜻이다.

```text
Docker 명령을 처리해줄 데몬이 실행 중이 아니다.
```

---

## 4. 쿠버네티스에서 자주 보는 Daemon

쿠버네티스 노드에도 여러 Daemon이 돌아간다.

대표적으로 `kubelet`, `containerd`, `kube-proxy`가 있다.

---

## 5. kubelet

`kubelet`은 각 노드에서 실행되는 데몬이다.

역할은 간단히 말하면 이렇다.

```text
이 노드에서 어떤 Pod를 실행해야 하는지 확인
컨테이너 런타임에게 Pod 실행 요청
Pod 상태를 API Server에 보고
죽은 Pod가 있으면 다시 맞춰줌
```

즉 `kubelet`은 노드의 현장 관리자 같은 존재다.

API Server가 “이 노드에 Pod를 띄워야 한다”고 알려주면, kubelet이 해당 노드에서 실제 실행을 챙긴다.

```text
API Server
   ↓
kubelet
   ↓
container runtime
   ↓
Pod 실행
```

kubelet이 없으면 노드는 쿠버네티스 클러스터의 일원으로 제대로 동작할 수 없다.

---

## 6. containerd

`containerd`는 컨테이너 실행을 담당하는 데몬이다.

쿠버네티스가 직접 컨테이너를 실행하는 것은 아니다.

흐름은 대략 이렇다.

```text
API Server
   ↓
kubelet
   ↓
containerd
   ↓
컨테이너 실행
```

`kubelet`은 “이 Pod를 실행해줘”라고 요청하고, `containerd`는 실제로 컨테이너를 실행한다.

즉 kubelet은 노드의 관리자, containerd는 컨테이너 실행 담당자라고 볼 수 있다.

---

## 7. kube-proxy

`kube-proxy`도 각 노드에서 동작하는 네트워크 관련 데몬이다.

Service로 들어온 트래픽이 실제 Pod로 갈 수 있도록 네트워크 규칙을 관리한다.

```text
Service IP로 요청
   ↓
kube-proxy가 만든 iptables/IPVS 규칙
   ↓
실제 Pod IP로 전달
```

쿠버네티스에서 Service를 통해 Pod에 접근할 수 있는 것도 이런 네트워크 규칙 덕분이다.

---

## 8. 그래서 DaemonSet이란?

이제 `DaemonSet`이라는 이름이 조금 이해된다.

DaemonSet은 특정 Pod를 **모든 노드 또는 일부 노드에 하나씩 실행시키기 위한 쿠버네티스 리소스**다.

즉 이런 상황에서 쓴다.

```text
각 노드마다 항상 떠 있어야 하는 Pod가 필요할 때
```

예를 들어 노드가 3개 있다고 하자.

```text
Node A
Node B
Node C
```

각 노드마다 로그 수집 Pod를 하나씩 띄우고 싶다면 DaemonSet을 쓴다.

```text
Node A → 로그 수집 Pod 1개
Node B → 로그 수집 Pod 1개
Node C → 로그 수집 Pod 1개
```

Deployment는 보통 “Pod를 몇 개 유지할 것인가”가 기준이다.

```text
Deployment replicas: 3
→ 클러스터 어딘가에 Pod 3개
```

반면 DaemonSet은 “노드마다 하나씩 띄울 것인가”가 기준이다.

```text
DaemonSet
→ 노드마다 Pod 1개씩
```

---

## 9. DaemonSet을 쓰는 대표적인 경우

DaemonSet은 보통 노드 단위로 뭔가를 해야 할 때 사용한다.

대표적인 예시는 다음과 같다.

```text
로그 수집기
모니터링 에이전트
네트워크 플러그인
스토리지 에이전트
보안 에이전트
```

예를 들어 Fluent Bit 같은 로그 수집기는 각 노드에 떠 있어야 한다.

왜냐하면 각 노드마다 여러 Pod의 로그가 생기기 때문이다.

```text
Node A의 로그 → Node A의 Fluent Bit가 수집
Node B의 로그 → Node B의 Fluent Bit가 수집
Node C의 로그 → Node C의 Fluent Bit가 수집
```

Prometheus Node Exporter도 비슷하다.

노드의 CPU, 메모리, 디스크 같은 정보를 수집하려면 각 노드마다 하나씩 떠 있어야 한다.

```text
Node A의 자원 사용량 → Node A의 Node Exporter가 수집
Node B의 자원 사용량 → Node B의 Node Exporter가 수집
Node C의 자원 사용량 → Node C의 Node Exporter가 수집
```

그래서 이런 종류의 에이전트는 DaemonSet으로 배포하는 경우가 많다.

---

## 10. Deployment와 DaemonSet 차이

가장 중요한 차이는 기준이다.

| 구분      | Deployment      | DaemonSet         |
| ------- | --------------- | ----------------- |
| 기준      | Pod 개수          | Node 개수           |
| 목적      | 애플리케이션 복제       | 노드별 에이전트 실행       |
| 예시      | 웹 서버, API 서버    | 로그 수집기, 모니터링 에이전트 |
| 배치 방식   | 클러스터 어딘가에 N개    | 각 노드마다 1개         |
| 노드 추가 시 | replicas에 따라 유지 | 새 노드에도 자동 생성      |

예를 들어 노드가 3개일 때 Deployment replicas가 2라면 이렇게 될 수 있다.

```text
Node A → web Pod
Node B → web Pod
Node C → 없음
```

하지만 DaemonSet이라면 이렇게 된다.

```text
Node A → agent Pod
Node B → agent Pod
Node C → agent Pod
```

노드가 하나 더 추가되면 DaemonSet은 새 노드에도 자동으로 Pod를 만든다.

```text
Node D → agent Pod 자동 생성
```

즉 DaemonSet은 노드 수에 맞춰 움직인다.

---

## 11. DaemonSet 예시 YAML

간단한 DaemonSet 예시는 이렇게 생겼다.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-agent
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: node-agent
  template:
    metadata:
      labels:
        app: node-agent
    spec:
      containers:
        - name: node-agent
          image: busybox
          command:
            - sh
            - -c
            - "while true; do echo running on node; sleep 10; done"
```

핵심은 이 부분이다.

```yaml
kind: DaemonSet
```

구조는 Deployment와 비슷하다.

`selector`로 관리할 Pod를 찾고, `template`에 실제로 띄울 Pod 모양을 정의한다.

하지만 Deployment와 다르게 `replicas`가 없다.

왜냐하면 DaemonSet은 Pod 개수를 직접 정하는 것이 아니라, 노드 수에 따라 자동으로 맞춰지기 때문이다.

```text
Deployment
→ replicas로 개수 지정

DaemonSet
→ 노드마다 자동 배치
```

---

## 12. DaemonSet 확인 명령어

DaemonSet 목록 확인

```bash
kubectl get daemonset
```

줄여서 이렇게도 쓴다.

```bash
kubectl get ds
```

네임스페이스 지정

```bash
kubectl get ds -n monitoring
```

전체 네임스페이스에서 확인

```bash
kubectl get ds -A
```

DaemonSet 상세 확인

```bash
kubectl describe ds <daemonset-name> -n <namespace>
```

DaemonSet이 만든 Pod 확인

```bash
kubectl get pod -n <namespace> -o wide
```

`-o wide`를 붙이면 어떤 노드에 Pod가 떠 있는지 볼 수 있다.

```text
NAME              READY   STATUS    NODE
node-agent-abcde  1/1     Running   worker-1
node-agent-fghij  1/1     Running   worker-2
node-agent-klmno  1/1     Running   worker-3
```

---

## 13. 자주 헷갈리는 포인트

### DaemonSet은 무조건 모든 노드에 뜰까?

기본적으로는 가능한 모든 노드에 뜨는 것이 목표다.

하지만 조건이 있으면 일부 노드에만 뜰 수 있다.

예를 들어 다음 조건에 따라 특정 노드에는 뜨지 않을 수 있다.

```text
nodeSelector
affinity
taints / tolerations
```

정리하면 이렇다.

```text
DaemonSet은 모든 노드에 뜨는 것이 기본 목표
하지만 스케줄링 조건에 따라 일부 노드는 제외될 수 있음
```

---

### control-plane 노드에도 뜰까?

환경에 따라 다르다.

control-plane 노드에 taint가 걸려 있으면 일반 Pod는 스케줄링되지 않는다.

DaemonSet도 마찬가지로 toleration이 없으면 뜨지 못할 수 있다.

그래서 일부 DaemonSet은 이런 toleration을 가진다.

```yaml
tolerations:
  - key: node-role.kubernetes.io/control-plane
    operator: Exists
    effect: NoSchedule
```

이런 설정이 있으면 control-plane 노드에도 Pod가 뜰 수 있다.

---

### DaemonSet도 업데이트가 될까?

된다.

DaemonSet도 이미지 버전을 바꾸면 롤링 업데이트를 할 수 있다.

```bash
kubectl set image ds/node-agent node-agent=busybox:1.36
```

업데이트 상태 확인

```bash
kubectl rollout status ds/node-agent
```

업데이트 이력 확인

```bash
kubectl rollout history ds/node-agent
```

즉 DaemonSet도 Deployment처럼 업데이트 관리가 가능하다.

---

## 14. Daemon과 DaemonSet을 같이 정리하면

Daemon은 시스템 뒤에서 계속 실행되는 백그라운드 프로그램이다.

```text
sshd
dockerd
kubelet
containerd
kube-proxy
```

DaemonSet은 쿠버네티스에서 각 노드마다 이런 데몬성 Pod를 하나씩 띄우기 위한 리소스다.

```text
Node마다 로그 수집기
Node마다 모니터링 에이전트
Node마다 네트워크 플러그인
Node마다 보안 에이전트
```

즉 이름 그대로다.

```text
DaemonSet
= Daemon처럼 계속 떠 있어야 하는 Pod들의 집합
= 노드마다 하나씩 배치되는 백그라운드 작업 세트
```

---

## 15. 한 번에 정리

Daemon은 백그라운드에서 계속 실행되는 프로그램이다.

쿠버네티스에서는 `kubelet`, `containerd`, `kube-proxy` 같은 것들이 데몬처럼 동작한다.

DaemonSet은 각 노드마다 특정 Pod를 하나씩 실행시키기 위한 리소스다.

비교하면 이렇다.

```text
Deployment
→ Pod 몇 개 띄울래?

DaemonSet
→ Node마다 하나씩 띄울래?
```

그래서 로그 수집기, 모니터링 에이전트, 네트워크 플러그인처럼 노드마다 반드시 떠 있어야 하는 것들은 DaemonSet으로 배포한다.

핵심만 기억하면 된다.

```text
Daemon
= 시스템 뒤에서 계속 실행되는 프로그램

DaemonSet
= 각 노드마다 Daemon처럼 떠 있어야 하는 Pod를 배포하는 리소스
```

쿠버네티스에서 DaemonSet을 본다면 이렇게 생각하면 된다.

```text
아, 이건 노드마다 하나씩 필요한 에이전트구나.
```
