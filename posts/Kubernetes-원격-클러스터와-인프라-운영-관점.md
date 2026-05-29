---
title: "[Kubernetes] 원격 클러스터와 인프라 운영 관점"
source: "https://velog.io/@yorange50/Kubernetes-원격-클러스터와-인프라-운영-관점"
published: "2026-05-14T08:07:47.318Z"
tags: ""
backup_date: "2026-05-29T14:52:52.739503"
---

Kubernetes를 처음 배울 때는 보통 서버에 직접 SSH로 들어가서 명령어를 치는 방식이 익숙하다.

```bash
ssh ubuntu@server-ip
kubectl get pods
```

그런데 실무 관점으로 가면 조금 다른 생각을 해야 한다.

```text
매번 서버에 들어가서 명령어를 치는 게 맞을까?
내 로컬에서 여러 클러스터를 바꿔가며 관리할 수는 없을까?
VM1, VM2, VM3에 각각 들어가지 않고 중앙에서 제어할 수는 없을까?
```

이 질문이 바로 Kubernetes 운영, kubeconfig, context, IaC, 자동화 사고로 이어진다. 실습 메모에서도 “서버 들어가서 하지 말고 어떻게든 로컬로 빼오려는 마인드”, “로컬에서 kubectl 치면 컨텍스트 바꿔가면서 하자는 것”, “이 개념을 잡으면 인프라에서 코드가 될 수 있는 아키텍처가 된다”는 흐름이 강조된다. 

---

# [KUBERNETES] 로컬 kubectl로 원격 VM 클러스터를 관리하는 원리

## 1. kubectl은 어디에 명령을 보내는가?

`kubectl`은 단순히 내 컴퓨터 안에서만 동작하는 명령어가 아니다.

`kubectl`은 Kubernetes API Server에 요청을 보내는 클라이언트다.

```text
kubectl
= Kubernetes API Server와 통신하는 CLI 도구
```

예를 들어 다음 명령어를 친다고 하자.

```bash
kubectl get pods
```

이 명령어는 사실 이런 의미다.

```text
현재 kubeconfig에 설정된 Kubernetes API Server에게
Pod 목록을 요청한다.
```

즉, `kubectl`은 “내 컴퓨터에 있는 클러스터”만 보는 게 아니다.
어떤 클러스터를 볼지는 **kubeconfig**가 결정한다.

---

## 2. kubeconfig란?

`kubeconfig`는 `kubectl`이 어떤 Kubernetes 클러스터에 접속할지 알려주는 설정 파일이다.

보통 위치는 여기다.

```bash
~/.kube/config
```

Mac이나 Linux에서 `.kube` 폴더는 숨김 폴더라서 기본 Finder나 파일 탐색기에서는 안 보일 수 있다.

이 파일 안에는 대략 이런 정보가 들어 있다.

```text
clusters
= 접속 가능한 Kubernetes 클러스터 정보

users
= 인증 정보

contexts
= 어떤 user로 어떤 cluster에 접속할지 묶은 정보

current-context
= 지금 kubectl이 바라보는 기본 context
```

즉, kubeconfig는 Kubernetes 접속 주소록 같은 것이다.

---

## 3. kubeconfig에 remote 정보 저장

예를 들어 내 로컬 노트북에서 원격 VM에 설치된 K3s 클러스터를 관리하고 싶다고 하자.

구조는 이렇다.

```text
내 노트북
 └── kubectl

원격 VM
 └── K3s Cluster
      └── Kubernetes API Server
```

이때 내 노트북의 `~/.kube/config`에 원격 VM의 Kubernetes API Server 주소와 인증 정보를 넣으면, 로컬에서 바로 원격 클러스터를 관리할 수 있다.

```text
로컬 kubectl
      ↓
원격 VM의 Kubernetes API Server
      ↓
원격 클러스터의 Pod / Service / Deployment 관리
```

이렇게 되면 매번 원격 서버에 SSH로 들어가서 `kubectl`을 칠 필요가 줄어든다.

---

## 4. SSH 없이 관리한다는 뜻

여기서 “SSH 없이 관리한다”는 말은 서버에 아예 접속하지 않는다는 뜻이라기보다, **운영 명령을 위해 매번 서버 쉘에 들어가지 않아도 된다**는 뜻에 가깝다.

기존 방식은 이렇다.

```bash
ssh ubuntu@vm1
kubectl get pods
kubectl apply -f deployment.yaml
```

로컬 기반 운영 방식은 이렇다.

```bash
kubectl --context vm1 get pods
kubectl --context vm1 apply -f deployment.yaml
```

즉, 명령어를 실행하는 위치가 바뀐다.

```text
기존 방식
= 서버 안에 들어가서 명령 실행

로컬 기반 방식
= 내 로컬에서 원격 클러스터 API Server로 명령 전송
```

이 차이가 작아 보이지만 운영 관점에서는 꽤 크다.

---

## 5. VM1 / VM2 운영은 어떻게 하나?

VM이 여러 대 있다고 생각해보자.

```text
VM1
= dev 클러스터

VM2
= staging 클러스터

VM3
= prod 클러스터
```

각 VM마다 Kubernetes 클러스터가 있거나, 여러 VM이 하나의 클러스터를 구성할 수도 있다.

로컬 kubeconfig에는 여러 클러스터 정보를 넣을 수 있다.

```text
contexts:
  dev
  staging
  prod
```

그러면 로컬에서 context만 바꿔가며 관리할 수 있다.

```bash
kubectl config use-context dev
kubectl get pods

kubectl config use-context staging
kubectl get pods

kubectl config use-context prod
kubectl get pods
```

또는 명령어마다 context를 직접 지정할 수도 있다.

```bash
kubectl --context dev get pods
kubectl --context staging get pods
kubectl --context prod get pods
```

이렇게 하면 여러 클러스터를 하나의 로컬 터미널에서 제어할 수 있다.

---

## 6. current-context란?

`current-context`는 현재 `kubectl`이 기본으로 바라보는 클러스터다.

예를 들어 현재 context가 `dev`라면,

```bash
kubectl get pods
```

이 명령어는 dev 클러스터에 요청을 보낸다.

현재 context 확인은 이렇게 한다.

```bash
kubectl config current-context
```

context 목록은 이렇게 본다.

```bash
kubectl config get-contexts
```

context 변경은 이렇게 한다.

```bash
kubectl config use-context <context-name>
```

정리하면 다음과 같다.

```text
kubectl config get-contexts
= 등록된 context 목록 확인

kubectl config current-context
= 현재 바라보는 context 확인

kubectl config use-context dev
= dev context로 전환
```

---

## 7. kubectx는 왜 쓰는가?

context가 많아지면 `kubectl config use-context ...`를 매번 치기 귀찮다.

이때 많이 쓰는 도구가 `kubectx`다.

```bash
kubectx
```

등록된 context 목록을 쉽게 볼 수 있고,

```bash
kubectx dev
```

이렇게 빠르게 context를 바꿀 수 있다.

namespace 전환은 `kubens`라는 도구를 많이 쓴다.

```bash
kubens ingress-nginx
kubens default
kubens kube-system
```

즉, 운영자가 여러 클러스터와 namespace를 왔다 갔다 해야 할 때 `kubectx`, `kubens` 같은 도구가 편하다.

---

# [INFRA] 서버에 직접 들어가지 않으려는 이유

## 1. 서버에 직접 들어가는 방식의 한계

처음에는 서버에 직접 SSH로 들어가는 게 편하다.

```bash
ssh ubuntu@server
docker ps
kubectl get pods
vi deployment.yaml
```

그런데 서버가 1대가 아니라 여러 대가 되면 문제가 생긴다.

```text
VM1에 들어가서 작업
VM2에 들어가서 작업
VM3에 들어가서 작업
prod 서버에 들어가서 작업
staging 서버에 들어가서 작업
```

이러면 작업이 사람 손에 많이 의존하게 된다.

문제는 사람 손에 의존하는 작업은 실수하기 쉽다는 것이다.

```text
어느 서버에 들어와 있는지 착각
dev인 줄 알고 prod에서 명령 실행
수정한 파일이 서버 안에만 남음
누가 언제 뭘 바꿨는지 추적 어려움
반복 작업 자동화 어려움
```

그래서 운영에서는 점점 “서버에 들어가서 고치는 방식”을 줄이려고 한다.

---

## 2. 중앙 관리 관점

로컬에서 여러 클러스터를 관리한다는 것은 중앙 관리의 시작이다.

```text
내 로컬 또는 CI/CD 서버
      ↓
dev 클러스터
staging 클러스터
prod 클러스터
```

운영자는 각 서버에 직접 접속하는 대신, 중앙에서 명령을 내린다.

```bash
kubectl --context dev get pods
kubectl --context staging get pods
kubectl --context prod get pods
```

이 방식은 관리 포인트를 줄여준다.

```text
서버마다 들어가지 않아도 됨
명령 실행 위치를 통제할 수 있음
스크립트화하기 쉬움
CI/CD와 연결하기 쉬움
작업 이력을 남기기 쉬움
```

즉, 서버 안에서 일하는 방식에서 서버 밖에서 제어하는 방식으로 사고가 바뀐다.

---

## 3. 로컬 기반 운영

로컬 기반 운영이란, 내 노트북 또는 운영용 관리 머신에서 원격 인프라를 제어하는 방식이다.

예를 들어 다음과 같은 파일들이 로컬에 있다.

```text
kubernetes/
 ├── dev/
 │    ├── deployment.yaml
 │    └── service.yaml
 ├── staging/
 │    ├── deployment.yaml
 │    └── service.yaml
 └── prod/
      ├── deployment.yaml
      └── service.yaml
```

그리고 로컬에서 적용한다.

```bash
kubectl --context dev apply -f kubernetes/dev/
kubectl --context staging apply -f kubernetes/staging/
kubectl --context prod apply -f kubernetes/prod/
```

이렇게 하면 서버에 들어가서 파일을 수정하지 않아도 된다.

파일은 로컬 또는 Git에 있고, 적용만 원격 클러스터에 하는 것이다.

---

## 4. 왜 서버 안에서 vi로 고치면 안 좋을까?

서버 안에서 직접 파일을 고치는 방식은 당장은 빠르다.

```bash
vi deployment.yaml
kubectl apply -f deployment.yaml
```

하지만 운영에서는 위험하다.

왜냐하면 변경사항이 서버 안에만 남을 수 있기 때문이다.

```text
Git에 기록 안 됨
누가 바꿨는지 모름
원래 설정과 달라짐
서버가 날아가면 수정사항도 사라짐
다른 환경에 똑같이 재현하기 어려움
```

Docker에서도 비슷한 문제가 있었다. 컨테이너 안에 들어가서 설정 파일을 고치면 재생성 시 사라진다. 그래서 설정을 호스트 파일, 볼륨, 이미지, 코드로 관리하려는 방향으로 간다.

Kubernetes와 인프라도 마찬가지다.

```text
서버 안에서 직접 고치지 말고
설정 파일을 밖으로 빼고
Git으로 관리하고
자동화된 방식으로 적용하자
```

이게 운영 철학에 가깝다.

---

## 5. 자동화 철학

자동화의 핵심은 반복 작업을 사람 손에서 빼는 것이다.

나쁜 방식은 이렇다.

```text
1. 서버 접속
2. 파일 열기
3. 설정 수정
4. 명령어 실행
5. 결과 확인
6. 다른 서버에서도 반복
```

좋은 방식은 점점 이렇게 간다.

```text
1. Git에 설정 변경
2. CI/CD 파이프라인 실행
3. kubectl 또는 Helm으로 배포
4. 모니터링으로 확인
```

또는 IaC 도구를 사용한다.

```text
Terraform
= 인프라 리소스 생성 자동화

Ansible
= 서버 설정 자동화

Helm
= Kubernetes 리소스 패키지 배포

Argo CD
= GitOps 기반 Kubernetes 배포
```

즉, 서버에 직접 들어가지 않으려는 이유는 단순히 귀찮아서가 아니다.

```text
실수를 줄이고
재현성을 높이고
변경 이력을 남기고
자동화하기 위해서
```

---

# [INFRA] “인프라를 코드로 관리한다”는 감각

## 1. IaC란?

IaC는 Infrastructure as Code의 줄임말이다.

한국어로는 **인프라를 코드로 관리한다**는 뜻이다.

예전에는 서버를 만들고 설정할 때 사람이 콘솔에서 직접 클릭하거나, 서버에 들어가서 명령어를 쳤다.

```text
AWS 콘솔에서 EC2 생성
서버 SSH 접속
패키지 설치
설정 파일 수정
방화벽 설정
서비스 실행
```

IaC 관점에서는 이런 작업을 코드로 표현한다.

```hcl
resource "aws_instance" "web" {
  ami           = "ami-xxxx"
  instance_type = "t3.micro"
}
```

또는 Kubernetes 리소스를 YAML로 선언한다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 3
```

중요한 것은 “명령어를 한 번 쳤다”가 아니라, **원하는 인프라 상태를 코드로 남긴다**는 것이다.

---

## 2. Kubernetes YAML도 IaC 감각에 가깝다

Kubernetes YAML은 선언형이다.

```yaml
replicas: 3
```

이 말은 다음과 같다.

```text
Pod를 지금 3개 만들어라
```

라기보다는,

```text
이 애플리케이션은 항상 Pod 3개 상태를 유지해야 한다
```

에 가깝다.

Kubernetes는 이 선언을 보고 desired state를 유지한다.

그래서 Kubernetes YAML도 넓게 보면 IaC 감각과 연결된다.

```text
YAML로 원하는 상태 선언
Git으로 버전 관리
kubectl 또는 GitOps 도구로 적용
클러스터가 상태를 맞춤
```

---

## 3. context 전환이 중요한 이유

여러 클러스터를 운영하면 context 전환이 중요해진다.

```text
dev context
staging context
prod context
```

이때 context는 단순한 접속 설정이 아니다.

운영자 입장에서는 “내가 지금 어떤 인프라를 바라보고 있는가”를 의미한다.

```bash
kubectl config current-context
```

이 명령어를 확인하지 않고 작업하면 위험하다.

예를 들어 dev에 배포해야 하는데 현재 context가 prod라면 큰 사고가 날 수 있다.

```bash
kubectl delete deployment app
```

이 명령어 하나가 dev가 아니라 prod에 실행될 수 있다.

그래서 운영에서는 context 확인 습관이 중요하다.

```bash
kubectl config current-context
kubectl get ns
kubectl get pods -A
```

작업 전에는 항상 내가 어디를 보고 있는지 확인해야 한다.

---

## 4. kubectl automation

`kubectl` 명령어는 사람이 직접 칠 수도 있지만, 스크립트나 CI/CD 파이프라인에서 실행할 수도 있다.

예를 들어 간단한 배포 스크립트를 만들 수 있다.

```bash
#!/bin/bash

set -e

CONTEXT=dev
NAMESPACE=default

kubectl --context $CONTEXT -n $NAMESPACE apply -f deployment.yaml
kubectl --context $CONTEXT -n $NAMESPACE rollout status deployment/my-app
```

이렇게 하면 매번 사람이 명령어를 기억해서 치지 않아도 된다.

CI/CD에서도 비슷하게 쓸 수 있다.

```text
GitHub Actions
Jenkins
GitLab CI
Argo CD
```

예를 들어 Jenkins에서 테스트가 통과하면 Kubernetes에 배포할 수 있다.

```text
1. Git push
2. CI 테스트 실행
3. Docker image build
4. image push
5. kubectl set image 또는 helm upgrade
6. rollout 상태 확인
```

이런 흐름이 되면 운영이 훨씬 안정적이다.

---

## 5. IaC와 kubectl의 연결

`kubectl`은 IaC 그 자체라기보다는, 선언된 인프라 상태를 클러스터에 적용하는 도구에 가깝다.

예를 들어 Git에 YAML이 있다.

```text
git repository
 └── k8s/
      ├── deployment.yaml
      ├── service.yaml
      └── ingress.yaml
```

그리고 CI/CD에서 적용한다.

```bash
kubectl apply -f k8s/
```

그러면 Git에 있는 코드가 클러스터 상태로 반영된다.

이 구조가 점점 발전하면 GitOps가 된다.

```text
Git
= 원하는 상태의 원본

Kubernetes Cluster
= 실제 상태

Controller
= Git과 Cluster 상태를 비교하고 맞춤
```

Argo CD 같은 도구는 Git에 있는 YAML과 클러스터 상태를 계속 비교하면서 맞춘다.

즉, Kubernetes의 desired state 개념과 IaC/GitOps는 자연스럽게 연결된다.

---

## 6. agent화 관점

실습 메모에서 말한 “agent화” 관점은 이렇게 이해하면 좋다.

처음에는 사람이 직접 서버에 들어간다.

```text
사람
 ↓ SSH
서버
 ↓ 명령어 실행
Kubernetes 조작
```

그다음에는 로컬에서 원격 클러스터를 제어한다.

```text
사람
 ↓ kubectl
원격 Kubernetes API Server
```

그다음에는 스크립트나 CI/CD가 대신 실행한다.

```text
Git push
 ↓
CI/CD
 ↓
kubectl apply / helm upgrade
 ↓
Kubernetes Cluster
```

더 나아가면 클러스터 안의 Controller가 계속 상태를 맞춘다.

```text
Git Repository
 ↓
Argo CD / Flux
 ↓
Kubernetes Cluster
```

이렇게 사람이 직접 서버에 들어가는 비중이 줄고, 도구와 자동화가 상태를 관리하게 된다.

이게 인프라 운영의 방향이다.

```text
수동 접속
→ 로컬 제어
→ 스크립트 자동화
→ CI/CD 자동화
→ GitOps / Controller 기반 운영
```

---

# 전체 흐름으로 정리

## 1. 로컬 kubectl 운영

```text
kubectl은 kubeconfig를 보고
어떤 Kubernetes API Server에 접속할지 결정한다.

kubeconfig에 원격 클러스터 정보가 있으면
내 로컬에서도 원격 VM 클러스터를 관리할 수 있다.
```

## 2. context 전환

```text
context는 cluster + user + namespace 조합이다.

dev, staging, prod context를 등록해두면
로컬에서 클러스터를 바꿔가며 관리할 수 있다.
```

## 3. 서버에 직접 들어가지 않는 이유

```text
서버에 직접 들어가서 수정하면
변경 이력이 흐려지고
재현성이 떨어지고
자동화가 어려워진다.

그래서 설정을 밖으로 빼고
Git에 저장하고
로컬이나 CI/CD에서 적용하는 방향으로 간다.
```

## 4. IaC 감각

```text
인프라를 코드로 관리한다는 것은
서버 상태를 사람 손으로 기억하는 게 아니라
코드와 설정 파일로 선언하고
그 상태를 자동으로 재현 가능하게 만드는 것이다.
```

## 5. agent화 관점

```text
처음에는 사람이 서버에 접속한다.
그다음에는 로컬 kubectl이 원격 클러스터를 제어한다.
그다음에는 CI/CD가 kubectl을 실행한다.
마지막에는 GitOps Controller가 상태를 계속 맞춘다.
```

---

# 실습 명령어 정리

현재 context 확인:

```bash
kubectl config current-context
```

context 목록 확인:

```bash
kubectl config get-contexts
```

context 변경:

```bash
kubectl config use-context dev
```

명령어마다 context 지정:

```bash
kubectl --context dev get pods
```

특정 namespace 조회:

```bash
kubectl --context dev -n kube-system get pods
```

전체 namespace 조회:

```bash
kubectl --context dev get pods -A
```

kubeconfig 파일 위치:

```bash
~/.kube/config
```

kubectx로 context 전환:

```bash
kubectx dev
```

kubens로 namespace 전환:

```bash
kubens kube-system
```

---

# 정리

로컬 `kubectl`로 원격 VM 클러스터를 관리할 수 있는 이유는 `kubectl`이 직접 클러스터 안에서 실행되는 도구가 아니라, kubeconfig를 보고 Kubernetes API Server에 요청을 보내는 클라이언트이기 때문이다. `~/.kube/config`에 원격 클러스터 주소와 인증 정보가 들어 있으면 내 노트북에서도 원격 Kubernetes 클러스터를 관리할 수 있다.

서버에 직접 들어가지 않으려는 이유는 운영을 사람 손에 덜 의존하게 만들기 위해서다. 서버 안에서 직접 수정하면 변경 이력이 흐려지고, 재현성이 떨어지고, 자동화가 어려워진다. 반대로 로컬이나 CI/CD에서 선언된 파일을 기준으로 적용하면 중앙 관리, 버전 관리, 자동화가 쉬워진다.

“인프라를 코드로 관리한다”는 감각은 결국 원하는 인프라 상태를 코드로 선언하고, 그 코드를 기준으로 실제 인프라를 맞춰가는 것이다. Kubernetes의 YAML, kubeconfig context 전환, `kubectl apply`, Helm, Terraform, Argo CD 같은 도구들이 모두 이 흐름과 연결된다.

핵심은 이거다.

```text
서버에 들어가서 고치는 사람 중심 운영에서
코드와 자동화가 상태를 맞추는 시스템 중심 운영으로 넘어가는 것
```

그래서 Kubernetes 운영을 배울 때는 단순히 `kubectl get pods`만 외우는 게 아니라, 내가 지금 어떤 context를 보고 있는지, 이 설정이 어디에 저장되는지, 이 작업을 나중에 어떻게 자동화할 수 있는지를 같이 생각해야 한다.
