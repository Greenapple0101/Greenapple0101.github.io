---
title: "[Kubernetes] kubectl describe nodes는 어디부터 봐야 할까?"
source: "https://velog.io/@yorange50/Kubernetes-kubectl-describe-nodes는-어디부터-봐야-할까"
published: "2026-05-12T09:18:04.365Z"
tags: ""
backup_date: "2026-05-29T14:52:52.755570"
---

쿠버네티스를 공부하다 보면 `kubectl describe nodes` 명령어를 자주 보게 된다.

```bash
kubectl describe nodes
```

처음 이 명령어를 치면 출력이 너무 길다.

노드 이름, 라벨, 어노테이션, IP, 자원, 파드 목록, 이벤트까지 한 번에 쏟아진다.

그래서 처음에는 이런 생각이 든다.

> 이걸 다 봐야 하나?
> 어디가 중요한 거지?
> CKA에서는 뭘 보고 판단해야 하지?

결론부터 말하면 전부 다 외울 필요는 없다.

실제로는 아래 순서대로 보면 된다.

```text
Conditions → Taints → Capacity/Allocatable → Allocated resources → Events
```

이 순서만 익혀도 노드 상태를 읽는 기본 흐름은 잡을 수 있다.

---

# 1. Conditions

가장 먼저 볼 곳은 `Conditions`다.

`Conditions`는 노드가 지금 정상 상태인지, 자원 압박을 받고 있는지 보여준다.

예시는 이런 식으로 나온다.

```text
Conditions:
  Type             Status
  ----             ------
  MemoryPressure   False
  DiskPressure     False
  PIDPressure      False
  Ready            True
```

여기서 제일 먼저 봐야 하는 것은 `Ready`다.

```text
Ready   True
```

`Ready`가 `True`면 일단 노드는 정상적으로 클러스터에 붙어 있는 상태다.

반대로 이렇게 나오면 문제가 있다.

```text
Ready   False
```

또는

```text
Ready   Unknown
```

이 경우에는 노드 자체가 정상적으로 동작하지 않거나, API Server가 노드 상태를 제대로 확인하지 못하는 상황일 수 있다.

---

## Conditions에서 보는 핵심 값

| 항목             | 정상 상태 | 의미             |
| -------------- | ----: | -------------- |
| Ready          |  True | 노드가 정상적으로 동작 중 |
| MemoryPressure | False | 메모리 부족 없음      |
| DiskPressure   | False | 디스크 부족 없음      |
| PIDPressure    | False | 프로세스 수 압박 없음   |

정상적인 노드는 보통 이렇게 보이면 된다.

```text
Ready            True
MemoryPressure   False
DiskPressure     False
PIDPressure      False
```

즉, 해석하면 이렇다.

```text
노드는 살아 있고,
메모리도 괜찮고,
디스크도 괜찮고,
프로세스 수도 괜찮다.
```

반대로 `DiskPressure True`가 보이면 디스크 부족 문제를 의심해야 한다.

```text
DiskPressure   True
```

이 상태에서는 Pod가 제대로 스케줄링되지 않거나, 기존 Pod가 Evicted될 수도 있다.

`MemoryPressure True`도 마찬가지다.

```text
MemoryPressure   True
```

메모리가 부족해서 Pod가 쫓겨나거나 새 Pod가 올라가지 못할 수 있다.

그래서 `kubectl describe nodes`를 보면 제일 먼저 이렇게 생각하면 된다.

> 이 노드 Ready인가?
> Pressure 걸린 건 없는가?

---

# 2. Taints

두 번째로 볼 곳은 `Taints`다.

예시는 이런 식으로 나온다.

```text
Taints: node-role.kubernetes.io/control-plane:NoSchedule
```

`Taints`는 쉽게 말하면 노드가 Pod를 받지 않기 위해 걸어두는 조건이다.

특히 control-plane 노드에는 보통 이런 taint가 붙어 있다.

```text
node-role.kubernetes.io/control-plane:NoSchedule
```

뜻은 이거다.

```text
일반 Pod는 이 노드에 스케줄링하지 마라.
```

그래서 Pod가 Pending 상태일 때 `Taints`를 꼭 봐야 한다.

예를 들어 노드는 Ready인데 Pod가 계속 Pending이라면 이런 가능성이 있다.

```text
노드는 살아 있음
하지만 Taint 때문에 Pod가 못 올라감
```

---

## Taints가 중요한 이유

Pod는 기본적으로 아무 노드에나 올라가는 것이 아니다.

노드에 `Taint`가 있으면, Pod는 그 Taint를 견딜 수 있는 `Toleration`이 있어야 올라갈 수 있다.

간단히 말하면 이렇다.

```text
Taint = 노드가 Pod를 거부하는 조건
Toleration = Pod가 그 조건을 견디겠다는 설정
```

예를 들어 control-plane 노드에 이런 taint가 있으면:

```text
node-role.kubernetes.io/control-plane:NoSchedule
```

일반 Pod는 그 노드에 올라가지 못한다.

그래서 CKA 문제를 풀 때 Pod가 Pending이면 이런 흐름으로 보면 된다.

```bash
kubectl describe pod 파드이름
kubectl describe node 노드이름
```

그리고 노드 쪽에서 `Taints`를 확인한다.

---

# 3. Capacity / Allocatable

세 번째로 볼 곳은 `Capacity`와 `Allocatable`이다.

출력은 보통 이런 식이다.

```text
Capacity:
  cpu:                2
  memory:             4042468Ki
  pods:               110

Allocatable:
  cpu:                2
  memory:             3930068Ki
  pods:               110
```

여기서는 노드가 가진 자원과 실제로 Pod에게 줄 수 있는 자원을 확인한다.

---

## Capacity

`Capacity`는 노드가 전체적으로 가지고 있는 자원이다.

```text
Capacity:
  cpu: 2
  memory: 4042468Ki
  pods: 110
```

해석하면 이렇다.

```text
이 노드는 CPU 2개,
메모리 약 4GB,
최대 Pod 110개 정도를 수용할 수 있다.
```

---

## Allocatable

`Allocatable`은 Pod가 실제로 사용할 수 있는 자원이다.

```text
Allocatable:
  cpu: 2
  memory: 3930068Ki
  pods: 110
```

`Capacity`와 `Allocatable`은 완전히 같지 않을 수 있다.

왜냐하면 노드 자체도 kubelet, container runtime, 시스템 프로세스 같은 것들이 자원을 사용하기 때문이다.

쉽게 비유하면 이렇다.

```text
Capacity = 노트북 전체 용량
Allocatable = 앱들이 실제로 사용할 수 있는 용량
```

쿠버네티스에서는 Pod를 스케줄링할 때 아무 기준 없이 올리지 않는다.

Pod의 `requests`를 보고, 노드의 `Allocatable` 안에 들어갈 수 있는지 판단한다.

그래서 Pod가 Pending일 때는 이런 질문을 해야 한다.

> 이 노드에 실제로 남은 자원이 있나?
> Pod가 요청한 CPU/Memory를 받을 수 있나?

---

# 4. Allocated resources

네 번째로 볼 곳은 `Allocated resources`다.

예시는 이런 식이다.

```text
Allocated resources:
  Resource           Requests    Limits
  cpu                250m (12%)  0 (0%)
  memory             140Mi (3%)  340Mi (8%)
```

여기는 현재 노드에 올라간 Pod들이 얼마나 자원을 요청하고 있는지 보여준다.

중요한 값은 `Requests`와 `Limits`다.

---

## Requests

`Requests`는 Pod가 최소한 필요하다고 요청한 자원이다.

예를 들어 어떤 Pod가 이렇게 설정되어 있다고 해보자.

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
```

그러면 쿠버네티스 스케줄러는 이렇게 판단한다.

```text
이 Pod는 최소 CPU 100m, Memory 128Mi가 필요하구나.
이걸 수용할 수 있는 노드에 배치해야겠다.
```

즉, 스케줄링 기준은 실제 사용량이 아니라 `requests`다.

---

## Limits

`Limits`는 Pod가 최대로 사용할 수 있는 자원이다.

```yaml
resources:
  limits:
    cpu: 500m
    memory: 512Mi
```

해석하면 이렇다.

```text
이 Pod는 CPU는 최대 500m까지,
메모리는 최대 512Mi까지 사용할 수 있다.
```

특히 메모리 limit을 넘으면 Pod가 죽을 수 있다.

---

## Allocated resources를 왜 봐야 할까?

Pod가 Pending일 때 이런 상황이 있을 수 있다.

```text
노드는 Ready True
Taint도 문제 없음
그런데 Pod가 안 올라감
```

이때는 자원이 부족한지 봐야 한다.

예를 들어 `Allocated resources`가 이렇게 되어 있다고 하자.

```text
cpu      1900m (95%)
memory   3700Mi (94%)
```

그러면 새 Pod가 요청한 자원을 받아줄 공간이 없을 수 있다.

즉, `Allocated resources`는 이런 걸 확인하는 곳이다.

```text
이 노드가 이미 꽉 찼나?
Pod들이 request를 너무 많이 잡고 있나?
새 Pod를 받을 수 있나?
```

---

# 5. Events

마지막으로 볼 곳은 `Events`다.

보통 출력 맨 아래에 있다.

```text
Events:
  Type     Reason                   Age    From     Message
  ----     ------                   ----   ----     -------
  Normal   Starting                 10m    kubelet  Starting kubelet.
  Warning  InvalidDiskCapacity      10m    kubelet  invalid capacity 0 on image filesystem
```

`Events`는 노드에서 발생한 사건 로그다.

문제가 있을 때는 여기에 힌트가 많이 나온다.

특히 봐야 할 것은 `Warning`이다.

```text
Warning
```

예를 들어 이런 메시지가 있을 수 있다.

```text
NodeNotReady
KubeletNotReady
DiskPressure
MemoryPressure
NetworkPluginNotReady
InvalidDiskCapacity
```

이벤트는 원인을 직접적으로 알려주는 경우가 많다.

예를 들어 `NetworkPluginNotReady`가 보이면 CNI 문제를 의심할 수 있다.

```text
NetworkPluginNotReady
```

`DiskPressure`가 보이면 디스크 부족 문제를 의심할 수 있다.

```text
DiskPressure
```

`KubeletNotReady`가 보이면 kubelet 상태를 확인해야 한다.

```text
KubeletNotReady
```

그래서 `Events`는 마지막에 보는 이유가 있다.

앞에서 상태를 먼저 보고, 마지막에 이벤트로 원인을 확인하는 흐름이다.

---

# 정리

`kubectl describe nodes`는 출력이 길지만, 보는 순서는 단순하다.

```text
Conditions → Taints → Capacity/Allocatable → Allocated resources → Events
```

각각의 의미는 이렇다.

| 순서 | 보는 곳                 | 확인할 것                      |
| -: | -------------------- | -------------------------- |
|  1 | Conditions           | 노드가 Ready인지, Pressure가 있는지 |
|  2 | Taints               | Pod 스케줄링을 막는 조건이 있는지       |
|  3 | Capacity/Allocatable | 노드 전체 자원과 실제 사용 가능 자원      |
|  4 | Allocated resources  | 현재 Pod들이 예약한 자원            |
|  5 | Events               | Warning이나 장애 힌트            |

실제로는 이렇게 생각하면서 보면 된다.

```text
1. 노드가 살아 있나?
2. 노드가 Pod를 거부하고 있나?
3. 노드에 자원은 충분한가?
4. 이미 자원이 꽉 차 있나?
5. 이벤트에 에러 힌트가 있나?
```

CKA나 실무에서 노드 문제를 볼 때도 이 흐름이 기본이다.

```bash
kubectl get nodes
kubectl describe node 노드이름
```

그리고 출력이 길어도 당황하지 말고 이 순서대로 보면 된다.

```text
Conditions
Taints
Capacity/Allocatable
Allocated resources
Events
```

결국 `kubectl describe nodes`는 단순히 노드 정보를 많이 보여주는 명령어가 아니라,

```text
노드가 정상인지
Pod가 올라갈 수 있는지
자원이 부족한지
무슨 문제가 있었는지
```

를 한 번에 확인하는 명령어다.
