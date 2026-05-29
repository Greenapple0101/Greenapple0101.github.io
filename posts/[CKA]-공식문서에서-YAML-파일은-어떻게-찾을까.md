---
title: "[CKA] 공식문서에서 YAML 파일은 어떻게 찾을까?"
source: "https://velog.io/@yorange50/CKA-공식문서에서-YAML-파일은-어떻게-찾을까"
published: "2026-05-20T04:05:07.181Z"
tags: ""
backup_date: "2026-05-29T14:52:52.719700"
---

CKA를 준비하다 보면 이런 생각이 든다.

```text
“이 YAML을 내가 다 외워야 하나?”
“Deployment YAML은 어디서 찾지?”
“Service 예시는 공식문서 어디에 있지?”
“Gateway API YAML은 어떻게 찾지?”
```

결론부터 말하면, YAML을 전부 외우는 시험이 아니다.

더 중요한 건:

```text
공식문서에서 예제 YAML을 빠르게 찾고
내 문제 조건에 맞게 고치는 능력
```

이다.

---

# 1. YAML을 찾는 기본 감각

쿠버네티스 공식문서에서 YAML을 찾을 때는 보통 두 가지 방식이 있다.

```text
1. 리소스 이름으로 검색
2. 기능 이름으로 검색
```

예를 들어 Deployment YAML이 필요하면:

```text
Deployment
```

Service YAML이 필요하면:

```text
Service
```

ConfigMap YAML이 필요하면:

```text
ConfigMap
```

Ingress YAML이 필요하면:

```text
Ingress
```

이렇게 검색한다.

근데 CKA에서는 단순히 “개념 설명”보다 “예제 YAML”이 있는 페이지를 빨리 찾는 게 중요하다.

---

# 2. 공식문서 검색창에 칠 키워드

공식문서 검색창에서 이런 식으로 검색하면 된다.

```text
deployment
```

```text
service
```

```text
configmap
```

```text
secret
```

```text
persistent volume
```

```text
pod
```

```text
ingress
```

```text
gateway api
```

```text
network policy
```

여기서 중요한 건 너무 길게 검색하지 않는 것이다.

예를 들어:

```text
how to create deployment yaml file
```

이렇게 길게 치는 것보다

```text
deployment
```

이렇게 치는 게 더 잘 잡힌다.

---

# 3. 페이지 안에서는 `Ctrl + F`를 쓴다

공식문서 페이지에 들어갔으면 이제 브라우저 검색을 쓴다.

Windows/Linux:

```text
Ctrl + F
```

Mac:

```text
Command + F
```

그리고 이런 단어를 찾는다.

```text
apiVersion
```

```text
kind:
```

```text
yaml
```

```text
example
```

```text
manifest
```

왜냐면 YAML 예시는 보통 이런 형태로 시작하기 때문이다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
```

즉 페이지 안에서 `apiVersion`을 검색하면 예제 YAML 위치로 바로 이동할 수 있다.

---

# 4. 제일 강한 검색어는 `apiVersion`

쿠버네티스 YAML은 거의 항상 이렇게 시작한다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
```

그래서 공식문서 페이지 안에서:

```text
apiVersion
```

을 검색하면 YAML 예제를 빠르게 찾을 수 있다.

이건 진짜 유용하다.

문서가 아무리 길어도 `apiVersion`을 치면 예제 매니페스트 근처로 바로 간다.

---

# 5. 리소스별로 자주 찾는 위치

## Pod

검색어:

```text
pod
```

페이지 안 검색:

```text
apiVersion
```

예시 형태:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - name: nginx
    image: nginx
```

---

## Deployment

검색어:

```text
deployment
```

페이지 안 검색:

```text
apiVersion
```

예시 형태:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
```

Deployment는 특히 구조가 길다.

그래서 처음부터 다 외우기보다 공식문서 예제를 복사해서 고치는 방식이 훨씬 현실적이다.

---

## Service

검색어:

```text
service
```

페이지 안 검색:

```text
type:
```

또는:

```text
NodePort
```

예시 형태:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: NodePort
  selector:
    app: MyApp
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30007
```

Service는 문제 조건에 따라 `type`이 중요하다.

```text
ClusterIP
NodePort
LoadBalancer
```

이 부분만 잘 바꿔주면 된다.

---

## ConfigMap

검색어:

```text
configmap
```

페이지 안 검색:

```text
data:
```

예시 형태:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: game-demo
data:
  player_initial_lives: "3"
  ui_properties_file_name: "user-interface.properties"
```

ConfigMap은 보통 `data:` 아래에 값을 넣는다.

---

## Secret

검색어:

```text
secret
```

페이지 안 검색:

```text
stringData
```

또는:

```text
data:
```

예시 형태:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
type: Opaque
stringData:
  username: admin
  password: password
```

Secret은 `data`와 `stringData` 차이를 알아두면 좋다.

시험에서는 사람이 읽기 편한 `stringData`를 쓰는 경우도 많다.

---

## Ingress

검색어:

```text
ingress
```

페이지 안 검색:

```text
rules:
```

또는:

```text
path:
```

예시 형태:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: minimal-ingress
spec:
  rules:
  - http:
      paths:
      - path: /testpath
        pathType: Prefix
        backend:
          service:
            name: test
            port:
              number: 80
```

Ingress는 구조가 길어서 공식문서 복붙 후 수정하는 게 거의 정석이다.

---

## NetworkPolicy

검색어:

```text
network policy
```

페이지 안 검색:

```text
podSelector
```

또는:

```text
ingress:
```

예시 형태:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: test-network-policy
spec:
  podSelector:
    matchLabels:
      role: db
  policyTypes:
  - Ingress
```

NetworkPolicy는 YAML 모양보다 조건 해석이 더 어렵다.

그래서 예제를 가져온 다음:

```text
podSelector
ingress
egress
from
to
ports
```

만 문제 조건에 맞게 바꾸는 식으로 접근하면 된다.

---

# 6. 공식문서에서 YAML 찾는 실전 루틴

CKA 시험장에서 이렇게 움직이면 된다.

```text
1. 문제에서 리소스 이름 확인
2. 공식문서 검색창에 리소스 이름 검색
3. 예제 페이지 진입
4. Ctrl + F로 apiVersion 검색
5. YAML 예제 복사
6. 문제 조건에 맞게 name, namespace, image, port 수정
7. kubectl apply -f
8. kubectl get / describe / curl 등으로 검증
```

흐름으로 보면:

```text
문제 조건
  ↓
공식문서 검색
  ↓
YAML 예제 복사
  ↓
내 조건으로 수정
  ↓
적용
  ↓
검증
```

---

# 7. 검색어를 너무 문장처럼 치지 말기

공식문서 검색창에서는 긴 문장보다 짧은 키워드가 좋다.

별로인 검색:

```text
how to create yaml file for nginx deployment in kubernetes
```

좋은 검색:

```text
deployment
```

```text
nginx deployment
```

```text
service nodeport
```

```text
configmap
```

```text
network policy
```

공식문서는 블로그 검색이 아니라 레퍼런스 문서 검색이기 때문에, 핵심 명사 위주로 치는 게 빠르다.

---

# 8. `kubectl explain`도 같이 쓰면 좋다

공식문서에서 예제 YAML을 찾은 뒤, 필드 의미가 헷갈리면 터미널에서 이렇게 볼 수 있다.

```bash
kubectl explain deployment.spec
```

더 깊게 보고 싶으면:

```bash
kubectl explain deployment.spec.template.spec.containers
```

Service라면:

```bash
kubectl explain service.spec
```

NetworkPolicy라면:

```bash
kubectl explain networkpolicy.spec
```

즉:

```text
공식문서 = 예제 YAML 찾기
kubectl explain = 필드 구조 확인하기
```

이렇게 역할을 나누면 좋다.

---

# 9. 자동생성과 공식문서 복붙을 같이 쓴다

YAML을 만드는 방법은 크게 두 가지다.

```text
1. kubectl --dry-run=client -o yaml 로 자동생성
2. 공식문서에서 예제 YAML 복사
```

둘 중 하나만 쓰는 게 아니다.

보통은 이렇게 나뉜다.

## 자동생성이 편한 것

```text
Pod
Deployment
Service
ConfigMap
Secret
Job
CronJob
```

예시:

```bash
kubectl create deployment web \
  --image=nginx \
  --dry-run=client \
  -o yaml > deploy.yaml
```

---

## 공식문서 복붙이 편한 것

```text
Ingress
Gateway API
NetworkPolicy
PersistentVolume
PersistentVolumeClaim
RBAC
```

이런 것들은 구조가 길거나 조건이 복잡해서, 공식문서 예제를 가져와 수정하는 게 편하다.

---

# 10. 외우는 게 아니라 찾는 속도를 훈련해야 한다

CKA에서 중요한 건 YAML 전체 암기가 아니다.

진짜 중요한 건 이거다.

```text
“이 YAML은 공식문서 어디쯤에 있겠다”
```

라는 감각이다.

예를 들어:

```text
트래픽 라우팅 문제 → Ingress / Gateway API
접근 제한 문제 → NetworkPolicy
권한 문제 → RBAC
저장소 문제 → PV / PVC
설정 주입 문제 → ConfigMap / Secret
배포 문제 → Deployment
노출 문제 → Service
```

이 연결이 머리에 있으면 공식문서에서 빠르게 찾을 수 있다.

---

# 마무리

YAML을 전부 외우려고 하면 쿠버네티스가 너무 버거워진다.

대신 이렇게 생각하면 된다.

```text
자주 쓰는 건 자동생성
복잡한 건 공식문서 예제 복붙
헷갈리는 필드는 kubectl explain
```

그리고 공식문서에서 YAML을 찾을 때는:

```text
리소스 이름 검색
→ 페이지 안에서 apiVersion 검색
→ 예제 YAML 복사
→ 조건에 맞게 수정
```

이 흐름만 익히면 된다.

CKA는 YAML 암기 시험이 아니라, 필요한 리소스를 빠르게 찾고 정확히 적용하는 시험에 가깝다.
