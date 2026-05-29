---
title: "[Kubernetes] Service 종류 3가지: ClusterIP, NodePort, LoadBalancer"
source: "https://velog.io/@yorange50/Kubernetes-Service-종류-3가지-ClusterIP-NodePort-LoadBalancer"
published: "2026-05-14T03:56:05.351Z"
tags: ""
backup_date: "2026-05-29T14:52:52.743406"
---


쿠버네티스에서 Pod는 계속 생성되고 삭제될 수 있다.
문제는 Pod가 새로 만들어질 때마다 IP가 바뀔 수 있다는 점이다.

그래서 클라이언트가 Pod IP를 직접 바라보게 만들면 안정적이지 않다.

```text
Pod A IP: 10.244.1.3
Pod 삭제
Pod B 새로 생성
Pod B IP: 10.244.1.9
```

이런 상황에서 매번 바뀌는 Pod IP를 직접 찾아서 접근하는 건 현실적으로 어렵다.

그래서 Kubernetes는 **Service**라는 리소스를 제공한다.

---

# 1. Service란?

Service는 쉽게 말하면 **Pod 앞에 세우는 고정된 입구**다.

Pod는 바뀔 수 있지만, Service는 비교적 안정적인 주소를 제공한다.

```text
Client
  ↓
Service
  ↓
Pod
```

즉, 사용자는 Pod를 직접 찾는 것이 아니라 Service를 통해 접근한다.

Service는 뒤에 있는 Pod들을 selector로 찾아서 요청을 전달한다.

```yaml
selector:
  app: web
```

이렇게 되어 있으면 Service는 `app=web` 라벨을 가진 Pod들을 찾아서 요청을 보낸다.

---

# 2. 왜 Service가 필요할까?

Pod는 일회성에 가깝다.

Deployment가 Pod를 관리하긴 하지만, Pod 자체는 언제든지 죽고 다시 만들어질 수 있다.

예를 들어 장애가 나면 기존 Pod가 죽고 새 Pod가 생성된다.

```text
기존 Pod 죽음
  ↓
새 Pod 생성
  ↓
새 IP 할당
```

이때 Service가 없으면 클라이언트는 매번 바뀐 Pod IP를 알아야 한다.

하지만 Service가 있으면 클라이언트는 Service만 바라보면 된다.

```text
Client
  ↓
Service IP는 유지
  ↓
뒤쪽 Pod는 바뀌어도 됨
```

즉, Service의 핵심 목적은 다음과 같다.

```text
Pod의 IP가 바뀌어도
고정된 접근 지점을 제공하기 위해
```

---

# 3. Service 종류 3가지

CKA나 쿠버네티스 기초에서 가장 많이 보는 Service 종류는 보통 세 가지다.

```text
ClusterIP
NodePort
LoadBalancer
```

각각 접근 범위가 다르다.

```text
ClusterIP      → 클러스터 내부 접근
NodePort       → 외부에서 Node IP와 Port로 접근
LoadBalancer   → 클라우드 로드밸런서를 통해 외부 접근
```

---

# 4. ClusterIP

## ClusterIP란?

ClusterIP는 Kubernetes Service의 기본 타입이다.

Service를 만들 때 type을 따로 지정하지 않으면 기본적으로 ClusterIP가 된다.

```yaml
type: ClusterIP
```

ClusterIP는 **클러스터 내부에서만 접근 가능한 Service**다.

즉, 외부 사용자가 직접 접근하는 용도가 아니라, 클러스터 안의 Pod들끼리 통신할 때 사용한다.

---

## ClusterIP 구조

```text
Pod A
  ↓
ClusterIP Service
  ↓
Pod B
```

예를 들어 백엔드 Pod가 데이터베이스 Pod에 접근해야 한다고 해보자.

백엔드가 DB Pod의 IP를 직접 바라보면 위험하다.
DB Pod가 재시작되면 IP가 바뀔 수 있기 때문이다.

그래서 DB 앞에 Service를 둔다.

```text
backend Pod
  ↓
db-service
  ↓
db Pod
```

백엔드는 DB Pod IP를 몰라도 된다.
그냥 `db-service`라는 Service 이름으로 접근하면 된다.

---

## ClusterIP 예시 YAML

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: ClusterIP
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8080
```

여기서 중요한 부분은 이거다.

```yaml
type: ClusterIP
```

그리고 port와 targetPort의 의미는 다음과 같다.

```text
port
= Service가 받는 포트

targetPort
= Pod 컨테이너로 전달할 포트
```

즉, 요청 흐름은 이렇게 된다.

```text
Client Pod
  ↓
web-service:80
  ↓
web Pod:8080
```

---

## ClusterIP 특징 정리

```text
클러스터 내부에서만 접근 가능
Service의 기본 타입
Pod 간 통신에 사용
외부에서는 직접 접근 불가
```

한 줄로 정리하면 이렇다.

```text
ClusterIP = 클러스터 내부용 고정 입구
```

---

# 5. NodePort

## NodePort란?

NodePort는 외부에서 Kubernetes 클러스터 안의 Pod에 접근할 수 있게 해주는 Service 타입이다.

```yaml
type: NodePort
```

NodePort를 사용하면 각 Node의 특정 포트가 열린다.

외부 사용자는 다음과 같은 방식으로 접근할 수 있다.

```text
NodeIP:NodePort
```

예를 들어 Node IP가 `192.168.0.10`이고 nodePort가 `30080`이면 다음처럼 접근한다.

```text
http://192.168.0.10:30080
```

---

## NodePort 구조

```text
외부 사용자
  ↓
NodeIP:30080
  ↓
NodePort Service
  ↓
Pod
```

NodePort는 외부 접근이 가능하기 때문에 실습에서 자주 사용된다.

특히 KodeKloud나 CKA 연습 문제에서 이런 형태가 많이 나온다.

```text
Create a Service
Type: NodePort
targetPort: 8080
port: 8080
nodePort: 30080
```

---

## NodePort 예시 YAML

```yaml
apiVersion: v1
kind: Service
metadata:
  name: webapp-service
spec:
  type: NodePort
  selector:
    name: simple-webapp
  ports:
  - port: 8080
    targetPort: 8080
    nodePort: 30080
```

이 설정을 하나씩 보면 다음과 같다.

```yaml
type: NodePort
```

Service 타입을 NodePort로 만든다는 뜻이다.

```yaml
selector:
  name: simple-webapp
```

`name=simple-webapp` 라벨을 가진 Pod로 요청을 보내겠다는 뜻이다.

```yaml
port: 8080
```

Service가 내부적으로 받을 포트다.

```yaml
targetPort: 8080
```

Pod 컨테이너로 전달할 포트다.

```yaml
nodePort: 30080
```

외부에서 접근할 때 사용할 Node의 포트다.

---

## port, targetPort, nodePort 차이

NodePort에서 제일 헷갈리는 게 이 세 개다.

```text
nodePort
= 외부 사용자가 Node로 들어올 때 사용하는 포트

port
= Service 자체의 포트

targetPort
= 실제 Pod 컨테이너의 포트
```

흐름으로 보면 더 쉽다.

```text
외부 사용자
  ↓
NodeIP:30080
  ↓
Service:8080
  ↓
Pod:8080
```

즉, 위 YAML에서는 이렇게 연결된다.

```text
30080 → 8080 → 8080
```

---

## NodePort 특징 정리

```text
외부에서 접근 가능
Node의 특정 포트를 열어줌
기본 포트 범위는 보통 30000~32767
실습 환경에서 많이 사용
운영 환경에서는 LoadBalancer나 Ingress를 더 많이 사용
```

한 줄로 정리하면 이렇다.

```text
NodePort = 노드에 외부에서 들어올 수 있는 문을 하나 뚫는 방식
```

---

# 6. LoadBalancer

## LoadBalancer란?

LoadBalancer는 클라우드 환경에서 외부 로드밸런서를 생성해주는 Service 타입이다.

```yaml
type: LoadBalancer
```

AWS, GCP, Azure 같은 클라우드 환경에서 LoadBalancer 타입의 Service를 만들면 클라우드 로드밸런서가 생성된다.

외부 사용자는 로드밸런서의 IP나 DNS로 접근한다.

---

## LoadBalancer 구조

```text
외부 사용자
  ↓
Cloud Load Balancer
  ↓
Kubernetes Service
  ↓
Pod
```

NodePort는 사용자가 직접 Node IP와 NodePort를 알아야 한다.

반면 LoadBalancer는 클라우드 로드밸런서가 앞에서 요청을 받아준다.

그래서 운영 환경에서는 NodePort를 직접 노출하기보다 LoadBalancer나 Ingress를 사용하는 경우가 많다.

---

## LoadBalancer 예시 YAML

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
```

이 Service를 만들면 클라우드 환경에서는 외부 IP가 할당될 수 있다.

확인은 이렇게 한다.

```bash
kubectl get service
```

예시 출력은 이런 느낌이다.

```text
NAME            TYPE           CLUSTER-IP      EXTERNAL-IP      PORT(S)
nginx-service   LoadBalancer   10.96.120.10    1.2.3.4          80:31234/TCP
```

여기서 `EXTERNAL-IP`가 외부에서 접근할 수 있는 주소다.

---

## LoadBalancer 특징 정리

```text
클라우드 로드밸런서를 생성
외부 IP 또는 DNS를 통해 접근
운영 환경에서 외부 트래픽을 받을 때 사용
AWS, GCP, Azure 같은 클라우드 환경과 연결됨
```

한 줄로 정리하면 이렇다.

```text
LoadBalancer = 클라우드 로드밸런서를 붙여서 외부에 공개하는 방식
```

---

# 7. 세 가지 Service 비교

| 타입           | 접근 범위        | 주 사용 목적       |
| ------------ | ------------ | ------------- |
| ClusterIP    | 클러스터 내부      | Pod 간 내부 통신   |
| NodePort     | 외부 → Node 포트 | 실습, 간단한 외부 노출 |
| LoadBalancer | 외부 → 클라우드 LB | 운영 환경 외부 공개   |

조금 더 쉽게 표현하면 이렇다.

```text
ClusterIP
= 내부 직원들끼리 쓰는 사내 전화번호

NodePort
= 건물 외벽에 임시 출입문 하나 뚫기

LoadBalancer
= 정식 안내 데스크와 정문 만들기
```

---

# 8. 요청 흐름으로 다시 보기

## ClusterIP

```text
클러스터 내부 Pod
  ↓
ClusterIP Service
  ↓
Pod
```

외부에서는 접근하지 못한다.

---

## NodePort

```text
외부 사용자
  ↓
NodeIP:30080
  ↓
NodePort Service
  ↓
Pod
```

Node의 포트를 통해 외부 접근이 가능하다.

---

## LoadBalancer

```text
외부 사용자
  ↓
Cloud Load Balancer
  ↓
Service
  ↓
Pod
```

클라우드 로드밸런서가 앞에서 요청을 받아준다.

---

# 9. CKA 실습에서 자주 나오는 감각

CKA나 KodeKloud 문제에서는 Service YAML을 직접 작성하라는 문제가 자주 나온다.

예를 들어 이런 문제다.

```text
Create a new service to access the web application.

Name: webapp-service
Type: NodePort
targetPort: 8080
port: 8080
nodePort: 30080
selector:
  name: simple-webapp
```

그러면 YAML은 이렇게 작성하면 된다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: webapp-service
spec:
  type: NodePort
  selector:
    name: simple-webapp
  ports:
  - port: 8080
    targetPort: 8080
    nodePort: 30080
```

여기서 중요한 건 Service가 Pod를 직접 이름으로 찾는 게 아니라는 점이다.

Service는 Pod 이름을 보는 게 아니라 **label**을 본다.

```yaml
selector:
  name: simple-webapp
```

이 selector와 Pod의 label이 맞아야 연결된다.

Pod에 이런 label이 있어야 한다.

```yaml
metadata:
  labels:
    name: simple-webapp
```

만약 selector와 label이 다르면 Service는 Pod를 찾지 못한다.

그 결과 endpoint가 비어 있을 수 있다.

```bash
kubectl get endpoints
```

이 명령어로 Service가 실제로 어떤 Pod와 연결되어 있는지 확인할 수 있다.

---

# 10. 정리

Kubernetes Service는 Pod 앞에 세우는 고정된 접근 지점이다.

Pod는 죽고 다시 만들어질 수 있고, IP도 바뀔 수 있다.
그래서 클라이언트가 Pod를 직접 바라보면 안정적이지 않다.

Service는 이 문제를 해결한다.

```text
Pod는 바뀌어도
Service는 고정된 입구 역할을 한다
```

Service 종류는 대표적으로 세 가지가 있다.

```text
ClusterIP
= 클러스터 내부 통신용

NodePort
= Node의 포트를 열어서 외부 접근 허용

LoadBalancer
= 클라우드 로드밸런서를 붙여서 외부 공개
```

최종적으로 이렇게 기억하면 된다.

```text
ClusterIP는 내부용

NodePort는 노드 포트로 외부 노출

LoadBalancer는 클라우드 로드밸런서로 외부 노출
```

쿠버네티스 네트워크를 이해할 때 Service는 정말 중요한 개념이다.
Pod가 실제 일하는 애라면, Service는 그 Pod들을 찾아갈 수 있게 해주는 안정적인 입구라고 보면 된다.
