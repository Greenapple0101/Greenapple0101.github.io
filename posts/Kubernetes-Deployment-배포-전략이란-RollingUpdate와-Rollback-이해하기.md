---
title: "[Kubernetes] Deployment 배포 전략이란? RollingUpdate와 Rollback 이해하기"
source: "https://velog.io/@yorange50/Kubernetes-Deployment-배포-전략이란-RollingUpdate와-Rollback-이해하기"
published: "2026-05-14T01:51:01.681Z"
tags: ""
backup_date: "2026-05-29T14:52:52.743709"
---


Kubernetes에서 애플리케이션을 운영하다 보면 단순히 Pod를 한 번 실행하는 것보다 더 중요한 문제가 생긴다. 바로 “새 버전으로 어떻게 안전하게 바꿀 것인가?”이다. 예를 들어 현재 `kodekloud/webapp-color:v1` 이미지를 사용 중인데, 새 버전인 `v2`로 바꾸고 싶다고 하자. 이때 기존 Pod를 전부 한 번에 죽이고 새 Pod를 띄우면 순간적으로 서비스가 끊길 수 있다. 그래서 Kubernetes의 Deployment는 애플리케이션을 안전하게 업데이트하기 위한 배포 전략을 제공한다. 대표적인 전략이 `RollingUpdate`이고, 문제가 생겼을 때 이전 버전으로 되돌리는 기능이 `Rollback`이다.

---

## 1. Deployment는 왜 필요한가?

Pod는 Kubernetes에서 컨테이너를 실행하는 가장 작은 단위다. 하지만 Pod만 직접 만들면 운영이 불편하다. Pod가 죽었을 때 다시 살려야 하고, 개수를 늘려야 하고, 새 버전으로 교체해야 한다.

이 역할을 해주는 리소스가 Deployment다.

Deployment는 직접 Pod를 관리하는 것이 아니라 중간에 ReplicaSet을 만들고, ReplicaSet이 Pod를 관리하게 한다.

```text
Deployment
  ↓
ReplicaSet
  ↓
Pod
```

그래서 우리가 Deployment를 수정하면 Kubernetes는 새로운 ReplicaSet을 만들고, 기존 ReplicaSet의 Pod를 줄이면서 새 ReplicaSet의 Pod를 늘린다.

이 과정이 바로 Rolling Update다.

---

## 2. 현재 Deployment 상태 보기

Deployment 상태는 다음 명령어로 확인할 수 있다.

```bash
kubectl describe deployment frontend
```

예시 출력 중 중요한 부분은 다음과 같다.

```text
Name:                   frontend
Namespace:              default
Replicas:               4 desired | 4 updated | 4 total | 4 available | 0 unavailable
StrategyType:           RollingUpdate
MinReadySeconds:        20
RollingUpdateStrategy:  25% max unavailable, 25% max surge
```

이 출력만 봐도 현재 Deployment가 어떻게 배포되고 있는지 알 수 있다.

---

## 3. Replicas 상태 해석하기

```text
Replicas: 4 desired | 4 updated | 4 total | 4 available | 0 unavailable
```

하나씩 보면 다음과 같다.

```text
4 desired
```

원하는 Pod 개수가 4개라는 뜻이다. Deployment의 `replicas: 4` 설정과 연결된다.

```text
4 updated
```

현재 Deployment의 최신 설정으로 업데이트된 Pod가 4개라는 뜻이다. 만약 새 이미지를 배포하는 중이라면 이 숫자가 점점 올라간다.

```text
4 total
```

현재 존재하는 전체 Pod 개수다.

```text
4 available
```

실제로 사용 가능한 Ready 상태의 Pod가 4개라는 뜻이다.

```text
0 unavailable
```

사용 불가능한 Pod가 없다는 뜻이다.

즉 이 상태는 정상이다. 원하는 개수도 4개, 최신 버전도 4개, 사용 가능한 Pod도 4개이기 때문이다.

---

## 4. StrategyType: RollingUpdate

출력에서 가장 중요한 부분 중 하나가 이것이다.

```text
StrategyType: RollingUpdate
```

Deployment의 기본 배포 전략은 `RollingUpdate`다.

RollingUpdate는 기존 Pod를 한 번에 전부 죽이지 않고, 조금씩 새 버전 Pod로 교체하는 방식이다.

예를 들어 현재 v1 Pod가 4개 떠 있다고 하자.

```text
v1 v1 v1 v1
```

여기서 이미지를 v2로 바꾸면 Kubernetes는 대략 이런 식으로 움직인다.

```text
v1 v1 v1 v1
↓
v1 v1 v1 v1 v2
↓
v1 v1 v1 v2
↓
v1 v1 v2 v2
↓
v1 v2 v2 v2
↓
v2 v2 v2 v2
```

즉 서비스가 완전히 내려가지 않도록 기존 Pod와 새 Pod를 섞어서 교체한다.

---

## 5. max unavailable이란?

출력에 이런 값이 있다.

```text
25% max unavailable
```

`max unavailable`은 Rolling Update 중에 사용 불가능해도 되는 Pod의 최대 개수다.

현재 replicas가 4개이고, max unavailable이 25%라면:

```text
4개의 25% = 1개
```

즉 업데이트 중에 최대 1개까지는 unavailable 상태가 되어도 된다는 뜻이다.

다르게 말하면, 최소 3개는 계속 사용 가능한 상태로 유지하려고 한다.

```text
전체 Pod: 4개
최대 unavailable: 1개
최소 available: 3개
```

그래서 서비스 중단을 줄일 수 있다.

---

## 6. max surge란?

또 이런 값도 있다.

```text
25% max surge
```

`max surge`는 Rolling Update 중에 원래 replicas 개수보다 추가로 더 만들 수 있는 Pod의 최대 개수다.

현재 replicas가 4개이고, max surge가 25%라면:

```text
4개의 25% = 1개
```

즉 업데이트 중에 잠깐 Pod가 5개까지 늘어날 수 있다.

```text
원래 원하는 개수: 4개
추가로 더 만들 수 있는 개수: 1개
업데이트 중 최대 Pod 개수: 5개
```

왜 굳이 더 만들까?

새 Pod가 정상적으로 Ready 상태가 된 뒤에 기존 Pod를 줄이기 위해서다. 이렇게 하면 서비스 안정성이 좋아진다.

---

## 7. RollingUpdateStrategy 정리

현재 설정은 다음과 같다.

```text
RollingUpdateStrategy: 25% max unavailable, 25% max surge
```

replicas가 4개라면 의미는 이렇다.

```text
max unavailable: 1개까지 unavailable 허용
max surge: 1개까지 추가 생성 허용
```

그래서 업데이트 중 Pod 개수는 대략 3개에서 5개 사이로 유지될 수 있다.

```text
최소 사용 가능 Pod 수: 3개
최대 전체 Pod 수: 5개
```

이 방식 덕분에 새 버전 배포 중에도 서비스가 완전히 끊기지 않는다.

---

## 8. 이미지 업데이트하기

현재 Deployment가 이런 이미지를 사용 중이라고 하자.

```text
kodekloud/webapp-color:v1
```

새 버전으로 바꾸려면 다음 명령어를 사용할 수 있다.

```bash
kubectl set image deployment/frontend simple-webapp=kodekloud/webapp-color:v2
```

구조는 다음과 같다.

```bash
kubectl set image deployment/<deployment-name> <container-name>=<new-image>
```

여기서:

```text
deployment/frontend
```

`frontend`라는 Deployment를 수정한다는 뜻이다.

```text
simple-webapp
```

Deployment 안에 있는 컨테이너 이름이다.

```text
kodekloud/webapp-color:v2
```

새로 적용할 이미지다.

명령어를 실행하면 Kubernetes는 새 ReplicaSet을 만들고 Rolling Update를 시작한다.

---

## 9. Rollout 상태 확인하기

업데이트가 잘 진행되는지 보려면 다음 명령어를 사용한다.

```bash
kubectl rollout status deployment/frontend
```

정상적으로 배포되면 이런 식으로 나온다.

```text
deployment "frontend" successfully rolled out
```

업데이트 중이라면 새 Pod가 Ready 될 때까지 기다리는 메시지가 나온다.

---

## 10. ReplicaSet 확인하기

Deployment가 업데이트되면 ReplicaSet이 어떻게 바뀌는지도 볼 수 있다.

```bash
kubectl get replicaset
```

또는 짧게:

```bash
kubectl get rs
```

Rolling Update 전에는 ReplicaSet이 하나만 있을 수 있다.

```text
frontend-685dfcc44   4   4   4
```

업데이트 후에는 이전 ReplicaSet과 새 ReplicaSet이 같이 보일 수 있다.

```text
frontend-685dfcc44   0   0   0
frontend-7c9f8d9b    4   4   4
```

이전 ReplicaSet을 바로 삭제하지 않는 이유는 Rollback을 위해서다.

---

## 11. Rollout history 확인하기

Deployment의 배포 이력을 보려면 다음 명령어를 사용한다.

```bash
kubectl rollout history deployment/frontend
```

예시는 다음과 같다.

```text
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
```

몇 번째 배포인지 확인할 수 있다.

더 자세히 보고 싶으면 revision 번호를 지정할 수 있다.

```bash
kubectl rollout history deployment/frontend --revision=2
```

---

## 12. Rollback이란?

Rollback은 새 버전 배포 후 문제가 생겼을 때 이전 버전으로 되돌리는 기능이다.

예를 들어 v1에서 v2로 업데이트했는데, v2 애플리케이션에 문제가 있다고 하자.

이때 다시 v1 이미지를 직접 찾아서 수정할 수도 있지만, Kubernetes Deployment는 이전 ReplicaSet 정보를 가지고 있기 때문에 명령어 하나로 되돌릴 수 있다.

```bash
kubectl rollout undo deployment/frontend
```

이 명령어를 실행하면 직전 revision으로 돌아간다.

---

## 13. 특정 revision으로 Rollback하기

바로 직전 버전이 아니라 특정 revision으로 돌아가고 싶을 수도 있다.

그럴 때는 다음 명령어를 사용한다.

```bash
kubectl rollout undo deployment/frontend --to-revision=1
```

이 명령어는 Deployment를 revision 1 상태로 되돌린다.

---

## 14. 배포 일시정지와 재개

Deployment에는 배포를 잠깐 멈추는 기능도 있다.

```bash
kubectl rollout pause deployment/frontend
```

이 상태에서는 Deployment 변경 사항이 바로 배포되지 않는다.

예를 들어 여러 설정을 한 번에 바꾸고 싶을 때 사용할 수 있다.

다시 배포를 진행하려면 다음 명령어를 사용한다.

```bash
kubectl rollout resume deployment/frontend
```

---

## 15. recreate 전략이란?

Deployment에는 RollingUpdate 말고 `Recreate` 전략도 있다.

```yaml
strategy:
  type: Recreate
```

Recreate는 기존 Pod를 모두 삭제한 뒤 새 Pod를 만드는 방식이다.

```text
v1 v1 v1 v1
↓
전부 삭제
↓
v2 v2 v2 v2
```

이 방식은 단순하지만 중간에 서비스가 끊길 수 있다.

그래서 일반적인 웹 애플리케이션에서는 RollingUpdate를 많이 사용한다.

다만 동시에 두 버전이 떠 있으면 안 되는 애플리케이션이라면 Recreate가 필요할 수도 있다.

예를 들어 특정 락 파일이나 단일 writer 구조 때문에 v1과 v2가 동시에 실행되면 문제가 생기는 경우다.

---

## 16. CKA에서 자주 보는 명령어

CKA에서는 배포 전략 문제에서 이런 명령어들이 자주 나온다.

Deployment 상태 확인:

```bash
kubectl describe deployment frontend
```

이미지 업데이트:

```bash
kubectl set image deployment/frontend simple-webapp=kodekloud/webapp-color:v2
```

rollout 상태 확인:

```bash
kubectl rollout status deployment/frontend
```

배포 이력 확인:

```bash
kubectl rollout history deployment/frontend
```

rollback:

```bash
kubectl rollout undo deployment/frontend
```

특정 revision으로 rollback:

```bash
kubectl rollout undo deployment/frontend --to-revision=1
```

ReplicaSet 확인:

```bash
kubectl get rs
```

Pod 확인:

```bash
kubectl get pods
```

---

## 17. describe deployment에서 봐야 할 부분

`kubectl describe deployment`를 쳤을 때는 모든 줄을 다 외우려고 하지 말고, 아래 순서로 보면 된다.

```text
Replicas
```

원하는 Pod 개수와 실제 사용 가능한 Pod 개수를 본다.

```text
StrategyType
```

RollingUpdate인지 Recreate인지 본다.

```text
RollingUpdateStrategy
```

max unavailable, max surge 값을 본다.

```text
Pod Template
```

컨테이너 이름, 이미지, 포트를 본다.

```text
Conditions
```

Available, Progressing 상태를 본다.

```text
NewReplicaSet / OldReplicaSets
```

현재 어떤 ReplicaSet이 사용 중인지 본다.

```text
Events
```

최근에 어떤 일이 있었는지 본다.

---

## 18. 지금 출력 해석

현재 출력은 대략 이런 상태다.

```text
Name: frontend
Replicas: 4 desired | 4 updated | 4 total | 4 available | 0 unavailable
StrategyType: RollingUpdate
MinReadySeconds: 20
RollingUpdateStrategy: 25% max unavailable, 25% max surge
Image: kodekloud/webapp-color:v1
NewReplicaSet: frontend-685dfcc44
```

해석하면:

```text
frontend Deployment가 default namespace에 있음
원하는 Pod 개수는 4개
현재 4개 모두 최신 상태
4개 모두 available
문제 있는 Pod 없음
배포 전략은 RollingUpdate
업데이트 중 최대 1개 unavailable 허용
업데이트 중 최대 1개 추가 Pod 생성 가능
현재 이미지는 kodekloud/webapp-color:v1
현재 ReplicaSet은 frontend-685dfcc44
```

즉 지금은 정상 상태다.

---

## 19. 정리

Kubernetes Deployment의 배포 전략은 애플리케이션을 새 버전으로 안전하게 바꾸는 방식이다. 기본 전략은 RollingUpdate이며, 기존 Pod를 한 번에 모두 죽이지 않고 조금씩 새 Pod로 교체한다. `max unavailable`은 업데이트 중 사용 불가능해도 되는 Pod 수를 정하고, `max surge`는 업데이트 중 추가로 만들 수 있는 Pod 수를 정한다. 배포가 잘못되면 `kubectl rollout undo`로 이전 버전으로 되돌릴 수 있다. CKA에서는 이 개념을 외우는 것보다 `describe`, `set image`, `rollout status`, `rollout history`, `rollout undo` 명령어 흐름을 손에 익히는 것이 중요하다.
