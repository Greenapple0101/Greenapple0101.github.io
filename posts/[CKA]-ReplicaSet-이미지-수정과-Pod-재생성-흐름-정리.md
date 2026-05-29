---
title: "[CKA] ReplicaSet 이미지 수정과 Pod 재생성 흐름 정리"
source: "https://velog.io/@yorange50/CKA-ReplicaSet-이미지-수정과-Pod-재생성-흐름-정리"
published: "2026-05-07T01:51:53.724Z"
tags: ""
backup_date: "2026-05-29T14:52:52.774251"
---

Kubernetes를 공부하다 보면 ReplicaSet 문제에서 자주 만나는 상황이 있다.

```text id="vwjz4q"
ReplicaSet은 존재하는데,
Pod 이미지가 잘못되었다.
```

예를 들면 이런 문제다.

```text id="n7itk2"
Fix the original replica set new-replica-set to use the correct image with name as busybox.

Either delete and recreate the ReplicaSet or update the existing ReplicaSet and then delete all PODs, so new ones with the correct image will be created.
```

처음 보면 헷갈린다.

```text id="3d26pf"
ReplicaSet만 수정하면 끝 아닌가?
왜 Pod까지 삭제하라는 거지?
```

이번 글에서는 ReplicaSet과 Pod의 관계, 이미지 수정 흐름, 왜 Pod를 다시 만들어야 하는지까지 같이 정리해본다.

---

# ReplicaSet이란?

ReplicaSet은 쉽게 말하면 다음 역할을 한다.

```text id="jlwmqf"
"Pod 개수를 원하는 만큼 유지해주는 관리자"
```

예를 들어 replicas가 4라면:

```yaml id="gxnlva"
spec:
  replicas: 4
```

ReplicaSet은 항상 Pod가 4개 유지되도록 감시한다.

현재 구조를 단순하게 보면 이렇다.

```text id="m5op7g"
ReplicaSet
 ├── Pod
 ├── Pod
 ├── Pod
 └── Pod
```

Pod 하나가 죽으면 ReplicaSet이 새 Pod를 자동으로 만든다.

---

# 왜 ReplicaSet을 쓰는가?

Pod만 직접 만들면 문제가 있다.

```text id="vyjlwm"
Pod가 죽으면 끝이다.
자동 복구가 없다.
```

예를 들어:

```bash id="wstml2"
kubectl delete pod nginx
```

직접 만든 단일 Pod라면 그냥 사라진다.

하지만 ReplicaSet이 관리 중이면 다르다.

```text id="4m4ec6"
Pod 삭제
→ ReplicaSet 감지
→ 새 Pod 자동 생성
```

즉 ReplicaSet은 Kubernetes의 기본적인 Self-Healing 기능을 담당한다.

---

# 현재 ReplicaSet 확인하기

ReplicaSet 목록 확인:

```bash id="k1fuhh"
kubectl get rs
```

또는:

```bash id="ofrm3n"
kubectl get replicasets
```

출력 예시:

```bash id="2wz5mn"
NAME              DESIRED   CURRENT   READY   AGE
new-replica-set   4         4         0       10m
```

컬럼 의미:

| 컬럼      | 의미              |
| ------- | --------------- |
| DESIRED | 원하는 Pod 개수      |
| CURRENT | 현재 존재하는 Pod 개수  |
| READY   | Ready 상태 Pod 개수 |
| AGE     | 생성된 지 얼마나 지났는지  |

---

# ReplicaSet이 만든 Pod 확인하기

```bash id="0qjwbe"
kubectl get pods
```

예시:

```bash id="fru1bw"
NAME                        READY   STATUS             AGE
new-replica-set-m7ctj       0/1     ImagePullBackOff  2m
new-replica-set-qrk9x       0/1     ImagePullBackOff  2m
new-replica-set-jnnf7       0/1     ErrImagePull      2m
new-replica-set-9wlx9       0/1     ImagePullBackOff  2m
```

여기서 이름을 보면:

```text id="9xg9k6"
new-replica-set-xxxxx
```

형태다.

즉 ReplicaSet 이름 뒤에 랜덤 문자열이 붙는다.

---

# ImagePullBackOff가 뜨는 이유

ReplicaSet 문제에서 자주 보이는 상태:

```text id="mjlwmx"
ImagePullBackOff
ErrImagePull
```

이 뜻은:

```text id="umyycy"
컨테이너 이미지를 가져오지 못했다.
```

예를 들어 이미지 이름을 잘못 적으면:

```yaml id="6stbo9"
image: nginxx
```

Kubernetes는 Docker Hub에서 `nginxx` 이미지를 찾으려 한다.

하지만 존재하지 않으므로 실패한다.

```text id="e8j0ft"
ErrImagePull
→ 이미지 다운로드 실패

ImagePullBackOff
→ 재시도 중
```

---

# ReplicaSet 상세 보기

ReplicaSet 정보 확인:

```bash id="g9u4mf"
kubectl describe rs new-replica-set
```

또는:

```bash id="l4e3ml"
kubectl describe replicaset new-replica-set
```

확인 가능한 것:

| 항목           | 설명            |
| ------------ | ------------- |
| Replicas     | 원하는 Pod 개수    |
| Selector     | 어떤 Pod를 관리하는지 |
| Pod Template | 새 Pod 생성 템플릿  |
| Events       | 생성/삭제 이벤트     |

특히 중요한 건 Pod Template다.

ReplicaSet은 이 템플릿을 기반으로 새 Pod를 만든다.

---

# ReplicaSet YAML 구조 이해하기

ReplicaSet YAML 기본 구조:

```yaml id="x6h8eh"
apiVersion: apps/v1
kind: ReplicaSet

metadata:
  name: new-replica-set

spec:
  replicas: 4

  selector:
    matchLabels:
      app: myapp

  template:
    metadata:
      labels:
        app: myapp

    spec:
      containers:
        - name: busybox
          image: busybox
```

핵심은:

```yaml id="3owp71"
template:
```

부분이다.

ReplicaSet은 이 template을 복사해서 Pod를 만든다.

즉:

```text id="hvr3l1"
ReplicaSet = Pod 공장
template = Pod 설계도
```

---

# 왜 ReplicaSet 수정만 하면 안 되는가?

여기서 가장 많이 헷갈린다.

예를 들어 ReplicaSet을 이렇게 수정했다고 하자.

```yaml id="zhq7cs"
image: busybox
```

그러면 왜 기존 Pod 이미지가 자동으로 안 바뀔까?

이유는 ReplicaSet이 하는 역할 때문이다.

ReplicaSet은:

```text id="m4nml0"
"Pod 개수 유지"
```

를 담당한다.

하지만:

```text id="glt3w0"
기존 Pod 내용을 업데이트하는 역할은 아니다.
```

즉 ReplicaSet은:

```text id="wfgpsq"
현재 Pod가 살아 있는지만 본다.
```

이미 존재하는 Pod의 컨테이너 이미지를 교체하지 않는다.

그래서 흐름이 이렇게 된다.

```text id="f3l77n"
ReplicaSet 수정
→ 기존 Pod는 그대로
→ 기존 Pod 삭제
→ ReplicaSet이 새 Pod 생성
→ 새 Pod는 수정된 이미지 사용
```

---

# ReplicaSet 수정하기

ReplicaSet 직접 수정:

```bash id="zk3f75"
kubectl edit rs new-replica-set
```

또는:

```bash id="gkzqnm"
k edit rs new-replica-set
```

편집기가 열리면:

```yaml id="y2i35d"
containers:
- image: 잘못된이미지
```

이 부분을 찾는다.

예를 들어:

```yaml id="0jk4pb"
image: nginxx
```

이렇게 되어 있다면:

```yaml id="3l2w5v"
image: busybox
```

로 수정한다.

최종 형태:

```yaml id="6gdx0v"
containers:
- name: busybox
  image: busybox
```

---

# vi 편집기 저장 방법

수정 후 저장:

```text id="0clc7x"
Esc
:wq
Enter
```

vi 종료:

| 명령  | 의미       |
| --- | -------- |
| i   | 입력 모드    |
| Esc | 명령 모드    |
| :wq | 저장 후 종료  |
| :q! | 저장 없이 종료 |

---

# 기존 Pod 삭제하기

ReplicaSet 수정 후 기존 Pod를 삭제해야 한다.

현재 Pod 확인:

```bash id="j6ym0l"
kubectl get pods
```

예시:

```bash id="6vuxzw"
new-replica-set-m7ctj
new-replica-set-qrk9x
new-replica-set-jnnf7
new-replica-set-9wlx9
```

삭제:

```bash id="vhvh2z"
kubectl delete pod new-replica-set-m7ctj
```

또는 여러 개:

```bash id="e1kqkh"
kubectl delete pod new-replica-set-m7ctj new-replica-set-qrk9x
```

전체 삭제:

```bash id="1lr5ka"
kubectl delete pod --all
```

하지만 실습 초반에는 하나씩 삭제하는 게 더 안전하다.

---

# Pod 삭제 후 무슨 일이 일어나는가?

삭제 직후:

```bash id="z6e1n6"
kubectl get pods
```

잠깐 후:

```text id="mjlwmw"
새로운 이름의 Pod 생성
```

예시:

```bash id="1v1kz8"
NAME                        READY   STATUS
new-replica-set-abc12       1/1     Running
new-replica-set-def34       1/1     Running
```

ReplicaSet이 자동으로 새 Pod를 만든 것이다.

---

# 새 Pod 이미지 확인하기

새 Pod가 정말 busybox 이미지인지 확인:

```bash id="9vppj6"
kubectl describe pod <pod-name>
```

또는:

```bash id="h6t66u"
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].image}'
```

출력:

```bash id="fjlwmw"
busybox
```

이면 성공이다.

---

# ReplicaSet 삭제 후 재생성 방법

문제에서는 이런 방법도 허용한다.

```text id="0otew2"
ReplicaSet 삭제 후 다시 생성
```

기존 ReplicaSet 삭제:

```bash id="jlwmz0"
kubectl delete rs new-replica-set
```

파일 수정:

```bash id="ndjdzj"
vi /root/new-replica-set.yaml
```

image 수정:

```yaml id="uk3p8t"
image: busybox
```

저장 후:

```bash id="i84m7o"
kubectl create -f /root/new-replica-set.yaml
```

---

# ReplicaSet 삭제 시 Pod도 같이 삭제되는 이유

ReplicaSet이 관리 중인 Pod는 보통 같이 삭제된다.

이유는 ReplicaSet이 owner reference를 가지고 있기 때문이다.

구조적으로 보면:

```text id="5h6b91"
ReplicaSet
 └── Pod
```

Pod는 ReplicaSet 소유로 등록된다.

그래서 ReplicaSet 삭제 시:

```text id="bzwkz8"
ReplicaSet 삭제
→ 관리하던 Pod도 삭제
```

가 발생한다.

---

# Pod와 ReplicaSet 관계 정리

| 리소스        | 역할                 |
| ---------- | ------------------ |
| Pod        | 실제 컨테이너 실행         |
| ReplicaSet | Pod 개수 유지          |
| Deployment | ReplicaSet 업데이트 관리 |

ReplicaSet은 Pod 관리용이다.

Deployment는 ReplicaSet을 관리한다.

실무에서는 Deployment를 훨씬 많이 쓴다.

---

# 왜 실무에서는 Deployment를 더 쓰는가?

ReplicaSet만 쓰면:

```text id="h1h9ym"
이미지 수정
→ 기존 Pod 삭제 필요
```

같은 번거로움이 있다.

Deployment는 Rolling Update 기능이 있어서:

```text id="jlwmwn"
새 Pod 생성
→ 기존 Pod 순차 교체
→ 무중단 업데이트
```

를 지원한다.

즉 ReplicaSet보다 한 단계 더 높은 관리 리소스다.

---

# 자주 쓰는 ReplicaSet 명령어

## ReplicaSet 목록 보기

```bash id="8rpnv5"
kubectl get rs
```

---

## ReplicaSet 자세히 보기

```bash id="1t0c13"
kubectl describe rs new-replica-set
```

---

## ReplicaSet YAML 보기

```bash id="7z3lv4"
kubectl get rs new-replica-set -o yaml
```

---

## ReplicaSet 수정

```bash id="yjlwm2"
kubectl edit rs new-replica-set
```

---

## ReplicaSet 삭제

```bash id="6vjlwm"
kubectl delete rs new-replica-set
```

---

## Pod 목록 확인

```bash id="cjlwm3"
kubectl get pods
```

---

## Pod 삭제

```bash id="jlwmw4"
kubectl delete pod <pod-name>
```

---

## Pod 이미지 확인

```bash id="njlwm5"
kubectl describe pod <pod-name>
```

또는:

```bash id="mjlwm6"
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].image}'
```

---

# 실습 흐름 전체 정리

이번 문제의 핵심 흐름은 다음이다.

## 1. ReplicaSet 수정

```bash id="qjlwm7"
kubectl edit rs new-replica-set
```

---

## 2. image 수정

```yaml id="zjlwm8"
image: busybox
```

---

## 3. 기존 Pod 확인

```bash id="xjlwm9"
kubectl get pods
```

---

## 4. 기존 Pod 삭제

```bash id="yjlwm0"
kubectl delete pod <pod-name>
```

---

## 5. ReplicaSet이 새 Pod 생성

```text id="ajlwm1"
새 Pod 자동 생성
```

---

## 6. 새 Pod 이미지 확인

```bash id="bjlwm2"
kubectl describe pod <pod-name>
```

또는:

```bash id="cjlwm3"
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].image}'
```

---

# 핵심 개념 한 줄 정리

```text id="djlwm4"
ReplicaSet은 Pod 개수를 유지한다.
```

```text id="ejlwm5"
ReplicaSet 수정만으로 기존 Pod는 바뀌지 않는다.
```

```text id="fjlwm6"
기존 Pod를 삭제해야 새 이미지가 적용된 Pod가 다시 생성된다.
```

---

# 마무리

ReplicaSet 문제를 처음 풀 때 가장 헷갈리는 부분은 이거다.

```text id="gjlwm7"
왜 ReplicaSet 수정했는데 Pod가 안 바뀌지?
```

이유는 ReplicaSet 역할이:

```text id="hjlwm8"
"Pod 개수 유지"
```

이지,

```text id="ijjlwm9"
"Pod 업데이트"
```

가 아니기 때문이다.

그래서 실제 흐름은 항상 다음과 같다.

```text id="jjlwm0"
ReplicaSet 수정
→ 기존 Pod 삭제
→ ReplicaSet이 새 Pod 생성
→ 새 이미지 적용
```

이 흐름을 이해하면 Kubernetes의 Self-Healing 구조와 ReplicaSet의 역할이 훨씬 명확해진다.
