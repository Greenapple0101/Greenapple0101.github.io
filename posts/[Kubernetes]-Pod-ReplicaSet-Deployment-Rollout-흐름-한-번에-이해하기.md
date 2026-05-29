---
title: "[KUBERNETES] Pod, ReplicaSet, Deployment, Rollout 흐름 한 번에 이해하기"
source: "https://velog.io/@yorange50/KUBERNETES-Pod-ReplicaSet-Deployment-Rollout-흐름-한-번에-이해하기"
published: "2026-05-18T08:40:42.096Z"
tags: ""
backup_date: "2026-05-29T14:52:52.729106"
---

쿠버네티스를 처음 보면 `pod.yaml`, `deploy.yaml`, `service.yaml` 같은 YAML 파일을 계속 만나게 된다. 처음에는 이 파일들이 전부 다르게 생긴 것처럼 보이지만, 계속 보다 보면 구조가 거의 비슷하다는 걸 알 수 있다. 쿠버네티스 매니페스트는 결국 “내가 원하는 상태를 YAML로 선언하는 문서”이고, 쿠버네티스는 그 선언을 보고 실제 클러스터 상태를 맞추려고 계속 움직인다. 이번 글에서는 Pod부터 ReplicationController, ReplicaSet, Deployment, Rollout까지 이어지는 흐름을 정리해본다. 실습 파일에서도 Pod 생성, ReplicationController, ReplicaSet, Deployment, Rollout 순서로 학습 흐름이 잡혀 있다. 

---

## 1. Manifest란?

쿠버네티스에서 `pod.yaml` 같은 파일을 매니페스트라고 부른다.

매니페스트는 쿠버네티스에게 다음과 같이 말하는 문서다.

```text
이런 리소스를 만들어줘.
이런 이름으로 만들어줘.
이런 이미지로 컨테이너를 띄워줘.
복제본은 3개 유지해줘.
```

즉, 명령형으로 하나하나 실행하는 것이 아니라 YAML 파일에 원하는 상태를 선언해두는 방식이다.

예를 들어 Pod 매니페스트는 이런 식이다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-nginx
  labels:
    app: nginx
    app2: nginx-my
spec:
  containers:
    - name: nginx
      image: nginx:latest
```

처음 보면 복잡해 보이지만 크게 보면 항상 이 구조다.

```yaml
apiVersion:
kind:
metadata:
spec:
```

이 네 가지가 기본 뼈대다.

---

## 2. apiVersion, kind, metadata, spec

### apiVersion

```yaml
apiVersion: v1
```

이 리소스가 어떤 쿠버네티스 API 버전을 사용하는지 나타낸다.

Pod는 보통 `v1`을 사용한다.

Deployment나 ReplicaSet은 보통 `apps/v1`을 사용한다.

```yaml
apiVersion: apps/v1
kind: Deployment
```

이 버전을 잘못 쓰면 에러가 난다. 그래서 리소스마다 맞는 `apiVersion`을 알아야 한다.

---

### kind

```yaml
kind: Pod
```

`kind`는 어떤 종류의 리소스를 만들 것인지 나타낸다.

예를 들면 다음과 같다.

```yaml
kind: Pod
kind: ReplicaSet
kind: Deployment
kind: Service
```

즉 `kind: Pod`라고 쓰면 Pod를 만들겠다는 뜻이고, `kind: Deployment`라고 쓰면 Deployment를 만들겠다는 뜻이다.

---

### metadata

```yaml
metadata:
  name: my-nginx
  labels:
    app: nginx
```

`metadata`는 리소스 자기 자신에 대한 정보다.

여기에는 보통 다음이 들어간다.

```text
이름
라벨
어노테이션
네임스페이스
```

예를 들어 `name: my-nginx`는 이 Pod의 이름이 `my-nginx`라는 뜻이다.

`labels`는 이 리소스에 붙이는 태그다.

```yaml
labels:
  app: nginx
  app2: nginx-my
```

이 라벨은 사용자가 직접 정하는 값이다. 쿠버네티스가 “반드시 app이라는 이름을 써라”라고 강제하는 게 아니다. 내가 구분하기 쉽게 붙이는 태그라고 보면 된다.

---

### spec

```yaml
spec:
  containers:
    - name: nginx
      image: nginx:latest
```

`spec`은 이 리소스를 어떻게 만들지에 대한 실제 스펙이다.

Pod라면 어떤 컨테이너를 띄울지, 어떤 이미지를 쓸지, 포트는 무엇인지 등을 적는다.

Deployment라면 복제본을 몇 개 만들지, 어떤 Pod를 만들지, 어떤 라벨을 가진 Pod를 관리할지 등을 적는다.

정리하면 이렇다.

```text
metadata: 이 리소스 자기 자신에 대한 정보
spec: 이 리소스를 어떻게 동작시킬지에 대한 정보
```

---

## 3. Pod란?

Pod는 쿠버네티스에서 가장 작은 실행 단위다.

쿠버네티스는 컨테이너를 직접 관리하는 것처럼 보이지만, 정확히는 Pod를 관리한다. 그리고 그 Pod 안에 컨테이너가 들어간다.

```text
Pod
 └── Container
```

가장 단순한 구조는 Pod 하나에 컨테이너 하나가 들어가는 것이다.

예를 들어 nginx 컨테이너 하나를 띄우는 Pod는 다음과 같다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-nginx
  labels:
    app: nginx
spec:
  containers:
    - name: nginx
      image: nginx:latest
```

여기서 중요한 부분은 이거다.

```yaml
containers:
  - name: nginx
    image: nginx:latest
```

`image: nginx:latest`는 nginx 이미지를 사용하겠다는 뜻이다.

`name: nginx`는 이 컨테이너의 이름을 nginx로 하겠다는 뜻이다.

즉, nginx라는 이미지를 기반으로 nginx라는 이름의 컨테이너를 Pod 안에 띄우는 것이다.

---

## 4. Label과 Selector

쿠버네티스에서 정말 중요한 개념이 Label과 Selector다.

### Label

Label은 리소스에 붙이는 태그다.

```yaml
labels:
  app: nginx
```

이건 “이 Pod는 app=nginx라는 라벨을 가진다”는 뜻이다.

라벨은 사용자가 마음대로 만들 수 있다.

```yaml
labels:
  app: nginx
  tier: frontend
  env: dev
```

이런 식으로 붙일 수 있다.

---

### Selector

Selector는 라벨을 기준으로 대상을 찾는 조건이다.

예를 들어 다음과 같은 selector가 있다고 하자.

```yaml
selector:
  app: nginx
```

이 뜻은 다음과 같다.

```text
app=nginx 라벨을 가진 Pod를 찾아서 관리하겠다.
```

쿠버네티스는 이름으로만 리소스를 관리하지 않는다. 특히 ReplicaSet, Deployment, Service 같은 리소스는 라벨과 셀렉터를 이용해서 “내가 관리해야 할 Pod가 누구인지” 찾는다.

그래서 라벨과 셀렉터가 서로 맞지 않으면 리소스가 Pod를 제대로 찾지 못한다.

---

## 5. ReplicationController란?

Pod 하나만 만들면 문제가 있다.

Pod는 언제든 죽을 수 있다.

컨테이너가 에러로 종료될 수도 있고, 노드에 문제가 생길 수도 있다.

이때 사람이 매번 다시 Pod를 만들어야 한다면 운영이 너무 불안정하다.

그래서 나온 개념이 ReplicationController다.

ReplicationController는 이름 그대로 복제본을 만들고 그 개수를 유지하는 컨트롤러다.

예를 들어 다음과 같은 설정이 있다고 하자.

```yaml
spec:
  replicas: 3
```

이 뜻은 다음과 같다.

```text
Pod를 항상 3개 유지해라.
```

전체 예시는 다음과 같다.

```yaml
apiVersion: v1
kind: ReplicationController
metadata:
  name: my-nginx
spec:
  replicas: 3
  selector:
    app: nginx
  template:
    metadata:
      name: nginx
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:latest
          ports:
            - containerPort: 80
```

여기서 중요한 부분은 세 가지다.

```yaml
replicas: 3
selector:
  app: nginx
template:
```

---

## 6. template은 무엇인가?

ReplicationController 안에 있는 `template`은 Pod를 만들기 위한 설계도다.

```yaml
template:
  metadata:
    name: nginx
    labels:
      app: nginx
  spec:
    containers:
      - name: nginx
        image: nginx:latest
```

이 부분은 사실상 Pod 매니페스트와 비슷하다.

즉 ReplicationController는 이렇게 동작한다.

```text
1. selector로 자신이 관리할 Pod를 찾음
2. replicas 개수만큼 Pod가 있는지 확인함
3. 부족하면 template을 보고 Pod를 새로 만듦
4. 많으면 줄임
```

그래서 `template`은 “어떤 Pod를 만들 것인가”에 대한 정의라고 보면 된다.

---

## 7. 왜 Pod 이름 뒤에 난수가 붙을까?

ReplicationController로 Pod를 3개 만들면 이름이 이런 식으로 나온다.

```text
my-nginx-g8w2q
my-nginx-k2p9x
my-nginx-v7m1a
```

뒤에 이상한 난수가 붙는다.

이유는 간단하다.

Pod는 같은 이름을 가질 수 없다.

그런데 ReplicationController는 같은 template으로 Pod를 여러 개 만들어야 한다. 그래서 기본 이름 뒤에 고유한 난수를 붙여서 서로 다른 Pod 이름을 만든다.

즉 “nginx Pod 3개”를 만들지만, 실제 Pod 이름은 각각 고유해야 하기 때문에 뒤에 난수가 붙는 것이다.

---

## 8. Desired, Current, Ready

ReplicaSet이나 Deployment를 조회하면 이런 값들이 나온다.

```text
DESIRED   CURRENT   READY
3         3         3
```

각각의 의미는 다음과 같다.

### Desired

원하는 개수다.

```text
나는 Pod 3개를 원한다.
```

### Current

현재 만들어져 있는 개수다.

```text
현재 Pod가 3개 있다.
```

### Ready

정상적으로 준비된 개수다.

```text
정상적으로 요청을 받을 수 있는 Pod가 3개다.
```

예를 들어 이런 상태라면 문제가 있다.

```text
DESIRED   CURRENT   READY
3         3         2
```

Pod 3개는 만들어졌지만, 그중 1개는 아직 정상 상태가 아니라는 뜻이다.

또 이런 상태도 가능하다.

```text
DESIRED   CURRENT   READY
3         2         2
```

이 경우는 원하는 개수는 3개인데 현재 2개밖에 없다는 뜻이다.

그러면 쿠버네티스는 다시 Pod를 하나 더 만들려고 한다.

이게 쿠버네티스의 핵심이다.

```text
원하는 상태와 현재 상태를 계속 비교하고, 원하는 상태에 맞추려고 한다.
```

---

## 9. ReplicationController를 지워야 Pod가 사라지는 이유

ReplicationController가 관리하는 Pod를 하나 직접 지워도 다시 생긴다.

왜냐하면 ReplicationController 입장에서는 이런 상황이 된다.

```text
원하는 개수: 3
현재 개수: 2
```

그러면 다시 3개를 맞추기 위해 Pod를 하나 더 만든다.

그래서 근본적으로 없애려면 Pod만 지우면 안 된다.

ReplicationController 자체를 삭제해야 한다.

```bash
kubectl delete -f rc.yaml
```

또는

```bash
kubectl delete replicationcontroller my-nginx
```

이렇게 컨트롤러를 지워야 그 컨트롤러가 관리하던 Pod들도 같이 정리된다.

---

## 10. ReplicaSet이란?

ReplicaSet은 ReplicationController와 비슷하다.

둘 다 Pod 복제본을 유지한다.

차이는 ReplicaSet이 더 발전된 selector를 사용할 수 있다는 점이다.

예를 들어 ReplicaSet은 이런 식으로 쓴다.

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: my-nginx
  labels:
    app: nginx
    tier: frontend
spec:
  replicas: 3
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
          image: nginx:latest
          ports:
            - containerPort: 80
```

여기서 selector는 다음과 같다.

```yaml
selector:
  matchLabels:
    tier: frontend
```

이 뜻은 다음과 같다.

```text
tier=frontend 라벨을 가진 Pod를 관리하겠다.
```

그리고 template 안의 Pod 라벨도 똑같이 맞춰져 있다.

```yaml
template:
  metadata:
    labels:
      tier: frontend
```

이게 중요하다.

ReplicaSet의 selector와 Pod template의 label이 서로 맞아야 한다.

안 맞으면 ReplicaSet이 자신이 만든 Pod를 제대로 찾지 못한다.

---

## 11. 라벨이 왜 두 군데 있어야 할까?

ReplicaSet이나 Deployment YAML을 보면 라벨이 두 군데 나온다.

```yaml
selector:
  matchLabels:
    app: nginx

template:
  metadata:
    labels:
      app: nginx
```

처음 보면 왜 같은 걸 두 번 쓰는지 헷갈린다.

하지만 역할이 다르다.

### selector 쪽 라벨

```yaml
selector:
  matchLabels:
    app: nginx
```

이건 “어떤 Pod를 관리할 것인가”를 찾는 조건이다.

### template 쪽 라벨

```yaml
template:
  metadata:
    labels:
      app: nginx
```

이건 “앞으로 만들 Pod에 어떤 라벨을 붙일 것인가”다.

즉 정리하면 이렇다.

```text
selector: 내가 찾을 Pod의 조건
template.metadata.labels: 내가 만들 Pod에 붙일 라벨
```

둘이 서로 맞아야 한다.

---

## 12. matchLabels와 matchExpressions

ReplicaSet은 `matchLabels`뿐 아니라 `matchExpressions`도 사용할 수 있다.

### matchLabels

단순한 라벨 매칭이다.

```yaml
selector:
  matchLabels:
    tier: frontend
```

뜻은 다음과 같다.

```text
tier=frontend인 Pod를 찾아라.
```

---

### matchExpressions

조금 더 복잡한 조건을 걸 수 있다.

```yaml
selector:
  matchExpressions:
    - key: env
      operator: NotIn
      values:
        - production
```

뜻은 다음과 같다.

```text
env 라벨 값이 production이 아닌 Pod를 찾아라.
```

이런 식으로 여러 조건을 조합할 수 있다.

다만 실제로는 ReplicaSet을 직접 작성하는 경우보다 Deployment를 사용하는 경우가 훨씬 많다.

---

## 13. Deployment란?

Deployment는 실무에서 가장 많이 쓰는 리소스다.

Pod를 직접 만들 수도 있고, ReplicaSet을 직접 만들 수도 있지만 일반적으로는 Deployment를 사용한다.

Deployment는 내부적으로 ReplicaSet을 만들고, ReplicaSet이 Pod를 만든다.

구조는 이렇게 보면 된다.

```text
Deployment
  └── ReplicaSet
        └── Pod
```

Deployment 매니페스트 예시는 다음과 같다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  selector:
    matchLabels:
      app: nginx
  replicas: 3
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.17
          ports:
            - containerPort: 80
```

여기서도 구조는 비슷하다.

```text
metadata: Deployment 자기 자신에 대한 정보
spec: Deployment가 어떻게 동작할지에 대한 정보
template: Deployment가 만들 Pod의 설계도
```

---

## 14. Deployment 안에 spec이 두 번 나오는 이유

Deployment YAML을 보면 `spec`이 두 번 나온다.

```yaml
spec:
  selector:
    matchLabels:
      app: nginx
  replicas: 3
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.17
```

처음 보는 사람 입장에서는 “왜 spec이 두 개지?” 싶다.

이유는 계층이 다르기 때문이다.

첫 번째 `spec`은 Deployment의 스펙이다.

```yaml
spec:
  selector:
  replicas:
  template:
```

이건 Deployment에게 말하는 것이다.

```text
너는 app=nginx인 Pod를 관리하고,
복제본은 3개 유지하고,
Pod는 아래 template대로 만들어라.
```

두 번째 `spec`은 Pod의 스펙이다.

```yaml
template:
  spec:
    containers:
      - name: nginx
        image: nginx:1.17
```

이건 Pod에게 말하는 것이다.

```text
이 Pod 안에는 nginx 컨테이너를 띄워라.
```

즉 이렇게 나눠서 보면 된다.

```text
Deployment spec: Deployment가 어떻게 관리할지
Pod template spec: Pod 안에 어떤 컨테이너를 띄울지
```

---

## 15. Deployment를 만들면 ReplicaSet이 생긴다

Deployment를 생성하면 바로 Pod만 생기는 게 아니다.

중간에 ReplicaSet이 만들어진다.

```bash
kubectl get deploy
kubectl get rs
kubectl get pod
```

이렇게 보면 구조가 보인다.

```text
Deployment 생성
→ ReplicaSet 생성
→ Pod 생성
```

그래서 Deployment는 단순히 Pod를 만드는 도구가 아니라, Pod의 배포 상태와 버전 관리를 담당하는 상위 리소스라고 볼 수 있다.

---

## 16. kubectl apply와 unchanged

매니페스트 파일을 적용할 때 보통 이렇게 한다.

```bash
kubectl apply -f pod.yaml
```

그런데 이미 같은 내용이 적용되어 있으면 이런 메시지가 나온다.

```text
unchanged
```

이건 에러가 아니다.

`apply`는 현재 클러스터에 적용된 내용과 내가 다시 적용하려는 YAML을 비교한다.

변경된 내용이 없으면 다시 만들지 않고 `unchanged`라고 알려준다.

즉 이런 뜻이다.

```text
이미 같은 상태라서 바꿀 게 없음.
```

이게 선언형 방식의 장점이다.

같은 YAML을 여러 번 적용해도 결과가 동일하게 유지된다.

---

## 17. Annotation이란?

Annotation은 리소스에 붙이는 부가 정보다.

Label과 비슷해 보이지만 목적이 다르다.

### Label

Label은 선택과 필터링에 사용한다.

```yaml
labels:
  app: nginx
```

예를 들면 이런 식으로 조회할 수 있다.

```bash
kubectl get pods -l app=nginx
```

즉 Label은 쿠버네티스가 리소스를 찾고 묶을 때 사용한다.

---

### Annotation

Annotation은 설명이나 부가 정보를 저장할 때 사용한다.

```yaml
annotations:
  kubernetes.io/change-cause: "image updated to 1.18"
```

이 값은 selector로 찾기 위한 목적이라기보다는, 사람이 보거나 시스템이 참고할 메타데이터에 가깝다.

---

## 18. apply와 Annotation의 관계

`kubectl apply`는 내부적으로 마지막으로 적용한 설정을 저장한다.

예전에는 `kubectl.kubernetes.io/last-applied-configuration` 같은 Annotation에 적용된 설정이 들어갔다.

그래서 매니페스트가 너무 커지면 Annotation도 커질 수 있다.

Annotation이 너무 커지면 쿠버네티스 제한에 걸려 에러가 날 수 있다.

특히 리소스 내용이 1MB를 넘는 식으로 커지면 문제가 생길 수 있다.

그래서 `apply`는 편하지만, 너무 큰 매니페스트나 복잡한 리소스에서는 Annotation 크기 문제도 생각해야 한다.

---

## 19. kubectl get -l, --show-labels

라벨을 기준으로 Pod를 조회할 수 있다.

```bash
kubectl get pods -l app=nginx
```

이 명령어는 다음 뜻이다.

```text
app=nginx 라벨을 가진 Pod만 보여줘.
```

라벨까지 같이 보고 싶으면 다음 명령어를 쓴다.

```bash
kubectl get pods --show-labels
```

그러면 Pod마다 어떤 라벨이 붙어 있는지 볼 수 있다.

이 명령어는 ReplicaSet이나 Service 문제를 디버깅할 때 중요하다.

왜냐하면 쿠버네티스는 라벨과 셀렉터로 리소스를 연결하기 때문이다.

---

## 20. Pod 안에 컨테이너는 여러 개 넣을 수 있을까?

가능하다.

Pod의 `containers`는 배열이다.

```yaml
spec:
  containers:
    - name: app
      image: my-app
    - name: sidecar
      image: log-agent
```

즉 Pod 하나 안에 컨테이너를 여러 개 넣을 수 있다.

하지만 일반적으로는 “1 Pod 1 Container”가 권장되는 경우가 많다.

---

## 21. 왜 1 Pod 1 Container를 권장할까?

Pod 하나에 여러 컨테이너를 넣으면 관리가 어려워질 수 있다.

예를 들어 Pod 하나 안에 nginx, tomcat, java app을 다 넣었다고 해보자.

문제가 생겼을 때 확인해야 할 것이 많아진다.

```text
nginx가 죽었나?
tomcat이 죽었나?
java app이 죽었나?
서로 영향을 줬나?
로그는 어디를 봐야 하나?
```

또 스케일링도 애매해진다.

트래픽이 많아져서 Java 애플리케이션만 늘리고 싶은데, nginx와 tomcat까지 같이 묶여 있으면 전체 Pod를 같이 늘려야 한다.

반면 1 Pod 1 Container 구조라면 각각을 독립적으로 관리하기 쉽다.

```text
장애 원인 파악 쉬움
로그 확인 쉬움
스케일링 쉬움
리소스 분리 쉬움
운영 단위 명확함
```

그래서 일반적인 애플리케이션은 1 Pod 1 Container 구조로 가는 게 운영상 편하다.

---

## 22. 그러면 여러 컨테이너 Pod는 언제 쓸까?

대표적인 경우가 Sidecar 패턴이다.

Sidecar는 말 그대로 오토바이 옆에 붙은 보조 좌석 같은 개념이다.

주인공은 메인 컨테이너다.

옆에서 보조 역할을 하는 컨테이너가 Sidecar다.

구조는 이런 식이다.

```text
Pod
 ├── Main Container
 └── Sidecar Container
```

예를 들어 메인 컨테이너가 애플리케이션 서버라고 하자.

그리고 그 애플리케이션이 로그 파일을 남긴다.

이때 Sidecar 컨테이너가 그 로그 파일을 읽어서 외부 로그 시스템으로 전송할 수 있다.

```text
Main Container: 애플리케이션 실행
Sidecar Container: 로그 수집 및 전송
```

이런 구조가 가능한 이유는 같은 Pod 안의 컨테이너들이 일부 리소스를 공유할 수 있기 때문이다.

대표적으로 다음을 공유할 수 있다.

```text
네트워크
볼륨
라이프사이클
```

그래서 Sidecar는 메인 컨테이너를 보조하는 역할에 적합하다.

---

## 23. Sidecar 예시

대표적인 Sidecar 예시는 다음과 같다.

```text
로그 수집 컨테이너
프록시 컨테이너
보안 인증 보조 컨테이너
설정 동기화 컨테이너
```

예를 들어 서비스 메시에서 Envoy Proxy가 Sidecar로 붙는 경우가 있다.

애플리케이션 컨테이너는 자기 일만 하고, 네트워크 트래픽 제어는 Envoy 같은 프록시가 대신 처리하는 구조다.

```text
Pod
 ├── Application Container
 └── Envoy Proxy Container
```

이렇게 하면 애플리케이션 코드에 직접 네트워크 제어 로직을 넣지 않아도 된다.

---

## 24. cAdvisor도 Sidecar인가?

일반적으로 cAdvisor는 Sidecar라고 보기는 어렵다.

Sidecar는 보통 특정 Pod 안에서 메인 컨테이너를 보조하는 컨테이너를 말한다.

반면 cAdvisor는 컨테이너의 리소스 사용량을 수집하는 모니터링 컴포넌트에 가깝다.

다만 “주 애플리케이션이 아닌 관측/보조 역할”이라는 느낌에서는 Sidecar와 비슷하게 느껴질 수 있다.

정리하면 이렇다.

```text
Sidecar: 특정 Pod 안에서 메인 컨테이너를 보조
cAdvisor: 노드/컨테이너 리소스 메트릭 수집
```

---

## 25. Pod는 어느 노드에 뜰까?

Pod를 여러 개 만들었다고 해서 전부 같은 서버에 뜨는 것은 아니다.

쿠버네티스는 스케줄러를 통해 Pod를 적절한 노드에 배치한다.

예를 들어 nginx Pod가 4개 있다고 하자.

```text
nginx-pod-1
nginx-pod-2
nginx-pod-3
nginx-pod-4
```

이 Pod들이 전부 같은 노드에 있을 수도 있지만, 보통은 여러 노드에 나뉘어 배치될 수 있다.

```text
Node1: nginx-pod-1, nginx-pod-2
Node2: nginx-pod-3
Node3: nginx-pod-4
```

쿠버네티스는 CPU, Memory 같은 리소스 상황을 보고 적절한 곳에 Pod를 배치한다.

이런 방식이 서버 자원을 효율적으로 채워 넣는 빈패킹과 연결된다.

---

## 26. Namespace는 논리적인 공간이다

Pod들이 물리적으로 같은 노드에 있지 않아도 같은 Namespace에 있을 수 있다.

Namespace는 물리적인 서버 개념이 아니라 논리적인 구분이다.

예를 들어 다음과 같은 Namespace를 만들 수 있다.

```text
default
dev
prod
monitoring
kube-system
```

`kube-system`에는 쿠버네티스 클러스터 운영에 필요한 시스템 Pod들이 들어간다.

예를 들면 CoreDNS 같은 것들이 있다.

---

## 27. Rollout이란?

Rollout은 Deployment의 배포 과정을 관리하는 기능이다.

예를 들어 nginx 이미지를 1.17에서 1.18로 바꾼다고 해보자.

```text
nginx:1.17 → nginx:1.18
```

이때 기존 Pod를 한 번에 다 죽이고 새 Pod를 만드는 것이 아니라, 기본적으로 Rolling Update 방식으로 점진적으로 교체한다.

즉 무중단 배포에 가깝게 동작한다.

---

## 28. Rolling Update

쿠버네티스 Deployment의 기본 업데이트 전략은 Rolling Update다.

이 방식은 기존 Pod를 조금씩 줄이고 새 버전 Pod를 조금씩 늘린다.

```text
기존 버전 Pod 일부 종료
새 버전 Pod 생성
정상 확인
다음 Pod 교체
```

이런 식으로 진행되기 때문에 서비스 중단 가능성을 줄일 수 있다.

---

## 29. rollout status

배포 진행 상태를 확인할 수 있다.

```bash
kubectl rollout status deploy/nginx-deployment
```

이 명령어는 Deployment의 업데이트가 정상적으로 진행 중인지 확인할 때 사용한다.

---

## 30. rollout history

배포 이력을 확인할 수 있다.

```bash
kubectl rollout history deploy/nginx-deployment
```

결과는 이런 식으로 나온다.

```text
REVISION  CHANGE-CAUSE
1         image updated to 1.17
2         image updated to 1.18
3         image updated to 1.19
```

여기서 `REVISION`은 배포 버전 번호다.

`CHANGE-CAUSE`는 어떤 변경이 있었는지 설명하는 값이다.

---

## 31. change-cause Annotation

Rollout history에서 변경 사유를 보기 위해 Annotation을 넣을 수 있다.

```bash
kubectl annotate deployment/nginx-deployment kubernetes.io/change-cause="image updated to 1.18"
```

또는 매니페스트에 직접 넣을 수도 있다.

```yaml
metadata:
  name: nginx-deployment
  annotations:
    kubernetes.io/change-cause: "image updated to 1.17"
```

이렇게 해두면 나중에 history를 봤을 때 어떤 버전에서 어떤 변경을 했는지 확인하기 쉽다.

---

## 32. kubectl set image

이미지만 바꾸고 싶을 때는 `set image` 명령어를 사용할 수 있다.

```bash
kubectl set image deployment/nginx-deployment nginx=nginx:1.18
```

이 명령어의 의미는 다음과 같다.

```text
nginx-deployment 안의 nginx 컨테이너 이미지를 nginx:1.18로 바꿔라.
```

여기서 앞의 `nginx`는 컨테이너 이름이고, 뒤의 `nginx:1.18`은 이미지 이름이다.

```bash
kubectl set image deployment/nginx-deployment nginx=nginx:1.18
```

구조를 나눠보면 이렇다.

```text
deployment/nginx-deployment: 수정할 Deployment
nginx: Deployment 안의 컨테이너 이름
nginx:1.18: 새 이미지
```

---

## 33. rollout undo

새 버전 배포 후 문제가 생기면 이전 버전으로 되돌릴 수 있다.

```bash
kubectl rollout undo deploy/nginx-deployment
```

이 명령어는 현재 Deployment를 바로 이전 Revision으로 되돌린다.

예를 들어 현재가 1.19이고 이전이 1.18이었다면, 다시 1.18로 돌아간다.

---

## 34. 특정 Revision으로 되돌리기

특정 Revision으로 되돌릴 수도 있다.

```bash
kubectl rollout undo deploy/nginx-deployment --to-revision=1
```

하지만 실무나 시험에서는 그냥 바로 이전 버전으로 되돌리는 `rollout undo`를 더 자주 보게 된다.

```bash
kubectl rollout undo deploy/nginx-deployment
```

---

## 35. rollout history는 어디까지 남을까?

Deployment는 ReplicaSet 이력을 일정 개수까지 보관한다.

기본적으로 과거 Revision을 무한히 다 저장하지 않는다.

보통 일정 개수만 남기고 오래된 이력은 정리된다.

그래서 history를 봤을 때 예전 Revision이 사라져 있을 수도 있다.

---

## 36. 전체 흐름 정리

쿠버네티스의 기본 리소스 흐름은 이렇게 잡으면 된다.

```text
Pod
```

가장 작은 실행 단위다.

```text
ReplicationController
```

Pod 복제본 수를 유지한다.

```text
ReplicaSet
```

ReplicationController와 비슷하지만 selector 표현력이 더 좋다.

```text
Deployment
```

ReplicaSet을 관리하고, 배포와 업데이트, 롤백을 담당한다.

```text
Rollout
```

Deployment의 배포 이력, 상태, 롤백을 관리한다.

구조로 보면 이렇게 된다.

```text
Deployment
  └── ReplicaSet
        └── Pod
              └── Container
```

---

## 37. 핵심 개념만 다시 정리

### Manifest

쿠버네티스 리소스를 YAML로 선언한 파일.

### metadata

리소스 자기 자신에 대한 정보.

### spec

리소스를 어떻게 만들고 동작시킬지에 대한 정보.

### label

리소스에 붙이는 태그.

### selector

라벨을 기준으로 리소스를 찾는 조건.

### template

컨트롤러가 Pod를 만들 때 사용하는 Pod 설계도.

### replicas

유지하고 싶은 Pod 개수.

### Deployment

ReplicaSet과 Pod를 관리하는 상위 배포 리소스.

### Rollout

Deployment의 배포 상태, 이력, 롤백을 관리하는 기능.

---

## 38. 최종적으로 이해해야 하는 한 문장

쿠버네티스는 YAML 매니페스트에 선언된 원하는 상태를 기준으로, 현재 상태를 계속 비교하면서 부족하면 만들고, 많으면 줄이고, 문제가 생기면 다시 맞추는 시스템이다.

그래서 Pod 하나를 직접 띄우는 것보다 Deployment로 선언하고, Deployment가 ReplicaSet을 만들고, ReplicaSet이 Pod를 유지하는 흐름을 이해하는 게 중요하다.

결국 쿠버네티스의 기본은 이 구조다.

```text
원하는 상태 선언
→ 현재 상태 확인
→ 차이 감지
→ 원하는 상태로 복구
```

그리고 그 중심에 있는 것이 바로 다음 개념들이다.

```text
Manifest
Label
Selector
Template
ReplicaSet
Deployment
Rollout
```
