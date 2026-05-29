---
title: "[Kubernetes] ReplicaSet YAML에서 selector와 template label은 왜 같아야 할까?"
source: "https://velog.io/@yorange50/Kubernetes-ReplicaSet-YAML에서-selector와-template-label은-왜-같아야-할까"
published: "2026-05-13T08:49:01.720Z"
tags: ""
backup_date: "2026-05-29T14:52:52.744283"
---

Kubernetes에서 `ReplicaSet`을 만들다 보면 이런 YAML을 자주 만나게 된다.

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: replicaset-2
spec:
  replicas: 2
  selector:
    matchLabels:
      tier: frontend
  template:
    metadata:
      labels:
        tier: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
```

겉으로 보면 큰 문제 없어 보인다.

`ReplicaSet`을 만들고, `replicas: 2`니까 Pod를 2개 만들고, 컨테이너는 `nginx` 이미지를 사용하겠다는 뜻처럼 보인다.

그런데 이 YAML에는 중요한 오류가 있다.

바로 이 부분이다.

```yaml
selector:
  matchLabels:
    tier: frontend
```

그리고 이 부분이다.

```yaml
template:
  metadata:
    labels:
      tier: nginx
```

둘이 다르다.

```text
selector는 tier=frontend
template label은 tier=nginx
```

이게 왜 문제가 되는지 하나씩 뜯어보자.

---

## 1. ReplicaSet은 무엇을 하는 리소스일까?

`ReplicaSet`은 Pod 개수를 유지해주는 Kubernetes 리소스다.

예를 들어 아래처럼 적으면:

```yaml
replicas: 2
```

Kubernetes에게 이렇게 말하는 것이다.

```text
이 조건에 맞는 Pod가 항상 2개 떠 있게 해줘.
```

즉, Pod가 하나 죽으면 다시 하나를 만들고, Pod가 너무 많으면 줄인다.

ReplicaSet의 핵심 역할은 이것이다.

```text
원하는 개수만큼 Pod를 유지하는 것
```

---

## 2. ReplicaSet은 어떤 Pod를 자기 Pod라고 판단할까?

ReplicaSet은 아무 Pod나 관리하지 않는다.

자기가 관리할 Pod를 찾기 위해 `selector`를 사용한다.

```yaml
selector:
  matchLabels:
    tier: frontend
```

이 뜻은 다음과 같다.

```text
나는 tier=frontend 라벨을 가진 Pod를 관리할 거야.
```

즉, ReplicaSet은 클러스터 안에서 이런 라벨을 가진 Pod를 찾는다.

```yaml
labels:
  tier: frontend
```

이 조건에 맞는 Pod만 자기 관리 대상으로 본다.

---

## 3. template은 무엇일까?

`template`은 ReplicaSet이 새 Pod를 만들 때 사용할 Pod 설계도다.

```yaml
template:
  metadata:
    labels:
      tier: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
```

이 뜻은 다음과 같다.

```text
새 Pod를 만들 때 이 모양으로 만들어줘.
```

즉, ReplicaSet이 Pod를 새로 만들면 그 Pod에는 이런 라벨이 붙는다.

```yaml
labels:
  tier: nginx
```

그리고 그 안에는 `nginx` 컨테이너가 실행된다.

---

## 4. 지금 YAML의 진짜 문제

문제는 `selector`와 `template.metadata.labels`가 서로 다르다는 것이다.

현재 YAML은 이렇게 되어 있다.

```yaml
selector:
  matchLabels:
    tier: frontend
```

ReplicaSet은 이렇게 말한다.

```text
나는 tier=frontend인 Pod를 관리할 거야.
```

그런데 실제로 새로 만드는 Pod는 이렇게 되어 있다.

```yaml
template:
  metadata:
    labels:
      tier: nginx
```

즉, 새 Pod에는 이런 라벨이 붙는다.

```text
tier=nginx
```

결과적으로 이상한 상황이 된다.

```text
ReplicaSet: 나는 tier=frontend Pod를 찾을 거야.
ReplicaSet이 만든 Pod: 나는 tier=nginx야.
```

ReplicaSet이 직접 만든 Pod인데, 정작 ReplicaSet의 selector 조건에는 맞지 않는다.

즉, 자기 자식을 자기가 못 알아보는 구조가 된다.

그래서 Kubernetes는 이 YAML을 잘못된 설정으로 판단한다.

---

## 5. 왜 Kubernetes가 이걸 막을까?

만약 Kubernetes가 이 설정을 허용하면 문제가 생긴다.

ReplicaSet은 `tier=frontend` 라벨을 가진 Pod가 2개 있어야 한다고 생각한다.

```yaml
replicas: 2
selector:
  matchLabels:
    tier: frontend
```

그런데 새로 만드는 Pod는 `tier=nginx` 라벨을 가진다.

```yaml
template:
  metadata:
    labels:
      tier: nginx
```

그러면 ReplicaSet 입장에서는 이렇게 된다.

```text
tier=frontend인 Pod가 없네?
그럼 2개 만들어야지.
```

그래서 Pod를 만든다.

그런데 만들어진 Pod는 `tier=nginx`다.

ReplicaSet은 다시 본다.

```text
어? 아직도 tier=frontend인 Pod가 없네?
그럼 또 만들어야지.
```

이런 식으로 꼬일 수 있다.

그래서 Kubernetes는 ReplicaSet에서 반드시 이 조건을 요구한다.

```text
spec.selector.matchLabels는
spec.template.metadata.labels에 포함되어 있어야 한다.
```

쉽게 말하면:

```text
ReplicaSet이 찾는 라벨과
ReplicaSet이 만드는 Pod의 라벨이 맞아야 한다.
```

---

## 6. 고치는 방법 1: template label을 selector에 맞추기

가장 자연스러운 수정은 `template.metadata.labels`를 `selector.matchLabels`에 맞추는 것이다.

수정 전:

```yaml
selector:
  matchLabels:
    tier: frontend
template:
  metadata:
    labels:
      tier: nginx
```

수정 후:

```yaml
selector:
  matchLabels:
    tier: frontend
template:
  metadata:
    labels:
      tier: frontend
```

전체 YAML은 이렇게 된다.

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: replicaset-2
spec:
  replicas: 2
  selector:
    matchLabels:
      tier: frontend
  template:
    metadata:
      labels:
        tier: frontend
    spec:
      containers:
      - name: nginx
        image: nginx
```

이제 구조가 맞다.

```text
ReplicaSet이 찾는 Pod: tier=frontend
ReplicaSet이 만드는 Pod: tier=frontend
```

즉, ReplicaSet이 자기가 만든 Pod를 정상적으로 관리할 수 있다.

---

## 7. 고치는 방법 2: selector를 template label에 맞추기

반대로 `selector`를 `template.metadata.labels`에 맞춰도 된다.

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: replicaset-2
spec:
  replicas: 2
  selector:
    matchLabels:
      tier: nginx
  template:
    metadata:
      labels:
        tier: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
```

이 경우에는 ReplicaSet이 `tier=nginx`인 Pod를 관리한다.

```text
ReplicaSet이 찾는 Pod: tier=nginx
ReplicaSet이 만드는 Pod: tier=nginx
```

이것도 정상이다.

---

## 8. 그럼 name이 nginx인 건 상관없을까?

여기서 헷갈릴 수 있는 부분이 있다.

```yaml
containers:
- name: nginx
  image: nginx
```

이 부분의 `name: nginx`는 컨테이너 이름이다.

그리고 아래의 `tier: nginx`는 Pod 라벨이다.

```yaml
labels:
  tier: nginx
```

둘은 완전히 다른 의미다.

정리하면 이렇다.

| 위치                          | 의미                           |
| --------------------------- | ---------------------------- |
| `metadata.name`             | ReplicaSet 이름                |
| `spec.selector.matchLabels` | ReplicaSet이 관리할 Pod를 찾는 조건   |
| `template.metadata.labels`  | ReplicaSet이 새로 만들 Pod에 붙일 라벨 |
| `containers.name`           | Pod 안 컨테이너 이름                |
| `containers.image`          | 컨테이너 실행에 사용할 이미지             |

즉, 아래 부분은 오류가 아니다.

```yaml
containers:
- name: nginx
  image: nginx
```

이건 그냥 컨테이너 이름과 이미지 이름을 `nginx`로 설정한 것이다.

진짜 오류는 여기다.

```yaml
selector:
  matchLabels:
    tier: frontend
```

```yaml
template:
  metadata:
    labels:
      tier: nginx
```

`frontend`와 `nginx`가 서로 맞지 않는 것이 문제다.

---

## 9. ReplicaSet YAML을 볼 때 확인 순서

ReplicaSet YAML을 보면 먼저 이 순서로 보면 좋다.

### 1단계: 어떤 리소스인가?

```yaml
kind: ReplicaSet
```

ReplicaSet이다.

즉, Pod 개수를 유지하는 리소스다.

---

### 2단계: 몇 개를 유지하려고 하는가?

```yaml
replicas: 2
```

Pod를 2개 유지하려고 한다.

---

### 3단계: 어떤 Pod를 관리하려고 하는가?

```yaml
selector:
  matchLabels:
    tier: frontend
```

`tier=frontend` 라벨을 가진 Pod를 관리하려고 한다.

---

### 4단계: 새로 만들 Pod에는 어떤 라벨을 붙이는가?

```yaml
template:
  metadata:
    labels:
      tier: nginx
```

새로 만들 Pod에는 `tier=nginx` 라벨을 붙인다.

---

### 5단계: selector와 template label이 같은가?

```text
selector: tier=frontend
template label: tier=nginx
```

다르다.

그래서 오류다.

---

## 10. 핵심 정리

ReplicaSet에서 제일 중요한 관계는 이것이다.

```yaml
spec:
  selector:
    matchLabels:
      tier: frontend
  template:
    metadata:
      labels:
        tier: frontend
```

이 두 부분은 서로 맞아야 한다.

왜냐하면 ReplicaSet은 `selector`로 Pod를 찾고, `template`으로 Pod를 만들기 때문이다.

정리하면:

```text
selector = ReplicaSet이 관리할 Pod를 찾는 기준
template.metadata.labels = ReplicaSet이 만드는 Pod에 붙는 라벨
```

그래서 둘이 안 맞으면 ReplicaSet이 자기가 만든 Pod를 관리할 수 없게 된다.

이번 오류의 핵심은 이것이다.

```text
selector는 tier=frontend를 찾는데
template은 tier=nginx인 Pod를 만들려고 해서 오류
```

고치려면 둘 중 하나로 통일하면 된다.

```yaml
tier: frontend
```

또는

```yaml
tier: nginx
```

둘 다 가능하지만, 중요한 건 **selector와 template label이 서로 일치해야 한다는 것**이다.
