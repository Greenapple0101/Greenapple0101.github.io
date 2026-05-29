---
title: "[Kubernetes] ReplicaSet 생성 중 no matches for kind \"ReplicaSet\" in version \"v1\" 에러 해결 + 공식 Docs 보는 법"
source: "https://velog.io/@yorange50/Kubernetes-ReplicaSet-생성-중-no-matches-for-kind-ReplicaSet-in-version-v1-에러-해결-공식-Docs-보는-법"
published: "2026-05-11T03:51:00.227Z"
tags: ""
backup_date: "2026-05-29T14:52:52.766422"
---

쿠버네티스 실습을 하다 보면 가장 많이 마주치는 것 중 하나가 YAML 오류다.

특히 CKA/KodeKloud에서는 일부러 틀린 YAML 파일을 주고 수정하게 만드는 문제가 굉장히 자주 나온다.

이번에는 ReplicaSet 생성 중 발생한 에러를 해결하면서:

* ReplicaSet 개념
* YAML 구조
* apiVersion 의미
* kubectl explain 사용법
* 공식 Kubernetes Docs 보는 방법

까지 한 번에 정리해보자.

---

# 문제 상황

문제:

```text
Create a ReplicaSet using the replicaset-definition-1.yaml file located at /root/.

There is an issue with the file, so try to fix it.
```

파일 생성 시도:

```bash
k create -f /root/replicaset-definition-1.yaml
```

에러 발생:

```text
error: resource mapping not found for name: "replicaset-1"
namespace: "" from "/root/replicaset-definition-1.yaml":
no matches for kind "ReplicaSet" in version "v1"
```

---

# 에러 해석

핵심은 이 부분이다.

```text
no matches for kind "ReplicaSet" in version "v1"
```

즉:

```text
ReplicaSet은 v1 버전이 아닌데
YAML에서 v1으로 작성했다
```

라는 뜻이다.

---

# 원인 확인

파일 열기:

```bash
vi /root/replicaset-definition-1.yaml
```

문제 YAML:

```yaml
apiVersion: v1
kind: ReplicaSet
```

여기서 잘못된 부분은:

```yaml
apiVersion: v1
```

이다.

---

# 왜 틀렸을까?

쿠버네티스 리소스마다 사용하는 API 그룹이 다르다.

예를 들면:

| 리소스        | apiVersion |
| ---------- | ---------- |
| Pod        | v1         |
| Service    | v1         |
| ConfigMap  | v1         |
| ReplicaSet | apps/v1    |
| Deployment | apps/v1    |

즉 ReplicaSet은:

```yaml
apiVersion: apps/v1
```

를 사용해야 한다.

---

# 수정 방법

수정 후:

```yaml
apiVersion: apps/v1
kind: ReplicaSet
```

저장 후 다시 생성:

```bash
k create -f /root/replicaset-definition-1.yaml
```

확인:

```bash
k get rs
```

예상 출력:

```text
NAME             DESIRED   CURRENT   READY
replicaset-1     3         3         3
```

Pod 확인:

```bash
k get pods
```

---

# ReplicaSet이란?

ReplicaSet은:

```text
지정한 개수만큼 Pod를 유지하는 컨트롤러
```

이다.

예를 들어 replicas: 3 이면:

* Pod 하나 죽음
* ReplicaSet이 자동으로 새 Pod 생성

즉 “복제 개수 유지 관리자” 같은 느낌이다.

---

# ReplicaSet YAML 구조 이해하기

대표 구조:

```yaml
apiVersion: apps/v1
kind: ReplicaSet

metadata:
  name: myapp-replicaset

spec:
  replicas: 3

  selector:
    matchLabels:
      app: myapp

  template:
    metadata:
      labels:
        app: myapp

    spec:
      containers:
      - name: nginx
        image: nginx
```

---

# 가장 중요한 부분: selector 와 labels

여기 진짜 중요하다.

```yaml
selector:
  matchLabels:
    app: myapp
```

ReplicaSet이 관리할 Pod를 찾는 조건이다.

그리고:

```yaml
template:
  metadata:
    labels:
      app: myapp
```

생성할 Pod의 label이다.

즉:

```text
selector.matchLabels
==
template.metadata.labels
```

이 둘이 반드시 일치해야 한다.

안 맞으면 ReplicaSet이 Pod를 인식하지 못한다.

---

# 공식 Docs로 해결하는 방법

CKA에서 중요한 건 암기가 아니다.

```text
공식 문서를 얼마나 빨리 찾아서 적용하느냐
```

이다.

ReplicaSet 문제면 검색:

```text
kubernetes replicaset
```

공식 문서:
[Kubernetes ReplicaSet Documentation](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/?utm_source=chatgpt.com)

들어가면 바로 예제 YAML이 나온다.

실전에서는:

* 예제 복붙
* 필요한 부분 수정

이 흐름으로 많이 푼다.

---

# kubectl explain 사용법

웹 Docs 말고 CLI에서도 구조 탐색 가능하다.

ReplicaSet 전체 구조 보기:

```bash
k explain rs
```

spec 보기:

```bash
k explain rs.spec
```

template 보기:

```bash
k explain rs.spec.template
```

replicas 필드 보기:

```bash
k explain rs.spec.replicas
```

출력 예시:

```text
FIELD: replicas <integer>

Number of desired pods.
```

즉:

```text
YAML 구조를 터미널 안에서 탐색 가능
```

하다.

이거 CKA에서 엄청 중요하다.

---

# 실무에서도 docs를 보는 이유

쿠버네티스는:

* YAML 필드 많음
* apiVersion 계속 바뀜
* 리소스 구조 깊음
* indentation 민감함

그래서 실무에서도 전부 암기 안 한다.

대부분:

* 공식 docs
* kubectl explain
* 기존 YAML 참고

이걸 조합해서 작업한다.

---

# CKA 스타일로 빠르게 푸는 흐름

문제 확인

```bash
k create -f file.yaml
```

에러 발생

```text
no matches for kind ...
```

파일 열기

```bash
vi file.yaml
```

공식 docs 참고

* apiVersion 확인
* selector 확인
* labels 확인

수정 후 재적용

```bash
k create -f file.yaml
```

검증

```bash
k get rs
k get pods
```

---

# 핵심 정리

* ReplicaSet은 `apps/v1`
* `selector.matchLabels` 와 `template.metadata.labels` 는 반드시 일치
* YAML 오류는 CKA에서 매우 자주 나옴
* 쿠버네티스는 “암기 시험”보다 “문서 탐색 시험”에 가까움
* 공식 Docs + `kubectl explain` 사용 습관이 중요
* 실무에서도 대부분 Docs 참고하면서 작업함
