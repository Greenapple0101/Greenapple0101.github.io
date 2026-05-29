---
title: "[Kubernetes] Static Pod란? kubelet이 직접 관리하는 Pod"
source: "https://velog.io/@yorange50/Kubernetes-Static-Pod란-kubelet이-직접-관리하는-Pod"
published: "2026-05-27T15:22:57.566Z"
tags: ""
backup_date: "2026-05-29T14:52:52.712542"
---

쿠버네티스에서 Pod는 보통 `kubectl apply`로 만든다.

```bash
kubectl apply -f pod.yaml
```

그러면 일반적인 Pod 생성 흐름은 이렇게 된다.

```text
사용자
→ API Server
→ etcd 저장
→ Scheduler가 노드 선택
→ kubelet이 Pod 실행
```

그런데 **Static Pod**는 이 흐름과 조금 다르다.

Static Pod는 한 줄로 말하면 이거다.

```text
Static Pod = API Server가 아니라 kubelet이 직접 실행하고 관리하는 Pod
```

---

## 1. 일반 Pod는 어떻게 만들어질까?

보통 Pod를 만들 때는 `kubectl` 명령어를 사용한다.

```bash
kubectl apply -f nginx-pod.yaml
```

이 명령어를 치면 `kubectl`이 API Server에게 요청을 보낸다.

```text
API Server야, nginx Pod 하나 만들어줘
```

그 다음에는 이런 과정이 진행된다.

```text
API Server가 요청을 받음
→ etcd에 Pod 정보 저장
→ Scheduler가 어느 노드에 띄울지 결정
→ 해당 노드의 kubelet이 Pod 실행
```

즉 일반 Pod는 **API Server를 통해 생성되는 Pod**다.

---

## 2. Static Pod는 뭐가 다를까?

Static Pod는 `kubectl apply`로 만드는 Pod가 아니다.

노드 안의 특정 디렉토리에 YAML 파일을 넣어두면, 그 노드의 `kubelet`이 파일을 보고 직접 Pod를 실행한다.

보통 그 디렉토리는 여기다.

```bash
/etc/kubernetes/manifests
```

여기에 Pod YAML 파일이 있으면 kubelet이 감시한다.

```text
/etc/kubernetes/manifests 안에 YAML 파일 존재
→ kubelet이 파일을 읽음
→ kubelet이 직접 Pod 실행
```

즉 Static Pod의 흐름은 이렇게 된다.

```text
kubelet
→ 로컬 manifest 파일 감시
→ Pod 실행
```

API Server가 중간에 끼지 않는다.

---

## 3. 왜 Static Pod가 필요할까?

여기서 중요한 질문이 나온다.

> API Server도 Pod로 떠 있는데, API Server는 누가 띄우지?

쿠버네티스 control plane 컴포넌트들은 보통 Pod 형태로 떠 있다.

예를 들면 이런 것들이다.

```text
kube-apiserver
etcd
kube-scheduler
kube-controller-manager
```

그런데 생각해보면 이상하다.

Pod를 만들려면 API Server가 필요하다.
그런데 API Server 자기 자신도 Pod다.

```text
Pod를 만들려면 API Server가 필요함
근데 API Server도 Pod임
그럼 API Server는 누가 띄움?
```

이 문제를 해결하는 방식이 **Static Pod**다.

`kubelet`은 API Server가 없어도 로컬 파일을 보고 Pod를 실행할 수 있다.

그래서 control plane 노드의 `/etc/kubernetes/manifests` 안에는 보통 이런 파일들이 있다.

```bash
ls /etc/kubernetes/manifests
```

```text
etcd.yaml
kube-apiserver.yaml
kube-controller-manager.yaml
kube-scheduler.yaml
```

이 파일들을 kubelet이 직접 읽고 control plane Pod들을 띄운다.

---

## 4. Static Pod 확인하기

control plane 노드에서 아래 명령어를 쳐보면 된다.

```bash
ls /etc/kubernetes/manifests
```

보통 이런 파일들이 있다.

```text
etcd.yaml
kube-apiserver.yaml
kube-controller-manager.yaml
kube-scheduler.yaml
```

그리고 쿠버네티스에서 Pod 목록을 보면 이렇게 보인다.

```bash
kubectl get pod -n kube-system
```

```text
etcd-controlplane
kube-apiserver-controlplane
kube-controller-manager-controlplane
kube-scheduler-controlplane
```

여기서 중요한 점이 있다.

Static Pod는 kubelet이 직접 관리하지만, `kubectl get pod`에서도 보인다.

이유는 kubelet이 API Server에 **Mirror Pod**를 만들어서 보여주기 때문이다.

---

## 5. Mirror Pod란?

Static Pod는 원래 API Server가 만든 Pod가 아니다.

그런데 `kubectl get pod`로 아예 안 보이면 관리하기 불편하다.

그래서 kubelet이 API Server에게 이렇게 알려준다.

```text
이 노드에서 이런 Static Pod가 돌고 있어요
```

그러면 API Server에는 Static Pod의 복사본 같은 정보가 생긴다.

이걸 **Mirror Pod**라고 한다.

```text
실제 관리 주체: kubelet
kubectl에서 보이는 것: mirror pod
```

그래서 `kubectl get pod`로 보이긴 하지만, 실제 생성과 관리는 kubelet이 한다.

---

## 6. Static Pod 삭제는 어떻게 할까?

일반 Pod는 이렇게 삭제한다.

```bash
kubectl delete pod nginx
```

그런데 Static Pod를 이렇게 지우면 어떻게 될까?

```bash
kubectl delete pod kube-apiserver-controlplane -n kube-system
```

잠깐 사라졌다가 다시 살아난다.

왜냐하면 kubelet이 여전히 로컬 YAML 파일을 보고 있기 때문이다.

```text
Pod 삭제됨
→ kubelet이 /etc/kubernetes/manifests/kube-apiserver.yaml 발견
→ 다시 Pod 생성
```

진짜로 없애려면 manifest 파일을 지워야 한다.

```bash
sudo rm /etc/kubernetes/manifests/kube-apiserver.yaml
```

그러면 kubelet이 파일이 없어진 걸 감지하고 해당 Static Pod를 내린다.

정리하면 이렇다.

```text
manifest 파일 있음 → Static Pod 실행
manifest 파일 수정 → Static Pod 재생성
manifest 파일 삭제 → Static Pod 삭제
```

---

## 7. Static Pod 수정은 어떻게 할까?

Static Pod는 `kubectl edit pod`로 수정하는 게 핵심이 아니다.

Static Pod를 수정하려면 로컬 manifest 파일을 수정해야 한다.

예를 들어 etcd 설정을 바꾸고 싶으면 이 파일을 수정한다.

```bash
sudo vi /etc/kubernetes/manifests/etcd.yaml
```

파일을 저장하면 kubelet이 변경을 감지한다.

```text
etcd.yaml 수정
→ kubelet이 변경 감지
→ 기존 etcd Pod 재생성
→ 수정된 설정으로 다시 실행
```

그래서 Static Pod는 `kubectl`보다 **노드 안의 YAML 파일**이 중요하다.

---

## 8. CKA에서 왜 중요할까?

Static Pod는 특히 **etcd backup & restore 문제**에서 중요하다.

etcd 복구 문제에서는 보통 snapshot을 restore한다.

```bash
sudo ETCDCTL_API=3 etcdctl snapshot restore /data/etcd-snapshot.db \
  --data-dir=/var/lib/etcd-new
```

그 다음 etcd가 새 데이터 디렉토리를 보도록 설정을 바꿔야 한다.

그래서 이 파일을 수정한다.

```bash
sudo vi /etc/kubernetes/manifests/etcd.yaml
```

안에서 etcd 데이터 경로를 바꾼다.

```yaml
volumes:
- hostPath:
    path: /var/lib/etcd-new
    type: DirectoryOrCreate
  name: etcd-data
```

왜 이 파일을 수정할까?

etcd가 Static Pod로 떠 있기 때문이다.

```text
/etc/kubernetes/manifests/etcd.yaml 수정
→ kubelet이 변경 감지
→ etcd Static Pod 재시작
→ 새 data-dir 기준으로 etcd 실행
```

그래서 CKA에서 etcd restore를 풀 때 Static Pod 개념을 모르면 흐름이 잘 안 잡힌다.

---

## 9. 일반 Pod vs Static Pod

| 구분    | 일반 Pod               | Static Pod           |
| ----- | -------------------- | -------------------- |
| 생성 주체 | API Server           | kubelet              |
| 생성 방법 | `kubectl apply`      | 노드 로컬 manifest 파일 배치 |
| 저장 위치 | etcd                 | 노드의 로컬 파일            |
| 스케줄링  | Scheduler가 노드 선택     | 해당 노드에서 바로 실행        |
| 삭제 방법 | `kubectl delete pod` | manifest 파일 삭제       |
| 대표 예시 | 애플리케이션 Pod           | control plane 컴포넌트   |

핵심 차이는 이거다.

```text
일반 Pod = API Server를 통해 생성되는 Pod
Static Pod = kubelet이 직접 생성하는 Pod
```

---

## 10. 반드시 기억할 경로

Static Pod에서 제일 중요한 경로는 이거다.

```bash
/etc/kubernetes/manifests
```

여기 안에 있는 YAML 파일들을 kubelet이 감시한다.

대표적으로 이런 파일들이 있다.

```text
/etc/kubernetes/manifests/etcd.yaml
/etc/kubernetes/manifests/kube-apiserver.yaml
/etc/kubernetes/manifests/kube-controller-manager.yaml
/etc/kubernetes/manifests/kube-scheduler.yaml
```

CKA에서는 이 경로는 거의 외워두는 게 좋다.

특히 etcd 문제에서 자주 만난다.

---

## 11. 한 줄 정리

```text
Static Pod = kubelet이 노드 로컬 manifest 파일을 보고 직접 실행하는 Pod
```

조금 더 쉽게 말하면:

```text
API Server 없이도 kubelet이 직접 띄울 수 있는 Pod
```

실전에서는 이렇게 기억하면 된다.

```text
/etc/kubernetes/manifests 안의 YAML
= kubelet이 감시하는 Static Pod 설정 파일
```

그리고 CKA에서 가장 중요한 연결은 이거다.

```text
etcd restore
→ /etc/kubernetes/manifests/etcd.yaml 수정
→ kubelet이 감지
→ etcd Static Pod 재시작
```

Static Pod는 그냥 이론 개념이 아니라,
**control plane을 살리고 고칠 때 직접 만지는 Pod**라고 보면 된다.
