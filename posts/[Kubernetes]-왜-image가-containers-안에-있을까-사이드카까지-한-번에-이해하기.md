---
title: "[Kubernetes] 왜 image가 containers 안에 있을까? 사이드카까지 한 번에 이해하기"
source: "https://velog.io/@yorange50/Kubernetes-왜-image가-containers-안에-있을까-사이드카까지-한-번에-이해하기"
published: "2026-05-22T05:10:16.018Z"
tags: ""
backup_date: "2026-05-29T14:52:52.715313"
---

Kubernetes YAML을 처음 보면 이런 부분이 자주 헷갈림.

```yaml
containers:
  - name: nginx-pod
    image: nginx:1.25
```

처음 보면 이렇게 생각할 수 있다.

```text
왜 이미지가 컨테이너 안에 들어가 있지?
이미지가 컨테이너 안에 있는 건가?
```

근데 정확히는 **이미지가 컨테이너 안에 들어가는 것**이 아니다.

정확한 의미는 이거다.

```text
이 컨테이너를 만들 때 nginx:1.25 이미지를 사용하라
```

즉 `image: nginx:1.25`는 컨테이너 안에 들어가는 파일이 아니라, **컨테이너를 만들기 위한 기준 이미지**를 지정하는 설정이다.

---

## 이미지와 컨테이너의 관계

이미지와 컨테이너는 이렇게 생각하면 쉽다.

```text
image
= 실행 환경이 담긴 템플릿

container
= 그 이미지를 실제로 실행한 결과
```

예를 들어 Docker에서 이 명령어를 실행한다고 해보자.

```bash
docker run nginx:1.25
```

이건 이런 뜻이다.

```text
nginx:1.25 이미지를 기반으로 컨테이너를 하나 실행해라
```

Kubernetes에서는 이걸 YAML로 표현한다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
    - name: nginx-pod
      image: nginx:1.25
```

이 YAML은 이렇게 읽으면 된다.

```text
nginx-pod라는 Pod를 만들고,
그 안에 nginx-pod라는 컨테이너를 하나 실행한다.
그 컨테이너는 nginx:1.25 이미지를 기반으로 만든다.
```

구조로 보면 이렇다.

```text
Pod
└── Container
    ├── name: nginx-pod
    └── image: nginx:1.25
```

여기서 중요한 말은 이거다.

```text
이미지가 컨테이너 안에 들어가는 게 아니라,
컨테이너가 이미지를 바탕으로 만들어진다.
```

---

## 그러면 왜 image가 containers 아래에 있을까?

이유는 간단하다.

**Pod 안에는 컨테이너가 여러 개 있을 수 있고, 각 컨테이너마다 사용하는 이미지가 다를 수 있기 때문이다.**

예를 들어 이런 YAML을 볼 수 있다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-container-pod
spec:
  containers:
    - name: nginx
      image: nginx:1.25

    - name: sidecar
      image: busybox:1.36
```

이 구조는 이렇게 된다.

```text
Pod
├── nginx 컨테이너
│   └── nginx:1.25 이미지로 실행됨
└── sidecar 컨테이너
    └── busybox:1.36 이미지로 실행됨
```

즉 `image`는 Pod 전체에 붙는 설정이 아니라, **각 컨테이너에 붙는 설정**이다.

그래서 `image`가 `containers` 아래에 있는 것이다.

---

## Pod와 Container의 관계

Kubernetes에서 Pod는 컨테이너를 감싸는 가장 작은 실행 단위다.

처음에는 이렇게 생각하면 된다.

```text
Pod = 컨테이너를 담는 실행 단위
Container = 실제 애플리케이션이 실행되는 공간
Image = 컨테이너를 만들기 위한 템플릿
```

정리하면 이렇다.

```text
Image
↓
Container
↓
Pod 안에서 실행됨
```

하지만 실제 YAML 구조는 이렇게 표현된다.

```yaml
spec:
  containers:
    - name: app
      image: nginx:1.25
```

왜냐하면 Kubernetes 입장에서는 Pod를 만들 때,

```text
이 Pod 안에 어떤 컨테이너들을 실행할 것인가?
각 컨테이너는 어떤 이미지로 만들 것인가?
```

를 정의해야 하기 때문이다.

---

## 사이드카 컨테이너는 컨테이너 안에 들어가는 걸까?

여기서 또 하나 헷갈리는 게 있다.

```text
컨테이너 안에 사이드카가 있을 수도 있지 않나?
```

감각은 거의 맞는데, 계층 구조는 조금 다르다.

정확히는 이거다.

```text
컨테이너 안에 사이드카가 있는 게 아니라,
Pod 안에 메인 컨테이너와 사이드카 컨테이너가 같이 있다.
```

즉 사이드카도 컨테이너 하나다.

```text
Pod
├── main container
└── sidecar container
```

예를 들어 nginx 컨테이너 옆에 로그를 수집하는 sidecar 컨테이너를 같이 둘 수 있다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-with-sidecar
spec:
  containers:
    - name: nginx
      image: nginx:1.25

    - name: log-sidecar
      image: busybox:1.36
      command: ["sh", "-c", "while true; do echo sidecar running; sleep 5; done"]
```

이 YAML은 이렇게 읽으면 된다.

```text
nginx-with-sidecar라는 Pod를 만든다.
그 안에 컨테이너를 2개 실행한다.

첫 번째 컨테이너는 nginx이고 nginx:1.25 이미지로 실행한다.
두 번째 컨테이너는 log-sidecar이고 busybox:1.36 이미지로 실행한다.
```

구조는 이렇다.

```text
Pod
├── nginx container
│   └── image: nginx:1.25
└── log-sidecar container
    └── image: busybox:1.36
```

여기서 중요한 건 이거다.

```text
컨테이너는 컨테이너 안에 들어가지 않는다.
컨테이너들은 Pod 안에서 나란히 실행된다.
```

---

## 사이드카는 왜 쓰는 걸까?

사이드카는 메인 컨테이너 옆에서 보조 역할을 하는 컨테이너다.

예를 들면 이런 역할을 할 수 있다.

```text
로그 수집
프록시
설정 갱신
파일 동기화
모니터링 에이전트
```

예를 들어 nginx 컨테이너가 로그를 남기고, sidecar 컨테이너가 그 로그를 읽어서 외부로 전송한다고 해보자.

```text
Pod
├── nginx container
│   └── 로그 생성
├── log-sidecar container
│   └── 로그 수집 및 전송
└── shared volume
    └── 두 컨테이너가 같이 사용
```

이때 nginx와 sidecar는 같은 Pod 안에 있기 때문에 서로 가까운 관계를 가진다.

같은 Pod 안의 컨테이너들은 보통 다음을 공유할 수 있다.

```text
같은 네트워크
같은 localhost
같은 volume
같은 생명주기
```

그래서 sidecar는 메인 컨테이너와 붙어서 움직이는 보조 컨테이너라고 보면 된다.

---

## Pod 안에 컨테이너가 여러 개 있을 때의 느낌

Pod 하나에 컨테이너 하나만 있는 경우가 가장 흔하다.

```text
Pod
└── app container
```

하지만 필요한 경우에는 Pod 하나 안에 컨테이너 여러 개를 둘 수 있다.

```text
Pod
├── app container
├── log sidecar container
└── proxy sidecar container
```

이때 각 컨테이너는 자기만의 이미지를 가진다.

```yaml
containers:
  - name: app
    image: my-app:1.0

  - name: log-agent
    image: fluent-bit:latest

  - name: proxy
    image: envoyproxy/envoy:v1.29
```

이걸 해석하면 이렇다.

```text
app 컨테이너는 my-app:1.0 이미지로 실행
log-agent 컨테이너는 fluent-bit 이미지로 실행
proxy 컨테이너는 envoy 이미지로 실행
```

그래서 `image`는 반드시 각 컨테이너 안쪽 설정으로 들어간다.

---

## 최종 정리

처음 봤던 YAML을 다시 보자.

```yaml
containers:
  - name: nginx-pod
    image: nginx:1.25
```

이건 이렇게 해석하면 된다.

```text
Pod 안에 nginx-pod라는 컨테이너를 하나 만들고,
그 컨테이너는 nginx:1.25 이미지를 기반으로 실행한다.
```

그리고 사이드카가 있는 경우에는 이렇게 된다.

```yaml
containers:
  - name: main-app
    image: my-app:1.0

  - name: sidecar
    image: busybox:1.36
```

이건 이렇게 해석한다.

```text
Pod 안에 컨테이너가 2개 있다.
main-app 컨테이너는 my-app:1.0 이미지로 실행된다.
sidecar 컨테이너는 busybox:1.36 이미지로 실행된다.
```

핵심은 이거다.

```text
이미지가 컨테이너 안에 들어가는 게 아니다.
컨테이너가 이미지를 기반으로 만들어지는 것이다.

사이드카가 컨테이너 안에 들어가는 게 아니다.
사이드카도 하나의 컨테이너이고, 메인 컨테이너와 같은 Pod 안에서 나란히 실행된다.
```

그래서 Kubernetes YAML에서 `containers` 아래에 `image`가 있는 이유는 명확하다.

```text
Pod 안에 여러 컨테이너가 있을 수 있고,
각 컨테이너마다 어떤 이미지로 실행할지 따로 정해야 하기 때문이다.
```
