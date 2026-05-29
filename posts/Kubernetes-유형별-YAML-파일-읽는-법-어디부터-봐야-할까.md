---
title: "[Kubernetes] 유형별 YAML 파일 읽는 법 — 어디부터 봐야 할까?"
source: "https://velog.io/@yorange50/Kubernetes-유형별-YAML-파일-읽는-법-어디부터-봐야-할까"
published: "2026-05-20T04:30:04.149Z"
tags: ""
backup_date: "2026-05-29T14:52:52.719244"
---

\쿠버네티스 YAML을 처음 보면 대부분 이런 느낌이 든다.

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
        ports:
        - containerPort: 80
```

분명 글자는 읽히는데 구조가 안 보인다.

```text
이 YAML이 뭘 만드는 건지
어디가 이름인지
어디가 조건인지
어디가 실제 컨테이너인지
Service랑 Deployment는 뭐가 다른지
```

처음에는 전부 비슷해 보인다.

근데 쿠버네티스 YAML은 유형별로 읽는 순서가 있다.

오늘은 CKA 공부할 때 기준으로, 리소스별 YAML을 어떻게 읽으면 되는지 정리해본다.

---

# 1. 모든 YAML의 공통 구조

쿠버네티스 YAML은 거의 항상 이 네 덩어리로 시작한다.

```yaml
apiVersion:
kind:
metadata:
spec:
```

각각 의미는 이렇다.

```text
apiVersion: 이 리소스가 어떤 API 버전을 쓰는지
kind: 어떤 종류의 리소스인지
metadata: 이름, 네임스페이스, 라벨 같은 자기소개
spec: 원하는 상태, 즉 진짜 설정 내용
```

예시:

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

읽을 때는 위에서부터 이렇게 보면 된다.

```text
1. kind 확인
2. metadata.name 확인
3. metadata.namespace 확인
4. spec 확인
```

가장 먼저 볼 건 `kind`다.

왜냐면 `kind`를 봐야 이 YAML이 Pod인지, Service인지, Deployment인지 알 수 있기 때문이다.

---

# 2. Pod YAML 읽기

Pod는 가장 기본 단위다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx
    ports:
    - containerPort: 80
```

Pod YAML은 이렇게 읽으면 된다.

```text
kind: Pod
→ Pod를 만드는 YAML

metadata.name
→ Pod 이름

metadata.labels
→ 이 Pod에 붙은 라벨

spec.containers
→ Pod 안에서 실행할 컨테이너 목록

image
→ 어떤 이미지로 컨테이너를 띄울지

containerPort
→ 컨테이너 내부에서 열리는 포트
```

핵심은 여기다.

```yaml
spec:
  containers:
  - name: nginx
    image: nginx
```

Pod는 결국:

```text
컨테이너를 하나 또는 여러 개 담는 껍데기
```

라고 보면 된다.

그래서 Pod YAML을 읽을 때는 `spec.containers`부터 보면 된다.

---

# 3. Deployment YAML 읽기

Deployment는 Pod를 직접 하나 띄우는 게 아니라, Pod를 관리하는 리소스다.

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
        ports:
        - containerPort: 80
```

처음 보면 길다.

근데 Deployment는 세 덩어리만 보면 된다.

```text
1. replicas
2. selector
3. template
```

---

## replicas

```yaml
replicas: 3
```

의미:

```text
Pod를 3개 유지해라
```

즉 Pod 하나가 죽으면 Deployment가 다시 만들어준다.

---

## selector

```yaml
selector:
  matchLabels:
    app: nginx
```

의미:

```text
app=nginx 라벨을 가진 Pod를 내가 관리하겠다
```

Deployment에서 selector는 매우 중요하다.

---

## template

```yaml
template:
  metadata:
    labels:
      app: nginx
  spec:
    containers:
    - name: nginx
      image: nginx
```

의미:

```text
새로 만들 Pod의 설계도
```

Deployment 안에 Pod YAML이 들어있다고 보면 된다.

즉 Deployment 구조는 이렇게 읽으면 된다.

```text
Deployment
 └── spec
      ├── replicas: 몇 개 띄울지
      ├── selector: 어떤 Pod를 관리할지
      └── template: 어떤 Pod를 만들지
```

여기서 중요한 건 `selector.matchLabels`와 `template.metadata.labels`가 맞아야 한다는 것이다.

```yaml
selector:
  matchLabels:
    app: nginx

template:
  metadata:
    labels:
      app: nginx
```

둘 다 `app: nginx`다.

이게 안 맞으면 Deployment가 Pod를 제대로 관리하지 못한다.

---

# 4. Service YAML 읽기

Service는 Pod에 접근하기 위한 고정된 입구다.

Pod는 죽었다 살아나면서 IP가 바뀔 수 있다.

그래서 Service가 필요하다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: ClusterIP
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
```

Service YAML은 이렇게 읽는다.

```text
kind: Service
→ Service를 만드는 YAML

spec.type
→ 어떤 방식으로 노출할지

spec.selector
→ 어떤 Pod로 트래픽을 보낼지

spec.ports.port
→ Service가 받을 포트

spec.ports.targetPort
→ Pod 컨테이너로 보낼 포트
```

핵심은 `selector`다.

```yaml
selector:
  app: nginx
```

이 뜻은:

```text
app=nginx 라벨이 붙은 Pod로 트래픽을 보내라
```

이다.

즉 Service는 Pod 이름을 직접 보고 연결하지 않는다.

라벨을 보고 연결한다.

---

## Service port 구조

```yaml
ports:
- port: 80
  targetPort: 8080
```

이건 이렇게 읽으면 된다.

```text
Service의 80번 포트로 들어오면
Pod의 8080번 포트로 보내라
```

NodePort라면 하나가 더 붙는다.

```yaml
ports:
- port: 80
  targetPort: 8080
  nodePort: 30080
```

의미:

```text
노드의 30080번 포트로 들어오면
Service 80번을 거쳐
Pod 8080번으로 전달
```

흐름은 이렇게 보면 된다.

```text
사용자
  ↓
NodeIP:30080
  ↓
Service port: 80
  ↓
Pod targetPort: 8080
```

---

# 5. ConfigMap YAML 읽기

ConfigMap은 설정값을 담는 리소스다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_MODE: production
  LOG_LEVEL: info
```

ConfigMap은 `spec`이 아니라 `data`를 많이 본다.

읽는 순서:

```text
kind: ConfigMap
→ 설정값 저장소

metadata.name
→ ConfigMap 이름

data
→ 실제 설정값
```

이 ConfigMap은 이런 값을 담고 있다.

```text
APP_MODE=production
LOG_LEVEL=info
```

Pod에서 사용할 때는 환경변수로 넣을 수 있다.

```yaml
envFrom:
- configMapRef:
    name: app-config
```

이 뜻은:

```text
app-config ConfigMap에 있는 값을 환경변수로 주입하겠다
```

이다.

---

# 6. Secret YAML 읽기

Secret은 비밀번호, 토큰 같은 민감한 값을 담는 리소스다.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
stringData:
  DB_PASSWORD: mypassword
```

읽는 순서:

```text
kind: Secret
→ 민감한 설정값 저장소

metadata.name
→ Secret 이름

type
→ Secret 종류

stringData 또는 data
→ 실제 값
```

`stringData`는 사람이 읽기 편하게 평문으로 넣는 방식이다.

```yaml
stringData:
  DB_PASSWORD: mypassword
```

`data`는 base64 인코딩된 값을 넣는 방식이다.

```yaml
data:
  DB_PASSWORD: bXlwYXNzd29yZA==
```

처음 공부할 때는 이렇게 기억하면 된다.

```text
ConfigMap: 일반 설정값
Secret: 민감한 설정값
```

---

# 7. Ingress YAML 읽기

Ingress는 외부 HTTP 요청을 내부 Service로 라우팅하는 리소스다.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
spec:
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-service
            port:
              number: 80
```

Ingress는 이렇게 읽는다.

```text
host
→ 어떤 도메인으로 들어오는 요청인지

path
→ 어떤 경로인지

backend.service.name
→ 어느 Service로 보낼지

backend.service.port.number
→ Service의 몇 번 포트로 보낼지
```

흐름은 이렇다.

```text
app.example.com/
  ↓
Ingress
  ↓
app-service:80
  ↓
Pod
```

Ingress는 Pod로 직접 보내는 게 아니다.

반드시 Service를 거쳐서 보낸다.

그래서 Ingress YAML을 읽을 때는 backend service 이름을 꼭 확인해야 한다.

---

# 8. NetworkPolicy YAML 읽기

NetworkPolicy는 Pod 간 통신을 제한하는 리소스다.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-policy
spec:
  podSelector:
    matchLabels:
      role: db
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: backend
    ports:
    - protocol: TCP
      port: 5432
```

NetworkPolicy는 어렵게 느껴지지만 질문을 나눠서 보면 된다.

```text
1. 누구를 보호하는가?
2. 들어오는 트래픽을 막는가, 나가는 트래픽을 막는가?
3. 누구에게 허용하는가?
4. 어떤 포트를 허용하는가?
```

위 YAML은 이렇게 읽는다.

```yaml
podSelector:
  matchLabels:
    role: db
```

의미:

```text
role=db 라벨이 붙은 Pod에 정책 적용
```

```yaml
policyTypes:
- Ingress
```

의미:

```text
들어오는 트래픽을 제어
```

```yaml
from:
- podSelector:
    matchLabels:
      role: backend
```

의미:

```text
role=backend 라벨이 붙은 Pod에서 오는 트래픽만 허용
```

```yaml
ports:
- protocol: TCP
  port: 5432
```

의미:

```text
TCP 5432 포트만 허용
```

전체 의미는:

```text
role=db Pod는
role=backend Pod로부터 들어오는
TCP 5432 요청만 허용한다
```

---

# 9. PersistentVolumeClaim YAML 읽기

PVC는 저장공간을 요청하는 리소스다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

읽는 순서:

```text
kind: PersistentVolumeClaim
→ 저장공간 요청서

metadata.name
→ PVC 이름

accessModes
→ 어떤 방식으로 마운트할지

resources.requests.storage
→ 얼마나 필요한지
```

`storage: 1Gi`는:

```text
1Gi 크기의 저장공간이 필요하다
```

라는 뜻이다.

Pod에서 사용할 때는 이렇게 연결한다.

```yaml
volumes:
- name: app-storage
  persistentVolumeClaim:
    claimName: app-pvc
```

의미:

```text
app-pvc라는 저장공간 요청을 Pod에 연결
```

---

# 10. Job YAML 읽기

Job은 한 번 실행되고 끝나는 작업을 만들 때 쓴다.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: hello-job
spec:
  template:
    spec:
      containers:
      - name: hello
        image: busybox
        command: ["echo", "hello"]
      restartPolicy: Never
```

읽는 순서:

```text
kind: Job
→ 일회성 작업

spec.template
→ 실행할 Pod 설계도

containers
→ 어떤 컨테이너로 실행할지

command
→ 어떤 명령을 실행할지

restartPolicy
→ 실패하거나 종료됐을 때 재시작 정책
```

Deployment와 비슷하게 `template` 안에 Pod 설계도가 들어있다.

하지만 차이는 목적이다.

```text
Deployment: 계속 떠 있어야 하는 서비스
Job: 한 번 실행하고 끝나는 작업
```

---

# 11. CronJob YAML 읽기

CronJob은 정해진 시간마다 Job을 실행하는 리소스다.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: hello-cron
spec:
  schedule: "*/5 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: hello
            image: busybox
            command: ["echo", "hello"]
          restartPolicy: OnFailure
```

읽는 순서:

```text
kind: CronJob
→ 반복 실행 작업

schedule
→ 언제 실행할지

jobTemplate
→ 실행할 Job의 템플릿

containers
→ 실제 실행할 컨테이너
```

핵심은 `schedule`이다.

```yaml
schedule: "*/5 * * * *"
```

의미:

```text
5분마다 실행
```

CronJob 구조는 이렇게 보면 된다.

```text
CronJob
 └── schedule
 └── jobTemplate
      └── Job
           └── Pod template
                └── container
```

---

# 12. RBAC YAML 읽기

RBAC는 권한 설정이다.

보통 `Role`, `ClusterRole`, `RoleBinding`, `ClusterRoleBinding`이 나온다.

## Role

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

읽는 순서:

```text
kind: Role
→ 특정 네임스페이스 안에서의 권한

resources
→ 어떤 리소스에 대해

verbs
→ 어떤 행동을 허용할지
```

위 YAML은:

```text
default namespace에서
pods 리소스에 대해
get, watch, list 가능
```

이라는 뜻이다.

---

## RoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: jane
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

RoleBinding은 이렇게 읽는다.

```text
subjects
→ 누구에게 권한을 줄지

roleRef
→ 어떤 Role을 연결할지
```

즉 위 YAML은:

```text
jane 사용자에게
pod-reader Role을 연결한다
```

는 뜻이다.

RBAC는 이렇게 기억하면 된다.

```text
Role: 권한 내용
RoleBinding: 권한을 누구에게 붙일지
```

---

# 13. 유형별로 가장 먼저 볼 부분

정리하면 이렇게 보면 된다.

| 리소스           | 가장 먼저 볼 부분                                  | 의미                      |
| ------------- | ------------------------------------------- | ----------------------- |
| Pod           | `spec.containers`                           | 어떤 컨테이너를 띄우는가           |
| Deployment    | `replicas`, `selector`, `template`          | Pod를 몇 개, 어떤 기준으로 관리하는가 |
| Service       | `type`, `selector`, `ports`                 | 어떤 Pod로 트래픽을 보내는가       |
| ConfigMap     | `data`                                      | 어떤 설정값을 담는가             |
| Secret        | `stringData` 또는 `data`                      | 어떤 민감값을 담는가             |
| Ingress       | `rules`, `backend.service`                  | 어떤 요청을 어느 Service로 보내는가 |
| NetworkPolicy | `podSelector`, `ingress/egress`             | 누구의 통신을 제한하는가           |
| PVC           | `accessModes`, `resources.requests.storage` | 어떤 저장공간을 요청하는가          |
| Job           | `template.spec.containers`, `command`       | 어떤 작업을 한 번 실행하는가        |
| CronJob       | `schedule`, `jobTemplate`                   | 언제 어떤 Job을 반복 실행하는가     |
| Role          | `resources`, `verbs`                        | 어떤 리소스에 어떤 행동을 허용하는가    |
| RoleBinding   | `subjects`, `roleRef`                       | 누구에게 어떤 Role을 붙이는가      |

---

# 14. YAML 읽는 공통 루틴

어떤 YAML이든 처음 보면 이렇게 읽으면 된다.

```text
1. kind를 본다
2. metadata.name을 본다
3. metadata.namespace를 본다
4. spec에서 핵심 필드를 찾는다
5. selector와 labels가 연결되는지 본다
6. ports가 어디에서 어디로 이어지는지 본다
7. apply 후 get / describe로 실제 상태를 확인한다
```

특히 쿠버네티스에서 자주 나오는 연결은 이거다.

```text
Deployment template label
↔ Service selector
```

예시:

```yaml
template:
  metadata:
    labels:
      app: nginx
```

```yaml
selector:
  app: nginx
```

이 둘이 맞아야 Service가 Deployment가 만든 Pod를 찾을 수 있다.

---

# 마무리

쿠버네티스 YAML은 처음 보면 너무 길고 복잡해 보인다.

하지만 리소스마다 보는 위치가 정해져 있다.

```text
Pod는 containers
Deployment는 replicas, selector, template
Service는 type, selector, ports
ConfigMap과 Secret은 data
Ingress는 rules와 backend
NetworkPolicy는 podSelector와 ingress/egress
PVC는 storage 요청
RBAC는 resources, verbs, subjects, roleRef
```

이렇게 유형별로 읽으면 YAML이 훨씬 덜 무섭다.

결국 중요한 건 YAML을 통째로 외우는 게 아니라:

```text
이 리소스는 어디를 봐야 하는지
어떤 필드끼리 연결되는지
문제 조건을 어느 위치에 넣어야 하는지
```

를 아는 것이다.
