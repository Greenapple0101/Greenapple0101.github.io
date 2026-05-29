---
title: "[KUBERNETES] Helm으로 ingress-nginx 설치하고, kubectl로 nginx 앱까지 연결하기"
source: "https://velog.io/@yorange50/KUBERNETES-Helm으로-ingress-nginx-설치하고-kubectl로-nginx-앱까지-연결하기"
published: "2026-05-13T05:44:39.802Z"
tags: ""
backup_date: "2026-05-29T14:52:52.745395"
---


Kubernetes에서 Ingress를 처음 실습하면 머리가 복잡해진다.

Helm도 나오고, kubectl도 나오고, ingress-nginx도 나오고, nginx-ingress도 나오고, nginx Service와 nginx Pod까지 나온다.

처음에는 이런 생각이 든다.

```text
도대체 nginx가 몇 개야?
Helm으로 설치한 nginx랑 내가 띄운 nginx 앱이 같은 건가?
Ingress를 만들었는데 왜 503이 뜨지?
앱도 없는데 나는 뭘 한 거지?
```

이번 글은 `localhost`로 접속했을 때 `Welcome to nginx!` 화면이 뜨기까지의 전체 흐름을 정리한 글이다.

## 1. 전체 결론 먼저 보기

최종적으로 우리가 만든 흐름은 이렇다.

```text
브라우저
  ↓
localhost:80
  ↓
k3d LoadBalancer
  ↓
ingress-nginx Controller
  ↓
nginx-ingress 규칙
  ↓
nginx Service
  ↓
nginx Pod
  ↓
nginx 컨테이너
  ↓
Welcome to nginx!
```

여기서 각각의 역할은 다르다.

```text
ingress-nginx
= Helm으로 설치한 Ingress Controller
= 외부 요청을 실제로 받아서 라우팅하는 애

nginx-ingress
= kubectl apply로 만든 Ingress 리소스 이름
= localhost 요청을 nginx Service로 보내라는 규칙

nginx Service
= nginx Pod로 가는 고정 입구

nginx Pod
= nginx 컨테이너가 떠 있는 실행 공간

nginx
= Pod 안에서 실행 중인 웹서버 애플리케이션
```

핵심은 이거다.

```text
Helm으로 받은 건 nginx 웹서버 앱이 아니라 ingress-nginx Controller다.
nginx 웹서버 앱은 kubectl create deployment nginx --image=nginx 명령어로 따로 띄운다.
```

## 2. k3d 클러스터 생성

먼저 로컬에서 Kubernetes 실습을 하기 위해 k3d 클러스터를 만든다.

```sh
k3d cluster create hello-cluster -p "80:80@loadbalancer"
```

여기서 중요한 부분은 이것이다.

```sh
-p "80:80@loadbalancer"
```

이 옵션은 로컬 맥북의 80번 포트를 k3d 클러스터의 LoadBalancer 80번 포트로 연결한다.

즉, 브라우저에서 `localhost`로 접속했을 때 요청이 Kubernetes 클러스터 안으로 들어갈 수 있게 해준다.

```text
localhost:80
→ k3d LoadBalancer:80
```

만약 이 포트 매핑 없이 클러스터를 만들면 브라우저에서 `localhost`에 접속했을 때 이런 에러가 날 수 있다.

```text
ERR_CONNECTION_REFUSED
```

이건 브라우저 요청이 Kubernetes 안까지 들어가지 못했다는 뜻이다.

클러스터가 만들어졌는지 확인한다.

```sh
k3d cluster list
```

노드 상태도 확인한다.

```sh
kubectl get nodes
```

정상이라면 `Ready` 상태의 노드가 보여야 한다.

```text
NAME                         STATUS   ROLES
k3d-hello-cluster-server-0   Ready    control-plane,master
```

## 3. Helm으로 ingress-nginx Controller 설치

이제 Ingress를 처리할 Controller를 설치한다.

여기서 사용하는 도구가 Helm이다.

Helm은 Kubernetes의 패키지 매니저다. 여러 Kubernetes 리소스를 하나의 Chart로 묶어서 설치할 수 있다.

먼저 ingress-nginx Helm 저장소를 추가한다.

```sh
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
```

저장소 정보를 업데이트한다.

```sh
helm repo update
```

이제 ingress-nginx Controller를 설치한다.

```sh
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

이 명령어는 단순히 Ingress 리소스 하나를 만드는 명령어가 아니다.

이 명령어는 Ingress를 실제로 처리하는 `ingress-nginx Controller`를 설치한다.

Helm Chart는 내부적으로 여러 리소스를 만든다.

```text
Deployment
Pod
Service
ServiceAccount
ConfigMap
ClusterRole
ClusterRoleBinding
IngressClass
Webhook
```

즉, 이 명령어는 이런 뜻에 가깝다.

```text
Ingress 규칙을 감시하고,
외부 요청을 받아서,
알맞은 Service로 라우팅하는 시스템을 설치해라.
```

설치 확인은 이렇게 한다.

```sh
kubectl get pods -n ingress-nginx
```

Service도 확인한다.

```sh
kubectl get svc -n ingress-nginx
```

여기서 주의할 점이 있다.

Helm으로 설치한 `ingress-nginx`는 테스트용 nginx 웹서버 앱이 아니다.

```text
ingress-nginx
= Ingress Controller
= 라우터 역할

nginx
= 테스트용 웹서버 앱
= 실제 응답하는 백엔드
```

이 둘을 섞어서 생각하면 굉장히 헷갈린다.

## 4. 아직 앱은 없다

여기까지 했다고 해서 브라우저에 `Welcome to nginx!`가 뜨는 것은 아니다.

지금까지 만든 것은 앞단이다.

```text
브라우저
  ↓
localhost:80
  ↓
k3d LoadBalancer
  ↓
ingress-nginx Controller
```

하지만 아직 뒤쪽이 없다.

```text
nginx Service
nginx Pod
nginx 웹서버 앱
```

즉, 이런 상태다.

```text
문지기는 있다.
라우터도 있다.
그런데 실제 응답할 앱은 없다.
```

이 상태에서 Ingress만 만들어놓고 접속하면 503이 날 수 있다.

```text
503 Service Temporarily Unavailable
```

이건 요청이 ingress-nginx Controller까지는 왔지만, 뒤쪽 Service나 Pod로 넘기지 못했다는 뜻이다.

## 5. 테스트용 nginx 앱 만들기

이제 실제 응답할 애플리케이션을 만든다.

가장 단순한 테스트용 웹서버로 nginx를 사용한다.

```sh
kubectl create deployment nginx --image=nginx
```

이 명령어의 의미는 이렇다.

```text
nginx라는 이름의 Deployment를 만들고,
nginx 이미지를 사용해서 Pod를 실행해라.
```

여기서 `--image=nginx`는 Docker Hub의 nginx 이미지를 의미한다.

내가 직접 `docker pull nginx`를 하지 않았더라도 괜찮다.

Kubernetes가 Pod를 만들 때 필요한 이미지를 보고, 노드의 컨테이너 런타임이 알아서 이미지를 가져온다.

흐름은 이렇다.

```text
kubectl create deployment nginx --image=nginx
→ Kubernetes가 nginx 이미지가 필요하다고 판단
→ 노드의 컨테이너 런타임이 nginx 이미지를 pull
→ Pod 안에서 nginx 컨테이너 실행
→ nginx 웹서버 앱 실행
```

확인한다.

```sh
kubectl get pods
```

정상이라면 nginx Pod가 떠 있어야 한다.

```text
NAME                     READY   STATUS    RESTARTS   AGE
nginx-xxxxx              1/1     Running   0          1m
```

## 6. nginx Service 만들기

Pod가 생겼다고 해서 Ingress가 바로 Pod로 직접 보내는 것은 아니다.

Ingress는 보통 Service를 바라본다.

Service는 Pod로 가는 고정 입구다.

Pod는 죽었다가 다시 만들어지면 IP가 바뀔 수 있다. 그래서 Ingress가 Pod IP를 직접 바라보면 불안정하다.

대신 Service를 만든다.

```sh
kubectl expose deployment nginx --port=80 --target-port=80
```

이 명령어의 의미는 이렇다.

```text
nginx Deployment가 관리하는 Pod들로 가는 Service를 만들어라.
Service의 포트는 80이고,
Pod 컨테이너의 80번 포트로 보내라.
```

확인한다.

```sh
kubectl get svc
```

정상이라면 `nginx` Service가 보여야 한다.

```text
NAME         TYPE        CLUSTER-IP      PORT(S)
nginx        ClusterIP   10.43.x.x       80/TCP
```

여기서 Service는 앱을 가지고 있는 게 아니다.

정확히는 이렇다.

```text
nginx 앱은 Pod 안에서 실행된다.
nginx Service는 그 Pod로 가는 고정 입구다.
```

구조는 이렇게 된다.

```text
nginx Service
  ↓
nginx Pod
  ↓
nginx Container
  ↓
nginx 웹서버 앱
```

Service가 Pod를 잘 찾고 있는지 확인하려면 describe를 볼 수 있다.

```sh
kubectl describe svc nginx
```

여기서 `Endpoints`가 중요하다.

정상이면 이런 식으로 나온다.

```text
Endpoints: 10.42.0.12:80
```

문제가 있으면 이렇게 나온다.

```text
Endpoints: <none>
```

`Endpoints: <none>`이면 Service가 연결할 Pod를 못 찾고 있다는 뜻이다. 이 상태에서는 Ingress를 만들어도 503이 날 수 있다.

## 7. Ingress YAML 만들기

이제 외부 요청을 nginx Service로 보내는 Ingress 규칙을 만든다.

파일 이름은 예를 들어 `nginx-ingress.yaml`로 한다.

```sh
vi nginx-ingress.yaml
```

내용은 다음과 같이 작성한다.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
spec:
  ingressClassName: nginx
  rules:
    - host: localhost
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: nginx
                port:
                  number: 80
```

여기서 중요한 부분은 `kind: Ingress`다.

```yaml
kind: Ingress
```

이 YAML은 nginx 앱을 만드는 파일이 아니다.

이 YAML은 라우팅 규칙을 만드는 파일이다.

뜻은 이렇다.

```text
host가 localhost이고
path가 /이면
nginx Service의 80번 포트로 보내라.
```

그리고 이 부분이 실제 Service 이름과 맞아야 한다.

```yaml
service:
  name: nginx
  port:
    number: 80
```

즉, `kubectl get svc` 했을 때 `nginx`라는 Service가 있어야 한다.

## 8. kubectl apply로 Ingress 적용

이제 Ingress YAML을 적용한다.

```sh
kubectl apply -f nginx-ingress.yaml
```

정상이라면 이런 메시지가 나온다.

```text
ingress.networking.k8s.io/nginx-ingress created
```

Ingress를 확인한다.

```sh
kubectl get ingress
```

예상 결과는 다음과 같다.

```text
NAME            CLASS   HOSTS       ADDRESS   PORTS   AGE
nginx-ingress   nginx   localhost             80      8s
```

여기서 `nginx-ingress`는 Ingress 리소스 이름이다.

다시 구분하면 이렇다.

```text
ingress-nginx
= Helm으로 설치한 Ingress Controller

nginx-ingress
= kubectl apply로 만든 Ingress 규칙

nginx
= 테스트용 웹서버 앱 이름이자 Service/Deployment 이름
```

이름이 비슷해서 헷갈리지만, 역할이 다르다.

## 9. 브라우저에서 localhost 접속

이제 브라우저에서 접속한다.

```text
http://localhost
```

정상이라면 다음 화면이 뜬다.

```text
Welcome to nginx!
```

이 화면이 떴다는 것은 전체 연결이 성공했다는 뜻이다.

```text
브라우저
  ↓
localhost:80
  ↓
k3d LoadBalancer
  ↓
ingress-nginx Controller
  ↓
nginx-ingress 규칙
  ↓
nginx Service
  ↓
nginx Pod
  ↓
nginx 컨테이너
  ↓
nginx 웹서버 앱
```

즉, 요청이 실제 nginx 앱까지 도달했고, nginx가 기본 페이지를 응답한 것이다.

## 10. 에러별로 이해하기

이번 과정에서 만날 수 있는 에러를 정리하면 다음과 같다.

### error: the path "nginx-ingress.yaml" does not exist

```text
YAML 파일을 현재 디렉토리에서 찾지 못했다는 뜻
```

확인할 명령어:

```sh
pwd
ls
```

현재 위치에 파일이 없다면 파일이 있는 경로로 이동하거나, 정확한 경로를 지정해야 한다.

```sh
kubectl apply -f /정확한/경로/nginx-ingress.yaml
```

### ERR_CONNECTION_REFUSED

```text
브라우저의 localhost 요청이 Kubernetes 안으로 들어가지 못했다는 뜻
```

k3d 클러스터 생성 시 포트 매핑이 없으면 발생할 수 있다.

```sh
k3d cluster create hello-cluster -p "80:80@loadbalancer"
```

이미 같은 이름의 클러스터가 있으면 삭제 후 다시 만들어야 한다.

```sh
k3d cluster delete hello-cluster
k3d cluster create hello-cluster -p "80:80@loadbalancer"
```

### 503 Service Temporarily Unavailable

```text
요청은 ingress-nginx Controller까지 도착했지만,
뒤쪽 Service 또는 Pod로 연결되지 못했다는 뜻
```

확인할 명령어:

```sh
kubectl get pods
kubectl get svc
kubectl get ingress
kubectl describe ingress nginx-ingress
kubectl describe svc nginx
```

특히 Service의 Endpoints를 확인해야 한다.

```text
Endpoints: <none>
```

이면 Service가 Pod를 못 찾고 있는 상태다.

## 11. 최종 명령어 순서 정리

처음부터 다시 한다면 전체 순서는 다음과 같다.

```sh
k3d cluster create hello-cluster -p "80:80@loadbalancer"
```

```sh
kubectl get nodes
```

```sh
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
```

```sh
helm repo update
```

```sh
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

```sh
kubectl get pods -n ingress-nginx
```

```sh
kubectl create deployment nginx --image=nginx
```

```sh
kubectl expose deployment nginx --port=80 --target-port=80
```

```sh
kubectl get pods
```

```sh
kubectl get svc
```

```sh
vi nginx-ingress.yaml
```

```sh
kubectl apply -f nginx-ingress.yaml
```

```sh
kubectl get ingress
```

```sh
kubectl describe ingress nginx-ingress
```

브라우저에서 확인:

```text
http://localhost
```

## 12. 최종 정리

이번 실습의 핵심은 `ingress-nginx`, `nginx-ingress`, `nginx`를 구분하는 것이다. Helm으로 설치한 `ingress-nginx`는 nginx 웹서버 앱이 아니라 Ingress Controller다. 이 Controller는 외부 요청을 받아 Ingress 규칙에 따라 Service로 라우팅한다. `nginx-ingress`는 kubectl apply로 만든 Ingress 리소스 이름이며, localhost 요청을 nginx Service로 보내라는 규칙이다. `nginx`는 kubectl create deployment nginx --image=nginx 명령어로 생성한 테스트용 웹서버 애플리케이션이다. Kubernetes는 이 명령어를 보고 nginx 이미지를 pull하고 Pod 안에서 nginx 컨테이너를 실행한다. 이후 nginx Service가 nginx Pod로 요청을 전달하고, 최종적으로 nginx 웹서버가 `Welcome to nginx!` 페이지를 응답한다. 따라서 전체 흐름은 `브라우저 → k3d LoadBalancer → ingress-nginx Controller → nginx-ingress 규칙 → nginx Service → nginx Pod → nginx 컨테이너 → nginx 앱`으로 이해하면 된다.
