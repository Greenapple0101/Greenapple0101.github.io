---
title: "[Kubernetes] kubectl config는 도대체 뭐고, CKA에서 언제 쓰는 걸까?"
source: "https://velog.io/@yorange50/Kubernetes-kubectl-config는-도대체-뭐고-CKA에서-언제-쓰는-걸까"
published: "2026-05-27T04:36:31.530Z"
tags: ""
backup_date: "2026-05-29T14:52:52.713890"
---

CKA 공부하다 보면 이런 명령어가 나온다.

```bash
kubectl config view
kubectl config get-contexts
kubectl config current-context
kubectl config use-context my-cluster-name
kubectl config set-context --current --namespace=ggckad-s2
```

처음 보면 느낌이 이렇다.

```text
config?
context?
cluster?
user?
namespace?
이걸 왜 kubectl에서 설정하지?
```

근데 이건 생각보다 단순하다.

`kubectl config`는 **kubectl이 어느 쿠버네티스 클러스터에 접속할지 정하는 설정 명령어**다.

---

# 1. kubectl은 혼자서 클러스터를 아는 게 아니다

우리가 평소에 이렇게 입력한다.

```bash
kubectl get pods
```

그러면 kubectl이 알아서 Kubernetes API Server에 요청을 보낸다.

그런데 여기서 중요한 질문이 생긴다.

```text
kubectl은 어느 클러스터에 요청을 보내는 걸까?
kubectl은 어떤 사용자 권한으로 요청을 보내는 걸까?
kubectl은 어느 namespace를 기본으로 보는 걸까?
```

이 정보를 저장해둔 파일이 바로 **kubeconfig**다.

보통 위치는 여기다.

```bash
~/.kube/config
```

즉 kubectl은 명령을 실행할 때 이 파일을 보고 판단한다.

```text
kubectl 명령 실행
  ↓
~/.kube/config 확인
  ↓
현재 context 확인
  ↓
cluster / user / namespace 결정
  ↓
Kubernetes API Server에 요청
```

---

# 2. kubeconfig 안에는 뭐가 들어있을까?

kubeconfig에는 크게 3가지가 있다.

```text
clusters
users
contexts
```

## clusters

`clusters`는 **접속할 쿠버네티스 클러스터 정보**다.

예를 들면 이런 정보가 들어간다.

```text
클러스터 이름
API Server 주소
CA 인증서 정보
```

쉽게 말하면:

```text
어느 쿠버네티스 서버로 갈 건데?
```

에 대한 답이다.

---

## users

`users`는 **그 클러스터에 접속할 사용자 인증 정보**다.

예를 들면 이런 것들이 들어갈 수 있다.

```text
client certificate
client key
token
username/password
```

쉽게 말하면:

```text
누구 권한으로 접속할 건데?
```

에 대한 답이다.

---

## contexts

`contexts`는 제일 중요하다.

context는 다음 3개를 묶어둔 프로필이다.

```text
cluster + user + namespace
```

예를 들면 이런 느낌이다.

```text
context 이름: dev-admin
cluster: dev-cluster
user: admin-user
namespace: default
```

이 뜻은 다음과 같다.

```text
dev-cluster에
admin-user 권한으로
default namespace를 기본으로 보고 접속하겠다
```

즉 context는 kubectl의 현재 작업 위치 같은 것이다.

---

# 3. 그래서 current-context가 중요하다

현재 kubectl이 어느 context를 보고 있는지 확인하는 명령어가 있다.

```bash
kubectl config current-context
```

예를 들어 결과가 이렇게 나온다고 하자.

```bash
kubernetes-admin@kubernetes
```

그러면 지금 kubectl은 `kubernetes-admin@kubernetes`라는 context를 사용 중이라는 뜻이다.

이 상태에서 다음 명령을 치면:

```bash
kubectl get pods
```

kubectl은 현재 context에 설정된 cluster, user, namespace 기준으로 pod를 조회한다.

---

# 4. context 목록 보기

사용 가능한 context 목록을 보고 싶으면 다음 명령어를 쓴다.

```bash
kubectl config get-contexts
```

출력 예시는 대충 이런 식이다.

```text
CURRENT   NAME                          CLUSTER      AUTHINFO           NAMESPACE
*         kubernetes-admin@kubernetes   kubernetes   kubernetes-admin   default
          dev-context                   dev-cluster  dev-user           dev
          prod-context                  prod-cluster prod-user          prod
```

여기서 `*` 표시가 붙은 것이 현재 사용 중인 context다.

```text
* = 지금 kubectl이 바라보는 대상
```

context 이름만 보고 싶으면 이렇게 쓴다.

```bash
kubectl config get-contexts -o name
```

---

# 5. context 바꾸기

다른 context로 바꾸고 싶으면 이렇게 한다.

```bash
kubectl config use-context my-cluster-name
```

예를 들어:

```bash
kubectl config use-context dev-context
```

이제부터는 kubectl이 `dev-context`를 기준으로 동작한다.

```bash
kubectl get pods
```

이 명령을 치면 이제 `dev-context`에 연결된 클러스터의 pod를 조회한다.

---

# 6. namespace 고정하기

CKA에서 진짜 자주 쓰는 게 이거다.

```bash
kubectl config set-context --current --namespace=ggckad-s2
```

이 명령은 현재 context의 기본 namespace를 `ggckad-s2`로 바꾼다.

원래는 이렇게 쳐야 했다.

```bash
kubectl get pods -n ggckad-s2
kubectl get svc -n ggckad-s2
kubectl get deploy -n ggckad-s2
```

근데 namespace를 고정하면 이렇게 칠 수 있다.

```bash
kubectl get pods
kubectl get svc
kubectl get deploy
```

왜냐하면 kubectl이 기본 namespace를 이미 알고 있기 때문이다.

시험에서는 namespace 실수가 진짜 많이 난다.

```bash
kubectl get pods
```

했는데 아무것도 안 나와서 당황한다.

알고 보니 리소스는 `default`가 아니라 `monitoring`, `autoscale`, `nginx-static` 같은 namespace에 있다.

그래서 문제에서 namespace를 주면, 아예 처음에 박아두는 게 좋다.

```bash
kubectl config set-context --current --namespace=<문제에서 준 namespace>
```

---

# 7. kubectl config view는 뭐냐

```bash
kubectl config view
```

이 명령어는 현재 kubeconfig 내용을 보여준다.

즉 이런 것들을 볼 수 있다.

```text
clusters
users
contexts
current-context
```

다만 민감한 인증 정보는 일부 가려져서 나온다.

예를 들어 인증서 데이터나 토큰 같은 정보는 그대로 안 보일 수 있다.

---

# 8. --raw는 뭐냐

```bash
kubectl config view --raw
```

`--raw`를 붙이면 숨겨진 인증 정보까지 더 원본에 가깝게 보여준다.

예를 들어 certificate data, token 같은 민감한 값이 노출될 수 있다.

그래서 실무에서는 조심해야 한다.

```text
kubectl config view        = 안전하게 보기
kubectl config view --raw  = 민감정보까지 포함해서 보기
```

CKA 초반 학습에서는 `--raw`를 깊게 외울 필요는 없다.

다만 문제에서 인증서 값이나 user 정보를 추출하라고 하면 나올 수 있다.

---

# 9. jsonpath는 왜 같이 나오냐

이런 명령어도 있다.

```bash
kubectl config view -o jsonpath='{.users[*].name}'
```

이건 kubeconfig 결과에서 원하는 값만 뽑는 명령어다.

예를 들어 user 이름만 보고 싶을 때 쓴다.

```bash
kubectl config view -o jsonpath='{.users[*].name}'
```

특정 user의 password를 뽑는 예시는 이런 식이다.

```bash
kubectl config view -o jsonpath='{.users[?(@.name == "e2e")].user.password}'
```

특정 user의 client certificate를 뽑고 base64 디코딩하는 예시는 이렇게 생겼다.

```bash
kubectl config view --raw -o jsonpath='{.users[?(.name == "e2e")].user.client-certificate-data}' | base64 -d
```

근데 처음 공부할 때는 이렇게 보면 된다.

```text
jsonpath = kubectl 결과에서 원하는 필드만 뽑는 방법
```

CKA에서는 리소스 조회할 때 더 자주 나온다.

예를 들면:

```bash
kubectl get pod nginx -o jsonpath='{.metadata.name}'
kubectl get node node01 -o jsonpath='{.status.nodeInfo.kubeletVersion}'
```

---

# 10. set-cluster는 뭐냐

```bash
kubectl config set-cluster my-cluster-name
```

이건 kubeconfig 안에 cluster 항목을 만들거나 수정하는 명령어다.

더 실무적인 예시는 이런 식이다.

```bash
kubectl config set-cluster my-cluster-name --server=https://1.2.3.4:6443
```

또는 프록시를 설정할 수도 있다.

```bash
kubectl config set-cluster my-cluster-name --proxy-url=my-proxy-url
```

이건 보통 kubeconfig를 직접 구성할 때 쓴다.

CKA에서는 아주 핵심은 아니다.

우리가 보통 시험에서 더 많이 쓰는 건 이미 존재하는 context를 확인하고 바꾸는 것이다.

---

# 11. set-credentials는 뭐냐

```bash
kubectl config set-credentials kubeuser/foo.kubernetes.com \
  --username=kubeuser \
  --password=kubepassword
```

이건 kubeconfig 안에 user 인증 정보를 추가하거나 수정하는 명령어다.

쉽게 말하면:

```text
이 이름의 사용자는 이런 인증 정보로 접속한다
```

를 설정하는 것이다.

하지만 CKA에서 매번 직접 user를 만드는 문제는 config 기본 파트에서는 자주 나오지 않는다.

인증서, RBAC, ServiceAccount 쪽 문제와 연결되면 나올 수 있다.

---

# 12. set-context는 뭐냐

```bash
kubectl config set-context gce --user=cluster-admin --namespace=foo
```

이건 context를 만들거나 수정하는 명령어다.

context는 다시 말해서:

```text
cluster + user + namespace 조합
```

이다.

예를 들어:

```bash
kubectl config set-context gce \
  --cluster=my-cluster \
  --user=cluster-admin \
  --namespace=foo
```

이렇게 하면 `gce`라는 context에 어떤 cluster, user, namespace를 쓸지 지정할 수 있다.

그리고 이 context를 사용하려면:

```bash
kubectl config use-context gce
```

라고 하면 된다.

---

# 13. unset은 뭐냐

```bash
kubectl config unset users.foo
```

이건 kubeconfig에서 특정 항목을 삭제하는 명령어다.

예를 들어 `users.foo`를 삭제하면 `foo`라는 user 설정이 제거된다.

시험에서 자주 쓰는 핵심 명령은 아니지만, kubeconfig 구조를 이해하면 의미는 쉽다.

```text
unset = kubeconfig 안의 특정 설정 삭제
```

---

# 14. alias kx, kn은 왜 쓰냐

공식 문서나 Quick Reference를 보면 이런 alias가 나온다.

```bash
alias kx='f() { [ "$1" ] && kubectl config use-context $1 || kubectl config current-context ; } ; f'
```

이건 context를 빠르게 바꾸거나 확인하는 alias다.

사용 예시:

```bash
kx
```

현재 context 확인.

```bash
kx dev-context
```

`dev-context`로 context 변경.

---

namespace용 alias도 있다.

```bash
alias kn='f() { [ "$1" ] && kubectl config set-context --current --namespace $1 || kubectl config view --minify | grep namespace | cut -d" " -f6 ; } ; f'
```

사용 예시:

```bash
kn
```

현재 namespace 확인.

```bash
kn monitoring
```

현재 context의 기본 namespace를 `monitoring`으로 변경.

다만 CKA에서는 alias를 새로 외우는 것보다 이 명령을 정확히 아는 게 더 중요하다.

```bash
kubectl config set-context --current --namespace=<namespace>
```

---

# 15. CKA에서는 어떤 문제랑 같이 나오나?

`kubectl config`는 단독 문제로도 나올 수 있지만, 보통은 다른 문제를 풀기 전에 환경을 맞추는 용도로 나온다.

## 1. context 변경 문제

문제에서 이런 식으로 나온다.

```text
Set the current context to k8s-cluster-1.
```

또는:

```text
Switch to the correct context before performing the task.
```

이때는 먼저 context 목록을 본다.

```bash
kubectl config get-contexts
```

그리고 문제에서 요구한 context로 바꾼다.

```bash
kubectl config use-context k8s-cluster-1
```

확인한다.

```bash
kubectl config current-context
```

---

## 2. namespace 지정 문제

문제에서 이런 식으로 나온다.

```text
Create a deployment named nginx in the app-team1 namespace.
```

이때 매번 `-n app-team1`을 붙여도 된다.

```bash
kubectl create deployment nginx --image=nginx -n app-team1
```

하지만 문제를 풀기 전에 namespace를 고정해도 된다.

```bash
kubectl config set-context --current --namespace=app-team1
```

그러면 이후 명령어를 짧게 칠 수 있다.

```bash
kubectl create deployment nginx --image=nginx
kubectl get pods
```

주의할 점은 문제마다 namespace가 바뀔 수 있다는 것이다.

문제 넘어갈 때 namespace를 잘 확인해야 한다.

---

## 3. Service, ConfigMap, Secret 생성 문제

예를 들어 이런 문제다.

```text
Create a ConfigMap named app-config in the dev namespace.
```

풀이 방법 1:

```bash
kubectl create configmap app-config \
  --from-literal=APP_MODE=production \
  -n dev
```

풀이 방법 2:

```bash
kubectl config set-context --current --namespace=dev

kubectl create configmap app-config \
  --from-literal=APP_MODE=production
```

namespace를 고정해두면 명령어가 짧아진다.

---

## 4. HPA 문제

예를 들어 이런 문제다.

```text
Create a HorizontalPodAutoscaler named apache-server in the autoscale namespace.
```

이럴 때 namespace를 먼저 맞출 수 있다.

```bash
kubectl config set-context --current --namespace=autoscale
```

그다음 HPA를 만들거나 yaml을 적용한다.

```bash
kubectl apply -f hpa.yaml
```

또는 확인할 때도 편하다.

```bash
kubectl get hpa
kubectl describe hpa apache-server
```

원래는 이렇게 해야 한다.

```bash
kubectl get hpa -n autoscale
kubectl describe hpa apache-server -n autoscale
```

---

## 5. Ingress 문제

예를 들어 이런 문제다.

```text
Create an Ingress resource in the nginx-static namespace.
```

먼저 namespace를 고정한다.

```bash
kubectl config set-context --current --namespace=nginx-static
```

그다음 리소스를 확인한다.

```bash
kubectl get pod
kubectl get svc
kubectl get ingress
```

Ingress 문제는 Service 이름과 port를 찾아야 하는 경우가 많아서 namespace를 맞춰두면 실수를 줄일 수 있다.

---

## 6. NetworkPolicy 문제

NetworkPolicy도 namespace가 중요하다.

```text
Create a NetworkPolicy in the payroll namespace.
```

이럴 때:

```bash
kubectl config set-context --current --namespace=payroll
```

그다음 pod label을 확인한다.

```bash
kubectl get pods --show-labels
```

yaml을 작성하고 적용한다.

```bash
kubectl apply -f netpol.yaml
```

NetworkPolicy는 namespace를 잘못 잡으면 아예 엉뚱한 곳에 정책을 만들 수 있다.

---

## 7. Troubleshooting 문제

트러블슈팅 문제에서도 context와 namespace 확인은 기본이다.

예를 들어:

```text
A pod is not running in the monitoring namespace. Fix the issue.
```

바로 확인한다.

```bash
kubectl config set-context --current --namespace=monitoring
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

트러블슈팅에서는 namespace 잘못 보고 있으면 처음부터 길을 잃는다.

---

# 16. 시험장에서 config 관련 루틴

문제를 받으면 먼저 이렇게 생각하면 된다.

```text
1. context 맞나?
2. namespace 맞나?
3. 그다음 리소스 작업
```

명령어 루틴은 이 정도면 충분하다.

```bash
kubectl config get-contexts
kubectl config current-context
kubectl config use-context <context-name>
kubectl config set-context --current --namespace=<namespace>
```

확인용:

```bash
kubectl get ns
kubectl get pods
```

---

# 17. config 명령어 우선순위

처음부터 전부 외울 필요 없다.

우선순위는 이렇게 잡으면 된다.

## 1순위: 무조건 알아야 함

```bash
kubectl config get-contexts
kubectl config current-context
kubectl config use-context <context-name>
kubectl config set-context --current --namespace=<namespace>
```

CKA에서 바로 쓴다.

---

## 2순위: 알면 좋음

```bash
kubectl config view
kubectl config get-contexts -o name
kubectl config view --minify
```

현재 설정을 확인하거나 현재 context만 보고 싶을 때 쓴다.

---

## 3순위: 나중에 봐도 됨

```bash
kubectl config view --raw
kubectl config set-cluster
kubectl config set-credentials
kubectl config unset
kubectl config view -o jsonpath='...'
```

kubeconfig를 직접 수정하거나 인증 정보를 추출하는 쪽이다.

처음 CKA 준비할 때는 너무 깊게 붙잡지 않아도 된다.

---

# 18. 한 줄 정리

`kubectl config`는 kubectl의 접속 설정을 관리하는 명령어다.

```text
cluster = 어느 쿠버네티스 클러스터?
user = 어떤 사용자 권한?
namespace = 어느 작업 공간?
context = cluster + user + namespace 묶음
```

CKA에서 가장 중요한 사용법은 이거다.

```bash
kubectl config get-contexts
kubectl config use-context <context-name>
kubectl config set-context --current --namespace=<namespace>
```

즉, `kubectl config`는 문제를 직접 푸는 명령이라기보다 **문제를 풀기 전에 내가 올바른 클러스터와 namespace를 보고 있는지 맞추는 명령어**다.

시험장에서는 이 감각이면 된다.

```text
문제 풀기 전:
내가 지금 어디 보고 있지?

문제 푸는 중:
namespace 실수 안 했나?

문제 푼 후:
원하는 namespace에 리소스가 생겼나?
```

그래서 `config`는 어렵게 보면 인증서, user, cluster, context가 다 얽힌 설정 파일이지만, CKA 관점에서는 일단 이렇게 이해하면 충분하다.

```text
kubectl의 현재 작업 위치를 정하는 도구
```
