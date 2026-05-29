---
title: "[CKA] KodeKloud Pod 문제 풀면서 익힌 기본 명령어 정리\n"
source: "https://velog.io/@yorange50/Kubernetes-KodeKloud-Pod-문제-풀면서-익힌-기본-명령어-정리"
published: "2026-05-06T22:29:26.075Z"
tags: ""
backup_date: "2026-05-29T14:52:52.774527"
---

KodeKloud에서 Kubernetes Pod 문제를 풀다 보면 처음에는 명령어 자체보다도 “문제에서 뭘 물어보는지”를 해석하는 게 더 헷갈린다. 특히 `kubectl get pods`, `READY`, `describe`, `delete` 같은 명령어는 초반 Pod 실습에서 거의 계속 나온다. 이번 글은 KodeKloud Pod 문제를 풀면서 실제로 자주 만난 명령어와 헷갈렸던 부분을 정리한 내용이다.

---

## Pod란?

Pod는 Kubernetes에서 컨테이너가 실행되는 가장 작은 단위다.

보통 Docker에서는 컨테이너 하나를 바로 실행한다고 생각하지만, Kubernetes에서는 컨테이너를 직접 관리하기보다 Pod라는 단위 안에 컨테이너를 넣어서 관리한다.

즉, 구조를 간단히 보면 다음과 같다.

```text
Kubernetes
 └── Pod
      └── Container
```

보통 Pod 하나에는 컨테이너 하나가 들어가는 경우가 많지만, 필요하면 Pod 하나 안에 컨테이너가 여러 개 들어갈 수도 있다.

---

## 현재 Pod 목록 확인하기

가장 기본 명령어는 다음과 같다.

```bash
kubectl get pods
```

또는 짧게 alias가 잡혀 있다면 다음처럼 쓸 수도 있다.

```bash
k get pods
```

실행하면 대략 이런 형태로 나온다.

```bash
NAME            READY   STATUS             RESTARTS   AGE
newpods-r6mnr   1/1     Running            0          10m
newpods-dw8lv   1/1     Running            0          10m
newpods-5x6jn   1/1     Running            0          10m
nginx           1/1     Running            0          8m42s
webapp          1/2     ImagePullBackOff   0          5m42s
```

각 컬럼의 의미는 다음과 같다.

| 컬럼       | 의미                     |
| -------- | ---------------------- |
| NAME     | Pod 이름                 |
| READY    | 준비된 컨테이너 수 / 전체 컨테이너 수 |
| STATUS   | Pod 상태                 |
| RESTARTS | 재시작 횟수                 |
| AGE      | 생성된 지 얼마나 지났는지         |

---

## READY 컬럼의 의미

`READY` 컬럼은 Pod 안에 있는 컨테이너 중 몇 개가 정상 준비 상태인지 보여준다.

예를 들어 다음과 같은 출력이 있다고 하자.

```bash
NAME      READY   STATUS    RESTARTS   AGE
nginx     1/1     Running   0          5m
webapp    1/2     Running   0          3m
```

여기서 `nginx`의 `READY`가 `1/1`이라는 것은 다음 의미다.

```text
전체 컨테이너 1개 중 1개가 Ready 상태
```

반면 `webapp`의 `READY`가 `1/2`라면 다음 의미다.

```text
전체 컨테이너 2개 중 1개만 Ready 상태
```

즉, `webapp` Pod 안에는 컨테이너가 2개 있는데 그중 하나는 아직 정상 준비되지 않았다는 뜻이다.

KodeKloud 문제에서 이런 질문이 나올 수 있다.

```text
What does the READY column in the output of the kubectl get pods command indicate?
```

정답은 다음과 같이 이해하면 된다.

```text
READY 컬럼은 Pod 안의 전체 컨테이너 중 몇 개의 컨테이너가 Ready 상태인지 나타낸다.
```

영어로 답하면 다음과 같다.

```text
It indicates how many containers in the pod are ready out of the total number of containers in that pod.
```

---

## Pod 상태 확인하기

Pod 목록을 보면 `STATUS` 컬럼도 중요하다.

자주 보이는 상태는 다음과 같다.

| STATUS            | 의미                        |
| ----------------- | ------------------------- |
| Running           | 정상 실행 중                   |
| Pending           | 아직 실행될 노드가 정해지지 않았거나 준비 중 |
| ContainerCreating | 컨테이너 생성 중                 |
| ImagePullBackOff  | 이미지를 가져오지 못해서 재시도 중       |
| ErrImagePull      | 이미지 가져오기 실패               |
| CrashLoopBackOff  | 컨테이너가 실행됐다가 계속 죽는 중       |
| Completed         | 작업이 끝남                    |

예를 들어 다음 상태를 보자.

```bash
webapp   1/2   ImagePullBackOff   0   5m42s
```

이 경우 `webapp` Pod 안에 컨테이너는 2개인데, 그중 하나가 이미지를 가져오지 못해서 정상 실행되지 못하고 있는 상태다.

---

## Pod 자세히 보기

Pod의 자세한 정보를 보려면 `describe`를 사용한다.

```bash
kubectl describe pod webapp
```

또는 짧게:

```bash
k describe pod webapp
```

이 명령어로 확인할 수 있는 내용은 다음과 같다.

| 항목         | 설명                           |
| ---------- | ---------------------------- |
| Name       | Pod 이름                       |
| Namespace  | Pod가 속한 namespace            |
| Node       | Pod가 배치된 노드                  |
| Containers | Pod 안의 컨테이너 목록               |
| Image      | 각 컨테이너가 사용하는 이미지             |
| State      | 컨테이너 상태                      |
| Events     | 스케줄링, 이미지 다운로드, 실행 실패 등의 이벤트 |

특히 에러가 났을 때는 아래쪽 `Events`를 잘 봐야 한다.

예를 들어 이런 로그가 있을 수 있다.

```bash
Failed to pull image "agentx"
Error: ImagePullBackOff
```

이 뜻은 Kubernetes가 `agentx`라는 이미지를 가져오려고 했는데 실패했다는 뜻이다.

이미지 이름이 틀렸거나, 존재하지 않거나, 권한이 필요한 private image일 수 있다.

---

## Pod가 어느 노드에 올라갔는지 확인하기

KodeKloud 문제에서 이런 질문도 자주 나온다.

```text
Which nodes are these pods placed on?
```

이럴 때는 `-o wide` 옵션을 붙이면 된다.

```bash
kubectl get pods -o wide
```

출력 예시:

```bash
NAME      READY   STATUS    IP           NODE
nginx     1/1     Running   10.42.0.10   controlplane
webapp    1/2     Running   10.42.0.11   node01
```

여기서 `NODE` 컬럼을 보면 각 Pod가 어느 노드에 배치됐는지 알 수 있다.

---

## Pod 안의 컨테이너 개수 확인하기

문제에서 이런 식으로 물어볼 수 있다.

```text
How many containers are part of the webapp pod?
```

이때는 먼저 `describe`로 확인하면 된다.

```bash
kubectl describe pod webapp
```

출력 중에서 `Containers:` 부분을 보면 된다.

예시:

```bash
Containers:
  nginx:
  agentx:
```

이렇게 컨테이너 이름이 2개 나오면 `webapp` Pod 안에는 컨테이너가 2개 있는 것이다.

또는 명령어로 간단히 확인할 수도 있다.

```bash
kubectl get pod webapp -o jsonpath='{.spec.containers[*].name}'
```

출력 예시:

```bash
nginx agentx
```

이 경우 컨테이너는 2개다.

---

## Pod가 사용하는 이미지 확인하기

문제에서 이런 질문도 나온다.

```text
Which image is specified for the pod?
```

이때는 다음 명령어를 사용한다.

```bash
kubectl describe pod webapp
```

그리고 `Image:` 부분을 보면 된다.

또는 더 짧게 확인하려면 다음처럼 쓸 수 있다.

```bash
kubectl get pod webapp -o jsonpath='{.spec.containers[*].image}'
```

출력 예시:

```bash
nginx agentx
```

이 경우 `webapp` Pod는 `nginx`, `agentx` 이미지를 사용하고 있다는 뜻이다.

---

## nginx Pod 생성하기

KodeKloud에서 자주 나오는 문제다.

```text
Create a new pod using the nginx image.
```

이때는 다음 명령어를 사용한다.

```bash
kubectl run nginx --image=nginx
```

의미는 다음과 같다.

```text
nginx라는 이름의 Pod를 만들고, nginx 이미지를 사용한다.
```

구조로 보면 다음과 같다.

```bash
kubectl run <pod-name> --image=<image-name>
```

예를 들어 `webapp`이라는 이름의 Pod를 `nginx` 이미지로 만들고 싶으면 다음처럼 쓴다.

```bash
kubectl run webapp --image=nginx
```

---

## Pod 삭제하기

Pod를 삭제할 때는 다음 명령어를 사용한다.

```bash
kubectl delete pod webapp
```

또는 짧게:

```bash
k delete pod webapp
```

KodeKloud에서 이런 문제가 나올 수 있다.

```text
Delete the webapp Pod.
Once deleted, wait for the pod to fully terminate.
```

이 경우 정답 명령어는 다음과 같다.

```bash
kubectl delete pod webapp
```

삭제 후에는 바로 Check를 누르지 말고, Pod가 완전히 사라졌는지 확인하는 게 좋다.

```bash
kubectl get pods
```

목록에서 `webapp`이 사라졌으면 삭제가 완료된 것이다.

---

## `<webapp>`이라고 치면 안 되는 이유

실습하면서 헷갈렸던 부분이 있다.

처음에는 이런 식으로 입력했다.

```bash
kubectl delete pod <webapp>
```

그랬더니 이런 에러가 났다.

```bash
-bash: syntax error near unexpected token `newline'
```

이유는 간단하다.

문서에서 자주 보이는 `<pod-name>` 같은 표기는 “여기에 실제 Pod 이름을 넣으세요”라는 뜻이다.
실제로 명령어에 `< >`까지 입력하라는 뜻이 아니다.

즉, 아래처럼 쓰면 안 된다.

```bash
kubectl delete pod <webapp>
```

정확한 명령어는 다음과 같다.

```bash
kubectl delete pod webapp
```

정리하면 다음과 같다.

| 잘못된 명령어                       | 올바른 명령어                     |
| ----------------------------- | --------------------------- |
| `kubectl delete pod <webapp>` | `kubectl delete pod webapp` |
| `k delete pod <webapp>`       | `k delete pod webapp`       |

`< >`는 설명용 표시일 뿐 실제 명령어에는 넣지 않는다.

---

## Pod 개수 세기

문제에서 이런 질문이 나올 수 있다.

```text
How many pods exist on the system?
In the current(default) namespace.
```

이때는 현재 namespace의 Pod만 보면 된다.

```bash
kubectl get pods
```

만약 개수를 명령어로 세고 싶으면 Linux 환경에서는 다음처럼 쓸 수 있다.

```bash
kubectl get pods --no-headers | wc -l
```

하지만 KodeKloud 초반 문제에서는 보통 `kubectl get pods`를 보고 눈으로 세도 충분하다.

주의할 점은 문제에서 `current(default) namespace`라고 했으면 `-A`를 붙이면 안 된다는 것이다.

```bash
kubectl get pods -A
```

이 명령어는 모든 namespace의 Pod를 보여준다.
문제가 default namespace만 물어보는 경우에는 답이 달라질 수 있다.

---

## 전체 namespace의 Pod 보기

모든 namespace의 Pod를 보고 싶을 때는 다음 명령어를 사용한다.

```bash
kubectl get pods -A
```

또는:

```bash
kubectl get pods --all-namespaces
```

하지만 KodeKloud 문제에서는 “현재 namespace에서”라고 하는지, “전체 시스템에서”라고 하는지 잘 읽어야 한다.

---

## Pod 로그 확인하기

Pod의 로그를 보고 싶으면 다음 명령어를 사용한다.

```bash
kubectl logs webapp
```

Pod 안에 컨테이너가 하나라면 이 명령어로 충분하다.

하지만 Pod 안에 컨테이너가 여러 개 있으면 컨테이너 이름을 지정해야 한다.

```bash
kubectl logs webapp -c nginx
```

형식은 다음과 같다.

```bash
kubectl logs <pod-name> -c <container-name>
```

여기서도 마찬가지로 `< >`는 실제로 입력하지 않는다.

---

## Pod 안으로 들어가기

Pod 내부에 접속하고 싶을 때는 `exec`를 사용한다.

```bash
kubectl exec -it webapp -- sh
```

만약 bash가 있는 이미지라면 다음처럼 쓸 수도 있다.

```bash
kubectl exec -it webapp -- bash
```

하지만 `nginx`, `busybox`, `alpine` 같은 가벼운 이미지는 bash가 없는 경우가 많다.
그럴 때는 보통 `sh`를 사용한다.

```bash
kubectl exec -it webapp -- sh
```

---

## Pod YAML 확인하기

Pod의 전체 설정을 YAML로 보고 싶으면 다음 명령어를 사용한다.

```bash
kubectl get pod webapp -o yaml
```

이 명령어로 확인할 수 있는 것들은 다음과 같다.

| 항목       | 설명                        |
| -------- | ------------------------- |
| metadata | 이름, 라벨, namespace 등       |
| spec     | 컨테이너 이미지, 포트, 볼륨 등 원하는 상태 |
| status   | 현재 상태, IP, 컨테이너 상태 등      |

Pod 설정을 더 정확히 보고 싶을 때는 `describe`와 `-o yaml`을 같이 활용하면 좋다.

---

## Pod YAML 파일 만들기

시험이나 실습에서는 명령어로 바로 Pod를 만들 수도 있지만, YAML 파일을 만들어 수정하는 방식도 많이 쓴다.

다음 명령어는 Pod를 실제로 만들지 않고 YAML 파일만 생성한다.

```bash
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml
```

생성된 파일 확인:

```bash
cat pod.yaml
```

적용:

```bash
kubectl apply -f pod.yaml
```

또는:

```bash
kubectl create -f pod.yaml
```

---

## KodeKloud Pod 문제 풀이 흐름

Pod 문제를 풀 때는 보통 다음 순서로 접근하면 된다.

### 1. 먼저 Pod 목록 확인

```bash
kubectl get pods
```

현재 어떤 Pod가 있는지 확인한다.

---

### 2. 자세한 정보 확인

```bash
kubectl describe pod webapp
```

이미지, 컨테이너 개수, 이벤트, 에러 원인 등을 확인한다.

---

### 3. 노드 정보까지 확인

```bash
kubectl get pods -o wide
```

Pod가 어느 노드에 올라갔는지 확인한다.

---

### 4. 필요한 경우 로그 확인

```bash
kubectl logs webapp
```

컨테이너가 여러 개면:

```bash
kubectl logs webapp -c nginx
```

---

### 5. 삭제 문제면 delete 사용

```bash
kubectl delete pod webapp
```

삭제 후 확인:

```bash
kubectl get pods
```

---

## 자주 나오는 문제별 명령어 정리

### Create a new pod using the nginx image.

```bash
kubectl run nginx --image=nginx
```

---

### How many pods exist on the system?

```bash
kubectl get pods
```

---

### What does the READY column indicate?

```text
Pod 안의 전체 컨테이너 중 Ready 상태인 컨테이너 수를 나타낸다.
```

예시:

```text
1/2 = 전체 컨테이너 2개 중 1개가 Ready 상태
```

---

### Which image is specified for the pod?

```bash
kubectl describe pod <pod-name>
```

예시:

```bash
kubectl describe pod webapp
```

또는:

```bash
kubectl get pod webapp -o jsonpath='{.spec.containers[*].image}'
```

---

### Which nodes are these pods placed on?

```bash
kubectl get pods -o wide
```

---

### How many containers are part of the webapp pod?

```bash
kubectl describe pod webapp
```

또는:

```bash
kubectl get pod webapp -o jsonpath='{.spec.containers[*].name}'
```

---

### Delete the webapp Pod.

```bash
kubectl delete pod webapp
```

삭제 확인:

```bash
kubectl get pods
```

---

## 헷갈리지 말아야 할 것

문서나 문제 풀이에서 자주 나오는 이런 표기들이 있다.

```bash
kubectl describe pod <pod-name>
kubectl delete pod <pod-name>
kubectl logs <pod-name>
```

여기서 `<pod-name>`은 실제로 입력하는 값이 아니다.

예를 들어 Pod 이름이 `webapp`이면 다음처럼 입력해야 한다.

```bash
kubectl describe pod webapp
kubectl delete pod webapp
kubectl logs webapp
```

아래처럼 입력하면 안 된다.

```bash
kubectl delete pod <webapp>
```

`< >`는 설명용 기호다.
실제 터미널에서는 빼고 입력해야 한다.

---

## 핵심 명령어만 다시 정리

```bash
kubectl get pods
```

Pod 목록 확인

```bash
kubectl get pods -o wide
```

Pod 목록과 노드 정보 확인

```bash
kubectl describe pod webapp
```

Pod 상세 정보 확인

```bash
kubectl run nginx --image=nginx
```

nginx 이미지로 Pod 생성

```bash
kubectl delete pod webapp
```

Pod 삭제

```bash
kubectl logs webapp
```

Pod 로그 확인

```bash
kubectl exec -it webapp -- sh
```

Pod 내부 접속

```bash
kubectl get pod webapp -o yaml
```

Pod YAML 확인

```bash
kubectl get pod webapp -o jsonpath='{.spec.containers[*].image}'
```

Pod 이미지 확인

---

## 마무리

KodeKloud Pod 문제는 처음에는 영어 문제도 헷갈리고 명령어도 낯설어서 어렵게 느껴진다.
하지만 초반 문제들은 대부분 `get`, `describe`, `run`, `delete` 네 가지 명령어 안에서 해결된다.

가장 중요한 흐름은 다음과 같다.

```text
목록 확인은 get
자세한 정보는 describe
생성은 run
삭제는 delete
상태 원인은 Events 확인
```

그리고 `<pod-name>` 같은 표기는 실제로 입력하는 게 아니라, 그 자리에 진짜 Pod 이름을 넣으라는 뜻이다.

예를 들어 문제에서 `webapp` Pod를 삭제하라고 하면 정답은 다음이다.

```bash
kubectl delete pod webapp
```

Pod 실습 초반에는 이 정도 명령어만 익숙해져도 KodeKloud 문제를 훨씬 덜 헤매고 풀 수 있다.
