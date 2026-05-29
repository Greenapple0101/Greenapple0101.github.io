---
title: "[CKA] 시험 전에 꼭 알아야 하는 Kubernetes 개념사전"
source: "https://velog.io/@yorange50/CKA-시험-전에-꼭-알아야-하는-Kubernetes-개념사전"
published: "2026-05-19T07:48:16.800Z"
tags: ""
backup_date: "2026-05-29T14:52:52.721931"
---

CKA를 준비하다 보면 단어가 너무 많이 나온다. 처음에는 Pod, Deployment, Service 정도만 알아도 될 것 같은데, 조금만 들어가면 ConfigMap, Secret, Ingress, Gateway API, PVC, RBAC, kubelet, etcd, taint, CoreDNS 같은 단어들이 한꺼번에 쏟아진다. 이 글은 CKA를 준비할 때 반드시 익숙해져야 하는 핵심 개념들을 “무슨 뜻인지”, “어디에 쓰이는지”, “시험에서는 어떻게 만나는지” 기준으로 정리한 개념사전이다.

---

# 1. Pod

Pod는 Kubernetes에서 애플리케이션이 실행되는 가장 작은 단위다.

컨테이너를 직접 Kubernetes에 띄우는 것이 아니라, Kubernetes는 컨테이너를 Pod라는 단위로 감싸서 실행한다.

```text
Pod
 └── Container
```

보통 하나의 Pod 안에는 하나의 컨테이너가 들어간다. 하지만 필요하면 여러 컨테이너가 하나의 Pod 안에 같이 들어갈 수도 있다.

예를 들어 Nginx를 실행하면 실제로는 Nginx 컨테이너가 들어 있는 Pod가 만들어진다.

```bash
kubectl run nginx --image=nginx
```

Pod는 직접 만들 수도 있지만, 운영에서는 보통 Deployment가 Pod를 관리하게 만든다.

CKA에서 Pod는 가장 기본 단위다. Pod가 Pending인지, Running인지, CrashLoopBackOff인지, ImagePullBackOff인지 확인하고 원인을 찾는 문제가 자주 나온다.

```bash
kubectl get pod
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

---

# 2. Deployment

Deployment는 Pod를 안정적으로 관리하는 리소스다.

Pod를 직접 만들면 Pod가 죽었을 때 직접 다시 만들어야 한다. 하지만 Deployment를 사용하면 원하는 개수의 Pod를 계속 유지해준다.

```text
Deployment
 └── ReplicaSet
      └── Pod
      └── Pod
      └── Pod
```

예를 들어 replicas를 3으로 설정하면 Deployment는 Pod 3개가 항상 떠 있도록 관리한다.

```bash
kubectl create deployment web --image=nginx --replicas=3
```

Deployment가 하는 일은 크게 다음과 같다.

```text
Pod 개수 유지
Pod 재생성
Rolling Update
Rollback
Scale 조정
```

이미지를 변경할 때도 Deployment를 사용한다.

```bash
kubectl set image deployment/web nginx=nginx:1.25
kubectl rollout status deployment/web
kubectl rollout undo deployment/web
```

CKA에서는 Deployment 생성, 이미지 변경, replica 수 변경, rollout 확인 문제가 자주 나온다.

---

# 3. Service

Service는 Pod에 접근하기 위한 고정된 네트워크 입구다.

Pod는 언제든지 죽고 다시 만들어질 수 있다. 이때 Pod IP도 바뀐다. 그래서 클라이언트가 Pod IP에 직접 접근하면 불안정하다.

Service는 이 문제를 해결한다.

```text
Client
  ↓
Service
  ↓
Pod
```

Service는 Pod를 직접 기억하는 것이 아니라 Label과 Selector로 Pod를 찾는다.

```text
Service selector: app=web
Pod label: app=web
```

둘이 맞으면 Service가 Pod로 트래픽을 보낸다.

확인 명령어는 다음과 같다.

```bash
kubectl get svc
kubectl describe svc <service-name>
kubectl get endpoints
kubectl get pod --show-labels
```

CKA에서 Service 문제가 나오면 selector와 label이 맞는지, port와 targetPort가 맞는지, endpoint가 생겼는지를 확인해야 한다.

---

# 4. ConfigMap

ConfigMap은 애플리케이션 설정값을 저장하는 리소스다.

예를 들어 환경 이름, 로그 레벨, 외부 API 주소, 설정 파일 같은 값을 컨테이너 이미지 안에 넣지 않고 Kubernetes 리소스로 분리할 수 있다.

```text
ConfigMap = 일반 설정값 저장
```

예시:

```bash
kubectl create configmap app-config \
  --from-literal=APP_MODE=prod \
  --from-literal=LOG_LEVEL=info
```

Pod에서는 ConfigMap을 환경변수로 주입하거나 파일처럼 마운트할 수 있다.

```yaml
envFrom:
  - configMapRef:
      name: app-config
```

CKA에서는 ConfigMap을 만들고 Pod에 연결하는 문제가 나올 수 있다.

---

# 5. Secret

Secret은 민감한 값을 저장하는 리소스다.

예를 들어 비밀번호, 토큰, 인증키, TLS 인증서 같은 값을 저장한다.

```text
Secret = 민감한 설정값 저장
```

ConfigMap과 비슷하지만, Secret은 민감 정보를 다룬다는 차이가 있다.

```bash
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password=1234
```

Pod에서는 Secret을 환경변수나 파일로 사용할 수 있다.

```yaml
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-secret
        key: password
```

CKA에서는 Secret 생성, Pod 연결, TLS Secret 사용 문제가 나올 수 있다.

---

# 6. Namespace

Namespace는 Kubernetes 리소스를 논리적으로 나누는 공간이다.

하나의 클러스터 안에서 dev, prod, test처럼 환경을 나누거나 팀별로 리소스를 분리할 때 사용한다.

```text
Cluster
 ├── namespace: dev
 ├── namespace: prod
 └── namespace: test
```

명령어에서 namespace를 지정할 때는 `-n`을 사용한다.

```bash
kubectl get pod -n dev
kubectl get svc -n prod
```

전체 namespace를 볼 때는 `-A`를 사용한다.

```bash
kubectl get pod -A
```

CKA에서는 문제에 namespace가 지정되어 있는 경우가 많다. `-n`을 빼먹으면 엉뚱한 namespace에서 작업하게 된다.

---

# 7. Label

Label은 Kubernetes 리소스에 붙이는 식별용 태그다.

예를 들어 Pod에 `app=web`이라는 label을 붙이면, Service나 Deployment가 이 label을 기준으로 Pod를 찾을 수 있다.

```yaml
metadata:
  labels:
    app: web
    tier: frontend
```

명령어로 label을 붙일 수도 있다.

```bash
kubectl label pod nginx app=web
```

label 확인:

```bash
kubectl get pod --show-labels
```

CKA에서 label은 Service, selector, scheduling, NetworkPolicy 등 여러 곳에서 계속 나온다.

---

# 8. Selector

Selector는 Label을 기준으로 리소스를 선택하는 조건이다.

Service가 Pod를 찾을 때 selector를 사용한다.

```yaml
selector:
  app: web
```

이 selector는 `app=web` label이 붙은 Pod를 찾는다.

```text
Service selector: app=web
        ↓
Pod label: app=web
```

Deployment에서도 selector가 중요하다.

```yaml
selector:
  matchLabels:
    app: web
```

CKA에서 Service가 연결되지 않으면 가장 먼저 봐야 할 것이 selector와 label이다.

```bash
kubectl get svc
kubectl describe svc <svc-name>
kubectl get pod --show-labels
kubectl get endpoints
```

---

# 9. Annotation

Annotation은 Kubernetes 리소스에 부가 정보를 붙이는 메타데이터다.

Label은 선택과 분류에 사용되지만, Annotation은 설명이나 설정 정보 저장에 많이 사용된다.

```yaml
metadata:
  annotations:
    description: "this is nginx pod"
```

명령어로도 추가할 수 있다.

```bash
kubectl annotate pod nginx description="test pod"
```

Annotation은 Ingress Controller, Gateway, monitoring, CI/CD 도구들이 추가 설정을 읽을 때도 사용된다.

CKA에서는 label과 annotation을 구분하는 것이 중요하다.

```text
Label = 선택하기 위한 태그
Annotation = 부가 정보를 담는 메모
```

---

# 10. ClusterIP

ClusterIP는 Service의 기본 타입이다.

클러스터 내부에서만 접근 가능한 IP를 제공한다.

```text
Pod → ClusterIP Service → Pod
```

예를 들어 백엔드 Pod가 DB Service에 접근할 때 ClusterIP를 사용할 수 있다.

```yaml
spec:
  type: ClusterIP
```

ClusterIP는 외부에서 직접 접근할 수 없다. 클러스터 내부 통신용이다.

확인:

```bash
kubectl get svc
```

CKA에서는 내부 서비스 연결 문제에서 자주 나온다.

---

# 11. NodePort

NodePort는 각 Node의 특정 포트를 열어서 외부에서 Service에 접근할 수 있게 하는 방식이다.

```text
외부 사용자
  ↓
NodeIP:NodePort
  ↓
Service
  ↓
Pod
```

예시:

```yaml
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080
```

여기서 의미는 다음과 같다.

```text
nodePort: 외부에서 접근하는 노드 포트
port: Service가 노출하는 포트
targetPort: Pod 컨테이너의 포트
```

CKA에서는 NodePort와 LoadBalancer, ClusterIP의 차이를 알아야 한다.

---

# 12. LoadBalancer

LoadBalancer는 클라우드 환경에서 외부 로드밸런서를 생성해 Service에 연결하는 타입이다.

```text
External LoadBalancer
  ↓
Service
  ↓
Pod
```

AWS, GCP, Azure 같은 클라우드 환경에서는 LoadBalancer 타입 Service를 만들면 클라우드 로드밸런서가 생성된다.

```yaml
spec:
  type: LoadBalancer
```

로컬 k3d, minikube 환경에서는 실제 클라우드 로드밸런서가 없기 때문에 별도 설정이 필요할 수 있다.

CKA에서는 LoadBalancer 개념 자체보다 Service 타입 간 차이를 이해하는 것이 중요하다.

---

# 13. Ingress

Ingress는 HTTP/HTTPS 요청을 Service로 라우팅하는 리소스다.

Service가 L4 수준의 포트 연결이라면, Ingress는 L7 수준의 HTTP 라우팅을 담당한다.

```text
example.com/api  → api-service
example.com/web  → web-service
```

Ingress 자체만 만든다고 동작하지 않는다. 반드시 Ingress Controller가 필요하다.

```text
Ingress = 라우팅 규칙
Ingress Controller = 실제로 트래픽을 처리하는 컨트롤러
```

예시 구조:

```text
Client
  ↓
Ingress Controller
  ↓
Ingress rule
  ↓
Service
  ↓
Pod
```

CKA에서는 Ingress rule, host, path, TLS, IngressClass를 다룰 수 있어야 한다.

---

# 14. Gateway API

Gateway API는 Ingress보다 더 발전된 Kubernetes 네트워크 라우팅 API다.

Ingress가 단순한 HTTP 라우팅 중심이라면, Gateway API는 역할을 더 명확하게 나눈다.

```text
GatewayClass
  ↓
Gateway
  ↓
HTTPRoute
  ↓
Service
```

각 개념은 다음과 같다.

```text
GatewayClass = 어떤 Gateway Controller를 사용할지 정의
Gateway = 실제 트래픽을 받을 입구
HTTPRoute = 어떤 요청을 어떤 Service로 보낼지 정의
```

예를 들어 `gateway.web.k8s.local`로 들어온 요청을 특정 Service로 보내는 방식이다.

CKA에서는 기존 Ingress를 Gateway API로 마이그레이션하는 문제가 나올 수 있다.

---

# 15. PV

PV는 PersistentVolume의 약자다.

Kubernetes 클러스터에서 사용할 수 있는 실제 저장소 리소스를 의미한다.

```text
PV = 클러스터에 준비된 저장소
```

예를 들어 NFS, local disk, cloud disk 같은 저장소가 PV로 표현될 수 있다.

```yaml
kind: PersistentVolume
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
```

PV는 Pod가 직접 사용하는 것이 아니라 PVC를 통해 사용한다.

---

# 16. PVC

PVC는 PersistentVolumeClaim의 약자다.

Pod가 저장소를 요청할 때 사용하는 리소스다.

```text
Pod
 ↓
PVC
 ↓
PV
```

PVC는 “1Gi짜리 저장소가 필요하다”처럼 요청서를 작성하는 느낌이다.

```yaml
kind: PersistentVolumeClaim
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

Pod에서는 PVC를 volume으로 연결한다.

```yaml
volumes:
  - name: data
    persistentVolumeClaim:
      claimName: my-pvc
```

CKA에서는 PVC가 Pending 상태일 때 원인을 찾는 문제가 나올 수 있다.

---

# 17. StorageClass

StorageClass는 저장소를 동적으로 생성하기 위한 템플릿이다.

PV를 사람이 미리 만들어두는 방식은 Static Provisioning이고, PVC가 생성될 때 자동으로 PV가 만들어지는 방식은 Dynamic Provisioning이다.

```text
PVC 생성
  ↓
StorageClass 참조
  ↓
PV 자동 생성
```

StorageClass는 어떤 provisioner를 사용할지 정의한다.

```yaml
kind: StorageClass
provisioner: kubernetes.io/no-provisioner
```

CKA에서는 PVC, PV, StorageClass의 관계를 이해해야 한다.

```text
PV = 실제 저장소
PVC = 저장소 요청
StorageClass = 저장소 자동 생성 방식
```

---

# 18. Role

Role은 특정 namespace 안에서 권한을 정의하는 리소스다.

예를 들어 dev namespace 안에서 Pod를 조회할 수 있는 권한을 만들 수 있다.

```bash
kubectl create role pod-reader \
  --verb=get,list,watch \
  --resource=pods \
  -n dev
```

Role은 권한만 정의한다. 실제 사용자나 ServiceAccount에 연결하려면 RoleBinding이 필요하다.

```text
Role = 권한 내용
RoleBinding = 권한을 누구에게 줄지 연결
```

---

# 19. ClusterRole

ClusterRole은 클러스터 범위의 권한을 정의하는 리소스다.

Role은 namespace 안에서만 동작하지만, ClusterRole은 클러스터 전체 리소스나 여러 namespace에 걸친 권한을 정의할 수 있다.

```bash
kubectl create clusterrole node-reader \
  --verb=get,list,watch \
  --resource=nodes
```

ClusterRole은 RoleBinding과도 연결할 수 있고, ClusterRoleBinding과도 연결할 수 있다.

```text
ClusterRole + RoleBinding = 특정 namespace 안에서만 권한 부여
ClusterRole + ClusterRoleBinding = 클러스터 전체에 권한 부여
```

---

# 20. RoleBinding

RoleBinding은 Role 또는 ClusterRole을 특정 대상에게 연결하는 리소스다.

대상은 User, Group, ServiceAccount가 될 수 있다.

```bash
kubectl create rolebinding read-pods \
  --role=pod-reader \
  --serviceaccount=dev:dev-sa \
  -n dev
```

이 명령은 dev namespace의 dev-sa ServiceAccount에게 pod-reader Role을 연결한다.

권한 확인은 다음 명령어로 한다.

```bash
kubectl auth can-i get pods \
  --as=system:serviceaccount:dev:dev-sa \
  -n dev
```

CKA에서 RBAC 문제를 풀 때 `auth can-i`는 매우 중요하다.

---

# 21. ClusterRoleBinding

ClusterRoleBinding은 ClusterRole을 클러스터 전체 범위로 특정 대상에게 연결한다.

```bash
kubectl create clusterrolebinding read-nodes \
  --clusterrole=node-reader \
  --serviceaccount=dev:dev-sa
```

이 경우 dev-sa는 클러스터 전체에서 node-reader 권한을 갖게 된다.

정리하면 다음과 같다.

```text
Role = namespace 권한
ClusterRole = 클러스터 권한

RoleBinding = namespace 안에서 권한 연결
ClusterRoleBinding = 클러스터 전체 권한 연결
```

---

# 22. ServiceAccount

ServiceAccount는 Pod가 Kubernetes API에 접근할 때 사용하는 계정이다.

사람이 kubectl로 접근할 때는 User 계정을 쓰고, Pod 내부 애플리케이션이 API에 접근할 때는 ServiceAccount를 사용한다.

```bash
kubectl create serviceaccount app-sa -n dev
```

Pod에 ServiceAccount를 지정할 수 있다.

```yaml
spec:
  serviceAccountName: app-sa
```

CKA에서는 ServiceAccount를 만들고 RoleBinding으로 권한을 부여하는 문제가 자주 나온다.

---

# 23. kubeadm

kubeadm은 Kubernetes 클러스터를 설치하고 관리하는 도구다.

Control Plane을 초기화할 때 사용한다.

```bash
kubeadm init
```

Worker Node를 클러스터에 join할 때도 사용한다.

```bash
kubeadm join <control-plane-ip>:6443 --token <token> ...
```

클러스터 업그레이드에도 사용된다.

```bash
kubeadm upgrade plan
kubeadm upgrade apply
```

CKA에서는 kubeadm init, join, upgrade, reset, token 관련 문제가 나올 수 있다.

---

# 24. kubelet

kubelet은 각 Node에서 실행되는 에이전트다.

kubelet은 API Server로부터 Pod 실행 명령을 받고, 해당 Node에서 컨테이너가 잘 실행되도록 관리한다.

```text
API Server
  ↓
kubelet
  ↓
container runtime
  ↓
container
```

kubelet에 문제가 생기면 Node가 NotReady가 되거나 Pod가 실행되지 않을 수 있다.

확인 명령어:

```bash
systemctl status kubelet
journalctl -u kubelet
```

CKA troubleshooting에서 kubelet은 매우 중요하다.

---

# 25. kube-apiserver

kube-apiserver는 Kubernetes 클러스터의 입구다.

kubectl 명령어를 치면 대부분 kube-apiserver로 요청이 간다.

```text
kubectl
  ↓
kube-apiserver
  ↓
etcd / scheduler / controller
```

모든 Kubernetes 리소스 생성, 조회, 수정, 삭제 요청은 API Server를 거친다.

kube-apiserver가 죽으면 kubectl 명령어 자체가 제대로 동작하지 않는다.

Control Plane 장애 문제에서 kube-apiserver static pod 설정을 확인해야 할 수 있다.

```bash
ls /etc/kubernetes/manifests
```

---

# 26. etcd

etcd는 Kubernetes 클러스터 상태를 저장하는 key-value 저장소다.

Pod, Service, Deployment, ConfigMap 같은 리소스 정보가 etcd에 저장된다.

```text
etcd = Kubernetes의 상태 저장소
```

etcd가 망가지면 클러스터 상태를 잃을 수 있기 때문에 백업과 복구가 중요하다.

CKA에서는 etcd snapshot 백업/복구 문제가 매우 중요하다.

```bash
ETCDCTL_API=3 etcdctl snapshot save snapshot.db
```

복구:

```bash
ETCDCTL_API=3 etcdctl snapshot restore snapshot.db
```

---

# 27. scheduler

scheduler는 새로 만들어진 Pod를 어느 Node에 배치할지 결정하는 컴포넌트다.

```text
Pod 생성
  ↓
scheduler가 적절한 Node 선택
  ↓
kubelet이 해당 Node에서 Pod 실행
```

scheduler는 다음 조건들을 고려한다.

```text
nodeSelector
affinity
taint/toleration
resource request
node 상태
```

Pod가 Pending 상태라면 scheduler가 배치할 Node를 찾지 못한 것일 수 있다.

```bash
kubectl describe pod <pod-name>
```

Events에 FailedScheduling 메시지가 있는지 확인해야 한다.

---

# 28. cordon

cordon은 특정 Node에 더 이상 새로운 Pod가 스케줄되지 않도록 막는 명령이다.

```bash
kubectl cordon node01
```

기존에 실행 중인 Pod는 그대로 둔다. 새 Pod만 올라가지 못하게 한다.

```text
cordon = 새 Pod 배치 금지
```

Node 점검 전에 자주 사용한다.

---

# 29. drain

drain은 Node에서 기존 Pod들을 다른 Node로 빼내는 명령이다.

```bash
kubectl drain node01 --ignore-daemonsets
```

Node를 점검하거나 업그레이드하기 전에 사용한다.

```text
cordon = 새 Pod 못 올라오게 막기
drain = 기존 Pod 빼내기
```

DaemonSet Pod는 기본적으로 drain 대상에서 제외해야 하므로 `--ignore-daemonsets` 옵션을 자주 사용한다.

---

# 30. taint

taint는 특정 Node에 아무 Pod나 올라오지 못하게 막는 설정이다.

```bash
kubectl taint nodes node01 key=value:NoSchedule
```

taint가 걸린 Node에는 해당 taint를 견딜 수 있는 toleration을 가진 Pod만 올라올 수 있다.

```text
Node taint = 이 Node에는 아무나 오지 마라
Pod toleration = 나는 그 조건을 견딜 수 있다
```

effect에는 대표적으로 다음이 있다.

```text
NoSchedule
PreferNoSchedule
NoExecute
```

---

# 31. toleration

toleration은 Pod가 Node의 taint를 견딜 수 있도록 하는 설정이다.

```yaml
tolerations:
  - key: "key"
    operator: "Equal"
    value: "value"
    effect: "NoSchedule"
```

taint가 Node 입장에서 “막는 조건”이라면, toleration은 Pod 입장에서 “그 조건을 허용하는 설정”이다.

```text
taint = Node가 거부
toleration = Pod가 허용
```

CKA에서는 taint가 걸린 Node에 특정 Pod를 올리는 문제가 나올 수 있다.

---

# 32. nodeSelector

nodeSelector는 특정 label이 붙은 Node에만 Pod를 배치하는 가장 단순한 스케줄링 방법이다.

먼저 Node에 label을 붙인다.

```bash
kubectl label node node01 disktype=ssd
```

Pod에 nodeSelector를 설정한다.

```yaml
spec:
  nodeSelector:
    disktype: ssd
```

그러면 해당 Pod는 `disktype=ssd` label이 붙은 Node에만 배치된다.

CKA에서는 특정 Node에 Pod를 배치하라는 문제가 나올 수 있다.

---

# 33. affinity

affinity는 nodeSelector보다 더 정교한 스케줄링 규칙이다.

대표적으로 Node Affinity와 Pod Affinity가 있다.

```text
Node Affinity = 특정 조건의 Node에 배치
Pod Affinity = 특정 Pod와 가까이 배치
Pod Anti-Affinity = 특정 Pod와 떨어뜨려 배치
```

Node Affinity는 다음처럼 사용한다.

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
```

`required`는 반드시 만족해야 하는 조건이고, `preferred`는 가능하면 만족하면 좋은 조건이다.

```text
required = 필수 조건
preferred = 선호 조건
```

CKA에서는 nodeSelector보다 복잡한 스케줄링 조건으로 affinity가 등장할 수 있다.

---

# 34. logs

logs는 컨테이너 애플리케이션 로그를 확인하는 명령이다.

```bash
kubectl logs <pod-name>
```

여러 컨테이너가 있는 Pod라면 컨테이너 이름을 지정해야 한다.

```bash
kubectl logs <pod-name> -c <container-name>
```

이전 컨테이너 로그를 볼 때는 `--previous`를 사용한다.

```bash
kubectl logs <pod-name> --previous
```

CKA에서 애플리케이션이 왜 죽는지 확인할 때 가장 먼저 쓰는 명령어 중 하나다.

---

# 35. describe

describe는 리소스의 상세 상태와 이벤트를 확인하는 명령이다.

```bash
kubectl describe pod <pod-name>
```

describe는 단순 조회보다 더 자세한 정보를 보여준다.

Pod의 경우 다음을 확인할 수 있다.

```text
Node 배치 여부
Container 상태
Image pull 상태
Volume mount 상태
Events
```

Pod가 Pending, CrashLoopBackOff, ImagePullBackOff 상태일 때 describe를 보면 원인을 찾기 쉽다.

CKA troubleshooting의 핵심 명령어다.

---

# 36. events

events는 Kubernetes 클러스터에서 발생한 사건 기록이다.

예를 들어 스케줄링 실패, 이미지 pull 실패, probe 실패 같은 정보가 event에 남는다.

```bash
kubectl get events
```

시간순으로 보고 싶으면 다음처럼 사용한다.

```bash
kubectl get events --sort-by=.metadata.creationTimestamp
```

namespace를 지정하는 것도 중요하다.

```bash
kubectl get events -n dev --sort-by=.metadata.creationTimestamp
```

CKA에서는 describe 하단의 Events와 `kubectl get events`를 통해 원인을 찾는 일이 많다.

---

# 37. top

top은 리소스 사용량을 확인하는 명령이다.

Pod CPU/Memory 사용량 확인:

```bash
kubectl top pod
```

Node CPU/Memory 사용량 확인:

```bash
kubectl top node
```

이 명령은 metrics-server가 설치되어 있어야 동작한다.

CKA에서는 리소스 사용량 확인, HPA 확인, 노드 상태 점검에서 사용할 수 있다.

---

# 38. journalctl

journalctl은 Linux systemd 로그를 확인하는 명령이다.

Kubernetes에서는 kubelet 로그를 볼 때 자주 사용한다.

```bash
journalctl -u kubelet
```

최근 로그만 보고 싶으면 다음처럼 쓸 수 있다.

```bash
journalctl -u kubelet -f
```

kubelet이 죽었거나 Node가 NotReady 상태일 때 확인해야 한다.

```bash
systemctl status kubelet
journalctl -u kubelet
```

CKA에서 클러스터 컴포넌트 장애나 Node 문제를 고칠 때 중요하다.

---

# 39. NetworkPolicy

NetworkPolicy는 Pod 간 네트워크 통신을 제한하는 리소스다.

기본적으로 Kubernetes에서는 Pod끼리 자유롭게 통신할 수 있다. NetworkPolicy를 사용하면 특정 Pod에서 특정 Pod로만 통신하도록 제한할 수 있다.

```text
NetworkPolicy = Pod 간 통신 방화벽
```

NetworkPolicy는 label selector를 기반으로 동작한다.

```yaml
podSelector:
  matchLabels:
    app: web
```

Ingress와 Egress를 나눠서 제어할 수 있다.

```text
ingress = 들어오는 트래픽
egress = 나가는 트래픽
```

주의할 점은 NetworkPolicy를 지원하는 CNI가 있어야 실제로 동작한다는 것이다.

CKA에서는 특정 namespace나 Pod 사이의 통신을 허용/차단하는 문제가 나올 수 있다.

---

# 40. CoreDNS

CoreDNS는 Kubernetes 클러스터 내부 DNS를 담당한다.

Service 이름으로 통신할 수 있는 이유가 CoreDNS 때문이다.

```text
my-service.default.svc.cluster.local
```

Pod 안에서 Service 이름으로 요청하면 CoreDNS가 Service IP를 찾아준다.

```bash
nslookup my-service
```

CoreDNS는 보통 kube-system namespace에 있다.

```bash
kubectl get pod -n kube-system
kubectl logs -n kube-system -l k8s-app=kube-dns
```

Service 이름으로 접근이 안 된다면 CoreDNS 문제인지, Service 문제인지, Endpoint 문제인지 확인해야 한다.

---

# 41. Endpoint

Endpoint는 Service가 실제로 연결할 Pod IP 목록이다.

Service가 selector로 Pod를 찾으면, 그 결과가 Endpoint에 저장된다.

```text
Service
  ↓
Endpoint
  ↓
Pod IP
```

Service는 있는데 통신이 안 되면 Endpoint를 확인해야 한다.

```bash
kubectl get endpoints
```

Endpoint가 비어 있다면 보통 selector와 label이 맞지 않는 것이다.

```text
Service selector 불일치
Pod label 없음
Pod가 Ready 상태 아님
```

CKA에서 Service troubleshooting의 핵심이다.

---

# 42. EndpointSlice

EndpointSlice는 Endpoint의 확장 버전이다.

Pod가 많아질수록 하나의 Endpoint 리소스에 모든 Pod IP를 담는 방식은 비효율적이다. EndpointSlice는 Endpoint 정보를 여러 조각으로 나눠 관리한다.

```text
EndpointSlice = Endpoint 정보를 더 확장성 있게 관리하는 리소스
```

확인 명령어:

```bash
kubectl get endpointslice
```

CKA에서는 Endpoint와 EndpointSlice를 함께 볼 수 있으면 Service 문제를 더 정확하게 확인할 수 있다.

---

# 43. Helm

Helm은 Kubernetes의 패키지 매니저다.

여러 YAML 파일을 하나의 Chart로 묶어서 설치, 업그레이드, 삭제할 수 있게 해준다.

```text
Helm Chart = Kubernetes YAML 패키지
Release = Chart를 설치한 결과물
values.yaml = 설정값 파일
```

기본 명령어:

```bash
helm repo add
helm repo update
helm install
helm upgrade
helm uninstall
helm list
```

예를 들어 Nginx Ingress Controller, Prometheus, Grafana 같은 도구를 설치할 때 Helm을 자주 사용한다.

CKA에서는 Helm으로 컴포넌트를 설치하거나 values를 수정하는 문제가 나올 수 있다.

---

# 44. Kustomize

Kustomize는 Kubernetes YAML을 환경별로 조합하고 수정할 수 있게 해주는 도구다.

Helm은 템플릿 기반이고, Kustomize는 기존 YAML을 patch하는 방식에 가깝다.

```text
base = 공통 YAML
overlay = 환경별 수정 YAML
```

예를 들어 dev와 prod가 같은 Deployment를 쓰되 replica 수만 다르게 하고 싶을 때 Kustomize를 사용할 수 있다.

```bash
kubectl apply -k .
```

주요 파일:

```text
kustomization.yaml
```

CKA에서는 Kustomize를 사용해 리소스를 배포하거나 patch하는 문제가 나올 수 있다.

---

# 45. CRD

CRD는 CustomResourceDefinition의 약자다.

Kubernetes에 기본으로 있는 리소스는 Pod, Service, Deployment 같은 것들이다. CRD를 사용하면 새로운 리소스 타입을 직접 추가할 수 있다.

```text
기본 리소스:
Pod, Service, Deployment

CRD로 추가된 리소스:
Certificate, Gateway, Prometheus, MyApp 등
```

CRD를 만들면 Kubernetes API에 새로운 Kind가 생긴다.

```bash
kubectl get crd
```

예를 들어 cert-manager를 설치하면 Certificate 같은 리소스가 생긴다. Gateway API도 CRD 형태로 설치되는 경우가 많다.

CKA에서는 CRD 자체를 깊게 개발하는 것보다는, CRD가 무엇이고 어떻게 조회하는지 정도를 알아두면 좋다.

---

# 46. Operator

Operator는 Kubernetes에서 특정 애플리케이션 운영을 자동화하는 컨트롤러다.

단순히 리소스를 생성하는 것을 넘어서, 백업, 복구, 스케일링, 장애 대응 같은 운영 작업을 자동화할 수 있다.

```text
CRD = 새로운 리소스 타입
Operator = 그 리소스를 보고 실제 운영 작업을 수행하는 컨트롤러
```

예를 들어 Prometheus Operator는 Prometheus 관련 CRD를 보고 Prometheus 서버를 자동으로 구성한다.

```text
ServiceMonitor 생성
  ↓
Prometheus Operator가 감지
  ↓
Prometheus 설정 자동 반영
```

CKA에서는 Operator를 직접 만드는 문제는 거의 아니지만, CRD와 Operator의 관계를 이해하면 Kubernetes 확장 구조를 이해하기 쉽다.

---

# 전체 관계 요약

CKA에서 이 개념들은 따로따로 외우는 것이 아니라 흐름으로 연결해서 이해해야 한다.

```text
Deployment가 Pod를 만든다.
Pod는 Container를 실행한다.
Service는 Label/Selector로 Pod를 찾는다.
Endpoint는 Service가 찾은 Pod IP 목록이다.
Ingress나 Gateway API는 외부 HTTP 요청을 Service로 보낸다.
ConfigMap과 Secret은 Pod에 설정값을 주입한다.
PVC는 Pod가 저장소를 요청하는 방식이다.
PV는 실제 저장소이고, StorageClass는 저장소를 자동 생성하는 방식이다.
Role과 ClusterRole은 권한을 정의한다.
RoleBinding과 ClusterRoleBinding은 권한을 대상에게 연결한다.
ServiceAccount는 Pod가 사용할 계정이다.
scheduler는 Pod를 Node에 배치한다.
kubelet은 Node에서 Pod를 실행한다.
kube-apiserver는 모든 요청의 입구다.
etcd는 클러스터 상태를 저장한다.
CoreDNS는 Service 이름을 IP로 바꿔준다.
NetworkPolicy는 Pod 간 통신을 제어한다.
Helm과 Kustomize는 YAML 배포를 편하게 해준다.
CRD와 Operator는 Kubernetes를 확장한다.
```

---

# CKA 관점에서 제일 중요한 감각

이 단어들을 단순히 외우는 것보다 중요한 것은 “문제가 생겼을 때 어디를 봐야 하는가”다.

예를 들어 Service가 안 되면 다음 순서로 본다.

```bash
kubectl get svc
kubectl describe svc <service-name>
kubectl get endpoints
kubectl get pod --show-labels
kubectl describe pod <pod-name>
```

Pod가 안 뜨면 다음 순서로 본다.

```bash
kubectl get pod
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl get events --sort-by=.metadata.creationTimestamp
```

Node가 이상하면 다음 순서로 본다.

```bash
kubectl get nodes
kubectl describe node <node-name>
systemctl status kubelet
journalctl -u kubelet
```

권한 문제가 나면 다음 순서로 본다.

```bash
kubectl auth can-i <verb> <resource>
kubectl get role,rolebinding -n <namespace>
kubectl get clusterrole,clusterrolebinding
```

---

# 마무리

CKA는 개념을 많이 아는 시험이 아니라, Kubernetes 리소스를 실제로 만들고 고치고 확인하는 시험이다. 그래서 위 단어들은 “암기 목록”이라기보다 “문제를 풀 때 계속 만나게 되는 기본 도구 이름”에 가깝다.

처음에는 Pod, Deployment, Service, Namespace, Label, Selector부터 잡고, 그다음 Storage, RBAC, Scheduling, Troubleshooting, Networking으로 넓혀가면 된다.

결국 CKA에서 중요한 흐름은 이거다.

```text
무엇을 만들 것인가
어디에 배치할 것인가
어떻게 연결할 것인가
어떤 설정을 주입할 것인가
어떤 권한을 줄 것인가
어디가 고장났는지 어떻게 찾을 것인가
```

이 흐름으로 보면 Kubernetes 단어들이 따로 놀지 않고 하나의 운영 시스템으로 연결된다.
