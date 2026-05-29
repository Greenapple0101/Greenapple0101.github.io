---
title: "[Kubernetes] ServiceAccount는 왜 필요할까?"
source: ""
published: "2026-05-29T17:36:10.000Z"
---

쿠버네티스에서 권한 관리를 공부하다 보면 `User`, `Role`, `RoleBinding`, `ClusterRole`, `ClusterRoleBinding` 같은 개념이 나온다. 그중에서 처음에 제일 애매하게 느껴지는 게 `ServiceAccount`다.

이름만 보면 그냥 서비스용 계정 같은데, 정확히 어디에 쓰이는지 헷갈린다.

간단히 말하면 이렇다.

```text
User
→ 사람이 Kubernetes API에 접근할 때 사용하는 주체

ServiceAccount
→ Pod나 애플리케이션이 Kubernetes API에 접근할 때 사용하는 주체
```

즉, `ServiceAccount`는 **사람이 아니라 프로그램을 위한 계정**이다.

---

## 1. ServiceAccount란?

`ServiceAccount`는 쿠버네티스 안에서 동작하는 Pod가 Kubernetes API Server에 접근할 때 사용하는 계정이다.

예를 들어 사람이 직접 명령어를 치면 보통 이런 구조다.

```bash
kubectl get pods
```

```text
사람
  ↓
kubectl
  ↓
Kubernetes API Server
```

이때 사람은 보통 kubeconfig, 인증서, 토큰, 클라우드 IAM 등을 통해 인증된다.

그런데 Pod 안에서 실행 중인 애플리케이션이 API Server에 접근해야 하는 경우도 있다.

```text
Pod 내부 애플리케이션
  ↓
Kubernetes API Server
```

이때 사용하는 계정이 바로 `ServiceAccount`다.

---

## 2. 왜 Pod가 API Server에 접근해야 할까?

처음에는 이런 생각이 든다.

> Pod는 그냥 컨테이너 실행하는 거 아닌가?
> 왜 API Server에 접근하지?

그런데 쿠버네티스에서 동작하는 여러 도구들은 클러스터 상태를 계속 조회하거나 리소스를 수정해야 한다.

예를 들어 이런 경우다.

```text
Argo CD
→ Deployment, Pod, Service 상태를 조회하고 배포 상태를 동기화

Prometheus
→ Pod, Service, Endpoint 정보를 조회해서 모니터링 대상 탐색

Jenkins
→ Kubernetes에 Deployment 생성 또는 업데이트

cert-manager
→ Certificate, Secret, Ingress 등을 보고 인증서 발급 자동화

ExternalDNS
→ Ingress나 Service를 보고 DNS 레코드 자동 생성
```

이런 도구들은 전부 Kubernetes API Server와 통신해야 한다.

그런데 아무 권한 없이 API Server에 접근하게 할 수는 없다.
그래서 각 Pod에 ServiceAccount를 붙이고, 그 ServiceAccount에 필요한 권한만 부여한다.

---

## 3. 기본 ServiceAccount

쿠버네티스에서는 네임스페이스를 만들면 기본적으로 `default`라는 ServiceAccount가 생성된다.

확인해보자.

```bash
kubectl get serviceaccount
```

또는 줄여서 이렇게도 쓸 수 있다.

```bash
kubectl get sa
```

결과는 대략 이런 식이다.

```text
NAME      SECRETS   AGE
default   0         10d
```

여기서 `sa`는 `serviceaccount`의 줄임말이다.

```text
serviceaccount = sa
```

Pod를 만들 때 별도로 ServiceAccount를 지정하지 않으면 자동으로 `default` ServiceAccount가 사용된다.

즉, 아래 Pod는 ServiceAccount를 따로 지정하지 않았다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
    - name: nginx
      image: nginx
```

하지만 실제로는 해당 네임스페이스의 `default` ServiceAccount를 사용한다.

```text
nginx-pod
  ↓
default ServiceAccount 사용
```

---

## 4. ServiceAccount 직접 만들기

ServiceAccount는 YAML로 만들 수 있다.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
  namespace: dev
```

적용한다.

```bash
kubectl apply -f serviceaccount.yaml
```

명령어로 바로 만들 수도 있다.

```bash
kubectl create serviceaccount app-sa -n dev
```

생성 확인은 이렇게 한다.

```bash
kubectl get sa -n dev
```

결과는 이런 식으로 나온다.

```text
NAME      SECRETS   AGE
app-sa    0         5s
default   0         10d
```

---

## 5. Pod에 ServiceAccount 연결하기

ServiceAccount를 만들었다고 해서 자동으로 모든 Pod가 그 계정을 쓰는 것은 아니다.

Pod spec에 `serviceAccountName`을 지정해야 한다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
  namespace: dev
spec:
  serviceAccountName: app-sa
  containers:
    - name: app
      image: nginx
```

이제 이 Pod는 `dev` 네임스페이스의 `app-sa` ServiceAccount를 사용한다.

구조로 보면 이렇다.

```text
app-pod
  ↓
serviceAccountName: app-sa
  ↓
app-sa 권한으로 Kubernetes API 접근
```

---

## 6. ServiceAccount만 만들면 권한이 생길까?

아니다.

ServiceAccount는 말 그대로 **계정**일 뿐이다.
계정을 만들었다고 권한이 자동으로 생기는 것은 아니다.

예를 들어 `app-sa`를 만들었다고 해도, 이 계정이 Pod를 조회할 수 있는지는 별개의 문제다.

```text
app-sa가 있다
→ 인증 주체는 생김

app-sa가 pods를 조회할 수 있다
→ 권한이 부여되어야 함
```

이 권한 부여를 위해 필요한 것이 RBAC다.

RBAC에서는 보통 다음 리소스를 사용한다.

```text
Role
RoleBinding
ClusterRole
ClusterRoleBinding
```

---

## 7. ServiceAccount에 권한 주기

예를 들어 `dev` 네임스페이스 안에서 Pod 목록을 조회할 수 있는 권한을 주고 싶다고 하자.

먼저 Role을 만든다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: dev
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
```

이 Role의 의미는 이렇다.

```text
dev 네임스페이스에서
pods 리소스에 대해
get, list, watch 가능
```

그런 다음 RoleBinding으로 `app-sa`에 연결한다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-sa-pod-reader-binding
  namespace: dev
subjects:
  - kind: ServiceAccount
    name: app-sa
    namespace: dev
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

이 설정의 의미는 이렇다.

```text
dev 네임스페이스의 app-sa ServiceAccount에게
pod-reader Role을 부여한다
```

전체 흐름은 이렇게 된다.

```text
Pod
  ↓
ServiceAccount: app-sa
  ↓
RoleBinding
  ↓
Role: pod-reader
  ↓
pods get/list/watch 가능
```

---

## 8. RoleBinding에서 subjects가 중요한 이유

RoleBinding을 보면 `subjects`라는 부분이 있다.

```yaml
subjects:
  - kind: ServiceAccount
    name: app-sa
    namespace: dev
```

여기서 `subjects`는 권한을 받을 대상을 의미한다.

대상은 User일 수도 있고, Group일 수도 있고, ServiceAccount일 수도 있다.

```text
subjects
→ 이 권한을 누구에게 줄 것인가
```

ServiceAccount에 권한을 줄 때는 보통 이렇게 쓴다.

```yaml
subjects:
  - kind: ServiceAccount
    name: app-sa
    namespace: dev
```

여기서 namespace를 빼먹으면 헷갈릴 수 있다.
ServiceAccount는 네임스페이스에 속하는 리소스이기 때문에 어느 네임스페이스의 ServiceAccount인지 명확히 적는 게 좋다.

---

## 9. ServiceAccount 권한 확인하기

권한이 잘 들어갔는지 확인할 때는 `kubectl auth can-i`를 사용한다.

현재 사용자 기준으로 확인할 때는 이렇게 한다.

```bash
kubectl auth can-i get pods -n dev
```

ServiceAccount 기준으로 확인하려면 `--as` 옵션을 사용한다.

```bash
kubectl auth can-i get pods \
  --as=system:serviceaccount:dev:app-sa \
  -n dev
```

결과가 `yes`면 가능하다는 뜻이다.

```text
yes
```

결과가 `no`면 권한이 없다는 뜻이다.

```text
no
```

여기서 ServiceAccount를 표현하는 형식은 다음과 같다.

```text
system:serviceaccount:<namespace>:<serviceaccount-name>
```

예를 들어 `dev` 네임스페이스의 `app-sa`는 이렇게 표현된다.

```text
system:serviceaccount:dev:app-sa
```

---

## 10. ServiceAccount 토큰

ServiceAccount는 API Server에 접근할 때 토큰을 사용한다.

예전 쿠버네티스에서는 ServiceAccount를 만들면 Secret 기반 토큰이 자동으로 만들어지는 경우가 많았다.

그래서 예전 자료를 보면 이런 식으로 나온다.

```bash
kubectl get secret
```

```text
app-sa-token-xxxxx
```

하지만 최신 쿠버네티스에서는 토큰 관리 방식이 바뀌었다.
보통 Bound ServiceAccount Token Volume 방식으로 Pod에 토큰이 자동 마운트된다.

Pod 안에서는 대체로 이런 경로에서 토큰을 볼 수 있다.

```text
/var/run/secrets/kubernetes.io/serviceaccount/token
```

같은 디렉터리에 CA 인증서와 namespace 정보도 들어간다.

```text
/var/run/secrets/kubernetes.io/serviceaccount/
  ├── token
  ├── ca.crt
  └── namespace
```

즉, Pod 안의 애플리케이션은 이 토큰을 사용해서 API Server에 인증할 수 있다.

구조로 보면 이렇다.

```text
Pod
  ↓
ServiceAccount Token 자동 마운트
  ↓
API Server에 요청할 때 토큰 사용
  ↓
API Server가 이 ServiceAccount가 누구인지 인증
  ↓
RBAC로 권한 확인
```

---

## 11. 토큰 자동 마운트 끄기

모든 Pod가 Kubernetes API에 접근할 필요는 없다.

예를 들어 단순히 Nginx 웹서버만 띄우는 Pod라면 API Server에 접근할 일이 없을 수 있다.

이럴 때는 ServiceAccount 토큰 자동 마운트를 끌 수 있다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  automountServiceAccountToken: false
  containers:
    - name: nginx
      image: nginx
```

ServiceAccount 자체에서 끌 수도 있다.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
automountServiceAccountToken: false
```

보안 관점에서는 필요 없는 Pod에 토큰을 마운트하지 않는 것이 좋다.

```text
API Server에 접근할 필요 없는 Pod
→ ServiceAccount Token 자동 마운트 비활성화 고려
```

---

## 12. default ServiceAccount를 조심해야 하는 이유

네임스페이스마다 기본 `default` ServiceAccount가 있다.

별도 설정이 없으면 Pod는 이 `default` ServiceAccount를 사용한다.

처음 공부할 때는 편하다.

하지만 운영 환경에서는 조심해야 한다.

만약 default ServiceAccount에 강한 권한을 줘버리면 어떻게 될까?

```text
해당 namespace의 모든 기본 Pod가 강한 권한을 가질 수 있음
```

예를 들어 default ServiceAccount에 Secret 조회 권한을 주면, 그 네임스페이스에서 별도 ServiceAccount를 지정하지 않은 Pod들이 Secret을 조회할 가능성이 생긴다.

그래서 운영 환경에서는 보통 이런 방식이 더 안전하다.

```text
default ServiceAccount에는 거의 권한을 주지 않기
애플리케이션별 ServiceAccount 따로 만들기
필요한 권한만 Role/RoleBinding으로 부여하기
```

---

## 13. ServiceAccount와 Secret의 관계

ServiceAccount를 공부하다 보면 Secret도 같이 나온다.

이유는 ServiceAccount가 API Server에 접근할 때 토큰을 사용하고, 그 토큰이 Secret 형태로 다뤄지는 경우가 있었기 때문이다.

또한 ServiceAccount는 imagePullSecrets와도 관련이 있다.

Private Registry에서 이미지를 가져오려면 인증 정보가 필요하다.

이때 imagePullSecret을 ServiceAccount에 연결해둘 수 있다.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
  namespace: dev
imagePullSecrets:
  - name: regcred
```

이렇게 하면 이 ServiceAccount를 사용하는 Pod는 기본적으로 `regcred`를 사용해서 이미지를 pull할 수 있다.

구조는 이렇다.

```text
ServiceAccount: app-sa
  ↓
imagePullSecrets: regcred
  ↓
Private Registry에서 이미지 pull 가능
```

Pod마다 매번 `imagePullSecrets`를 적지 않아도 되기 때문에 편하다.

---

## 14. 실무 예시: Jenkins 배포용 ServiceAccount

Jenkins가 쿠버네티스에 배포를 해야 한다고 해보자.

이때 Jenkins에게 클러스터 관리자 권한을 바로 주는 것은 위험하다.

좋은 방식은 Jenkins 전용 ServiceAccount를 만들고, 특정 네임스페이스에 필요한 권한만 주는 것이다.

예를 들어 `app` 네임스페이스에 배포만 하도록 만들 수 있다.

```text
jenkins-sa
  ↓
app namespace의 Deployment, Service 수정 권한
  ↓
prod 전체 권한은 없음
  ↓
Secret 전체 조회 권한도 없음
```

이런 식으로 최소 권한을 주는 게 좋다.

```text
필요한 작업만 가능하게 만들기
```

이것이 ServiceAccount와 RBAC를 같이 쓰는 핵심 이유다.

---

## 15. 실무 예시: Prometheus 모니터링용 ServiceAccount

Prometheus는 클러스터 안의 Pod, Service, Endpoint 정보를 알아야 모니터링 대상을 찾을 수 있다.

그래서 Prometheus Pod는 ServiceAccount를 사용해서 Kubernetes API를 조회한다.

대략 구조는 이렇다.

```text
Prometheus Pod
  ↓
prometheus-sa
  ↓
ClusterRoleBinding
  ↓
Pod, Service, Endpoint, Node 정보 조회 가능
```

Prometheus는 여러 네임스페이스의 리소스를 봐야 할 수 있으므로 `ClusterRole`과 `ClusterRoleBinding`을 사용하는 경우가 많다.

하지만 이때도 필요한 조회 권한만 주는 것이 좋다.

```text
get, list, watch 중심
create, update, delete는 불필요하면 주지 않기
```

---

## 16. Role과 ClusterRole 중 뭘 써야 할까?

ServiceAccount에 권한을 줄 때 고민되는 부분이다.

기준은 범위다.

```text
특정 namespace 안에서만 작업
→ Role + RoleBinding

클러스터 전체 또는 여러 namespace 조회
→ ClusterRole + ClusterRoleBinding

공통 권한을 정의해두고 특정 namespace에만 적용
→ ClusterRole + RoleBinding
```

예를 들어 `dev` 네임스페이스 안에서만 Pod를 조회하면 된다면 Role을 쓰면 된다.

```text
Role + RoleBinding
```

반대로 Prometheus처럼 여러 네임스페이스의 리소스를 봐야 한다면 ClusterRole이 필요할 수 있다.

```text
ClusterRole + ClusterRoleBinding
```

---

## 17. 자주 하는 실수

### 17.1 ServiceAccount만 만들고 권한이 생겼다고 생각하기

ServiceAccount는 계정일 뿐이다.

```text
ServiceAccount 생성
→ 인증 주체 생성

RoleBinding 생성
→ 권한 연결
```

권한은 반드시 RBAC로 연결해야 한다.

---

### 17.2 default ServiceAccount에 너무 큰 권한 주기

default ServiceAccount에 큰 권한을 주면, 별도로 ServiceAccount를 지정하지 않은 Pod들이 예상보다 큰 권한을 가질 수 있다.

운영 환경에서는 되도록 애플리케이션별 ServiceAccount를 따로 만드는 것이 좋다.

---

### 17.3 ClusterRoleBinding을 남발하기

ClusterRoleBinding은 클러스터 전체 권한을 줄 수 있다.

편하다고 아무 도구에나 ClusterRoleBinding을 주면 위험하다.

```text
특정 namespace만 필요
→ RoleBinding 우선 고려

전체 cluster 권한 필요
→ ClusterRoleBinding 고려
```

---

### 17.4 Secret 조회 권한을 쉽게 주기

Secret은 base64로 보일 뿐, 쉽게 디코딩할 수 있다.

따라서 ServiceAccount에 Secret 조회 권한을 줄 때는 조심해야 한다.

```text
secrets get/list 권한
→ 사실상 민감정보 조회 가능
```

---

## 18. 정리

ServiceAccount는 쿠버네티스에서 Pod나 애플리케이션이 API Server에 접근할 때 사용하는 계정이다.

```text
User
→ 사람이 API Server에 접근할 때 사용

ServiceAccount
→ Pod나 프로그램이 API Server에 접근할 때 사용
```

ServiceAccount 자체는 권한이 아니다.
권한을 주려면 RBAC와 연결해야 한다.

```text
ServiceAccount
  ↓
RoleBinding 또는 ClusterRoleBinding
  ↓
Role 또는 ClusterRole
  ↓
실제 권한 부여
```

최종적으로 이렇게 기억하면 된다.

```text
ServiceAccount
= Pod에게 붙는 Kubernetes API 접근용 계정

Role
= namespace 안에서의 권한 정의

RoleBinding
= Role을 ServiceAccount에 연결

ClusterRole
= cluster 범위 권한 정의

ClusterRoleBinding
= ClusterRole을 ServiceAccount에 연결
```

한 줄로 요약하면 이렇다.

> ServiceAccount는 Pod가 Kubernetes API Server와 대화할 때 사용하는 신분증이고, RBAC는 그 신분증으로 어디까지 할 수 있는지 정하는 권한표다.
