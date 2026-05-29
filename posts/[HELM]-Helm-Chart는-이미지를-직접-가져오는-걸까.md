---
title: "[HELM] Helm Chart는 이미지를 직접 가져오는 걸까?"
source: "https://velog.io/@yorange50/HELM-Helm-Chart는-이미지를-직접-가져오는-걸까"
published: "2026-05-17T12:01:03.260Z"
tags: ""
backup_date: "2026-05-29T14:52:52.730856"
---

Helm을 처음 배우다 보면 이런 생각이 든다.

```bash id="j8hz0p"
helm install ingress-nginx ingress-nginx/ingress-nginx
```

“이 명령어를 치면 Helm이 Docker 이미지를 가져오는 건가?”

특히 `helm install`을 실행하면 Pod가 자동으로 뜨고, Docker Hub에서 이미지도 자동으로 받아오는 것처럼 보인다.

그래서:

```text id="5c3yff"
Helm = 이미지 다운로드 도구
```

처럼 느껴질 수 있다.

하지만 실제로는 조금 다르다.

---

# 결론부터 말하면

Helm은 이미지를 직접 다운로드하지 않는다.

Helm의 역할은:

```text id="u3n6x4"
Kubernetes YAML 생성
Kubernetes 리소스 설치
설정값(values) 주입
```

이다.

실제 이미지 다운로드는 Kubernetes의 컨테이너 런타임이 수행한다.

즉 역할이 나뉜다.

```text id="k0uybi"
Helm
= YAML 생성 및 배포

Kubernetes
= 리소스 생성 및 관리

containerd/docker
= 실제 이미지 pull
```

---

# 전체 흐름 먼저 보기

예를 들어 이런 명령어를 실행했다고 하자.

```bash id="m4uq4h"
helm install my-nginx bitnami/nginx
```

그러면 내부적으로는 이런 일이 일어난다.

```text id="5z4h6g"
1. Helm이 Chart를 읽음
2. values.yaml 값을 읽음
3. Deployment YAML 생성
4. image: nginx 같은 값 포함
5. Kubernetes API Server에 적용
6. Scheduler가 Pod 배치
7. kubelet이 필요한 이미지 확인
8. containerd/docker가 Registry에서 이미지 pull
9. 컨테이너 실행
```

즉 Helm은 Kubernetes YAML을 만들어서 적용하는 역할이고:

```text id="j0dn2o"
실제 이미지 다운로드
```

는 Kubernetes 노드의 컨테이너 런타임이 한다.

---

# Helm Chart 안에는 뭐가 들어있을까?

Helm Chart 안에는 보통 이런 파일들이 있다.

```text id="x6o6rw"
Chart.yaml
values.yaml
templates/
```

그중 실제 이미지 정보는 보통:

```text id="t7u2l4"
values.yaml
templates/deployment.yaml
```

안에 들어있다.

예를 들어 values.yaml:

```yaml id="4gy4l1"
image:
  repository: nginx
  tag: "1.27"
```

그리고 templates/deployment.yaml:

```yaml id="q8xqeu"
containers:
  - name: nginx
    image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
```

Helm은 이 템플릿을 렌더링해서 최종 Kubernetes YAML을 만든다.

```yaml id="mjf9pn"
containers:
  - name: nginx
    image: nginx:1.27
```

즉 Helm은:

```text id="13t3c0"
“이 Pod는 nginx:1.27 이미지를 써”
```

라고 Kubernetes에 전달하는 역할이다.

---

# 실제 이미지는 누가 가져오나?

이 부분이 중요하다.

실제 이미지는 Kubernetes 노드 안의 컨테이너 런타임이 가져온다.

예를 들어:

```text id="6vjlwm"
containerd
Docker
CRI-O
```

같은 런타임이 Registry에 접속한다.

```text id="wjlwm7"
Docker Hub
ECR
GCR
Harbor
Quay
```

그리고 이미지를 다운로드한다.

흐름은 이렇게 된다.

```text id="rjlwm8"
Helm
  ↓
Deployment 생성
  ↓
Kubernetes가 Pod 생성 시도
  ↓
container runtime가 image pull
  ↓
컨테이너 실행
```

즉 Helm은:

```text id="2jlwm9"
이미지를 “직접 다운로드”하는 게 아니라,
Deployment에 image 정보를 적어주는 역할
```

이다.

---

# 왜 Helm이 이미지를 가져오는 것처럼 보일까?

이유는 Helm install을 하면 Pod가 바로 뜨기 때문이다.

예를 들어:

```bash id="l3wlma"
helm install my-app ./chart
```

를 실행하면 곧바로:

```bash id="g1wlmb"
kubectl get pods
```

했을 때 Pod가 생성된다.

그러면 자연스럽게:

```text id="x1wlmc"
“Helm이 이미지를 받아왔구나”
```

처럼 느껴진다.

하지만 실제로는:

```text id="z0wlmd"
Helm → Deployment 생성
Kubernetes → Pod 생성
containerd/docker → 이미지 pull
```

순서다.

즉 Helm은 시작 버튼 역할에 가깝다.

---

# 인터넷이 안 되면 어떻게 될까?

여기서 중요한 운영 포인트가 나온다.

이미지는 Registry에서 받아와야 하기 때문에:

```text id="k9wlme"
Docker Hub
ECR
GCR
Harbor
```

에 접근이 안 되면 Pod가 뜨지 않는다.

예를 들어 인터넷이 안 되거나:

```text id="w2wlmf"
이미지 이름 틀림
레지스트리 인증 실패
네트워크 차단
```

같은 문제가 있으면 Pod 상태가 이렇게 된다.

```text id="q8wlmg"
ImagePullBackOff
ErrImagePull
```

즉:

```text id="h5wlmh"
Helm 설치 성공
≠ Pod 실행 성공
```

이다.

Helm은 Kubernetes 리소스를 잘 만들었더라도, 이미지 pull 실패는 별개 문제다.

---

# ImagePullBackOff는 왜 뜨는 걸까?

대표적인 원인은 이런 것들이다.

## 1. 이미지 이름 틀림

예:

```yaml id="c3wlmi"
image: ngnix:latest
```

오타 때문에 Registry에서 이미지를 못 찾는다.

---

## 2. private registry 인증 실패

예를 들어 ECR이나 Harbor private registry는 인증이 필요할 수 있다.

```text id="o4wlmj"
imagePullSecret 필요
```

이 설정이 없으면 pull 실패가 난다.

---

## 3. 인터넷 연결 문제

노드가 Registry에 접근하지 못하면 이미지 다운로드가 안 된다.

특히 사설망 환경에서 자주 발생한다.

---

## 4. Registry Rate Limit

Docker Hub는 pull 제한이 걸릴 수 있다.

트래픽이 많으면:

```text id="e7wlmk"
Too Many Requests
```

에러가 뜰 수도 있다.

---

# ingress-nginx Helm Chart도 이미지 여러 개를 쓴다

Ingress NGINX Helm Chart를 예로 들어보자.

```bash id="u0wlml"
helm install ingress-nginx ingress-nginx/ingress-nginx
```

이 명령어 하나만 보면 이미지 하나만 쓸 것 같지만 실제로는 여러 이미지가 사용될 수 있다.

예:

```text id="s1wlmm"
controller 이미지
admission webhook 이미지
default backend 이미지
```

등.

그래서 설치 후:

```bash id="j2wlmn"
kubectl get pods -n ingress-nginx
```

를 보면 여러 Pod가 뜬다.

그리고 각각 필요한 이미지를 pull한다.

즉 Helm Chart는 단순히 Pod 하나만 띄우는 파일이 아니다.

복잡한 Kubernetes 리소스 묶음이다.

---

# values.yaml로 이미지 바꾸기

Helm의 강력한 장점 중 하나가 이미지 설정 변경이다.

예를 들어 values.yaml:

```yaml id="m3wlmo"
image:
  repository: my-app
  tag: v2
```

이렇게 수정하고:

```bash id="v4wlmp"
helm upgrade my-app ./chart
```

를 실행하면 Kubernetes가 새 이미지로 Rolling Update를 수행한다.

즉 Helm은:

```text id="x5wlmq"
이미지 버전 관리
환경별 이미지 설정
registry 변경
```

등을 쉽게 할 수 있게 해준다.

---

# Helm template로 보면 더 이해 쉬움

이 명령어를 쓰면:

```bash id="f6wlmr"
helm template my-app ./chart
```

Helm이 실제로 어떤 YAML을 생성하는지 볼 수 있다.

예를 들어 최종 결과에:

```yaml id="d7wlms"
image: nginx:1.27
```

가 들어있는 걸 확인할 수 있다.

즉 Helm은 결국:

```text id="b8wlmt"
Kubernetes YAML 생성기
```

에 가깝다.

이미지 파일 자체를 다운로드하는 건 아니다.

---

# Docker Compose와 비교하면?

Docker Compose에서는 이런 걸 많이 본다.

```yaml id="a9wlmu"
services:
  app:
    image: nginx
```

Compose도 비슷하게 동작한다.

```text id="v0wlmv"
docker compose up
→ Docker Engine이 image pull
```

즉 Compose도 YAML에 image 정보만 적고, 실제 pull은 Docker가 한다.

Helm도 비슷하다.

```text id="u1wlmw"
Helm
→ YAML 생성

Kubernetes/containerd
→ 실제 image pull
```

---

# 면접에서 설명한다면

면접에서:

```text id="m2wlmx"
“Helm Chart는 이미지를 직접 가져오나요?”
```

라고 물어보면 이렇게 답할 수 있다.

```text id="n3wlmy"
Helm 자체가 이미지를 직접 다운로드하는 것은 아닙니다.

Helm은 values.yaml과 templates를 조합해서 Deployment 같은 Kubernetes 리소스를 생성하고, 그 안에 image 정보를 포함시킵니다.

이후 Kubernetes가 Pod를 생성할 때 kubelet과 container runtime(containerd/docker)이 실제 Registry에서 이미지를 pull합니다.

즉 Helm은 Kubernetes manifest를 생성하고 배포하는 역할이고, 실제 image pull은 Kubernetes 노드에서 수행됩니다.
```

프로젝트 경험과 연결하면 이렇게도 말할 수 있다.

```text id="p4wlmz"
Ingress NGINX Controller를 Helm Chart로 설치하면서, Helm이 여러 Kubernetes 리소스를 자동 생성하는 과정을 경험했습니다.

실제 컨테이너 이미지는 Helm이 직접 다운로드하는 것이 아니라, 생성된 Deployment를 기반으로 Kubernetes의 container runtime가 Docker Hub에서 pull해서 실행했습니다.
```

---

# 핵심 정리

```text id="q5wlna"
Helm
= Kubernetes YAML 생성 및 배포 도구

Helm Chart
= 리소스 템플릿 패키지

image 정보
= values.yaml / templates 안에 포함

실제 image pull
= Kubernetes의 container runtime(containerd/docker)가 수행
```

흐름은 이렇다.

```text id="r6wlnb"
Helm install
  ↓
Deployment 생성
  ↓
Pod 생성
  ↓
container runtime가 Registry에서 image pull
  ↓
컨테이너 실행
```

한 줄로 정리하면:

```text id="s7wlnc"
Helm은 이미지를 직접 다운로드하는 게 아니라,
Kubernetes가 어떤 이미지를 사용할지 정의한 YAML을 생성하고 배포하는 역할을 한다.
```