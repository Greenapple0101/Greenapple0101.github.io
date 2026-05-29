---
title: "[KUBERNETES] k3s 워커 노드는 어떻게 마스터 노드에 조인될까? — node-token으로 이해하는 노드 조인"
source: "https://velog.io/@yorange50/KUBERNETES-k3s-워커-노드는-어떻게-마스터-노드에-조인될까-node-token으로-이해하는-노드-조인"
published: "2026-05-17T10:54:34.111Z"
tags: ""
backup_date: "2026-05-29T14:52:52.734028"
---

쿠버네티스를 처음 구성할 때 가장 헷갈렸던 부분 중 하나가 **워커 노드 조인**이었다.
처음에는 워커 노드를 클러스터에 붙이기 위해 여러 설정 파일을 직접 복사하고 수정해야 하는 줄 알았다. 그런데 k3s에서는 핵심이 생각보다 단순했다.

결론부터 말하면, k3s 워커 노드를 마스터 노드에 조인시키기 위해 가장 중요한 것은 **마스터 노드의 node-token**이다.

---

## 1. 문제 상황

팀 프로젝트에서 k3s 기반 클러스터를 구성하던 중, 서버는 여러 대 있었지만 실제로는 모든 서버가 클러스터에 정상적으로 붙어 있지 않았다.

겉으로는 각 서버에 k3s가 설치된 것처럼 보였지만, 마스터 노드에서 확인해보면 일부 워커 노드가 보이지 않았다.

```bash
kubectl get nodes
```

정상이라면 이런 식으로 마스터와 워커 노드가 모두 보여야 한다.

```bash
NAME       STATUS   ROLES
master     Ready    control-plane
worker1    Ready    <none>
worker2    Ready    <none>
```

하지만 문제가 있을 때는 마스터만 보였다.

```bash
NAME       STATUS   ROLES
master     Ready    control-plane
```

즉, 워커 서버에 뭔가 설치되어 있다고 해서 그 서버가 자동으로 클러스터에 참여하는 것은 아니었다.
워커 노드는 반드시 **마스터 노드의 토큰을 사용해 조인**해야 한다.

---

## 2. 워커 조인에 필요한 핵심: node-token

k3s에서 워커 노드가 마스터 노드에 조인하려면 마스터가 발급한 토큰이 필요하다.

이 토큰은 마스터 노드의 다음 경로에 있다.

```bash
/var/lib/rancher/k3s/server/node-token
```

마스터 노드에서 아래 명령어로 확인할 수 있다.

```bash
sudo cat /var/lib/rancher/k3s/server/node-token
```

출력 예시는 이런 형태다.

```bash
K10d8f3a4f6...::server:...
```

이 값이 바로 워커 노드가 마스터 클러스터에 들어갈 때 사용하는 인증 토큰이다.

쉽게 말하면,

```text
node-token
= 워커 노드가 마스터에게
  “나 이 클러스터에 들어가도 되나요?”라고 요청할 때 쓰는 비밀번호
```

라고 볼 수 있다.

---

## 3. 기존에 꼬인 k3s 상태 정리

이미 워커 노드에 k3s가 잘못 설치되어 있거나, agent가 애매하게 남아 있는 상태라면 먼저 정리하는 것이 좋다.

워커 노드에서 기존 agent를 제거한다.

```bash
sudo /usr/local/bin/k3s-agent-uninstall.sh
```

마스터 노드까지 재설치해야 하는 실습 환경이라면 다음 명령어를 사용할 수도 있다.

```bash
sudo /usr/local/bin/k3s-uninstall.sh
```

다만 운영 중인 클러스터라면 무작정 삭제하면 안 된다.
실습이나 데모 환경처럼 초기 구성이 꼬였을 때만 신중하게 정리해야 한다.

---

## 4. 마스터 노드에서 node-token 확인

마스터 노드에 접속해서 node-token을 확인한다.

```bash
sudo cat /var/lib/rancher/k3s/server/node-token
```

이 토큰을 복사해둔다.

이때 중요한 것은 토큰 값을 일부만 복사하면 안 된다는 것이다.
출력된 전체 문자열을 그대로 사용해야 한다.

---

## 5. 워커 노드에서 마스터로 조인하기

이제 워커 노드에서 아래 명령어를 실행한다.

```bash
curl -sfL https://get.k3s.io | \
K3S_URL=https://MASTER_IP:6443 \
K3S_TOKEN=NODE_TOKEN \
sh -
```

예를 들어 마스터 노드 IP가 `192.168.0.10`이고, node-token이 `K10d8f3a4f6...::server:...`라면 다음처럼 실행한다.

```bash
curl -sfL https://get.k3s.io | \
K3S_URL=https://192.168.0.10:6443 \
K3S_TOKEN=K10d8f3a4f6...::server:... \
sh -
```

여기서 중요한 값은 두 가지다.

```text
K3S_URL
= 워커 노드가 접속할 마스터 API Server 주소

K3S_TOKEN
= 마스터 노드에서 가져온 node-token
```

이 명령어를 실행하면 워커 노드에 k3s agent가 설치되고, 워커는 마스터 API Server에 접속해 클러스터에 등록된다.

---

## 6. 내부적으로 일어나는 일

겉으로 보면 명령어 한 줄이지만 내부에서는 다음 흐름이 일어난다.

```text
1. 워커 노드에 k3s agent 설치
2. 워커가 마스터 API Server(:6443)에 접속
3. node-token으로 인증
4. 워커 노드가 클러스터에 등록
5. Kubernetes 스케줄러가 해당 노드에 Pod를 배치할 수 있게 됨
```

즉, node-token은 단순한 문자열이 아니라
**워커 노드가 클러스터 구성원으로 인정받기 위한 인증 정보**다.

---

## 7. 마스터 노드에서 조인 확인

워커 노드에서 조인 명령어를 실행한 뒤, 마스터 노드에서 확인한다.

```bash
kubectl get nodes
```

정상적으로 붙었다면 다음처럼 워커 노드가 보인다.

```bash
NAME       STATUS   ROLES
master     Ready    control-plane
worker1    Ready    <none>
worker2    Ready    <none>
```

노드 상태가 `Ready`라면 클러스터에 정상 참여한 것이다.

Pod가 어느 노드에 떠 있는지 확인하고 싶다면 다음 명령어를 사용할 수 있다.

```bash
kubectl get pods -A -o wide --sort-by=.spec.nodeName
```

출력 결과의 `NODE` 컬럼을 보면 각 Pod가 어느 노드에 스케줄링되었는지 알 수 있다.

```bash
NAMESPACE     NAME              STATUS    IP           NODE
default       spring-app         Running   10.42.1.50   worker1
default       mysql-0            Running   10.42.1.49   worker1
default       recommend          Running   10.42.2.49   worker2
```

---

## 8. 트러블슈팅 포인트

워커 조인이 잘 안 될 때는 다음을 먼저 확인해야 한다.

### 1. 마스터 IP가 워커에서 접근 가능한가?

워커 노드에서 마스터 노드의 6443 포트로 접근할 수 있어야 한다.

```bash
curl -k https://MASTER_IP:6443
```

또는 보안 그룹, 방화벽, 네트워크 설정에서 6443 포트가 열려 있는지 확인해야 한다.

---

### 2. node-token을 정확히 복사했는가?

마스터에서 확인한 토큰 전체를 그대로 넣어야 한다.

```bash
sudo cat /var/lib/rancher/k3s/server/node-token
```

중간이 잘리거나 공백이 들어가면 조인이 실패할 수 있다.

---

### 3. 기존 k3s 설치가 꼬여 있지 않은가?

워커에 기존 agent가 남아 있으면 재조인이 꼬일 수 있다.

```bash
sudo /usr/local/bin/k3s-agent-uninstall.sh
```

정리 후 다시 조인 명령어를 실행하는 것이 더 빠를 때가 있다.

---

### 4. 조인 후 노드가 Ready 상태인가?

조인 명령어가 실행됐다고 끝이 아니다.
반드시 마스터에서 확인해야 한다.

```bash
kubectl get nodes
```

노드가 보이더라도 `NotReady`라면 아직 정상 상태가 아니다.
이 경우 네트워크, container runtime, kubelet 상태 등을 추가로 확인해야 한다.

---

## 9. 내가 헷갈렸던 이유

처음에는 워커 노드 조인이 여러 설정을 복사하고 수동으로 맞춰야 하는 복잡한 작업이라고 생각했다.

하지만 정리하고 보니 핵심은 단순했다.

```text
1. 마스터 노드에서 node-token을 확인한다.
2. 워커 노드에서 K3S_URL과 K3S_TOKEN을 넣고 k3s agent를 설치한다.
3. 마스터에서 kubectl get nodes로 조인 여부를 확인한다.
```

즉, k3s에서는 워커 조인 과정이 상당 부분 자동화되어 있었다.

---

## 10. 이 경험에서 얻은 교훈

Pod가 안 뜬다고 해서 항상 Deployment YAML이 문제인 것은 아니다.

쿠버네티스에서는 먼저 클러스터 상태를 봐야 한다.

특히 멀티 노드 환경에서는 다음 순서가 중요하다.

```text
1. 워커 노드가 클러스터에 조인되어 있는가?
2. kubectl get nodes에서 Ready 상태인가?
3. Pod가 어느 노드에 스케줄링되었는가?
4. 그 다음 Deployment, Service, Ingress 설정을 확인한다.
```

워커 노드가 클러스터에 조인되어 있지 않으면,
아무리 YAML이 맞아도 해당 서버에는 Pod가 배치될 수 없다.

---

## 마무리

이번 트러블슈팅을 통해 k3s 워커 조인의 핵심을 확실히 이해했다.

```text
워커 조인의 핵심은 node-token이다.
```

마스터 노드에서 node-token을 확인하고,

```bash
sudo cat /var/lib/rancher/k3s/server/node-token
```

워커 노드에서 이 토큰을 사용해 조인한다.

```bash
curl -sfL https://get.k3s.io | \
K3S_URL=https://MASTER_IP:6443 \
K3S_TOKEN=NODE_TOKEN \
sh -
```

그리고 마지막으로 마스터에서 확인한다.

```bash
kubectl get nodes
```

처음에는 복잡해 보였지만, 결국 핵심은 단순했다.

**마스터의 node-token을 워커가 사용해서 클러스터에 들어간다.**

쿠버네티스 운영에서 중요한 것은 명령어를 외우는 것이 아니라,
**그 명령어가 어떤 인증 흐름과 운영 전제조건 위에서 동작하는지 이해하는 것**이었다.