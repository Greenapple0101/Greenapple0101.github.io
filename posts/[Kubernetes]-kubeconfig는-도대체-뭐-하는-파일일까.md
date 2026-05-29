---
title: "[Kubernetes] kubeconfig는 도대체 뭐 하는 파일일까?"
source: ""
published: "2026-05-29T17:47:37.000Z"
---

쿠버네티스를 쓰다 보면 이런 명령어를 계속 치게 된다.

```bash
kubectl get pods
kubectl get nodes
kubectl apply -f deployment.yaml
```

그런데 생각해보면 이상하다.

`kubectl`은 어떻게 내가 접속해야 할 Kubernetes 클러스터를 알고 있을까?

```text
내 클러스터 주소가 뭔지
인증서는 어디 있는지
나는 어떤 사용자로 접근하는지
어떤 namespace를 기본으로 쓸지
```

이 정보를 담고 있는 파일이 바로 **kubeconfig**다.

한 줄로 말하면 이렇다.

> kubeconfig는 `kubectl`이 Kubernetes API Server에 접속하기 위해 사용하는 접속 설정 파일이다.

---

## 1. kubeconfig란?

`kubeconfig`는 Kubernetes 클러스터 접속 정보를 담고 있는 설정 파일이다.

보통 기본 위치는 여기다.

```bash
~/.kube/config
```

즉, 내가 터미널에서 `kubectl get pods`를 치면 `kubectl`은 기본적으로 이 파일을 읽는다.

```text
kubectl 명령 실행
        ↓
~/.kube/config 읽기
        ↓
어느 클러스터에 접속할지 확인
        ↓
어떤 사용자 인증정보를 쓸지 확인
        ↓
Kubernetes API Server에 요청
```

그래서 kubeconfig는 단순 설정 파일이 아니라, **클러스터 접속증** 같은 역할을 한다.

---

## 2. kubeconfig에는 뭐가 들어있을까?

kubeconfig에는 크게 세 가지 정보가 들어있다.

```text
clusters
users
contexts
```

처음 보면 이름이 헷갈리는데, 이렇게 보면 된다.

```text
clusters
→ 어디로 접속할지

users
→ 누구로 접속할지

contexts
→ 어떤 클러스터에 어떤 사용자로 접속할지 묶어둔 설정
```

즉, `cluster`와 `user`를 조합한 것이 `context`다.

---

## 3. 전체 구조 먼저 보기

kubeconfig 파일은 보통 이런 구조다.

```yaml
apiVersion: v1
kind: Config

clusters:
  - name: my-cluster
    cluster:
      server: https://127.0.0.1:6443
      certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0t...

users:
  - name: my-user
    user:
      client-certificate-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0t...
      client-key-data: LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVkt...

contexts:
  - name: my-context
    context:
      cluster: my-cluster
      user: my-user
      namespace: default

current-context: my-context
```

처음 보면 길어 보이지만 핵심은 단순하다.

```text
my-cluster라는 클러스터가 있고
my-user라는 사용자가 있고
my-context는 my-cluster + my-user 조합이다
현재는 my-context를 사용한다
```

---

## 4. clusters: 어디로 접속할지

`clusters`에는 Kubernetes API Server 주소와 인증서 정보가 들어간다.

```yaml
clusters:
  - name: my-cluster
    cluster:
      server: https://127.0.0.1:6443
      certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0t...
```

여기서 중요한 건 `server`다.

```yaml
server: https://127.0.0.1:6443
```

이 주소가 바로 Kubernetes API Server 주소다.

즉, `kubectl`은 이 주소로 요청을 보낸다.

```text
kubectl
  ↓
https://127.0.0.1:6443
  ↓
Kubernetes API Server
```

`certificate-authority-data`는 API Server의 인증서를 검증하기 위한 CA 정보다.

쉽게 말하면 이런 역할이다.

```text
내가 접속하는 API Server가 진짜 믿을 수 있는 서버인지 확인
```

---

## 5. users: 누구로 접속할지

`users`에는 인증 정보가 들어간다.

```yaml
users:
  - name: my-user
    user:
      client-certificate-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0t...
      client-key-data: LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVkt...
```

이 부분은 `kubectl`이 API Server에 요청할 때 **나는 누구인지 증명하기 위해 쓰는 정보**다.

인증 방식은 환경마다 다를 수 있다.

```text
client certificate
token
username/password
exec plugin
cloud provider 인증
```

예를 들어 로컬 실습 환경이나 kubeadm 환경에서는 인증서 기반으로 들어있는 경우가 많고, EKS, GKE, AKS 같은 클라우드 Kubernetes에서는 별도의 인증 플러그인이나 클라우드 CLI와 연결되는 경우가 많다.

중요한 건 이것이다.

```text
users
→ Kubernetes API Server에 내가 누구인지 증명하는 정보
```

---

## 6. contexts: cluster와 user를 묶은 것

`contexts`는 cluster와 user를 연결한 설정이다.

```yaml
contexts:
  - name: my-context
    context:
      cluster: my-cluster
      user: my-user
      namespace: default
```

이걸 문장으로 읽으면 이렇다.

```text
my-context를 사용하면
my-cluster에
my-user로 접속하고
기본 namespace는 default를 사용한다
```

즉, context는 접속 프로필이다.

```text
context = cluster + user + namespace
```

여러 클러스터를 쓰는 사람은 context가 여러 개 있을 수 있다.

```text
dev-cluster-admin
dev-cluster-viewer
prod-cluster-admin
prod-cluster-readonly
```

이렇게 context를 바꿔가며 다른 클러스터나 다른 권한으로 접속할 수 있다.

---

## 7. current-context: 지금 사용할 context

kubeconfig에는 현재 사용할 context가 지정되어 있다.

```yaml
current-context: my-context
```

즉, 내가 그냥 이렇게 명령어를 치면

```bash
kubectl get pods
```

`kubectl`은 `current-context`에 적힌 context를 사용한다.

```text
current-context: my-context
        ↓
my-context 확인
        ↓
my-cluster에 my-user로 접속
        ↓
default namespace 기준으로 pods 조회
```

그래서 현재 내가 어느 클러스터를 보고 있는지 확인하는 것이 중요하다.

운영 클러스터를 보고 있는 줄 모르고 `delete` 명령을 치면 큰일 날 수 있다.

---

## 8. kubeconfig 확인 명령어

현재 kubeconfig 내용을 보려면 이렇게 한다.

```bash
kubectl config view
```

현재 context만 확인하려면 이렇게 한다.

```bash
kubectl config current-context
```

등록된 context 목록은 이렇게 본다.

```bash
kubectl config get-contexts
```

출력은 대략 이런 식이다.

```text
CURRENT   NAME            CLUSTER        AUTHINFO     NAMESPACE
*         dev-context     dev-cluster    dev-user     default
          prod-context    prod-cluster   prod-user    prod
```

여기서 `*` 표시가 현재 사용 중인 context다.

---

## 9. context 바꾸기

다른 context로 바꾸려면 이렇게 한다.

```bash
kubectl config use-context prod-context
```

이제부터 `kubectl`은 `prod-context`를 기준으로 동작한다.

```text
kubectl get pods
        ↓
prod-context 사용
        ↓
prod-cluster에 prod-user로 요청
```

그래서 context 변경은 항상 조심해야 한다.

특히 이런 상황이 위험하다.

```text
dev에서 테스트하던 명령어를
prod context 상태에서 그대로 실행
```

그래서 실무에서는 현재 context를 터미널 프롬프트에 표시해두거나, `kubectx`, `kubens` 같은 도구를 쓰기도 한다.

---

## 10. namespace 기본값 바꾸기

context에는 기본 namespace도 들어갈 수 있다.

현재 context의 기본 namespace를 바꾸려면 이렇게 한다.

```bash
kubectl config set-context --current --namespace=dev
```

이렇게 하면 매번 `-n dev`를 붙이지 않아도 된다.

```bash
kubectl get pods
```

이 명령은 이제 기본적으로 `dev` namespace 기준으로 실행된다.

원래는 이렇게 쳐야 했던 것을

```bash
kubectl get pods -n dev
```

기본 namespace 설정으로 줄일 수 있는 것이다.

현재 context와 namespace를 확인하려면 이렇게 본다.

```bash
kubectl config get-contexts
```

---

## 11. KUBECONFIG 환경변수

기본 kubeconfig 위치는 `~/.kube/config`다.

하지만 다른 파일을 쓰고 싶을 때는 `KUBECONFIG` 환경변수를 사용할 수 있다.

```bash
export KUBECONFIG=/path/to/my-kubeconfig
```

이렇게 하면 `kubectl`은 기본 파일 대신 이 파일을 사용한다.

여러 kubeconfig 파일을 동시에 합쳐서 볼 수도 있다.

```bash
export KUBECONFIG=~/.kube/config:~/Downloads/other-config
kubectl config view --merge
```

Mac/Linux에서는 `:`로 구분한다.

```text
config1:config2
```

Windows에서는 보통 `;`로 구분한다.

```text
config1;config2
```

---

## 12. kubeconfig 병합하기

회사에서 새 클러스터 접속 파일을 받거나, 로컬 실습 클러스터를 새로 만들면 kubeconfig가 여러 개 생길 수 있다.

이때 병합해서 하나로 만들 수 있다.

```bash
KUBECONFIG=~/.kube/config:~/Downloads/new-config \
kubectl config view --merge --flatten > ~/merged-config
```

그다음 기존 config를 백업하고 교체한다.

```bash
cp ~/.kube/config ~/.kube/config.backup
mv ~/merged-config ~/.kube/config
```

여기서 `--flatten`은 외부 파일 참조를 풀어서 하나의 파일 안에 인증서 데이터를 포함시키는 역할을 한다.

실무에서는 kubeconfig 파일을 건드리기 전에 항상 백업하는 게 좋다.

```bash
cp ~/.kube/config ~/.kube/config.backup
```

---

## 13. kubeconfig 안의 base64

kubeconfig를 보면 이런 값이 많이 나온다.

```yaml
certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0t...
client-certificate-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0t...
client-key-data: LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVkt...
```

이 값들은 base64로 인코딩된 인증서나 키 데이터다.

여기서도 중요한 점은 같다.

```text
base64는 암호화가 아니다
```

즉, `client-key-data` 같은 값은 민감한 정보다.

kubeconfig 안에 개인키나 토큰이 들어있으면, 이 파일을 가진 사람이 클러스터에 접근할 수 있다.

그래서 kubeconfig는 절대 함부로 공유하면 안 된다.

---

## 14. kubeconfig는 비밀번호 같은 파일이다

이 부분 진짜 중요하다.

kubeconfig는 단순 설정 파일처럼 보이지만, 실제로는 클러스터 접속 권한을 담고 있다.

특히 이런 정보가 들어있을 수 있다.

```text
client certificate
client key
token
cloud auth exec 설정
API Server 주소
기본 namespace
```

그래서 kubeconfig가 유출되면 이런 일이 생길 수 있다.

```text
누군가 내 권한으로 클러스터 조회
Secret 조회 가능성
Pod 삭제 가능성
Deployment 수정 가능성
운영 장애 발생 가능성
```

물론 실제로 어디까지 가능한지는 해당 user나 ServiceAccount에 부여된 RBAC 권한에 따라 다르다.

하지만 어쨌든 kubeconfig는 민감정보로 다뤄야 한다.

```text
kubeconfig = 클러스터 출입증
```

---

## 15. kubeconfig와 RBAC의 관계

kubeconfig는 접속 정보를 담는다.

RBAC는 접속한 사용자가 어떤 작업을 할 수 있는지 정한다.

둘은 역할이 다르다.

```text
kubeconfig
→ API Server에 누구로 접속할지 알려줌

RBAC
→ 그 사용자가 무엇을 할 수 있는지 판단
```

예를 들어 kubeconfig에 `dev-user` 인증 정보가 있다고 하자.

```text
dev-user로 인증 성공
```

그다음 API Server는 RBAC를 확인한다.

```text
dev-user가 pods를 get 할 수 있는가?
dev-user가 deployments를 delete 할 수 있는가?
dev-user가 secrets를 list 할 수 있는가?
```

즉, 흐름은 이렇게 된다.

```text
kubectl
  ↓
kubeconfig 읽기
  ↓
API Server에 인증 요청
  ↓
Authentication: 너 누구야?
  ↓
Authorization: 이 작업 해도 돼?
  ↓
허용 또는 거부
```

---

## 16. 자주 만나는 에러

### 16.1 kubeconfig 파일이 없을 때

```bash
kubectl get pods
```

했는데 이런 식의 에러가 날 수 있다.

```text
The connection to the server localhost:8080 was refused
```

이건 보통 `kubectl`이 제대로 된 kubeconfig를 못 찾았을 때 자주 본다.

확인할 것:

```bash
ls ~/.kube/config
echo $KUBECONFIG
kubectl config view
```

---

### 16.2 context가 잘못됐을 때

현재 context가 엉뚱한 클러스터를 보고 있을 수 있다.

```bash
kubectl config current-context
kubectl config get-contexts
```

원하는 context로 바꾼다.

```bash
kubectl config use-context 원하는-context명
```

---

### 16.3 namespace가 달라서 리소스가 안 보일 때

Pod가 있는데 안 보이는 것처럼 느껴질 때가 있다.

```bash
kubectl get pods
```

그런데 사실 다른 namespace에 있는 경우가 많다.

전체 namespace에서 확인해보자.

```bash
kubectl get pods -A
```

또는 특정 namespace를 지정한다.

```bash
kubectl get pods -n dev
```

기본 namespace를 바꿀 수도 있다.

```bash
kubectl config set-context --current --namespace=dev
```

---

### 16.4 권한이 없을 때

접속은 됐는데 권한이 없으면 이런 식의 에러가 난다.

```text
Error from server (Forbidden): pods is forbidden
```

이건 kubeconfig 문제가 아니라 RBAC 문제일 가능성이 크다.

확인해보자.

```bash
kubectl auth can-i get pods -n dev
```

특정 사용자나 ServiceAccount 기준으로도 확인할 수 있다.

```bash
kubectl auth can-i get pods \
  --as=system:serviceaccount:dev:app-sa \
  -n dev
```

---

## 17. 실습할 때 자주 쓰는 명령어 정리

```bash
# kubeconfig 전체 보기
kubectl config view

# 민감정보까지 포함해서 보기
kubectl config view --raw

# 현재 context 보기
kubectl config current-context

# context 목록 보기
kubectl config get-contexts

# context 변경
kubectl config use-context <context-name>

# 현재 context의 기본 namespace 변경
kubectl config set-context --current --namespace=<namespace>

# 특정 kubeconfig 파일 사용
KUBECONFIG=/path/to/config kubectl get nodes

# 여러 kubeconfig 병합해서 보기
KUBECONFIG=config1:config2 kubectl config view --merge

# 현재 권한 확인
kubectl auth can-i get pods -n dev
```

---

## 18. kubeconfig를 읽는 방식

kubeconfig를 볼 때는 위에서부터 전부 외우려고 하지 말고, 이 질문 세 개만 잡으면 된다.

```text
1. clusters
→ 어디로 접속하지?

2. users
→ 누구로 접속하지?

3. contexts
→ 어떤 cluster와 user 조합을 쓰지?
```

그리고 마지막으로 이것을 본다.

```text
current-context
→ 지금 실제로 쓰는 설정은 뭐지?
```

즉, kubeconfig 분석 순서는 이렇게 잡으면 된다.

```text
current-context 확인
        ↓
contexts에서 해당 context 찾기
        ↓
그 context가 가리키는 cluster 확인
        ↓
그 context가 가리키는 user 확인
        ↓
server 주소와 인증정보 확인
```

---

## 19. 정리

kubeconfig는 `kubectl`이 Kubernetes 클러스터에 접속하기 위해 사용하는 설정 파일이다.

기본 위치는 보통 다음과 같다.

```bash
~/.kube/config
```

kubeconfig의 핵심 구성은 세 가지다.

```text
clusters
→ 접속할 Kubernetes API Server 정보

users
→ 인증에 사용할 사용자 정보

contexts
→ cluster와 user와 namespace를 묶은 접속 프로필
```

현재 사용 중인 context는 `current-context`로 정해진다.

```text
current-context
→ 지금 kubectl이 사용할 접속 설정
```

마지막으로 이렇게 기억하면 된다.

> kubeconfig는 kubectl의 내비게이션이다. 어느 클러스터로 갈지, 누구로 들어갈지, 어느 namespace를 기본으로 볼지를 알려주는 접속 설정 파일이다. 다만 인증서와 토큰이 들어있을 수 있으므로 비밀번호처럼 조심해서 다뤄야 한다.
