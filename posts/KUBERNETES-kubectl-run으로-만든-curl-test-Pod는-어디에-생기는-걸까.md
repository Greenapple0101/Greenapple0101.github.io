---
title: "[KUBERNETES] kubectl run으로 만든 curl-test Pod는 어디에 생기는 걸까?"
source: "https://velog.io/@yorange50/KUBERNETES-kubectl-run으로-만든-curl-test-Pod는-어디에-생기는-걸까"
published: "2026-05-19T03:38:11.599Z"
tags: ""
backup_date: "2026-05-29T14:52:52.728052"
---

Kubernetes에서 `ClusterIP`를 테스트하다 보면 이런 명령어를 자주 쓰게 된다.

```bash
kubectl run curl-test --image=curlimages/curl -it --rm -- sh
```

처음 보면 이런 생각이 든다.

> 이게 대체 어디에 설치되는 거지?
> 내 로컬에 curl을 까는 건가?
> 아니면 Kubernetes 클러스터 안에 들어가는 건가?
> 만약 클러스터가 여러 개면 어디에 생기는 거지?

이번 글에서는 이 명령어가 정확히 어떤 의미인지 정리해보려고 한다.

---

## 1. ClusterIP는 클러스터 내부 전용 IP다

Kubernetes Service에는 여러 타입이 있다.

대표적으로 다음 세 가지가 있다.

```text
ClusterIP
NodePort
LoadBalancer
```

이 중 `ClusterIP`는 기본 Service 타입이다.

예를 들어 Service를 조회했을 때 다음과 같이 나온다고 해보자.

```bash
kubectl get svc
```

```text
NAME             TYPE        CLUSTER-IP      PORT(S)
my-app-service   ClusterIP   10.43.188.207   8080/TCP
```

여기서 `10.43.188.207`이 바로 ClusterIP다.

하지만 이 IP는 내 맥북이나 윈도우 브라우저에서 바로 접근하는 IP가 아니다.

```bash
curl http://10.43.188.207
```

이 명령을 로컬 PC에서 실행하면 안 될 수 있다.

왜냐하면 ClusterIP는 Kubernetes 클러스터 내부에서만 통하는 가상 IP이기 때문이다.

즉, 접근 가능한 위치는 이런 곳이다.

```text
같은 클러스터 안의 Pod
같은 클러스터 안의 Node
클러스터 내부 네트워크에 붙어 있는 환경
```

반대로 이런 곳에서는 보통 직접 접근할 수 없다.

```text
내 로컬 PC
다른 Kubernetes 클러스터
외부 인터넷
```

---

## 2. 그래서 테스트용 Pod를 만든다

ClusterIP가 클러스터 내부에서만 접근 가능하다면, 테스트도 클러스터 내부에서 해야 한다.

그때 사용하는 명령어가 이것이다.

```bash
kubectl run curl-test --image=curlimages/curl -it --rm -- sh
```

이 명령어는 한 문장으로 말하면 다음과 같다.

> 현재 kubectl이 바라보고 있는 Kubernetes 클러스터 안에 curl이 설치된 임시 Pod를 만들고, 그 안의 shell로 바로 접속하는 명령어

즉, 내 로컬 PC에 curl을 설치하는 것이 아니다.

Kubernetes 클러스터 내부에 임시 컨테이너를 하나 띄우는 것이다.

---

## 3. 명령어 하나씩 쪼개보기

```bash
kubectl run curl-test --image=curlimages/curl -it --rm -- sh
```

하나씩 보면 다음과 같다.

```text
kubectl run curl-test
```

`curl-test`라는 이름의 Pod를 생성한다.

```text
--image=curlimages/curl
```

`curlimages/curl`이라는 컨테이너 이미지를 사용한다.

이 이미지는 curl 명령어가 이미 들어 있는 이미지다.

그래서 컨테이너 안에서 바로 `curl`을 사용할 수 있다.

```text
-it
```

터미널로 직접 들어가서 명령어를 입력할 수 있게 한다.

즉, 대화형 모드로 실행한다는 뜻이다.

```text
--rm
```

shell에서 빠져나오면 Pod를 자동으로 삭제한다.

임시 테스트용 Pod이기 때문에 사용이 끝나면 남겨둘 필요가 없다.

```text
-- sh
```

컨테이너 안에서 `sh` shell을 실행한다.

그래서 명령어를 실행하면 바로 컨테이너 내부 shell로 들어간 것처럼 보인다.

---

## 4. 실제 흐름

명령어를 실행하면 내부적으로는 이런 흐름으로 동작한다.

```text
사용자
  ↓
kubectl run 명령 실행
  ↓
Kubernetes API Server에 Pod 생성 요청
  ↓
클러스터의 Node가 curlimages/curl 이미지 pull
  ↓
curl-test Pod 실행
  ↓
kubectl이 해당 Pod의 sh에 터미널 연결
```

그래서 사용자는 마치 바로 컨테이너 안으로 들어간 것처럼 보게 된다.

실제로는 Kubernetes 클러스터 안에 Pod가 하나 생성되고, 그 Pod의 shell에 접속한 것이다.

---

## 5. 그럼 이 Pod는 어느 클러스터에 생길까?

가장 중요한 부분이다.

`kubectl run`으로 만든 Pod는 **현재 kubectl이 바라보고 있는 클러스터**에 생성된다.

현재 연결된 클러스터는 다음 명령어로 확인할 수 있다.

```bash
kubectl config current-context
```

예를 들어 결과가 이렇게 나오면:

```text
k3d-my-cluster
```

방금 실행한 명령어는 `k3d-my-cluster` 안에 Pod를 만든 것이다.

```bash
kubectl run curl-test --image=curlimages/curl -it --rm -- sh
```

즉, 이 명령의 의미는 다음과 같다.

```text
k3d-my-cluster 안에
curl-test라는 임시 Pod를 만들고
그 안으로 접속한다
```

---

## 6. 클러스터가 하나만 있다면?

현재 내 환경에 클러스터가 `my-cluster` 하나만 있다면 단순하다.

```text
현재 클러스터 = my-cluster
kubectl run 실행
curl-test Pod 생성 위치 = my-cluster 내부
```

그래서 `curl-test` Pod 안에서 다음 명령어를 실행하면:

```bash
curl http://10.43.188.207
```

같은 클러스터 내부의 ClusterIP에 접근할 수 있다.

구조는 이렇게 된다.

```text
my-cluster
├─ my-app Pod
├─ my-app Service
│   └─ ClusterIP: 10.43.188.207
└─ curl-test Pod
    └─ curl http://10.43.188.207 가능
```

둘 다 같은 클러스터 안에 있기 때문에 ClusterIP 접근이 가능하다.

---

## 7. 만약 클러스터가 여러 개라면?

Kubernetes에서는 클러스터를 여러 개 사용할 수 있다.

예를 들어 로컬에 다음과 같은 클러스터들이 있을 수 있다.

```text
k3d-dev
k3d-prod
```

현재 context를 확인하면 다음처럼 나올 수 있다.

```bash
kubectl config get-contexts
```

```text
CURRENT   NAME
*         k3d-dev
          k3d-prod
```

여기서 `*`가 붙은 것이 현재 kubectl이 바라보고 있는 클러스터다.

이 상태에서 다음 명령어를 실행하면:

```bash
kubectl run curl-test --image=curlimages/curl -it --rm -- sh
```

`curl-test` Pod는 `k3d-dev` 클러스터에 생성된다.

`k3d-prod`에 생성되는 것이 아니다.

즉, `kubectl`은 항상 현재 context 기준으로 동작한다.

```text
현재 context = k3d-dev
kubectl run 실행
curl-test Pod = k3d-dev에 생성
```

---

## 8. 다른 클러스터의 ClusterIP에는 접근할 수 있을까?

기본적으로는 접근할 수 없다.

예를 들어 다음과 같은 상황이라고 해보자.

```text
Cluster A
├─ Service A
└─ ClusterIP: 10.43.188.207

Cluster B
└─ curl-test Pod
```

`curl-test` Pod가 Cluster B에 있다면, Cluster A의 ClusterIP인 `10.43.188.207`에는 보통 접근할 수 없다.

왜냐하면 ClusterIP는 클러스터 내부에서만 통하는 IP이기 때문이다.

각 클러스터는 자기만의 네트워크를 가진다.

```text
Cluster A 내부 네트워크
Cluster B 내부 네트워크
```

이 둘은 기본적으로 서로 분리되어 있다.

그래서 ClusterIP는 이렇게 이해하면 된다.

```text
ClusterIP = 같은 클러스터 안에서만 통하는 서비스 주소
```

---

## 9. 다른 클러스터에 Pod를 만들고 싶다면?

현재 context를 바꾸면 된다.

예를 들어 현재 `k3d-dev`를 보고 있는데, `k3d-prod`로 바꾸고 싶다면:

```bash
kubectl config use-context k3d-prod
```

그 후 다시 확인한다.

```bash
kubectl config current-context
```

```text
k3d-prod
```

이제 이 상태에서 명령어를 실행하면:

```bash
kubectl run curl-test --image=curlimages/curl -it --rm -- sh
```

`curl-test` Pod는 `k3d-prod` 클러스터에 생성된다.

그래서 실무에서는 `apply`, `delete`, `run` 같은 명령어를 치기 전에 현재 context를 꼭 확인하는 습관이 중요하다.

```bash
kubectl config current-context
```

왜냐하면 dev 클러스터인 줄 알고 명령어를 쳤는데, 실제로는 prod 클러스터를 바라보고 있으면 사고가 날 수 있기 때문이다.

---

## 10. 앱 컨테이너에 curl이 없을 수도 있다

Pod 안에 들어가서 다음 명령어를 실행했는데:

```bash
curl http://10.43.188.207
```

이런 에러가 날 수 있다.

```bash
bash: curl: command not found
```

이건 이상한 게 아니다.

해당 컨테이너 이미지 안에 curl이 설치되어 있지 않다는 뜻이다.

운영용 애플리케이션 이미지는 보통 가볍게 만들기 위해 불필요한 도구를 많이 빼둔다.

그래서 앱 컨테이너 안에는 `curl`, `vim`, `ping`, `netstat` 같은 도구가 없을 수 있다.

이럴 때 앱 컨테이너에 억지로 curl을 설치하기보다는, 디버깅용 Pod를 따로 띄우는 방식이 더 깔끔하다.

```bash
kubectl run curl-test --image=curlimages/curl -it --rm -- sh
```

그리고 그 안에서 테스트한다.

```bash
curl http://10.43.188.207
```

---

## 11. 정리

`kubectl run curl-test --image=curlimages/curl -it --rm -- sh`는 로컬 PC에 뭔가를 설치하는 명령이 아니다.

현재 kubectl이 바라보고 있는 Kubernetes 클러스터 안에 임시 테스트용 Pod를 생성하는 명령이다.

정리하면 다음과 같다.

```text
ClusterIP
= 같은 클러스터 내부에서만 접근 가능한 Service IP

kubectl run curl-test
= 현재 context의 클러스터 안에 임시 Pod 생성

curlimages/curl
= curl이 설치되어 있는 테스트용 컨테이너 이미지

-it
= 터미널로 직접 접속

--rm
= 종료하면 Pod 자동 삭제

-- sh
= 컨테이너 안에서 shell 실행
```

결국 중요한 핵심은 이것이다.

```text
kubectl은 현재 context가 가리키는 클러스터에 명령을 실행한다.
```

그래서 ClusterIP를 테스트할 때는 같은 클러스터 안에 임시 Pod를 만들고, 그 Pod 안에서 curl을 날리면 된다.

```bash
kubectl run curl-test --image=curlimages/curl -it --rm -- sh
```

```bash
curl http://10.43.188.207
```

이렇게 하면 클러스터 내부에서 Service가 정상적으로 연결되는지 확인할 수 있다.
