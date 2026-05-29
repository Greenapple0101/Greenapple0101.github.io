---
title: "[Kubernetes] Deployment YAML, 처음부터 다 외워야 할까?"
source: "https://velog.io/@yorange50/Kubernetes-Deployment-YAML-처음부터-다-외워야-할까"
published: "2026-05-11T07:14:34.563Z"
tags: ""
backup_date: "2026-05-29T14:52:52.765435"
---

쿠버네티스를 공부하다 보면 이런 문제를 자주 만난다.

```bash
Create a new Deployment

Name: httpd-frontend
Replicas: 3
Image: httpd:2.4-alpine
```

처음 보면 이런 생각이 든다.

> 이 YAML을 실전에서 다 외워서 쓰나?

결론부터 말하면 **다 외우는 게 아니다.**
실무에서도 처음부터 YAML을 손으로 전부 치기보다는, `kubectl` 명령어로 기본 뼈대를 만들고 수정하는 방식이 많이 쓰인다.

---

## 1. 명령어로 Deployment 바로 만들기

가장 빠른 방법은 이거다.

```bash
kubectl create deployment httpd-frontend \
  --image=httpd:2.4-alpine \
  --replicas=3
```

의미는 단순하다.

```text
httpd-frontend 라는 Deployment를 만들고
이미지는 httpd:2.4-alpine을 쓰고
Pod는 3개 띄워라
```

확인은 이렇게 한다.

```bash
kubectl get deployments
kubectl get pods
```

---

## 2. 그런데 실무에서는 YAML이 필요하다

명령어로 바로 만드는 건 빠르지만, 실무에서는 보통 YAML 파일로 관리한다.

왜냐하면 YAML 파일은:

```text
Git에 저장 가능
변경 이력 추적 가능
리뷰 가능
재사용 가능
환경별 관리 가능
```

하기 때문이다.

그래서 실무에서는 보통 이런 흐름을 쓴다.

```text
kubectl 명령어로 YAML 뼈대 생성
→ 필요한 부분 수정
→ kubectl apply로 반영
```

---

## 3. YAML 뼈대 자동 생성하기

처음부터 YAML을 다 외우지 말고 이렇게 만든다.

```bash
kubectl create deployment httpd-frontend \
  --image=httpd:2.4-alpine \
  --dry-run=client -o yaml
```

여기서 중요한 옵션은 두 개다.

```text
--dry-run=client
실제로 만들지는 않고 결과만 미리 보여줌

-o yaml
출력을 YAML 형식으로 보여줌
```

파일로 저장하려면 이렇게 한다.

```bash
kubectl create deployment httpd-frontend \
  --image=httpd:2.4-alpine \
  --dry-run=client -o yaml > deployment.yaml
```

---

## 4. replicas 수정하기

자동 생성된 YAML에는 기본적으로 replicas가 없거나 1로 되어 있을 수 있다.

그럼 `spec` 아래에 추가하면 된다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: httpd-frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: httpd-frontend
  template:
    metadata:
      labels:
        app: httpd-frontend
    spec:
      containers:
      - name: httpd
        image: httpd:2.4-alpine
```

여기서 핵심 구조는 이거다.

```text
Deployment
└── spec
    ├── replicas: 3
    ├── selector
    └── template
        └── Pod 설정
            └── container image
```

Deployment는 결국 **Pod를 직접 만드는 게 아니라, Pod 템플릿을 관리하는 객체**다.

---

## 5. YAML 적용하기

파일을 만들었으면 적용한다.

```bash
kubectl apply -f deployment.yaml
```

확인:

```bash
kubectl get deploy
kubectl get pods
```

상세 확인:

```bash
kubectl describe deployment httpd-frontend
```

---

## 6. 헷갈릴 때는 kubectl explain

YAML 구조가 헷갈리면 공식 문서를 매번 검색해도 되지만, 터미널에서도 바로 확인할 수 있다.

```bash
kubectl explain deployment
```

더 깊게 들어가면:

```bash
kubectl explain deployment.spec
kubectl explain deployment.spec.replicas
kubectl explain deployment.spec.template
kubectl explain deployment.spec.template.spec.containers
```

예를 들어 `replicas`가 어디 들어가는지 헷갈리면:

```bash
kubectl explain deployment.spec.replicas
```

이렇게 확인하면 된다.

---

## 7. create, apply, set image 차이

쿠버네티스에서 자주 쓰는 명령어는 이렇게 구분하면 된다.

| 명령어                 | 의미                    |
| ------------------- | --------------------- |
| `kubectl create`    | 새 리소스 생성              |
| `kubectl apply -f`  | YAML 파일 내용 반영         |
| `kubectl set image` | 기존 Deployment의 이미지 변경 |
| `kubectl delete`    | 리소스 삭제                |
| `kubectl describe`  | 리소스 상세 상태 확인          |

이미지만 빠르게 바꾸고 싶으면:

```bash
kubectl set image deployment/httpd-frontend httpd=httpd:2.4-alpine
```

YAML을 수정했다면:

```bash
kubectl apply -f deployment.yaml
```

---

## 8. 결론

쿠버네티스 YAML은 처음부터 다 외우는 것이 아니다.

실전 흐름은 보통 이렇다.

```text
1. kubectl create --dry-run=client -o yaml 로 기본 YAML 생성
2. 필요한 값 수정
3. kubectl apply -f 로 반영
4. kubectl get / describe / logs 로 확인
```

즉, 중요한 건 YAML을 통째로 암기하는 게 아니라,

```text
Deployment가 Pod 템플릿을 관리한다
replicas는 spec 아래에 둔다
image는 template.spec.containers 아래에 둔다
selector와 labels는 맞아야 한다
```

이 구조를 이해하는 것이다.

쿠버네티스는 암기 과목이라기보다,
**명령어로 뼈대를 만들고 구조를 읽으면서 고치는 도구**에 가깝다.
