---
title: "[K3D/KUBERNETES] LoadBalancer Service를 쓰려면 왜 클러스터 생성 때 포트 매핑을 해야 할까?"
source: "https://velog.io/@yorange50/K3DKUBERNETES-LoadBalancer-Service를-쓰려면-왜-클러스터-생성-때-포트-매핑을-해야-할까"
published: "2026-05-19T05:43:52.434Z"
tags: ""
backup_date: "2026-05-29T14:52:52.724180"
---

Kubernetes에서 Service 타입 중 `LoadBalancer`를 만들면 외부에서 바로 접속할 수 있을 것처럼 느껴진다.

예를 들어 이런 Service YAML이 있다고 하자.

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

적용하면:

```sh
kubectl apply -f loabalancer-svc.yaml
```

Service는 생성된다.

```sh
kubectl get svc nginx-svc
```

그런데 k3d 환경에서는 `EXTERNAL-IP`가 `<pending>`으로 보이거나, `curl localhost`가 안 될 수 있다.

처음에는 이런 생각이 든다.

> LoadBalancer Service를 만들었는데 왜 외부 접속이 안 되지?
> Endpoints도 잡혔는데 왜 localhost로 안 들어가지?
> NodePort처럼 로드밸런싱은 되는 거 아닌가?

결론부터 말하면, **Service 내부 로드밸런싱은 된다.**
하지만 **Mac에서 k3d 클러스터 안으로 들어가는 입구가 없으면 외부 접속은 안 된다.**

이 입구를 만들어주는 것이 k3d의 포트 매핑이다.

---

## 1. LoadBalancer Service는 무엇을 하는가?

LoadBalancer Service는 외부 트래픽을 받아서 Service 뒤의 Pod들로 전달하는 Service 타입이다.

일반적인 클라우드 환경에서는 LoadBalancer Service를 만들면 클라우드 로드밸런서가 자동으로 붙는다.

예를 들어 AWS EKS라면 이런 구조가 된다.

```text
외부 사용자
    ↓
AWS Load Balancer
    ↓
Kubernetes LoadBalancer Service
    ↓
Pod 1 / Pod 2 / Pod 3
```

즉, Service 앞에 실제 외부 로드밸런서가 생기고, 사용자는 그 외부 주소로 접근한다.

그래서 AWS 같은 환경에서는 `kubectl get svc` 했을 때 `EXTERNAL-IP`나 외부 DNS가 잡힐 수 있다.

```text
NAME        TYPE           CLUSTER-IP      EXTERNAL-IP
nginx-svc   LoadBalancer   10.43.x.x       abc.elb.amazonaws.com
```

하지만 k3d는 AWS가 아니다.

---

## 2. k3d는 진짜 클라우드 LoadBalancer를 만들어주지 않는다

k3d는 로컬에서 Kubernetes를 쉽게 띄우기 위한 도구다.

중요한 점은 k3d의 Kubernetes Node가 실제 VM이 아니라 Docker 컨테이너라는 것이다.

구조는 대략 이렇다.

```text
Mac
 |
Docker Desktop
 |
Docker network
 |
k3d server container
k3d agent container
k3d loadbalancer container
```

즉, k3d 안의 Kubernetes 클러스터는 Mac 안에서 직접 돌고 있는 것처럼 보이지만, 실제로는 Docker 내부 네트워크 안에 있다.

그래서 LoadBalancer Service를 만들었다고 해서 Mac의 `localhost:80`으로 자동 연결되는 것이 아니다.

Mac에서 k3d 내부로 들어가려면 Docker/k3d 레벨에서 포트를 열어줘야 한다.

---

## 3. Endpoints가 잡혔다는 것은 내부 연결이 정상이라는 뜻

Service를 describe 했을 때 이런 줄이 나올 수 있다.

```text
Endpoints: 10.42.1.8:80,10.42.2.7:80,10.42.0.8:80
```

이건 아주 중요한 정보다.

해석하면:

```text
nginx-svc Service
    ↓
10.42.1.8:80
10.42.2.7:80
10.42.0.8:80
```

즉, `nginx-svc`가 nginx Pod 3개를 정상적으로 찾고 있다는 뜻이다.

이 상태는 Service 입장에서 정상이다.

```text
Service 생성됨
selector가 Pod를 찾음
Endpoints에 Pod IP 3개 잡힘
Service 내부 로드밸런싱 대상 존재
```

즉, 여기까지는 성공이다.

하지만 이것만으로 Mac에서 바로 접속할 수 있다는 뜻은 아니다.

---

## 4. 내부 로드밸런싱과 외부 접속은 다르다

여기서 헷갈리기 쉬운 부분이 있다.

LoadBalancer Service가 Pod 3개를 바라보고 있으면 로드밸런싱 대상은 잡힌 것이다.

하지만 외부에서 그 Service까지 들어오는 길이 없으면 접속이 안 된다.

구조를 나눠보면 이렇다.

```text
[Service 내부]
nginx-svc
  ↓
Pod 1 / Pod 2 / Pod 3
```

이 부분은 Endpoints로 확인할 수 있다.

반면 외부 접속은 이 부분이다.

```text
[외부 접속]
Mac localhost:80
  ↓
k3d 내부
  ↓
nginx-svc
```

여기서 `Mac localhost:80 → k3d 내부`로 들어가는 문이 없으면, Service가 아무리 정상이어도 외부에서는 접근할 수 없다.

---

## 5. 그래서 k3d에서는 클러스터 생성 때 포트 매핑이 필요하다

k3d에서 LoadBalancer Service를 Mac에서 확인하고 싶다면, 클러스터를 만들 때 포트 매핑을 해줘야 한다.

예를 들어 LoadBalancer Service가 80번 포트를 사용한다면 클러스터 생성 시 이렇게 만든다.

```sh
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "80:80@loadbalancer"
```

여기서 핵심은 이 부분이다.

```sh
--port "80:80@loadbalancer"
```

이건 이렇게 읽으면 된다.

```text
Mac의 80번 포트로 들어온 요청을
k3d loadbalancer 컨테이너의 80번 포트로 보내라
```

즉, 외부에서 들어오는 입구를 미리 열어주는 것이다.

전체 흐름은 이렇게 된다.

```text
Mac
curl localhost:80
      ↓
k3d loadbalancer container:80
      ↓
nginx-svc LoadBalancer Service:80
      ↓
nginx Pod:80
```

그래서 클러스터를 이렇게 만든 뒤 LoadBalancer Service를 적용하면:

```sh
kubectl apply -f loabalancer-svc.yaml
```

Mac에서 이렇게 확인할 수 있다.

```sh
curl http://localhost
```

---

## 6. 포트 매핑을 안 하면 어떻게 될까?

클러스터 생성할 때 포트 매핑을 하나도 안 했다면 이런 상태다.

```text
Mac localhost:80
      ↓
들어갈 문 없음
      ↓
k3d 내부로 전달되지 않음
```

Service 자체는 정상일 수 있다.

```text
nginx-svc LoadBalancer 생성됨
Endpoints 정상
Pod 3개 연결됨
```

하지만 Mac에서:

```sh
curl http://localhost
```

를 하면 안 될 수 있다.

이건 LoadBalancer Service가 Pod를 못 찾는 문제가 아니다.

문제는 더 앞단이다.

```text
Mac에서 k3d 내부로 들어가는 포트가 열려 있지 않음
```

즉, Service 내부 로드밸런싱 문제와 외부 접속 문제를 분리해서 봐야 한다.

---

## 7. NodePort와 비교하면 이해가 쉽다

NodePort도 비슷한 문제가 있었다.

NodePort Service를 만들면 Kubernetes 내부에서는 Node의 특정 포트를 연다.

예를 들어:

```text
nginx-svc   NodePort   10.43.188.207   80:30001/TCP
```

이 뜻은:

```text
Service 80번 포트를
NodePort 30001번으로 외부에 노출
```

이다.

일반 VM 환경이라면 이렇게 접근할 수 있다.

```sh
curl http://<Node-IP>:30001
```

하지만 k3d에서는 Node가 실제 VM이 아니라 Docker 컨테이너다.

그래서 Mac에서 k3d Node IP로 바로 접근이 안 될 수 있다.

이때도 클러스터 생성 시 포트 매핑을 해줘야 한다.

```sh
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "30001:30001@loadbalancer"
```

그러면 Mac에서 이렇게 접근할 수 있다.

```sh
curl http://localhost:30001
```

즉, NodePort든 LoadBalancer든 k3d에서는 결국 외부에서 들어오는 통로를 열어줘야 한다.

---

## 8. LoadBalancer와 NodePort의 공통점

LoadBalancer와 NodePort는 모두 Service다.

둘 다 selector로 Pod를 찾고, Endpoints에 잡힌 Pod들로 요청을 보낸다.

```yaml
selector:
  app: nginx
```

이 selector가 `app=nginx` 라벨을 가진 Pod를 찾는다.

그래서 Endpoints에 이런 식으로 잡힌다.

```text
Endpoints: 10.42.1.8:80,10.42.2.7:80,10.42.0.8:80
```

즉 둘 다 최종 목적지는 같다.

```text
Service
  ↓
Endpoints
  ↓
Pod 1 / Pod 2 / Pod 3
```

공통점은 이것이다.

```text
Service 뒤의 Pod들로 트래픽을 분산한다
```

---

## 9. LoadBalancer와 NodePort의 차이점

차이는 외부에서 들어오는 입구다.

NodePort는 Node의 포트를 통해 들어온다.

```text
외부 요청
  ↓
NodeIP:NodePort
  ↓
NodePort Service
  ↓
Pod
```

LoadBalancer는 원래 외부 로드밸런서를 통해 들어온다.

```text
외부 요청
  ↓
External LoadBalancer IP
  ↓
LoadBalancer Service
  ↓
Pod
```

AWS라면 외부 로드밸런서가 실제로 생긴다.

하지만 k3d에서는 실제 AWS LoadBalancer가 생기지 않는다.

그래서 k3d의 loadbalancer 컨테이너와 포트 매핑을 이용해서 비슷한 흐름을 만들어준다.

```text
Mac localhost:80
  ↓
k3d loadbalancer container:80
  ↓
LoadBalancer Service
  ↓
Pod
```

---

## 10. k3d 포트 매핑의 앞쪽 포트와 뒤쪽 포트

k3d 포트 매핑은 이런 형식이다.

```sh
--port "80:80@loadbalancer"
```

포트가 두 개 나오면 이렇게 보면 된다.

```text
앞쪽 포트 : 뒤쪽 포트

앞쪽 포트 = Mac에서 접속할 포트
뒤쪽 포트 = k3d loadbalancer 컨테이너 안으로 넘길 포트
```

즉:

```sh
--port "80:80@loadbalancer"
```

은:

```text
Mac localhost:80
    ↓
k3d loadbalancer:80
```

이라는 뜻이다.

만약 이렇게 쓰면:

```sh
--port "8080:80@loadbalancer"
```

뜻은:

```text
Mac localhost:8080
    ↓
k3d loadbalancer:80
```

이 된다.

그러면 접속은 이렇게 해야 한다.

```sh
curl http://localhost:8080
```

앞쪽 포트가 내가 접속하는 포트이기 때문이다.

---

## 11. 포트 매핑을 하고 클러스터를 만든 뒤 확인하는 흐름

LoadBalancer Service를 k3d에서 외부 접속까지 확인하고 싶다면 흐름은 이렇다.

먼저 클러스터를 만들 때 80번 포트를 연다.

```sh
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "80:80@loadbalancer"
```

nginx Deployment를 만든다.

```sh
kubectl create deployment nginx-deployment \
  --image=nginx \
  --replicas=3
```

LoadBalancer Service를 적용한다.

```sh
kubectl apply -f loabalancer-svc.yaml
```

Service를 확인한다.

```sh
kubectl get svc nginx-svc
```

상세 정보도 확인한다.

```sh
kubectl describe svc nginx-svc
```

Endpoints가 잡혔는지 본다.

```text
Endpoints: 10.42.1.8:80,10.42.2.7:80,10.42.0.8:80
```

마지막으로 Mac에서 접속한다.

```sh
curl http://localhost
```

nginx 응답이 나오면 성공이다.

---

## 12. 이미 포트 매핑 없이 클러스터를 만들었다면?

이미 클러스터를 만들었는데 포트 매핑을 안 했다면, Mac에서 바로 `localhost:80`으로 접근하기 어렵다.

이때 방법은 두 가지다.

첫 번째는 클러스터를 다시 만드는 것이다.

```sh
k3d cluster delete my-cluster
```

```sh
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "80:80@loadbalancer"
```

두 번째는 임시 확인용으로 `kubectl port-forward`를 쓰는 것이다.

```sh
kubectl port-forward svc/nginx-svc 8080:80
```

그리고 다른 터미널에서:

```sh
curl http://localhost:8080
```

단, 이건 k3d 포트 매핑과는 다르다.

```text
k3d --port
= 클러스터 생성 시 Docker/k3d 레벨에서 포트를 열어둠

kubectl port-forward
= kubectl이 임시로 로컬 포트와 Service 포트를 연결함
```

`kubectl port-forward`는 명령어가 실행 중일 때만 유지된다.

---

## 13. 정리

k3d에서 LoadBalancer Service를 사용할 때 포트 매핑이 필요한 이유는 단순하다.

LoadBalancer Service가 Pod를 정상적으로 찾고 있어도, Mac에서 k3d 내부로 들어가는 통로가 없으면 외부 접속이 안 되기 때문이다.

정리하면:

```text
LoadBalancer Service 생성
→ Service 내부에서는 Pod 3개를 Endpoints로 잡음
→ 내부 로드밸런싱 대상은 정상

하지만 k3d는 Docker 내부 네트워크에서 동작
→ Mac localhost에서 k3d 내부로 자동 연결되지 않음
→ 클러스터 생성 시 --port로 입구를 열어야 함
```

LoadBalancer Service 확인에서 중요한 것은 두 단계다.

```text
1. Service가 Pod를 잘 찾는가?
   → kubectl describe svc nginx-svc
   → Endpoints 확인

2. 외부에서 Service까지 들어오는 입구가 있는가?
   → k3d cluster create 시 --port "80:80@loadbalancer" 필요
```

한 문장으로 정리하면 다음과 같다.

```text
k3d에서 LoadBalancer Service를 외부에서 확인하려면, Service 자체뿐 아니라 Mac에서 k3d loadbalancer 컨테이너로 들어가는 포트 매핑이 필요하다.
```
