---
title: "[Kubernetes] `--dry-run=client` 도대체 뭐 하는 옵션일까?"
source: "https://velog.io/@yorange50/Kubernetes-dry-runclient-도대체-뭐-하는-옵션일까"
published: "2026-05-20T01:31:02.564Z"
tags: ""
backup_date: "2026-05-29T14:52:52.720135"
---

쿠버네티스를 공부하다 보면 이런 명령어를 자주 보게 된다.

```bash
kubectl run nginx --image=nginx --dry-run=client -o yaml
```

혹은

```bash
kubectl create deployment myapp --image=nginx --dry-run=client -o yaml
```

처음 보면:

* 왜 실행 안 하고 dry-run을 하지?
* client는 또 뭐고 server는 뭐지?
* 왜 yaml 생성할 때 항상 붙어있지?

같은 생각이 든다.

근데 이 옵션은 CKA에서도 엄청 중요하고,
실무에서도 “매니페스트 초안 생성기”처럼 정말 많이 쓴다.

오늘은 `--dry-run=client`가 정확히 뭔지,
왜 쓰는지,
언제 쓰는지 정리해본다.

---

# 1. dry-run이란?

말 그대로:

> “실제로 적용은 하지 않고 시뮬레이션만 해보는 것”

이다.

예를 들어:

```bash
kubectl run nginx --image=nginx
```

를 실행하면 실제로 Pod가 생성된다.

하지만:

```bash
kubectl run nginx --image=nginx --dry-run=client
```

를 실행하면?

→ 생성은 안 함
→ 대신 “이렇게 생성될 예정이었다”만 보여줌

즉:

```text
실행은 안 하지만
명령어 검증 + 결과 미리보기
```

를 하는 옵션이다.

---

# 2. 왜 이름이 dry-run일까?

원래 프로그래밍/배포 세계에서 dry-run은:

```text
"진짜 실행 전에 테스트로 한번 돌려봄"
```

이라는 의미로 많이 사용된다.

예시:

* Terraform plan
* Jenkins 테스트 배포
* SQL 실행 계획
* Docker compose config

이런 것들도 비슷한 개념이다.

쿠버네티스에서도:

```text
"실제로 클러스터에 적용하지 않고 미리 확인"
```

하는 기능으로 들어간 것이다.

---

# 3. `client`는 무슨 뜻일까?

여기서 client는:

```text
kubectl 실행 중인 내 컴퓨터(Mac, 서버 등)
```

를 의미한다.

즉:

```bash
--dry-run=client
```

는:

```text
API Server까지 요청 보내지 말고
kubectl 클라이언트 내부에서만 검증해라
```

라는 뜻이다.

흐름으로 보면:

---

## 일반 실행

```text
kubectl
   ↓
API Server
   ↓
etcd 저장
   ↓
리소스 생성
```

---

## dry-run=client

```text
kubectl 내부에서만 처리
(클러스터로 안 감)
```

즉 실제 리소스 생성이 안 된다.

---

# 4. 가장 많이 쓰는 이유: YAML 자동 생성

사실 이 옵션의 핵심은 이거다.

쿠버네티스 YAML 직접 쓰다 보면 너무 귀찮다.

예를 들어 Pod 하나만 만들어도:

```yaml
apiVersion:
kind:
metadata:
spec:
containers:
```

등을 다 써야 한다.

그래서 많이 하는 방식이:

```bash
kubectl run nginx \
  --image=nginx \
  --dry-run=client \
  -o yaml
```

이다.

그러면 kubectl이 자동으로 YAML 초안을 만들어준다.

출력 예시:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - image: nginx
    name: nginx
```

이걸 파일로 저장해서 수정하면 된다.

---

# 5. 그래서 CKA에서 엄청 많이 씀

CKA에서는 시간 절약이 중요하다.

직접 YAML 치면 느리다.

그래서 보통:

```bash
kubectl create deployment web \
  --image=nginx \
  --dry-run=client \
  -o yaml > deploy.yaml
```

처럼 초안을 만든 뒤 수정한다.

실무에서도 똑같다.

특히:

* Deployment
* Service
* ConfigMap
* Secret
* Job
* CronJob

같은 것들 만들 때 많이 사용한다.

---

# 6. `-o yaml`은 왜 같이 쓰나?

`-o`는 output format이다.

즉:

```bash
-o yaml
```

는:

```text
결과를 YAML 형식으로 출력해라
```

라는 의미다.

같이 붙는 이유:

```bash
--dry-run=client -o yaml
```

조합이:

```text
"실제 생성은 하지 말고
생성될 YAML만 보여줘"
```

가 되기 때문이다.

거의 세트처럼 사용된다.

---

# 7. 실무 느낌으로 보면

실무에서는 이런 흐름이 많다.

---

## 1단계

초안 생성

```bash
kubectl create deployment api \
  --image=myapp:v1 \
  --dry-run=client \
  -o yaml > deploy.yaml
```

---

## 2단계

yaml 수정

```yaml
replicas:
resources:
env:
livenessProbe:
```

같은 거 추가

---

## 3단계

적용

```bash
kubectl apply -f deploy.yaml
```

---

즉:

```text
dry-run=client는
yaml 생성기처럼 많이 사용된다
```

라고 이해하면 된다.

---

# 8. `client`와 `server` 차이

가끔 이런 것도 보인다.

```bash
--dry-run=server
```

차이는:

---

## client

```text
kubectl 내부에서만 검사
클러스터와 통신 안 함
```

빠름

---

## server

```text
실제로 API Server까지 요청 보내서 검증
하지만 저장은 안 함
```

즉:

* admission controller
* 실제 스키마
* 서버 validation

까지 검사 가능하다.

실무에서는 server도 꽤 유용하다.

---

# 9. 가장 많이 쓰는 패턴들

## Pod YAML 생성

```bash
kubectl run nginx \
  --image=nginx \
  --dry-run=client \
  -o yaml
```

---

## Deployment YAML 생성

```bash
kubectl create deployment web \
  --image=nginx \
  --dry-run=client \
  -o yaml
```

---

## Service YAML 생성

```bash
kubectl expose deployment web \
  --port=80 \
  --target-port=8080 \
  --dry-run=client \
  -o yaml
```

---

## 파일 저장

```bash
kubectl create deployment web \
  --image=nginx \
  --dry-run=client \
  -o yaml > deploy.yaml
```

---

# 마무리

`--dry-run=client`는 단순한 옵션이 아니다.

쿠버네티스를:

```text
CLI → YAML → apply
```

흐름으로 다루게 만들어주는 핵심 옵션이다.

특히 CKA에서는 거의 필수 수준이다.

핵심만 기억하면:

```text
--dry-run=client
=
실제 생성은 하지 않고
kubectl 내부에서만 결과를 미리 생성/검증
```

그리고 대부분:

```bash
-o yaml
```

과 함께 사용해서
YAML 초안을 자동 생성하는 용도로 사용한다.
