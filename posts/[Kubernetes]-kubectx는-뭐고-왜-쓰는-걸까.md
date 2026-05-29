---
title: "[KUBERNETES] kubectx는 뭐고 왜 쓰는 걸까?"
source: "https://velog.io/@yorange50/KUBERNETES-kubectx는-뭐고-왜-쓰는-걸까"
published: "2026-05-13T04:57:08.513Z"
tags: ""
backup_date: "2026-05-29T14:52:52.748490"
---

![](https://velog.velcdn.com/images/yorange50/post/a4d41c3c-c7da-4398-b818-fc2a43ffafec/image.png)

쿠버네티스를 쓰다 보면 `kubectl` 명령어를 많이 사용하게 된다.

처음에는 클러스터가 하나뿐이라 크게 헷갈릴 일이 없다.

```bash
kubectl get pods
kubectl get nodes
kubectl get svc
```

그런데 쿠버네티스를 계속 쓰다 보면 클러스터가 여러 개가 되는 순간이 온다.

예를 들면 이런 식이다.

```text
로컬 실습용 k3d 클러스터
Docker Desktop Kubernetes
minikube 클러스터
회사 개발 클러스터
회사 운영 클러스터
```

이때 중요한 질문이 생긴다.

```text
지금 내 kubectl은 어느 클러스터를 보고 있는가?
```

이걸 쉽게 확인하고 바꿀 수 있게 해주는 도구가 바로 **kubectx**다.

## kubectx란?

**kubectx는 Kubernetes context를 쉽게 확인하고 전환하는 CLI 도구**다.

조금 더 쉽게 말하면, `kubectl`이 바라보는 클러스터를 빠르게 바꿔주는 도구다.

쿠버네티스에서 `kubectl get pods`를 입력하면, 이 명령어는 아무 클러스터에나 요청을 보내는 것이 아니다.

현재 선택된 context를 기준으로 요청을 보낸다.

```bash
kubectl get pods
```

이 명령어의 실제 의미는 다음과 비슷하다.

```text
현재 context에 설정된 클러스터에 접속해서 Pod 목록을 가져와라
```

그래서 context가 잘못 잡혀 있으면 내가 의도하지 않은 클러스터를 보게 된다.

## context란 무엇인가?

쿠버네티스에서 context는 `kubectl`이 어느 클러스터에 어떤 사용자 정보로 접속할지를 정해둔 설정 묶음이다.

보통 context에는 다음 정보가 연결되어 있다.

```text
cluster
user
namespace
```

즉, context는 단순한 클러스터 이름이 아니다.

```text
context = cluster + user + namespace 설정 묶음
```

예를 들어 다음과 같은 context가 있을 수 있다.

```text
k3d-hello-cluster
docker-desktop
minikube
company-dev
company-prod
```

현재 context가 `k3d-hello-cluster`라면 `kubectl`은 로컬 k3d 클러스터를 바라본다.

현재 context가 `company-prod`라면 `kubectl`은 회사 운영 클러스터를 바라볼 수 있다.

이 차이가 매우 중요하다.

## kubectx가 필요한 이유

쿠버네티스에서 context 확인은 실수 방지와 직접 연결된다.

예를 들어 이런 명령어를 친다고 해보자.

```bash
kubectl delete pod my-app
```

내가 로컬 실습 클러스터에서 삭제한다고 생각했는데, 실제 현재 context가 운영 클러스터라면 문제가 커질 수 있다.

그래서 쿠버네티스를 다룰 때는 항상 현재 context를 확인하는 습관이 필요하다.

기본 `kubectl` 명령어로도 확인할 수 있다.

```bash
kubectl config current-context
```

context 목록은 이렇게 볼 수 있다.

```bash
kubectl config get-contexts
```

context 변경은 이렇게 한다.

```bash
kubectl config use-context k3d-hello-cluster
```

하지만 명령어가 길다. 그래서 `kubectx`를 쓰면 더 짧게 처리할 수 있다.

## kubectx로 context 목록 보기

현재 사용할 수 있는 context 목록은 다음 명령어로 확인한다.

```bash
kubectx
```

예를 들어 출력이 이렇게 나올 수 있다.

```text
k3d-hello-cluster
docker-desktop
minikube
```

이 목록은 현재 내 kubeconfig에 등록된 context들이다.

여기서 kubeconfig는 `kubectl`이 클러스터 접속 정보를 저장해두는 설정 파일이다.

보통 위치는 다음과 같다.

```bash
~/.kube/config
```

즉, `kubectx`는 완전히 새로운 정보를 만들어내는 것이 아니라, 내 kubeconfig 안에 있는 context 목록을 보기 쉽게 보여주는 도구다.

## 현재 context 확인하기

`kubectx`를 실행하면 context 목록을 볼 수 있고, 현재 선택된 context를 확인할 수 있다.

예를 들어 현재 context가 `k3d-hello-cluster`라면 다음처럼 표시된다.

```text
k3d-hello-cluster
```

이 말은 현재 `kubectl`이 `k3d-hello-cluster`라는 클러스터 설정을 바라보고 있다는 뜻이다.

스크린샷 상황도 이 흐름이다.

```bash
kubectx
```

출력:

```text
k3d-hello-cluster
```

즉, 현재 `kubectl` 명령어는 로컬 k3d 클러스터인 `k3d-hello-cluster`를 기준으로 실행된다.

## kubectx로 context 변경하기

다른 context로 변경하고 싶다면 context 이름을 붙여서 실행한다.

```bash
kubectx docker-desktop
```

그러면 현재 context가 `docker-desktop`으로 바뀐다.

이후 실행하는 `kubectl` 명령어는 `docker-desktop` 클러스터를 대상으로 한다.

```bash
kubectl get nodes
```

이 명령어는 이제 `docker-desktop` context에 연결된 클러스터에 요청을 보낸다.

다시 k3d 클러스터로 돌아가고 싶다면 다음처럼 입력한다.

```bash
kubectx k3d-hello-cluster
```

그러면 다시 `k3d-hello-cluster`가 현재 context가 된다.

## 이전 context로 돌아가기

kubectx에는 바로 이전 context로 돌아가는 기능도 있다.

```bash
kubectx -
```

예를 들어 현재 context가 `k3d-hello-cluster`였고, 방금 `docker-desktop`으로 바꿨다고 해보자.

```bash
kubectx docker-desktop
```

이후 다시 이전 context로 돌아가고 싶으면 다음 명령어를 입력하면 된다.

```bash
kubectx -
```

그러면 다시 `k3d-hello-cluster`로 돌아간다.

여러 클러스터를 오가면서 확인할 때 유용하다.

## kubectl config와 kubectx의 차이

kubectx는 새로운 기능을 제공한다기보다, 기존 `kubectl config` 명령어를 더 짧고 편하게 사용할 수 있게 해주는 도구다.

| 작업             | kubectl 기본 명령어                   | kubectx      |
| -------------- | -------------------------------- | ------------ |
| 현재 context 확인  | `kubectl config current-context` | `kubectx`    |
| context 목록 보기  | `kubectl config get-contexts`    | `kubectx`    |
| context 변경     | `kubectl config use-context 이름`  | `kubectx 이름` |
| 이전 context로 이동 | 직접 다시 변경                         | `kubectx -`  |

즉, 핵심은 이거다.

```text
kubectl config = 원래 방식
kubectx = context 전환을 쉽게 만든 방식
```

## 스크린샷 상황으로 이해하기

스크린샷에서는 k3d 클러스터가 생성되어 있다.

```text
Cluster 'hello-cluster' created successfully!
```

그리고 노드도 정상적으로 Ready 상태다.

```text
k3d-hello-cluster-server-0   Ready   control-plane,master
```

이후 `kubectx`를 실행하면 다음과 같이 나온다.

```text
k3d-hello-cluster
```

이 뜻은 다음과 같다.

```text
현재 kubectl은 k3d-hello-cluster를 바라보고 있다.
```

그래서 다음 명령어를 치면:

```bash
kubectl get nodes
```

`k3d-hello-cluster` 안의 노드가 조회된다.

그리고 다음 명령어를 치면:

```bash
kubectl get pods
```

`k3d-hello-cluster` 안의 현재 namespace에서 Pod를 찾는다.

만약 결과가 이렇게 나와도:

```text
No resources found in default namespace.
```

이건 클러스터 연결 문제가 아니다.

현재 context는 정상이고, 단지 default namespace에 Pod가 없다는 뜻이다.

## kubectx를 사용할 때 꼭 기억할 점

kubectx에서 가장 중요한 건 **현재 context가 어디인지 확인하는 습관**이다.

특히 여러 클러스터를 다룰 때는 더 중요하다.

```text
로컬 클러스터인지
개발 클러스터인지
운영 클러스터인지
```

이걸 확인하지 않고 명령어를 치면 실수할 수 있다.

특히 다음과 같은 명령어를 실행하기 전에는 context를 꼭 확인하는 것이 좋다.

```bash
kubectl delete
kubectl apply
kubectl rollout restart
kubectl scale
```

조회 명령어는 비교적 안전하지만, 삭제나 변경 명령어는 실제 클러스터 상태를 바꾼다.

그래서 kubectx는 단순히 편의 도구가 아니라, 여러 클러스터 환경에서 실수를 줄여주는 도구라고 볼 수 있다.

## 정리

kubectx는 Kubernetes context를 쉽게 확인하고 전환하기 위한 CLI 도구다. context는 `kubectl`이 어느 클러스터에 어떤 사용자 정보와 namespace 기준으로 접속할지를 정해둔 설정 묶음이다. 쿠버네티스 클러스터가 하나뿐일 때는 크게 필요성을 못 느낄 수 있지만, k3d, minikube, docker-desktop, 개발 클러스터, 운영 클러스터처럼 여러 환경을 다루기 시작하면 매우 유용해진다. `kubectx`를 사용하면 context 목록 확인, context 변경, 이전 context 복귀를 짧은 명령어로 처리할 수 있다. 핵심은 `kubectl` 명령어를 실행하기 전에 현재 context가 어디인지 확인하는 습관이다. 특히 삭제, 배포, 재시작 같은 작업 전에는 반드시 현재 context를 확인해야 한다.
