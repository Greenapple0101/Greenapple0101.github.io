---
title: "[KUBERNETES] LoadBalancer랑 NodePort는 뭐가 다를까? 사실 비슷해 보이는 게 맞다"
source: "https://velog.io/@yorange50/KUBERNETES-LoadBalancer랑-NodePort는-뭐가-다를까-사실-비슷해-보이는-게-맞다"
published: "2026-05-19T05:56:35.130Z"
tags: ""
backup_date: "2026-05-29T14:52:52.723718"
---

Kubernetes Service를 공부하다 보면 `ClusterIP`, `NodePort`, `LoadBalancer`가 나온다. 처음에는 셋이 완전히 다른 방식처럼 느껴지는데, 실습을 해보면 이런 생각이 든다.

```text
LoadBalancer랑 NodePort랑 뭐가 다른 거지?
둘 다 결국 Pod로 보내는 거 아닌가?
Endpoints도 똑같이 잡히는데?
```

결론부터 말하면, **그렇게 느끼는 게 맞다.**

`NodePort`와 `LoadBalancer`는 완전히 별개의 구조라기보다, 같은 Service 구조 위에서 **외부에서 들어오는 입구가 다를 뿐**이다.

---

## 1. Service의 진짜 역할

Kubernetes에서 실제 애플리케이션은 Pod 안에서 실행된다.

예를 들어 nginx Pod가 3개 떠 있다고 하자.

```text
nginx Pod 1
nginx Pod 2
nginx Pod 3
```

그런데 Pod는 언제든지 죽고 다시 만들어질 수 있다. Pod가 다시 만들어지면 IP도 바뀔 수 있다.

그래서 사용자가 Pod IP를 직접 바라보면 불안정하다.

```text
Pod IP 직접 접근
→ Pod가 죽으면 IP 바뀜
→ 접근 주소도 바뀜
```

그래서 중간에 Service를 둔다.

```text
사용자 또는 다른 Pod
        ↓
Service
        ↓
Pod 1 / Pod 2 / Pod 3
```

Service는 고정된 입구 역할을 하고, 뒤에 있는 Pod들로 요청을 나눠 보낸다.

즉 Service의 핵심은 이거다.

```text
Service = Pod 앞에 세우는 고정된 접근 지점
```

---

## 2. Service는 Pod를 어떻게 찾을까?

Service는 `selector`를 보고 Pod를 찾는다.

예를 들어 이런 Service가 있다고 하자.

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

여기서 중요한 부분은 이거다.

```yaml
selector:
  app: nginx
```

뜻은 다음과 같다.

```text
app=nginx 라벨을 가진 Pod들을 찾아라
```

그래서 `app=nginx` 라벨을 가진 Pod가 3개 있으면, Service는 그 3개 Pod를 자신의 대상으로 잡는다.

이걸 확인할 때 보는 게 `Endpoints`다.

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

---

## 3. NodePort와 LoadBalancer가 비슷해 보이는 이유

NodePort든 LoadBalancer든 결국 Service다.

둘 다 selector로 Pod를 찾고, Endpoints에 잡힌 Pod들로 요청을 보낸다.

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
둘 다 똑같이 Pod 3개로 보내는 거 아닌가?
```

맞다.

**최종 목적지는 둘 다 Pod다.**

차이는 Pod로 가기 전, 외부 요청이 Service까지 들어오는 방식이다.

---

## 4. NodePort는 Node의 포트로 직접 들어간다

NodePort는 말 그대로 Kubernetes Node의 특정 포트를 외부에 열어주는 방식이다.

예를 들어 Service가 이렇게 떠 있다고 하자.

```bash
kubectl get svc nginx-svc
```

```text
NAME        TYPE       CLUSTER-IP      PORT(S)
nginx-svc   NodePort   10.43.188.207   80:30001/TCP
```

여기서 `30001`이 NodePort다.

이 말은:

```text
Node의 30001번 포트로 들어오면
nginx-svc Service의 80번 포트로 보내겠다
```

라는 뜻이다.

일반 VM 환경에서는 이렇게 접근한다.

```bash
curl http://<Node-IP>:30001
```

예를 들면:

```bash
curl http://172.26.8.74:30001
```

흐름은 이렇다.

```text
외부 사용자
    ↓
NodeIP:30001
    ↓
NodePort Service
    ↓
nginx Pod 중 하나
```

즉 NodePort는 사용자가 Node IP와 NodePort를 알고 직접 들어가는 방식이다.

---

## 5. LoadBalancer는 앞에 외부 로드밸런서가 하나 더 붙는다

LoadBalancer는 NodePort와 완전히 다른 길로 가는 게 아니다.

보통은 NodePort 앞에 외부 LoadBalancer가 하나 더 붙는 구조로 이해하면 쉽다.

```text
외부 사용자
    ↓
외부 LoadBalancer IP 또는 DNS
    ↓
NodeIP:NodePort
    ↓
Service
    ↓
Pod
```

예를 들어 AWS EKS에서 LoadBalancer Service를 만들면, AWS ELB 같은 클라우드 로드밸런서가 생성될 수 있다.

그러면 사용자는 Worker Node IP를 직접 몰라도 된다.

그냥 LoadBalancer 주소 하나로 접속하면 된다.

```text
http://abc.elb.amazonaws.com
```

흐름은 이렇게 된다.

```text
사용자
  ↓
AWS Load Balancer
  ↓
Kubernetes Node
  ↓
Service
  ↓
Pod 1 / Pod 2 / Pod 3
```

즉 LoadBalancer의 핵심은 이것이다.

```text
사용자가 Node IP를 직접 몰라도 되게 앞에서 받아주는 외부 입구를 만든다
```

---

## 6. 계층으로 보면 더 쉽다

Kubernetes Service 타입은 이렇게 계층처럼 이해하면 편하다.

```text
ClusterIP
= 클러스터 내부에서만 접근 가능한 Service

NodePort
= ClusterIP + 모든 Node에 외부 포트 하나 열기

LoadBalancer
= NodePort + 외부 LoadBalancer 붙이기
```

그림으로 보면:

```text
ClusterIP
  ↓
클러스터 내부에서만 접근

NodePort
  ↓
NodeIP:NodePort로 외부 접근 가능

LoadBalancer
  ↓
외부 LoadBalancer 주소로 접근 가능
```

즉 LoadBalancer는 NodePort와 완전히 다른 Service라기보다는, **NodePort를 외부 서비스답게 감싼 형태**로 보면 된다.

---

## 7. NodePort와 LoadBalancer 비교

### NodePort

```text
외부 사용자
  ↓
NodeIP:30001
  ↓
nginx-svc
  ↓
Pod
```

사용자는 Node IP와 포트를 직접 알아야 한다.

```bash
curl http://172.26.8.74:30001
```

### LoadBalancer

```text
외부 사용자
  ↓
LoadBalancer 주소
  ↓
nginx-svc
  ↓
Pod
```

사용자는 Node IP를 몰라도 된다.

```bash
curl http://로드밸런서주소
```

정리하면:

| 구분                   | NodePort          | LoadBalancer          |
| -------------------- | ----------------- | --------------------- |
| 외부 접속 주소             | `NodeIP:NodePort` | `LoadBalancer IP/DNS` |
| 사용자가 Node IP를 알아야 하나 | 알아야 함             | 몰라도 됨                 |
| Service 뒤 Pod 로드밸런싱  | 됨                 | 됨                     |
| Endpoints            | Pod 목록 잡힘         | Pod 목록 잡힘             |
| 클라우드 로드밸런서 생성        | 안 함               | 함                     |
| 실무 외부 공개용            | 제한적               | 더 일반적                 |

---

## 8. k3d에서는 왜 더 똑같아 보일까?

로컬에서 k3d로 실습하면 LoadBalancer와 NodePort가 더 비슷해 보인다.

이유는 k3d가 AWS 같은 진짜 클라우드 환경이 아니기 때문이다.

k3d는 Kubernetes Node를 실제 VM으로 만드는 게 아니라 Docker 컨테이너로 만든다.

구조는 대략 이렇다.

```text
Mac
 |
Docker Desktop
 |
k3d node containers
```

그래서 LoadBalancer Service를 만든다고 해서 AWS ELB 같은 진짜 외부 로드밸런서가 생기지는 않는다.

k3d에서는 보통 `k3d loadbalancer container`와 Docker 포트 매핑을 이용해서 외부 접근을 흉내 낸다.

예를 들어 클러스터를 만들 때 이렇게 해야 한다.

```bash
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "80:80@loadbalancer"
```

이 설정은 이런 의미다.

```text
Mac localhost:80
        ↓
k3d loadbalancer container:80
        ↓
LoadBalancer Service
        ↓
Pod
```

그래서 Mac에서 이렇게 접속할 수 있다.

```bash
curl http://localhost
```

---

## 9. 포트 매핑을 안 하면 어떻게 될까?

LoadBalancer Service를 만들었는데 클러스터 생성 때 포트 매핑을 안 했다면 이런 상태다.

```text
Service는 있음
Endpoints도 잡힘
Pod도 연결됨

하지만 Mac에서 k3d 안으로 들어가는 문이 없음
```

즉 `kubectl describe svc nginx-svc`에서:

```text
Endpoints: 10.42.1.8:80,10.42.2.7:80,10.42.0.8:80
```

이렇게 나와도, Mac에서:

```bash
curl http://localhost
```

가 안 될 수 있다.

이건 Service가 Pod를 못 찾는 문제가 아니다.

문제는 더 앞쪽이다.

```text
Mac → k3d 내부로 들어가는 포트 매핑이 없음
```

그래서 k3d에서는 LoadBalancer를 외부에서 테스트하려면 클러스터 생성 시 포트 매핑을 해줘야 한다.

```bash
k3d cluster create my-cluster \
  --port "80:80@loadbalancer"
```

---

## 10. 그래서 “둘이 똑같은 거 아니야?”에 대한 답

거의 맞다.

**Pod로 트래픽을 보내는 내부 구조는 비슷하다.**

둘 다 결국:

```text
Service
  ↓
Endpoints
  ↓
Pod들
```

로 간다.

하지만 외부에서 Service까지 들어오는 방식이 다르다.

```text
NodePort
= 사용자가 NodeIP:NodePort로 직접 들어간다

LoadBalancer
= 외부 LoadBalancer가 앞에서 받아서 Service로 넘긴다
```

즉 차이는 “Pod로 보내느냐”가 아니라 “외부 입구를 누가 제공하느냐”다.

---

## 11. 비유로 이해하기

Pod를 음식점 주방이라고 생각해보자.

Service는 카운터다.

```text
손님
 ↓
카운터(Service)
 ↓
주방(Pod)
```

NodePort는 이런 느낌이다.

```text
손님이 건물 뒷문 번호를 알고 직접 찾아감

172.26.8.74:30001
```

즉 손님이 어느 건물의 몇 번 문으로 들어가야 하는지 알아야 한다.

LoadBalancer는 이런 느낌이다.

```text
손님은 대표 안내 데스크로 감

대표 주소 하나만 알면 됨
```

안내 데스크가 알아서 적절한 건물과 문으로 보내준다.

그래서 사용자는 Node IP를 몰라도 된다.

---

## 12. 한 번에 정리

NodePort:

```text
외부 사용자
  ↓
NodeIP:NodePort
  ↓
Service
  ↓
Pod들
```

LoadBalancer:

```text
외부 사용자
  ↓
LoadBalancer IP/DNS
  ↓
Service
  ↓
Pod들
```

k3d LoadBalancer:

```text
Mac localhost:80
  ↓
k3d port mapping
  ↓
k3d loadbalancer container
  ↓
Service
  ↓
Pod들
```

결국 Pod로 가는 건 같다.

차이는 앞쪽 입구다.

---

## 13. 결론

LoadBalancer와 NodePort가 비슷해 보이는 이유는 정상이다.

둘 다 Kubernetes Service이고, 둘 다 selector로 Pod를 찾고, 둘 다 Endpoints에 잡힌 Pod들로 트래픽을 보낸다.

다만 NodePort는 사용자가 직접 Node IP와 Port로 들어가는 방식이고, LoadBalancer는 그 앞에 외부 로드밸런서가 붙어서 사용자가 Node 정보를 몰라도 접속하게 해주는 방식이다.

k3d에서는 진짜 클라우드 LoadBalancer가 없기 때문에 둘의 차이가 더 흐릿하게 느껴진다. 그래서 k3d에서는 LoadBalancer를 외부에서 테스트하려면 `--port "80:80@loadbalancer"` 같은 포트 매핑이 필요하다.

한 문장으로 정리하면 다음과 같다.

```text
NodePort와 LoadBalancer는 둘 다 결국 Service 뒤의 Pod들로 트래픽을 보내지만, NodePort는 NodeIP:Port로 직접 들어가고, LoadBalancer는 그 앞에 외부 로드밸런서라는 대표 입구를 하나 더 둔다.
```
