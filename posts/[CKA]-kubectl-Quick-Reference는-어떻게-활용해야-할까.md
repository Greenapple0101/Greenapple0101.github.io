---
title: "[CKA] kubectl Quick Reference는 어떻게 활용해야 할까?"
source: "https://velog.io/@yorange50/CKA-kubectl-Quick-Reference는-어떻게-활용해야-할까"
published: "2026-05-19T15:54:38.263Z"
tags: ""
backup_date: "2026-05-29T14:52:52.720635"
---

CKA를 준비할 때 공식문서를 본다고 하면 보통 Kubernetes Concepts나 Tasks 문서를 떠올리기 쉽다.
그런데 실제 시험장에서 제일 자주 열게 되는 문서는 의외로 **kubectl Quick Reference**다.

`kubectl Quick Reference`는 말 그대로 `kubectl` 명령어 빠른 참고표다.
공식문서에서도 이 페이지를 “commonly used kubectl commands and flags”를 모아둔 페이지라고 설명한다. 현재 문서는 Kubernetes v1.36 기준으로 정리되어 있다. ([Kubernetes][1])

CKA에서는 모든 YAML을 처음부터 외워서 쓰기보다, `kubectl`로 기본 리소스를 빠르게 만들고 수정하는 능력이 중요하다.

```text
문제 읽기
→ 필요한 리소스 판단
→ kubectl 명령어로 기본 YAML 생성
→ 문제 조건에 맞게 수정
→ apply
→ get / describe / logs / curl 로 검증
```

이 흐름에서 `kubectl Quick Reference`는 시험장용 명령어 사전처럼 쓰면 된다.

---

## 1. kubectl Quick Reference는 외우는 문서가 아니다

처음 CKA를 준비하면 이런 생각을 하기 쉽다.

```text
kubectl 명령어를 다 외워야 하나?
옵션도 다 외워야 하나?
-o yaml, --dry-run=client, --selector 이런 거 다 암기해야 하나?
```

물론 자주 쓰는 건 손에 익어야 한다.
하지만 모든 옵션을 외울 필요는 없다.

중요한 건 이거다.

```text
어떤 상황에서 Quick Reference를 열어야 하는지 아는 것
필요한 명령어를 빠르게 찾는 것
찾은 명령어를 내 문제에 맞게 바꾸는 것
```

즉, Quick Reference는 읽는 문서가 아니라 **꺼내 쓰는 문서**다.

---

## 2. 제일 먼저 봐야 하는 부분: 기본 문법

`kubectl`의 기본 구조는 이렇다.

```bash
kubectl [command] [TYPE] [NAME] [flags]
```

예를 들면:

```bash
kubectl get pod nginx
kubectl describe pod nginx
kubectl delete pod nginx
kubectl get svc nginx-svc -n default
```

여기서 구조를 나누면:

```text
command: get, describe, delete
TYPE: pod, svc
NAME: nginx, nginx-svc
flags: -n default
```

CKA에서 명령어가 헷갈릴 때는 이 기본 구조부터 다시 생각하면 된다.

```text
무엇을 할 건가? → get / create / delete / describe / edit
어떤 리소스인가? → pod / deploy / svc / cm / secret
이름은 무엇인가?
namespace가 있는가?
추가 옵션이 필요한가?
```

---

## 3. 가장 많이 쓰는 조회 명령어

시험장에서 제일 많이 쓰는 명령어는 리소스를 확인하는 명령어다.

```bash
kubectl get pods
kubectl get pods -o wide
kubectl get deployments
kubectl get svc
kubectl get nodes
kubectl get cm
kubectl get secret
kubectl get ns
```

특정 namespace를 봐야 하면 `-n`을 붙인다.

```bash
kubectl get pods -n kube-system
kubectl get svc -n default
kubectl get cm -n nginx-static
```

전체 namespace에서 보고 싶으면 `-A`를 쓴다.

```bash
kubectl get pods -A
kubectl get svc -A
```

CKA 문제에서는 namespace 조건이 자주 나온다.

```text
in the nginx-static namespace
in the web namespace
in namespace default
```

이런 문장이 보이면 거의 모든 명령어에 `-n`을 붙여야 한다.

---

## 4. describe는 에러 확인용이다

`get`이 목록 확인이라면, `describe`는 원인 확인이다.

```bash
kubectl describe pod <pod-name>
kubectl describe deployment <deployment-name>
kubectl describe svc <service-name>
kubectl describe node <node-name>
```

공식문서의 kubectl describe 설명에 따르면, `describe`는 특정 리소스의 자세한 정보와 관련 이벤트를 출력한다. 그래서 Pod가 Pending이거나, ImagePullBackOff가 나거나, Service 연결이 이상할 때 원인 확인용으로 매우 자주 쓴다. ([Kubernetes][2])

예를 들어 Pod가 Pending이면:

```bash
kubectl describe pod my-pod
```

여기서 봐야 하는 곳은 보통 아래쪽이다.

```text
Events:
```

자주 보는 원인:

```text
이미지 이름 오류
포트 설정 오류
PVC 바인딩 실패
스케줄링 실패
노드 리소스 부족
taint 때문에 스케줄링 불가
```

시험장에서는 에러가 났을 때 감으로 고치지 말고, 먼저 `describe`를 봐야 한다.

---

## 5. -o yaml은 리소스를 파일로 뽑을 때 쓴다

CKA에서 정말 자주 쓰는 옵션이 `-o yaml`이다.

```bash
kubectl get pod nginx -o yaml
kubectl get deploy nginx -o yaml
kubectl get svc nginx-svc -o yaml
```

파일로 저장하려면:

```bash
kubectl get deploy nginx -o yaml > deploy.yaml
```

이렇게 하면 현재 클러스터에 있는 리소스를 YAML 형태로 뽑을 수 있다.

다만 주의할 점이 있다.
기존 리소스를 `get -o yaml`로 뽑으면 불필요한 필드가 많이 포함된다.

```text
uid
resourceVersion
managedFields
creationTimestamp
status
```

그래서 단순 참고용으로는 좋지만, 그대로 수정해서 apply할 때는 지저분할 수 있다.

시험장에서는 가능하면 아래 방식이 더 깔끔하다.

```bash
kubectl create deployment nginx --image=nginx --dry-run=client -o yaml > deploy.yaml
```

즉, 기존 리소스를 뽑는 용도와 새 YAML을 만드는 용도를 구분해야 한다.

---

## 6. dry-run=client와 -o yaml 조합이 핵심이다

CKA에서 가장 중요한 조합 중 하나가 이거다.

```bash
--dry-run=client -o yaml
```

뜻은 간단하다.

```text
실제로 만들지는 말고
만들 YAML만 출력해줘
```

Pod YAML 만들기:

```bash
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml
```

Deployment YAML 만들기:

```bash
kubectl create deployment nginx --image=nginx --dry-run=client -o yaml > deploy.yaml
```

Service YAML 만들기:

```bash
kubectl expose deployment nginx \
  --port=80 \
  --target-port=80 \
  --dry-run=client -o yaml > svc.yaml
```

ConfigMap YAML 만들기:

```bash
kubectl create configmap app-config \
  --from-literal=APP_MODE=prod \
  --dry-run=client -o yaml > configmap.yaml
```

Secret YAML 만들기:

```bash
kubectl create secret generic app-secret \
  --from-literal=password=1234 \
  --dry-run=client -o yaml > secret.yaml
```

이걸 할 줄 알면 YAML을 처음부터 다 안 외워도 된다.

```text
kubectl로 기본 뼈대를 만든다
→ vi로 연다
→ 문제 조건만 추가한다
→ apply 한다
```

---

## 7. run은 Pod 만들 때 쓴다

Pod 하나를 빠르게 만들고 싶으면 `kubectl run`을 쓴다.

```bash
kubectl run nginx --image=nginx
```

명령어를 실행하는 임시 Pod가 필요할 때도 자주 쓴다.

```bash
kubectl run tmp-shell --rm -it --image=busybox -- sh
```

curl 테스트용 Pod를 만들고 싶으면:

```bash
kubectl run curlpod --image=curlimages/curl -it --rm -- sh
```

CKA에서 Service DNS 테스트를 할 때 이런 식으로 쓸 수 있다.

```bash
curl nginx-svc.default.svc.cluster.local
```

다만 `kubectl run`은 기본적으로 Pod 생성에 가깝다.
Deployment를 만들고 싶으면 `create deployment`를 쓰는 게 더 명확하다.

---

## 8. create deployment는 Deployment 만들 때 쓴다

Deployment 기본 YAML을 만들 때는 이 명령어가 빠르다.

```bash
kubectl create deployment nginx --image=nginx
```

YAML만 만들려면:

```bash
kubectl create deployment nginx \
  --image=nginx \
  --dry-run=client -o yaml > deploy.yaml
```

replicas를 바로 지정하고 싶으면:

```bash
kubectl create deployment nginx \
  --image=nginx \
  --replicas=3 \
  --dry-run=client -o yaml > deploy.yaml
```

그 다음 적용한다.

```bash
kubectl apply -f deploy.yaml
```

확인한다.

```bash
kubectl get deploy
kubectl get pods
```

---

## 9. expose는 Service 만들 때 쓴다

Deployment를 Service로 노출하고 싶으면 `kubectl expose`를 쓴다.

```bash
kubectl expose deployment nginx --port=80 --target-port=80
```

NodePort Service YAML로 만들고 싶으면:

```bash
kubectl expose deployment nginx \
  --type=NodePort \
  --port=80 \
  --target-port=80 \
  --dry-run=client -o yaml > svc.yaml
```

이후 필요하면 `nodePort`를 직접 추가한다.

```yaml
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30080
```

Service 문제에서 자주 헷갈리는 건 이거다.

```text
port: Service가 받는 포트
targetPort: Pod 컨테이너로 전달할 포트
nodePort: 외부에서 NodeIP:nodePort로 들어오는 포트
```

---

## 10. edit은 작은 수정에 좋다

리소스를 빠르게 수정하고 싶으면 `kubectl edit`을 쓴다.

```bash
kubectl edit deployment nginx
kubectl edit svc nginx-svc
kubectl edit cm nginx-config -n nginx-static
```

예를 들어 ConfigMap 하나 고치는 문제라면:

```bash
kubectl edit configmap nginx-config -n nginx-static
```

이게 제일 빠를 수 있다.

하지만 복잡한 수정이면 파일로 빼는 게 좋다.

```bash
kubectl get deploy nginx -o yaml > deploy.yaml
vi deploy.yaml
kubectl apply -f deploy.yaml
```

정리하면:

```text
작은 수정 → kubectl edit
큰 수정 → yaml 파일로 저장 후 수정
새 리소스 생성 → dry-run=client -o yaml
```

---

## 11. rollout은 Deployment 변경 확인용이다

Deployment 이미지를 바꾸거나 재시작하면 rollout 상태를 확인해야 한다.

이미지 변경:

```bash
kubectl set image deployment/nginx nginx=nginx:1.25
```

rollout 상태 확인:

```bash
kubectl rollout status deployment/nginx
```

히스토리 확인:

```bash
kubectl rollout history deployment/nginx
```

롤백:

```bash
kubectl rollout undo deployment/nginx
```

ConfigMap을 바꿨는데 Pod에 반영이 안 되는 경우, Deployment를 재시작할 수도 있다.

```bash
kubectl rollout restart deployment/nginx
```

namespace가 있으면:

```bash
kubectl rollout restart deployment/nginx -n nginx-static
```

CKA에서 Nginx 설정 ConfigMap을 바꾼 뒤 적용이 안 되면, Deployment 재시작이나 Pod 재생성이 필요할 수 있다.

---

## 12. logs와 exec는 문제 검증용이다

Pod 안에서 로그를 봐야 하면:

```bash
kubectl logs <pod-name>
```

이전 컨테이너 로그를 봐야 하면:

```bash
kubectl logs <pod-name> --previous
```

컨테이너가 여러 개면:

```bash
kubectl logs <pod-name> -c <container-name>
```

Pod 안에 들어가야 하면:

```bash
kubectl exec -it <pod-name> -- sh
```

bash가 있으면:

```bash
kubectl exec -it <pod-name> -- bash
```

명령어 하나만 실행할 수도 있다.

```bash
kubectl exec <pod-name> -- curl localhost
kubectl exec <pod-name> -- cat /etc/nginx/nginx.conf
```

CKA에서 검증은 정말 중요하다.

```text
리소스를 만들었다
→ 끝이 아니다

정상 동작하는지 확인했다
→ 이게 끝이다
```

---

## 13. config 명령어는 context 확인용이다

시험장에서는 여러 클러스터 context가 주어질 수 있다.
이때 `kubectl config` 명령어를 쓴다.

현재 context 확인:

```bash
kubectl config current-context
```

context 목록 확인:

```bash
kubectl config get-contexts
```

context 변경:

```bash
kubectl config use-context <context-name>
```

짧게 쓰면:

```bash
kubectl config use-context k8s
```

CKA에서는 문제마다 context를 바꾸라는 지시가 나올 수 있다.
그걸 놓치면 아무리 YAML을 잘 작성해도 엉뚱한 클러스터에 적용하게 된다.

문제를 풀기 전에 항상 확인하는 습관이 좋다.

```bash
kubectl config current-context
```

---

## 14. explain은 필드가 헷갈릴 때 쓴다

YAML 필드가 헷갈리면 `kubectl explain`을 쓸 수 있다.

```bash
kubectl explain pod
kubectl explain pod.spec
kubectl explain pod.spec.containers
kubectl explain deployment.spec
kubectl explain svc.spec
```

예를 들어 Pod의 tolerations 위치가 헷갈리면:

```bash
kubectl explain pod.spec.tolerations
```

리소스 필드 구조를 자세히 보고 싶으면:

```bash
kubectl explain pod --recursive
```

공식문서를 찾는 것도 좋지만, 필드 위치가 헷갈릴 때는 `kubectl explain`이 더 빠를 때가 많다.

```text
공식문서 → 예제 찾기 좋음
kubectl explain → 필드 위치 확인하기 좋음
```

---

## 15. label과 selector는 get에서 자주 쓴다

라벨 확인:

```bash
kubectl get pods --show-labels
```

특정 라벨만 조회:

```bash
kubectl get pods -l app=nginx
```

라벨 추가:

```bash
kubectl label pod nginx app=nginx
```

라벨 수정:

```bash
kubectl label pod nginx app=web --overwrite
```

Service가 Pod를 못 잡는 경우에는 거의 selector 문제다.

확인 순서:

```bash
kubectl get pods --show-labels
kubectl describe svc nginx-svc
kubectl get endpoints nginx-svc
```

`endpoints`가 비어 있으면 Service selector와 Pod label이 안 맞는 경우가 많다.

```text
Service selector: app=nginx
Pod label: app=web
```

이러면 연결이 안 된다.

---

## 16. delete는 리소스 정리용이다

리소스 삭제:

```bash
kubectl delete pod nginx
kubectl delete deployment nginx
kubectl delete svc nginx-svc
kubectl delete cm app-config
```

파일 기준 삭제:

```bash
kubectl delete -f pod.yaml
```

namespace 기준 삭제:

```bash
kubectl delete pod nginx -n default
```

강제 삭제가 필요한 경우도 있지만, 시험에서는 무작정 강제 삭제보다 일반 삭제를 먼저 쓰는 게 안전하다.

---

## 17. Quick Reference를 시험장에서 쓰는 실제 흐름

예를 들어 이런 문제가 나왔다고 하자.

```text
nginx 이미지를 사용하는 Deployment를 만들고,
replica를 3개로 설정하고,
NodePort Service로 노출하라.
```

시험장에서 흐름은 이렇게 간다.

### 1단계. Deployment YAML 생성

```bash
kubectl create deployment nginx \
  --image=nginx \
  --replicas=3 \
  --dry-run=client -o yaml > deploy.yaml
```

### 2단계. 적용

```bash
kubectl apply -f deploy.yaml
```

### 3단계. Service YAML 생성

```bash
kubectl expose deployment nginx \
  --type=NodePort \
  --port=80 \
  --target-port=80 \
  --dry-run=client -o yaml > svc.yaml
```

### 4단계. 필요하면 nodePort 수정

```bash
vi svc.yaml
```

```yaml
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30080
```

### 5단계. 적용

```bash
kubectl apply -f svc.yaml
```

### 6단계. 검증

```bash
kubectl get deploy
kubectl get pods -o wide
kubectl get svc
kubectl get endpoints
curl localhost:30080
```

이게 CKA식 풀이 흐름이다.

---

## 18. Quick Reference에서 내가 자주 찾을 키워드

브라우저 검색이나 문서 내 검색으로 아래 키워드를 자주 찾으면 된다.

```text
run
create deployment
expose
dry-run
output
label
rollout
logs
exec
config
context
namespace
```

특히 `Ctrl + F` 또는 브라우저 검색창으로 `dry-run`, `rollout`, `expose`를 바로 찾는 연습을 해두면 좋다.

---

## 19. 자주 쓰는 명령어 모음

```bash
# 현재 context 확인
kubectl config current-context

# context 목록
kubectl config get-contexts

# context 변경
kubectl config use-context <context-name>

# 전체 namespace Pod 확인
kubectl get pods -A

# 특정 namespace 확인
kubectl get pods -n <namespace>

# 자세한 정보 확인
kubectl describe pod <pod-name>

# Pod YAML 생성
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml

# Deployment YAML 생성
kubectl create deployment nginx --image=nginx --dry-run=client -o yaml > deploy.yaml

# Service YAML 생성
kubectl expose deployment nginx --port=80 --target-port=80 --dry-run=client -o yaml > svc.yaml

# ConfigMap YAML 생성
kubectl create configmap app-config --from-literal=key=value --dry-run=client -o yaml > cm.yaml

# Secret YAML 생성
kubectl create secret generic app-secret --from-literal=password=1234 --dry-run=client -o yaml > secret.yaml

# 적용
kubectl apply -f file.yaml

# 삭제
kubectl delete -f file.yaml

# 로그 확인
kubectl logs <pod-name>

# Pod 내부 명령 실행
kubectl exec -it <pod-name> -- sh

# rollout 확인
kubectl rollout status deployment/<deployment-name>

# rollout 재시작
kubectl rollout restart deployment/<deployment-name>

# 롤백
kubectl rollout undo deployment/<deployment-name>
```

---

## 20. 결론

`kubectl Quick Reference`는 CKA에서 단순한 참고 문서가 아니다.
시험장에서 명령어를 빠르게 꺼내 쓰기 위한 **작업 도구**다.

CKA 준비를 할 때는 명령어를 무작정 외우기보다, 아래 흐름을 손에 익히는 게 중요하다.

```text
Quick Reference에서 명령어 찾기
→ dry-run으로 YAML 만들기
→ 문제 조건에 맞게 수정하기
→ apply 하기
→ get / describe / logs / exec로 검증하기
```

결국 CKA에서 중요한 건 “명령어를 다 외웠는가”가 아니라:

```text
필요한 명령어를 빠르게 찾을 수 있는가
YAML을 빠르게 만들 수 있는가
문제 조건에 맞게 수정할 수 있는가
정상 동작을 검증할 수 있는가
```

이다.

`kubectl Quick Reference`를 잘 쓰면, CKA 문제를 풀 때 매번 처음부터 외워서 쓰는 부담이 줄어든다.
시험장에서 모르는 옵션이 나와도 당황하지 않고, 공식문서에서 찾아서 바로 적용할 수 있게 된다.

[1]: https://kubernetes.io/docs/reference/kubectl/quick-reference/?utm_source=chatgpt.com "kubectl Quick Reference"
[2]: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_describe/?utm_source=chatgpt.com "kubectl describe"
