---
title: "[KUBERNETES] -f"
source: "https://velog.io/@yorange50/KUBERNETES-f"
published: "2026-05-13T09:05:34.885Z"
tags: ""
backup_date: "2026-05-29T14:52:52.744055"
---

지금 오류 원인은 **명령어에서 `-f`를 잘못 쓴 것**이야.

## 지금 친 명령어

```bash
k scale -f rs new-replica-set --replicas=5
```

이렇게 치면 Kubernetes는 `rs`를 **리소스 종류**로 해석하는 게 아니라, `-f` 옵션 뒤에 온 값이라서 **파일 경로**로 해석함.

즉 Kubernetes 입장에서는 이렇게 이해함.

```text
-f rs
```

```text
rs라는 파일을 찾아서 scale 하라는 뜻인가?
```

그래서 이런 오류가 뜬 거야.

```text
error: the path "rs" does not exist
```

즉, `rs`라는 파일이 없다는 뜻.

---

## 두 번째 명령어도 같은 이유

```bash
k scale -f new-replica-set --replicas=5
```

이것도 Kubernetes는 이렇게 해석함.

```text
new-replica-set이라는 파일을 찾아라
```

그런데 그런 파일이 없으니까:

```text
error: the path "new-replica-set" does not exist
```

라고 나온 것.

---

## 세 번째도 마찬가지

```bash
k scale -f ReplicaSet --replicas=5
```

이것도:

```text
ReplicaSet이라는 파일을 찾아라
```

로 해석됨.

그래서:

```text
error: the path "ReplicaSet" does not exist
```

---

# 정답 명령어

이미 `new-replica-set`이라는 ReplicaSet을 만들었으니까, 파일 기준이 아니라 **리소스 기준으로 scale** 해야 해.

```bash
k scale rs new-replica-set --replicas=5
```

또는 풀네임으로:

```bash
kubectl scale replicaset new-replica-set --replicas=5
```

또는 이렇게도 가능:

```bash
kubectl scale rs/new-replica-set --replicas=5
```

---

## 왜 `-f`를 빼야 하냐

`-f`는 파일을 사용할 때 쓰는 옵션이야.

예를 들어 YAML 파일을 수정해서 적용할 때는:

```bash
kubectl apply -f new-replica-set.yaml
```

이건 맞음.

하지만 이미 생성된 리소스를 이름으로 조작할 때는 `-f`를 쓰면 안 됨.

```bash
kubectl scale rs new-replica-set --replicas=5
```

이렇게 해야 함.

---

## 지금 바로 할 순서

먼저 ReplicaSet 이름 확인:

```bash
k get rs
```

아마 이렇게 나올 거야.

```text
NAME              DESIRED   CURRENT   READY
new-replica-set   2         2         2
```

그다음 scale:

```bash
k scale rs new-replica-set --replicas=5
```

확인:

```bash
k get rs
```

또는 Pod 확인:

```bash
k get pods
```

---

## 핵심만 정리

```bash
-f
```

는 **파일 경로를 넘길 때** 쓰는 옵션.

```bash
k scale -f rs ...
```

라고 치면 `rs`를 리소스 타입이 아니라 **파일 이름**으로 봄.

그래서 정답은:

```bash
k scale rs new-replica-set --replicas=5
```

이거야.
