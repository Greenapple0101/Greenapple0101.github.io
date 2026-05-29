---
title: "[Kubernetes] CoreDNS란? 서비스 이름을 IP로 바꿔주는 DNS 서버"
source: "https://velog.io/@yorange50/Kubernetes-CoreDNS란-서비스-이름을-IP로-바꿔주는-DNS-서버"
published: "2026-05-28T23:56:37.788Z"
tags: ""
backup_date: "2026-05-29T14:52:52.705078"
---



쿠버네티스를 공부하다 보면 이런 주소를 자주 보게 된다.

```text
mysql.default.svc.cluster.local
```

또는 파드 안에서 그냥 이렇게 호출하기도 한다.

```bash
curl http://mysql
```

처음 보면 조금 이상하다.

“mysql이라는 도메인을 산 적도 없는데 왜 접속이 되지?”
“저 이름을 누가 IP로 바꿔주는 거지?”

이걸 가능하게 해주는 핵심 컴포넌트가 바로 **CoreDNS**다.

---

## 1. CoreDNS를 한 줄로 말하면

CoreDNS는 쿠버네티스 클러스터 안에서 DNS 역할을 하는 서버다.

쉽게 말하면 파드가 어떤 서비스 이름으로 요청을 보냈을 때, CoreDNS가 그 이름을 실제 IP로 바꿔준다.

```text
CoreDNS
= 쿠버네티스 내부 DNS 서버
= Service 이름을 ClusterIP로 바꿔주는 역할
= 파드들이 IP를 몰라도 이름으로 통신할 수 있게 해주는 컴포넌트
```

예를 들어 쿠버네티스에 이런 Service가 있다고 하자.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql
  namespace: default
spec:
  selector:
    app: mysql
  ports:
    - port: 3306
```

그러면 같은 클러스터 안의 다른 파드는 아래 이름들로 접근할 수 있다.

```text
mysql
mysql.default
mysql.default.svc
mysql.default.svc.cluster.local
```

이 이름들을 IP로 해석해주는 것이 CoreDNS다.

---

## 2. 왜 CoreDNS가 필요할까?

쿠버네티스에서 Pod는 언제든지 죽고 다시 만들어질 수 있다.

그러면 Pod IP도 바뀔 수 있다.

```text
기존 mysql Pod IP: 10.42.1.15
재시작 후 mysql Pod IP: 10.42.2.31
```

만약 애플리케이션이 Pod IP를 직접 바라보고 있었다면 문제가 생긴다.

Pod가 재시작될 때마다 접속 주소가 바뀌기 때문이다.

그래서 쿠버네티스에서는 보통 Pod에 직접 접근하지 않고 **Service**를 만든다.

```text
mysql Service 이름
        ↓
mysql Service ClusterIP
        ↓
실제 mysql Pod들
```

여기서 `mysql`이라는 이름을 Service의 ClusterIP로 바꿔주는 역할을 CoreDNS가 한다.

즉 CoreDNS 덕분에 애플리케이션은 매번 바뀌는 Pod IP를 몰라도 된다.

그냥 Service 이름만 알면 된다.

---

## 3. CoreDNS는 어디에 있을까?

CoreDNS도 결국 쿠버네티스 안에서 돌아가는 Pod다.

보통 `kube-system` 네임스페이스에 있다.

확인하려면 아래 명령어를 쓴다.

```bash
kubectl get pod -n kube-system
```

예시는 이런 식이다.

```text
coredns-xxxxxxxxxx-xxxxx   1/1   Running
coredns-xxxxxxxxxx-yyyyy   1/1   Running
```

Deployment로 관리되는 경우가 많다.

```bash
kubectl get deploy -n kube-system
```

예시는 다음과 같다.

```text
coredns   2/2   2   2
```

즉 CoreDNS는 특별한 외부 DNS 서버가 아니라, 클러스터 내부에서 동작하는 DNS Pod다.

---

## 4. 파드는 CoreDNS를 어떻게 알고 있을까?

파드 안에 들어가서 `/etc/resolv.conf`를 보면 DNS 서버 정보가 들어 있다.

```bash
kubectl exec -it <pod-name> -- cat /etc/resolv.conf
```

대략 이런 식으로 나온다.

```text
nameserver 10.43.0.10
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

여기서 중요한 건 `nameserver`다.

```text
nameserver 10.43.0.10
```

이 IP는 보통 `kube-dns` Service의 ClusterIP다.

확인해보면 다음과 같다.

```bash
kubectl get svc -n kube-system
```

예시는 이런 식이다.

```text
NAME       TYPE        CLUSTER-IP    PORT(S)
kube-dns   ClusterIP   10.43.0.10    53/UDP,53/TCP
```

이 `kube-dns` Service 뒤에 CoreDNS Pod들이 붙어 있다.

흐름을 정리하면 이렇다.

```text
Pod
 ↓
/etc/resolv.conf의 nameserver
 ↓
kube-dns Service
 ↓
CoreDNS Pod
 ↓
Service 이름을 ClusterIP로 응답
```

즉 파드는 직접 CoreDNS Pod IP를 외우는 게 아니다.

파드의 DNS 설정에는 `kube-dns` Service IP가 들어 있고, 그 Service가 CoreDNS Pod로 연결해준다.

---

## 5. Service 이름은 어떻게 해석될까?

예를 들어 `default` 네임스페이스에 `mysql` Service가 있다고 하자.

같은 네임스페이스의 파드에서는 이렇게 호출할 수 있다.

```bash
curl http://mysql
```

이렇게 짧게 써도 되는 이유는 DNS 검색 경로 때문이다.

파드의 `/etc/resolv.conf`에는 보통 이런 검색 경로가 들어 있다.

```text
search default.svc.cluster.local svc.cluster.local cluster.local
```

그래서 `mysql`이라고만 써도 내부적으로 이런 이름들을 순서대로 찾아본다.

```text
mysql.default.svc.cluster.local
mysql.svc.cluster.local
mysql.cluster.local
mysql
```

그래서 같은 네임스페이스 안에서는 `mysql`만 써도 되는 경우가 많다.

하지만 다른 네임스페이스에서 접근한다면 네임스페이스까지 붙이는 게 안전하다.

```bash
curl http://mysql.default
```

또는 전체 이름을 쓸 수도 있다.

```bash
curl http://mysql.default.svc.cluster.local
```

---

## 6. CoreDNS와 kube-dns는 같은 걸까?

이름 때문에 헷갈릴 수 있다.

현재 쿠버네티스에서는 보통 CoreDNS가 DNS 서버 역할을 한다.

그런데 Service 이름은 여전히 `kube-dns`인 경우가 많다.

```bash
kubectl get svc -n kube-system
```

```text
kube-dns   ClusterIP   10.43.0.10
```

즉 이름은 `kube-dns`지만, 실제 뒤에서 동작하는 Pod는 CoreDNS일 수 있다.

```text
kube-dns Service
        ↓
CoreDNS Pod
```

그래서 실무에서는 이런 말을 자주 듣게 된다.

```text
CoreDNS 확인해봐.
```

그런데 막상 명령어를 치면 `kube-dns` Service를 확인하게 되는 경우가 있다.

정리하면 이렇게 보면 된다.

```text
CoreDNS
= 실제 DNS 서버 역할을 하는 Pod

kube-dns Service
= CoreDNS Pod 앞에 있는 Service 이름
```

---

## 7. CoreDNS 설정은 어디에 있을까?

CoreDNS 설정은 보통 ConfigMap으로 관리된다.

먼저 ConfigMap 목록을 확인한다.

```bash
kubectl get configmap -n kube-system
```

보통 `coredns`라는 ConfigMap이 있다.

내용을 보려면 다음 명령어를 쓴다.

```bash
kubectl get configmap coredns -n kube-system -o yaml
```

대략 이런 구조가 나온다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns
  namespace: kube-system
data:
  Corefile: |
    .:53 {
        errors
        health
        ready
        kubernetes cluster.local in-addr.arpa ip6.arpa {
            pods insecure
            fallthrough in-addr.arpa ip6.arpa
        }
        forward . /etc/resolv.conf
        cache 30
        loop
        reload
        loadbalance
    }
```

여기서 중요한 부분은 이것이다.

```text
kubernetes cluster.local
```

CoreDNS가 쿠버네티스 내부 도메인인 `cluster.local`을 처리한다는 뜻이다.

그리고 이 부분도 중요하다.

```text
forward . /etc/resolv.conf
```

클러스터 내부 이름이 아닌 외부 도메인 요청은 외부 DNS로 넘긴다는 뜻이다.

예를 들어 파드 안에서 이런 요청을 보냈다고 하자.

```bash
curl https://google.com
```

이건 쿠버네티스 Service 이름이 아니다.

그래서 CoreDNS가 직접 처리하지 않고 외부 DNS로 전달한다.

---

## 8. CoreDNS 장애가 나면 무슨 일이 생길까?

CoreDNS가 죽거나 이상해지면 클러스터 내부에서 이름 해석이 안 된다.

예를 들어 이런 요청이 실패할 수 있다.

```bash
curl http://mysql
```

결과는 이런 식으로 나올 수 있다.

```text
Could not resolve host: mysql
```

애플리케이션 로그에서는 이런 에러가 보일 수도 있다.

```text
UnknownHostException
Name or service not known
Temporary failure in name resolution
```

이때 실제 `mysql` Pod가 죽은 게 아닐 수도 있다.

Service도 정상일 수 있다.

문제는 단순히 이름을 IP로 바꿔주는 DNS가 안 되는 것일 수 있다.

그래서 클러스터 내부 통신 장애를 볼 때는 DNS도 같이 확인해야 한다.

```bash
kubectl get pod -n kube-system | grep coredns
kubectl get svc -n kube-system | grep kube-dns
kubectl logs -n kube-system deploy/coredns
```

---

## 9. CoreDNS 확인용 명령어

CoreDNS Pod 확인

```bash
kubectl get pod -n kube-system | grep coredns
```

CoreDNS Deployment 확인

```bash
kubectl get deploy -n kube-system coredns
```

kube-dns Service 확인

```bash
kubectl get svc -n kube-system kube-dns
```

CoreDNS 로그 확인

```bash
kubectl logs -n kube-system deploy/coredns
```

CoreDNS 설정 확인

```bash
kubectl get configmap coredns -n kube-system -o yaml
```

파드 내부 DNS 설정 확인

```bash
kubectl exec -it <pod-name> -- cat /etc/resolv.conf
```

DNS 테스트용 파드 실행

```bash
kubectl run dns-test --image=busybox:1.28 --restart=Never -it --rm -- sh
```

파드 안에서 테스트

```bash
nslookup kubernetes.default
nslookup mysql.default
```

---

## 10. CoreDNS를 그림으로 보면

전체 흐름을 그림처럼 보면 이렇다.

```text
[App Pod]
   |
   | curl http://mysql
   v
[/etc/resolv.conf]
   |
   | nameserver 10.43.0.10
   v
[kube-dns Service]
   |
   v
[CoreDNS Pod]
   |
   | mysql.default.svc.cluster.local 조회
   v
[mysql Service ClusterIP]
   |
   v
[mysql Pod]
```

즉 애플리케이션은 IP를 몰라도 된다.

그냥 Service 이름만 알면 된다.

```text
mysql
```

그러면 CoreDNS가 그 이름을 IP로 바꿔준다.

---

## 11. CKA나 실습에서 자주 나오는 포인트

CoreDNS는 직접 설정을 많이 건드리는 컴포넌트는 아니다.

하지만 문제 상황에서는 자주 등장한다.

### 1. DNS가 안 되는 상황

예를 들어 아래 명령어가 실패한다고 하자.

```bash
nslookup kubernetes.default
```

그러면 CoreDNS 상태를 봐야 한다.

```bash
kubectl get pod -n kube-system
kubectl logs -n kube-system deploy/coredns
```

---

### 2. Service 이름으로 접근이 안 되는 상황

예를 들어 아래 요청이 안 된다고 하자.

```bash
curl http://my-service
```

이때는 바로 CoreDNS만 의심하면 안 된다.

순서를 나눠서 봐야 한다.

```text
1. Service가 존재하는가?
2. Service selector가 Pod label과 맞는가?
3. Endpoint가 잡혔는가?
4. CoreDNS가 정상인가?
5. 파드의 /etc/resolv.conf가 정상인가?
```

Endpoint 확인은 아래 명령어로 할 수 있다.

```bash
kubectl get endpoints
```

또는 최신 방식으로는 EndpointSlice를 볼 수 있다.

```bash
kubectl get endpointslice
```

Service는 있는데 Endpoint가 비어 있다면, DNS 문제가 아니라 Service selector와 Pod label이 안 맞는 문제일 수 있다.

---

### 3. CoreDNS ConfigMap 문제

CoreDNS 설정이 깨지면 DNS 전체가 이상해질 수 있다.

설정은 아래 명령어로 확인한다.

```bash
kubectl get cm coredns -n kube-system -o yaml
```

설정을 수정한 뒤에는 CoreDNS를 재시작하는 경우도 있다.

```bash
kubectl rollout restart deployment coredns -n kube-system
```

---

## 12. 한 번에 정리

CoreDNS는 쿠버네티스 클러스터 내부의 DNS 서버다.

파드가 이런 이름으로 요청을 보내면

```text
mysql
redis
backend.default.svc.cluster.local
```

CoreDNS가 해당 Service의 ClusterIP를 찾아준다.

흐름은 이렇게 볼 수 있다.

```text
서비스 이름
    ↓
CoreDNS
    ↓
Service ClusterIP
    ↓
Pod
```

그래서 애플리케이션은 매번 바뀌는 Pod IP를 몰라도 된다.

그냥 안정적인 Service 이름으로 통신하면 된다.

마지막으로 핵심만 정리하면 이렇다.

```text
CoreDNS
= 쿠버네티스 내부 DNS 서버

kube-dns Service
= CoreDNS Pod 앞에 있는 Service

/etc/resolv.conf
= 파드가 어떤 DNS 서버를 볼지 적힌 파일

cluster.local
= 쿠버네티스 내부 도메인

Service 이름
= CoreDNS를 통해 ClusterIP로 해석됨
```

쿠버네티스에서 Service 이름으로 통신할 수 있는 이유가 바로 CoreDNS다.

그래서 클러스터 내부 통신 문제가 생겼을 때는 단순히 Pod만 볼 게 아니라 DNS 흐름도 같이 봐야 한다.

```bash
kubectl get pod -n kube-system | grep coredns
kubectl get svc -n kube-system kube-dns
kubectl exec -it <pod> -- cat /etc/resolv.conf
nslookup kubernetes.default
```

CoreDNS는 평소에는 조용히 뒤에서 일하지만, 문제가 생기면 클러스터 전체 통신이 흔들릴 수 있는 중요한 컴포넌트라고 보면 된다.
