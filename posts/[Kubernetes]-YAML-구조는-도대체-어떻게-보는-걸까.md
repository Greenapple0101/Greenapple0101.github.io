---
title: "[Kubernetes] YAML 구조는 도대체 어떻게 보는 걸까?"
source: "https://velog.io/@yorange50/Kubernetes-YAML-구조는-도대체-어떻게-보는-걸까"
published: "2026-05-22T07:56:04.445Z"
tags: ""
backup_date: "2026-05-29T14:52:52.714373"
---

Kubernetes 공부를 하다 보면 결국 YAML을 계속 보게 된다.

```yaml id="71devn"
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
    - name: nginx
      image: nginx
```

처음 보면 그냥 이상한 설정 파일처럼 보인다.
근데 계속 보다 보면 Kubernetes YAML은 거의 같은 구조를 반복한다.

```text id="2zy3ok"
apiVersion
kind
metadata
spec
```

이 4개만 먼저 잡으면 된다.

---

# 1. Kubernetes YAML의 기본 구조

Kubernetes YAML은 보통 이렇게 생겼다.

```yaml id="mqk8y3"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: dev
  labels:
    app: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx
          image: nginx
          ports:
            - containerPort: 80
```

길어 보이지만 사실 크게 보면 이거다.

```text id="cxwoeg"
apiVersion: 어느 API 그룹의 리소스인지
kind: 어떤 리소스인지
metadata: 리소스의 이름표
spec: 원하는 상태
```

---

# 2. apiVersion

```yaml id="j7wwcy"
apiVersion: apps/v1
```

`apiVersion`은 이 리소스가 Kubernetes API의 어느 그룹에 속하는지 나타낸다.

예를 들어 Deployment는 앱을 배포하고 관리하는 리소스다.

```yaml id="q03i27"
apiVersion: apps/v1
kind: Deployment
```

Pod, Service, ConfigMap 같은 기본 리소스는 보통 `v1`이다.

```yaml id="6e7v64"
apiVersion: v1
kind: Pod
```

HPA는 autoscaling 계열이다.

```yaml id="c61m8p"
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
```

NetworkPolicy와 Ingress는 networking 계열이다.

```yaml id="hzqbkq"
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
```

Gateway API는 gateway networking 계열이다.

```yaml id="0zhcz7"
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
```

처음에는 다 외우기 힘드니까 자주 나오는 것만 먼저 잡으면 된다.

```text id="bxfy9p"
Pod / Service / ConfigMap / Secret / PVC → v1
Deployment / DaemonSet / StatefulSet → apps/v1
Job / CronJob → batch/v1
HPA → autoscaling/v2
Ingress / NetworkPolicy → networking.k8s.io/v1
Gateway / HTTPRoute → gateway.networking.k8s.io/v1
```

---

# 3. kind

```yaml id="i91b7b"
kind: Deployment
```

`kind`는 이 YAML이 어떤 리소스를 만들지 정한다.

예를 들어:

```yaml id="0j0hw1"
kind: Pod
```

이면 Pod를 만든다.

```yaml id="kwb2i2"
kind: Service
```

이면 Service를 만든다.

```yaml id="ry7so2"
kind: ConfigMap
```

이면 ConfigMap을 만든다.

즉, `apiVersion`이 리소스의 소속이라면, `kind`는 리소스의 정체다.

```text id="dppext"
apiVersion: 어느 API 그룹?
kind: 어떤 리소스?
```

예를 들어:

```yaml id="l5guyf"
apiVersion: apps/v1
kind: Deployment
```

이건 이런 뜻이다.

```text id="e7dg4z"
apps/v1 그룹에 있는 Deployment 리소스를 만들겠다
```

---

# 4. metadata

```yaml id="wzajpp"
metadata:
  name: web
  namespace: dev
  labels:
    app: web
```

`metadata`는 리소스 자체에 대한 정보다.

대표적으로:

```text id="e970wy"
name
namespace
labels
annotations
```

이 들어간다.

## name

```yaml id="5wzch6"
metadata:
  name: web
```

리소스 이름이다.

문제에서:

```text id="uyef0p"
Create a Deployment named web
```

이라고 하면 여기 들어간다.

## namespace

```yaml id="ae1f77"
metadata:
  namespace: dev
```

리소스가 생성될 네임스페이스다.

문제에서:

```text id="a3ga2u"
in the dev namespace
```

라고 하면 여기 들어간다.

명령어로는:

```bash id="2xl5l4"
-n dev
```

YAML로는:

```yaml id="qmvx3k"
namespace: dev
```

## labels

```yaml id="bvj12h"
labels:
  app: web
```

label은 리소스에 붙이는 이름표다.

Service가 Pod를 찾을 때도 label을 기준으로 찾는다.

예를 들어 Pod에 이런 label이 있다고 해보자.

```yaml id="1y2ue4"
labels:
  app: web
```

Service는 이렇게 찾는다.

```yaml id="d48g5q"
selector:
  app: web
```

뜻은 이거다.

```text id="b2rse3"
app=web이라는 label이 붙은 Pod를 찾아라
```

---

# 5. spec

```yaml id="u4md32"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    ...
```

`spec`은 이 리소스가 어떤 상태가 되길 원하는지 적는 부분이다.

Kubernetes YAML에서 제일 중요한 부분이 보통 `spec`이다.

```text id="vex3qj"
metadata = 이 리소스가 누구인지
spec = 이 리소스가 어떻게 동작해야 하는지
```

Deployment의 spec에는 이런 것들이 들어간다.

```text id="hlrbiy"
replicas
selector
template
containers
image
ports
```

Service의 spec에는 이런 것들이 들어간다.

```text id="zlgg1r"
type
selector
ports
```

HPA의 spec에는 이런 것들이 들어간다.

```text id="rxbwdc"
scaleTargetRef
minReplicas
maxReplicas
metrics
behavior
```

NetworkPolicy의 spec에는 이런 것들이 들어간다.

```text id="qi4dxp"
podSelector
policyTypes
ingress
egress
```

즉, 리소스마다 `spec` 구조가 다르다.
그래서 CKA에서는 `apiVersion`, `kind`, `metadata`보다 **spec을 잘 보는 것**이 중요하다.

---

# 6. Deployment YAML 구조 보기

Deployment는 CKA에서 정말 많이 나온다.

```yaml id="hx8tg3"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: dev
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx
          image: nginx
          ports:
            - containerPort: 80
```

이 구조는 이렇게 읽으면 된다.

```text id="64ktzy"
Deployment 이름은 web
dev namespace에 생성
Pod를 3개 유지
app=web label을 가진 Pod를 관리
template 기준으로 Pod 생성
컨테이너 이미지는 nginx
컨테이너 포트는 80
```

여기서 제일 중요한 부분은 이거다.

```yaml id="agv6id"
selector:
  matchLabels:
    app: web
template:
  metadata:
    labels:
      app: web
```

둘이 맞아야 한다.

```text id="e4eo49"
selector.matchLabels
=
template.metadata.labels
```

Deployment는 `template`을 보고 Pod를 만든다.
그리고 `selector`를 보고 어떤 Pod를 자기 것으로 관리할지 결정한다.

그래서 label이 안 맞으면 문제가 생긴다.

---

# 7. Pod YAML 구조 보기

Pod는 기본 구조가 단순하다.

```yaml id="zjwv95"
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  namespace: dev
  labels:
    app: nginx
spec:
  containers:
    - name: nginx
      image: nginx
      ports:
        - containerPort: 80
```

이렇게 읽으면 된다.

```text id="k8p0ev"
nginx-pod라는 Pod를 dev namespace에 만든다
app=nginx label을 붙인다
nginx 컨테이너를 하나 실행한다
image는 nginx를 사용한다
containerPort는 80이다
```

Pod에서 자주 들어가는 것들:

```text id="ba0yc1"
containers
image
command
args
env
envFrom
volumeMounts
volumes
resources
livenessProbe
readinessProbe
tolerations
nodeSelector
affinity
```

중요한 건 대부분 `containers` 아래에 들어간다는 점이다.

예를 들어 환경변수:

```yaml id="v4h0wo"
containers:
  - name: app
    image: busybox
    env:
      - name: APP_MODE
        value: production
```

리소스 제한:

```yaml id="934z0y"
containers:
  - name: app
    image: nginx
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 500m
        memory: 256Mi
```

Probe:

```yaml id="fwlcg4"
containers:
  - name: nginx
    image: nginx
    livenessProbe:
      httpGet:
        path: /
        port: 80
```

---

# 8. Service YAML 구조 보기

Service는 Pod에 접근하기 위한 고정된 입구다.

```yaml id="xo452r"
apiVersion: v1
kind: Service
metadata:
  name: web-svc
  namespace: dev
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080
```

이렇게 읽으면 된다.

```text id="k92rjj"
web-svc라는 Service를 dev namespace에 만든다
NodePort 타입이다
app=web label을 가진 Pod를 바라본다
Service의 port는 80
Pod의 targetPort는 8080
외부에서 들어올 nodePort는 30080
```

여기서 제일 중요한 건 `selector`다.

```yaml id="nh09ow"
selector:
  app: web
```

Service는 이 selector로 Pod를 찾는다.

Pod label이 이거면 연결된다.

```yaml id="lb98gd"
labels:
  app: web
```

Pod label이 이거면 연결 안 된다.

```yaml id="whob57"
labels:
  app: api
```

확인 명령어:

```bash id="y65xg5"
kubectl get endpoints web-svc -n dev
```

endpoints가 비어 있으면 selector-label 불일치를 의심하면 된다.

---

# 9. ConfigMap YAML 구조 보기

ConfigMap은 일반 설정값을 저장한다.

```yaml id="3potb4"
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: dev
data:
  APP_MODE: production
  LOG_LEVEL: debug
```

이렇게 읽으면 된다.

```text id="u7qg9v"
app-config라는 ConfigMap을 dev namespace에 만든다
APP_MODE=production
LOG_LEVEL=debug
설정값을 저장한다
```

Pod에서 전체를 환경변수로 가져오려면:

```yaml id="m1lxak"
envFrom:
  - configMapRef:
      name: app-config
```

특정 key만 가져오려면:

```yaml id="it7fdf"
env:
  - name: APP_MODE
    valueFrom:
      configMapKeyRef:
        name: app-config
        key: APP_MODE
```

---

# 10. Secret YAML 구조 보기

Secret은 민감한 값을 저장한다.

```yaml id="0szdcf"
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
  namespace: dev
type: Opaque
stringData:
  DB_USER: admin
  DB_PASSWORD: pass123
```

처음 공부할 때는 `data`보다 `stringData`가 편하다.

```text id="jmj5nv"
data = base64 인코딩된 값
stringData = 평문으로 적으면 Kubernetes가 알아서 처리
```

Pod에서 전체를 환경변수로 가져오려면:

```yaml id="05czga"
envFrom:
  - secretRef:
      name: db-secret
```

특정 key만 가져오려면:

```yaml id="57mfbg"
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-secret
        key: DB_PASSWORD
```

---

# 11. PVC + Pod volume 구조 보기

PVC는 저장소 요청서다.

```yaml id="ksill4"
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-pvc
  namespace: dev
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

이렇게 읽으면 된다.

```text id="ber5zd"
data-pvc라는 PVC를 만든다
ReadWriteOnce 방식으로 사용한다
1Gi 저장소를 요청한다
```

Pod에서 PVC를 쓰려면 두 군데가 필요하다.

```yaml id="79wboo"
volumeMounts:
  - name: data
    mountPath: /data
```

```yaml id="db9bom"
volumes:
  - name: data
    persistentVolumeClaim:
      claimName: data-pvc
```

전체 예시:

```yaml id="218zcz"
apiVersion: v1
kind: Pod
metadata:
  name: pvc-pod
  namespace: dev
spec:
  containers:
    - name: nginx
      image: nginx
      volumeMounts:
        - name: data
          mountPath: /usr/share/nginx/html
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: data-pvc
```

여기서 중요한 건 이름이 같아야 한다는 것.

```text id="fuo0xo"
volumeMounts.name
=
volumes.name
```

---

# 12. HPA YAML 구조 보기

HPA는 Pod 개수를 자동으로 조절한다.

```yaml id="549zip"
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: apache-server
  namespace: autoscale
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: apache-server
  minReplicas: 1
  maxReplicas: 4
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 50
```

이렇게 읽으면 된다.

```text id="6cgh2z"
apache-server라는 HPA를 만든다
autoscale namespace에 만든다
apps/v1 Deployment apache-server를 대상으로 한다
Pod 개수는 최소 1개, 최대 4개
CPU 사용률 50%를 기준으로 조절한다
```

scale down 안정화 시간이 있으면:

```yaml id="5tdzro"
behavior:
  scaleDown:
    stabilizationWindowSeconds: 30
```

이 부분은 `spec` 아래에 들어간다.

---

# 13. NetworkPolicy YAML 구조 보기

NetworkPolicy는 Pod 간 통신을 제한한다.

```yaml id="b1gpva"
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-frontend
  namespace: dev
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080
```

이렇게 읽으면 된다.

```text id="z23i9h"
dev namespace에 NetworkPolicy를 만든다
app=backend Pod에 적용한다
Ingress 트래픽을 제한한다
app=frontend Pod에서 오는 요청만 허용한다
8080 포트만 허용한다
```

여기서 헷갈리는 포인트는 이거다.

```text id="twmpri"
podSelector = 정책을 적용받는 대상 Pod
ingress.from.podSelector = 접근을 허용할 출발 Pod
```

즉:

```yaml id="2l2aq1"
podSelector:
  matchLabels:
    app: backend
```

이건 backend Pod를 보호하겠다는 뜻.

```yaml id="2fjt3v"
from:
  - podSelector:
      matchLabels:
        app: frontend
```

이건 frontend Pod만 들어오게 하겠다는 뜻.

---

# 14. 들여쓰기 보는 법

YAML은 들여쓰기가 진짜 중요하다.

예를 들어 이건 맞다.

```yaml id="vpyds2"
containers:
  - name: nginx
    image: nginx
    ports:
      - containerPort: 80
```

이 구조는:

```text id="pbxhd6"
containers 아래에 리스트가 있고
그 리스트 안에 name, image, ports가 있다
```

근데 들여쓰기를 잘못하면 완전히 다른 뜻이 된다.

CKA에서 조심해야 하는 부분:

```text id="ls3alb"
containers
env
envFrom
volumeMounts
volumes
resources
livenessProbe
readinessProbe
metrics
behavior
ingress
from
ports
```

특히 리스트는 `-` 위치가 중요하다.

```yaml id="8xfr47"
ports:
  - port: 80
    targetPort: 8080
```

여기서 `port`와 `targetPort`는 같은 리스트 아이템 안에 있다.

---

# 15. YAML 볼 때 순서

시험장에서 YAML을 열면 이렇게 보면 된다.

```text id="ul0tto"
1. apiVersion 맞나
2. kind 맞나
3. metadata.name 맞나
4. metadata.namespace 맞나
5. labels 맞나
6. selector가 labels를 제대로 바라보나
7. spec 조건이 문제와 맞나
8. image 맞나
9. port / targetPort / nodePort 맞나
10. env / volume / probe / resource 위치 맞나
```

문제가 안 풀릴 때는 이 순서로 확인한다.

```bash id="mbatx4"
kubectl get
kubectl describe
kubectl logs
kubectl get events
kubectl get endpoints
```

---

# 16. 결론

Kubernetes YAML은 처음에는 복잡해 보이지만 큰 구조는 반복된다.

```text id="xm7jis"
apiVersion
kind
metadata
spec
```

이 4개를 먼저 잡으면 된다.

```text id="wji1ry"
apiVersion = 어느 API 그룹인지
kind = 어떤 리소스인지
metadata = 이름, namespace, label 같은 정보
spec = 원하는 동작 상태
```

그리고 CKA에서는 특히 이 감각이 중요하다.

```text id="04fy6a"
리소스 종류를 파악한다
YAML 구조를 찾는다
문제 조건에 맞게 spec을 수정한다
selector와 label을 확인한다
apply 후 get / describe로 검증한다
```

결국 CKA에서 YAML을 잘 본다는 건 이거다.

```text id="xrpw14"
YAML을 처음부터 다 외우는 게 아니라,
어디를 봐야 하는지 알고,
공식문서 예시를 가져와서,
문제 조건에 맞게 고치는 것
```

그래서 YAML이 무섭다면 일단 이것부터 보면 된다.

```text id="2igj0t"
apiVersion
kind
metadata
spec
```

여기서 시작하면 된다.
