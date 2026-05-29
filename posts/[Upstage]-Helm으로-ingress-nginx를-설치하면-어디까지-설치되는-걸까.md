---
title: "[Kubernetes] Helm으로 ingress-nginx를 설치하면 어디까지 설치되는 걸까?"
source: "https://velog.io/@yorange50/Kubernetes-Helm으로-ingress-nginx를-설치하면-어디까지-설치되는-걸까"
published: "2026-05-13T06:54:30.851Z"
tags: ""
backup_date: "2026-05-29T14:52:52.744615"
---



Ingress를 처음 실습할 때 가장 헷갈렸던 부분이 있다.

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

이 명령어를 치면 뭔가 Ingress 관련 설정이 다 끝난 것처럼 느껴진다.

그래서 이후에 다시 이런 명령어를 치면 헷갈린다.

```bash
kubectl create deployment nginx --image=nginx
kubectl expose deployment nginx --port=80 --target-port=80
```

처음에는 이런 생각이 든다.

> Helm으로 ingress-nginx 설치했는데 왜 nginx Deployment를 또 만들지?
> Helm으로 Service도 생긴 것 같은데 왜 Service를 또 만들지?
> Helm이 어디까지 해준 거지?

결론부터 말하면 이렇다.

> Helm으로 설치한 ingress-nginx는 **Ingress Controller를 운영하기 위한 리소스까지만 설치**한다.
> 실제 애플리케이션 Deployment, Service, Ingress 규칙은 사용자가 따로 만들어야 한다.

이건 실수나 누락이 아니라 **의도적인 구조**다.

---

# 1. Helm으로 설치한 것은 “앱”이 아니라 “컨트롤러”다

먼저 이 명령어를 보자.

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

이 명령어는 `nginx 웹서버 앱`을 설치하는 게 아니다.

설치하는 대상은 이것이다.

```text
ingress-nginx-controller
```

즉, **Ingress Controller**를 설치하는 명령어다.

Ingress Controller는 쉽게 말하면 이런 역할을 한다.

```text
외부에서 요청이 들어옴
→ Ingress 규칙을 확인함
→ 알맞은 Service로 요청을 넘김
```

즉, 직접 서비스를 제공하는 앱이라기보다는 **요청을 라우팅하는 컨트롤러**다.

비유하면:

```text
Ingress Controller
= 안내 데스크
= 교통 정리 담당자
= 라우터 역할
```

---

# 2. Helm으로 생기는 리소스들

Helm으로 `ingress-nginx`를 설치하면 보통 이런 리소스들이 생긴다.

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

Secret
- ingress-nginx-admission

ValidatingWebhookConfiguration
- ingress-nginx-admission
```

전부 공통점이 있다.

바로 **Ingress Controller 자체를 실행하고 운영하기 위한 리소스**라는 점이다.

확인하려면 이렇게 보면 된다.

```bash
kubectl get all -n ingress-nginx
```

또는 Service만 보고 싶으면:

```bash
kubectl get svc -n ingress-nginx
```

대략 이런 식으로 나온다.

```text
NAME                                 TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)
ingress-nginx-controller             LoadBalancer   10.x.x.x        <pending>     80:xxxxx/TCP,443:xxxxx/TCP
ingress-nginx-controller-admission   ClusterIP      10.x.x.x        <none>        443/TCP
```

여기서 중요한 건 이거다.

```text
ingress-nginx-controller Service
```

Helm으로 설치해도 Service가 생기긴 한다.

하지만 이 Service는 **내 애플리케이션용 Service가 아니다.**

이 Service는 **Ingress Controller Pod로 들어가는 Service**다.

---

# 3. Helm으로 설치된 Service의 역할

Helm으로 생긴 `ingress-nginx-controller Service`의 역할은 다음과 같다.

```text
외부 요청
   ↓
ingress-nginx-controller Service
   ↓
ingress-nginx-controller Pod
```

즉, 외부 요청을 Ingress Controller에게 전달하는 입구다.

여기까지는 “요청을 받을 준비”만 된 상태다.

아직 요청을 넘겨줄 실제 애플리케이션은 없다.

```text
외부 요청
   ↓
Ingress Controller
   ↓
어디로 보내야 하지?
```

Ingress Controller는 라우터 역할을 하는 애다.

하지만 라우터가 아무리 있어도, 뒤에 연결된 목적지 앱이 없으면 실제 응답을 줄 수 없다.

---

# 4. Helm이 실제 앱까지 만들어주지 않는 이유

Helm chart는 `ingress-nginx`를 설치할 뿐이다.

그런데 네가 실제로 어떤 앱을 띄울지는 Helm이 알 수 없다.

예를 들어 네 앱은 이런 것들 중 하나일 수 있다.

```text
Spring Boot 앱
FastAPI 앱
React 정적 페이지
Node.js API 서버
Django 서버
nginx 테스트 웹서버
게시판 API
AI 모델 서빙 서버
```

Helm chart 입장에서는 사용자가 어떤 앱을 배포할지 모른다.

그래서 `ingress-nginx` Helm chart는 딱 여기까지만 책임진다.

```text
Ingress Controller 설치
Ingress Controller 실행
Ingress Controller로 들어오는 Service 생성
Admission Webhook 등 보조 리소스 생성
```

반대로 아래 리소스들은 사용자가 직접 만들어야 한다.

```text
애플리케이션 Deployment
애플리케이션 Pod
애플리케이션 Service
Ingress 리소스 규칙
```

즉, Helm은 컨트롤러를 설치하고, 앱 연결은 사용자가 직접 정의하는 구조다.

---

# 5. 그래서 nginx Deployment를 따로 만든다

Ingress 실습에서는 보통 테스트용 앱으로 nginx를 띄운다.

```bash
kubectl create deployment nginx --image=nginx
```

이 명령어는 테스트용 nginx 웹서버를 실행한다.

생성되는 구조는 이렇다.

```text
Deployment nginx
   ↓
ReplicaSet
   ↓
Pod nginx-xxxxx
   ↓
nginx 컨테이너
```

여기서의 `nginx`는 Helm으로 설치한 `ingress-nginx`와 다르다.

이름이 비슷해서 헷갈리지만 역할이 완전히 다르다.

```text
ingress-nginx
= Ingress Controller
= 요청을 라우팅하는 애

nginx
= 테스트용 웹서버 애플리케이션
= 실제 HTML 응답을 주는 애
```

즉, Helm으로 설치한 것은 라우터고, `kubectl create deployment nginx`로 만든 것은 실제 목적지 앱이다.

---

# 6. 그런데 Deployment만 만들면 왜 부족할까?

`kubectl create deployment nginx --image=nginx`를 실행하면 Pod는 생긴다.

하지만 Ingress는 Pod를 직접 바라보지 않는다.

Ingress는 보통 Service를 backend로 바라본다.

```text
Ingress
   ↓
Service
   ↓
Pod
```

Pod는 언제든 죽었다가 다시 뜰 수 있고, IP도 바뀔 수 있다.

그래서 Kubernetes에서는 Pod 앞에 Service를 둔다.

Service는 Pod로 가는 고정된 입구 역할을 한다.

```text
Service
= Pod로 가는 안정적인 주소
```

그래서 nginx Deployment를 만든 다음에는 Service를 만들어야 한다.

```bash
kubectl expose deployment nginx --port=80 --target-port=80
```

이 명령어는 새로운 Service를 만든다.

이 Service는 Helm으로 설치된 Service가 아니다.

이건 **테스트용 nginx 앱 앞에 붙는 Service**다.

```text
nginx Service
   ↓
nginx Pod
```

---

# 7. Service가 두 종류 나오는 이유

Ingress 실습을 하면 Service가 여러 개 나와서 헷갈릴 수 있다.

하지만 역할을 나누면 간단하다.

## 1. Ingress Controller용 Service

Helm으로 생긴다.

```text
ingress-nginx-controller Service
```

역할:

```text
외부 요청을 Ingress Controller Pod로 전달
```

흐름:

```text
외부 요청
   ↓
ingress-nginx-controller Service
   ↓
ingress-nginx-controller Pod
```

---

## 2. 애플리케이션용 Service

`kubectl expose deployment nginx`로 생긴다.

```text
nginx Service
```

역할:

```text
Ingress Controller가 실제 nginx Pod로 요청을 넘길 수 있게 해주는 내부 입구
```

흐름:

```text
Ingress Controller
   ↓
nginx Service
   ↓
nginx Pod
```

---

# 8. Ingress 리소스는 직접 따로 만들어야 한다

Helm으로 Ingress Controller를 설치했다고 해서, 자동으로 라우팅 규칙까지 생기는 것은 아니다.

라우팅 규칙은 사용자가 직접 만들어야 한다.

예를 들어 이런 Ingress YAML을 작성한다.

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

여기서 핵심은 이 부분이다.

```yaml
backend:
  service:
    name: nginx
    port:
      number: 80
```

이 뜻은:

```text
/ 경로로 들어온 요청은 nginx Service로 보내라
```

라는 의미다.

즉, Ingress Controller는 요청이 들어오면 Ingress 규칙을 확인하고, 그 규칙에 적힌 Service로 요청을 전달한다.

---

# 9. 전체 흐름

전체 구조를 한 번에 보면 이렇다.

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

여기서 Helm이 담당한 부분은 앞쪽이다.

```text
ingress-nginx-controller Service
ingress-nginx-controller Pod
Controller 운영에 필요한 리소스들
```

사용자가 직접 만든 부분은 뒤쪽이다.

```text
nginx Deployment
nginx Pod
nginx Service
nginx Ingress
```

즉, 역할을 나누면 이렇게 된다.

```text
Helm install ingress-nginx
= Ingress Controller 설치

kubectl create deployment nginx
= 실제 앱 생성

kubectl expose deployment nginx
= 실제 앱으로 가는 Service 생성

kubectl apply -f ingress.yaml
= 어떤 요청을 어떤 Service로 보낼지 규칙 생성
```

---

# 10. 비유로 이해하기

이 구조는 비유하면 훨씬 쉽다.

```text
Helm install ingress-nginx
= 고속도로 톨게이트와 교통 관제소 설치

kubectl create deployment nginx
= 목적지 건물 짓기

kubectl expose deployment nginx
= 목적지 건물 입구 만들기

kubectl apply -f ingress.yaml
= 이 주소로 온 차는 저 건물로 보내라는 안내판 설치
```

Ingress Controller는 길을 안내할 수는 있지만, 목적지 건물을 대신 지어주지는 않는다.

그리고 목적지 건물이 생겼다고 해서 자동으로 안내판이 생기는 것도 아니다.

각각 따로 만들어야 한다.

---

# 11. 명령어별 책임 정리

## Helm으로 한 것

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

책임:

```text
Ingress Controller 설치
Controller Pod 실행
Controller Service 생성
Controller 설정 리소스 생성
Admission Webhook 관련 리소스 생성
```

즉:

```text
외부 요청을 받아서 라우팅할 준비
```

---

## kubectl create deployment로 한 것

```bash
kubectl create deployment nginx --image=nginx
```

책임:

```text
테스트용 nginx 애플리케이션 실행
Deployment 생성
ReplicaSet 생성
Pod 생성
컨테이너 실행
```

즉:

```text
실제 응답을 줄 앱 생성
```

---

## kubectl expose deployment로 한 것

```bash
kubectl expose deployment nginx --port=80 --target-port=80
```

책임:

```text
nginx Deployment 앞에 Service 생성
Ingress가 바라볼 backend Service 생성
Pod로 가는 안정적인 내부 입구 생성
```

즉:

```text
앱으로 들어가는 고정 입구 생성
```

---

## kubectl apply -f ingress.yaml로 한 것

```bash
kubectl apply -f ingress.yaml
```

책임:

```text
외부 요청을 어떤 Service로 보낼지 규칙 생성
```

즉:

```text
라우팅 규칙 생성
```

---

# 12. 핵심 착각 정리

## 착각 1. Helm으로 ingress-nginx 설치하면 앱까지 생긴다

아니다.

Helm으로 설치되는 것은 Ingress Controller다.

앱은 따로 만들어야 한다.

```text
Helm
= Controller 설치

kubectl create deployment
= 앱 설치
```

---

## 착각 2. Helm으로 생긴 Service가 nginx 앱 Service다

아니다.

Helm으로 생긴 Service는 Ingress Controller용 Service다.

```text
ingress-nginx-controller Service
= Controller로 들어가는 입구
```

앱용 Service는 따로 만든다.

```text
nginx Service
= nginx 앱 Pod로 들어가는 입구
```

---

## 착각 3. Ingress Controller만 설치하면 외부 요청이 자동으로 앱에 연결된다

아니다.

Ingress Controller는 라우팅을 수행하는 컴포넌트일 뿐이다.

반드시 Ingress 리소스가 있어야 한다.

```text
Ingress Controller
= 규칙을 실행하는 애

Ingress 리소스
= 실제 라우팅 규칙
```

둘 다 필요하다.

---

# 13. 최종 정리

Helm으로 `ingress-nginx`를 설치하면 **Ingress Controller 관련 리소스까지만 설치**된다.

이건 의도적인 구조다.

왜냐하면 Ingress Controller는 클러스터 공용 라우터 역할을 할 뿐이고, 실제 어떤 애플리케이션을 띄울지는 사용자가 결정해야 하기 때문이다.

따라서 Ingress 실습의 전체 순서는 보통 이렇게 된다.

```bash
# 1. Ingress Controller 설치
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace

# 2. 테스트 앱 생성
kubectl create deployment nginx --image=nginx

# 3. 테스트 앱 Service 생성
kubectl expose deployment nginx --port=80 --target-port=80

# 4. Ingress 규칙 생성
kubectl apply -f ingress.yaml
```

흐름은 이렇게 완성된다.

```text
외부 요청
   ↓
Ingress Controller Service
   ↓
Ingress Controller Pod
   ↓
Ingress 리소스 규칙
   ↓
Application Service
   ↓
Application Pod
```

한 문장으로 정리하면:

> Helm으로 ingress-nginx를 설치하는 것은 “외부 요청을 받아 라우팅할 컨트롤러”를 설치하는 것이고, 실제 앱 Deployment, 앱 Service, Ingress 라우팅 규칙은 사용자가 의도적으로 따로 만들어야 한다.
