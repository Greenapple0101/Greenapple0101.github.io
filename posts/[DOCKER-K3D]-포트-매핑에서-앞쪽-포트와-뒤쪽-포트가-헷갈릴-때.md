---
title: "[DOCKER/K3D] 포트 매핑에서 앞쪽 포트와 뒤쪽 포트가 헷갈릴 때"
source: "https://velog.io/@yorange50/DOCKERK3D-포트-매핑에서-앞쪽-포트와-뒤쪽-포트가-헷갈릴-때"
published: "2026-05-19T04:50:03.833Z"
tags: ""
backup_date: "2026-05-29T14:52:52.725197"
---

Docker나 k3d를 쓰다 보면 이런 문법을 자주 본다.

```bash
docker run -p 8080:80 nginx
```

또는 k3d에서는 이런 식으로 쓴다.

```bash
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "30001:30001@loadbalancer"
```

처음 보면 제일 헷갈리는 부분은 이거다.

```text
8080:80
30001:30001
```

포트가 두 개 나오는데, 앞쪽 포트가 뭔지, 뒤쪽 포트가 뭔지 잘 안 와닿는다.

이번 글에서는 이걸 정말 쉽게 정리해보려고 한다.

## 1. 제일 먼저 외울 공식

포트 매핑은 이렇게 읽으면 된다.

```text
앞쪽 포트 : 뒤쪽 포트

내가 접속하는 포트 : 실제 내부 서비스가 열려 있는 포트
밖에서 보이는 포트 : 안에서 기다리는 포트
Host 포트 : Container 포트
```

예를 들어:

```bash
docker run -p 8080:80 nginx
```

이건 이렇게 읽으면 된다.

```text
내 컴퓨터의 8080번 포트로 들어온 요청을
nginx 컨테이너 안의 80번 포트로 보내라
```

즉, 접속은 이렇게 한다.

```bash
curl localhost:8080
```

하지만 실제 nginx는 컨테이너 안에서 `80`번 포트로 요청을 받고 있다.

그림으로 보면 이렇다.

```text
내 Mac
localhost:8080
     ↓
Docker 포트 매핑
     ↓
nginx 컨테이너
80번 포트
```

## 2. 앞쪽 포트는 내가 치는 포트다

가장 중요한 건 이거다.

```text
앞쪽 포트 = 내가 브라우저나 curl로 접속하는 포트
```

예를 들어:

```bash
-p 8080:80
```

이면 나는 이렇게 접속한다.

```bash
curl localhost:8080
```

앞쪽이 `8080`이니까 `localhost:8080`으로 들어간다.

반대로 이렇게 쓰면:

```bash
-p 3000:80
```

접속은 이렇게 한다.

```bash
curl localhost:3000
```

앞쪽이 `3000`이기 때문이다.

즉, 내가 직접 입력하는 포트는 항상 앞쪽 포트다.

```text
-p 8080:80  →  localhost:8080 으로 접속
-p 3000:80  →  localhost:3000 으로 접속
-p 9999:80  →  localhost:9999 으로 접속
```

## 3. 뒤쪽 포트는 컨테이너 안에서 실제로 열려 있는 포트다

그럼 뒤쪽 포트는 뭘까?

```text
뒤쪽 포트 = 컨테이너 안에서 실제 서비스가 기다리고 있는 포트
```

nginx는 보통 컨테이너 안에서 `80`번 포트로 떠 있다.

그래서 Docker에서 nginx를 띄울 때 보통 이렇게 쓴다.

```bash
docker run -p 8080:80 nginx
```

여기서 뒤쪽 `80`은 nginx가 컨테이너 내부에서 실제로 사용하고 있는 포트다.

내가 밖에서 `8080`으로 들어가면 Docker가 그 요청을 컨테이너 안의 `80`으로 넘겨준다.

```text
localhost:8080
     ↓
container:80
```

즉, 밖에서는 `8080`으로 보이지만, 안에서는 `80`으로 받는 것이다.

## 4. 택배 비유로 이해하기

포트 매핑은 택배 주소처럼 생각하면 쉽다.

```text
앞쪽 포트 = 아파트 정문 번호
뒤쪽 포트 = 실제 집 호수
```

예를 들어:

```bash
-p 8080:80
```

은 이런 느낌이다.

```text
택배 기사가 8080번 정문으로 들어온다.
경비실이 그 택배를 안쪽 80번 집으로 전달한다.
```

외부 사람은 내부 구조를 몰라도 된다.

그냥 `8080`번 문으로 들어오면 된다.

그러면 Docker가 알아서 컨테이너 안의 `80`번 포트로 보내준다.

```text
외부 사람 입장 → localhost:8080만 알면 됨
컨테이너 입장 → 나는 80번 포트에서 기다리고 있음
```

## 5. 왜 굳이 포트를 다르게 쓰는 걸까?

이런 생각이 들 수 있다.

> nginx가 80번이면 그냥 80:80으로 하면 되는 거 아닌가?

가능하다.

```bash
docker run -p 80:80 nginx
```

이렇게 하면:

```text
내 컴퓨터 80번 포트
     ↓
nginx 컨테이너 80번 포트
```

가 된다.

그러면 접속은 이렇게 한다.

```bash
curl localhost
```

또는:

```bash
curl localhost:80
```

그런데 보통 개발할 때는 `8080:80`처럼 다르게 많이 쓴다.

이유는 내 컴퓨터의 80번 포트가 이미 다른 프로그램이 쓰고 있을 수도 있고, 80번 포트를 쓰려면 권한 문제가 생길 수도 있기 때문이다.

그래서 밖에서는 `8080`을 쓰고, 안에서는 nginx 기본 포트인 `80`으로 연결한다.

```text
밖에서는 8080
안에서는 80
```

이렇게 생각하면 된다.

## 6. k3d에서는 어떻게 봐야 할까?

k3d에서 이런 명령을 썼다고 하자.

```bash
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "30001:30001@loadbalancer"
```

여기서도 원리는 똑같다.

```text
앞쪽 30001 = 내 Mac에서 접속할 포트
뒤쪽 30001 = k3d loadbalancer 컨테이너 안으로 넘길 포트
```

즉:

```text
Mac localhost:30001
        ↓
k3d loadbalancer container:30001
        ↓
Kubernetes NodePort 30001
        ↓
nginx-svc
        ↓
nginx Pod:80
```

그래서 Mac에서는 이렇게 접속한다.

```bash
curl localhost:30001
```

여기서도 내가 직접 치는 건 앞쪽 포트다.

```text
--port "30001:30001@loadbalancer"

앞쪽 30001 → 내가 접속하는 포트
뒤쪽 30001 → k3d 내부로 넘겨지는 포트
```

## 7. 꼭 앞뒤 포트가 같아야 할까?

아니다.

꼭 같을 필요는 없다.

예를 들어 이렇게 써도 된다.

```bash
k3d cluster create my-cluster \
  --servers 1 \
  --agents 2 \
  --port "8080:30001@loadbalancer"
```

이건 이렇게 읽는다.

```text
내 Mac의 8080번 포트로 들어온 요청을
k3d 내부의 30001번 포트로 보내라
```

그러면 접속은 이렇게 해야 한다.

```bash
curl localhost:8080
```

왜냐하면 앞쪽 포트가 `8080`이기 때문이다.

전체 흐름은 이렇게 된다.

```text
Mac localhost:8080
        ↓
k3d 내부 30001
        ↓
Kubernetes NodePort 30001
        ↓
nginx-svc
        ↓
nginx Pod:80
```

즉, 뒤쪽 포트는 실제 내부에서 열려 있는 포트와 맞아야 한다.

하지만 앞쪽 포트는 내가 편한 포트로 바꿀 수 있다.

```text
--port "30001:30001@loadbalancer"
→ localhost:30001로 접속

--port "8080:30001@loadbalancer"
→ localhost:8080으로 접속

--port "9999:30001@loadbalancer"
→ localhost:9999로 접속
```

## 8. NodePort와 포트 매핑을 같이 보면 더 헷갈린다

Kubernetes Service를 보면 이런 식으로 나온다.

```bash
kubectl get svc nginx-svc
```

```text
NAME        TYPE       CLUSTER-IP      PORT(S)
nginx-svc   NodePort   10.43.188.207   80:30001/TCP
```

여기서도 포트가 두 개 나온다.

```text
80:30001
```

이건 Docker 포트 매핑의 `앞:뒤`랑 같은 의미로 보면 안 된다.

Kubernetes Service에서:

```text
80:30001/TCP
```

은 보통 이렇게 이해하면 된다.

```text
Service 내부 포트 = 80
NodePort 외부 포트 = 30001
```

즉:

```text
클러스터 안에서는 nginx-svc:80
클러스터 밖에서는 NodeIP:30001
```

그런데 k3d에서는 Node IP로 바로 접근이 어려울 수 있으니까, 추가로 k3d 포트 매핑을 해준다.

```bash
--port "30001:30001@loadbalancer"
```

그러면 최종적으로 Mac에서 이렇게 접근할 수 있다.

```bash
curl localhost:30001
```

전체 흐름을 한 번에 보면 이렇다.

```text
Mac localhost:30001
        ↓
k3d 포트 매핑
        ↓
k3d loadbalancer:30001
        ↓
Kubernetes NodePort:30001
        ↓
nginx-svc Service:80
        ↓
nginx Pod:80
```

## 9. 가장 헷갈리는 포인트 정리

### Docker 포트 매핑

```bash
-p 8080:80
```

의미:

```text
localhost:8080 → container:80
```

접속:

```bash
curl localhost:8080
```

### k3d 포트 매핑

```bash
--port "8080:30001@loadbalancer"
```

의미:

```text
localhost:8080 → k3d 내부 30001
```

접속:

```bash
curl localhost:8080
```

### Kubernetes NodePort

```text
80:30001/TCP
```

의미:

```text
Service 80번 포트가 NodePort 30001번으로 외부에 노출됨
```

접속 방식:

```bash
curl NodeIP:30001
```

단, k3d에서는 Node IP가 Docker 내부 IP라서 Mac에서 바로 안 될 수 있다.

그래서:

```bash
--port "30001:30001@loadbalancer"
```

로 열고:

```bash
curl localhost:30001
```

로 접근한다.

## 10. 진짜 쉽게 외우기

포트 매핑에서 이것만 기억하면 된다.

```text
앞쪽 포트는 내가 치는 포트
뒤쪽 포트는 안에서 실제로 열려 있는 포트
```

예를 들어:

```bash
-p 8080:80
```

이면:

```text
나는 localhost:8080으로 접속한다.
Docker는 그걸 container:80으로 보내준다.
```

```bash
--port "8080:30001@loadbalancer"
```

이면:

```text
나는 localhost:8080으로 접속한다.
k3d는 그걸 내부 30001로 보내준다.
```

```bash
--port "30001:30001@loadbalancer"
```

이면:

```text
나는 localhost:30001로 접속한다.
k3d도 내부 30001로 보내준다.
```

## 11. 정리

포트 매핑은 외부 포트와 내부 포트를 연결하는 작업이다.

```text
외부 포트:내부 포트
```

Docker에서는:

```bash
-p 8080:80
```

```text
내 컴퓨터 8080 → 컨테이너 80
```

k3d에서는:

```bash
--port "30001:30001@loadbalancer"
```

```text
내 Mac 30001 → k3d 내부 30001
```

Kubernetes NodePort까지 같이 보면 최종 흐름은 이렇게 된다.

```text
Mac localhost:30001
        ↓
k3d 포트 매핑
        ↓
k3d loadbalancer:30001
        ↓
Kubernetes NodePort:30001
        ↓
nginx-svc Service:80
        ↓
nginx Pod:80
```

한 문장으로 정리하면 다음과 같다.

```text
앞쪽 포트는 내가 밖에서 접속하는 문이고, 뒤쪽 포트는 안에서 실제 서비스가 기다리고 있는 문이다.
```
