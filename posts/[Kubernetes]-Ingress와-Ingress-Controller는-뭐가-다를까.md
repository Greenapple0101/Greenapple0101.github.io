---
title: "[KUBERNETES] Ingress와 Ingress Controller는 뭐가 다를까?"
source: "https://velog.io/@yorange50/KUBERNETES-Ingress와-Ingress-Controller는-뭐가-다를까"
published: "2026-05-17T11:54:28.070Z"
tags: ""
backup_date: "2026-05-29T14:52:52.731622"
---

쿠버네티스에서 외부 요청을 서비스로 연결할 때 `Service`만 쓰는 게 아니라 `Ingress`라는 것도 자주 등장한다.

처음 보면 이름이 비슷해서 헷갈린다.

```text
Ingress
Ingress Controller
```

둘 다 외부 요청을 내부 서비스로 보내는 것 같고, 둘 다 라우팅과 관련 있어 보인다.

그런데 핵심은 이것이다.

```text
Ingress
= 라우팅 규칙을 적어둔 Kubernetes 리소스

Ingress Controller
= 그 규칙을 실제로 읽고 동작시키는 실행 주체
```

조금 더 쉽게 말하면:

```text
Ingress
= 설정서

Ingress Controller
= 설정서를 읽고 실제로 요청을 처리하는 서버
```

Kubernetes 공식 문서에서도 Ingress는 외부에서 클러스터 내부 서비스로 들어오는 HTTP/HTTPS 라우팅 규칙을 정의하는 리소스이고, 실제 구현은 Ingress Controller가 담당한다고 설명한다. ([Kubernetes][1])

---

# 1. Ingress란?

Ingress는 Kubernetes 리소스다.

즉 `Pod`, `Service`, `Deployment`처럼 YAML로 만드는 오브젝트다.

예를 들어 이런 YAML이 Ingress다.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
```

이 YAML의 의미는 이렇다.

```text
example.com/ 으로 들어오면
→ frontend-service로 보내라

example.com/api 로 들어오면
→ backend-service로 보내라
```

즉 Ingress는 직접 요청을 처리하는 서버가 아니다.

Ingress는 그냥 Kubernetes API Server에 저장된 **라우팅 규칙**이다.

---

# 2. Ingress만 만들면 바로 동작할까?

아니다.

이게 제일 중요한 부분이다.

Ingress 리소스만 만들면 외부 요청이 자동으로 서비스로 전달되는 게 아니다.

예를 들어 내가 이런 Ingress를 만들었다고 하자.

```text
/api → backend-service
```

그런데 클러스터 안에 Ingress Controller가 없으면 아무 일도 일어나지 않는다.

왜냐하면 Ingress는 그냥 규칙이기 때문이다.

```text
Ingress
= “/api는 backend-service로 보내세요”라고 적힌 문서
```

이 문서를 읽고 실제로 요청을 받아주는 애가 필요하다.

그게 바로 Ingress Controller다.

---

# 3. Ingress Controller란?

Ingress Controller는 실제로 클러스터 외부에서 들어오는 요청을 받아서 내부 서비스로 보내는 컴포넌트다.

대표적으로 이런 것들이 있다.

```text
NGINX Ingress Controller
Traefik
HAProxy Ingress
Kong Ingress Controller
AWS Load Balancer Controller
GCE Ingress Controller
```

Ingress Controller는 보통 클러스터 안에서 Pod로 실행된다.

그리고 Kubernetes API Server를 계속 감시한다.

```text
Ingress Controller:
“새로운 Ingress 리소스가 생겼나?”
“기존 Ingress 규칙이 바뀌었나?”
“Service나 Endpoint가 바뀌었나?”
```

이렇게 감시하다가 Ingress 규칙이 생기면, 그 규칙에 맞게 자신이 가진 프록시 설정을 바꾼다.

예를 들어 NGINX Ingress Controller라면 Ingress 규칙을 읽고 Nginx 설정으로 변환한다. Ingress-NGINX는 NGINX를 reverse proxy와 load balancer로 사용하는 Kubernetes용 Ingress Controller다. ([GitHub][2])

---

# 4. 전체 작동 흐름

Ingress와 Ingress Controller의 작동 흐름은 이렇게 보면 된다.

```text
1. 개발자가 Ingress YAML을 작성한다
2. kubectl apply로 Ingress 리소스를 생성한다
3. Kubernetes API Server에 Ingress 규칙이 저장된다
4. Ingress Controller가 API Server를 감시하다가 Ingress를 발견한다
5. Ingress Controller가 해당 규칙을 자신의 프록시 설정으로 반영한다
6. 외부 사용자가 도메인으로 접속한다
7. 요청이 Ingress Controller로 들어온다
8. Ingress Controller가 규칙에 따라 Service로 요청을 보낸다
9. Service가 실제 Pod로 트래픽을 전달한다
```

그림으로 보면 이렇다.

```text
사용자
  ↓
example.com/api
  ↓
Ingress Controller
  ↓
Ingress 규칙 확인
  ↓
backend-service
  ↓
backend Pod
```

조금 더 Kubernetes스럽게 보면:

```text
Client
  ↓
LoadBalancer / NodePort
  ↓
Ingress Controller Pod
  ↓
Service
  ↓
Pod
```

---

# 5. Ingress와 Ingress Controller 비교

| 구분    | Ingress                  | Ingress Controller       |
| ----- | ------------------------ | ------------------------ |
| 정체    | Kubernetes API 리소스       | 실제로 동작하는 컨트롤러/프록시        |
| 역할    | 라우팅 규칙 정의                | 규칙을 읽고 요청을 실제로 전달        |
| 실행 여부 | 실행되는 프로그램 아님             | Pod 또는 외부 로드밸런서 형태로 실행   |
| 예시    | `/api → backend-service` | NGINX Ingress Controller |
| 없으면?  | 규칙 자체가 없음                | 규칙은 있어도 아무도 처리하지 않음      |
| 비유    | 주문서                      | 주문서를 보고 요리하는 주방          |

가장 중요한 차이는 이거다.

```text
Ingress는 “어떻게 보낼지”를 정의한다.
Ingress Controller는 “실제로 보낸다.”
```

---

# 6. Service와는 뭐가 다를까?

Ingress를 이해하려면 Service와의 차이도 같이 봐야 한다.

Service는 Pod 앞에 고정된 접근 지점을 만들어준다.

```text
Service
= Pod로 가는 내부 고정 입구
```

예를 들어 backend Pod가 여러 개 있어도 Service는 하나의 이름으로 접근하게 해준다.

```text
backend-service
  ├─ backend-pod-1
  ├─ backend-pod-2
  └─ backend-pod-3
```

그런데 Service만으로 외부 HTTP 라우팅을 세밀하게 관리하기는 어렵다.

예를 들어 이런 요청 분기는 Service만으로 깔끔하게 하기 어렵다.

```text
example.com/      → frontend-service
example.com/api   → backend-service
admin.example.com → admin-service
```

이런 HTTP/HTTPS 기반 라우팅을 담당하는 것이 Ingress다.

정리하면:

```text
Service
= Pod 앞의 고정 입구

Ingress
= 외부 HTTP 요청을 어떤 Service로 보낼지 정하는 규칙

Ingress Controller
= 그 규칙을 실제로 실행하는 프록시
```

---

# 7. 실제 요청은 어디로 들어올까?

여기서 헷갈리는 포인트가 하나 있다.

“사용자 요청이 Ingress 리소스로 들어가는 건가?”

아니다.

사용자 요청은 Ingress 리소스로 들어가지 않는다.

Ingress는 YAML로 만든 규칙일 뿐이다.

실제 요청은 Ingress Controller로 들어간다.

```text
틀린 이해:
사용자 → Ingress → Service → Pod

정확한 이해:
사용자 → Ingress Controller → Service → Pod
              ↑
          Ingress 규칙을 읽음
```

Ingress는 트래픽이 지나가는 통로가 아니라, Ingress Controller가 참고하는 설정값이다.

---

# 8. Ingress Controller는 어떻게 규칙을 반영할까?

Ingress Controller는 Kubernetes API Server를 계속 watch한다.

```text
watch Ingress
watch Service
watch Endpoint 또는 EndpointSlice
watch Secret
```

왜 Secret도 보냐면 HTTPS 인증서가 Secret에 저장되는 경우가 많기 때문이다.

예를 들어 TLS 설정이 있는 Ingress는 이런 식이다.

```yaml
spec:
  tls:
  - hosts:
    - example.com
    secretName: example-tls
```

그러면 Ingress Controller는 `example-tls` Secret을 읽어서 HTTPS 인증서 설정에 반영한다.

즉 Ingress Controller는 단순히 Ingress만 보는 게 아니라, 라우팅에 필요한 여러 Kubernetes 리소스를 함께 본다.

```text
Ingress
= 어떤 host/path를 어떤 Service로 보낼지

Service
= 어떤 Pod 집합으로 보낼지

Endpoint/EndpointSlice
= 실제 Pod IP 목록

Secret
= HTTPS 인증서 정보
```

---

# 9. NGINX Ingress Controller 기준 흐름

NGINX Ingress Controller를 예로 들면 작동 방식은 이렇게 볼 수 있다.

```text
1. NGINX Ingress Controller가 Pod로 떠 있음
2. Kubernetes API Server를 감시함
3. Ingress 리소스가 생성됨
4. Controller가 Ingress 규칙을 읽음
5. NGINX 설정으로 변환함
6. NGINX가 외부 요청을 받음
7. 요청 path/host에 따라 Service로 프록시함
```

예를 들어 Ingress에 이런 규칙이 있다고 하자.

```text
example.com/api → backend-service
```

그러면 NGINX Ingress Controller는 내부적으로 이런 식의 설정을 만든다고 이해하면 된다.

```nginx
server {
    server_name example.com;

    location /api {
        proxy_pass http://backend-service;
    }
}
```

물론 실제 설정은 더 복잡하지만, 개념적으로는 이렇다.

즉 Ingress YAML이 바로 Nginx 설정이 되는 게 아니라:

```text
Ingress YAML
→ Ingress Controller가 읽음
→ NGINX 설정으로 변환
→ NGINX가 요청 처리
```

이 흐름이다.

Ingress-NGINX 계열은 ConfigMap, annotation, custom template 등을 통해 NGINX 동작을 조정할 수 있다. ([Kubernetes][3])

---

# 10. ingressClassName은 왜 필요할까?

Ingress YAML을 보면 이런 필드가 있다.

```yaml
spec:
  ingressClassName: nginx
```

이건 “이 Ingress 규칙을 어떤 Ingress Controller가 처리할 것인가”를 지정하는 값이다.

왜 필요할까?

클러스터 안에는 Ingress Controller가 여러 개 있을 수 있다.

```text
nginx ingress controller
traefik ingress controller
aws load balancer controller
```

그러면 Kubernetes 입장에서는 어떤 컨트롤러가 어떤 Ingress를 처리해야 하는지 구분해야 한다.

그래서 IngressClass를 사용한다.

```text
ingressClassName: nginx
→ nginx Ingress Controller가 처리

ingressClassName: alb
→ AWS Load Balancer Controller가 처리
```

Kubernetes 공식 문서에서도 여러 Ingress Controller를 배포할 수 있고, Ingress 리소스에서 `ingressClassName`을 지정해 어떤 컨트롤러가 처리할지 명시한다고 설명한다. ([Kubernetes][4])

---

# 11. Ingress Controller를 설치해야 하는 이유

Kubernetes에 Ingress라는 리소스 종류는 기본으로 있다.

그래서 이런 명령어는 가능하다.

```bash
kubectl apply -f ingress.yaml
```

하지만 Ingress Controller는 클러스터에 기본으로 항상 설치되어 있는 것이 아니다.

환경에 따라 직접 설치해야 한다.

예를 들어 k3d나 로컬 Kubernetes에서 NGINX Ingress Controller를 Helm으로 설치할 수 있다.

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

이 명령어는 Ingress 리소스를 만드는 게 아니라, Ingress 규칙을 실제로 처리할 컨트롤러를 설치하는 것이다.

즉:

```text
Helm으로 설치하는 것
= Ingress Controller

내가 YAML로 만드는 것
= Ingress
```

---

# 12. 예시로 전체 흐름 보기

먼저 백엔드 Deployment와 Service가 있다고 하자.

```text
backend Deployment
→ backend Pod 생성

backend Service
→ backend Pod로 가는 고정 입구 생성
```

그다음 Ingress를 만든다.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
```

이 Ingress는 이렇게 말하는 것이다.

```text
example.com/api 요청은 backend-service로 보내라
```

그러면 Ingress Controller가 이 규칙을 읽는다.

```text
Ingress Controller:
“아, example.com/api는 backend-service로 보내면 되는구나”
```

이후 사용자가 접속한다.

```text
사용자 → example.com/api
```

실제 흐름은 이렇게 된다.

```text
사용자
  ↓
Ingress Controller
  ↓
backend-service
  ↓
backend Pod
```

---

# 13. Ingress만 있고 Controller가 없으면?

이 상황을 면접에서 물어볼 수도 있다.

```text
Ingress 리소스를 만들었는데 Ingress Controller가 없으면 어떻게 되나요?
```

답은 이렇다.

```text
Ingress YAML은 Kubernetes API Server에 저장되지만,
그 규칙을 실제로 처리할 컨트롤러가 없기 때문에
외부 요청은 서비스로 라우팅되지 않는다.
```

즉 Ingress는 존재하지만, 아무도 실행하지 않는 상태다.

비유하면:

```text
Ingress
= 배달 주소와 주문서를 적어둠

Ingress Controller 없음
= 주문서를 읽고 배달할 사람이 없음
```

---

# 14. Ingress Controller만 있고 Ingress가 없으면?

반대로 Ingress Controller만 있고 Ingress 리소스가 없으면 어떨까?

```text
Ingress Controller는 떠 있지만,
적용할 라우팅 규칙이 없다.
```

즉 요청을 받아도 어떤 서비스로 보내야 하는지 모른다.

비유하면:

```text
Ingress Controller
= 배달 기사는 있음

Ingress 없음
= 어디로 배달해야 할지 적힌 주문서가 없음
```

그래서 둘은 같이 있어야 한다.

```text
Ingress
= 규칙

Ingress Controller
= 실행자
```

---

# 15. 면접 답변식

면접에서 “Ingress와 Ingress Controller 차이가 뭐예요?”라고 물어보면 이렇게 답하면 좋다.

```text
Ingress는 Kubernetes에서 HTTP/HTTPS 트래픽을 어떤 Service로 보낼지 정의하는 API 리소스입니다.

예를 들어 example.com/api 요청은 backend-service로 보내라는 host/path 기반 라우팅 규칙을 YAML로 선언합니다.

하지만 Ingress 자체는 실제 트래픽을 처리하지 않고, 이 규칙을 실제로 적용하는 주체가 Ingress Controller입니다.

Ingress Controller는 클러스터 내에서 실행되면서 API Server를 감시하고, Ingress 리소스가 생성되거나 변경되면 해당 규칙을 Nginx 같은 reverse proxy 설정으로 반영합니다.

실제 외부 요청은 Ingress 리소스가 아니라 Ingress Controller로 들어오고, Controller가 Ingress 규칙에 따라 Service와 Pod로 요청을 전달합니다.
```

조금 더 짧게 말하면:

```text
Ingress는 라우팅 규칙이고, Ingress Controller는 그 규칙을 실제로 수행하는 reverse proxy입니다.
```

---

# 16. 프로젝트 기준으로 말하면

네가 k3d나 Kubernetes 실습에서 NGINX Ingress Controller를 Helm으로 설치하고, nginx 테스트 앱을 Ingress로 노출했다면 이렇게 말할 수 있다.

```text
Kubernetes에서 외부 요청을 서비스로 라우팅하기 위해 Ingress와 NGINX Ingress Controller를 사용했습니다.

먼저 Helm으로 NGINX Ingress Controller를 설치해서 외부 요청을 받을 수 있는 프록시 계층을 만들었습니다.

그 다음 Ingress 리소스를 작성해서 특정 host와 path 요청이 nginx Service로 전달되도록 설정했습니다.

즉 Ingress는 라우팅 규칙이고, Ingress Controller는 그 규칙을 읽어서 실제 요청을 Service로 전달하는 역할을 했습니다.
```

---

# 17. 핵심 정리

```text
Ingress
= Kubernetes 리소스
= host/path 기반 라우팅 규칙
= 직접 요청을 처리하지 않음

Ingress Controller
= 실제로 실행되는 컨트롤러
= 보통 reverse proxy/load balancer 역할
= Ingress 규칙을 읽고 Service로 요청 전달
```

전체 흐름은 이렇다.

```text
사용자
  ↓
Ingress Controller
  ↓
Ingress 규칙 참고
  ↓
Service
  ↓
Pod
```

한 줄로 정리하면:

```text
Ingress는 “어디로 보낼지 적어둔 규칙”이고,
Ingress Controller는 “그 규칙대로 실제 요청을 보내는 실행자”다.
```

[1]: https://kubernetes.io/docs/concepts/services-networking/ingress/?utm_source=chatgpt.com "Ingress"
[2]: https://github.com/kubernetes/ingress-nginx?utm_source=chatgpt.com "Ingress NGINX Controller for Kubernetes"
[3]: https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/?utm_source=chatgpt.com "Introduction - Ingress-Nginx Controller"
[4]: https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/?utm_source=chatgpt.com "Ingress Controllers"