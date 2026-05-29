---
title: "[CKA] YAML이 무서우면 apiVersion부터 외우자"
source: "https://velog.io/@yorange50/CKA-YAML이-무서우면-apiVersion부터-외우자"
published: "2026-05-22T07:29:14.646Z"
tags: ""
backup_date: "2026-05-29T14:52:52.714863"
---

CKA를 공부하다 보면 YAML이 너무 많이 나온다.

```yaml
apiVersion:
kind:
metadata:
spec:
```

처음에는 이 구조 자체가 부담스럽다.

특히 이런 생각이 든다.

```text
이걸 다 외워야 하나?
공식문서에서 찾아야 하나?
시험장에서 기억 안 나면 어떡하지?
```

근데 YAML을 전부 외우려고 하면 금방 지친다.
대신 조금 더 현실적인 방법이 있다.

```text
apiVersion + kind까지만 빠르게 떠올리고,
spec 구조는 공식문서 예시를 찾아서 수정한다.
```

즉, YAML 전체를 통째로 외우는 게 아니라 **YAML의 입구를 외우는 방식**이다.

---

# 1. apiVersion이 뭐길래 중요할까

Kubernetes YAML은 보통 이렇게 시작한다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  ...
```

여기서 `apiVersion`은 이 리소스가 **Kubernetes API의 어느 그룹에 속하는지**를 나타낸다.

예를 들어 Deployment는 앱을 배포하고 관리하는 리소스다.

그래서:

```yaml
apiVersion: apps/v1
kind: Deployment
```

이렇게 쓴다.

HPA는 autoscaling 계열 리소스다.

그래서:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
```

이렇게 쓴다.

Gateway API는 gateway networking 계열이다.

그래서:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
```

이렇게 쓴다.

이걸 알고 있으면 공식문서 검색창에 바로 이런 식으로 칠 수 있다.

```text
autoscaling/v2
gateway.networking.k8s.io/v1
networking.k8s.io/v1
```

그러면 해당 리소스 예시 YAML을 찾기가 훨씬 쉬워진다.

---

# 2. CKA에서 외워두면 좋은 apiVersion

## HPA

```text
HPA → autoscaling/v2
```

예시:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
```

HPA는 HorizontalPodAutoscaler의 줄임말이다.
부하에 따라 Deployment 같은 리소스의 Pod 개수를 자동으로 늘리거나 줄인다.

HPA 문제에서는 보통 이런 조건이 나온다.

```text
CPU 50%
minReplicas: 1
maxReplicas: 4
target Deployment 지정
scaleDown stabilizationWindowSeconds 지정
```

그래서 공식문서 검색창에는 이렇게 치면 좋다.

```text
autoscaling/v2
horizontal pod autoscaler
stabilizationWindowSeconds
```

---

## Gateway API

```text
Gateway API → gateway.networking.k8s.io/v1
```

예시:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
```

또는:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
```

Gateway API 문제는 보통 Ingress를 Gateway, HTTPRoute로 바꾸는 식으로 나온다.

자주 보는 리소스는 이거다.

```text
GatewayClass
Gateway
HTTPRoute
```

검색 키워드:

```text
gateway.networking.k8s.io/v1
gateway api
httproute
```

Gateway는 입구를 만들고, HTTPRoute는 실제 라우팅 규칙을 연결한다고 보면 된다.

```text
Gateway
= 어떤 포트와 프로토콜로 받을지 정의

HTTPRoute
= 어떤 hostname/path 요청을 어느 Service로 보낼지 정의
```

---

## Ingress / NetworkPolicy

```text
Ingress/NetworkPolicy → networking.k8s.io/v1
```

Ingress 예시:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
```

NetworkPolicy 예시:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
```

둘 다 네트워킹 계열이라 `networking.k8s.io/v1`을 쓴다.

Ingress는 외부 HTTP/HTTPS 요청을 Service로 연결하는 리소스다.

```text
외부 요청
→ Ingress
→ Service
→ Pod
```

NetworkPolicy는 Pod 간 통신을 제한하는 리소스다.

```text
frontend Pod만 backend Pod에 접근 가능하게 하라
특정 namespace에서만 접근 가능하게 하라
특정 port만 허용하라
```

이런 문제가 나오면 NetworkPolicy다.

검색 키워드:

```text
networking.k8s.io/v1
ingress
networkpolicy
network policy
```

---

## Deployment

```text
Deployment → apps/v1
```

예시:

```yaml
apiVersion: apps/v1
kind: Deployment
```

Deployment는 Pod를 직접 관리하기보다 ReplicaSet을 통해 Pod 개수를 유지한다.

```text
Deployment
→ ReplicaSet
→ Pod
```

자주 나오는 조건:

```text
replicas
image
containerPort
selector
template labels
rollout
rollback
```

검색 키워드:

```text
apps/v1 deployment
deployment
rolling update deployment
```

Deployment는 CKA 기본기 중 기본기라 `apps/v1`은 꼭 외우는 게 좋다.

---

## Job / CronJob

```text
Job/CronJob → batch/v1
```

Job 예시:

```yaml
apiVersion: batch/v1
kind: Job
```

CronJob 예시:

```yaml
apiVersion: batch/v1
kind: CronJob
```

Job은 한 번 실행하고 끝나는 작업이다.

```text
데이터 처리
백업 작업
일회성 스크립트 실행
```

CronJob은 정해진 시간마다 반복 실행하는 작업이다.

```text
매 분 실행
매일 자정 실행
매주 실행
```

검색 키워드:

```text
batch/v1
job
cronjob
```

`batch`라는 단어를 보면 “아, 실행하고 끝나는 작업 계열이구나”라고 떠올리면 된다.

---

## Pod / Service / ConfigMap / Secret / PVC

```text
Pod/Service/ConfigMap/Secret/PVC → v1
```

예시:

```yaml
apiVersion: v1
kind: Pod
```

```yaml
apiVersion: v1
kind: Service
```

```yaml
apiVersion: v1
kind: ConfigMap
```

```yaml
apiVersion: v1
kind: Secret
```

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
```

기본 리소스들은 대부분 `v1`이다.

특히 CKA에서 자주 보는 것들:

```text
Pod
Service
ConfigMap
Secret
PersistentVolumeClaim
Namespace
ServiceAccount
PersistentVolume
```

이런 건 거의 `v1`로 시작한다고 보면 된다.

검색 키워드:

```text
pod
service
configmap
secret
persistent volume claim
```

---

# 3. apiVersion 치트시트

| 리소스           | apiVersion                     |
| ------------- | ------------------------------ |
| HPA           | `autoscaling/v2`               |
| Gateway API   | `gateway.networking.k8s.io/v1` |
| Gateway       | `gateway.networking.k8s.io/v1` |
| HTTPRoute     | `gateway.networking.k8s.io/v1` |
| Ingress       | `networking.k8s.io/v1`         |
| NetworkPolicy | `networking.k8s.io/v1`         |
| Deployment    | `apps/v1`                      |
| Job           | `batch/v1`                     |
| CronJob       | `batch/v1`                     |
| Pod           | `v1`                           |
| Service       | `v1`                           |
| ConfigMap     | `v1`                           |
| Secret        | `v1`                           |
| PVC           | `v1`                           |

조금 더 묶어서 보면 이렇다.

```text
HPA
→ autoscaling/v2

Gateway API
→ gateway.networking.k8s.io/v1

Ingress / NetworkPolicy
→ networking.k8s.io/v1

Deployment
→ apps/v1

Job / CronJob
→ batch/v1

Pod / Service / ConfigMap / Secret / PVC
→ v1
```

---

# 4. 이걸 어떻게 써먹을까

예를 들어 HPA 문제가 나왔다.

```text
Create a HorizontalPodAutoscaler named apache-server.
Target Deployment is apache-server.
CPU target is 50%.
minReplicas 1, maxReplicas 4.
```

그러면 바로 떠올린다.

```text
HPA니까 autoscaling/v2
```

YAML 시작:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: apache-server
```

그다음 공식문서에서 `autoscaling/v2`를 검색해서 예시를 찾는다.

그리고 문제 조건에 맞게 수정한다.

---

NetworkPolicy 문제가 나왔다.

```text
Allow ingress to backend only from frontend pods.
```

바로 떠올린다.

```text
NetworkPolicy니까 networking.k8s.io/v1
```

YAML 시작:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-frontend
```

그다음 공식문서에서 `networkpolicy`를 검색해서 `podSelector`, `ingress`, `from`, `ports` 구조를 가져온다.

---

Gateway API 문제가 나왔다.

```text
Create a Gateway and HTTPRoute.
```

바로 떠올린다.

```text
Gateway API니까 gateway.networking.k8s.io/v1
```

YAML 시작:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
```

또는:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
```

그다음 `gateway api`, `httproute`를 검색해서 `listeners`, `parentRefs`, `backendRefs` 구조를 가져온다.

---

# 5. apiVersion만 외우면 충분할까?

완전히 충분하진 않다.

예를 들어 이건 외울 수 있다.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
```

하지만 HPA의 진짜 핵심은 이 부분이다.

```yaml
spec:
  scaleTargetRef:
  minReplicas:
  maxReplicas:
  metrics:
  behavior:
```

NetworkPolicy도 마찬가지다.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
```

여기까지는 쉽다.

근데 진짜 어려운 건 여기다.

```yaml
spec:
  podSelector:
  policyTypes:
  ingress:
  - from:
    - podSelector:
    ports:
```

Gateway API도:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
```

여기까지보다 중요한 건:

```yaml
spec:
  parentRefs:
  hostnames:
  rules:
  - matches:
    backendRefs:
```

그래서 전략은 이거다.

```text
apiVersion + kind는 외워서 시작 속도를 높인다.
spec 구조는 공식문서 예시에서 가져온다.
```

이게 제일 현실적이다.

---

# 6. YAML 시작 템플릿

## HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: NAME
  namespace: NAMESPACE
spec:
```

## Gateway

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: NAME
  namespace: NAMESPACE
spec:
```

## HTTPRoute

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: NAME
  namespace: NAMESPACE
spec:
```

## Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: NAME
  namespace: NAMESPACE
spec:
```

## NetworkPolicy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: NAME
  namespace: NAMESPACE
spec:
```

## Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: NAME
  namespace: NAMESPACE
spec:
```

## Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: NAME
  namespace: NAMESPACE
spec:
```

## CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: NAME
  namespace: NAMESPACE
spec:
```

## Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: NAME
  namespace: NAMESPACE
spec:
```

## Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: NAME
  namespace: NAMESPACE
spec:
```

## ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: NAME
  namespace: NAMESPACE
data:
```

## Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: NAME
  namespace: NAMESPACE
type: Opaque
stringData:
```

## PVC

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: NAME
  namespace: NAMESPACE
spec:
```

---

# 7. 결론

CKA에서 YAML을 전부 외우려고 하면 너무 힘들다.
대신 이렇게 접근하면 된다.

```text
apiVersion으로 리소스의 집을 찾고,
kind로 정확한 리소스를 지정하고,
spec은 공식문서 예시를 보고 고친다.
```

제일 먼저 외울 묶음은 이거다.

```text
HPA → autoscaling/v2
Gateway API → gateway.networking.k8s.io/v1
Ingress/NetworkPolicy → networking.k8s.io/v1
Deployment → apps/v1
Job/CronJob → batch/v1
Pod/Service/ConfigMap/Secret/PVC → v1
```

이걸 외우면 YAML이 조금 덜 무섭다.

빈 파일을 열었을 때 최소한 이렇게 시작할 수 있기 때문이다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
```

그리고 그다음부터는 공식문서 예시를 가져와서 문제 조건에 맞게 바꾸면 된다.

CKA는 YAML 통암기 시험이 아니다.
문제를 보고 리소스를 알아차리고, 공식문서에서 빠르게 예시를 찾아 수정하는 시험에 가깝다.
