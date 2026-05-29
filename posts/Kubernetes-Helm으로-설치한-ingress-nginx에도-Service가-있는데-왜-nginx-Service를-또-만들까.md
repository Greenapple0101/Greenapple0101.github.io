---
title: "[Kubernetes] Helm으로 설치한 ingress-nginx에도 Service가 있는데, 왜 nginx Service를 또 만들까?"
source: "https://velog.io/@yorange50/Kubernetes-Helm으로-설치한-ingress-nginx에도-Service가-있는데-왜-nginx-Service를-또-만들까"
published: "2026-05-13T06:48:16.759Z"
tags: ""
backup_date: "2026-05-29T14:52:52.745008"
---

Kubernetes에서 Ingress를 실습하다 보면 처음에 많이 헷갈리는 부분이 있다.

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

이렇게 Helm으로 `ingress-nginx`를 설치했는데, 이후에 또 이런 명령어를 친다.

```bash
kubectl expose deployment nginx --port=80 --target-port=80
```

처음 보면 이런 생각이 든다.

> 어? Helm으로 ingress-nginx 설치할 때 Service가 이미 생긴 거 아니야?
> 근데 왜 또 Service를 만드는 거지?
> 원래 있던 Service를 노출시키는 건가?
> 아니면 새로운 Service를 만드는 건가?

결론부터 말하면 이렇다.

> Helm으로 설치한 ingress-nginx에도 Service는 있다.
> 하지만 그 Service는 Ingress Controller용 Service이고, `kubectl expose deployment nginx`로 만드는 Service는 내가 만든 nginx 앱용 Service다.

즉, **둘 다 Service는 맞지만 역할이 다르다.**

---

# 1. 먼저 Helm으로 ingress-nginx를 설치한다

Ingress Controller를 설치할 때 보통 아래 명령어를 사용한다.

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

이 명령어는 `ingress-nginx`라는 Helm chart를 설치한다.

설치 결과로 보통 이런 리소스들이 생성된다.

```text
Namespace
- ingress-nginx

Deployment
- ingress-nginx-controller

Pod
- ingress-nginx-controller-xxxxx

Service
- ingress-nginx-controller
- ingress-nginx-controller-admission

ConfigMap
- ingress-nginx-controller

Job
- ingress-nginx-admission-create
- ingress-nginx-admission-patch
```

여기서 중요한 것은 이거다.

```text
ingress-nginx-controller Service
```

Helm으로 설치했을 때 이미 Service가 생긴다.

확인하려면 이렇게 보면 된다.

```bash
kubectl get svc -n ingress-nginx
```

그러면 대략 이런 식으로 나온다.

```text
NAME                                 TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)
ingress-nginx-controller             LoadBalancer   10.x.x.x        <pending>     80:xxxxx/TCP,443:xxxxx/TCP
ingress-nginx-controller-admission   ClusterIP      10.x.x.x        <none>        443/TCP
```

즉, Helm으로 설치한 리소스 안에도 Service는 있다.

---

# 2. 그런데 이 Service는 누구를 위한 Service일까?

Helm으로 설치된 `ingress-nginx-controller` Service는 **Ingress Controller Pod로 들어가는 입구**다.

구조로 보면 이렇다.

```text
외부 요청
   ↓
ingress-nginx-controller Service
   ↓
ingress-nginx-controller Pod
```

여기서 `ingress-nginx-controller Pod`가 바로 실제로 Ingress 규칙을 읽고 요청을 라우팅하는 애다.

즉, Helm으로 설치된 Service의 역할은 다음과 같다.

```text
ingress-nginx-controller Service
= 외부 요청을 받는 입구
= Ingress Controller Pod로 요청을 전달하는 Service
```

이 Service는 **내가 만든 nginx 웹서버 Pod로 바로 보내는 Service가 아니다.**

---

# 3. Ingress Controller와 nginx 앱은 다르다

여기서 이름 때문에 헷갈리기 쉽다.

`ingress-nginx`에도 nginx라는 이름이 들어가고, 우리가 테스트용으로 만든 앱도 `nginx`다.

하지만 둘은 완전히 다른 존재다.

```text
ingress-nginx
= Ingress Controller
= 요청을 받아서 어디로 보낼지 판단하는 라우터 역할

nginx
= 테스트용 웹서버 애플리케이션
= 실제 HTML 응답을 돌려주는 앱
```

즉, `ingress-nginx`는 교통정리하는 애고, `nginx`는 실제 목적지 앱이다.

비유하면 이렇다.

```text
ingress-nginx-controller
= 안내 데스크

nginx 앱
= 실제 사무실

ingress-nginx-controller Service
= 안내 데스크로 들어가는 입구

nginx Service
= 실제 사무실로 들어가는 내부 입구
```

---

# 4. 테스트용 nginx Deployment를 만든다

Ingress 실습을 하려면 실제 요청을 받을 애플리케이션이 필요하다.

그래서 테스트용 nginx Deployment를 만든다.

```bash
kubectl create deployment nginx --image=nginx
```

이 명령어를 치면 Kubernetes가 nginx 이미지를 가져와서 Pod 안에 실행한다.

생성 흐름은 이렇다.

```text
Deployment nginx
   ↓
ReplicaSet
   ↓
Pod nginx-xxxxx
   ↓
nginx 컨테이너 실행
```

여기까지 하면 nginx Pod는 떠 있다.

확인해보면:

```bash
kubectl get pods
```

대략 이런 식으로 나온다.

```text
NAME                     READY   STATUS    RESTARTS   AGE
nginx-7854ff8877-abcde   1/1     Running   0          1m
```

하지만 아직 문제가 있다.

Pod는 떠 있지만, Pod는 언제든 이름이 바뀔 수 있고 IP도 바뀔 수 있다.

그래서 Pod 앞에 고정된 입구가 필요하다.

그게 바로 Service다.

---

# 5. 그래서 nginx 앱용 Service를 새로 만든다

이때 사용하는 명령어가 이거다.

```bash
kubectl expose deployment nginx --port=80 --target-port=80
```

이 명령어는 기존 Helm Service를 수정하는 게 아니다.

새로운 Service를 만든다.

정확히 말하면:

```text
nginx Deployment가 관리하는 Pod들을 찾아서,
그 앞에 nginx라는 Service를 만들어줘.
Service의 포트는 80이고,
Pod 안 컨테이너의 80번 포트로 보내줘.
```

라는 뜻이다.

명령어 실행 후 확인해보면:

```bash
kubectl get svc
```

이런 Service가 생긴다.

```text
NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)
kubernetes   ClusterIP   10.96.0.1       <none>        443/TCP
nginx        ClusterIP   10.96.x.x       <none>        80/TCP
```

여기서 새로 생긴 게 이거다.

```text
nginx Service
```

이 Service는 `nginx Pod`로 가는 고정 입구다.

```text
nginx Service
   ↓
nginx Pod
```

---

# 6. 그럼 Service가 두 개라는 뜻인가?

맞다.

Ingress 실습에서는 보통 Service가 최소 두 종류 나온다.

첫 번째는 Ingress Controller용 Service다.

```text
ingress-nginx-controller Service
```

얘는 Helm으로 설치된다.

역할은:

```text
외부 요청을 Ingress Controller Pod로 전달
```

두 번째는 애플리케이션용 Service다.

```text
nginx Service
```

얘는 `kubectl expose deployment nginx`로 만든다.

역할은:

```text
Ingress Controller가 nginx Pod로 요청을 넘길 수 있게 하는 내부 입구
```

둘을 나란히 보면 이렇다.

```text
ingress-nginx-controller Service
= Ingress Controller로 들어가는 입구

nginx Service
= nginx 앱 Pod로 들어가는 입구
```

---

# 7. 전체 요청 흐름

Ingress까지 연결하면 전체 흐름은 이렇게 된다.

```text
사용자 요청
   ↓
ingress-nginx-controller Service
   ↓
ingress-nginx-controller Pod
   ↓
Ingress 리소스 규칙 확인
   ↓
nginx Service
   ↓
nginx Pod
   ↓
nginx 컨테이너
```

여기서 각각의 역할을 다시 정리하면 다음과 같다.

```text
사용자 요청
= 브라우저나 curl로 들어오는 요청

ingress-nginx-controller Service
= 외부 요청이 Ingress Controller로 들어가는 입구

ingress-nginx-controller Pod
= Ingress 규칙을 읽고 라우팅하는 실제 컨트롤러

Ingress 리소스
= 어떤 host/path 요청을 어떤 Service로 보낼지 적어둔 규칙

nginx Service
= nginx Pod로 가는 고정 입구

nginx Pod
= 실제 nginx 웹서버가 실행되는 공간

nginx 컨테이너
= 실제 응답을 생성하는 웹서버 애플리케이션
```

---

# 8. Ingress 리소스는 nginx Service를 바라본다

Ingress 리소스는 보통 이런 식으로 작성한다.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
spec:
  ingressClassName: nginx
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx
            port:
              number: 80
```

여기서 중요한 부분은 이거다.

```yaml
backend:
  service:
    name: nginx
    port:
      number: 80
```

Ingress는 Pod를 직접 바라보지 않는다.

Ingress는 Service를 바라본다.

즉, Ingress Controller는 요청을 받으면 이 규칙을 보고 이렇게 판단한다.

```text
/ 로 들어온 요청은 nginx Service로 보내야겠구나.
```

그리고 `nginx Service`는 다시 nginx Pod로 요청을 넘긴다.

```text
Ingress Controller
   ↓
nginx Service
   ↓
nginx Pod
```

---

# 9. 왜 Ingress가 Pod를 직접 바라보지 않을까?

Pod는 불안정한 존재다.

Pod는 죽었다가 다시 뜰 수 있고, 새로 뜨면 이름과 IP가 바뀔 수 있다.

예를 들어 지금은 Pod가 이렇게 떠 있을 수 있다.

```text
nginx-7854ff8877-abcde
```

그런데 재배포하면 이렇게 바뀔 수 있다.

```text
nginx-7854ff8877-zxywv
```

IP도 바뀔 수 있다.

그래서 Ingress가 Pod를 직접 바라보면 안정적이지 않다.

반대로 Service는 고정된 이름을 가진다.

```text
nginx
```

그래서 Ingress는 Pod가 아니라 Service를 바라본다.

```text
Ingress
   ↓
Service
   ↓
Pod
```

이 구조 덕분에 Pod가 바뀌어도 Ingress 설정은 그대로 유지된다.

---

# 10. 명령어별 역할 정리

전체 명령어를 순서대로 보면 더 명확하다.

## 1단계: Ingress Controller 설치

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

이 명령어는 Ingress Controller를 설치한다.

생기는 주요 리소스는 다음과 같다.

```text
ingress-nginx-controller Deployment
ingress-nginx-controller Pod
ingress-nginx-controller Service
```

여기서 Service는 Ingress Controller용 Service다.

---

## 2단계: 테스트용 nginx 앱 생성

```bash
kubectl create deployment nginx --image=nginx
```

이 명령어는 테스트용 nginx 앱을 실행한다.

생기는 구조는 다음과 같다.

```text
Deployment nginx
   ↓
ReplicaSet
   ↓
Pod nginx-xxxxx
```

하지만 아직 Service는 없다.

---

## 3단계: nginx 앱 앞에 Service 생성

```bash
kubectl expose deployment nginx --port=80 --target-port=80
```

이 명령어는 nginx Deployment 앞에 Service를 새로 만든다.

생기는 구조는 다음과 같다.

```text
Service nginx
   ↓
Pod nginx-xxxxx
```

즉, 이 명령어는 Helm으로 설치한 Service를 노출하는 게 아니라, nginx 앱용 Service를 새로 만드는 것이다.

---

## 4단계: Ingress 리소스 생성

```bash
kubectl apply -f ingress.yaml
```

Ingress 리소스는 요청을 어떤 Service로 보낼지 정의한다.

예를 들어:

```text
/ 로 들어온 요청
   ↓
nginx Service로 전달
```

이런 규칙을 만든다.

---

# 11. 최종 구조

최종 구조는 이렇게 볼 수 있다.

```text
[외부 사용자]
     ↓
[ingress-nginx-controller Service]
     ↓
[ingress-nginx-controller Pod]
     ↓
[Ingress 리소스 규칙 확인]
     ↓
[nginx Service]
     ↓
[nginx Pod]
     ↓
[nginx 컨테이너]
```

이 구조에서 Service는 두 번 등장한다.

```text
ingress-nginx-controller Service
= 외부 요청을 Ingress Controller로 보내는 Service

nginx Service
= Ingress Controller가 실제 앱 Pod로 요청을 보내기 위한 Service
```

둘은 이름도 다르고, 네임스페이스도 다르고, 역할도 다르다.

---

# 12. 자주 하는 착각

## 착각 1. Helm으로 설치한 ingress-nginx에는 Service가 없었다

아니다.

Helm으로 설치한 ingress-nginx에도 Service는 있다.

```bash
kubectl get svc -n ingress-nginx
```

로 확인할 수 있다.

다만 그 Service는 Ingress Controller용 Service다.

---

## 착각 2. kubectl expose deployment nginx는 Helm Service를 노출하는 명령어다

아니다.

```bash
kubectl expose deployment nginx --port=80 --target-port=80
```

이 명령어는 `nginx` Deployment를 기준으로 새로운 Service를 만든다.

즉, 기존 Helm Service를 수정하거나 노출하는 명령어가 아니다.

---

## 착각 3. Ingress가 Pod로 바로 보낸다

아니다.

Ingress는 보통 Service를 backend로 바라본다.

```text
Ingress
   ↓
Service
   ↓
Pod
```

그래서 Ingress 실습을 하려면 앱 Pod만 있으면 안 되고, 앱 Service도 필요하다.

---

# 13. 한 문장으로 정리

Helm으로 설치한 `ingress-nginx` 안에도 Service는 있지만, 그건 **Ingress Controller로 들어가는 입구**이고, `kubectl expose deployment nginx --port=80 --target-port=80`로 만드는 Service는 **내가 만든 nginx 앱 Pod로 가는 입구**다.

즉, 하나는 Controller용 Service이고, 하나는 Application용 Service다.

```text
ingress-nginx-controller Service
= Ingress Controller용

nginx Service
= 애플리케이션용
```

Ingress를 이해할 때 핵심은 이 흐름이다.

```text
외부 요청
   ↓
Ingress Controller Service
   ↓
Ingress Controller Pod
   ↓
Ingress 규칙
   ↓
Application Service
   ↓
Application Pod
```

이 구조가 잡히면 Ingress, Service, Deployment, Pod의 관계가 훨씬 덜 헷갈린다.
