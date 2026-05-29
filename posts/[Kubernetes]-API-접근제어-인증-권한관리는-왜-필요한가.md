---
title: "[Kubernetes] API 접근제어, 인증, 권한관리는 왜 필요한가"
source: ""
published: "Thu, 29 May 2026 12:00:00 GMT"
---

쿠버네티스를 공부하다 보면 어느 순간부터 단순히 `Pod 만들기`, `Service 연결하기`, `Ingress 붙이기`를 넘어서 이런 질문이 나온다.

> 아무나 클러스터에 명령을 날릴 수 있으면 어떡하지?
> 사용자는 어떻게 구분하지?
> 특정 사람은 조회만 가능하고, 특정 프로그램은 배포까지 가능하게 하려면 어떻게 하지?

이때 나오는 개념이 바로 **API 접근제어**, **인증**, **권한관리**다.

쿠버네티스는 결국 모든 요청이 **API Server**를 통해 처리된다.
`kubectl get pod`를 하든, `kubectl apply -f deployment.yaml`을 하든, 내부적으로는 전부 Kubernetes API Server에 요청을 보내는 것이다.

그래서 쿠버네티스 보안의 핵심 흐름은 이렇게 볼 수 있다.

```text
사용자 또는 프로그램
        ↓
Kubernetes API Server에 요청
        ↓
1. 너 누구야?        → 인증 Authentication
        ↓
2. 이 작업 해도 돼?  → 인가 Authorization
        ↓
3. 요청 내용 괜찮아? → Admission Control
        ↓
실제 리소스 생성/조회/수정/삭제
```

이번 글에서는 그중에서도 `API 접근제어`, `인증`, `권한관리`를 정리해본다.

---

## 1. API 접근제어란?

쿠버네티스에서 무언가를 조작하려면 대부분 API Server를 거친다.

예를 들어 아래 명령어를 실행한다고 해보자.

```bash
kubectl get pods
```

겉으로 보기에는 단순히 Pod 목록을 조회하는 명령어지만, 실제 흐름은 이렇다.

```text
kubectl
  → Kubernetes API Server
  → "Pod 목록 조회해도 되는 사용자야?"
  → 허용되면 Pod 목록 반환
```

즉, 쿠버네티스에서 API 접근제어란 **누가 API Server에 접근할 수 있고, 어떤 작업까지 할 수 있는지 통제하는 것**이다.

API 접근제어가 없으면 이런 문제가 생긴다.

```text
아무 개발자가 운영 네임스페이스의 Pod 삭제
인증되지 않은 요청이 Secret 조회
CI/CD 서버가 필요 이상의 권한으로 클러스터 전체 수정
테스트용 계정이 관리자 권한 보유
```

그래서 쿠버네티스는 요청을 받을 때 보통 다음 단계를 거친다.

```text
Authentication → Authorization → Admission Control
```

이번 글에서는 특히 앞의 두 개를 중심으로 보면 된다.

```text
Authentication: 너 누구야?
Authorization: 너 이거 해도 돼?
```

---

## 2. 인증 Authentication

인증은 말 그대로 **요청한 주체가 누구인지 확인하는 과정**이다.

쿠버네티스에서 요청 주체는 크게 두 종류가 있다.

```text
User
ServiceAccount
```

---

## 3. User란?

`User`는 보통 사람이 사용하는 계정이라고 생각하면 된다.

예를 들어 개발자, 운영자, 관리자 같은 사람이 `kubectl`을 통해 클러스터에 접근할 때 사용된다.

```text
개발자 A → kubectl get pods
운영자 B → kubectl delete pod
관리자 C → kubectl apply -f ...
```

다만 중요한 점이 있다.

쿠버네티스는 일반적인 애플리케이션처럼 자체적으로 사용자를 직접 관리하지 않는다.

즉, 쿠버네티스 안에 이런 식으로 사용자를 만드는 리소스가 따로 있는 것이 아니다.

```bash
kubectl create user seoyeon
```

이런 명령어는 없다.

대신 쿠버네티스는 외부 인증 방식을 사용한다.

대표적으로는 다음과 같은 방식이 있다.

```text
client certificate
token
OIDC
cloud provider IAM
```

예를 들어 AWS EKS에서는 IAM 기반으로 사용자를 인증할 수 있고, 회사 환경에서는 OIDC나 SSO와 연결해서 사용자 인증을 처리할 수도 있다.

정리하면 User는 이렇게 이해하면 된다.

```text
User = 사람이 클러스터에 접근할 때의 주체
```

---

## 4. ServiceAccount란?

`ServiceAccount`는 사람이 아니라 **Pod나 애플리케이션이 Kubernetes API에 접근할 때 사용하는 계정**이다.

예를 들어 어떤 Pod 안에서 Kubernetes API를 호출해야 한다고 해보자.

```text
Pod 내부 애플리케이션이 다른 Pod 목록 조회
Argo CD가 Deployment 상태 확인
Prometheus가 Kubernetes 리소스 메트릭 수집
CI/CD 도구가 배포 자동화
```

이런 경우 사람이 직접 `kubectl`을 치는 것이 아니다.
클러스터 안의 프로그램이 API Server에 접근한다.

이때 사용하는 계정이 바로 `ServiceAccount`다.

기본적으로 Pod는 ServiceAccount를 하나 사용할 수 있다.
아무것도 지정하지 않으면 `default` ServiceAccount가 붙는다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sample-pod
spec:
  serviceAccountName: my-service-account
  containers:
    - name: nginx
      image: nginx
```

여기서 핵심은 이것이다.

```text
User = 사람이 사용하는 계정
ServiceAccount = Pod나 프로그램이 사용하는 계정
```

---

## 5. 인증만 하면 끝인가?

아니다.

인증은 단지 **누구인지 확인하는 것**일 뿐이다.

예를 들어 어떤 사용자가 클러스터에 접근했다고 해보자.

```text
이 사용자는 seoyeon입니다.
```

여기까지가 인증이다.

그런데 이 사람이 Pod를 조회해도 되는지, Secret을 봐도 되는지, Deployment를 삭제해도 되는지는 별개의 문제다.

```text
seoyeon은 Pod 조회 가능?
seoyeon은 Secret 조회 가능?
seoyeon은 Deployment 삭제 가능?
seoyeon은 kube-system 네임스페이스 접근 가능?
```

이걸 결정하는 것이 바로 **권한관리**, 즉 Authorization이다.

---

## 6. 권한관리 Authorization

쿠버네티스에서 권한관리는 보통 **RBAC**으로 처리한다.

RBAC는 Role-Based Access Control의 약자다.

이름 그대로 **역할 기반 접근 제어**다.

쉽게 말하면 이런 구조다.

```text
권한 묶음 만들기
        ↓
그 권한을 특정 사용자나 ServiceAccount에 연결하기
```

쿠버네티스 RBAC에서 자주 나오는 리소스는 네 가지다.

```text
Role
RoleBinding
ClusterRole
ClusterRoleBinding
```

처음 보면 이름이 비슷해서 헷갈리는데, 기준은 단순하다.

```text
Role / RoleBinding
→ 특정 namespace 안에서만 적용

ClusterRole / ClusterRoleBinding
→ 클러스터 전체 범위에 적용 가능
```

---

## 7. Role

`Role`은 특정 네임스페이스 안에서 사용할 수 있는 권한 묶음이다.

예를 들어 `dev` 네임스페이스에서 Pod 목록만 조회할 수 있는 Role을 만들 수 있다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: dev
  name: pod-reader
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
```

이 Role은 이런 의미다.

```text
dev 네임스페이스에서
pods 리소스에 대해
get, list, watch 가능
```

여기서 `verbs`는 가능한 동작을 의미한다.

대표적으로 많이 보는 verb는 다음과 같다.

```text
get     단일 리소스 조회
list    목록 조회
watch   변경 감시
create  생성
update  수정
patch   일부 수정
delete  삭제
```

즉, Role은 권한 그 자체를 정의한다.

하지만 Role만 만든다고 누군가에게 권한이 부여되는 것은 아니다.

---

## 8. RoleBinding

`RoleBinding`은 Role을 실제 사용자나 ServiceAccount에 연결한다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods-binding
  namespace: dev
subjects:
  - kind: User
    name: seoyeon
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

이 설정은 이렇게 해석할 수 있다.

```text
dev 네임스페이스에서
seoyeon이라는 User에게
pod-reader Role을 부여한다
```

즉, 이제 `seoyeon`은 `dev` 네임스페이스에서 Pod를 조회할 수 있다.

정리하면 이렇다.

```text
Role = 어떤 권한인지 정의
RoleBinding = 그 권한을 누구에게 줄지 연결
```

---

## 9. ServiceAccount에 RoleBinding하기

이번에는 사람 User가 아니라 ServiceAccount에 권한을 줄 수도 있다.

예를 들어 `dev` 네임스페이스에 있는 `app-sa`라는 ServiceAccount에게 Pod 조회 권한을 주고 싶다면 이렇게 한다.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
  namespace: dev
```

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

이제 `app-sa`를 사용하는 Pod는 `dev` 네임스페이스 안에서 Pod 목록을 조회할 수 있다.

이 구조는 실무에서 정말 많이 나온다.

예를 들어 Argo CD, Prometheus, Jenkins, ExternalDNS, cert-manager 같은 도구들은 Kubernetes API를 조회하거나 수정해야 한다.
이때 각 도구마다 ServiceAccount를 만들고, 필요한 권한만 Role 또는 ClusterRole로 부여한다.

---

## 10. ClusterRole

`ClusterRole`은 Role과 비슷하지만 범위가 더 넓다.

Role은 특정 네임스페이스 안에서만 동작한다.

```text
Role → namespace 범위
```

반면 ClusterRole은 클러스터 전체 리소스에 대한 권한을 정의할 수 있다.

```text
ClusterRole → cluster 범위
```

예를 들어 모든 네임스페이스의 Pod를 조회할 수 있는 ClusterRole은 이렇게 만들 수 있다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-pod-reader
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
```

여기서 metadata에 namespace가 없다.
ClusterRole은 네임스페이스에 종속되지 않는 리소스이기 때문이다.

ClusterRole은 이런 경우에 사용된다.

```text
모든 namespace의 Pod를 조회해야 할 때
Node 같은 cluster-level 리소스를 조회해야 할 때
PersistentVolume 같은 cluster-level 리소스를 다룰 때
클러스터 전체 모니터링 도구에 권한을 줄 때
```

---

## 11. ClusterRoleBinding

`ClusterRoleBinding`은 ClusterRole을 사용자나 ServiceAccount에 연결한다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: cluster-pod-reader-binding
subjects:
  - kind: User
    name: seoyeon
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: cluster-pod-reader
  apiGroup: rbac.authorization.k8s.io
```

이 설정은 이렇게 해석할 수 있다.

```text
seoyeon이라는 User에게
cluster-pod-reader ClusterRole을 부여한다
```

이제 이 사용자는 특정 네임스페이스 하나가 아니라, 클러스터 전체 범위에서 Pod를 조회할 수 있다.

---

## 12. RoleBinding과 ClusterRoleBinding 차이

이 부분이 처음에는 제일 헷갈린다.

핵심은 **권한이 적용되는 범위**다.

| 구분           | 권한 정의       | 권한 연결              | 적용 범위        |
| ------------ | ----------- | ------------------ | ------------ |
| namespace 단위 | Role        | RoleBinding        | 특정 namespace |
| cluster 전체   | ClusterRole | ClusterRoleBinding | 전체 cluster   |

조금 더 쉽게 보면 이렇다.

```text
Role + RoleBinding
→ dev 네임스페이스 안에서만 권한 부여

ClusterRole + ClusterRoleBinding
→ 클러스터 전체에 권한 부여
```

그런데 한 가지 더 있다.

`ClusterRole`을 `RoleBinding`으로 연결할 수도 있다.

즉, 권한 정의는 ClusterRole로 해두고, 적용 범위는 특정 네임스페이스로 제한하는 방식이다.

```text
ClusterRole + RoleBinding
→ ClusterRole에 정의된 권한을 특정 namespace 안에서만 사용
```

이 방식은 공통 권한 템플릿을 만들어두고 여러 네임스페이스에 재사용할 때 유용하다.

---

## 13. 실무적으로 왜 중요할까?

쿠버네티스 권한관리는 단순 시험용 개념이 아니다.

실무에서 정말 중요하다.

예를 들어 CI/CD 서버가 있다고 해보자.

Jenkins나 GitHub Actions가 Kubernetes에 배포를 해야 한다면 API Server에 접근할 권한이 필요하다.

그런데 귀찮다고 cluster-admin 권한을 줘버리면 위험하다.

```text
Jenkins가 모든 namespace 삭제 가능
Secret 전체 조회 가능
Node 정보 접근 가능
운영 리소스까지 수정 가능
```

이건 너무 큰 권한이다.

좋은 방식은 필요한 권한만 주는 것이다.

```text
특정 namespace의 Deployment 수정 가능
특정 namespace의 Pod 조회 가능
Secret 조회는 제한
Cluster 전체 권한은 금지
```

이런 방식을 **최소 권한 원칙**이라고 한다.

```text
필요한 만큼만 권한을 준다
```

쿠버네티스 RBAC는 이 최소 권한 원칙을 구현하기 위한 핵심 기능이다.

---

## 14. kubectl로 권한 확인하기

권한이 헷갈릴 때는 `kubectl auth can-i` 명령어를 많이 사용한다.

예를 들어 현재 사용자가 Pod를 조회할 수 있는지 확인하려면 이렇게 한다.

```bash
kubectl auth can-i get pods
```

결과는 보통 이렇게 나온다.

```bash
yes
```

또는

```bash
no
```

특정 네임스페이스 기준으로 확인할 수도 있다.

```bash
kubectl auth can-i get pods -n dev
```

특정 동작을 확인할 수도 있다.

```bash
kubectl auth can-i delete deployments -n prod
```

ServiceAccount 기준으로 확인할 수도 있다.

```bash
kubectl auth can-i get pods \
  --as=system:serviceaccount:dev:app-sa \
  -n dev
```

이 명령어는 RBAC 공부할 때 매우 유용하다.

```text
이 계정이 진짜 이 작업을 할 수 있는지 바로 확인 가능
```

---

## 15. 전체 흐름 예시

예를 들어 `dev` 네임스페이스에 있는 애플리케이션 Pod가 Pod 목록을 조회해야 한다고 해보자.

필요한 흐름은 이렇다.

```text
1. ServiceAccount 생성
2. Role 생성
3. RoleBinding으로 ServiceAccount와 Role 연결
4. Pod에서 serviceAccountName 지정
5. Pod 내부 프로그램이 Kubernetes API 호출
```

전체 구조는 이렇게 볼 수 있다.

```text
Pod
 └─ ServiceAccount: app-sa
        ↓
RoleBinding
        ↓
Role: pod-reader
        ↓
권한: dev namespace에서 pods get/list/watch 가능
```

즉, Pod 자체가 권한을 갖는 것이 아니라, Pod에 연결된 ServiceAccount가 권한을 갖는 구조다.

---

## 16. 정리

쿠버네티스에서 API 접근제어는 클러스터 보안의 핵심이다.

모든 요청은 API Server를 통과하고, 쿠버네티스는 그 요청에 대해 다음을 확인한다.

```text
Authentication: 요청한 주체가 누구인지 확인
Authorization: 그 주체가 해당 작업을 해도 되는지 확인
```

인증 주체는 크게 두 가지다.

```text
User
ServiceAccount
```

권한관리는 RBAC를 통해 처리한다.

```text
Role
RoleBinding
ClusterRole
ClusterRoleBinding
```

최종적으로 이렇게 기억하면 된다.

```text
User
→ 사람이 클러스터에 접근할 때 사용

ServiceAccount
→ Pod나 프로그램이 API Server에 접근할 때 사용

Role
→ namespace 안에서의 권한 정의

RoleBinding
→ Role을 User 또는 ServiceAccount에 연결

ClusterRole
→ cluster 범위 권한 정의

ClusterRoleBinding
→ ClusterRole을 User 또는 ServiceAccount에 연결
```

한 줄로 요약하면 이렇다.

> 쿠버네티스 권한관리는 “누가, 어디에서, 어떤 리소스에, 어떤 행동을 할 수 있는가”를 정하는 시스템이다.
