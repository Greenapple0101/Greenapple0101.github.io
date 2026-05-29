---
title: "[Kubernetes] kubectl create 랑 kubectl run 은 뭐가 다를까?"
source: "https://velog.io/@yorange50/Kubernetes-kubectl-create-랑-kubectl-run-은-뭐가-다를까"
published: "2026-05-22T04:34:55.405Z"
tags: ""
backup_date: "2026-05-29T14:52:52.715821"
---

CKA 공부하다 보면 이런 명령어를 자주 본다.

```bash
kubectl run nginx --image=nginx
```

또 이런 것도 본다.

```bash
kubectl create deployment web --image=nginx
```

둘 다 뭔가 “만드는” 명령어처럼 보인다.
그래서 처음에는 헷갈린다.

> 둘 다 리소스를 생성하는 명령어인데, `run`은 주로 Pod를 빠르게 실행할 때 쓰고, `create`는 Deployment, Namespace, ConfigMap, Secret 같은 여러 Kubernetes 리소스를 명시적으로 만들 때 쓴다.

---

## 1. `kubectl run`은 뭐냐

`kubectl run`은 말 그대로 **이미지를 하나 실행해서 Pod를 만드는 명령어**라고 보면 된다.

공식 문서에서도 `kubectl run`은 “특정 이미지를 Pod로 생성하고 실행한다”는 명령어로 설명된다. ([Kubernetes][1])

예를 들면:

```bash
kubectl run nginx-pod --image=nginx
```

이 명령어는 대충 이런 뜻이다.

```text
nginx 이미지로
nginx-pod라는 Pod 하나 만들어줘
```

즉 결과물은 보통 **Pod**다.

확인해보면:

```bash
kubectl get pod
```

이렇게 Pod 목록에 뜬다.

---

## 2. `kubectl create`는 뭐냐

`kubectl create`는 더 넓은 의미의 생성 명령어다.

공식 문서에서 `kubectl create`는 파일이나 표준 입력으로부터 리소스를 생성하는 명령어로 설명된다. YAML이나 JSON 파일을 넣어서 리소스를 만들 수 있다. ([Kubernetes][2])

예를 들면:

```bash
kubectl create namespace dev
```

```bash
kubectl create deployment web --image=nginx
```

```bash
kubectl create configmap app-config --from-literal=MODE=prod
```

```bash
kubectl create secret generic db-secret --from-literal=password=1234
```

이렇게 여러 종류의 Kubernetes 리소스를 만들 수 있다.

즉 `create`는 느낌상 이거다.

```text
Kubernetes 리소스 하나 만들어줘
근데 어떤 리소스인지 내가 뒤에 정확히 말할게
```

---

## 3. 제일 큰 차이

핵심만 보면 이거다.

| 명령어              | 주 용도       | 자주 만드는 것                                            |
| ---------------- | ---------- | --------------------------------------------------- |
| `kubectl run`    | 이미지를 바로 실행 | Pod                                                 |
| `kubectl create` | 특정 리소스를 생성 | Namespace, Deployment, ConfigMap, Secret, Service 등 |

예를 들어 nginx 하나 띄우고 싶다면:

```bash
kubectl run nginx-pod --image=nginx
```

이건 Pod를 바로 만든다.

반대로 운영용 Deployment를 만들고 싶다면:

```bash
kubectl create deployment web --image=nginx
```

이건 Deployment를 만든다. `kubectl create deployment`는 지정한 이름과 이미지로 Deployment를 생성하는 명령어다. ([Kubernetes][3])

---

## 4. Pod랑 Deployment 차이 때문에 헷갈리는 것

여기서 진짜 중요한 건 `run`과 `create` 차이보다 **Pod와 Deployment 차이**다.

`kubectl run`:

```bash
kubectl run nginx --image=nginx
```

결과:

```text
Pod 하나 생성
```

`kubectl create deployment`:

```bash
kubectl create deployment nginx --image=nginx
```

결과:

```text
Deployment 생성
→ Deployment가 ReplicaSet 생성
→ ReplicaSet이 Pod 생성
```

즉 둘 다 최종적으로는 nginx 컨테이너가 떠 있을 수 있다.
하지만 관리 방식이 다르다.

---

## 5. `run`으로 만든 Pod는 단독 Pod다

```bash
kubectl run nginx-pod --image=nginx
```

이렇게 만들면 Pod 하나가 생긴다.

```bash
kubectl get pod
```

```text
NAME        READY   STATUS    RESTARTS   AGE
nginx-pod   1/1     Running   0          10s
```

이 Pod는 혼자 있는 Pod다.
Deployment가 관리하는 Pod가 아니다.

그래서 삭제하면 그냥 사라진다.

```bash
kubectl delete pod nginx-pod
```

끝이다.
자동으로 다시 살아나지 않는다.

---

## 6. `create deployment`로 만든 Pod는 관리받는 Pod다

```bash
kubectl create deployment web --image=nginx
```

이렇게 만들면 Deployment가 생긴다.

```bash
kubectl get deploy
```

```text
NAME   READY   UP-TO-DATE   AVAILABLE   AGE
web    1/1     1            1           10s
```

Pod도 생긴다.

```bash
kubectl get pod
```

```text
NAME                   READY   STATUS    RESTARTS   AGE
web-xxxxxxxxxx-xxxxx    1/1     Running   0          10s
```

근데 이 Pod는 그냥 혼자 있는 게 아니다.

```text
Deployment
  ↓
ReplicaSet
  ↓
Pod
```

이 구조로 관리된다.

그래서 Pod를 삭제해도:

```bash
kubectl delete pod web-xxxxxxxxxx-xxxxx
```

다시 생긴다.

왜냐하면 Deployment가 이런 생각을 하기 때문이다.

```text
어? 나는 Pod 1개를 유지해야 하는데 하나가 죽었네?
그럼 다시 만들어야지.
```

공식 문서에서도 Deployment는 Pod와 ReplicaSet을 관리하고, 애플리케이션 배포와 업데이트에 사용되는 리소스로 설명된다. ([Kubernetes][4])

---

## 7. CKA에서는 언제 `run`을 쓰냐

CKA에서 `run`은 보통 이런 경우에 많이 쓴다.

### 1) 단일 Pod 빠르게 만들 때

```bash
kubectl run nginx-pod --image=nginx
```

### 2) 테스트용 임시 Pod 만들 때

```bash
kubectl run tmp --image=busybox --rm -it -- sh
```

또는 curl 테스트용으로:

```bash
kubectl run curl --image=curlimages/curl --rm -it -- sh
```

### 3) Pod YAML 뼈대 만들 때

```bash
kubectl run nginx-pod \
  --image=nginx \
  --dry-run=client \
  -o yaml > pod.yaml
```

이게 진짜 많이 쓰인다.

처음부터 YAML을 다 외우는 게 아니라, 명령어로 뼈대를 만들고 수정하는 방식이다.

---

## 8. CKA에서는 언제 `create`를 쓰냐

`create`는 범위가 훨씬 넓다.

### Namespace 만들기

```bash
kubectl create ns dev
```

### Deployment 만들기

```bash
kubectl create deployment web --image=nginx
```

### ConfigMap 만들기

```bash
kubectl create configmap app-config \
  --from-literal=MODE=prod
```

### Secret 만들기

```bash
kubectl create secret generic db-secret \
  --from-literal=password=1234
```

### YAML 파일로 리소스 만들기

```bash
kubectl create -f pod.yaml
```

다만 실전에서는 `create -f`보다 `apply -f`를 더 자주 쓰는 편이다.

---

## 9. 그럼 `create -f`랑 `apply -f`는 또 뭐가 다르냐

이것도 헷갈린다.

```bash
kubectl create -f pod.yaml
```

이건 “처음 생성” 느낌이 강하다.

이미 같은 리소스가 있으면 에러가 난다.

```text
already exists
```

반면:

```bash
kubectl apply -f pod.yaml
```

이건 “이 YAML 상태가 되게 맞춰줘”에 가깝다.

없으면 만들고, 있으면 변경 사항을 반영한다.

그래서 CKA에서는 보통:

```bash
kubectl apply -f file.yaml
```

을 많이 쓴다.

---

## 10. 시험장에서 감 잡는 법

문제에서 **Pod 하나 만들라**고 하면:

```bash
kubectl run
```

예:

```text
Create a pod named nginx-pod using image nginx.
```

풀이:

```bash
kubectl run nginx-pod --image=nginx
```

문제에서 **Deployment 만들라**고 하면:

```bash
kubectl create deployment
```

예:

```text
Create a deployment named web using image nginx with 3 replicas.
```

풀이:

```bash
kubectl create deployment web --image=nginx --replicas=3
```

문제에서 **Namespace, ConfigMap, Secret 만들라**고 하면:

```bash
kubectl create
```

예:

```bash
kubectl create ns dev
kubectl create configmap app-config --from-literal=MODE=prod
kubectl create secret generic db-secret --from-literal=password=1234
```

---

## 11. 한 줄로 정리

```text
kubectl run
= 이미지를 실행해서 Pod를 빠르게 만든다.

kubectl create
= 특정 Kubernetes 리소스를 명시적으로 만든다.
```

조금 더 CKA식으로 말하면:

```text
Pod 단독 생성 → kubectl run
Deployment 생성 → kubectl create deployment
Namespace/ConfigMap/Secret 생성 → kubectl create
YAML 뼈대 생성 → 둘 다 --dry-run=client -o yaml로 활용
```

---

## 12. 자주 쓰는 명령어 모음

```bash
# Pod 생성
kubectl run nginx-pod --image=nginx

# Pod YAML 뼈대 생성
kubectl run nginx-pod --image=nginx --dry-run=client -o yaml > pod.yaml

# Deployment 생성
kubectl create deployment web --image=nginx

# Deployment YAML 뼈대 생성
kubectl create deployment web --image=nginx --dry-run=client -o yaml > deploy.yaml

# Namespace 생성
kubectl create ns dev

# ConfigMap 생성
kubectl create configmap app-config --from-literal=MODE=prod

# Secret 생성
kubectl create secret generic db-secret --from-literal=PASSWORD=1234
```

---

## 결론

처음에는 `run`도 만들고, `create`도 만들고, 둘 다 비슷해 보인다.
근데 기준을 하나만 잡으면 된다.

```text
run은 “컨테이너 이미지 하나를 Pod로 실행”
create는 “Kubernetes 리소스를 생성”
```

그리고 CKA에서는 이 감각이 중요하다.

```text
nginx Pod 하나 필요하다
→ kubectl run

운영용 앱 배포가 필요하다
→ kubectl create deployment

설정값이나 비밀번호가 필요하다
→ kubectl create configmap / secret

YAML이 필요하다
→ --dry-run=client -o yaml
```

즉 `run`은 빠른 Pod 생성용 도구고, `create`는 리소스 생성용 도구라고 보면 된다.

[1]: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_run/?utm_source=chatgpt.com "kubectl run"
[2]: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_create/?utm_source=chatgpt.com "kubectl create"
[3]: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_create/kubectl_create_deployment/?utm_source=chatgpt.com "kubectl create deployment"
[4]: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/?utm_source=chatgpt.com "Deployments"
