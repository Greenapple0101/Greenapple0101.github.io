---
title: "[Kubernetes] 일부러 잘못된 이미지로 Pod 만들기: redis123 실습 이해하기"
source: "https://velog.io/@yorange50/Kubernetes-일부러-잘못된-이미지로-Pod-만들기-redis123-실습-이해하기"
published: "2026-05-12T09:54:19.678Z"
tags: ""
backup_date: "2026-05-29T14:52:52.754855"
---

쿠버네티스 실습을 하다 보면 이런 문제가 나온다.

```text
Create a new pod with the name redis and the image redis123.

Utilize a pod-definition YAML file.
Please note that the image name redis123 is intentionally incorrect.
Do NOT correct the image at this stage;
you will address this in the subsequent task.
```

처음 보면 조금 이상하다.

`redis` 이미지를 쓰면 될 것 같은데, 문제에서는 굳이 `redis123`이라는 잘못된 이미지를 쓰라고 한다.

여기서 중요한 포인트는 이것이다.

```text
이미지가 잘못된 걸 알고 있어도, 지금 단계에서는 고치면 안 된다.
```

왜냐하면 이 문제의 목적은 단순히 Redis Pod를 정상 실행하는 것이 아니라, **YAML 파일로 Pod를 만들고, 잘못된 이미지 때문에 Pod가 어떤 상태가 되는지 확인하는 것**이기 때문이다.

---

# 1. 문제 해석

요구사항은 세 가지다.

```text
1. Pod 이름은 redis
2. 이미지 이름은 redis123
3. YAML 파일을 사용해서 Pod 생성
```

여기서 `redis123`은 실제 Redis 이미지가 아니다.

정상적인 Redis 이미지는 보통 다음처럼 쓴다.

```text
redis
```

하지만 이번 문제에서는 일부러 틀린 이미지를 써야 한다.

```text
redis123
```

즉, 우리가 만들어야 하는 Pod는 정상 실행되는 Pod가 아니라, **이미지 pull 단계에서 실패하는 Pod**다.

---

# 2. Pod란 무엇인가?

쿠버네티스에서 Pod는 가장 작은 배포 단위다.

컨테이너를 직접 실행하는 것이 아니라, 쿠버네티스는 컨테이너를 Pod 안에 넣어서 실행한다.

간단히 말하면 이렇다.

```text
Pod = 컨테이너를 담는 최소 실행 단위
```

보통 하나의 Pod 안에는 하나의 컨테이너가 들어간다.

이번 실습에서는 다음 구조가 된다.

```text
Pod 이름: redis
컨테이너 이름: redis
사용 이미지: redis123
```

그림처럼 생각하면 이렇다.

```text
Kubernetes Cluster
└── Pod: redis
    └── Container: redis
        └── Image: redis123
```

---

# 3. YAML 파일을 왜 사용할까?

Pod를 만들 때 명령어 한 줄로도 만들 수 있다.

```bash
kubectl run redis --image=redis123
```

하지만 문제에서는 YAML 파일을 사용하라고 했다.

YAML 파일을 사용하는 이유는 쿠버네티스 리소스의 원하는 상태를 파일로 선언하기 위해서다.

쿠버네티스는 명령형 방식과 선언형 방식이 있다.

## 명령형 방식

```bash
kubectl run redis --image=redis123
```

이 방식은 명령어로 바로 실행하는 방식이다.

빠르지만, 설정이 파일로 남지 않는다.

## 선언형 방식

```bash
kubectl create -f pod-definition.yaml
```

이 방식은 YAML 파일에 원하는 상태를 적어두고, 쿠버네티스에게 적용하는 방식이다.

실무에서는 보통 YAML 파일을 많이 쓴다.

왜냐하면 설정을 파일로 남길 수 있고, Git으로 관리할 수 있기 때문이다.

---

# 4. pod-definition.yaml 작성하기

먼저 YAML 파일을 만든다.

```bash
vi pod-definition.yaml
```

내용은 다음과 같다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: redis
spec:
  containers:
    - name: redis
      image: redis123
```

이제 이 YAML 파일이 무슨 뜻인지 하나씩 보자.

---

# 5. YAML 구조 이해하기

## apiVersion

```yaml
apiVersion: v1
```

`apiVersion`은 이 리소스를 어떤 Kubernetes API 버전으로 만들 것인지를 뜻한다.

Pod는 기본 리소스이기 때문에 `v1`을 사용한다.

예를 들어 Deployment는 보통 이렇게 쓴다.

```yaml
apiVersion: apps/v1
```

하지만 Pod는 다음처럼 쓴다.

```yaml
apiVersion: v1
```

---

## kind

```yaml
kind: Pod
```

`kind`는 어떤 종류의 리소스를 만들 것인지 나타낸다.

이번에는 Pod를 만들 것이므로 다음처럼 쓴다.

```yaml
kind: Pod
```

쿠버네티스에는 여러 kind가 있다.

```text
Pod
Deployment
Service
ConfigMap
Secret
Namespace
```

즉, `kind: Pod`는 쿠버네티스에게 이렇게 말하는 것이다.

```text
나는 Pod 리소스를 만들고 싶다.
```

---

## metadata

```yaml
metadata:
  name: redis
```

`metadata`는 리소스의 이름, 라벨, 어노테이션 같은 정보를 적는 영역이다.

이번 문제에서는 Pod 이름이 `redis`여야 하므로 다음처럼 쓴다.

```yaml
metadata:
  name: redis
```

이렇게 하면 생성되는 Pod 이름은 `redis`가 된다.

확인할 때도 이 이름으로 보인다.

```bash
kubectl get pods
```

예상 출력:

```text
NAME    READY   STATUS   RESTARTS   AGE
redis   0/1     ...
```

---

## spec

```yaml
spec:
  containers:
    - name: redis
      image: redis123
```

`spec`은 이 리소스가 어떤 상태가 되기를 원하는지 적는 부분이다.

쿠버네티스에서는 이걸 자주 **desired state**, 즉 원하는 상태라고 부른다.

이번 Pod의 원하는 상태는 이렇다.

```text
redis라는 이름의 컨테이너를 하나 실행하고,
그 컨테이너는 redis123 이미지를 사용한다.
```

그래서 다음처럼 작성한다.

```yaml
spec:
  containers:
    - name: redis
      image: redis123
```

---

# 6. containers 부분 이해하기

Pod 안에는 하나 이상의 컨테이너가 들어갈 수 있다.

그래서 `containers`는 리스트 형태다.

YAML에서 리스트는 `-`로 표현한다.

```yaml
containers:
  - name: redis
    image: redis123
```

여기서 중요한 항목은 두 가지다.

```text
name
image
```

---

## name

```yaml
name: redis
```

이건 컨테이너 이름이다.

Pod 이름이 아니다.

이번 YAML에서는 Pod 이름도 `redis`이고, 컨테이너 이름도 `redis`다.

```yaml
metadata:
  name: redis
```

```yaml
containers:
  - name: redis
```

둘 다 같은 이름으로 썼지만 의미는 다르다.

정리하면 이렇다.

| 위치                  | 의미      |
| ------------------- | ------- |
| `metadata.name`     | Pod 이름  |
| `containers[].name` | 컨테이너 이름 |

즉, 이 YAML에서는 다음과 같다.

```text
Pod 이름: redis
컨테이너 이름: redis
```

---

## image

```yaml
image: redis123
```

이건 컨테이너를 실행할 때 사용할 이미지 이름이다.

쿠버네티스는 Pod를 만들 때 이 이미지를 container runtime에게 가져오라고 한다.

보통 Docker Hub에서 이미지를 찾는다.

이미지가 정상이라면 이런 흐름으로 진행된다.

```text
Pod 생성 요청
→ kube-scheduler가 노드 선택
→ 해당 노드의 kubelet이 Pod 실행 준비
→ container runtime이 이미지 pull
→ 컨테이너 실행
→ Pod Running
```

하지만 이번 이미지는 `redis123`이다.

이 이미지는 일부러 잘못된 이미지다.

그래서 이미지 pull 단계에서 실패한다.

---

# 7. Pod 생성하기

YAML 파일을 작성했다면 이제 Pod를 생성한다.

```bash
kubectl create -f pod-definition.yaml
```

또는 다음 명령어를 써도 된다.

```bash
kubectl apply -f pod-definition.yaml
```

CKA 실습에서는 둘 다 자주 쓰지만, 새로 만드는 상황이면 `create`를 써도 된다.

---

# 8. create와 apply 차이

간단하게 차이를 보면 이렇다.

## kubectl create

```bash
kubectl create -f pod-definition.yaml
```

새 리소스를 생성한다.

이미 같은 이름의 리소스가 있으면 에러가 난다.

```text
Error from server (AlreadyExists): pods "redis" already exists
```

## kubectl apply

```bash
kubectl apply -f pod-definition.yaml
```

YAML 파일에 적힌 상태를 클러스터에 적용한다.

리소스가 없으면 만들고, 있으면 변경 사항을 반영한다.

실무에서는 보통 `apply`를 많이 쓴다.

하지만 시험 문제에서 “create a new pod”라고 되어 있으면 `create -f`를 써도 괜찮다.

---

# 9. Pod 상태 확인하기

Pod를 만든 뒤 확인한다.

```bash
kubectl get pods
```

그러면 정상 Running이 아니라 이런 상태가 나올 수 있다.

```text
NAME    READY   STATUS             RESTARTS   AGE
redis   0/1     ErrImagePull       0          10s
```

조금 시간이 지나면 이렇게 바뀔 수 있다.

```text
NAME    READY   STATUS             RESTARTS   AGE
redis   0/1     ImagePullBackOff   0          1m
```

여기서 당황하면 안 된다.

이 문제에서는 이 상태가 정상이다.

왜냐하면 이미지 이름 `redis123`이 일부러 잘못되었기 때문이다.

---

# 10. ErrImagePull이란?

`ErrImagePull`은 컨테이너 이미지를 가져오는 데 실패했다는 뜻이다.

```text
ErrImagePull = 이미지 pull 실패
```

쿠버네티스는 Pod를 만들 때 먼저 이미지를 가져와야 한다.

그런데 `redis123`이라는 이미지를 찾지 못하면 컨테이너를 실행할 수 없다.

그래서 상태가 `ErrImagePull`이 된다.

---

# 11. ImagePullBackOff란?

처음에는 `ErrImagePull`이 뜨고, 시간이 지나면 `ImagePullBackOff`로 바뀔 수 있다.

```text
ImagePullBackOff
```

이건 쿠버네티스가 이미지를 계속 가져오려고 시도했지만 실패해서, 잠시 기다렸다가 다시 시도하는 상태다.

쉽게 말하면 이렇다.

```text
이미지 가져오기 실패
→ 바로 계속 재시도하면 부담이 큼
→ 잠깐 쉬었다가 다시 시도
→ ImagePullBackOff
```

즉, `ImagePullBackOff`는 이미지 pull 실패 후 재시도 대기 상태라고 보면 된다.

---

# 12. describe로 원인 확인하기

Pod 상태가 이상하면 `describe`를 본다.

```bash
kubectl describe pod redis
```

여기서 중요한 부분은 아래쪽 `Events`다.

예상되는 메시지는 이런 식이다.

```text
Events:
  Type     Reason     Age   From               Message
  ----     ------     ----  ----               -------
  Normal   Pulling    10s   kubelet            Pulling image "redis123"
  Warning  Failed     8s    kubelet            Failed to pull image "redis123"
  Warning  Failed     8s    kubelet            Error: ErrImagePull
  Normal   BackOff    5s    kubelet            Back-off pulling image "redis123"
  Warning  Failed     5s    kubelet            Error: ImagePullBackOff
```

여기서 보면 쿠버네티스가 정확히 무엇을 하다가 실패했는지 나온다.

```text
Pulling image "redis123"
Failed to pull image "redis123"
Error: ErrImagePull
Back-off pulling image "redis123"
Error: ImagePullBackOff
```

즉, 이 Pod가 안 뜨는 이유는 스케줄링 문제가 아니라 이미지 문제다.

---

# 13. 이 실습의 핵심 원리

이 문제의 핵심은 Pod가 생성되는 전체 흐름을 이해하는 것이다.

YAML을 적용하면 쿠버네티스는 바로 컨테이너를 실행하는 것이 아니다.

대략 이런 흐름으로 진행된다.

```text
1. 사용자가 YAML 파일 작성
2. kubectl create -f 실행
3. API Server에 Pod 생성 요청 전달
4. etcd에 원하는 상태 저장
5. scheduler가 Pod를 실행할 노드 선택
6. 해당 노드의 kubelet이 Pod 실행 시도
7. container runtime이 redis123 이미지 pull 시도
8. 이미지가 없어서 pull 실패
9. Pod 상태가 ErrImagePull 또는 ImagePullBackOff가 됨
```

중요한 점은 이것이다.

```text
Pod 리소스 생성은 성공할 수 있다.
하지만 컨테이너 실행은 실패할 수 있다.
```

즉, `kubectl create` 명령어가 성공했다고 해서 애플리케이션이 정상 실행된다는 뜻은 아니다.

---

# 14. 왜 문제에서 이미지를 고치지 말라고 했을까?

이 문제는 다음 단계와 이어지는 경우가 많다.

예를 들어 다음 문제에서 이런 요구가 나올 수 있다.

```text
Now change the image from redis123 to redis.
```

즉, 첫 번째 문제에서는 일부러 잘못된 이미지로 Pod를 만들고, 두 번째 문제에서 그 문제를 수정하는 흐름이다.

그래서 첫 번째 단계에서 `redis123`을 `redis`로 고쳐버리면 문제 의도와 달라진다.

CKA에서는 문제 요구사항을 그대로 따르는 것이 중요하다.

```text
잘못된 걸 알아도,
문제에서 고치지 말라고 하면 고치지 않는다.
```

---

# 15. 최종 YAML

이번 문제의 정답 YAML은 다음과 같다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: redis
spec:
  containers:
    - name: redis
      image: redis123
```

파일명은 보통 이렇게 둔다.

```text
pod-definition.yaml
```

---

# 16. 실행 명령어 정리

파일 생성:

```bash
vi pod-definition.yaml
```

YAML 작성:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: redis
spec:
  containers:
    - name: redis
      image: redis123
```

Pod 생성:

```bash
kubectl create -f pod-definition.yaml
```

Pod 확인:

```bash
kubectl get pods
```

상세 확인:

```bash
kubectl describe pod redis
```

---

# 17. 상태 해석 정리

| 상태                  | 의미                   |
| ------------------- | -------------------- |
| `Pending`           | Pod가 아직 실행 준비 중      |
| `ContainerCreating` | 컨테이너 생성 중            |
| `ErrImagePull`      | 이미지 pull 실패          |
| `ImagePullBackOff`  | 이미지 pull 실패 후 재시도 대기 |
| `Running`           | 정상 실행 중              |

이번 실습에서는 `Running`이 아니라 다음 상태가 나와도 정상이다.

```text
ErrImagePull
ImagePullBackOff
```

왜냐하면 `redis123`은 일부러 잘못된 이미지이기 때문이다.

---

# 18. 한 줄 요약

이번 문제는 Redis를 정상 실행하는 문제가 아니다.

핵심은 이것이다.

```text
YAML 파일로 Pod를 만들고,
일부러 잘못된 이미지 redis123 때문에
Pod가 ErrImagePull 또는 ImagePullBackOff 상태가 되는 것을 확인하는 문제
```

정리하면 흐름은 다음과 같다.

```text
YAML 작성
→ kubectl create -f 실행
→ Pod 리소스 생성
→ kubelet이 이미지 pull 시도
→ redis123 이미지 pull 실패
→ ErrImagePull / ImagePullBackOff 발생
```

그래서 이 문제에서는 절대 `redis123`을 `redis`로 고치면 안 된다.

다음 수정 문제에서 고치는 것이 맞다.
