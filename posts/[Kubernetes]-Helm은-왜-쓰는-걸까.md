---
title: "[KUBERNETES] Helm은 왜 쓰는 걸까?"
source: "https://velog.io/@yorange50/KUBERNETES-Helm은-왜-쓰는-걸까"
published: "2026-05-13T05:01:32.267Z"
tags: ""
backup_date: "2026-05-29T14:52:52.748005"
---



쿠버네티스를 공부하다 보면 처음에는 `Pod`, `Deployment`, `Service` 같은 YAML을 직접 작성하게 된다.

예를 들어 애플리케이션 하나를 배포하려면 보통 이런 리소스들이 필요하다.

```text
Deployment
Service
ConfigMap
Secret
Ingress
ServiceAccount
Role
RoleBinding
PersistentVolumeClaim
```

처음에는 하나씩 작성하면서 배우는 게 좋다. 그런데 실무에서는 앱 하나를 배포할 때 YAML 파일이 너무 많아진다.

이때 등장하는 도구가 **Helm**이다.

## Helm이란?

**Helm은 Kubernetes의 패키지 매니저**다.

조금 쉽게 말하면, 쿠버네티스 애플리케이션을 설치하고 관리하기 쉽게 만들어주는 도구다.

Docker에서 이미지를 받아 컨테이너를 실행하듯이, Kubernetes에서는 Helm Chart를 이용해서 복잡한 애플리케이션을 쉽게 설치할 수 있다.

```text
Docker 이미지 → 컨테이너 실행
Helm Chart → Kubernetes 리소스 설치
```

예를 들어 `ingress-nginx`를 직접 설치한다고 하면 여러 개의 YAML 파일이 필요하다.

```text
Deployment
Service
ConfigMap
IngressClass
ServiceAccount
ClusterRole
ClusterRoleBinding
Admission Webhook 관련 리소스
```

이걸 하나하나 직접 작성하고 적용하려면 꽤 복잡하다.

하지만 Helm을 쓰면 명령어 몇 줄로 설치할 수 있다.

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx
```

즉, Helm은 복잡한 Kubernetes 리소스 묶음을 쉽게 설치하게 해주는 도구다.

## Helm Chart란?

Helm에서 가장 중요한 개념은 **Chart**다.

**Chart는 Kubernetes 리소스들을 하나의 패키지로 묶어둔 것**이다.

예를 들어 어떤 애플리케이션을 배포하기 위해 다음 리소스들이 필요하다고 해보자.

```text
Deployment
Service
Ingress
ConfigMap
Secret
PVC
```

이 YAML들을 하나의 묶음으로 패키징한 것이 Helm Chart다.

```text
Helm Chart
 ├── Deployment YAML
 ├── Service YAML
 ├── Ingress YAML
 ├── ConfigMap YAML
 └── values.yaml
```

즉, Chart는 쿠버네티스 앱 설치 설명서이자 템플릿 묶음이라고 볼 수 있다.

## Helm이 해결하는 문제

쿠버네티스에서는 모든 것을 YAML로 정의한다.

이 방식은 명확하지만, 앱이 조금만 커져도 관리가 힘들어진다.

예를 들어 같은 애플리케이션을 개발 환경과 운영 환경에 배포한다고 해보자.

개발 환경에서는 replica가 1개면 충분하다.

```yaml
replicaCount: 1
```

운영 환경에서는 replica가 3개 이상 필요할 수 있다.

```yaml
replicaCount: 3
```

이미지 태그도 다를 수 있다.

```yaml
image:
  tag: dev
```

```yaml
image:
  tag: v1.0.0
```

Service 타입도 다를 수 있다.

```yaml
service:
  type: ClusterIP
```

```yaml
service:
  type: LoadBalancer
```

이걸 YAML 파일을 복사해서 환경별로 따로 관리하면 중복이 많아진다.

Helm은 이 문제를 `values.yaml`로 해결한다.

## values.yaml이란?

`values.yaml`은 Helm Chart에서 설정값을 따로 빼놓은 파일이다.

예를 들어 Chart 안에 Deployment 템플릿이 있다고 하자.

```yaml
replicas: {{ .Values.replicaCount }}
```

여기서 실제 값은 `values.yaml`에서 가져온다.

```yaml
replicaCount: 3
```

그러면 Helm이 설치할 때 이 값을 넣어서 최종 Kubernetes YAML을 만들어준다.

즉, Helm은 템플릿과 설정값을 조합해서 Kubernetes 리소스를 생성한다.

```text
templates/*.yaml + values.yaml
= 최종 Kubernetes YAML
```

이 구조 덕분에 같은 Chart를 쓰면서도 환경별 설정만 다르게 줄 수 있다.

```bash
helm install my-app ./my-chart -f values-dev.yaml
```

```bash
helm install my-app ./my-chart -f values-prod.yaml
```

## Helm Release란?

Helm에서 또 중요한 개념은 **Release**다.

**Release는 Chart를 Kubernetes 클러스터에 설치한 결과물**이다.

예를 들어 `ingress-nginx` Chart를 설치한다고 해보자.

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx
```

여기서 앞의 `ingress-nginx`는 Release 이름이다.

```text
Chart = 설치 패키지
Release = 그 패키지를 실제 클러스터에 설치한 결과
```

같은 Chart를 여러 번 설치하면 서로 다른 Release가 될 수 있다.

```bash
helm install dev-nginx ingress-nginx/ingress-nginx
helm install prod-nginx ingress-nginx/ingress-nginx
```

둘 다 같은 Chart를 사용하지만 Release 이름이 다르기 때문에 별개의 설치 결과로 관리된다.

## Helm 기본 명령어

Helm에서 자주 쓰는 명령어는 다음과 같다.

### Chart 저장소 추가

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
```

Helm Chart가 있는 저장소를 추가하는 명령어다.

### Chart 저장소 업데이트

```bash
helm repo update
```

로컬에 저장된 Chart 목록 정보를 최신 상태로 갱신한다.

### Chart 설치

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx
```

Chart를 클러스터에 설치한다.

구조는 다음과 같다.

```text
helm install [Release 이름] [Chart 이름]
```

### 설치된 Release 확인

```bash
helm list
```

현재 클러스터에 설치된 Helm Release 목록을 확인한다.

### Release 업그레이드

```bash
helm upgrade ingress-nginx ingress-nginx/ingress-nginx
```

이미 설치된 Release를 새 설정이나 새 Chart 버전으로 업데이트한다.

### 설치 또는 업그레이드

```bash
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx
```

이 명령어는 실무에서 자주 쓴다.

이미 설치되어 있으면 업그레이드하고, 설치되어 있지 않으면 새로 설치한다.

### Release 삭제

```bash
helm uninstall ingress-nginx
```

설치된 Release를 삭제한다.

## Helm을 쓰면 좋은 상황

Helm은 특히 이런 상황에서 유용하다.

```text
YAML 파일이 너무 많을 때
복잡한 오픈소스 앱을 설치할 때
dev, stage, prod 환경별 설정을 나누고 싶을 때
반복 배포를 자동화하고 싶을 때
설치, 업그레이드, 롤백을 관리하고 싶을 때
```

대표적으로 Helm으로 많이 설치하는 것들은 다음과 같다.

```text
ingress-nginx
cert-manager
prometheus
grafana
argo-cd
jenkins
redis
postgresql
mysql
loki
```

이런 것들은 직접 YAML을 작성해서 설치할 수도 있지만, 필요한 리소스가 많고 설정도 복잡하다.

그래서 보통 공식 Chart나 커뮤니티 Chart를 사용한다.

## Helm과 kubectl의 차이

`kubectl`은 Kubernetes 리소스를 직접 다루는 기본 도구다.

```bash
kubectl apply -f deployment.yaml
kubectl get pods
kubectl delete svc my-service
```

반면 Helm은 여러 Kubernetes 리소스를 하나의 패키지 단위로 관리한다.

```bash
helm install my-app ./chart
helm upgrade my-app ./chart
helm uninstall my-app
```

차이를 정리하면 이렇다.

| 구분    | kubectl              | Helm                         |
| ----- | -------------------- | ---------------------------- |
| 역할    | Kubernetes 리소스 직접 관리 | 앱 패키지 설치/관리                  |
| 단위    | YAML 파일              | Chart                        |
| 설정 관리 | 파일을 직접 수정            | values.yaml로 설정 분리           |
| 업데이트  | kubectl apply        | helm upgrade                 |
| 삭제    | 리소스별 삭제              | release 단위 삭제                |
| 사용 예시 | Pod, Service 확인      | ingress-nginx, Prometheus 설치 |

즉, `kubectl`은 기본 조작 도구이고, Helm은 앱 설치와 배포를 편하게 해주는 패키지 관리 도구다.

## Helm을 Docker에 비유하면

처음에는 Helm이 잘 안 와닿을 수 있다.

Docker와 비교하면 조금 이해하기 쉽다.

```text
Docker Hub에서 이미지 받기
→ docker run으로 컨테이너 실행
```

쿠버네티스에서는 이렇게 볼 수 있다.

```text
Helm Repository에서 Chart 받기
→ helm install로 Kubernetes 리소스 설치
```

Docker 이미지가 컨테이너 실행을 위한 패키지라면, Helm Chart는 Kubernetes 앱 설치를 위한 패키지다.

```text
Docker Image = 컨테이너 실행 패키지
Helm Chart = Kubernetes 배포 패키지
```

다만 완전히 같은 개념은 아니다.

Docker 이미지는 애플리케이션 실행 파일과 환경을 담은 결과물이고, Helm Chart는 Kubernetes YAML 템플릿과 설정값을 담은 배포 패키지다.

## ingress-nginx 예시로 보기

`ingress-nginx`를 설치한다고 해보자.

직접 설치하면 여러 리소스가 필요하다.

```text
Namespace
ServiceAccount
ClusterRole
ClusterRoleBinding
ConfigMap
Deployment
Service
IngressClass
ValidatingWebhookConfiguration
Job
```

이걸 전부 직접 관리하기는 번거롭다.

Helm을 쓰면 다음 흐름으로 설치할 수 있다.

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx
```

설치 후 확인은 `kubectl`로 한다.

```bash
kubectl get pods
kubectl get svc
kubectl get ingressclass
```

여기서 중요한 점은 Helm이 설치를 담당하고, kubectl은 상태 확인에 계속 사용된다는 것이다.

```text
Helm = 설치와 관리
kubectl = 조회와 직접 조작
```

## Helm이 실무에서 중요한 이유

실무에서는 같은 앱을 여러 환경에 배포해야 한다.

```text
local
dev
stage
prod
```

환경마다 설정이 다르다.

```text
replica 개수
image tag
resource limit
service type
ingress host
secret 값
autoscaling 설정
```

이걸 YAML 파일로만 관리하면 중복이 많아지고 실수가 생기기 쉽다.

Helm을 쓰면 공통 구조는 Chart에 두고, 환경별 차이는 values 파일로 분리할 수 있다.

```text
my-chart/
 ├── templates/
 ├── values.yaml
 ├── values-dev.yaml
 ├── values-stage.yaml
 └── values-prod.yaml
```

배포할 때는 환경별 values 파일을 지정한다.

```bash
helm upgrade --install my-app ./my-chart -f values-dev.yaml
```

```bash
helm upgrade --install my-app ./my-chart -f values-prod.yaml
```

이렇게 하면 같은 Chart를 재사용하면서 환경별 배포를 관리할 수 있다.

## 주의할 점

Helm은 편하지만, 내부에서 결국 Kubernetes YAML을 생성한다.

그래서 Helm을 쓴다고 해서 Kubernetes 기본 개념을 몰라도 되는 것은 아니다.

예를 들어 Helm 설치가 실패했을 때는 결국 이런 것들을 확인해야 한다.

```bash
kubectl get pods
kubectl describe pod
kubectl logs
kubectl get events
```

Helm은 설치를 쉽게 해주지만, 문제가 생겼을 때 원인을 해석하려면 Kubernetes 리소스 구조를 알아야 한다.

또한 Chart의 기본 설정을 그대로 쓰면 원하지 않는 리소스가 생성될 수 있다.

그래서 중요한 Chart를 설치할 때는 values를 확인하는 습관이 필요하다.

```bash
helm show values ingress-nginx/ingress-nginx
```

이 명령어로 Chart가 제공하는 기본 설정값을 볼 수 있다.

## 정리

Helm은 Kubernetes의 패키지 매니저다. Docker에서 이미지를 받아 컨테이너를 실행하듯이, Kubernetes에서는 Helm Chart를 이용해 복잡한 애플리케이션을 쉽게 설치하고 관리할 수 있다. Chart는 Deployment, Service, ConfigMap, Ingress 같은 Kubernetes 리소스 템플릿을 하나로 묶은 패키지이고, Release는 그 Chart를 실제 클러스터에 설치한 결과다. Helm을 사용하면 ingress-nginx, Prometheus, Grafana 같은 복잡한 앱을 명령어 몇 줄로 설치할 수 있고, values.yaml을 통해 환경별 설정도 깔끔하게 분리할 수 있다. 다만 Helm도 결국 Kubernetes 리소스를 생성하는 도구이기 때문에, 문제가 생겼을 때는 kubectl로 Pod 상태, 로그, 이벤트를 확인할 수 있어야 한다.
