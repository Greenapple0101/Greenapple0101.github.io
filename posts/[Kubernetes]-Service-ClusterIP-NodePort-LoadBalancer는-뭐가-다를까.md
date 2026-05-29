---
title: "[Kubernetes] Service, ClusterIP, NodePort, LoadBalancer는 뭐가 다를까?"
source: "https://velog.io/@yorange50/Kubernetes-Service-ClusterIP-NodePort-LoadBalancer는-뭐가-다를까"
published: "2026-05-06T07:04:46.575Z"
tags: ""
backup_date: "2026-05-29T14:52:52.775108"
---

쿠버네티스를 처음 공부하면 `Pod`, `Service`, `ClusterIP`, `NodePort`, `LoadBalancer` 같은 단어가 계속 나온다. 처음에는 전부 네트워크 관련 용어처럼 보여서 헷갈리는데, 핵심은 하나다.

**Pod는 계속 바뀔 수 있고, Service는 그 앞에 고정된 주소를 만들어준다.**

---

## Pod에 직접 접근하면 안 되는 이유

쿠버네티스에서 실제 애플리케이션은 `Pod` 안에서 실행된다.

예를 들어 게시판 API 서버가 있다고 하면, 이 API 서버는 어떤 Pod 안에서 실행된다.

```text
board-api Pod
```

그런데 Pod는 영구적인 존재가 아니다.

배포가 새로 일어나거나, 장애가 나거나, 스케일 아웃이 일어나면 Pod는 삭제되고 다시 생성될 수 있다.

문제는 이때 **Pod의 IP도 바뀔 수 있다**는 점이다.

```text
기존 Pod IP: 10.1.1.3
새로운 Pod IP: 10.1.2.7
```

만약 다른 애플리케이션이 기존 Pod IP인 `10.1.1.3`으로 직접 접근하고 있었다면, Pod가 새로 만들어지는 순간 통신이 깨질 수 있다.

그래서 쿠버네티스에서는 Pod에 직접 접근하기보다, 그 앞에 **Service**를 둔다.

---

## Service란?

Service는 바뀌는 Pod들 앞에 고정된 네트워크 주소를 제공하는 쿠버네티스 리소스다.

```text
Service
= 바뀌는 Pod들 앞에 고정된 진입점을 제공하는 것
```

Pod는 죽었다가 다시 살아날 수 있고, IP도 바뀔 수 있다.

하지만 Service는 고정된 이름과 주소를 제공한다.

```text
Client
→ Service
→ Pod
```

즉, 사용자는 Pod가 어디 있는지 직접 몰라도 된다.

Service가 현재 살아 있는 Pod를 찾아서 연결해준다.

---

## Service는 Pod를 어떻게 찾을까?

Service는 보통 `selector`를 이용해서 Pod를 찾는다.

예를 들어 Pod에 이런 라벨이 붙어 있다고 하자.

```yaml
labels:
  app: board-api
```

그리고 Service가 이 라벨을 바라보게 만든다.

```yaml
selector:
  app: board-api
```

그러면 Service는 `app=board-api` 라벨이 붙은 Pod들을 찾아서 트래픽을 전달한다.

```text
Service selector: app=board-api
        ↓
Pod A: app=board-api
Pod B: app=board-api
Pod C: app=board-api
```

그래서 Pod가 여러 개여도 Service 하나로 묶을 수 있다.

---

## Service 타입 3가지

쿠버네티스 Service에는 여러 타입이 있는데, 입문 단계에서는 아래 세 가지를 먼저 이해하면 된다.

```text
ClusterIP
NodePort
LoadBalancer
```

각각 “어디에서 접근할 수 있냐”가 다르다.

---

# 1. ClusterIP

ClusterIP는 쿠버네티스 Service의 기본 타입이다.

```text
ClusterIP
= 클러스터 내부 통신용 Service
```

외부에서는 접근할 수 없고, 쿠버네티스 클러스터 내부에서만 접근할 수 있다.

예를 들어 `backend` Pod가 `database` Pod와 통신해야 한다고 해보자.

이때 backend가 database Pod IP에 직접 접근하지 않고, database Service 이름으로 접근한다.

```text
backend Pod
→ database Service
→ database Pod
```

예시로는 이런 상황이다.

```text
board-api
→ board-db Service
→ PostgreSQL Pod
```

즉, ClusterIP는 내부 서비스끼리 통신할 때 사용한다.

---

## ClusterIP 예시

```yaml
apiVersion: v1
kind: Service
metadata:
  name: board-api-service
spec:
  type: ClusterIP
  selector:
    app: board-api
  ports:
    - port: 80
      targetPort: 8080
```

여기서 중요한 부분은 이거다.

```yaml
type: ClusterIP
```

그리고 포트는 이렇게 이해하면 된다.

```text
port: Service가 받는 포트
targetPort: Pod 안의 컨테이너가 실제로 열고 있는 포트
```

즉,

```text
Service의 80번 포트로 들어오면
Pod의 8080번 포트로 전달한다
```

---

# 2. NodePort

NodePort는 외부에서 접근할 수 있도록 각 Node의 특정 포트를 열어주는 Service 타입이다.

```text
NodePort
= 외부에서 Node IP와 Port로 접근하는 Service
```

접근 방식은 이렇게 생겼다.

```text
NodeIP:NodePort
```

예를 들어 Node IP가 `13.125.10.20`이고, NodePort가 `30080`이면 외부에서 이렇게 접근한다.

```text
http://13.125.10.20:30080
```

그러면 흐름은 이렇게 된다.

```text
외부 사용자
→ NodeIP:NodePort
→ Service
→ Pod
```

---

## NodePort 예시

```yaml
apiVersion: v1
kind: Service
metadata:
  name: board-api-service
spec:
  type: NodePort
  selector:
    app: board-api
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080
```

여기서 중요한 부분은 이거다.

```yaml
type: NodePort
```

그리고 `nodePort`는 외부에서 접근할 때 사용하는 포트다.

```text
nodePort: 30080
```

즉,

```text
외부에서 NodeIP:30080으로 접근
→ Service의 80번 포트
→ Pod의 8080번 포트
```

---

## NodePort는 언제 사용할까?

NodePort는 보통 실습이나 테스트 환경에서 많이 사용한다.

왜냐하면 외부에서 바로 접근할 수 있어서 편하다.

하지만 운영 환경에서는 Node IP와 포트를 직접 관리해야 하기 때문에 불편하다.

그래서 실제 운영에서는 보통 `LoadBalancer`나 `Ingress`를 더 많이 사용한다.

---

# 3. LoadBalancer

LoadBalancer는 클라우드 환경에서 외부 로드밸런서를 자동으로 생성해 붙이는 Service 타입이다.

```text
LoadBalancer
= 클라우드 로드밸런서를 붙이는 Service
```

AWS, GCP, Azure 같은 클라우드 환경에서 사용하면, 외부에서 접근 가능한 Load Balancer가 생성된다.

흐름은 이렇게 된다.

```text
외부 사용자
→ Cloud Load Balancer
→ Service
→ Pod
```

예를 들어 AWS EKS에서 `type: LoadBalancer`를 사용하면, AWS의 ELB 같은 로드밸런서가 생성될 수 있다.

사용자는 Node IP나 NodePort를 직접 몰라도 된다.

그냥 LoadBalancer 주소로 접근하면 된다.

---

## LoadBalancer 예시

```yaml
apiVersion: v1
kind: Service
metadata:
  name: board-api-service
spec:
  type: LoadBalancer
  selector:
    app: board-api
  ports:
    - port: 80
      targetPort: 8080
```

여기서 중요한 부분은 이거다.

```yaml
type: LoadBalancer
```

그러면 클라우드 환경에서는 외부 IP 또는 DNS가 붙는다.

```text
외부 사용자
→ LoadBalancer 주소
→ Service
→ Pod
```

---

# ClusterIP, NodePort, LoadBalancer 비교

| 타입           | 접근 범위   | 사용 목적                |
| ------------ | ------- | -------------------- |
| ClusterIP    | 클러스터 내부 | Pod끼리 내부 통신          |
| NodePort     | 클러스터 외부 | Node IP와 Port로 외부 접근 |
| LoadBalancer | 클러스터 외부 | 클라우드 로드밸런서를 통한 외부 접근 |

정리하면 이렇게 볼 수 있다.

```text
ClusterIP
= 내부용

NodePort
= 외부에서 NodeIP:Port로 접근

LoadBalancer
= 클라우드 로드밸런서로 외부 공개
```

---

# 전체 흐름으로 이해하기

내부 통신은 보통 이렇게 된다.

```text
backend Pod
→ ClusterIP Service
→ database Pod
```

외부에서 테스트용으로 접근할 때는 이렇게 된다.

```text
외부 사용자
→ NodeIP:NodePort
→ Service
→ Pod
```

클라우드 운영 환경에서는 보통 이렇게 된다.

```text
외부 사용자
→ LoadBalancer
→ Service
→ Pod
```

---

# 비유로 이해하기

Pod를 직원이라고 생각해보자.

직원들은 자리가 바뀔 수 있다.

오늘은 3층에 있다가 내일은 5층에 있을 수도 있다.

그런데 외부 사람이 특정 직원의 자리 번호를 외워서 찾아가면, 자리가 바뀌는 순간 찾을 수 없다.

그래서 회사 대표번호가 필요하다.

```text
Pod
= 자리 바뀌는 직원

Service
= 회사 대표번호

ClusterIP
= 사내 전화번호

NodePort
= 건물 외부에서 특정 내선번호로 바로 전화

LoadBalancer
= 안내 데스크가 알아서 담당자에게 연결
```

즉, Service는 바뀌는 Pod들 앞에 있는 안정적인 진입점이다.

---

# 핵심 정리

쿠버네티스에서 Pod는 계속 바뀔 수 있다.

Pod가 새로 생성되면 IP도 바뀔 수 있다.

그래서 Pod IP에 직접 접근하면 위험하다.

이 문제를 해결하기 위해 Service를 사용한다.

Service는 바뀌는 Pod들 앞에 고정된 네트워크 주소를 제공한다.

그중 ClusterIP는 클러스터 내부 통신용이고, NodePort는 외부에서 Node IP와 Port로 접근할 수 있게 해주고, LoadBalancer는 클라우드 로드밸런서를 붙여 외부 접근을 가능하게 한다.

마지막으로 이렇게 외우면 된다.

```text
Pod는 불안정하다.
Service는 안정적인 접근 지점이다.

ClusterIP는 내부용이다.
NodePort는 외부 테스트용이다.
LoadBalancer는 클라우드 외부 공개용이다.
```
