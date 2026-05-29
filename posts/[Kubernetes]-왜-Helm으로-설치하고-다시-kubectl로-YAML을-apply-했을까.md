---
title: "[KUBERNETES] 왜 Helm으로 설치하고, 다시 kubectl로 YAML을 apply 했을까?"
source: "https://velog.io/@yorange50/KUBERNETES-왜-Helm으로-설치하고-다시-kubectl로-YAML을-apply-했을까"
published: "2026-05-13T05:34:28.127Z"
tags: ""
backup_date: "2026-05-29T14:52:52.746280"
---

Helm = 큰 시스템 설치
kubectl apply = 내 규칙 추가


1. Helm으로 ingress-nginx 설치
   → 요청을 받아서 처리할 관리자 설치

2. nginx Deployment 만들기
   → 실제 응답할 웹서버 만들기

3. Service 만들기
   → nginx Pod로 가는 입구 만들기

4. Ingress YAML apply
   → localhost 요청을 nginx Service로 보내라는 규칙 추가
   
   
   
 브라우저
  ↓
localhost:80
  ↓
ingress-nginx controller   ← Helm으로 설치
  ↓
Ingress 규칙               ← kubectl apply
  ↓
Service                   ← kubectl expose
  ↓
Pod                       ← kubectl create deployment




Kubernetes에서 Ingress를 실습하다 보면 이런 흐름을 만나게 된다.

```sh
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

그리고 그다음에 또 이런 명령어를 친다.

```sh
kubectl apply -f nginx-ingress.yaml
```

처음 보면 헷갈린다.

“이미 Helm으로 ingress-nginx를 설치했는데, 왜 또 YAML을 kubectl로 apply 하지?”
“Helm이랑 kubectl이 둘 다 뭔가 생성하는 거 아닌가?”
“그럼 둘 중 하나만 쓰면 되는 거 아닌가?”

결론부터 말하면, **Helm과 kubectl로 한 작업은 서로 역할이 다르다.**

```text
Helm으로 ingress-nginx 설치
→ Ingress를 처리해주는 Controller 설치

kubectl apply로 nginx-ingress.yaml 적용
→ 그 Controller가 읽을 라우팅 규칙 생성
```

쉽게 말하면 이렇다.

```text
Helm = 라우터 설치
kubectl apply = 라우터 설정표 등록
```

## Ingress를 쓰려면 두 가지가 필요하다

Ingress를 이해할 때 가장 먼저 구분해야 하는 것이 있다.

```text
Ingress Controller
Ingress Resource
```

이 둘은 이름이 비슷해서 헷갈리지만, 역할이 다르다.

```text
Ingress Controller
= 실제로 트래픽을 받아서 처리하는 실행 주체

Ingress Resource
= 어떤 요청을 어떤 Service로 보낼지 적어둔 규칙
```

즉, Ingress Resource는 “규칙”이고, Ingress Controller는 그 규칙을 읽고 실제로 트래픽을 보내주는 “실행 담당자”다.

비유하면 이렇다.

```text
Ingress Controller = 라우터
Ingress Resource = 라우터 설정표
```

라우터 장비만 있다고 해서 자동으로 내가 원하는 곳으로 요청이 가는 것은 아니다.
라우터에 “이 주소로 들어오면 이 서버로 보내라”는 설정이 있어야 한다.

반대로 설정표만 있어도 실제로 요청을 받아 처리할 라우터가 없으면 동작하지 않는다.

그래서 둘 다 필요하다.

## Helm으로 한 일: ingress-nginx Controller 설치

먼저 실행한 명령어는 이것이었다.

```sh
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

이 명령어는 Ingress 규칙 하나를 만드는 명령어가 아니다.

정확히는 **ingress-nginx Controller를 설치하는 명령어**다.

즉, Kubernetes 클러스터 안에 외부 요청을 받아 Ingress 규칙대로 Service에 전달해주는 시스템을 설치한 것이다.

Helm을 쓰면 단순히 Pod 하나만 만들어지는 것이 아니다. Chart 안에 들어 있는 여러 Kubernetes 리소스들이 한 번에 생성된다.

예를 들면 ingress-nginx Chart는 대략 이런 리소스들을 만든다.

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

이게 Helm을 쓰는 이유다.

ingress-nginx Controller는 단순한 nginx Pod 하나가 아니다.
클러스터 안에서 Ingress 리소스를 계속 감시해야 하고, Service와 Endpoint 정보를 확인해야 하며, 외부 요청도 받아야 한다.

그러려면 권한도 필요하고, 설정도 필요하고, Service도 필요하다.

그래서 직접 YAML을 하나하나 작성하기보다 Helm Chart로 설치하는 것이다.

```text
Helm Chart
= 여러 Kubernetes 리소스를 하나의 패키지로 묶어둔 것
```

즉, 이 명령어는:

```sh
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

다음 의미에 가깝다.

```text
ingress-nginx Controller를 운영하는 데 필요한 리소스 세트를 한 번에 설치해라
```

## 하지만 Controller만 있다고 끝이 아니다

Helm으로 ingress-nginx Controller를 설치하면, 클러스터에는 요청을 처리할 수 있는 시스템이 생긴다.

하지만 아직 이런 규칙은 없다.

```text
localhost로 들어온 요청을 nginx Service로 보내라
```

즉, Controller는 준비됐지만, Controller가 읽을 라우팅 규칙이 없는 상태다.

이 상태를 비유하면 이렇다.

```text
라우터는 설치했는데,
아직 라우팅 설정을 안 넣은 상태
```

그래서 다음 단계로 직접 Ingress YAML을 작성하고 적용한 것이다.

## kubectl apply로 한 일: Ingress 규칙 생성

다음에 실행한 명령어는 이것이다.

```sh
kubectl apply -f nginx-ingress.yaml
```

이 명령어는 `nginx-ingress.yaml` 파일에 적힌 Kubernetes 리소스를 클러스터에 적용한다.

이 파일 안에는 보통 이런 내용이 들어간다.

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

즉, 이 YAML은 ingress-nginx Controller를 설치하는 YAML이 아니다.
이미 설치된 Controller가 읽을 **Ingress 규칙**을 만드는 YAML이다.

이 규칙의 의미는 다음과 같다.

```text
host가 localhost이고
path가 /이면
nginx Service의 80번 포트로 보내라
```

정리하면 이렇다.

```text
helm install ingress-nginx ...
= Ingress Controller 설치

kubectl apply -f nginx-ingress.yaml
= Ingress 라우팅 규칙 생성
```

## 전체 요청 흐름으로 이해하기

브라우저에서 `localhost`로 접속했을 때 요청 흐름은 다음과 같다.

```text
브라우저
→ localhost:80
→ k3d LoadBalancer
→ ingress-nginx Controller
→ Ingress 규칙
→ Service
→ Pod
```

여기서 Helm으로 만든 것은 이 부분이다.

```text
ingress-nginx Controller
```

그리고 kubectl apply로 만든 것은 이 부분이다.

```text
Ingress 규칙
```

전체 구조로 보면 다음과 같다.

```text
[브라우저]
    ↓
[localhost:80]
    ↓
[k3d LoadBalancer]
    ↓
[ingress-nginx Controller]  ← Helm으로 설치
    ↓
[nginx-ingress]             ← kubectl apply로 생성
    ↓
[nginx Service]
    ↓
[nginx Pod]
```

이 구조를 보면 왜 둘 다 필요한지 이해된다.

Helm으로 Controller만 설치하면 요청을 처리할 주체는 생긴다.
하지만 어떤 host와 path를 어떤 Service로 보낼지 모른다.

kubectl로 Ingress만 만들면 규칙은 생긴다.
하지만 그 규칙을 실제로 읽고 처리할 Controller가 없으면 동작하지 않는다.

## 버스 터미널 비유로 이해하기

조금 더 쉽게 비유하면 이렇다.

```text
Helm으로 ingress-nginx 설치
= 버스 터미널, 기사, 노선 관리 시스템 설치

kubectl apply -f nginx-ingress.yaml
= “localhost로 온 손님은 nginx행 버스에 태워라”라는 노선표 등록
```

버스 터미널만 있다고 해서 손님이 자동으로 목적지에 가는 것은 아니다.
어떤 손님을 어느 버스에 태울지 노선표가 있어야 한다.

반대로 노선표만 있어도 버스 터미널과 기사가 없으면 손님을 이동시킬 수 없다.

Ingress도 같다.

```text
Ingress Controller만 있음
→ 규칙이 없어서 어디로 보낼지 모름

Ingress 규칙만 있음
→ 규칙을 실행할 Controller가 없어서 동작하지 않음
```

그래서 실습에서 두 작업을 순서대로 한 것이다.

## 그럼 Helm으로 Ingress까지 만들 수는 없을까?

가능하다.

Helm은 Kubernetes 리소스 여러 개를 하나의 Chart로 묶어서 설치하는 도구다.

그래서 내가 만든 애플리케이션도 Helm Chart로 만들면 다음 리소스들을 한 번에 설치할 수 있다.

```text
my-app Helm Chart
 ├── Deployment
 ├── Service
 ├── ConfigMap
 └── Ingress
```

이렇게 만들면 명령어 하나로 애플리케이션 전체를 배포할 수 있다.

```sh
helm install my-app ./my-app-chart
```

그러면 Deployment, Service, Ingress가 한 번에 생성된다.

실무에서는 애플리케이션 배포도 Helm으로 관리하는 경우가 많다.

하지만 이번 실습에서는 역할을 나눠서 이해하는 것이 목적이었다.

```text
공식 Helm Chart로 ingress-nginx Controller 설치
직접 YAML로 Ingress 규칙 생성
```

이렇게 나눠서 해보면 Controller와 Resource의 차이가 명확해진다.

## kubectl과 Helm의 역할 차이

둘 다 Kubernetes 리소스를 만들 수 있지만, 사용 목적이 다르다.

| 구분    | kubectl                               | Helm                                                     |
| ----- | ------------------------------------- | -------------------------------------------------------- |
| 역할    | Kubernetes 리소스를 직접 생성/수정              | 여러 리소스를 패키지로 설치/관리                                       |
| 단위    | YAML 파일                               | Chart                                                    |
| 사용 예시 | Ingress 규칙 적용                         | ingress-nginx Controller 설치                              |
| 명령어   | `kubectl apply -f nginx-ingress.yaml` | `helm install ingress-nginx ingress-nginx/ingress-nginx` |
| 느낌    | 직접 리소스 하나씩 적용                         | 앱 설치 패키지 실행                                              |

이번 실습에 대입하면 다음과 같다.

```text
kubectl
= 내가 작성한 Ingress YAML을 적용하는 도구

Helm
= ingress-nginx Controller에 필요한 여러 리소스를 한 번에 설치하는 도구
```

## 헷갈리기 쉬운 이름 정리

이번 실습에서는 `nginx`라는 이름이 여러 번 나온다.

이 부분 때문에 더 헷갈릴 수 있다.

```text
ingress-nginx
= Ingress Controller 이름

nginx-ingress
= 내가 만든 Ingress 리소스 이름

nginx
= 테스트용 웹 서버 Deployment/Service 이름
```

각각 역할은 다르다.

```text
ingress-nginx Controller
= 요청을 받아 라우팅하는 컨트롤러

nginx-ingress
= localhost 요청을 어디로 보낼지 적은 규칙

nginx Service/Pod
= 실제 응답을 반환하는 백엔드 앱
```

즉, `ingress-nginx`와 `nginx-ingress`는 같은 것이 아니다.

이름이 비슷할 뿐 역할이 다르다.

## 503 에러와도 연결된다

실습 중 `localhost`로 접속했을 때 이런 화면이 나왔다.

```text
503 Service Temporarily Unavailable
nginx
```

이건 중요한 의미가 있다.

503이 떴다는 것은 요청이 적어도 ingress-nginx Controller까지는 도달했다는 뜻이다.

즉, Helm으로 설치한 Controller는 동작하고 있었다.

하지만 Controller가 Ingress 규칙을 따라 뒤쪽 Service나 Pod로 요청을 넘기지 못한 것이다.

주로 이런 경우에 발생한다.

```text
Ingress에 적은 Service 이름이 실제 Service 이름과 다름
Ingress에 적은 Service port가 실제 Service port와 다름
Service는 있는데 연결된 Pod가 없음
Service selector와 Pod label이 맞지 않음
Pod가 Running 상태가 아님
```

따라서 503이 떴을 때는 Helm 설치만 다시 볼 게 아니라, Ingress 뒤쪽 연결을 봐야 한다.

```sh
kubectl get pods
kubectl get svc
kubectl get ingress
kubectl describe ingress nginx-ingress
kubectl describe svc nginx
```

특히 Service의 `Endpoints`가 중요하다.

```text
Endpoints: <none>
```

이면 Service가 연결할 Pod를 못 찾고 있다는 뜻이다.

## 정리

Helm으로 `ingress-nginx`를 설치하고, 그다음 `kubectl apply -f nginx-ingress.yaml`을 실행한 이유는 두 작업의 역할이 다르기 때문이다. Helm으로 설치한 것은 Ingress 규칙을 실제로 처리하는 `ingress-nginx Controller`이고, kubectl로 적용한 YAML은 그 Controller가 읽을 `Ingress 라우팅 규칙`이다. Helm은 라우터를 설치한 것이고, kubectl apply는 라우터 설정표를 등록한 것이다. 브라우저 요청이 Pod까지 도달하려면 `ingress-nginx Controller`, `Ingress`, `Service`, `Pod`가 모두 연결되어 있어야 한다. 따라서 둘 중 하나만으로는 전체 Ingress 흐름이 완성되지 않는다. 실무에서는 애플리케이션의 Deployment, Service, Ingress까지 Helm Chart로 묶어 한 번에 배포할 수도 있지만, 처음 학습할 때는 Controller는 Helm으로 설치하고 Ingress 규칙은 직접 YAML로 적용하면서 역할 차이를 분리해서 이해하는 것이 좋다.
