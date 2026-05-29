---
title: "[Kubernetes] ClusterRole은 언제 쓰는 걸까?"
source: ""
published: "2026-05-29T17:45:29.000Z"
---

쿠버네티스에서 RBAC를 공부하다 보면 `Role` 다음에 바로 `ClusterRole`이 나온다.

처음 보면 이런 생각이 든다.

> Role이 권한이면 ClusterRole은 더 센 권한인가?
> ClusterRole은 무조건 클러스터 전체 권한인가?
> Role이랑 정확히 뭐가 다른 거지?

간단히 말하면 이렇다.

```text
Role
→ 특정 namespace 안에서만 적용되는 권한

ClusterRole
→ namespace에 묶이지 않는 권한
```

즉, `Role`은 네임스페이스 단위 권한이고, `ClusterRole`은 클러스터 범위까지 다룰 수 있는 권한이다.

---

## 1. Role과 ClusterRole의 가장 큰 차이

먼저 Role을 다시 보자.

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

이 Role은 `dev` 네임스페이스 안에서만 의미가 있다.

```text
dev namespace 안에서
pods를 get/list/watch 가능
```

즉, `prod` 네임스페이스에서는 이 Role이 적용되지 않는다.

반면 ClusterRole은 namespace를 적지 않는다.

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

여기에는 `metadata.namespace`가 없다.

왜냐하면 `ClusterRole`은 특정 namespace 안에 갇힌 리소스가 아니기 때문이다.

```text
Role
→ namespace 안에 존재

ClusterRole
→ cluster 범위에 존재
```

---

## 2. ClusterRole이 필요한 이유

쿠버네티스에는 namespace 안에 속하는 리소스도 있고, namespace에 속하지 않는 리소스도 있다.

예를 들어 Pod, Service, Deployment는 보통 namespace 안에 있다.

```text
namespaced resource
→ Pod
→ Service
→ Deployment
→ ConfigMap
→ Secret
```

반대로 Node, PersistentVolume 같은 리소스는 특정 namespace에 속하지 않는다.

```text
cluster-scoped resource
→ Node
→ PersistentVolume
→ Namespace
→ ClusterRole
→ ClusterRoleBinding
```

예를 들어 Node 목록을 조회하는 권한은 Role로 만들 수 없다.

Node는 namespace 안에 있는 리소스가 아니기 때문이다.

이럴 때 ClusterRole을 사용한다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-reader
rules:
  - apiGroups: [""]
    resources: ["nodes"]
    verbs: ["get", "list", "watch"]
```

이 권한은 이런 뜻이다.

```text
nodes 리소스에 대해
get/list/watch 가능
```

Node는 클러스터 범위 리소스이기 때문에 ClusterRole이 필요하다.

---

## 3. ClusterRole은 무조건 전체 권한일까?

헷갈리기 쉬운 부분이다.

`ClusterRole`이라고 해서 무조건 관리자 권한이라는 뜻은 아니다.

ClusterRole도 결국 `rules`에 적힌 권한만 가진다.

```yaml
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
```

이렇게 적으면 Pod 조회 권한만 있다.

```text
가능
→ pods get
→ pods list
→ pods watch

불가능
→ pods delete
→ secrets get
→ deployments update
→ nodes delete
```

즉, ClusterRole은 “무조건 강한 권한”이 아니라, “namespace에 묶이지 않는 권한 정의”라고 보는 게 더 정확하다.

다만 ClusterRoleBinding과 연결하면 클러스터 전체에 권한이 적용될 수 있기 때문에 조심해야 한다.

---

## 4. ClusterRole YAML 구조

ClusterRole의 기본 구조는 Role과 거의 비슷하다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: pod-reader
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
```

Role과 비교하면 차이는 여기다.

```yaml
kind: ClusterRole
metadata:
  name: pod-reader
```

Role은 namespace가 있다.

```yaml
kind: Role
metadata:
  name: pod-reader
  namespace: dev
```

ClusterRole은 namespace가 없다.

```yaml
kind: ClusterRole
metadata:
  name: pod-reader
```

이 차이가 핵심이다.

---

## 5. ClusterRole의 rules 읽는 법

ClusterRole에서 제일 중요한 건 `rules`다.

```yaml
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
```

각 항목은 이렇게 읽으면 된다.

```text
apiGroups
→ 어떤 API 그룹의 리소스인지

resources
→ 어떤 리소스에 대한 권한인지

verbs
→ 어떤 동작을 허용할지
```

여기서 `apiGroups: [""]`는 core API group을 의미한다.

Core API group에는 이런 리소스들이 있다.

```text
pods
services
configmaps
secrets
nodes
namespaces
persistentvolumes
persistentvolumeclaims
```

Deployment 같은 리소스는 `apps` API group에 있다.

```yaml
apiGroups: ["apps"]
resources: ["deployments"]
verbs: ["get", "list", "watch"]
```

즉, Deployment 조회 권한을 주고 싶으면 이렇게 쓴다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: deployment-reader
rules:
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "watch"]
```

---

## 6. ClusterRole과 ClusterRoleBinding

ClusterRole은 권한을 정의하는 리소스다.

하지만 ClusterRole만 만든다고 누군가 권한을 갖는 것은 아니다.

Role 때와 똑같다.

```text
ClusterRole
→ 어떤 권한인지 정의

ClusterRoleBinding
→ 그 권한을 누구에게 줄지 연결
```

예를 들어 `monitoring` 네임스페이스의 `prometheus-sa` ServiceAccount에게 클러스터 전체 Pod 조회 권한을 주고 싶다고 하자.

먼저 ClusterRole을 만든다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus-reader
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "endpoints", "nodes"]
    verbs: ["get", "list", "watch"]
```

그다음 ClusterRoleBinding으로 연결한다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: prometheus-reader-binding
subjects:
  - kind: ServiceAccount
    name: prometheus-sa
    namespace: monitoring
roleRef:
  kind: ClusterRole
  name: prometheus-reader
  apiGroup: rbac.authorization.k8s.io
```

이 설정은 이렇게 해석하면 된다.

```text
monitoring 네임스페이스의 prometheus-sa에게
prometheus-reader ClusterRole을 부여한다
```

결과적으로 `prometheus-sa`는 클러스터 전체에서 Pod, Service, Endpoint, Node 정보를 조회할 수 있다.

---

## 7. ClusterRole + RoleBinding 조합도 가능하다

여기서 중요한 포인트가 하나 있다.

ClusterRole은 꼭 ClusterRoleBinding하고만 연결해야 하는 게 아니다.

`ClusterRole + RoleBinding` 조합도 가능하다.

이 구조는 이렇게 이해하면 된다.

```text
ClusterRole
→ 권한 템플릿

RoleBinding
→ 특정 namespace 안에서만 그 권한 적용
```

예를 들어 쿠버네티스에는 기본 ClusterRole 중에 `view`라는 권한이 있다.

이 `view` 권한을 `dev` 네임스페이스 안에서만 특정 ServiceAccount에게 주고 싶다면 RoleBinding을 사용할 수 있다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: dev-view-binding
  namespace: dev
subjects:
  - kind: ServiceAccount
    name: app-sa
    namespace: dev
roleRef:
  kind: ClusterRole
  name: view
  apiGroup: rbac.authorization.k8s.io
```

이건 이런 뜻이다.

```text
view ClusterRole을 사용하되
dev namespace 안에서만 적용한다
```

즉, ClusterRole을 RoleBinding으로 묶으면 전체 클러스터 권한이 아니라, RoleBinding이 있는 namespace 안에서만 적용된다.

이 조합은 실무에서도 꽤 자주 쓰인다.

---

## 8. RoleBinding vs ClusterRoleBinding 차이

ClusterRole을 어디에 연결하느냐에 따라 권한 범위가 달라진다.

```text
ClusterRole + RoleBinding
→ 특정 namespace 안에서만 권한 적용

ClusterRole + ClusterRoleBinding
→ cluster 전체 범위에 권한 적용
```

예를 들어 같은 `view` ClusterRole이라도 연결 방식에 따라 범위가 다르다.

```text
dev namespace RoleBinding에 연결
→ dev 안에서만 view 권한

ClusterRoleBinding에 연결
→ 모든 namespace에서 view 권한
```

표로 보면 이렇다.

| 조합                               | 적용 범위        |
| -------------------------------- | ------------ |
| Role + RoleBinding               | 특정 namespace |
| ClusterRole + RoleBinding        | 특정 namespace |
| ClusterRole + ClusterRoleBinding | cluster 전체   |

여기서 `Role + ClusterRoleBinding`은 안 된다.

왜냐하면 Role은 namespace에 속한 권한인데, ClusterRoleBinding은 클러스터 전체에 연결하는 리소스이기 때문이다.

---

## 9. 기본 ClusterRole

쿠버네티스에는 기본으로 제공되는 ClusterRole도 있다.

대표적으로 이런 것들이 있다.

```text
cluster-admin
admin
edit
view
```

확인하려면 이렇게 한다.

```bash
kubectl get clusterrole
```

특정 ClusterRole을 자세히 보려면 이렇게 한다.

```bash
kubectl describe clusterrole view
```

각 역할을 아주 단순하게 보면 이렇다.

```text
cluster-admin
→ 거의 모든 권한

admin
→ namespace 안에서 관리자 수준 권한

edit
→ 대부분 리소스 수정 가능

view
→ 조회 중심 권한
```

하지만 이름만 보고 대충 쓰면 위험하다.

특히 `cluster-admin`은 매우 강한 권한이다.

```text
cluster-admin
→ 클러스터 전체 관리자 권한
```

실습할 때는 편해서 자주 쓰지만, 운영 환경에서는 정말 조심해야 한다.

---

## 10. cluster-admin은 왜 위험할까?

`cluster-admin`은 거의 모든 리소스에 대해 모든 동작을 할 수 있는 권한이다.

대략 이런 권한이라고 보면 된다.

```yaml
resources: ["*"]
verbs: ["*"]
```

즉, 이런 작업이 가능해질 수 있다.

```text
모든 namespace의 Secret 조회
운영 Deployment 삭제
Node 관련 리소스 수정
RBAC 권한 자체 수정
다른 사용자에게 관리자 권한 부여
```

그래서 CI/CD 도구나 애플리케이션 Pod에 습관적으로 `cluster-admin`을 주면 위험하다.

예를 들어 Jenkins가 배포만 하면 되는데 `cluster-admin`을 주면 너무 과하다.

```text
필요한 권한
→ 특정 namespace의 Deployment 업데이트

실제로 준 권한
→ 클러스터 전체 관리자
```

이런 상황은 최소 권한 원칙에 어긋난다.

---

## 11. 실무 예시: Prometheus

Prometheus는 클러스터 내부 리소스를 모니터링해야 한다.

그래서 여러 namespace의 Pod, Service, Endpoint, Node 정보를 조회할 수 있어야 한다.

이럴 때 ClusterRole이 자주 사용된다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus-discovery
rules:
  - apiGroups: [""]
    resources:
      - nodes
      - nodes/proxy
      - services
      - endpoints
      - pods
    verbs: ["get", "list", "watch"]
```

이 권한은 조회 중심이다.

```text
get/list/watch
→ 모니터링 대상 찾기 위해 조회만 수행
```

여기에 ClusterRoleBinding을 연결하면 Prometheus가 클러스터 전체 리소스를 볼 수 있다.

```text
Prometheus Pod
  ↓
prometheus-sa
  ↓
ClusterRoleBinding
  ↓
ClusterRole
  ↓
클러스터 전체 리소스 조회
```

---

## 12. 실무 예시: Argo CD

Argo CD는 Git에 있는 선언형 설정과 클러스터 상태를 비교하고 동기화한다.

즉, Kubernetes API를 많이 사용한다.

```text
현재 클러스터 상태 조회
Git에 있는 desired state와 비교
차이가 있으면 apply
필요하면 Deployment, Service, Ingress 등 수정
```

그래서 Argo CD는 관리 대상 범위에 따라 꽤 넓은 권한이 필요할 수 있다.

하지만 여기서도 중요한 건 범위다.

```text
특정 namespace만 배포
→ Role 또는 ClusterRole + RoleBinding 고려

여러 namespace 또는 클러스터 전체 관리
→ ClusterRole + ClusterRoleBinding 고려
```

무조건 `cluster-admin`을 주는 것보다, 실제 관리 범위에 맞게 권한을 줄이는 게 좋다.

---

## 13. 실무 예시: cert-manager

cert-manager는 인증서를 자동으로 발급하고 갱신하는 도구다.

이 과정에서 여러 리소스를 다룬다.

```text
Certificate
CertificateRequest
Issuer
ClusterIssuer
Secret
Ingress
```

특히 `ClusterIssuer`처럼 클러스터 범위 리소스를 다루는 경우 ClusterRole이 필요할 수 있다.

구조는 대략 이렇다.

```text
cert-manager Pod
  ↓
cert-manager ServiceAccount
  ↓
ClusterRoleBinding
  ↓
ClusterRole
  ↓
인증서 관련 리소스 조회/생성/수정
```

이런 컨트롤러류 도구들은 클러스터 여러 리소스를 감시해야 하기 때문에 ClusterRole을 자주 사용한다.

---

## 14. 권한 확인하기

ClusterRole이 제대로 적용됐는지 확인할 때도 `kubectl auth can-i`를 쓴다.

현재 사용자가 Node를 조회할 수 있는지 확인한다.

```bash
kubectl auth can-i list nodes
```

특정 ServiceAccount 기준으로 확인하려면 이렇게 한다.

```bash
kubectl auth can-i list nodes \
  --as=system:serviceaccount:monitoring:prometheus-sa
```

특정 namespace 안에서 Pod 조회 권한을 확인하려면 이렇게 한다.

```bash
kubectl auth can-i get pods \
  --as=system:serviceaccount:monitoring:prometheus-sa \
  -n dev
```

전체 namespace 기준으로 가능한지 보려면 이렇게 할 수도 있다.

```bash
kubectl auth can-i get pods --all-namespaces
```

권한이 기대와 다르면 보통 확인할 것은 세 가지다.

```text
1. ClusterRole rules가 맞는가
2. ClusterRoleBinding의 subject가 맞는가
3. ServiceAccount namespace/name이 맞는가
```

---

## 15. 자주 하는 실수

### 15.1 ClusterRole만 만들고 권한이 적용됐다고 생각하기

ClusterRole은 권한 정의일 뿐이다.

```text
ClusterRole 생성
→ 권한표만 생김

ClusterRoleBinding 생성
→ 실제 대상에게 권한 부여
```

권한이 안 먹으면 먼저 Binding이 있는지 확인해야 한다.

```bash
kubectl get clusterrolebinding
```

---

### 15.2 ClusterRoleBinding을 너무 쉽게 쓰기

ClusterRoleBinding은 권한을 클러스터 전체 범위로 연결할 수 있다.

그래서 특정 namespace만 필요할 때는 RoleBinding을 먼저 고려하는 게 좋다.

```text
dev 안에서만 권한 필요
→ RoleBinding

전체 cluster 권한 필요
→ ClusterRoleBinding
```

---

### 15.3 cluster-admin 남발하기

실습에서는 편하지만 운영에서는 위험하다.

```bash
kubectl create clusterrolebinding app-admin \
  --clusterrole=cluster-admin \
  --serviceaccount=dev:app-sa
```

이런 식으로 주면 `app-sa`는 클러스터 전체 관리자급 권한을 갖게 된다.

애플리케이션 Pod에 이런 권한을 주는 것은 매우 위험하다.

---

### 15.4 Secret 조회 권한을 가볍게 생각하기

ClusterRole에서 Secret 조회 권한을 주면 조심해야 한다.

```yaml
resources: ["secrets"]
verbs: ["get", "list"]
```

Secret은 base64로 보일 뿐 쉽게 디코딩할 수 있다.

즉, Secret 조회 권한은 민감정보 조회 권한에 가깝다.

```text
secrets get/list
→ 비밀번호, 토큰, 인증서 접근 가능성
```

---

## 16. Role, ClusterRole 한 번에 정리

| 구분                    | Role                  | ClusterRole                       |
| --------------------- | --------------------- | --------------------------------- |
| 범위                    | namespace             | cluster                           |
| namespace 지정          | 있음                    | 없음                                |
| namespaced 리소스 권한     | 가능                    | 가능                                |
| cluster-scoped 리소스 권한 | 불가능                   | 가능                                |
| 연결 리소스                | RoleBinding           | RoleBinding 또는 ClusterRoleBinding |
| 예시                    | dev namespace의 Pod 조회 | 모든 namespace의 Pod 조회, Node 조회     |

핵심은 이것이다.

```text
Role
→ 특정 namespace 안에서 권한을 정의

ClusterRole
→ namespace에 묶이지 않고 권한을 정의
```

그리고 연결 방식까지 같이 기억해야 한다.

```text
Role + RoleBinding
→ 특정 namespace에 권한 부여

ClusterRole + RoleBinding
→ 특정 namespace에 ClusterRole 권한 부여

ClusterRole + ClusterRoleBinding
→ cluster 전체에 권한 부여
```

---

## 17. 정리

ClusterRole은 쿠버네티스 RBAC에서 클러스터 범위 권한을 정의할 때 사용하는 리소스다.

Role과 비슷하지만 namespace에 속하지 않는다.

```text
Role
→ namespace 안에서 권한 정의

ClusterRole
→ cluster 범위에서 권한 정의
```

ClusterRole은 이런 경우에 사용한다.

```text
Node 같은 cluster-scoped 리소스를 다룰 때

여러 namespace의 Pod, Service 등을 조회해야 할 때

Prometheus, Argo CD, cert-manager 같은 클러스터 도구에 권한을 줄 때

공통 권한 템플릿을 만들고 여러 namespace에 재사용할 때
```

마지막으로 이렇게 기억하면 된다.

> ClusterRole은 클러스터 전체를 위한 권한표이고, ClusterRoleBinding은 그 권한표를 실제 사용자나 ServiceAccount에게 붙이는 연결고리다. 다만 ClusterRole을 RoleBinding에 연결하면 특정 namespace 안에서만 제한해서 사용할 수도 있다.
