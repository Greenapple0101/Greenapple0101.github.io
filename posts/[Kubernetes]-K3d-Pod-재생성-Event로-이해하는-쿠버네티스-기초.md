---
title: "[KUBERNETES] K3d, Pod 재생성, Event로 이해하는 쿠버네티스 기초"
source: "https://velog.io/@yorange50/KUBERNETES-K3d-Pod-재생성-Event로-이해하는-쿠버네티스-기초"
published: "2026-05-14T07:47:03.614Z"
tags: ""
backup_date: "2026-05-29T14:52:52.740460"
---

쿠버네티스를 처음 만지면 가장 먼저 드는 생각은 이것이다.

“분명 내가 뭔가를 지웠는데 왜 다시 생기지?”
“Pod가 죽었는데 왜 또 만들어지지?”
“에러가 났는데 어디부터 봐야 하지?”
“K3d는 또 뭐고, K3s랑은 뭐가 다른 거지?”

이번 글에서는 Kubernetes를 로컬에서 쉽게 실습할 수 있게 해주는 **K3d**, 그리고 Kubernetes가 컨테이너를 계속 다시 만드는 이유, 마지막으로 장애 분석에서 가장 먼저 봐야 하는 **Event** 개념을 정리해보려고 한다.

---

## 1. K3d는 무엇인가?

K3d는 한마디로 말하면 **Docker 위에서 K3s 기반 Kubernetes 클러스터를 빠르게 만들어주는 도구**다.

여기서 이름을 나눠서 보면 이해가 쉽다.

```text
K3s = 경량 Kubernetes
K3d = Docker 안에서 K3s 클러스터를 띄우는 도구
```

Kubernetes를 제대로 설치하려면 원래는 여러 노드, 네트워크 설정, kubeconfig, 컨테이너 런타임 등을 신경 써야 한다. 그런데 처음 공부하는 입장에서 이 모든 것을 직접 설치하면 Kubernetes를 배우기도 전에 설치에서 지칠 수 있다.

그래서 로컬 개발 환경에서는 K3d를 많이 쓴다.

K3d를 사용하면 내 노트북의 Docker 위에 Kubernetes 클러스터를 빠르게 만들 수 있다. 실제로 실습 중에도 “쿠버네티스를 30초 내에 생성한다는 건 매우 빠른 것”이라는 흐름으로 이해하면 좋다. 

---

## 2. K3d는 왜 로컬 개발 환경에 좋을까?

K3d의 장점은 명확하다.

```text
빠르게 클러스터 생성 가능
Docker 기반이라 로컬에서 실습 가능
K3s 기반이라 가벼움
클러스터를 만들고 지우기 쉬움
Kubernetes 기본 개념 실습에 적합
```

예를 들어 다음과 같은 작업을 로컬에서 실습할 수 있다.

```text
Pod 생성
Deployment 생성
Service 생성
Ingress 테스트
kubectl 명령어 실습
k9s로 리소스 확인
Event 확인
클러스터 삭제 후 재생성
```

즉, K3d는 운영용 대형 Kubernetes 클러스터를 처음부터 구축하기 위한 도구라기보다는, **Kubernetes의 동작 원리를 빠르게 몸으로 익히는 실습 환경**에 가깝다.

---

## 3. K3d는 Docker 기반 Kubernetes다

K3d로 클러스터를 만들면 실제로는 Docker 컨테이너들이 생성된다.

예를 들어 Kubernetes 클러스터를 만든다고 해서 내 노트북에 진짜 물리 서버가 생기는 것은 아니다. Docker 컨테이너 안에 K3s 서버 노드, 에이전트 노드, 로드밸런서 역할을 하는 컨테이너 등이 뜨는 구조다.

단순화하면 이런 느낌이다.

```text
내 노트북
 └── Docker
      ├── k3d-server 컨테이너
      ├── k3d-agent 컨테이너
      └── k3d-loadbalancer 컨테이너
```

즉, K3d는 Docker를 이용해서 Kubernetes 클러스터처럼 동작하는 환경을 만들어준다.

그래서 Docker가 먼저 설치되어 있어야 하고, K3d 클러스터를 만들면 `docker ps`에서도 관련 컨테이너를 확인할 수 있다.

---

## 4. K3s 기반 경량 Kubernetes란?

K3s는 Rancher에서 만든 **가벼운 Kubernetes 배포판**이다.

일반 Kubernetes보다 설치와 실행이 가볍고, 로컬 개발이나 엣지 환경, 테스트 환경에서 많이 사용된다.

일반 Kubernetes는 학습용으로 쓰기에는 무겁게 느껴질 수 있다. 반면 K3s는 Kubernetes의 핵심 기능은 유지하면서도 구성 요소를 단순화했다.

그래서 K3d는 이 K3s를 Docker 안에서 실행함으로써, 복잡한 설치 없이 Kubernetes 실습 환경을 만들어준다.

정리하면 다음과 같다.

```text
Kubernetes
= 컨테이너 오케스트레이션 플랫폼

K3s
= 가볍게 만든 Kubernetes 배포판

K3d
= Docker 안에서 K3s 클러스터를 띄우는 도구
```

---

# [KUBERNETES] Kubernetes는 왜 컨테이너를 계속 다시 만들까?

Kubernetes를 처음 보면 이상한 장면을 자주 보게 된다.

Pod를 지웠는데 다시 생긴다.

```bash
kubectl delete pod nginx-xxxxx
```

그런데 잠시 후 다시 확인하면 새로운 Pod가 생겨 있다.

```bash
kubectl get pods
```

처음에는 이게 버그처럼 보인다.

하지만 사실 이게 Kubernetes의 핵심이다.

Kubernetes는 사용자가 원하는 상태를 계속 유지하려고 한다.

이 개념을 **desired state**라고 한다.

---

## 1. Desired State란?

Desired State는 말 그대로 **원하는 상태**다.

예를 들어 내가 Deployment를 만들면서 이렇게 선언했다고 하자.

```yaml
replicas: 3
```

이 말은 Kubernetes에게 이렇게 말한 것과 같다.

```text
나는 이 애플리케이션 Pod가 항상 3개 떠 있기를 원해.
```

그러면 Kubernetes는 현재 상태를 계속 확인한다.

```text
원하는 상태: Pod 3개
현재 상태: Pod 2개
```

현재 상태가 원하는 상태와 다르면 Kubernetes는 다시 맞춘다.

```text
Pod 1개 새로 생성
```

그래서 사용자가 Pod 하나를 직접 삭제해도 Deployment가 관리하는 Pod라면 다시 만들어진다.

---

## 2. Kubernetes는 선언형 시스템이다

Kubernetes에서는 보통 “이걸 실행해줘”보다 “이런 상태가 되게 해줘”에 가깝게 명령한다.

예를 들어 Docker에서는 보통 이렇게 생각한다.

```text
컨테이너 하나 실행해줘
```

하지만 Kubernetes에서는 이렇게 생각한다.

```text
nginx Pod가 항상 3개 유지되게 해줘
```

그래서 Kubernetes는 한 번 실행하고 끝나는 시스템이 아니다.

계속 감시한다.
계속 비교한다.
계속 맞춘다.

이 흐름이 바로 Kubernetes의 핵심 동작 방식이다.

---

## 3. Self-Healing이란?

Self-Healing은 말 그대로 **스스로 복구하는 능력**이다.

Kubernetes는 Pod가 죽으면 그것을 장애로 보고 다시 살리려고 한다.

예를 들어 Pod 하나가 죽었다고 하자.

```text
원하는 상태: Pod 3개
현재 상태: Pod 2개
```

그러면 Kubernetes는 새 Pod를 만든다.

```text
새 Pod 생성
현재 상태: Pod 3개
```

이것이 self-healing이다.

그래서 Kubernetes에서는 “Pod 하나가 죽었다”는 사실보다 더 중요한 질문이 있다.

```text
이 Pod를 누가 관리하고 있는가?
```

Pod를 Deployment가 관리하고 있다면, Pod가 죽어도 다시 만들어진다.

---

## 4. Reconciliation Loop란?

Kubernetes가 원하는 상태와 현재 상태를 계속 비교하면서 맞추는 반복 작업을 **reconciliation loop**라고 한다.

조금 쉽게 말하면 Kubernetes 내부에서 계속 이런 생각을 하고 있는 것이다.

```text
사용자가 원하는 상태가 뭐지?
현재 클러스터 상태는 뭐지?
둘이 다르네?
그럼 맞춰야지.
```

예를 들어 Deployment가 Pod 3개를 원한다면 Kubernetes는 계속 확인한다.

```text
1. Deployment가 원하는 replicas 확인
2. 현재 Pod 개수 확인
3. 부족하면 새 Pod 생성
4. 많으면 Pod 제거
5. 문제가 생기면 다시 조정
```

이 반복 구조 때문에 Kubernetes는 장애가 나도 자동으로 복구하려고 한다.

---

## 5. Pod 재생성 원리

Pod가 다시 생기는 이유는 보통 Pod 자체 때문이 아니다.

Pod 위에 있는 상위 리소스 때문이다.

대표적으로 Deployment가 있다.

```text
Deployment
 └── ReplicaSet
      └── Pod
```

Deployment는 ReplicaSet을 만들고, ReplicaSet은 Pod 개수를 유지한다.

그래서 Pod를 직접 지워도 ReplicaSet이 다시 Pod를 만든다.

흐름은 다음과 같다.

```text
1. 사용자가 Deployment 생성
2. Deployment가 ReplicaSet 생성
3. ReplicaSet이 Pod 생성
4. 사용자가 Pod 삭제
5. ReplicaSet이 Pod 개수 부족을 감지
6. 새 Pod 생성
```

그래서 Kubernetes에서 Pod를 지웠는데 계속 살아난다면 이렇게 봐야 한다.

```text
Pod가 독립적으로 존재하는 게 아니라
Deployment나 ReplicaSet이 관리하고 있구나.
```

---

# [KUBERNETES] Event가 중요한 이유

Kubernetes에서 문제가 생겼을 때 가장 먼저 봐야 하는 것 중 하나가 **Event**다.

특히 Pod가 안 뜨거나, 이미지 Pull이 안 되거나, CrashLoopBackOff가 뜨거나, Pending 상태에서 멈춰 있을 때 Event는 매우 중요하다.

실습에서도 “파드가 죽으면 이벤트부터 본다”, “describe pod 하면 Pulling, Created, Started 같은 정보가 쌓인다”는 흐름이 중요하게 다뤄진다. 

---

## 1. Event란?

Event는 Kubernetes가 리소스를 처리하면서 남기는 **상태 변화 기록**이다.

쉽게 말하면 Kubernetes의 작업 로그에 가깝다.

Pod 하나가 만들어질 때도 내부적으로 여러 일이 일어난다.

```text
이미지 가져오기
컨테이너 생성하기
컨테이너 시작하기
네트워크 붙이기
볼륨 붙이기
실패하면 재시도하기
```

이런 흐름이 Event에 남는다.

---

## 2. kubectl describe pod에서 Event 보기

Pod 문제를 볼 때 가장 많이 쓰는 명령어는 이것이다.

```bash
kubectl describe pod <pod-name>
```

이 명령어를 치면 Pod의 상세 정보가 나온다.

아래쪽으로 내려가면 보통 `Events` 섹션이 있다.

예시는 이런 식이다.

```text
Events:
  Type    Reason     Age   From               Message
  ----    ------     ----  ----               -------
  Normal  Scheduled  10s   default-scheduler  Successfully assigned default/nginx to node01
  Normal  Pulling    9s    kubelet            Pulling image "nginx"
  Normal  Pulled     5s    kubelet            Successfully pulled image "nginx"
  Normal  Created    4s    kubelet            Created container nginx
  Normal  Started    3s    kubelet            Started container nginx
```

이걸 보면 Kubernetes가 Pod를 만들기 위해 어떤 단계를 거쳤는지 알 수 있다.

---

## 3. Pulling / Created / Started 읽는 법

Event에서 자주 보는 상태는 다음과 같다.

```text
Pulling
= 컨테이너 이미지를 가져오는 중

Pulled
= 컨테이너 이미지를 가져오는 데 성공

Created
= 컨테이너를 생성함

Started
= 컨테이너 실행을 시작함
```

즉 정상적인 Pod 생성 흐름은 보통 이렇게 간다.

```text
Scheduled
→ Pulling
→ Pulled
→ Created
→ Started
→ Running
```

이 흐름이 보이면 Pod가 정상적으로 만들어졌다고 볼 수 있다.

---

## 4. Event를 보면 장애 원인을 좁힐 수 있다

Pod가 안 뜰 때 무작정 YAML만 보면 답이 안 보일 때가 많다.

이때 Event를 보면 어디서 막혔는지 알 수 있다.

예를 들어 이미지 이름이 틀렸다면 이런 식으로 나온다.

```text
Failed to pull image
ImagePullBackOff
ErrImagePull
```

이 경우 문제는 애플리케이션 코드가 아니라 이미지 이름, 태그, 레지스트리 접근 권한 쪽이다.

예를 들어 리소스가 부족하면 이런 식으로 나올 수 있다.

```text
0/1 nodes are available: insufficient cpu
```

이 경우 문제는 이미지도 아니고 코드도 아니다.
노드에 CPU가 부족해서 스케줄링이 안 되는 것이다.

예를 들어 볼륨 마운트가 실패하면 이런 식으로 나온다.

```text
MountVolume.SetUp failed
```

이 경우는 PVC, PV, StorageClass, 볼륨 경로 문제를 봐야 한다.

즉 Event는 장애 원인을 빠르게 분류해준다.

---

## 5. Pod 문제 해결 순서

Pod가 이상할 때는 아래 순서로 보면 좋다.

```bash
kubectl get pods
```

먼저 Pod 상태를 본다.

```text
Running
Pending
CrashLoopBackOff
ImagePullBackOff
Error
Completed
```

그다음 문제가 있는 Pod를 자세히 본다.

```bash
kubectl describe pod <pod-name>
```

여기서 아래쪽의 Events를 본다.

그다음 컨테이너 로그를 확인한다.

```bash
kubectl logs <pod-name>
```

만약 컨테이너가 여러 개라면 컨테이너 이름을 지정한다.

```bash
kubectl logs <pod-name> -c <container-name>
```

정리하면 장애 분석 순서는 이렇게 잡으면 된다.

```text
1. kubectl get pods
   현재 상태 확인

2. kubectl describe pod <pod-name>
   상세 정보와 Event 확인

3. Events 확인
   Kubernetes가 어디서 실패했는지 확인

4. kubectl logs <pod-name>
   애플리케이션 내부 로그 확인

5. YAML 확인
   image, port, env, volume, command, args 확인
```

---

## 6. Event를 먼저 봐야 하는 이유

Kubernetes 초반에는 문제가 생기면 자꾸 YAML만 보게 된다.

물론 YAML도 중요하다.
하지만 Pod가 실제로 어떻게 처리되었는지는 Event에 남는다.

YAML은 내가 의도한 설정이고, Event는 Kubernetes가 실제로 처리한 결과다.

```text
YAML
= 내가 이렇게 해달라고 선언한 것

Event
= Kubernetes가 그 선언을 처리하면서 남긴 기록
```

그래서 장애 분석에서는 Event를 꼭 봐야 한다.

---

# 정리

K3d는 Docker 위에서 K3s 기반 Kubernetes 클러스터를 빠르게 만들어주는 도구다. 로컬 개발 환경에서 Kubernetes를 실습하기 좋고, 클러스터 생성과 삭제가 빠르다.

Kubernetes는 desired state를 기준으로 현재 상태를 계속 비교하고, 다르면 다시 맞춘다. 그래서 Pod를 삭제해도 Deployment나 ReplicaSet이 관리하고 있다면 다시 생성된다. 이 동작은 self-healing과 reconciliation loop의 결과다.

Pod가 안 뜨거나 문제가 생겼을 때는 Event를 봐야 한다. `kubectl describe pod`의 Events 영역에는 `Pulling`, `Created`, `Started`, `Failed`, `BackOff` 같은 기록이 남고, 이 기록을 보면 문제가 이미지 Pull인지, 스케줄링인지, 볼륨인지, 애플리케이션 실행 문제인지 빠르게 좁힐 수 있다.

결국 Kubernetes를 이해하는 핵심은 이 세 가지다.

```text
K3d
= 로컬에서 Kubernetes를 빠르게 실습하는 도구

Desired State
= Kubernetes가 유지하려는 목표 상태

Event
= Kubernetes가 실제로 무슨 일을 했는지 보여주는 기록
```

Kubernetes는 단순히 컨테이너를 실행하는 도구가 아니라, **원하는 상태를 계속 유지하려고 움직이는 시스템**이다. 그래서 Pod가 다시 생기고, 장애가 나도 복구하려 하고, 그 과정이 Event에 기록된다.
