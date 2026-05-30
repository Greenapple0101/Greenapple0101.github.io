---
title: "[Kubernetes] 쿠버네티스 DNS 정리: CoreDNS와 Service 이름 해석"
source: ""
published: "2026-05-30T17:19:27.000Z"
---

쿠버네티스에서 Service를 만들면 이런 식으로 접근할 수 있다.

```bash
curl http://svc-web
```

또는 더 길게는 이렇게도 접근할 수 있다.

```bash
curl http://svc-web.default.svc.cluster.local
```

처음 보면 이상하다.

```text
svc-web이라는 이름을 어떻게 IP로 바꾸는 걸까?

default.svc.cluster.local은 무슨 뜻일까?

Pod 안에서는 DNS 설정이 어디에 들어있을까?

CoreDNS는 정확히 뭘 하는 걸까?
```

이걸 이해하기 위해 필요한 개념이 **Kubernetes DNS**다.

이번 글에서는 쿠버네티스 DNS, kube-dns Service, CoreDNS, Service DNS 이름 규칙, Pod 내부 `/etc/resolv.conf` 설정을 정리한다. 강의 자료의 학습 내용도 CoreDNS 사용과 DNS 편집을 중심으로 구성되어 있다. 

---

## 1. 쿠버네티스에서 DNS가 필요한 이유

쿠버네티스에서는 Pod가 계속 생성되고 삭제된다.

```text
Pod 생성
Pod 삭제
Pod 재시작
Pod 스케일 아웃
Pod 스케일 인
```

이때 Pod IP는 바뀔 수 있다.

예를 들어 `web` 애플리케이션 Pod가 3개 있다고 하자.

```text
web-pod-1 → 10.40.0.1
web-pod-2 → 10.32.0.2
web-pod-3 → 10.46.0.2
```

클라이언트가 이 Pod IP를 직접 외우고 접근하면 문제가 생긴다.

```text
Pod가 재시작됨
→ IP 변경
→ 기존 IP로 접근 실패
```

그래서 쿠버네티스에서는 Pod 앞에 Service를 둔다.

```text
Service: svc-web
ClusterIP: 10.96.100.100
        ↓
Pod 1: 10.40.0.1
Pod 2: 10.32.0.2
Pod 3: 10.46.0.2
```

하지만 Service IP도 매번 외우기는 불편하다.

그래서 쿠버네티스는 Service 이름을 DNS로 해석할 수 있게 해준다.

```text
svc-web.default.svc.cluster.local
        ↓
10.96.100.100
```

즉, 쿠버네티스 DNS는 Service 이름을 IP로 바꿔주는 역할을 한다.

---

## 2. Kubernetes DNS란?

Kubernetes DNS는 클러스터 내부에서 Service와 Pod 이름을 DNS 이름으로 접근할 수 있게 해주는 기능이다.

강의 자료에서는 Kubernetes DNS가 클러스터에서 실행하는 모든 Pod가 사용할 수 있도록 구성되며, DNS를 통해 Service와 Pod에 접근할 수 있다고 설명한다. 

정리하면 이렇다.

```text
Kubernetes DNS
→ 클러스터 내부 DNS 시스템
→ Service 이름을 ClusterIP로 변환
→ Pod DNS 이름을 Pod IP로 변환
→ Pod들이 이름 기반으로 통신할 수 있게 해줌
```

예를 들어 애플리케이션이 DB에 접근한다고 해보자.

IP를 직접 쓰는 방식은 좋지 않다.

```text
mysql Pod IP: 10.32.0.7
```

Pod가 재시작되면 IP가 바뀔 수 있기 때문이다.

대신 Service 이름을 사용한다.

```text
mysql.default.svc.cluster.local
```

또는 같은 namespace라면 더 짧게 쓸 수도 있다.

```text
mysql
```

---

## 3. CoreDNS란?

쿠버네티스에서 DNS 서버 역할을 하는 대표 컴포넌트가 **CoreDNS**다.

과거에는 kube-dns가 사용되었지만, 현재는 CoreDNS가 일반적으로 사용된다.

강의 자료에서도 `kube-dns`라는 Service가 존재하고, 실제로는 CoreDNS Pod가 동작하는 구조를 보여준다. 예시에서 kube-dns Service의 ClusterIP는 `10.96.0.10`이고, CoreDNS Pod들이 `kube-system` namespace에서 실행되는 것으로 나온다. 

구조는 이렇게 볼 수 있다.

```text
Pod
  ↓
DNS 질의
  ↓
kube-dns Service
  ↓
CoreDNS Pod
  ↓
Service 이름을 ClusterIP로 응답
```

즉, Pod가 DNS 질의를 직접 CoreDNS Pod IP로 보내는 것이 아니라, 보통 `kube-dns` Service를 통해 DNS 질의를 보낸다.

---

## 4. kube-dns Service

쿠버네티스 클러스터에는 보통 `kube-system` namespace에 `kube-dns` Service가 있다.

확인 명령어는 다음과 같다.

```bash
kubectl get svc -A
```

예시 출력은 이런 식이다.

```text
NAMESPACE     NAME         TYPE        CLUSTER-IP    PORT(S)
default       kubernetes   ClusterIP   10.96.0.1     443/TCP
kube-system   kube-dns     ClusterIP   10.96.0.10    53/UDP,53/TCP,9153/TCP
```

여기서 중요한 부분은 이것이다.

```text
kube-dns Service
→ ClusterIP: 10.96.0.10
→ DNS port: 53
```

Pod들은 DNS 서버로 이 `kube-dns` Service IP를 사용한다.

CoreDNS Pod 확인은 이렇게 한다.

```bash
kubectl get pod -A | grep dns
```

출력 예시는 다음과 비슷하다.

```text
kube-system   coredns-558bd4d5db-kbqgr   1/1   Running
kube-system   coredns-558bd4d5db-vbn7m   1/1   Running
```

즉, 실제 DNS 서버 프로세스는 CoreDNS Pod로 동작하고, 앞에는 `kube-dns` Service가 있다.

---

## 5. Service DNS 이름 규칙

쿠버네티스 Service는 다음 형식의 DNS 이름을 가진다.

```text
service_name.namespace.svc.cluster.local
```

예를 들어 Service 이름이 `svc-web`이고 namespace가 `default`라면 전체 DNS 이름은 이렇게 된다.

```text
svc-web.default.svc.cluster.local
```

구조를 나눠보면 이렇다.

```text
svc-web
→ Service 이름

default
→ namespace 이름

svc
→ Service 리소스라는 의미

cluster.local
→ 클러스터 내부 DNS 도메인
```

즉, 이 이름은 이렇게 해석된다.

```text
default namespace에 있는 svc-web Service
```

Pod 안에서 다음 명령을 실행하면 Service로 접근할 수 있다.

```bash
curl http://svc-web.default.svc.cluster.local
```

강의 자료에도 `curl http://svc-web.default.svc.cluster.local` 형태의 접근 예시가 나온다. 

---

## 6. 같은 namespace에서는 짧게 접근 가능

만약 클라이언트 Pod와 Service가 같은 namespace에 있다면 Service 이름만으로 접근할 수 있다.

```bash
curl http://svc-web
```

예를 들어 둘 다 `default` namespace에 있다면 다음 두 주소는 비슷하게 동작한다.

```text
svc-web
svc-web.default.svc.cluster.local
```

왜냐하면 Pod 내부의 DNS search 설정이 자동으로 들어가기 때문이다.

Pod가 `svc-web`이라는 이름을 찾으면 Kubernetes DNS 검색 규칙에 따라 다음처럼 후보를 붙여서 찾는다.

```text
svc-web.default.svc.cluster.local
svc-web.svc.cluster.local
svc-web.cluster.local
```

그래서 같은 namespace에서는 짧은 이름으로도 접근이 된다.

---

## 7. 다른 namespace의 Service 접근

다른 namespace에 있는 Service에 접근할 때는 namespace까지 적어주는 것이 안전하다.

예를 들어 `dev` namespace의 `mysql` Service에 접근하려면 이렇게 쓴다.

```bash
curl http://mysql.dev
```

또는 전체 이름을 쓴다.

```bash
curl http://mysql.dev.svc.cluster.local
```

정리하면 이렇다.

```text
같은 namespace
→ service_name

다른 namespace
→ service_name.namespace

전체 DNS 이름
→ service_name.namespace.svc.cluster.local
```

---

## 8. Pod DNS 이름 규칙

Service뿐만 아니라 Pod도 DNS 이름을 가질 수 있다.

강의 자료에서는 Pod DNS 이름 형식을 다음처럼 제시한다.

```text
Pod-IP-Address.namespace.pod.cluster.local
```

예를 들어 Pod IP가 `10.40.0.1`이고 namespace가 `default`라면 DNS 이름은 보통 이런 형태로 표현된다.

```text
10-40-0-1.default.pod.cluster.local
```

여기서 IP의 점 `.`은 DNS 이름에서 하이픈 `-`으로 바뀐다.

```text
10.40.0.1
→ 10-40-0-1
```

다만 실무에서는 Pod IP 기반 DNS보다 Service DNS를 더 자주 사용한다.

이유는 간단하다.

```text
Pod IP
→ Pod 재생성 시 바뀔 수 있음

Service DNS
→ Service가 유지되는 동안 안정적
```

그래서 애플리케이션끼리 통신할 때는 보통 Pod DNS보다 Service DNS를 사용한다.

---

## 9. Service와 CoreDNS 동작 흐름

예를 들어 `svc-web` Service가 있다고 하자.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: svc-web
spec:
  clusterIP: 10.96.100.100
  selector:
    app: web
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```

이 Service 뒤에는 `app=web` 라벨을 가진 Pod들이 있다.

```text
svc-web: 10.96.100.100
        ↓
10.40.0.1
10.32.0.2
10.46.0.2
```

Pod 안에서 다음 요청을 보낸다.

```bash
curl http://svc-web.default.svc.cluster.local
```

전체 흐름은 이렇다.

```text
1. Pod가 svc-web.default.svc.cluster.local 조회
2. DNS 요청이 kube-dns Service로 감
3. kube-dns Service 뒤의 CoreDNS Pod가 응답
4. CoreDNS가 svc-web의 ClusterIP 10.96.100.100 반환
5. Pod가 10.96.100.100:80으로 요청
6. Service와 kube-proxy 규칙을 통해 실제 web Pod로 전달
```

즉, DNS는 이름을 Service IP로 바꿔주는 역할이고, 실제 트래픽 분산은 Service와 kube-proxy 쪽에서 처리된다.

---

## 10. Deployment와 Service 예시

강의 자료에는 `web` Deployment와 `svc-web` Service 예시가 나온다.

Deployment는 대략 이런 구조다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      name: nginx-pod
      labels:
        app: web
    spec:
      containers:
        - name: nginx-container
          image: nginx:1.14
```

Service는 이런 형태다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: svc-web
spec:
  clusterIP: 10.96.100.100
  selector:
    app: web
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```

여기서 중요한 연결고리는 label과 selector다.

```text
Pod label
→ app: web

Service selector
→ app: web
```

Service selector가 Pod label과 일치해야 Service가 Pod들을 찾을 수 있다.

```text
svc-web
  ↓
app=web Pod들
```

만약 selector가 잘못되면 Service는 만들어져도 뒤에 연결된 Pod가 없어진다.

확인 명령어는 다음과 같다.

```bash
kubectl get endpoints svc-web
```

또는

```bash
kubectl describe svc svc-web
```

---

## 11. Pod 내부 DNS 설정

Pod 안에서 DNS가 동작하는 이유는 Pod 내부에 DNS 설정이 들어가기 때문이다.

리눅스에서는 DNS 설정을 보통 이 파일에서 확인한다.

```bash
cat /etc/resolv.conf
```

Pod 안에서도 마찬가지다.

```bash
kubectl exec -it <pod-name> -- cat /etc/resolv.conf
```

기본적으로는 이런 형태가 들어간다.

```text
nameserver 10.96.0.10
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

여기서 `nameserver`는 DNS 서버 주소다.

```text
nameserver 10.96.0.10
→ kube-dns Service IP
```

`search`는 짧은 이름으로 질의했을 때 자동으로 붙여볼 도메인 목록이다.

```text
search default.svc.cluster.local svc.cluster.local cluster.local
```

그래서 `svc-web`만 입력해도 내부적으로 여러 후보를 검색할 수 있다.

---

## 12. dnsPolicy

Pod에는 `dnsPolicy`를 설정할 수 있다.

기본값은 보통 `ClusterFirst`다.

```yaml
dnsPolicy: ClusterFirst
```

의미는 이렇다.

```text
클러스터 내부 DNS를 먼저 사용한다
```

그래서 Pod에서 Service 이름을 조회하면 CoreDNS를 통해 클러스터 내부 Service를 찾을 수 있다.

반면 강의 자료의 예시처럼 `dnsPolicy: "None"`을 설정하면 DNS 설정을 직접 지정할 수 있다. 

---

## 13. dnsConfig로 Pod DNS 직접 설정하기

강의 자료에는 Pod의 `/etc/resolv.conf` 구성을 직접 설정하는 예시가 나온다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: dns-example
spec:
  containers:
    - name: test
      image: nginx
  dnsPolicy: "None"
  dnsConfig:
    nameservers:
      - 1.2.3.4
    searches:
      - ns1.svc.cluster-domain.example
      - my.dns.search.suffix
    options:
      - name: ndots
        value: "2"
      - name: edns0
```

이 설정은 Pod의 DNS 설정을 직접 지정한다.

```text
nameservers
→ 사용할 DNS 서버

searches
→ 검색 도메인 목록

options
→ DNS 옵션
```

예를 들어 위 설정에서는 nameserver가 `1.2.3.4`로 들어간다.

```text
nameserver 1.2.3.4
```

검색 도메인은 다음처럼 들어간다.

```text
search ns1.svc.cluster-domain.example my.dns.search.suffix
```

그리고 옵션은 다음과 비슷하게 들어간다.

```text
options ndots:2 edns0
```

즉, `dnsConfig`는 Pod 단위로 DNS 동작을 커스터마이징할 때 사용한다.

---

## 14. ndots란?

DNS 설정에서 자주 보이는 옵션이 `ndots`다.

```text
options ndots:5
```

`ndots`는 도메인 이름 안에 점이 몇 개 이상 있을 때 절대 도메인처럼 먼저 질의할지를 정하는 옵션이다.

예를 들어 `svc-web`은 점이 없다.

```text
svc-web
```

그러면 search domain을 붙여가며 찾는다.

```text
svc-web.default.svc.cluster.local
svc-web.svc.cluster.local
svc-web.cluster.local
```

반면 `svc-web.default.svc.cluster.local`처럼 점이 많은 이름은 전체 도메인으로 바로 질의될 수 있다.

강의 예시에서는 `ndots` 값을 `"2"`로 설정하는 YAML이 나온다.

```yaml
options:
  - name: ndots
    value: "2"
```

즉, DNS 이름 해석 방식을 Pod 단위로 조절할 수 있다.

---

## 15. CoreDNS 확인 명령어

CoreDNS 관련 상태를 확인할 때는 다음 명령어를 자주 쓴다.

```bash
kubectl get svc -A | grep dns
```

kube-dns Service를 확인한다.

```bash
kubectl get pod -A | grep dns
```

CoreDNS Pod가 Running인지 확인한다.

```bash
kubectl get pod -n kube-system -o wide | grep coredns
```

CoreDNS Pod가 어느 Node에서 실행 중인지 확인한다.

```bash
kubectl logs -n kube-system <coredns-pod-name>
```

CoreDNS 로그를 확인한다.

```bash
kubectl describe configmap coredns -n kube-system
```

CoreDNS 설정을 확인한다.

환경에 따라 ConfigMap 이름이 다를 수 있으므로 먼저 확인해도 된다.

```bash
kubectl get configmap -n kube-system | grep dns
```

---

## 16. DNS 테스트용 Pod 만들기

DNS가 정상인지 확인하려면 테스트 Pod를 하나 띄워서 `nslookup`, `curl`을 해보는 방식이 좋다.

```bash
kubectl run dns-test \
  --image=busybox:1.28 \
  --restart=Never \
  -- sleep 3600
```

Pod 안으로 들어간다.

```bash
kubectl exec -it dns-test -- sh
```

Service 이름 조회를 해본다.

```bash
nslookup kubernetes.default
```

특정 Service가 있다면 이렇게 확인한다.

```bash
nslookup svc-web.default.svc.cluster.local
```

또는 짧은 이름으로 확인한다.

```bash
nslookup svc-web
```

HTTP 요청도 확인한다.

```bash
wget -qO- http://svc-web
```

또는 curl이 있는 이미지라면 다음처럼 한다.

```bash
curl http://svc-web
```

---

## 17. DNS 문제 해결 순서

Service 이름으로 접근이 안 될 때는 순서대로 봐야 한다.

### 1단계. Service가 있는지 확인

```bash
kubectl get svc
```

`svc-web` Service가 있는지 확인한다.

---

### 2단계. Service의 ClusterIP 확인

```bash
kubectl get svc svc-web
```

예상 출력은 이런 식이다.

```text
NAME      TYPE        CLUSTER-IP      PORT(S)
svc-web   ClusterIP   10.96.100.100   80/TCP
```

---

### 3단계. Endpoint 확인

Service는 있는데 Endpoint가 비어 있으면 DNS 문제가 아니라 selector 문제일 수 있다.

```bash
kubectl get endpoints svc-web
```

Endpoint가 있어야 한다.

```text
svc-web   10.40.0.1:80,10.32.0.2:80,10.46.0.2:80
```

Endpoint가 없다면 Service selector와 Pod label을 확인한다.

```bash
kubectl describe svc svc-web
kubectl get pods --show-labels
```

---

### 4단계. CoreDNS Pod 확인

```bash
kubectl get pod -n kube-system | grep coredns
```

또는

```bash
kubectl get pod -A | grep dns
```

CoreDNS Pod가 `Running`인지 본다.

---

### 5단계. kube-dns Service 확인

```bash
kubectl get svc -n kube-system kube-dns
```

보통 53번 포트가 열려 있어야 한다.

```text
53/UDP, 53/TCP
```

---

### 6단계. Pod 내부 resolv.conf 확인

```bash
kubectl exec -it <pod-name> -- cat /etc/resolv.conf
```

여기서 nameserver가 kube-dns Service IP를 바라보는지 확인한다.

```text
nameserver 10.96.0.10
```

---

### 7단계. nslookup 테스트

```bash
kubectl exec -it <pod-name> -- nslookup svc-web
```

전체 도메인으로도 테스트한다.

```bash
kubectl exec -it <pod-name> -- nslookup svc-web.default.svc.cluster.local
```

---

## 18. 자주 하는 실수

### 18.1 Service selector와 Pod label이 다름

Service DNS 이름은 정상적으로 해석되더라도, 뒤에 Endpoint가 없으면 실제 통신은 안 된다.

예를 들어 Pod label은 이렇다.

```yaml
labels:
  app: web
```

그런데 Service selector가 이렇게 되어 있으면 문제가 생긴다.

```yaml
selector:
  app: webui
```

이 경우 Service가 Pod를 못 찾는다.

확인은 이렇게 한다.

```bash
kubectl get endpoints
```

Endpoint가 비어 있다면 DNS 문제가 아니라 Service selector 문제일 수 있다.

---

### 18.2 namespace를 잘못 씀

`default` namespace에 있는 Service를 `dev` namespace에서 짧은 이름으로 찾으면 안 될 수 있다.

```bash
curl http://svc-web
```

이 명령은 현재 Pod의 namespace를 기준으로 먼저 찾는다.

다른 namespace에 있는 Service라면 namespace를 붙인다.

```bash
curl http://svc-web.default
```

또는 전체 이름을 쓴다.

```bash
curl http://svc-web.default.svc.cluster.local
```

---

### 18.3 CoreDNS 문제를 애플리케이션 문제로 착각

Pod끼리 IP로는 통신되는데 Service 이름으로만 안 되면 DNS 문제일 수 있다.

```text
Pod IP로 curl 가능
Service 이름으로 curl 불가
→ DNS 또는 Service 설정 문제 의심
```

이때는 CoreDNS와 `/etc/resolv.conf`를 확인해야 한다.

---

### 18.4 dnsPolicy를 None으로 설정해놓고 잊음

`dnsPolicy: None`을 쓰면 기본 클러스터 DNS 설정이 자동으로 들어가지 않는다.

```yaml
dnsPolicy: "None"
```

이 상태에서 `dnsConfig`를 잘못 설정하면 클러스터 내부 Service 이름 해석이 안 될 수 있다.

실습 목적이 아니라면 기본값을 쓰는 게 안전하다.

```yaml
dnsPolicy: ClusterFirst
```

---

## 19. Service DNS 이름 한 번에 정리

```text
service_name.namespace.svc.cluster.local
```

예시:

```text
svc-web.default.svc.cluster.local
```

각 부분의 의미:

```text
svc-web
→ Service 이름

default
→ namespace 이름

svc
→ Service 리소스

cluster.local
→ 클러스터 내부 도메인
```

짧게 쓰는 방식:

```text
svc-web
→ 같은 namespace에서 사용 가능

svc-web.default
→ default namespace의 svc-web

svc-web.default.svc.cluster.local
→ 전체 DNS 이름
```

---

## 20. Pod DNS 이름 한 번에 정리

Pod DNS 이름은 다음 형식을 가진다.

```text
Pod-IP-Address.namespace.pod.cluster.local
```

예시:

```text
10-40-0-1.default.pod.cluster.local
```

각 부분의 의미:

```text
10-40-0-1
→ Pod IP 10.40.0.1을 DNS 이름 형태로 변환

default
→ namespace

pod
→ Pod 리소스

cluster.local
→ 클러스터 내부 도메인
```

하지만 실무에서는 Pod DNS보다 Service DNS를 더 많이 사용한다.

```text
Pod DNS
→ Pod 단위 접근

Service DNS
→ 안정적인 서비스 단위 접근
```

---

## 21. 전체 흐름 정리

쿠버네티스 DNS 동작 흐름은 이렇게 볼 수 있다.

```text
Pod에서 요청 발생
  ↓
curl http://svc-web.default.svc.cluster.local
  ↓
Pod의 /etc/resolv.conf 확인
  ↓
nameserver 10.96.0.10으로 DNS 질의
  ↓
kube-dns Service
  ↓
CoreDNS Pod
  ↓
svc-web Service의 ClusterIP 응답
  ↓
Pod가 ClusterIP로 실제 HTTP 요청
  ↓
Service와 kube-proxy를 통해 backend Pod로 전달
```

즉, DNS는 트래픽을 직접 전달하는 게 아니다.

```text
DNS
→ 이름을 IP로 바꿔줌

Service/kube-proxy
→ 실제 트래픽을 Pod로 전달
```

---

## 22. 정리

쿠버네티스 DNS는 클러스터 내부에서 Service와 Pod를 이름으로 찾을 수 있게 해주는 기능이다.

핵심은 다음과 같다.

```text
CoreDNS
→ 쿠버네티스 내부 DNS 서버 역할

kube-dns Service
→ CoreDNS Pod 앞에 있는 DNS Service

Service DNS
→ service_name.namespace.svc.cluster.local

Pod DNS
→ Pod-IP-Address.namespace.pod.cluster.local

/etc/resolv.conf
→ Pod 내부 DNS 설정 파일

dnsPolicy
→ Pod가 어떤 DNS 정책을 쓸지 결정

dnsConfig
→ Pod DNS 설정을 직접 커스터마이징
```

마지막으로 이렇게 기억하면 된다.

> 쿠버네티스 DNS는 Pod가 IP를 외우지 않고 Service 이름으로 통신하게 해주는 내부 이름표 시스템이다. CoreDNS가 이름을 ClusterIP로 바꿔주고, 실제 트래픽은 Service와 kube-proxy를 거쳐 Pod로 전달된다.
