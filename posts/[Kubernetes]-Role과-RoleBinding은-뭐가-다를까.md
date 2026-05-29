---
title: "[Kubernetes] Role과 RoleBinding은 뭐가 다를까?"
source: ""
published: "2026-05-29T17:42:40.000Z"
---

쿠버네티스에서 권한 관리를 공부하면 거의 무조건 나오는 개념이 있다.

```text
Role
RoleBinding
ClusterRole
ClusterRoleBinding
```

이름이 비슷해서 처음에는 헷갈린다.

특히 `Role`과 `RoleBinding`은 같이 나오기 때문에 이런 생각이 들 수 있다.

> Role이 권한이면 RoleBinding은 또 뭐지?
> Role만 만들면 권한이 적용되는 거 아닌가?
> 왜 굳이 두 개로 나눠놨지?

간단히 말하면 이렇다.

```text
Role
→ 어떤 권한인지 정의하는 것

RoleBinding
→ 그 권한을 누구에게 줄지 연결하는 것
```

즉, `Role`은 권한표이고, `RoleBinding`은 그 권한표를 특정 대상에게 붙이는 작업이다.

---

## 1. Role과 RoleBinding을 먼저 비유로 이해하기

회사에서 권한을 준다고 생각해보자.

예를 들어 이런 권한표가 있다.

```text
게시판 조회 권한
- 글 목록 보기 가능
- 글 상세 보기 가능
- 글 작성 불가
- 글 삭제 불가
```

이게 쿠버네티스에서는 `Role`에 가깝다.

그런데 권한표만 만들어놓는다고 누군가가 자동으로 그 권한을 갖는 건 아니다.

이제 이 권한을 누구에게 줄지 정해야 한다.

```text
게시판 조회 권한을
신입 개발자 A에게 부여
```

이게 `RoleBinding`에 가깝다.

정리하면 이렇다.

```text
Role
→ 권한 내용 정의

RoleBinding
→ 권한을 받을 대상과 Role을 연결
```

---

## 2. Role이란?

`Role`은 특정 namespace 안에서 사용할 수 있는 권한 묶음이다.

예를 들어 `dev` 네임스페이스 안에서 Pod를 조회할 수 있는 권한을 만들고 싶다고 해보자.

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

이 Role은 이런 의미다.

```text
dev 네임스페이스에서
pods 리소스에 대해
get, list, watch 작업을 허용
```

즉, `pod-reader`라는 이름의 권한 묶음을 만든 것이다.

여기서 중요한 부분은 `rules`다.

```yaml
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
```

이 부분이 실제 권한 내용을 정의한다.

---

## 3. Role의 구성 요소

Role YAML을 조금 더 쪼개서 보면 이렇다.

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

각 항목은 이렇게 이해하면 된다.

| 항목                   | 의미                    |
| -------------------- | --------------------- |
| `kind: Role`         | Role 리소스를 만들겠다는 뜻     |
| `metadata.name`      | Role 이름               |
| `metadata.namespace` | 이 Role이 적용될 namespace |
| `rules`              | 실제 권한 규칙              |
| `apiGroups`          | 어떤 API 그룹의 리소스인지      |
| `resources`          | 어떤 리소스에 대한 권한인지       |
| `verbs`              | 어떤 동작을 허용할지           |

여기서 `verbs`는 동작을 의미한다.

자주 나오는 verb는 다음과 같다.

```text
get
→ 리소스 하나 조회

list
→ 리소스 목록 조회

watch
→ 리소스 변경 감시

create
→ 리소스 생성

update
→ 리소스 전체 수정

patch
→ 리소스 일부 수정

delete
→ 리소스 삭제
```

예를 들어 아래 권한은 조회만 가능하다.

```yaml
verbs: ["get", "list", "watch"]
```

반대로 아래처럼 쓰면 생성, 수정, 삭제까지 가능해진다.

```yaml
verbs: ["get", "list", "watch", "create", "update", "delete"]
```

운영 환경에서는 필요한 verb만 주는 게 중요하다.

---

## 4. Role만 만들면 권한이 생길까?

아니다.

Role은 권한 내용을 정의할 뿐이다.

예를 들어 이런 Role을 만들었다고 해보자.

```yaml
kind: Role
metadata:
  name: pod-reader
  namespace: dev
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
```

이건 단지 `dev` 네임스페이스에서 Pod를 읽을 수 있는 권한표를 만든 것이다.

하지만 아직 이 권한을 받은 사람이나 ServiceAccount는 없다.

```text
Role 생성
→ 권한표만 존재

RoleBinding 생성
→ 특정 대상에게 권한 부여
```

그래서 Role만 만들고 바로 권한 테스트를 하면 기대한 대로 동작하지 않을 수 있다.

---

## 5. RoleBinding이란?

`RoleBinding`은 Role을 실제 대상에게 연결하는 리소스다.

대상은 보통 다음 중 하나다.

```text
User
Group
ServiceAccount
```

예를 들어 `dev` 네임스페이스의 `app-sa`라는 ServiceAccount에게 `pod-reader` Role을 주고 싶다고 해보자.

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

이 RoleBinding은 이런 뜻이다.

```text
dev 네임스페이스의 app-sa ServiceAccount에게
pod-reader Role을 연결한다
```

즉, 이제 `app-sa`는 `dev` 네임스페이스에서 Pod를 조회할 수 있다.

---

## 6. RoleBinding의 구성 요소

RoleBinding에서 중요한 부분은 두 가지다.

```text
subjects
roleRef
```

전체 YAML을 다시 보자.

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

### subjects

`subjects`는 권한을 받을 대상을 의미한다.

```yaml
subjects:
  - kind: ServiceAccount
    name: app-sa
    namespace: dev
```

이 뜻은 다음과 같다.

```text
dev 네임스페이스에 있는
app-sa ServiceAccount에게
권한을 주겠다
```

만약 사용자에게 권한을 주는 경우라면 이런 식이 될 수 있다.

```yaml
subjects:
  - kind: User
    name: seoyeon
    apiGroup: rbac.authorization.k8s.io
```

### roleRef

`roleRef`는 어떤 Role을 연결할지 지정한다.

```yaml
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

이 뜻은 다음과 같다.

```text
pod-reader라는 Role을 연결하겠다
```

정리하면 RoleBinding은 이렇게 읽으면 된다.

```text
subjects에게
roleRef 권한을 준다
```

---

## 7. 전체 흐름으로 보기

Role과 RoleBinding의 관계는 이렇게 볼 수 있다.

```text
ServiceAccount: app-sa
        ↓
RoleBinding
        ↓
Role: pod-reader
        ↓
pods get/list/watch 가능
```

또는 조금 더 문장처럼 보면 이렇다.

```text
app-sa라는 ServiceAccount가 있다.

pod-reader라는 Role이 있다.

RoleBinding으로 app-sa와 pod-reader를 연결한다.

그러면 app-sa는 pod-reader에 적힌 권한을 갖는다.
```

핵심은 이것이다.

```text
Role은 권한을 정의한다.
RoleBinding은 권한을 대상에게 붙인다.
```

---

## 8. 예제로 한 번에 만들기

이번에는 `dev` 네임스페이스에서 Pod 조회 권한을 가진 ServiceAccount를 만들어보자.

먼저 namespace를 만든다.

```bash
kubectl create namespace dev
```

ServiceAccount를 만든다.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
  namespace: dev
```

Role을 만든다.

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

RoleBinding을 만든다.

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

파일로 저장했다면 적용한다.

```bash
kubectl apply -f serviceaccount.yaml
kubectl apply -f role.yaml
kubectl apply -f rolebinding.yaml
```

---

## 9. 권한 확인하기

권한이 제대로 들어갔는지 확인하려면 `kubectl auth can-i`를 사용한다.

현재 사용자가 Pod를 조회할 수 있는지 보려면 이렇게 한다.

```bash
kubectl auth can-i get pods -n dev
```

ServiceAccount 기준으로 확인하려면 이렇게 한다.

```bash
kubectl auth can-i get pods \
  --as=system:serviceaccount:dev:app-sa \
  -n dev
```

결과가 `yes`면 권한이 있는 것이다.

```text
yes
```

삭제 권한이 있는지도 확인해보자.

```bash
kubectl auth can-i delete pods \
  --as=system:serviceaccount:dev:app-sa \
  -n dev
```

아까 Role에서 `delete` 권한은 주지 않았기 때문에 결과는 보통 이렇게 나온다.

```text
no
```

이렇게 확인하면 Role이 제대로 제한적으로 적용됐는지 볼 수 있다.

---

## 10. Role은 namespace 범위다

Role에서 중요한 특징이 있다.

`Role`은 namespace 범위의 권한이다.

예를 들어 아래 Role은 `dev` 네임스페이스에 만들어졌다.

```yaml
metadata:
  name: pod-reader
  namespace: dev
```

그러면 이 Role은 `dev` 네임스페이스 안에서만 의미가 있다.

즉, `app-sa`가 `dev`에서는 Pod를 조회할 수 있어도, `prod`에서는 조회하지 못할 수 있다.

```text
dev namespace
→ pods 조회 가능

prod namespace
→ 권한 없음
```

확인해보면 이런 식이다.

```bash
kubectl auth can-i get pods \
  --as=system:serviceaccount:dev:app-sa \
  -n dev
```

```text
yes
```

```bash
kubectl auth can-i get pods \
  --as=system:serviceaccount:dev:app-sa \
  -n prod
```

```text
no
```

이게 Role과 RoleBinding의 핵심 범위다.

```text
Role + RoleBinding
→ 특정 namespace 안에서 권한 부여
```

---

## 11. RoleBinding은 같은 namespace의 Role만 연결할까?

기본적으로 RoleBinding은 특정 namespace 안에 존재한다.

```yaml
metadata:
  name: app-sa-pod-reader-binding
  namespace: dev
```

이 RoleBinding은 `dev` 네임스페이스에서 권한을 부여한다.

보통은 같은 namespace에 있는 Role을 연결한다.

```yaml
roleRef:
  kind: Role
  name: pod-reader
```

하지만 RoleBinding이 꼭 Role만 참조할 수 있는 것은 아니다.

RoleBinding은 `ClusterRole`도 참조할 수 있다.

```yaml
roleRef:
  kind: ClusterRole
  name: view
  apiGroup: rbac.authorization.k8s.io
```

이 경우 의미는 이렇다.

```text
ClusterRole에 정의된 권한을
RoleBinding이 있는 namespace 안에서만 적용
```

즉, `ClusterRole + RoleBinding` 조합도 가능하다.

이 방식은 공통 권한 템플릿을 여러 namespace에 재사용할 때 자주 사용된다.

---

## 12. Role과 ClusterRole 차이 잠깐 보기

Role을 이해하다 보면 자연스럽게 ClusterRole과 비교하게 된다.

| 구분           | Role                  | ClusterRole                       |
| ------------ | --------------------- | --------------------------------- |
| 범위           | namespace 안           | cluster 전체                        |
| namespace 지정 | 있음                    | 없음                                |
| 사용 예시        | dev namespace의 Pod 조회 | 모든 namespace의 Pod 조회              |
| 연결 방식        | RoleBinding           | ClusterRoleBinding 또는 RoleBinding |

Role은 특정 namespace에 종속된다.

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
  name: cluster-pod-reader
```

간단히 기억하면 된다.

```text
Role
→ namespace 안에서 쓰는 권한

ClusterRole
→ 클러스터 범위로 쓰는 권한
```

---

## 13. 자주 하는 실수

### 13.1 Role만 만들고 권한이 적용됐다고 생각하기

Role은 권한표일 뿐이다.

```text
Role 생성
→ 권한 내용만 정의됨

RoleBinding 생성
→ 실제 대상에게 권한 부여
```

Role을 만들었는데 권한이 안 먹는다면 RoleBinding이 있는지 확인해야 한다.

```bash
kubectl get rolebinding -n dev
```

---

### 13.2 RoleBinding의 namespace를 잘못 지정하기

RoleBinding은 namespace 범위다.

예를 들어 `dev`에 권한을 주고 싶은데 RoleBinding을 `default`에 만들면 원하는 대로 동작하지 않을 수 있다.

```bash
kubectl get rolebinding -n dev
kubectl get rolebinding -n default
```

권한이 적용되는 namespace를 반드시 확인해야 한다.

---

### 13.3 ServiceAccount namespace를 빼먹기

ServiceAccount는 namespace에 속한다.

그래서 RoleBinding에서 ServiceAccount를 subject로 지정할 때 namespace를 명확히 쓰는 게 좋다.

```yaml
subjects:
  - kind: ServiceAccount
    name: app-sa
    namespace: dev
```

특히 같은 이름의 ServiceAccount가 여러 namespace에 있을 수 있기 때문에 주의해야 한다.

---

### 13.4 verbs를 너무 넓게 주기

귀찮다고 모든 권한을 줄 수도 있다.

```yaml
verbs: ["*"]
```

또는 모든 리소스에 권한을 줄 수도 있다.

```yaml
resources: ["*"]
```

이건 편하지만 위험하다.

운영 환경에서는 필요한 권한만 주는 것이 좋다.

```yaml
resources: ["pods"]
verbs: ["get", "list", "watch"]
```

이런 식으로 최소 권한을 주는 것이 안전하다.

---

## 14. 실무에서는 어떻게 쓰일까?

예를 들어 어떤 애플리케이션 Pod가 자기 namespace의 Pod 목록만 조회하면 된다고 하자.

이때 굳이 클러스터 전체 권한을 줄 필요가 없다.

```text
필요한 작업
→ dev namespace의 Pod 조회

필요 없는 작업
→ prod namespace 접근
→ Secret 조회
→ Deployment 삭제
→ Node 수정
```

이럴 때는 다음 조합을 쓰면 된다.

```text
ServiceAccount
Role
RoleBinding
```

구조는 이렇다.

```text
app-pod
  ↓
app-sa
  ↓
RoleBinding
  ↓
Role
  ↓
dev namespace에서 pods get/list/watch 가능
```

이렇게 하면 Pod는 필요한 만큼만 Kubernetes API를 사용할 수 있다.

---

## 15. 한 줄씩 외우기

처음에는 이렇게 외우면 된다.

```text
Role
→ 권한 목록

RoleBinding
→ 권한을 누구에게 줄지 연결

subjects
→ 권한을 받을 대상

roleRef
→ 연결할 Role

verbs
→ 허용할 동작

resources
→ 권한을 줄 리소스

namespace
→ 이 권한이 적용되는 공간
```

더 짧게 줄이면 이렇다.

```text
Role = What
RoleBinding = Who
```

Role은 “무엇을 할 수 있는가”를 정의한다.

RoleBinding은 “누가 그 권한을 갖는가”를 정한다.

---

## 16. 정리

쿠버네티스의 Role과 RoleBinding은 RBAC 권한관리의 기본이다.

Role은 권한 내용을 정의한다.

```text
pods를 get/list/watch 할 수 있다
```

RoleBinding은 그 권한을 특정 대상에게 연결한다.

```text
app-sa에게 pod-reader 권한을 준다
```

전체 흐름은 이렇게 정리할 수 있다.

```text
ServiceAccount 또는 User
        ↓
RoleBinding
        ↓
Role
        ↓
실제 권한
```

마지막으로 이렇게 기억하면 된다.

> Role은 권한표이고, RoleBinding은 그 권한표를 사용자나 ServiceAccount에게 붙이는 연결고리다.
