---
title: "[Kubernetes] K8s API란? 쿠버네티스가 움직이는 진짜 입구"
source: "https://velog.io/@yorange50/Kubernetes-K8s-API란-쿠버네티스가-움직이는-진짜-입구"
published: "2026-05-28T23:58:39.701Z"
tags: ""
backup_date: "2026-05-29T14:52:52.702741"
---


쿠버네티스를 쓰다 보면 이런 명령어를 자주 입력한다.

```bash
kubectl get pod
kubectl apply -f deployment.yaml
kubectl delete svc nginx
kubectl describe node worker-1
```

겉으로 보면 `kubectl`이 직접 쿠버네티스를 조작하는 것처럼 보인다.

그런데 실제로는 `kubectl`이 직접 Pod를 만들고, Service를 지우고, Deployment를 수정하는 것이 아니다.

`kubectl`은 **Kubernetes API Server에게 요청을 보내는 클라이언트**다.

즉 쿠버네티스의 모든 조작은 결국 **K8s API**를 통해 들어간다.

---

## 1. K8s API를 한 줄로 말하면

K8s API는 쿠버네티스 클러스터의 상태를 조회하고 변경하기 위한 인터페이스다.

쉽게 말하면 이거다.

```text
K8s API
= 쿠버네티스에게 명령을 전달하는 공식 창구
= 클러스터 상태를 읽고 바꾸는 통로
= kubectl, 컨트롤러, 스케줄러, kubelet이 모두 사용하는 입구
```

우리가 쿠버네티스에게 뭔가를 시키고 싶다면 결국 API Server를 거쳐야 한다.

Pod를 만들 때도,
Deployment를 수정할 때도,
Service를 삭제할 때도,
Node 상태를 조회할 때도 마찬가지다.

전부 K8s API를 통해 처리된다.

---

## 2. 누가 K8s API를 사용할까?

가장 먼저 떠오르는 건 사용자다.

```text
사용자
  ↓
kubectl
  ↓
Kubernetes API Server
```

우리가 `kubectl` 명령어를 입력하면, `kubectl`은 그 명령을 Kubernetes API 요청으로 바꿔서 API Server에 보낸다.

그런데 K8s API를 쓰는 건 사용자만이 아니다.

쿠버네티스 내부 컴포넌트들도 API Server와 계속 통신한다.

```text
Scheduler
Controller Manager
kubelet
kube-proxy
Operator
Custom Controller
```

즉 API Server는 쿠버네티스의 중심 입구다.

조금 비유하면 API Server는 쿠버네티스 클러스터의 **프론트 데스크** 같은 역할을 한다.

누가 와서 요청하든, 일단 여기로 들어온다.

---

## 3. kubectl은 사실 API 요청 도구다

예를 들어 우리가 이렇게 입력한다고 하자.

```bash
kubectl get pods
```

이 명령은 내부적으로 대략 이런 API 요청으로 바뀐다.

```http
GET /api/v1/namespaces/default/pods
```

Deployment를 조회하면 이런 느낌이다.

```bash
kubectl get deployment
```

내부적으로는 대략 이런 API를 바라본다.

```http
GET /apis/apps/v1/namespaces/default/deployments
```

즉 `kubectl`은 사람이 쓰기 편한 명령어를 Kubernetes API 요청으로 바꿔주는 도구다.

우리는 `kubectl get pod`처럼 간단히 쓰지만, 뒤에서는 API Server에게 HTTP 요청을 보내고 있는 것이다.

---

## 4. K8s API와 kube-apiserver는 다르다

여기서 헷갈리기 쉬운 게 있다.

**K8s API**와 **kube-apiserver**는 같은 말이 아니다.

```text
K8s API
= 쿠버네티스가 제공하는 API 규칙, 인터페이스

kube-apiserver
= 그 API를 실제로 제공하는 서버 프로세스
```

비유하면 이렇다.

```text
API
= 식당 메뉴판과 주문 규칙

API Server
= 실제 주문을 받는 카운터
```

K8s API는 “어떤 방식으로 요청을 보내야 하는지”에 대한 규칙이다.
kube-apiserver는 그 요청을 실제로 받아서 처리하는 서버다.

그래서 사용자는 보통 직접 etcd나 kubelet을 건드리지 않고, kube-apiserver를 통해 쿠버네티스와 대화한다.

---

## 5. 쿠버네티스에서 리소스란?

K8s API는 리소스 중심으로 동작한다.

우리가 자주 보는 것들이 전부 API 리소스다.

```text
Pod
Service
Deployment
ReplicaSet
ConfigMap
Secret
Namespace
Node
PersistentVolumeClaim
Ingress
Role
RoleBinding
```

쿠버네티스에서 리소스는 클러스터의 상태를 표현하는 객체다.

예를 들어 Deployment는 이런 상태를 표현한다.

```text
nginx 컨테이너를 사용하는 Pod를 3개 유지하고 싶다.
```

Service는 이런 상태를 표현한다.

```text
특정 라벨을 가진 Pod들에게 안정적인 접근 주소를 제공하고 싶다.
```

ConfigMap은 이런 상태를 표현한다.

```text
애플리케이션 설정값을 클러스터 안에 저장하고 싶다.
```

즉 쿠버네티스의 모든 것은 API 객체로 표현된다.

---

## 6. YAML은 그냥 설정 파일이 아니다

쿠버네티스를 처음 배울 때 YAML을 보면 그냥 설정 파일처럼 느껴진다.

하지만 조금 더 정확히 말하면 YAML은 **K8s API Server에 보내는 리소스 정의서**다.

예를 들어 이런 YAML이 있다고 하자.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deploy
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
          image: nginx:1.25
```

이걸 적용한다.

```bash
kubectl apply -f deployment.yaml
```

그러면 실제로는 이런 일이 일어난다.

```text
1. kubectl이 YAML을 읽음
2. apiVersion, kind를 보고 어떤 API로 보낼지 판단
3. kube-apiserver에 요청 전송
4. API Server가 문법과 권한 검증
5. etcd에 원하는 상태 저장
6. Controller가 그 상태를 보고 실제 Pod 생성
```

중요한 건 이거다.

```text
kubectl apply는 Pod를 직접 만드는 명령이 아니다.
API Server에게 “이 상태가 되게 해줘”라고 요청하는 명령이다.
```

---

## 7. apiVersion과 kind가 중요한 이유

YAML을 보면 항상 이런 필드가 나온다.

```yaml
apiVersion: apps/v1
kind: Deployment
```

이 두 줄은 Kubernetes API 입장에서 매우 중요하다.

```text
apiVersion
= 어느 API 그룹과 버전을 사용할지

kind
= 어떤 리소스 타입인지
```

예를 들어보자.

```yaml
apiVersion: v1
kind: Pod
```

이건 core API group의 Pod를 의미한다.

```yaml
apiVersion: apps/v1
kind: Deployment
```

이건 apps API group의 Deployment를 의미한다.

```yaml
apiVersion: batch/v1
kind: Job
```

이건 batch API group의 Job을 의미한다.

자주 보는 리소스를 정리하면 이렇다.

| 리소스           | apiVersion           |
| ------------- | -------------------- |
| Pod           | v1                   |
| Service       | v1                   |
| ConfigMap     | v1                   |
| Secret        | v1                   |
| Deployment    | apps/v1              |
| DaemonSet     | apps/v1              |
| StatefulSet   | apps/v1              |
| Job           | batch/v1             |
| CronJob       | batch/v1             |
| Ingress       | networking.k8s.io/v1 |
| NetworkPolicy | networking.k8s.io/v1 |
| HPA           | autoscaling/v2       |

그래서 YAML을 볼 때는 먼저 이 두 개를 보면 된다.

```text
apiVersion: 어느 API 그룹이지?
kind: 어떤 리소스를 만들려는 거지?
```

이것만 봐도 YAML의 정체가 어느 정도 보인다.

---

## 8. spec과 status

쿠버네티스 API 객체에서 정말 중요한 구조가 있다.

바로 `spec`과 `status`다.

```yaml
spec:
  replicas: 3

status:
  availableReplicas: 3
```

둘의 의미는 완전히 다르다.

```text
spec
= 사용자가 원하는 상태
= desired state

status
= 쿠버네티스가 관찰한 현재 상태
= current state
```

예를 들어 Deployment에 이렇게 적었다고 하자.

```yaml
spec:
  replicas: 3
```

이 말은 이런 뜻이다.

```text
나는 nginx Pod가 3개 떠 있기를 원한다.
```

그런데 현재 Pod가 1개만 떠 있다면 status는 이런 상태일 수 있다.

```yaml
status:
  replicas: 1
  availableReplicas: 1
```

그러면 Deployment Controller가 API Server를 계속 보다가 이렇게 판단한다.

```text
원하는 상태: 3개
현재 상태: 1개
부족한 상태: 2개

→ Pod를 2개 더 만들어야 한다.
```

이게 쿠버네티스의 핵심 동작 방식이다.

사용자는 `spec`에 원하는 상태를 적는다.
쿠버네티스는 `status`를 보면서 실제 상태를 원하는 상태에 맞춘다.

---

## 9. API Server 뒤에는 etcd가 있다

API Server는 요청을 받는 입구다.

그렇다면 클러스터 상태는 어디에 저장될까?

바로 **etcd**다.

```text
kubectl
  ↓
kube-apiserver
  ↓
etcd
```

예를 들어 사용자가 Deployment를 만들면 API Server는 그 객체 정보를 etcd에 저장한다.

그러면 컨트롤러들이 API Server를 통해 그 상태를 감시한다.

```text
Deployment 객체가 생겼네?
replicas가 3개네?

→ ReplicaSet 만들자.
→ Pod 3개 만들자.
```

중요한 건 보통 사용자가 etcd를 직접 건드리지 않는다는 점이다.

클러스터 상태는 API Server를 통해 다루는 것이 기본이다.

---

## 10. Deployment를 apply하면 실제로 일어나는 일

예를 들어 사용자가 Deployment를 적용한다고 하자.

```bash
kubectl apply -f deployment.yaml
```

전체 흐름은 이렇게 볼 수 있다.

```text
[사용자]
  |
  | kubectl apply -f deployment.yaml
  v
[kubectl]
  |
  | HTTP 요청
  v
[kube-apiserver]
  |
  | 인증, 인가, 검증
  v
[etcd]
  |
  | 원하는 상태 저장
  v
[controller-manager]
  |
  | Deployment 상태 감시
  v
[ReplicaSet 생성]
  |
  v
[Pod 생성 요청]
  |
  v
[scheduler]
  |
  | 어느 노드에 띄울지 결정
  v
[kubelet]
  |
  | 해당 노드에서 컨테이너 실행
  v
[Pod Running]
```

이 흐름에서 모든 컴포넌트가 API Server를 중심으로 움직인다.

`kubectl`도 API Server를 보고,
Controller도 API Server를 보고,
Scheduler도 API Server를 보고,
kubelet도 API Server와 통신한다.

그래서 API Server가 쿠버네티스의 중심 입구라고 하는 것이다.

---

## 11. K8s API는 선언형이다

쿠버네티스가 특이한 이유는 명령형보다 선언형에 가깝기 때문이다.

명령형은 이런 느낌이다.

```text
Pod 하나 만들어.
그 다음 이 노드에 배치해.
죽으면 다시 만들어.
```

반면 선언형은 이런 느낌이다.

```text
nginx Pod가 항상 3개 떠 있는 상태를 원해.
```

쿠버네티스에서는 사용자가 최종 상태를 선언한다.

```yaml
spec:
  replicas: 3
```

그러면 쿠버네티스가 현재 상태를 계속 관찰하면서 원하는 상태에 맞춘다.

```text
원하는 상태: 3개
현재 상태: 2개

→ 1개 더 생성
```

그래서 YAML은 실행 스크립트라기보다 **원하는 최종 상태를 적은 문서**에 가깝다.

---

## 12. API 요청 전에 일어나는 검사

API Server는 아무 요청이나 받아주지 않는다.

요청이 들어오면 대략 이런 과정을 거친다.

```text
1. Authentication
   너 누구야?

2. Authorization
   이 작업 할 권한 있어?

3. Admission Control
   클러스터 정책상 허용되는 요청이야?

4. Validation
   YAML 구조와 필드가 맞아?

5. etcd 저장
   문제가 없으면 상태 저장
```

예를 들어 권한이 없으면 이런 에러가 난다.

```text
Error from server (Forbidden): pods is forbidden
```

YAML 필드가 틀리면 이런 에러가 날 수 있다.

```text
error validating data
```

즉 API Server는 단순히 요청을 전달하는 곳이 아니다.

쿠버네티스 클러스터의 문지기 역할도 한다.

---

## 13. CKA에서 자주 나오는 관점

CKA나 쿠버네티스 실습에서는 “API”라는 단어가 직접 크게 나오지 않아도, 사실 거의 모든 문제가 API 객체를 다루는 문제다.

예를 들어 이런 문제들이 나온다.

```text
Pod 만들어라
Deployment 수정해라
Service 노출해라
ConfigMap 만들어라
Secret 연결해라
HPA 설정해라
Ingress 만들어라
```

전부 Kubernetes API object를 만드는 문제다.

그래서 YAML을 볼 때 이렇게 읽는 습관이 중요하다.

```text
apiVersion
= 이 리소스가 어느 API 그룹에 속하지?

kind
= 어떤 리소스를 만들지?

metadata
= 이름, 네임스페이스, 라벨은?

spec
= 내가 원하는 상태는?

status
= 현재 실제 상태는?
```

특히 `kubectl explain`을 잘 써야 한다.

```bash
kubectl explain deployment
kubectl explain deployment.spec
kubectl explain deployment.spec.template.spec.containers
```

이 명령은 해당 리소스의 API 필드 설명을 보여준다.

즉 시험장에서 모든 YAML 구조를 외우기보다, `kubectl explain`으로 API 구조를 확인하는 습관이 중요하다.

---

## 14. 자주 쓰는 API 관련 명령어

API 리소스 목록 보기

```bash
kubectl api-resources
```

특정 리소스의 API 버전 확인

```bash
kubectl api-resources | grep deployment
```

출력 예시

```text
deployments   deploy   apps/v1   true   Deployment
```

API 버전 목록 보기

```bash
kubectl api-versions
```

리소스 구조 확인

```bash
kubectl explain pod
kubectl explain service
kubectl explain deployment.spec
```

실제 객체 YAML 보기

```bash
kubectl get pod nginx -o yaml
```

API Server 주소 확인

```bash
kubectl cluster-info
```

현재 kubectl이 어떤 API Server를 보고 있는지 확인

```bash
kubectl config view
```

---

## 15. 그림으로 정리

전체 구조를 한 번에 보면 이렇다.

```text
사용자
  |
  | kubectl apply / get / delete
  v
kubectl
  |
  | Kubernetes API 요청
  v
kube-apiserver
  |
  | 인증 / 인가 / 검증
  v
etcd
  |
  | 클러스터 상태 저장
  v
Controller / Scheduler / Kubelet
  |
  | 실제 상태를 원하는 상태에 맞춤
  v
Pod / Service / Deployment 등 실행
```

결국 쿠버네티스는 API Server를 중심으로 움직인다.

---

## 16. 한 번에 정리

K8s API는 쿠버네티스를 조작하는 중심 인터페이스다.

```text
K8s API
= 클러스터 상태를 읽고 쓰는 공식 통로

kube-apiserver
= 그 API를 실제로 제공하는 서버

kubectl
= 사람이 쓰는 명령어를 API 요청으로 바꿔주는 도구

YAML
= API Server에 보내는 리소스 정의서

spec
= 원하는 상태

status
= 현재 상태
```

그래서 쿠버네티스를 공부할 때는 단순히 명령어만 외우면 안 된다.

중요한 건 이 감각이다.

```text
나는 지금 Kubernetes API에 어떤 리소스를 요청하고 있는가?
이 YAML은 어떤 API 객체를 만들고 있는가?
spec에는 어떤 원하는 상태를 적고 있는가?
status는 실제로 어떻게 변했는가?
```

이 관점이 잡히면 Pod, Deployment, Service, Ingress, HPA, DaemonSet이 각각 따로 외워야 하는 대상이 아니라, 전부 Kubernetes API로 관리되는 객체들로 보이기 시작한다.

즉 쿠버네티스를 이해한다는 건 결국

> Kubernetes API를 통해 원하는 상태를 선언하고,
> 쿠버네티스가 그 상태를 맞춰가는 과정을 이해하는 것

이라고 볼 수 있다.
