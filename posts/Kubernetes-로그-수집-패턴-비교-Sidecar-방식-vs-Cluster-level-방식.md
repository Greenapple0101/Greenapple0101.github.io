---
title: "[Kubernetes] 로그 수집 패턴 비교: Sidecar 방식 vs Cluster-level 방식"
source: "https://velog.io/@yorange50/Kubernetes-로그-수집-패턴-비교-Sidecar-방식-vs-Cluster-level-방식"
published: "2026-05-27T15:33:35.321Z"
tags: ""
backup_date: "2026-05-29T14:52:52.711285"
---

쿠버네티스에서 애플리케이션 로그를 수집하는 방식은 크게 두 가지로 볼 수 있다.

```text
1. 파드 사이드카 패턴 기반 로그 수집
2. 클러스터 레벨 패턴 기반 로그 수집
```

둘 다 “로그를 모은다”는 목적은 같지만, **어디에서 로그를 수집하느냐**, **누가 로그 수집을 담당하느냐**가 다르다.

---

## 1. 먼저 쿠버네티스 로그 기본 구조

쿠버네티스에서 컨테이너는 보통 표준 출력으로 로그를 남긴다.

```text
stdout
stderr
```

예를 들면 애플리케이션에서 이런 로그를 찍는다.

```text
[INFO] user login success
[ERROR] database connection failed
```

컨테이너는 이 로그를 stdout/stderr로 내보내고, 노드의 컨테이너 런타임이 이 로그를 파일로 저장한다.

대략 흐름은 이렇다.

```text
애플리케이션
→ stdout / stderr
→ 컨테이너 런타임 로그 파일
→ 로그 수집기
→ Elasticsearch / Loki / CloudWatch 등
```

여기서 로그 수집기를 어디에 두느냐에 따라 패턴이 나뉜다.

---

# 2. 파드 사이드카 패턴 기반 로그 수집

## Sidecar 패턴이란?

Sidecar는 하나의 Pod 안에 메인 컨테이너 옆에 보조 컨테이너를 같이 두는 방식이다.

```text
Pod
├── app container
└── log collector sidecar container
```

즉, 애플리케이션 컨테이너와 로그 수집 컨테이너가 **같은 Pod 안에서 함께 실행**된다.

---

## Sidecar 로그 수집 구조

예를 들어 애플리케이션이 파일에 로그를 남긴다고 해보자.

```text
/var/log/app/app.log
```

그러면 같은 Pod 안의 sidecar 컨테이너가 이 파일을 읽어서 외부 로그 시스템으로 보낸다.

```text
app container
→ /var/log/app/app.log
→ sidecar container가 읽음
→ 로그 저장소로 전송
```

구조로 보면 이렇다.

```text
Pod
├── app container
│   └── /var/log/app/app.log 에 로그 기록
│
└── sidecar container
    └── app.log 읽어서 Loki / Elasticsearch / Fluentd로 전송
```

이때 두 컨테이너는 같은 Pod 안에 있으므로 `emptyDir` 같은 볼륨을 공유할 수 있다.

---

## Sidecar 방식 예시 YAML

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-log-sidecar
spec:
  volumes:
  - name: log-volume
    emptyDir: {}

  containers:
  - name: app
    image: my-app
    volumeMounts:
    - name: log-volume
      mountPath: /var/log/app

  - name: log-sidecar
    image: fluent/fluent-bit
    volumeMounts:
    - name: log-volume
      mountPath: /var/log/app
```

핵심은 이 부분이다.

```yaml
volumes:
- name: log-volume
  emptyDir: {}
```

그리고 두 컨테이너가 같은 볼륨을 마운트한다.

```yaml
app container → /var/log/app에 로그 기록
sidecar container → /var/log/app의 로그 읽기
```

---

## Sidecar 방식의 장점

Sidecar 방식의 가장 큰 장점은 **애플리케이션별로 로그 수집 방식을 세밀하게 제어할 수 있다는 것**이다.

예를 들어 어떤 애플리케이션은 JSON 로그를 쓰고, 어떤 애플리케이션은 일반 텍스트 로그를 쓸 수 있다.

```text
app-a: JSON 로그
app-b: access.log / error.log 분리
app-c: 특수한 멀티라인 로그
```

이럴 때 Sidecar를 붙이면 애플리케이션마다 다른 로그 수집 설정을 줄 수 있다.

```text
app-a Pod에는 JSON 파서용 sidecar
app-b Pod에는 nginx 로그용 sidecar
app-c Pod에는 멀티라인 처리용 sidecar
```

즉, 애플리케이션 단위 커스터마이징이 쉽다.

---

## Sidecar 방식의 단점

하지만 단점도 크다.

Pod마다 로그 수집용 컨테이너가 하나씩 더 붙는다.

```text
app Pod 100개
→ sidecar container 100개 추가
```

이러면 리소스 사용량이 늘어난다.

```text
CPU 사용량 증가
Memory 사용량 증가
Pod 구성 복잡도 증가
YAML 길어짐
운영 관리 포인트 증가
```

또 모든 애플리케이션에 sidecar를 붙이면 배포 구조가 무거워질 수 있다.

---

# 3. 클러스터 레벨 패턴 기반 로그 수집

## Cluster-level 로그 수집이란?

Cluster-level 방식은 로그 수집기를 Pod마다 붙이는 게 아니라, **노드마다 하나씩 로그 수집기를 배치하는 방식**이다.

보통 `DaemonSet`으로 배포한다.

```text
Node 1 → 로그 수집기 1개
Node 2 → 로그 수집기 1개
Node 3 → 로그 수집기 1개
```

구조로 보면 이렇다.

```text
worker-node-1
├── app pod
├── app pod
└── log collector agent

worker-node-2
├── app pod
├── app pod
└── log collector agent
```

즉, 각 노드에 있는 로그 수집기가 그 노드의 컨테이너 로그들을 한꺼번에 수집한다.

---

## Cluster-level 로그 수집 구조

컨테이너 로그는 보통 노드의 특정 경로에 저장된다.

대표적으로 이런 경로들이 나온다.

```text
/var/log/containers
/var/log/pods
```

로그 수집기인 Fluent Bit, Fluentd, Promtail 같은 에이전트가 이 경로를 읽는다.

```text
각 컨테이너 stdout/stderr 로그
→ 노드의 /var/log/containers에 저장
→ DaemonSet 로그 에이전트가 수집
→ Loki / Elasticsearch / CloudWatch 등으로 전송
```

흐름은 이렇다.

```text
Pod 로그
→ Node 로그 파일
→ Node마다 떠 있는 로그 수집기
→ 중앙 로그 저장소
```

---

## Cluster-level 방식 예시

보통 이런 것들이 DaemonSet으로 뜬다.

```text
fluent-bit
fluentd
promtail
filebeat
datadog-agent
cloudwatch-agent
```

예를 들어 Promtail을 DaemonSet으로 띄우면 각 노드에서 컨테이너 로그를 읽고 Loki로 보낸다.

```text
worker-node-1: promtail
worker-node-2: promtail
worker-node-3: promtail
```

노드가 추가되면 DaemonSet이 자동으로 새 노드에도 로그 수집기를 띄운다.

```text
worker-node-4 추가
→ promtail Pod 자동 생성
→ worker-node-4의 로그도 수집 시작
```

---

## Cluster-level 방식의 장점

가장 큰 장점은 **운영이 단순하다**는 것이다.

애플리케이션 Pod마다 sidecar를 붙일 필요가 없다.

```text
애플리케이션 Pod는 그냥 로그만 stdout/stderr로 출력
로그 수집은 클러스터의 로그 에이전트가 처리
```

그래서 애플리케이션 YAML이 깔끔해진다.

```text
app container만 정의하면 됨
로그 수집용 sidecar를 매번 넣을 필요 없음
```

또 클러스터 전체에 공통 로그 수집 정책을 적용하기 쉽다.

```text
모든 Pod 로그를 Loki로 보낸다
모든 namespace 로그를 Elasticsearch로 보낸다
특정 label 로그만 필터링한다
```

대부분의 쿠버네티스 운영 환경에서는 이 방식이 기본에 가깝다.

---

## Cluster-level 방식의 단점

단점은 애플리케이션별로 아주 세밀한 로그 처리를 하기는 상대적으로 어렵다는 점이다.

예를 들어 어떤 애플리케이션만 특수한 로그 파싱이 필요할 수 있다.

```text
app-a는 JSON 파싱
app-b는 멀티라인 stack trace 처리
app-c는 특정 필드 마스킹
```

물론 Fluent Bit이나 Promtail 설정으로 어느 정도 처리할 수 있지만, Sidecar 방식처럼 애플리케이션 옆에 전용 수집기를 붙이는 것보다는 덜 직관적일 수 있다.

또 애플리케이션이 stdout/stderr가 아니라 컨테이너 내부 특정 파일에만 로그를 남긴다면, 클러스터 레벨 수집기가 바로 못 읽을 수도 있다.

이 경우에는 애플리케이션 로그를 stdout으로 바꾸거나, 별도 볼륨/sidecar 처리가 필요하다.

---

# 4. Sidecar 방식 vs Cluster-level 방식 비교

| 구분     | Sidecar 로그 수집                          | Cluster-level 로그 수집                     |
| ------ | -------------------------------------- | --------------------------------------- |
| 수집 위치  | Pod 내부                                 | Node 단위                                 |
| 배포 방식  | 각 Pod에 sidecar 컨테이너 추가                 | DaemonSet으로 노드마다 로그 에이전트 배포             |
| 대표 도구  | Fluent Bit sidecar, custom log shipper | Fluent Bit, Fluentd, Promtail, Filebeat |
| 로그 대상  | 특정 Pod/앱 중심                            | 클러스터 전체 Pod 로그                          |
| 설정 단위  | 애플리케이션별                                | 클러스터/노드별                                |
| 리소스 사용 | Pod마다 sidecar 추가로 증가                   | 노드당 에이전트 하나라 상대적으로 효율적                  |
| 운영 복잡도 | Pod YAML이 복잡해짐                         | 중앙 관리가 쉬움                               |
| 커스터마이징 | 앱별 세밀한 처리에 유리                          | 공통 정책 적용에 유리                            |
| 주 사용처  | 특수 로그 처리, 파일 로그 변환                     | 일반적인 클러스터 로그 수집                         |

---

# 5. 장단점 정리

## Sidecar 패턴 기반 로그 수집

### 장점

```text
애플리케이션별 로그 수집 설정 가능
특수한 로그 포맷 처리에 유리
파일 로그를 읽어 stdout 또는 외부 시스템으로 전달 가능
Pod 단위로 독립적인 로그 파이프라인 구성 가능
```

### 단점

```text
Pod마다 sidecar 컨테이너가 추가됨
CPU/Memory 사용량 증가
YAML이 복잡해짐
배포와 운영 관리 포인트 증가
대규모 클러스터에서는 비효율적일 수 있음
```

---

## Cluster-level 패턴 기반 로그 수집

### 장점

```text
클러스터 전체 로그를 중앙에서 수집 가능
DaemonSet으로 노드마다 하나씩 배포하면 됨
애플리케이션 Pod 구성이 단순함
운영 관리가 쉬움
대부분의 일반적인 로그 수집에 적합
리소스 효율이 Sidecar 방식보다 좋음
```

### 단점

```text
애플리케이션별 특수 로그 처리에는 상대적으로 불리함
stdout/stderr 기반 로그 수집에 더 적합함
컨테이너 내부 파일 로그는 바로 수집하기 어려울 수 있음
로그 에이전트 설정이 복잡해질 수 있음
```

---

# 6. 언제 Sidecar를 쓰고, 언제 Cluster-level을 쓸까?

## Cluster-level 방식을 쓰면 좋은 경우

대부분의 일반적인 쿠버네티스 운영 환경에서는 Cluster-level 로그 수집이 적합하다.

```text
대부분의 애플리케이션이 stdout/stderr로 로그를 출력함
클러스터 전체 로그를 한 곳으로 모으고 싶음
운영을 단순하게 유지하고 싶음
노드별 로그 에이전트로 충분함
```

예를 들면:

```text
모든 Pod 로그를 Loki로 수집
모든 컨테이너 로그를 Elasticsearch로 전송
CloudWatch로 EKS 전체 로그 수집
```

이런 경우에는 Cluster-level 방식이 자연스럽다.

---

## Sidecar 방식을 쓰면 좋은 경우

Sidecar 방식은 조금 특수한 상황에서 유용하다.

```text
애플리케이션이 stdout이 아니라 파일에만 로그를 남김
앱마다 로그 포맷이 너무 다름
특정 앱에만 별도 파서나 전처리가 필요함
로그를 수집하기 전에 마스킹/필터링/가공해야 함
Pod 단위로 독립적인 로그 파이프라인이 필요함
```

예를 들면:

```text
legacy app이 /var/log/app.log에만 로그를 씀
특정 서비스만 stack trace 멀티라인 처리가 복잡함
특정 앱 로그만 별도 저장소로 보내야 함
보안상 특정 로그를 Pod 내부에서 먼저 마스킹해야 함
```

이런 경우에는 Sidecar 방식이 더 맞을 수 있다.

---

# 7. 제일 현실적인 결론

실무에서는 보통 이렇게 간다.

```text
기본은 Cluster-level 로그 수집
특수한 애플리케이션만 Sidecar 추가
```

즉, 모든 Pod에 sidecar를 붙이는 것보다는 클러스터 전체에는 DaemonSet 기반 로그 에이전트를 깔고, 예외적인 서비스에만 sidecar를 붙이는 식이다.

```text
일반 서비스 로그
→ stdout/stderr
→ DaemonSet 로그 에이전트가 수집

특수 서비스 로그
→ 파일 로그
→ Sidecar가 전처리
→ 로그 저장소로 전송
```

이렇게 하면 운영 단순성과 유연성을 둘 다 챙길 수 있다.

---

# 8. 한 줄 정리

```text
Sidecar 로그 수집 = Pod 옆에 로그 수집 컨테이너를 붙이는 방식
Cluster-level 로그 수집 = 노드마다 로그 에이전트를 띄워 클러스터 전체 로그를 수집하는 방식
```

시험이나 면접에서는 이렇게 말하면 된다.

```text
일반적으로는 DaemonSet 기반 Cluster-level 로그 수집을 사용하고,
애플리케이션별 특수한 로그 처리나 파일 로그 수집이 필요할 때 Sidecar 패턴을 사용한다.
```

핵심은 이거다.

```text
Sidecar는 앱별 커스터마이징에 강하고,
Cluster-level은 운영 단순성과 전체 수집에 강하다.
```
