---
title: "[CKA] HPA 생성 문제 — 공식문서 보고 YAML로 푸는 법"
source: "https://velog.io/@yorange50/CKA-HPA-생성-문제-공식문서-보고-YAML로-푸는-법"
published: "2026-05-20T07:33:42.810Z"
tags: ""
backup_date: "2026-05-29T14:52:52.716811"
---

문제는 이거다.

```text id="ladp8e"
autoscale namespace에 HPA를 만들어라.

HPA 이름: apache-server
대상 Deployment: apache-server
namespace: autoscale

CPU 사용률 목표: 50%
minReplicas: 1
maxReplicas: 4
scaleDown stabilizationWindowSeconds: 30
```

이 문제는 `kubectl autoscale` 명령어만으로 풀기 애매하다.

왜냐면 단순 HPA는 명령어로 만들 수 있지만:

```bash id="w33syu"
kubectl autoscale deployment apache-server --cpu=50% --min=1 --max=4
```

여기에는 이 조건이 빠진다.

```yaml id="3v8t9b"
behavior:
  scaleDown:
    stabilizationWindowSeconds: 30
```

그래서 이 문제는 **공식문서에서 HPA YAML 예시를 찾아서 파일로 작성하는 방식**이 좋다.

---

# 1. 먼저 문제에서 값 뽑기

문제를 바로 YAML로 쓰려고 하지 말고, 먼저 조건을 쪼개야 한다.

| 문제 조건                         | YAML 위치                                             |
| ----------------------------- | --------------------------------------------------- |
| HPA 이름 `apache-server`        | `metadata.name`                                     |
| namespace `autoscale`         | `metadata.namespace`                                |
| 대상 Deployment `apache-server` | `spec.scaleTargetRef.name`                          |
| 대상 kind `Deployment`          | `spec.scaleTargetRef.kind`                          |
| CPU 목표 50%                    | `metrics.resource.target.averageUtilization`        |
| 최소 1개                         | `minReplicas: 1`                                    |
| 최대 4개                         | `maxReplicas: 4`                                    |
| downscale window 30초          | `behavior.scaleDown.stabilizationWindowSeconds: 30` |

이 표대로 넣으면 된다.

---

# 2. 공식문서 어디서 찾나

공식문서 검색창에 이렇게 검색한다.

```text id="3qun29"
horizontal pod autoscaler
```

또는:

```text id="b4hcdp"
hpa walkthrough
```

들어갈 문서는 보통 이거다.

```text id="i3e91x"
Documentation
  → Tasks
  → Run Applications
  → HorizontalPodAutoscaler Walkthrough
```

공식문서의 HPA Walkthrough는 HPA가 Deployment나 StatefulSet 같은 workload resource를 자동으로 스케일링하는 리소스라고 설명하고, 예제 애플리케이션에 HPA를 적용하는 과정을 보여준다. ([Kubernetes][1])

---

# 3. 문서 안에서 어떤 키워드로 찾나

문서에 들어가면 `Ctrl + F`로 이걸 찾는다.

```text id="bdkqg9"
Creating the autoscaler declaratively
```

또는 짧게:

```text id="ycgyo0"
apiVersion: autoscaling/v2
```

또는:

```text id="h0tqmb"
averageUtilization
```

공식문서 아래쪽에 “Creating the autoscaler declaratively” 섹션이 있고, 거기서 `autoscaling/v2` HPA YAML 예시를 제공한다. 그 예시는 `scaleTargetRef`, `minReplicas`, `maxReplicas`, `metrics.resource.name: cpu`, `target.type: Utilization`, `averageUtilization: 50` 구조를 보여준다. ([Kubernetes][1])

문서 예시는 대략 이런 구조다.

```yaml id="8zk3h9"
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: php-apache
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: php-apache
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
```

이걸 복사해서 문제 조건에 맞게 바꾸면 된다.

---

# 4. 그런데 `behavior`는 어디서 찾나

여기서 포인트가 하나 있다.

위 Walkthrough 예시에는 기본 HPA YAML은 있는데, `behavior.scaleDown.stabilizationWindowSeconds`가 안 나올 수 있다.

그럴 땐 공식문서에서 다시 검색한다.

```text id="j3crye"
hpa behavior stabilizationWindowSeconds
```

또는 문서 검색창에:

```text id="en6n6x"
Horizontal Pod Autoscaling behavior
```

Kubernetes HPA 문서에서는 `autoscaling/v2` HPA API에서 `behavior` 필드로 `scaleUp`과 `scaleDown` 동작을 별도로 설정할 수 있고, 안정화 윈도우를 지정해 replica 수가 짧은 시간에 흔들리는 것을 줄일 수 있다고 설명한다. ([Kubernetes][2])

즉 이 문제의 핵심 추가 조건은 이 구조다.

```yaml id="dquif1"
behavior:
  scaleDown:
    stabilizationWindowSeconds: 30
```

뜻은:

```text id="6om1li"
스케일 다운할 때 너무 바로 줄이지 말고
30초 안정화 윈도우를 적용해라
```

이다.

---

# 5. 최종 YAML

문제 조건을 반영하면 이렇게 된다.

```yaml id="8vk5wh"
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: apache-server
  namespace: autoscale
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: apache-server
  minReplicas: 1
  maxReplicas: 4
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 30
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
```

---

# 6. 실행 순서

## 1단계. 대상 Deployment 확인

먼저 HPA가 붙을 Deployment가 진짜 있는지 확인한다.

```bash id="2ss1l7"
kubectl get deployment apache-server -n autoscale
```

HPA는 혼자 일하는 리소스가 아니라, Deployment 같은 scale 가능한 workload를 대상으로 replica 수를 조절한다. 공식문서도 HPA가 workload resource를 자동으로 업데이트해 수요에 맞게 scale한다고 설명한다. ([Kubernetes][3])

---

## 2단계. YAML 파일 작성

```bash id="2s5qry"
vi hpa.yaml
```

내용:

```yaml id="91wcc6"
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: apache-server
  namespace: autoscale
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: apache-server
  minReplicas: 1
  maxReplicas: 4
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 30
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
```

---

## 3단계. dry-run으로 문법 확인

```bash id="h5aozi"
kubectl apply -f hpa.yaml --dry-run=client
```

또는 서버 검증까지 하고 싶으면:

```bash id="de8085"
kubectl apply -f hpa.yaml --dry-run=server
```

네가 올린 kubectl Quick Reference에도 `kubectl apply -f ./my-manifest.yaml`처럼 manifest 파일을 적용하는 기본 패턴이 나오고, Kubernetes manifest는 YAML 또는 JSON으로 정의할 수 있다고 정리되어 있다. 

---

## 4단계. 적용

```bash id="7otkef"
kubectl apply -f hpa.yaml
```

---

## 5단계. 확인

```bash id="sq54j4"
kubectl get hpa -n autoscale
```

또는 특정 HPA만:

```bash id="6nu40p"
kubectl get hpa apache-server -n autoscale
```

자세히:

```bash id="y8o53m"
kubectl describe hpa apache-server -n autoscale
```

공식 HPA Walkthrough에서도 HPA 생성 후 `kubectl get hpa`로 현재 상태를 확인하는 흐름이 나온다. ([Kubernetes][1])

---

# 7. CKA에서 문서 활용 루틴

시험장에서는 이렇게 하면 된다.

```text id="loq5te"
1. 문제에서 HPA 조건 추출
2. 공식문서 검색창에 horizontal pod autoscaler 검색
3. Walkthrough 문서 진입
4. Ctrl + F로 Creating the autoscaler declaratively 검색
5. autoscaling/v2 YAML 예시 복사
6. name, namespace, scaleTargetRef, min/max, averageUtilization 수정
7. behavior 조건은 hpa behavior 또는 stabilizationWindowSeconds 검색
8. behavior.scaleDown.stabilizationWindowSeconds 추가
9. kubectl apply --dry-run=client로 확인
10. kubectl apply -f로 적용
11. kubectl get hpa / describe hpa로 검증
```

---

# 8. 명령어 방식과 YAML 방식 차이

이 문제는 명령어로 일부만 만들 수 있다.

```bash id="flxy1e"
kubectl autoscale deployment apache-server \
  -n autoscale \
  --cpu=50% \
  --min=1 \
  --max=4
```

공식문서에도 `kubectl autoscale deployment php-apache --cpu=50% --min=1 --max=10`으로 HPA를 만드는 예시가 나온다. ([Kubernetes][1])

하지만 이 명령어만 쓰면:

```yaml id="3x6n1j"
behavior:
  scaleDown:
    stabilizationWindowSeconds: 30
```

를 넣기 어렵다.

그래서 이 문제는 처음부터 YAML 방식으로 가는 게 더 깔끔하다.

```text id="2lwlqk"
단순 HPA 생성
→ kubectl autoscale 가능

behavior까지 설정
→ YAML 작성이 안전
```

---

# 9. 이 YAML 읽는 법

```yaml id="m97pbv"
scaleTargetRef:
  apiVersion: apps/v1
  kind: Deployment
  name: apache-server
```

이 부분은:

```text id="djcqys"
apache-server Deployment를 대상으로 삼겠다
```

라는 뜻이다.

```yaml id="q6p0yc"
minReplicas: 1
maxReplicas: 4
```

이 부분은:

```text id="uo8cla"
최소 1개, 최대 4개까지만 늘리거나 줄이겠다
```

라는 뜻이다.

```yaml id="tnw9v9"
metrics:
- type: Resource
  resource:
    name: cpu
    target:
      type: Utilization
      averageUtilization: 50
```

이 부분은:

```text id="c0d4bo"
Pod들의 평균 CPU 사용률을 50% 근처로 맞추겠다
```

라는 뜻이다.

```yaml id="2vcqqa"
behavior:
  scaleDown:
    stabilizationWindowSeconds: 30
```

이 부분은:

```text id="cbvpgr"
스케일 다운 판단을 30초 안정화 윈도우 기준으로 하겠다
```

라는 뜻이다.

---

# 10. 실전 최종 답

```bash id="ygl95k"
cat <<EOF > hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: apache-server
  namespace: autoscale
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: apache-server
  minReplicas: 1
  maxReplicas: 4
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 30
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
EOF

kubectl apply -f hpa.yaml --dry-run=client
kubectl apply -f hpa.yaml

kubectl get hpa apache-server -n autoscale
kubectl describe hpa apache-server -n autoscale
```

---

# 마무리

이 문제의 핵심은 이거다.

```text id="qdp9jm"
HPA 기본 구조는 공식문서 Walkthrough에서 가져온다.
behavior.scaleDown.stabilizationWindowSeconds는 HPA behavior 문서에서 확인한다.
문제 조건을 metadata, scaleTargetRef, min/max, metrics, behavior에 끼워 넣는다.
```

정리하면:

```text id="yjoyoo"
문서에서 autoscaling/v2 HPA 예시 찾기
→ 이름/namespace/대상 Deployment 변경
→ min 1, max 4 변경
→ CPU averageUtilization 50 확인
→ behavior.scaleDown.stabilizationWindowSeconds 30 추가
→ apply 후 get/describe로 검증
```

이렇게 풀면 된다.

[1]: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/ "HorizontalPodAutoscaler Walkthrough | Kubernetes"
[2]: https://kubernetes.io/ko/docs/tasks/run-application/horizontal-pod-autoscale/?utm_source=chatgpt.com "Horizontal Pod Autoscaling"
[3]: https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/?utm_source=chatgpt.com "Horizontal Pod Autoscaling"
