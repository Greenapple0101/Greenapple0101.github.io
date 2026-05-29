---
title: "[KUBERNETES] Service는 왜 필요할까? ClusterIP, NodePort, LoadBalancer 한 번에 이해하기"
source: "https://velog.io/@yorange50/KUBERNETES-Service는-왜-필요할까-ClusterIP-NodePort-LoadBalancer-한-번에-이해하기"
published: "2026-05-18T09:13:26.646Z"
tags: ""
backup_date: "2026-05-29T14:52:52.728504"
---

쿠버네티스에서 Pod를 띄우는 것까지는 비교적 이해가 쉽다. `nginx` 이미지를 이용해서 Pod를 만들면 nginx 서버가 뜨고, Deployment를 만들면 여러 개의 Pod가 생성된다. 그런데 여기서 바로 문제가 생긴다. Pod는 계속 같은 자리에 있는 존재가 아니다. 죽었다가 다시 만들어질 수 있고, 새 버전으로 배포되면서 기존 Pod가 사라지고 새 Pod가 생길 수도 있다. 그러면 IP도 바뀐다. 그래서 클라이언트가 특정 Pod IP를 직접 바라보는 방식은 운영 환경에서 위험하다. 이 문제를 해결하기 위해 등장하는 리소스가 바로 **Service**다. Service는 여러 Pod 앞에 붙어서, Pod들을 하나의 안정적인 접속 지점으로 묶어주는 역할을 한다. 강의 메모에서도 Service의 가장 중요한 목적을 “로드밸런싱”이라고 정리했고, Service가 Pod를 직접 IP로 찾는 것이 아니라 **label selector**를 기준으로 바라본다는 점이 핵심으로 나온다. 

---

## Service를 이해하려면 먼저 Pod의 특성을 알아야 한다

쿠버네티스에서 Pod는 언제든지 새로 만들어질 수 있다. 예를 들어 Deployment가 `nginx` Pod 3개를 관리하고 있다고 해보자.

```text
nginx-pod-1
nginx-pod-2
nginx-pod-3
```

이 Pod들은 각각 IP를 가진다.

```text
10.42.1.17
10.42.2.20
10.42.2.21
```

그런데 장애가 나거나, 롤링 업데이트가 일어나거나, 노드 상태가 바뀌면 Pod가 죽고 새 Pod가 만들어질 수 있다. 그러면 기존 IP는 더 이상 유효하지 않다.

```text
기존 Pod 삭제
새 Pod 생성
새 IP 할당
```

즉, Pod IP를 직접 바라보는 구조는 불안정하다. 그래서 Service가 필요하다.

Service는 이런 식으로 동작한다.

```text
사용자 또는 다른 Pod
        ↓
     Service
        ↓
  label selector
        ↓
 nginx Pod들
```

Service는 Pod의 IP를 하나하나 외워서 연결하는 것이 아니라, Pod에 붙은 label을 보고 연결한다.

예를 들어 Service가 이렇게 되어 있다면:

```yaml
selector:
  app: nginx
```

Service는 현재 클러스터 안에서 `app=nginx` 라벨을 가진 Pod들을 찾아서 트래픽을 분산한다.

---

## Service의 핵심은 selector다

Service YAML을 보면 가장 중요한 부분은 `selector`다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-svc
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: ClusterIP
```

여기서 의미는 이렇다.

```text
selector:
  app: nginx
```

`app=nginx` 라벨이 붙은 Pod들을 Service 대상으로 삼겠다는 뜻이다.

```text
port: 80
```

Service가 받을 포트다.

```text
targetPort: 80
```

Service가 실제 Pod 내부 컨테이너로 전달할 포트다.

```text
type: ClusterIP
```

Service 타입은 ClusterIP로 만들겠다는 뜻이다.

정리하면:

```text
Service의 80번 포트로 요청이 들어오면
app=nginx 라벨을 가진 Pod들의 80번 포트로 전달한다
```

강의 실습 파일에서도 `nginx-svc`라는 Service를 만들고, selector로 `app: nginx`를 지정한 뒤, `port: 80`, `targetPort: 80`, `type: ClusterIP`를 사용하는 예제가 나온다. 

---

## ClusterIP란 무엇인가?

ClusterIP는 Service의 기본 타입이다. 따로 타입을 지정하지 않으면 기본적으로 ClusterIP가 된다.

ClusterIP는 말 그대로 **클러스터 내부에서만 접근 가능한 IP**를 만들어준다.

```text
Cluster 내부 Pod
        ↓
   ClusterIP Service
        ↓
      nginx Pod
```

예를 들어 Service를 만들고 나서 `kubectl get svc`를 하면 이런 식으로 가상의 IP가 생긴다.

```text
NAME        TYPE        CLUSTER-IP      PORT(S)
nginx-svc   ClusterIP   10.43.144.200   80/TCP
```

이 IP는 Pod IP가 아니다. Service가 가진 가상의 IP다.

그래서 클러스터 내부에서는 다음처럼 접근할 수 있다.

```bash
curl http://10.43.144.200
```

하지만 이건 클러스터 내부에서만 된다. 내 노트북 브라우저에서 바로 `10.43.144.200`을 치면 접속되지 않는다. 이 IP는 Kubernetes 클러스터 안에서만 의미가 있기 때문이다.

실습 파일에서도 ClusterIP Service를 만들고, master 노드에서 ClusterIP로 curl을 날려 nginx 응답을 확인하는 흐름이 정리되어 있다. 

---

## ClusterIP 로드밸런싱 확인하기

Service가 정말 여러 Pod로 트래픽을 나눠주는지 확인하려면 각 nginx Pod의 `index.html` 내용을 다르게 바꾸면 된다.

예를 들어 Pod 3개에 각각 들어가서 다음처럼 설정한다.

```bash
echo nginx-1 > /usr/share/nginx/html/index.html
echo nginx-2 > /usr/share/nginx/html/index.html
echo nginx-3 > /usr/share/nginx/html/index.html
```

그리고 Service IP로 여러 번 요청을 날린다.

```bash
for i in {1..1000}
do
  curl http://10.43.144.200
  echo " (${i})"
  sleep 1
done
```

그러면 응답이 이런 식으로 번갈아 나올 수 있다.

```text
nginx-1
nginx-2
nginx-3
nginx-1
nginx-3
...
```

이게 Service가 뒤쪽 Pod들로 트래픽을 분산하고 있다는 뜻이다.

즉, 사용자는 Service 하나만 바라본다.

```text
curl http://Service-IP
```

하지만 실제 요청은 여러 Pod 중 하나로 전달된다.

---

## endpoints는 Service가 바라보는 실제 Pod 목록이다

Service가 어떤 Pod들을 바라보고 있는지 확인하려면 `endpoints`를 보면 된다.

```bash
kubectl get endpoints
```

또는 줄여서:

```bash
kubectl get ep
```

예시:

```text
NAME        ENDPOINTS
nginx-svc   10.42.1.17:80,10.42.2.20:80,10.42.2.21:80
```

여기 나오는 IP들이 실제 Pod IP다.

즉, 구조는 이렇다.

```text
Service IP
10.43.144.200
        ↓
Endpoints
10.42.1.17:80
10.42.2.20:80
10.42.2.21:80
```

사용자는 Service IP만 바라보지만, Service는 내부적으로 endpoint 목록을 보고 실제 Pod로 트래픽을 보낸다.

강의 메모에서도 `kubectl get endpoints`를 통해 `nginx-svc`가 여러 Pod IP를 endpoint로 가지고 있는 것을 확인하는 내용이 나온다. 

---

## NodePort란 무엇인가?

ClusterIP는 내부 통신용이다. 그런데 외부에서 접속하고 싶으면 어떻게 해야 할까?

그때 사용하는 Service 타입 중 하나가 **NodePort**다.

NodePort는 모든 노드의 특정 포트를 외부에 열어준다.

```text
외부 사용자
    ↓
Node IP:30001
    ↓
NodePort Service
    ↓
Pod
```

예를 들어 NodePort Service YAML은 이렇게 생겼다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-svc
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      nodePort: 30001
      port: 80
      targetPort: 80
  type: NodePort
```

여기서 중요한 건 `nodePort: 30001`이다.

이제 외부에서 다음처럼 접속할 수 있다.

```bash
curl http://노드IP:30001
```

예를 들어 노드 IP가 `172.26.8.74`라면:

```bash
curl http://172.26.8.74:30001
```

실습 파일에서도 NodePort 타입으로 Service를 만들고, master node, worker node IP에 각각 `:30001`을 붙여 curl 테스트하는 예제가 나온다. 

---

## NodePort의 중요한 특징

NodePort에서 헷갈리기 쉬운 점이 있다.

Pod가 실제로 어떤 노드에 떠 있는지와 상관없이, 아무 노드의 `nodePort`로 요청해도 Service가 알아서 Pod까지 전달할 수 있다.

예를 들어 노드가 3개 있다고 하자.

```text
master-1   172.26.8.74
worker-1   172.26.3.104
worker-2   172.26.9.60
```

Pod가 `worker-2`에 떠 있어도 다음 요청들이 모두 가능할 수 있다.

```bash
curl 172.26.8.74:30001
curl 172.26.3.104:30001
curl 172.26.9.60:30001
```

왜냐하면 NodePort는 각 노드의 특정 포트를 열고, Kubernetes 내부 네트워크를 통해 Service와 Pod로 연결해주기 때문이다.

그래서 NodePort의 장점은 외부에서 클러스터로 들어오는 통로를 만들 수 있다는 것이다.

하지만 단점도 있다. 외부 사용자는 결국 노드 IP를 알아야 한다.

```text
어떤 노드 IP로 접속하지?
그 노드가 죽으면?
새 노드가 추가되면?
방화벽은 열려 있나?
```

이런 문제가 생긴다.

그래서 운영 환경에서는 NodePort만 단독으로 쓰기보다는, 앞단에 LoadBalancer를 두거나 Ingress/Gateway를 같이 사용하는 경우가 많다.

---

## LoadBalancer란 무엇인가?

LoadBalancer 타입은 외부 로드밸런서를 만들어서 Service에 연결하는 방식이다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-svc
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: LoadBalancer
```

LoadBalancer 타입을 사용하면 클라우드 환경에서는 AWS, GCP, Azure 같은 인프라가 외부 로드밸런서를 자동으로 만들어준다.

```text
외부 사용자
    ↓
Cloud Load Balancer
    ↓
Kubernetes Service
    ↓
Pod
```

예를 들어 AWS에서 `type: LoadBalancer`를 만들면 AWS Load Balancer가 생성되고, 외부에서 접근 가능한 주소가 붙는다.

하지만 로컬 Kubernetes나 순수 bare-metal 환경에서는 LoadBalancer를 만들었는데 `EXTERNAL-IP`가 계속 `Pending`으로 남을 수 있다.

```text
NAME        TYPE           EXTERNAL-IP
nginx-svc   LoadBalancer   <pending>
```

왜냐하면 LoadBalancer 타입은 외부 로드밸런서를 만들어줄 인프라 기능이 필요하기 때문이다. 클라우드에서는 이걸 클라우드 컨트롤러가 해주지만, bare-metal에서는 기본적으로 그런 기능이 없다. 그래서 MetalLB 같은 솔루션을 추가로 사용하기도 한다.

강의 파일에서도 LoadBalancer Service를 적용한 뒤 `pending`을 확인하는 흐름이 나온다. 

---

## NodePort와 LoadBalancer의 차이

둘 다 외부 노출에 사용할 수 있다. 하지만 느낌이 다르다.

| 구분       | NodePort           | LoadBalancer      |
| -------- | ------------------ | ----------------- |
| 외부 접근 방식 | 노드 IP + 포트         | 외부 LB IP 또는 DNS   |
| 예시       | `노드IP:30001`       | `LB주소:80`         |
| 장점       | 간단함                | 운영 환경에 적합         |
| 단점       | 노드 IP 관리 필요        | 클라우드/별도 솔루션 필요    |
| 주 사용처    | 실습, 테스트, 간단한 외부 노출 | 운영 환경의 외부 트래픽 진입점 |

NodePort는 이런 느낌이다.

```text
외부에서 직접 노드 문을 두드리는 방식
```

LoadBalancer는 이런 느낌이다.

```text
외부 전용 안내 데스크를 만들고,
그 안내 데스크가 Kubernetes 안으로 연결해주는 방식
```

---

## L4 LoadBalancer와 L7 Ingress의 차이도 알아야 한다

Service의 LoadBalancer는 기본적으로 L4에 가깝게 이해하면 된다.

L4는 TCP/UDP 같은 전송 계층 기준으로 트래픽을 전달한다.

```text
5432 포트로 오면 PostgreSQL로 전달
6379 포트로 오면 Redis로 전달
80 포트로 오면 nginx로 전달
```

이런 식이다.

반면 L7은 HTTP 요청의 내용을 볼 수 있다.

```text
/api 로 오면 backend-service
/static 으로 오면 frontend-service
/admin 으로 오면 admin-service
```

즉, URL path나 host 기반 라우팅을 할 수 있다.

그래서 일반적으로:

```text
DB, Redis, TCP 기반 서비스 → L4 LoadBalancer
HTTP path 기반 웹 라우팅 → Ingress 또는 Gateway API
```

이렇게 이해하면 좋다.

강의 메모에서도 PostgreSQL, Redis처럼 path가 없는 TCP 기반 서비스는 L4 로드밸런싱이 적합하고, HTTP path 기반 분기는 L7에서 가능하다는 설명이 나온다. 

---

## ExternalName이란?

ExternalName은 조금 특이한 Service 타입이다.

일반적인 Service는 selector로 Pod를 찾는다.

```text
Service
  ↓
selector
  ↓
Pod
```

그런데 ExternalName은 Pod를 찾는 게 아니라 외부 도메인으로 연결한다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: externalname1
spec:
  type: ExternalName
  externalName: naver.com
```

이렇게 만들면 클러스터 내부에서 다음 이름으로 접근할 수 있다.

```bash
curl -L externalname1.default.svc.cluster.local
```

그러면 실제로는 `naver.com`으로 연결된다.

즉, ExternalName은 외부 도메인을 Kubernetes Service 이름처럼 감싸는 역할을 한다.

다만 실무에서 아주 자주 쓰는 타입은 아니다. 외부 도메인은 그냥 직접 도메인으로 접근하는 경우도 많기 때문이다.

---

## Service 타입 한 번에 정리

| 타입           | 의미                              | 접근 범위               |
| ------------ | ------------------------------- | ------------------- |
| ClusterIP    | 클러스터 내부용 Service IP 생성          | 클러스터 내부             |
| NodePort     | 모든 노드의 특정 포트를 열어서 외부 노출         | 클러스터 외부 가능          |
| LoadBalancer | 외부 LoadBalancer를 생성해 Service 연결 | 클러스터 외부 가능          |
| ExternalName | 외부 도메인을 Service 이름으로 매핑         | 클러스터 내부에서 외부 도메인 참조 |

시험이나 실습에서는 특히 이 세 가지를 많이 본다.

```text
ClusterIP
NodePort
LoadBalancer
```

---

## 실습 흐름 정리

강의 실습 흐름은 대략 이렇게 볼 수 있다.

### 1. nginx Deployment 배포

```bash
kubectl apply -f deploy.yaml
```

### 2. ClusterIP Service 생성

```bash
kubectl apply -f clusterip-svc.yaml
```

### 3. Service 확인

```bash
kubectl get svc
```

### 4. 클러스터 내부에서 curl 테스트

```bash
curl http://ClusterIP
```

또는 curl 전용 Pod를 띄워서 테스트한다.

```bash
kubectl run curl -it --rm --image curlimages/curl -- sh
```

### 5. endpoints 확인

```bash
kubectl get endpoints
```

또는:

```bash
kubectl get ep
```

### 6. NodePort로 변경

```bash
kubectl apply -f nodeport-svc.yaml
```

### 7. 노드 IP 확인

```bash
kubectl get nodes -o wide
```

### 8. 외부에서 NodePort 접속

```bash
curl http://노드IP:30001
```

### 9. LoadBalancer로 변경

```bash
kubectl apply -f loabalancer-svc.yaml
```

### 10. EXTERNAL-IP 확인

```bash
kubectl get svc
```

실습 파일에서도 이 순서대로 ClusterIP, NodePort, LoadBalancer, ExternalName을 각각 적용하고 테스트하는 명령어가 정리되어 있다. 

---

## Pod, Deployment, Service의 관계

초반에 헷갈리기 쉬운 구조는 이거다.

```text
Deployment
    ↓
ReplicaSet
    ↓
Pod 여러 개
```

Deployment는 Pod를 직접 하나만 띄우는 것이 아니라, ReplicaSet을 통해 원하는 개수만큼 Pod를 유지한다.

그리고 Service는 그 Pod들을 앞에서 묶는다.

```text
Service
    ↓ selector: app=nginx
Pod 1
Pod 2
Pod 3
```

Deployment가 새 버전의 Pod를 만들고 기존 Pod를 죽이더라도, 새 Pod에 같은 label이 붙어 있다면 Service는 계속 그 Pod들을 찾아갈 수 있다.

그래서 Kubernetes에서는 IP보다 label이 중요하다.

```text
Pod IP는 바뀔 수 있다
하지만 label은 의도적으로 유지할 수 있다
Service는 label selector로 Pod를 찾는다
```

이게 Kubernetes Service의 핵심이다.

---

## 롤링 업데이트와 Service

쿠버네티스가 배포에 강한 이유도 Service와 관련이 있다.

기존 방식에서는 서버 몇 대를 로드밸런서에 직접 등록해두고, 배포할 때 서버를 하나씩 빼고 다시 넣는 작업을 해야 했다.

```text
서버 제거
배포
서버 재등록
다음 서버 제거
배포
재등록
```

이 과정에서 트래픽이 줄어들거나, 사람이 직접 개입해야 하거나, 배포 시간이 새벽으로 밀리는 경우가 많았다.

쿠버네티스에서는 Deployment가 새 Pod를 만들고, 준비가 완료되면 기존 Pod를 줄이는 방식으로 롤링 업데이트를 수행한다.

```text
v1 Pod 운영 중
v2 Pod 생성
v2 Pod Ready
Service가 v2 Pod에도 트래픽 전달
v1 Pod 제거
```

Service는 특정 IP가 아니라 label을 보고 Pod를 찾기 때문에, 새 Pod가 Ready 상태가 되면 자연스럽게 트래픽 대상에 포함될 수 있다.

강의 메모에서도 기존 서버 기반 배포와 비교하면서, Kubernetes에서는 새 Pod를 만들고 정상 상태가 되면 기존 Pod를 제거하는 흐름으로 로드밸런싱과 배포 안정성을 확보한다고 설명한다. 

---

## 정리

Service는 Kubernetes에서 Pod를 안정적으로 노출하기 위한 핵심 리소스다. Pod는 언제든지 죽고 다시 만들어질 수 있기 때문에 IP가 고정된 존재가 아니다. 그래서 클라이언트가 Pod IP를 직접 바라보면 운영이 불안정해진다.

Service는 이 문제를 해결한다.

```text
Pod IP를 직접 보지 않고
label selector로 Pod들을 묶고
하나의 안정적인 접속 지점을 제공한다
```

ClusterIP는 클러스터 내부 통신용이다.

```text
클러스터 내부에서만 접근 가능
```

NodePort는 노드의 특정 포트를 열어 외부에서 접근할 수 있게 한다.

```text
노드IP:포트
```

LoadBalancer는 외부 로드밸런서를 통해 Service를 노출한다.

```text
외부 LB → Service → Pod
```

ExternalName은 외부 도메인을 Kubernetes Service 이름처럼 사용할 수 있게 한다.

결국 Service를 한 문장으로 정리하면 이렇다.

> Service는 계속 바뀔 수 있는 Pod들 앞에 고정된 접근 지점을 만들어주고, label selector를 기준으로 트래픽을 분산해주는 Kubernetes 네트워크 리소스다.
