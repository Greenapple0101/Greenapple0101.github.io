---
title: "[CKA] etcd 정리: 클러스터의 상태를 저장하는 핵심 데이터베이스"
source: "https://velog.io/@yorange50/CKA-etcd-정리-클러스터의-상태를-저장하는-핵심-데이터베이스"
published: "2026-05-04T05:55:39.391Z"
tags: ""
backup_date: "2026-05-29T14:52:52.778007"
---

Kubernetes를 공부하다 보면 `etcd`라는 단어가 자주 나온다. 처음에는 이름부터 낯설다. Pod, Deployment, Service까지는 “애플리케이션을 배포하는 리소스구나” 하고 이해가 되는데, etcd는 조금 더 내부 구조에 가까운 개념이다. 특히 CKA를 준비한다면 etcd는 반드시 알아야 한다. 이유는 단순하다. Kubernetes 클러스터의 모든 상태 정보가 etcd에 저장되기 때문이다.

---

## 1. etcd란?

`etcd`는 Kubernetes 클러스터의 상태 정보를 저장하는 key-value 저장소다.

쉽게 말하면 다음과 같다.

```text
etcd = Kubernetes 클러스터의 데이터베이스
```

Kubernetes는 계속해서 클러스터의 상태를 기억해야 한다. 예를 들어 다음과 같은 정보들이다.

```text
현재 어떤 Pod가 있는지
Deployment의 replica 수가 몇 개인지
Service가 어떤 Pod를 바라보는지
ConfigMap과 Secret 값이 무엇인지
Namespace가 무엇이 있는지
Node 상태가 어떤지
RBAC 권한이 어떻게 설정되어 있는지
PV, PVC 정보가 무엇인지
```

이런 정보들이 저장되는 곳이 etcd다.

우리가 `kubectl get pods` 명령어로 보는 정보도 결국 Kubernetes API Server가 etcd에 저장된 상태를 읽어서 보여주는 것이다.

---

## 2. etcd는 일반 애플리케이션 DB가 아니다

etcd를 “Kubernetes의 DB”라고 설명하면 MySQL이나 PostgreSQL 같은 DB를 떠올릴 수 있다. 하지만 etcd는 사용자의 게시글, 주문 내역, 회원 정보 같은 애플리케이션 데이터를 저장하는 곳이 아니다.

예를 들어 Spring Boot 게시판 서비스를 운영한다고 해보자.

```text
Spring Boot 게시판 서비스
  ↓
MySQL
```

여기서 MySQL에는 게시글, 댓글, 회원 정보가 저장된다.

반면 Kubernetes의 etcd에는 다음과 같은 정보가 저장된다.

```text
board-api Deployment가 존재한다
replicas는 3이다
board-api Pod들이 실행 중이다
board-api Service가 app=board-api 라벨을 가진 Pod를 바라본다
```

즉, etcd는 서비스 데이터가 아니라 Kubernetes가 클러스터를 운영하기 위해 필요한 상태 정보를 저장한다.

정리하면 다음과 같다.

```text
MySQL = 애플리케이션 데이터 저장소
etcd = Kubernetes 클러스터 상태 저장소
```

---

## 3. kubectl 명령어와 etcd의 관계

사용자가 다음 명령어를 입력했다고 하자.

```bash
kubectl create deployment nginx --image=nginx --replicas=3
```

이 명령어는 단순히 바로 Pod 3개를 만드는 명령처럼 보인다. 하지만 내부적으로는 다음 흐름을 거친다.

```text
사용자
  ↓
kubectl
  ↓
kube-apiserver
  ↓
etcd
```

사용자가 `kubectl`로 명령을 보내면, 요청은 먼저 `kube-apiserver`로 간다. 그리고 API Server는 “nginx Deployment가 존재해야 하고, replica는 3개여야 한다”는 상태 정보를 etcd에 저장한다.

그 후 controller-manager, scheduler, kubelet 같은 Kubernetes 컴포넌트들이 이 상태를 보고 실제 Pod를 만든다.

즉, Kubernetes에서 중요한 것은 “명령을 한 번 실행했다”가 아니라 “원하는 상태가 etcd에 저장되었다”는 점이다.

---

## 4. Desired State와 etcd

Kubernetes의 핵심 개념 중 하나는 Desired State, 즉 원하는 상태다.

예를 들어 사용자가 다음과 같이 명령한다.

```bash
kubectl create deployment nginx --image=nginx --replicas=3
```

이것은 Kubernetes에게 이렇게 말하는 것과 같다.

```text
nginx Pod가 항상 3개 있었으면 좋겠어.
```

이 원하는 상태가 etcd에 저장된다.

```text
Deployment 이름: nginx
이미지: nginx
replicas: 3
```

만약 Pod 하나가 죽어서 현재 Pod가 2개가 되면 Kubernetes는 etcd에 저장된 원하는 상태와 현재 상태를 비교한다.

```text
원하는 상태: Pod 3개
현재 상태: Pod 2개
```

그러면 controller가 다시 Pod 하나를 생성해서 원하는 상태를 맞춘다.

```text
Pod 2개 → Pod 3개로 복구
```

이것이 Kubernetes가 스스로 복구하는 방식이다. 그리고 그 기준이 되는 상태 정보가 etcd에 저장된다.

---

## 5. etcd는 어디에서 실행될까?

kubeadm으로 만든 일반적인 Kubernetes 클러스터에서는 etcd가 control-plane 노드에서 static pod 형태로 실행된다.

확인은 다음 명령어로 할 수 있다.

```bash
kubectl get pods -n kube-system
```

출력 예시는 다음과 비슷하다.

```text
etcd-controlplane
kube-apiserver-controlplane
kube-scheduler-controlplane
kube-controller-manager-controlplane
```

또한 static pod manifest 파일은 보통 다음 경로에 있다.

```bash
/etc/kubernetes/manifests
```

해당 디렉터리를 확인하면 다음과 같은 파일들이 있다.

```bash
ls /etc/kubernetes/manifests
```

```text
etcd.yaml
kube-apiserver.yaml
kube-controller-manager.yaml
kube-scheduler.yaml
```

etcd 설정을 직접 확인하려면 다음 파일을 보면 된다.

```bash
cat /etc/kubernetes/manifests/etcd.yaml
```

CKA에서는 etcd 복구 문제를 풀 때 이 파일을 수정해야 하는 경우가 많다.

---

## 6. etcd가 중요한 이유

etcd가 중요한 이유는 Kubernetes 클러스터의 상태 정보가 모두 저장되어 있기 때문이다.

만약 etcd 데이터가 손상되거나 사라지면 Kubernetes는 다음 정보를 잃을 수 있다.

```text
어떤 Deployment가 있었는지
Pod를 몇 개 유지해야 하는지
Service가 어떤 Pod를 바라봐야 하는지
Secret 값이 무엇인지
RBAC 권한이 어떻게 설정되어 있었는지
PVC가 어떤 PV와 연결되어 있었는지
```

즉, etcd 장애는 단순한 컴포넌트 하나의 장애가 아니라 클러스터 전체 상태 정보의 장애로 이어질 수 있다.

그래서 운영 환경에서는 etcd 백업이 매우 중요하다.

---

## 7. etcd 백업이란?

etcd 백업은 현재 클러스터 상태 정보를 snapshot 파일로 저장하는 것이다.

CKA에서는 etcd snapshot을 특정 경로에 저장하라는 문제가 나올 수 있다.

먼저 etcdctl API 버전을 지정한다.

```bash
export ETCDCTL_API=3
```

그다음 snapshot을 저장한다.

```bash
ETCDCTL_API=3 etcdctl snapshot save /tmp/etcd-backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
```

이 명령어는 현재 etcd 데이터를 `/tmp/etcd-backup.db` 파일로 저장한다.

옵션의 의미는 다음과 같다.

```text
--endpoints
etcd 서버 주소

--cacert
etcd CA 인증서

--cert
etcd 인증서

--key
etcd 인증서 키
```

kubeadm 기반 클러스터에서는 보통 etcd 관련 인증서가 다음 경로에 있다.

```bash
/etc/kubernetes/pki/etcd/
```

확인은 다음 명령어로 할 수 있다.

```bash
ls /etc/kubernetes/pki/etcd/
```

---

## 8. snapshot 상태 확인

백업한 snapshot 파일이 정상인지 확인할 수 있다.

```bash
ETCDCTL_API=3 etcdctl snapshot status /tmp/etcd-backup.db
```

출력 예시는 다음과 같다.

```text
HASH        REVISION    TOTAL KEYS    TOTAL SIZE
abcd1234    12345       1000          5.2 MB
```

CKA에서는 백업 명령어를 실행한 뒤 snapshot status까지 확인하는 습관을 들이는 것이 좋다.

---

## 9. etcd 복구

etcd 복구는 snapshot 파일을 이용해 새로운 데이터 디렉터리를 만드는 과정이다.

```bash
ETCDCTL_API=3 etcdctl snapshot restore /tmp/etcd-backup.db \
  --data-dir=/var/lib/etcd-restore
```

이 명령어는 `/tmp/etcd-backup.db` snapshot을 기반으로 `/var/lib/etcd-restore` 디렉터리에 복구 데이터를 만든다.

흐름은 다음과 같다.

```text
/tmp/etcd-backup.db
  ↓
/var/lib/etcd-restore
```

복구 디렉터리를 만들었다고 끝나는 것은 아니다. Kubernetes가 새 데이터 디렉터리를 사용하도록 etcd static pod 설정을 수정해야 한다.

```bash
vi /etc/kubernetes/manifests/etcd.yaml
```

기존에는 보통 다음과 같은 설정이 있다.

```yaml
- --data-dir=/var/lib/etcd
```

이를 복구한 경로로 변경한다.

```yaml
- --data-dir=/var/lib/etcd-restore
```

또한 volume의 hostPath도 확인해야 한다.

```yaml
volumes:
- hostPath:
    path: /var/lib/etcd-restore
```

수정 후 저장하면 kubelet이 static pod manifest 변경을 감지하고 etcd Pod를 다시 실행한다.

---

## 10. CKA에서 etcd 문제를 푸는 흐름

CKA에서 etcd 문제는 크게 두 가지로 나온다.

```text
1. etcd snapshot을 특정 경로에 저장하라
2. 주어진 snapshot 파일로 etcd를 복구하라
```

백업 문제의 흐름은 다음과 같다.

```bash
export ETCDCTL_API=3
```

```bash
ETCDCTL_API=3 etcdctl snapshot save <저장경로> \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
```

```bash
ETCDCTL_API=3 etcdctl snapshot status <저장경로>
```

복구 문제의 흐름은 다음과 같다.

```bash
export ETCDCTL_API=3
```

```bash
ETCDCTL_API=3 etcdctl snapshot restore <snapshot-file> \
  --data-dir=<복구 디렉터리>
```

```bash
vi /etc/kubernetes/manifests/etcd.yaml
```

수정할 부분은 보통 다음과 같다.

```text
--data-dir 경로
volumeMounts의 mountPath
volumes의 hostPath path
```

마지막으로 클러스터 상태를 확인한다.

```bash
kubectl get pods -n kube-system
kubectl get nodes
```

---

## 11. etcd 관련 자주 쓰는 명령어

etcd Pod 확인:

```bash
kubectl get pods -n kube-system
```

etcd Pod 상세 확인:

```bash
kubectl describe pod etcd-<node-name> -n kube-system
```

static pod manifest 확인:

```bash
ls /etc/kubernetes/manifests
```

etcd manifest 확인:

```bash
cat /etc/kubernetes/manifests/etcd.yaml
```

etcd 인증서 경로 확인:

```bash
ls /etc/kubernetes/pki/etcd
```

kubelet 상태 확인:

```bash
systemctl status kubelet
```

kubelet 로그 확인:

```bash
journalctl -u kubelet -f
```

컨테이너 런타임 상태 확인:

```bash
crictl ps
```

---

## 12. etcd 백업 파일은 민감하다

etcd에는 Kubernetes 클러스터의 중요한 상태 정보가 저장된다. 특히 Secret도 etcd에 저장된다.

즉, etcd snapshot 파일에는 다음과 같은 민감한 정보가 포함될 수 있다.

```text
Secret
ServiceAccount 정보
RBAC 권한 정보
ConfigMap
클러스터 리소스 정보
```

따라서 운영 환경에서는 etcd snapshot 파일을 아무 곳에나 두면 안 된다. 백업 파일의 권한, 저장 위치, 암호화, 접근 제어까지 신경 써야 한다.

CKA 시험에서는 보통 명령어 수행이 중심이지만, 실무에서는 백업 파일 보안까지 고려해야 한다.

---

## 13. etcd를 한 문장으로 정리하면

etcd는 Kubernetes 클러스터의 모든 상태 정보를 저장하는 핵심 key-value 저장소다. Kubernetes는 etcd에 저장된 원하는 상태를 기준으로 현재 상태를 맞추고, 장애가 발생하면 다시 원하는 상태로 복구하려고 한다.

---

## 마무리

처음 Kubernetes를 공부할 때는 Pod, Deployment, Service처럼 눈에 보이는 리소스에 집중하게 된다. 하지만 CKA나 실제 운영 관점으로 넘어가면 etcd를 반드시 이해해야 한다.

정리하면 다음과 같다.

```text
kubectl 명령은 kube-apiserver로 전달된다.
kube-apiserver는 클러스터 상태를 etcd에 저장한다.
Deployment, Pod, Service, Secret, RBAC 정보도 etcd에 저장된다.
Kubernetes는 etcd에 저장된 Desired State를 기준으로 현재 상태를 맞춘다.
etcd가 망가지면 클러스터 상태 정보가 위험해진다.
그래서 etcd snapshot 백업과 복구가 중요하다.
```

CKA 기준으로는 특히 아래 두 명령어를 확실히 익혀두는 것이 좋다.

```bash
ETCDCTL_API=3 etcdctl snapshot save /tmp/etcd-backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
```

```bash
ETCDCTL_API=3 etcdctl snapshot restore /tmp/etcd-backup.db \
  --data-dir=/var/lib/etcd-restore
```

etcd를 이해하면 Kubernetes가 단순히 컨테이너를 띄우는 도구가 아니라, 클러스터의 상태를 저장하고 원하는 상태로 계속 맞춰가는 시스템이라는 점이 훨씬 선명하게 보인다.
