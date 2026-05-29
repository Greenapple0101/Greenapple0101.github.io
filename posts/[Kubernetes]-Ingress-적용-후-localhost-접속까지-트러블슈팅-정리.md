---
title: "[KUBERNETES] Ingress 적용 후 localhost 접속까지 트러블슈팅 정리"
source: "https://velog.io/@yorange50/KUBERNETES-Ingress-적용-후-localhost-접속까지-트러블슈팅-정리"
published: "2026-05-13T05:24:35.460Z"
tags: ""
backup_date: "2026-05-29T14:52:52.747053"
---

![](https://velog.velcdn.com/images/yorange50/post/351a7e1a-1db7-476f-a47f-d36542437280/image.png)
![](https://velog.velcdn.com/images/yorange50/post/abdde549-ad93-4db4-bec0-982030d3753f/image.png)


Kubernetes에서 `ingress-nginx`를 설치하고 Ingress YAML을 적용한 뒤 브라우저에서 `localhost`로 접속하려고 했다. 그런데 처음에는 YAML 파일을 찾지 못했고, 그다음에는 연결 거부가 났고, 마지막에는 `503 Service Temporarily Unavailable`이 발생했다. 이번 글은 이 과정을 하나씩 정리한 트러블슈팅 기록이다.

## 1. 처음 만난 에러: nginx-ingress.yaml 파일이 없다고 나옴

처음 실행한 명령어는 다음과 같았다.

```bash
k create -f nginx-ingress.yaml
```

또는 이후에는 다음처럼 실행했다.

```bash
k apply -f nginx-ingress.yaml
```

그런데 이런 에러가 발생했다.

```text
error: the path "nginx-ingress.yaml" does not exist
```

처음 보면 Kubernetes YAML 내용이 잘못된 것처럼 느껴질 수 있다. 하지만 이 에러는 Kubernetes 리소스 문제가 아니다. **터미널이 현재 위치에서 `nginx-ingress.yaml` 파일을 찾지 못했다는 뜻**이다.

즉, `kubectl`은 현재 내가 서 있는 디렉토리에서 이 파일을 찾는다.

```bash
k apply -f nginx-ingress.yaml
```

이 명령어는 다음과 같은 의미다.

```text
현재 디렉토리에 있는 nginx-ingress.yaml 파일을 Kubernetes에 적용해라
```

그런데 현재 위치에 해당 파일이 없으면 당연히 실패한다.

## 2. 현재 위치 확인하기

이럴 때 먼저 확인해야 하는 명령어는 `pwd`와 `ls`다.

```bash
pwd
```

현재 내가 어느 디렉토리에 있는지 확인한다.

```bash
ls
```

현재 디렉토리에 어떤 파일이 있는지 확인한다.

이때 `nginx-ingress.yaml`이 목록에 없다면, `k apply -f nginx-ingress.yaml`은 실패한다.

## 3. 파일 경로를 잘못 지정한 경우

처음에는 다음처럼 경로를 지정해서 실행했다.

```bash
k apply -f ~/hello-world/nginx-ingress.yaml
```

그런데 이런 에러가 나왔다.

```text
error: the path "/Users/baegseoyeon/hello-world/nginx-ingress.yaml" does not exist
```

이 말은 `/Users/baegseoyeon/hello-world/` 안에도 `nginx-ingress.yaml` 파일이 없다는 뜻이다.

즉, 문제는 Kubernetes가 아니라 파일 위치였다.

## 4. 현재 위치에 파일을 만들고 다시 적용

그래서 현재 홈 디렉토리에서 직접 파일을 만들었다.

```bash
vi nginx-ingress.yaml
```

파일을 작성한 뒤 다시 적용했다.

```bash
k apply -f nginx-ingress.yaml
```

이번에는 성공했다.

```text
ingress.networking.k8s.io/nginx-ingress created
```

이 메시지는 `nginx-ingress`라는 Ingress 리소스가 Kubernetes 클러스터에 생성되었다는 뜻이다.

## 5. Ingress 생성 확인

Ingress가 생성되었는지 확인했다.

```bash
kubectl get ingress
```

결과는 다음과 같았다.

```text
NAME            CLASS   HOSTS       ADDRESS   PORTS   AGE
nginx-ingress   nginx   localhost             80      8s
```

여기서 중요한 점은 `nginx-ingress`라는 Ingress가 실제로 생성되었다는 것이다.

```text
NAME: nginx-ingress
CLASS: nginx
HOSTS: localhost
PORTS: 80
```

즉, Kubernetes 안에는 다음과 같은 규칙이 생긴 상태다.

```text
localhost로 들어오는 HTTP 요청을 특정 Service로 보내라
```

하지만 이 시점에서 바로 브라우저 접속이 되는 것은 아니다. Ingress는 라우팅 규칙일 뿐이고, 실제 요청을 받는 Ingress Controller와 뒤쪽의 Service, Pod가 모두 정상이어야 한다.

## 6. localhost 접속 시 ERR_CONNECTION_REFUSED 발생

처음 브라우저에서 `localhost`로 접속했을 때는 다음 에러가 나왔다.

```text
ERR_CONNECTION_REFUSED
```

이 에러는 브라우저가 `localhost:80`으로 요청을 보냈는데, 그 요청을 받아줄 대상이 없다는 뜻이다.

이때 구조를 보면 다음과 같다.

```text
브라우저
→ localhost:80
→ k3d LoadBalancer
→ ingress-nginx controller
→ Ingress
→ Service
→ Pod
```

그런데 `ERR_CONNECTION_REFUSED`는 보통 앞단에서 막힌다.

즉, 브라우저 요청이 Kubernetes 안의 ingress-nginx까지 도달하지 못한 상태다.

## 7. 원인: k3d 클러스터 생성 시 80번 포트 매핑이 안 되어 있었음

k3d를 사용할 때 로컬 맥북의 80번 포트를 클러스터 안의 LoadBalancer로 연결하려면 클러스터 생성 시 포트 매핑을 해줘야 한다.

```bash
k3d cluster create hello-cluster -p "80:80@loadbalancer"
```

이 명령어의 의미는 다음과 같다.

```text
맥북 localhost:80
→ k3d loadbalancer의 80번 포트
→ ingress-nginx controller
```

그런데 이미 `hello-cluster`라는 클러스터가 존재하는 상태에서 다시 생성하려고 하니 이런 에러가 발생했다.

```text
FATA[0000] Failed to create cluster 'hello-cluster' because a cluster with that name already exists
```

이 말은 이미 같은 이름의 클러스터가 있기 때문에 새로 만들 수 없다는 뜻이다.

즉, 기존 클러스터에는 `80:80@loadbalancer` 포트 매핑이 없었고, 포트 매핑을 추가한 새 클러스터 생성도 실패한 상태였다.

## 8. 해결: 기존 클러스터 삭제 후 포트 매핑 포함해서 다시 생성

실습 환경이라면 기존 클러스터를 삭제하고 다시 만드는 것이 가장 깔끔하다.

```bash
k3d cluster delete hello-cluster
```

그다음 80번 포트 매핑을 포함해서 다시 생성한다.

```bash
k3d cluster create hello-cluster -p "80:80@loadbalancer"
```

이렇게 하면 로컬 브라우저에서 `localhost`로 들어온 요청이 k3d 클러스터의 LoadBalancer까지 전달될 수 있다.

## 9. ingress-nginx 다시 설치

클러스터를 새로 만들면 기존에 설치했던 리소스들은 사라진다. 따라서 ingress-nginx도 다시 설치해야 한다.

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

이 명령어는 `ingress-nginx` namespace를 만들고, 그 안에 ingress-nginx controller를 설치한다.

설치 후에는 다음 명령어로 확인할 수 있다.

```bash
kubectl get pods -n ingress-nginx
```

또는 전체 namespace 기준으로 확인할 수도 있다.

```bash
kubectl get pods -A | grep ingress
```

Service도 확인한다.

```bash
kubectl get svc -A | grep ingress
```

## 10. Ingress YAML 다시 적용

클러스터를 다시 만들었기 때문에 Ingress YAML도 다시 적용해야 한다.

```bash
k apply -f nginx-ingress.yaml
```

그리고 확인한다.

```bash
k get ingress
```

정상적으로 생성되면 다음처럼 보인다.

```text
NAME            CLASS   HOSTS       ADDRESS   PORTS   AGE
nginx-ingress   nginx   localhost             80      8s
```

이제 브라우저에서 `localhost`로 접속하면 적어도 ingress-nginx controller까지는 요청이 갈 수 있는 상태가 된다.

## 11. 이번에는 503 Service Temporarily Unavailable 발생

포트 매핑 문제를 해결하고 다시 접속하니 이번에는 화면이 바뀌었다.

```text
503 Service Temporarily Unavailable
nginx
```

이건 이전의 `ERR_CONNECTION_REFUSED`와 의미가 다르다.

`ERR_CONNECTION_REFUSED`는 입구 자체가 막힌 것이다.

```text
브라우저 → localhost:80
여기서 연결 실패
```

반면 `503 Service Temporarily Unavailable`은 nginx가 응답을 준 것이다.

즉, 요청이 ingress-nginx controller까지는 도착했다.

```text
브라우저
→ localhost:80
→ k3d loadbalancer
→ ingress-nginx controller
```

여기까지는 성공한 것이다.

하지만 ingress-nginx가 뒤쪽의 Service나 Pod로 요청을 넘기지 못해서 503을 반환한 것이다.

## 12. 503의 의미

Ingress 구조는 다음과 같다.

```text
브라우저
→ Ingress Controller
→ Ingress 규칙
→ Service
→ Pod
```

503이 떴다는 것은 보통 다음 중 하나다.

```text
Ingress에 적은 Service 이름이 실제 Service 이름과 다름
Ingress에 적은 Service port가 실제 Service port와 다름
Service는 있지만 연결된 Pod가 없음
Service selector와 Pod label이 맞지 않음
Pod가 아직 Running 상태가 아님
```

즉, 이제 문제는 포트 매핑이나 Ingress Controller 설치 문제가 아니라 **백엔드 Service와 Pod 연결 문제**로 넘어간 것이다.

## 13. 확인해야 할 명령어

먼저 Ingress가 어떤 Service로 보내려고 하는지 확인한다.

```bash
k describe ingress nginx-ingress
```

여기서 backend 부분을 봐야 한다.

```text
Backend:
  Service: 서비스이름:포트
```

그다음 실제 Service 목록을 확인한다.

```bash
k get svc
```

Pod 목록도 확인한다.

```bash
k get pods
```

전체를 한 번에 보고 싶으면 다음 명령어가 좋다.

```bash
k get all
```

## 14. Service와 Pod 연결 확인

Service가 있다고 해서 무조건 Pod로 연결되는 것은 아니다.

Service는 selector를 통해 Pod를 찾는다.

Service의 selector와 Pod의 label이 맞아야 한다.

확인하려면 다음 명령어를 사용한다.

```bash
k describe svc 서비스이름
```

여기서 중요한 부분은 `Endpoints`다.

정상이라면 다음처럼 Pod IP가 보여야 한다.

```text
Endpoints: 10.42.0.12:80
```

문제가 있으면 이렇게 나온다.

```text
Endpoints: <none>
```

`Endpoints: <none>`이면 Service가 연결할 Pod를 찾지 못하고 있다는 뜻이다.

이 경우 Ingress는 Service로 요청을 보내려고 하지만, Service 뒤에 실제 Pod가 없기 때문에 503이 발생할 수 있다.

## 15. 테스트용 nginx Deployment와 Service 만들기

만약 아직 백엔드 앱을 만들지 않았다면, 테스트용 nginx를 만들 수 있다.

```bash
k create deployment nginx --image=nginx
```

그리고 Service를 만든다.

```bash
k expose deployment nginx --port=80 --target-port=80
```

확인한다.

```bash
k get pods
k get svc
```

정상이라면 다음과 같은 리소스가 있어야 한다.

```text
deployment.apps/nginx
pod/nginx-...
service/nginx
ingress.networking.k8s.io/nginx-ingress
```

이제 Ingress YAML의 backend service 이름이 `nginx`인지 확인해야 한다.

예를 들어 Ingress YAML은 이런 식이어야 한다.

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

여기서 중요한 부분은 이거다.

```yaml
service:
  name: nginx
  port:
    number: 80
```

이 이름과 포트가 실제 Service와 맞아야 한다.

```bash
k get svc
```

결과에 `nginx` Service가 있고, port가 80이어야 한다.

## 16. 수정 후 다시 적용

Ingress YAML을 수정했다면 다시 적용한다.

```bash
k apply -f nginx-ingress.yaml
```

그다음 다시 확인한다.

```bash
k describe ingress nginx-ingress
```

그리고 브라우저에서 접속한다.

```text
http://localhost
```

정상이라면 nginx 기본 페이지가 뜬다.

## 17. 이번 트러블슈팅 흐름 정리

이번 문제는 단계별로 에러의 의미가 달랐다.

```text
1. error: the path "nginx-ingress.yaml" does not exist
→ YAML 파일이 현재 경로에 없음
→ Kubernetes 문제가 아니라 파일 경로 문제

2. ingress.networking.k8s.io/nginx-ingress created
→ Ingress 리소스 생성 성공

3. ERR_CONNECTION_REFUSED
→ localhost:80 요청이 ingress-nginx까지 도달하지 못함
→ k3d 생성 시 80:80@loadbalancer 포트 매핑 필요

4. FATA cluster already exists
→ 같은 이름의 k3d 클러스터가 이미 있어서 포트 매핑 포함 재생성 실패
→ 기존 클러스터 삭제 후 다시 생성 필요

5. 503 Service Temporarily Unavailable
→ ingress-nginx controller까지 요청은 도달함
→ 하지만 뒤쪽 Service 또는 Pod 연결 실패
```

## 18. 에러별로 보는 원인

이번 트러블슈팅을 에러 기준으로 보면 더 명확하다.

| 에러                                    | 의미                       | 확인할 것                   |
| ------------------------------------- | ------------------------ | ----------------------- |
| `path does not exist`                 | YAML 파일 경로 문제            | `pwd`, `ls`, 파일 위치      |
| `ERR_CONNECTION_REFUSED`              | localhost 포트에 연결할 대상 없음  | k3d 포트 매핑               |
| `cluster already exists`              | 같은 이름의 k3d 클러스터 존재       | `k3d cluster list`      |
| `503 Service Temporarily Unavailable` | Ingress는 받았지만 backend 없음 | Service, Pod, Endpoints |

## 19. 핵심 개념 정리

이번 과정에서 중요한 개념은 세 가지다.

첫째, `kubectl apply -f`는 파일 경로를 기준으로 동작한다.

```bash
k apply -f nginx-ingress.yaml
```

이 명령어는 현재 디렉토리에 있는 파일을 찾는다. 파일이 없으면 Kubernetes까지 가지도 못하고 로컬에서 실패한다.

둘째, k3d에서 브라우저로 접속하려면 포트 매핑이 필요하다.

```bash
k3d cluster create hello-cluster -p "80:80@loadbalancer"
```

이 설정이 있어야 맥북의 `localhost:80` 요청이 k3d 클러스터 안으로 들어갈 수 있다.

셋째, Ingress는 단독으로 동작하지 않는다.

```text
Ingress Controller
Ingress
Service
Pod
```

이 네 가지가 연결되어야 브라우저에서 정상 페이지를 볼 수 있다.

## 정리

`error: the path "nginx-ingress.yaml" does not exist`는 Kubernetes 문제가 아니라 현재 디렉토리에 YAML 파일이 없어서 발생한 파일 경로 문제였다. 파일을 현재 위치에 만들고 `k apply -f nginx-ingress.yaml`을 실행하자 Ingress 리소스는 정상적으로 생성되었다. 이후 브라우저에서 `localhost` 접속 시 `ERR_CONNECTION_REFUSED`가 발생했는데, 이는 k3d 클러스터 생성 시 `80:80@loadbalancer` 포트 매핑이 없어서 로컬 80번 포트가 클러스터의 ingress-nginx까지 연결되지 않았기 때문이다. 기존 `hello-cluster`가 이미 존재했기 때문에 같은 이름으로 다시 만들 수 없었고, 실습 환경에서는 기존 클러스터를 삭제한 뒤 포트 매핑을 포함해서 다시 생성하는 방식으로 해결할 수 있다. 그다음 나타난 `503 Service Temporarily Unavailable`은 요청이 ingress-nginx controller까지 도달했다는 뜻이지만, Ingress 뒤쪽의 Service 또는 Pod 연결이 제대로 되지 않았다는 의미다. 따라서 최종적으로는 Ingress의 backend service 이름과 port, 실제 Service 존재 여부, Service의 Endpoints, Pod Running 상태를 확인해야 한다.
