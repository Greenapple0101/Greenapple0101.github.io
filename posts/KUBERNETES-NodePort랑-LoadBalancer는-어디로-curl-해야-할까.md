---
title: "[KUBERNETES] NodePort랑 LoadBalancer는 어디로 curl 해야 할까?"
source: "https://velog.io/@yorange50/KUBERNETES-NodePort랑-LoadBalancer는-어디로-curl-해야-할까"
published: "2026-05-19T06:13:59.847Z"
tags: ""
backup_date: "2026-05-29T14:52:52.723290"
---

Kubernetes Service를 공부하다 보면 `NodePort`와 `LoadBalancer`가 자주 나온다. 그런데 실습을 하다 보면 둘이 너무 비슷해 보인다.

```text
NodePort도 Service 뒤의 Pod로 보내고
LoadBalancer도 Service 뒤의 Pod로 보낸다

그럼 둘이 뭐가 다른 거지?
그리고 curl은 어디로 쳐야 하지?
```

이번 글에서는 **Service 타입이 NodePort일 때와 LoadBalancer일 때 각각 어디로 접속해야 하는지**를 정리해보려고 한다.

---

## 1. 먼저 Service의 공통 구조부터 이해하기

Kubernetes에서 실제 애플리케이션은 Pod 안에서 실행된다.

예를 들어 nginx Pod가 3개 있다고 하자.

```text
nginx Pod 1
nginx Pod 2
nginx Pod 3
```

그런데 Pod는 언제든지 죽고 다시 만들어질 수 있다. 이때 Pod IP도 바뀔 수 있다.

그래서 외부에서 Pod IP를 직접 바라보는 것은 좋지 않다.

```text
Pod IP 직접 접근
→ Pod가 재생성되면 IP가 바뀜
→ 접근 주소가 불안정함
```

그래서 Kubernetes에서는 중간에 Service를 둔다.

```text
사용자
  ↓
Service
  ↓
Pod 1 / Pod 2 / Pod 3
```

Service는 고정된 입구 역할을 하고, 뒤에 있는 Pod들로 요청을 보내준다.

즉 Service의 핵심은 이것이다.

```text
Service = Pod 앞에 세우는 고정된 접근 지점
```

---

## 2. Service는 Pod를 어떻게 찾을까?

Service는 `selector`를 보고 Pod를 찾는다.

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

여기서 중요한 부분은 이것이다.

```yaml
selector:
  app: nginx
```

뜻은 다음과 같다.

```text
app=nginx 라벨을 가진 Pod를 찾아라
```

그래서 `app=nginx` 라벨을 가진 Pod가 3개 있으면, Service는 그 3개 Pod를 자신의 대상으로 잡는다.

이걸 확인할 때 보는 것이 `Endpoints`다.

```bash
kubectl describe svc nginx-svc
```

결과에 이런 줄이 나오면:

```text
Endpoints: 10.42.1.8:80,10.42.2.7:80,10.42.0.8:80
```

이 뜻이다.

```text
nginx-svc Service가
10.42.1.8:80
10.42.2.7:80
10.42.0.8:80

이 세 개의 Pod를 바라보고 있다
```

즉 Service 뒤에 Pod 3개가 정상적으로 연결된 것이다.

이 부분은 NodePort든 LoadBalancer든 똑같다.

---

## 3. NodePort와 LoadBalancer가 비슷해 보이는 이유

NodePort와 LoadBalancer는 둘 다 Kubernetes Service다.

그래서 둘 다 결국 이런 구조를 가진다.

```text
Service
  ↓
Endpoints
  ↓
Pod 1 / Pod 2 / Pod 3
```

그래서 `kubectl describe svc`를 했을 때 Endpoints가 잡히는 모습은 비슷하다.

NodePort여도:

```text
Endpoints: 10.42.1.8:80,10.42.2.7:80,10.42.0.8:80
```

LoadBalancer여도:

```text
Endpoints: 10.42.1.8:80,10.42.2.7:80,10.42.0.8:80
```

이렇게 보일 수 있다.

그래서 실습하다 보면 당연히 이런 생각이 든다.

```text
둘 다 결국 Pod 3개로 보내는 거 아닌가?
```

맞다.

**최종 목적지는 둘 다 Pod다.**

다른 점은 **외부에서 Service까지 들어오는 입구**다.

---

# 4. NodePort일 때는 어디로 curl 해야 할까?

NodePort Service를 만들면 `kubectl get svc` 결과가 이런 식으로 나온다.

```bash
kubectl get svc nginx-svc
```

```text
NAME        TYPE       CLUSTER-IP      PORT(S)
nginx-svc   NodePort   10.43.188.207   80:30001/TCP
```

여기서 중요한 부분은 이것이다.

```text
TYPE = NodePort
PORT(S) = 80:30001/TCP
```

이 의미는 다음과 같다.

```text
Service 내부 포트 = 80
외부에서 들어갈 NodePort = 30001
```

즉, 외부에서는 `30001`번 포트로 들어가야 한다.

---

## 5. 일반 VM/AWS 환경의 NodePort 접근

일반 VM이나 AWS EC2 기반 Kubernetes라면 Node가 실제 서버다.

그러면 외부에서는 Node IP와 NodePort로 접근한다.

```bash
curl http://<Node-IP>:30001
```

예를 들어 Node IP가 다음과 같다면:

```text
master-1  172.26.8.74
worker-1  172.26.3.104
worker-2  172.26.9.60
```

이렇게 접속할 수 있다.

```bash
curl http://172.26.8.74:30001
curl http://172.26.3.104:30001
curl http://172.26.9.60:30001
```

AWS라면 Worker Node의 External IP로 접속할 수 있다.

```bash
curl http://<worker-node-external-ip>:30001
```

브라우저에서는 이렇게 들어간다.

```text
http://<worker-node-external-ip>:30001
```

단, AWS에서는 보안그룹이나 방화벽에서 `30001` 포트가 열려 있어야 한다.

```text
NodePort Service 생성
+ AWS 보안그룹 30001 인바운드 오픈
= 외부에서 NodeIP:30001 접근 가능
```

NodePort는 이렇게 외우면 된다.

```text
NodePort = Node IP + NodePort 번호로 들어간다
```

---

## 6. k3d 환경의 NodePort 접근

k3d에서는 조금 다르다.

k3d의 Node는 실제 VM이 아니라 Docker 컨테이너다.

```text
Mac
  ↓
Docker Desktop
  ↓
k3d node containers
```

그래서 `kubectl get nodes -o wide`에 보이는 Node IP가 이런 식이어도:

```text
k3d-my-cluster-server-0   172.19.0.3
k3d-my-cluster-agent-0    172.19.0.4
k3d-my-cluster-agent-1    172.19.0.5
```

Mac에서 바로 다음처럼 접속이 안 될 수 있다.

```bash
curl http://172.19.0.3:30001
```

왜냐하면 저 IP는 Mac이 직접 접근하는 실제 VM IP가 아니라 Docker 내부 네트워크의 컨테이너 IP이기 때문이다.

그래서 k3d에서는 클러스터를 만들 때 포트 매핑을 해줘야 한다.

```bash
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "30001:30001@loadbalancer"
```

이 의미는 다음과 같다.

```text
Mac localhost:30001
        ↓
k3d loadbalancer container:30001
        ↓
Kubernetes NodePort 30001
        ↓
nginx-svc
        ↓
nginx Pod
```

그러면 Mac에서는 이렇게 접속한다.

```bash
curl http://localhost:30001
```

정리하면:

```text
NodePort + 일반 VM/AWS
→ curl http://NodeIP:30001

NodePort + k3d 포트 매핑
→ curl http://localhost:30001
```

---

# 7. LoadBalancer일 때는 어디로 curl 해야 할까?

이번에는 Service 타입이 LoadBalancer라고 하자.

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

적용한다.

```bash
kubectl apply -f loabalancer-svc.yaml
```

Service를 확인한다.

```bash
kubectl get svc nginx-svc
```

출력 예시는 다음과 같다.

```text
NAME        TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)
nginx-svc   LoadBalancer   10.43.188.207   <pending>     80:xxxxx/TCP
```

여기서 중요한 부분은 이것이다.

```text
TYPE = LoadBalancer
port = 80
```

LoadBalancer는 원래 외부 LoadBalancer 주소로 들어가는 방식이다.

---

## 8. AWS/EKS 환경의 LoadBalancer 접근

AWS EKS 같은 클라우드 환경에서는 LoadBalancer Service를 만들면 AWS Load Balancer가 생성될 수 있다.

구조는 이렇게 된다.

```text
외부 사용자
    ↓
AWS Load Balancer
    ↓
Kubernetes Service
    ↓
Pod 1 / Pod 2 / Pod 3
```

이 경우 `kubectl get svc`를 했을 때 `EXTERNAL-IP`나 외부 DNS가 잡힐 수 있다.

```text
NAME        TYPE           CLUSTER-IP      EXTERNAL-IP
nginx-svc   LoadBalancer   10.43.x.x       abc.elb.amazonaws.com
```

그러면 접속은 이렇게 한다.

```bash
curl http://abc.elb.amazonaws.com
```

또는:

```bash
curl http://<LoadBalancer-External-IP>
```

브라우저에서는 이렇게 들어간다.

```text
http://abc.elb.amazonaws.com
```

만약 Service가 80번 포트로 열려 있다면 뒤에 `:80`은 생략할 수 있다.

```text
http://abc.elb.amazonaws.com
=
http://abc.elb.amazonaws.com:80
```

왜냐하면 HTTP의 기본 포트가 80이기 때문이다.

---

## 9. k3d 환경의 LoadBalancer 접근

k3d는 AWS가 아니다.

즉, LoadBalancer Service를 만들었다고 해서 진짜 AWS ELB 같은 외부 로드밸런서가 생기는 것은 아니다.

k3d에서는 Docker/k3d loadbalancer 컨테이너와 포트 매핑을 이용해 외부 접근을 흉내 낸다.

그래서 LoadBalancer Service를 Mac에서 확인하려면 클러스터를 만들 때 포트 매핑을 해줘야 한다.

예를 들어 Service가 80번 포트를 사용한다면:

```bash
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "80:80@loadbalancer"
```

이 의미는 다음과 같다.

```text
Mac localhost:80
        ↓
k3d loadbalancer container:80
        ↓
nginx-svc LoadBalancer Service:80
        ↓
nginx Pod:80
```

그러면 Mac에서 이렇게 접속할 수 있다.

```bash
curl http://localhost
```

또는:

```bash
curl http://localhost:80
```

둘은 같은 의미다.

왜냐하면 HTTP의 기본 포트가 80이기 때문이다.

---

## 10. LoadBalancer를 8080으로 매핑했다면?

만약 클러스터를 이렇게 만들었다고 하자.

```bash
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "8080:80@loadbalancer"
```

이건 이렇게 읽는다.

```text
Mac localhost:8080
        ↓
k3d loadbalancer container:80
        ↓
nginx-svc Service:80
        ↓
nginx Pod:80
```

이때는 Mac에서 이렇게 접속해야 한다.

```bash
curl http://localhost:8080
```

`curl http://localhost`로 하면 안 맞다.

왜냐하면 `http://localhost`는 자동으로 80번 포트로 요청을 보내는데, 지금 Mac에서 열어둔 포트는 8080이기 때문이다.

정리하면:

```text
--port "80:80@loadbalancer"
→ curl http://localhost

--port "8080:80@loadbalancer"
→ curl http://localhost:8080

--port "3000:80@loadbalancer"
→ curl http://localhost:3000
```

앞쪽 포트가 내가 접속하는 포트다.

---

# 11. NodePort와 LoadBalancer curl 주소 비교

이제 진짜 핵심만 모아서 비교해보자.

## NodePort

Service 예시:

```text
nginx-svc   NodePort   10.43.188.207   80:30001/TCP
```

일반 VM/AWS:

```bash
curl http://<Node-IP>:30001
```

k3d에서 포트 매핑한 경우:

```bash
curl http://localhost:30001
```

---

## LoadBalancer

Service 예시:

```text
nginx-svc   LoadBalancer   10.43.188.207   EXTERNAL-IP   80/TCP
```

AWS/EKS:

```bash
curl http://<LoadBalancer-DNS>
```

또는:

```bash
curl http://<LoadBalancer-External-IP>
```

k3d에서 `80:80` 포트 매핑한 경우:

```bash
curl http://localhost
```

k3d에서 `8080:80` 포트 매핑한 경우:

```bash
curl http://localhost:8080
```

---

## 12. 클러스터 내부에서는 둘 다 비슷하다

NodePort든 LoadBalancer든 Service는 ClusterIP를 가진다.

그래서 클러스터 내부에서는 Service 이름이나 ClusterIP로 접근할 수 있다.

curl 테스트 Pod를 띄운다.

```bash
kubectl run curl-test --image=curlimages/curl -it --rm -- sh
```

Pod 안에서 Service 이름으로 접근한다.

```bash
curl http://nginx-svc
```

또는 ClusterIP로 접근한다.

```bash
curl http://10.43.188.207
```

이건 NodePort든 LoadBalancer든 가능하다.

왜냐하면 둘 다 결국 Kubernetes Service이고, 내부에서는 Service 이름이나 ClusterIP로 접근할 수 있기 때문이다.

```text
curl-test Pod
    ↓
nginx-svc
    ↓
Pod 1 / Pod 2 / Pod 3
```

---

# 13. 한 번에 정리하는 표

| Service 타입   | 환경               | 접속 주소                            |
| ------------ | ---------------- | -------------------------------- |
| NodePort     | 일반 VM/AWS        | `curl http://<Node-IP>:30001`    |
| NodePort     | k3d 포트 매핑 있음     | `curl http://localhost:30001`    |
| LoadBalancer | AWS/EKS          | `curl http://<LoadBalancer-DNS>` |
| LoadBalancer | k3d `80:80` 매핑   | `curl http://localhost`          |
| LoadBalancer | k3d `8080:80` 매핑 | `curl http://localhost:8080`     |
| 둘 다 내부 테스트   | curl-test Pod 안  | `curl http://nginx-svc`          |

---

## 14. 진짜 쉽게 외우기

NodePort는 이렇게 외우면 된다.

```text
NodePort
= Node IP와 NodePort 번호로 들어간다
= http://NodeIP:30001
```

LoadBalancer는 이렇게 외우면 된다.

```text
LoadBalancer
= LoadBalancer 주소로 들어간다
= http://로드밸런서주소
```

k3d에서는 이렇게 외우면 된다.

```text
k3d는 Node가 Docker 컨테이너다
그래서 Mac에서 localhost로 들어가려면 클러스터 생성 시 포트 매핑이 필요하다
```

포트 매핑은 이렇게 읽는다.

```text
앞쪽 포트 : 뒤쪽 포트

앞쪽 포트 = 내가 curl이나 브라우저에서 치는 포트
뒤쪽 포트 = k3d 내부로 넘길 포트
```

예를 들어:

```bash
--port "8080:80@loadbalancer"
```

이면:

```text
내가 접속하는 주소 = localhost:8080
k3d 내부로 넘기는 포트 = 80
```

그래서 접속은 이렇게 한다.

```bash
curl http://localhost:8080
```

---

## 15. 결론

NodePort와 LoadBalancer는 둘 다 결국 Service 뒤의 Pod들로 트래픽을 보낸다.

그래서 Endpoints를 보면 비슷해 보이는 것이 정상이다.

```text
Service
  ↓
Endpoints
  ↓
Pod들
```

하지만 외부에서 Service까지 들어오는 입구가 다르다.

```text
NodePort
= 사용자가 NodeIP:NodePort로 직접 들어감

LoadBalancer
= 외부 LoadBalancer 주소로 들어감
```

그리고 k3d에서는 진짜 클라우드 LoadBalancer가 있는 것이 아니기 때문에, Mac에서 테스트하려면 클러스터 생성 시 포트 매핑이 필요하다.

한 문장으로 정리하면 다음과 같다.

```text
NodePort는 NodeIP:NodePort로 들어가고, LoadBalancer는 LoadBalancer 주소로 들어가며, k3d에서는 둘 다 localhost로 테스트하려면 미리 포트 매핑을 해줘야 한다.
```
