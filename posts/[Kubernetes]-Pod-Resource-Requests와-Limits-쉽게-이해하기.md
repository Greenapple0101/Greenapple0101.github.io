---
title: "[Kubernetes] Pod Resource Requests와 Limits 쉽게 이해하기"
source: "https://velog.io/@yorange50/Kubernetes-Pod-Resource-Requests와-Limits-쉽게-이해하기"
published: "2026-05-27T15:25:39.035Z"
tags: ""
backup_date: "2026-05-29T14:52:52.711881"
---

쿠버네티스에서 Pod를 만들 때 컨테이너가 사용할 CPU, Memory를 지정할 수 있다.

이때 나오는 개념이 두 개다.

```text
requests
limits
```

처음 보면 둘 다 “리소스 설정”이라 헷갈리는데, 역할이 다르다.

---

## 1. Requests란?

`requests`는 **이 Pod를 실행하기 위해 최소한 이 정도 리소스는 필요하다**고 쿠버네티스에게 알려주는 값이다.

쉽게 말하면:

```text
나 이 정도는 최소로 필요해.
이 정도 줄 수 있는 노드에 배치해줘.
```

예를 들어 이런 Pod가 있다고 하자.

```yaml
resources:
  requests:
    cpu: "500m"
    memory: "256Mi"
```

이 뜻은:

```text
CPU 최소 0.5개 필요
메모리 최소 256Mi 필요
```

쿠버네티스 Scheduler는 이 값을 보고 어느 노드에 Pod를 올릴지 결정한다.

예를 들어 노드에 남은 CPU가 `300m`밖에 없으면, 이 Pod는 거기에 스케줄링되지 않는다.

```text
Pod 요청 CPU: 500m
노드 남은 CPU: 300m

→ 부족함
→ 이 노드에는 배치 안 함
```

즉, `requests`는 **스케줄링 기준**이다.

---

## 2. Limits란?

`limits`는 **이 Pod가 사용할 수 있는 최대 리소스 양**이다.

쉽게 말하면:

```text
너 여기까지만 써.
그 이상은 안 돼.
```

예시는 이렇게 쓴다.

```yaml
resources:
  limits:
    cpu: "1"
    memory: "512Mi"
```

이 뜻은:

```text
CPU는 최대 1개까지 사용 가능
Memory는 최대 512Mi까지 사용 가능
```

여기서 CPU와 Memory의 동작이 조금 다르다.

---

## 3. CPU limit을 넘으면?

CPU limit을 넘는다고 Pod가 바로 죽지는 않는다.

대신 CPU 사용량이 제한된다.

```text
CPU limit 초과
→ 속도 제한 걸림
→ 느려짐
→ 하지만 보통 죽지는 않음
```

예를 들어 CPU limit이 `1`인데 애플리케이션이 CPU를 더 쓰려고 하면, 쿠버네티스가 CPU 사용을 조절한다.

```text
더 쓰고 싶어도 1 CPU까지만 사용 가능
```

---

## 4. Memory limit을 넘으면?

Memory는 다르다.

Memory limit을 넘으면 Pod가 죽을 수 있다.

이걸 **OOMKilled**라고 한다.

```text
OOM = Out Of Memory
Killed = 죽임
```

즉:

```text
Memory limit 초과
→ OOMKilled 발생
→ 컨테이너 종료
→ 다시 재시작될 수 있음
```

화면에 나온 이 문장이 그 뜻이야.

```text
Memory limit을 초과해서 사용되는 파드는 종료(OOM Kill)되며 다시 스케줄링 된다.
```

정확히는 컨테이너가 죽고, Pod의 restartPolicy에 따라 다시 시작될 수 있어.

---

## 5. requests와 limits 차이

| 구분          | requests   | limits          |
| ----------- | ---------- | --------------- |
| 의미          | 최소 보장 요청량  | 최대 사용 제한량       |
| 사용 시점       | 스케줄링할 때 중요 | 실행 중 제한할 때 중요   |
| CPU 초과 시    | 해당 없음      | 느려짐, throttling |
| Memory 초과 시 | 해당 없음      | OOMKilled 가능    |
| 비유          | 최소 필요 예산   | 사용 한도           |

한 줄로 외우면 이거다.

```text
requests = 이 정도는 필요해요
limits = 이 이상은 쓰지 마세요
```

---

## 6. 전체 YAML 예시

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-demo
spec:
  containers:
  - name: app
    image: nginx
    resources:
      requests:
        cpu: "500m"
        memory: "256Mi"
      limits:
        cpu: "1"
        memory: "512Mi"
```

해석하면:

```text
최소 CPU 0.5개, 메모리 256Mi 필요
최대 CPU 1개, 메모리 512Mi까지 사용 가능
```

---

## 7. CPU 단위에서 m은 뭐야?

CPU에서 `500m`은 `0.5 CPU`라는 뜻이다.

```text
1000m = 1 CPU
500m = 0.5 CPU
250m = 0.25 CPU
100m = 0.1 CPU
```

즉:

```yaml
cpu: "500m"
```

은 CPU 반 개 정도를 요청한다는 뜻이다.

---

## 8. Memory 단위

Memory는 보통 이렇게 쓴다.

```text
Mi
Gi
```

예를 들면:

```text
256Mi
512Mi
1Gi
```

대충 이렇게 보면 된다.

```text
1024Mi = 1Gi
```

---

## 9. CKA에서 어떻게 나올까?

CKA에서는 보통 이런 식으로 나온다.

```text
Create a Pod named nginx with image nginx.
Set CPU request to 100m and memory request to 128Mi.
Set CPU limit to 500m and memory limit to 256Mi.
```

그러면 YAML에서 이 부분을 넣으면 된다.

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"
```

시험에서는 문서에서 `assign-cpu-resource`나 `resource requirements` 예시를 찾아서 복붙 후 수정하면 된다.

---

## 10. 한 줄 정리

```text
requests는 Pod를 배치할 때 필요한 최소 리소스
limits는 Pod가 실행 중 사용할 수 있는 최대 리소스
```

진짜 시험용으로 외우면 이렇게다.

```text
requests → scheduler가 노드 고를 때 봄
limits → 컨테이너가 실행 중 넘지 못하게 막음
memory limit 초과 → OOMKilled
CPU limit 초과 → 느려짐
```
