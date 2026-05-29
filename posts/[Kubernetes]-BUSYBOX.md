---
title: "[K8S] BUSYBOX"
source: "https://velog.io/@yorange50/K8S-BUSYBOX"
published: "2026-05-12T09:51:29.188Z"
tags: ""
backup_date: "2026-05-29T14:52:52.755245"
---

`busybox`는 쉽게 말하면 **아주 작은 리눅스 도구 상자 이미지**

쿠버네티스 실습에서 `kubectl describe pods` 했을 때 `busybox`가 보이는 이유는 보통 그 Pod가 **busybox 이미지를 기반으로 만들어졌기 때문**이야.

---

# busybox가 뭔데?

일반 리눅스에는 명령어가 많다.

```bash
ls
cat
echo
sh
wget
sleep
ping
ps
```

이런 기본 명령어들이 많잖아.

`busybox`는 이런 기본 명령어들을 **아주 작게 모아놓은 미니 리눅스 이미지**라고 보면 된다.

즉:

```text
busybox = 작고 가벼운 리눅스 명령어 모음 이미지
```

---

# 왜 쿠버네티스에서 자주 쓰냐?

쿠버네티스 실습에서는 굳이 무거운 Ubuntu나 CentOS 이미지를 쓸 필요가 없을 때가 많아.

예를 들어 그냥 Pod 하나 띄워서:

```bash
sleep 3600
```

하게 만들거나,

```bash
echo hello
```

출력하게 하거나,

```bash
wget
nslookup
ping
```

같은 간단한 테스트를 하고 싶을 때가 있다.

이럴 때 `busybox`를 쓴다.

가볍고 빠르기 때문이다.

---

# 예를 들어 이런 Pod가 있다고 해보자

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: busybox-pod
spec:
  containers:
    - name: busybox
      image: busybox
      command: ["sleep", "3600"]
```

이 Pod는 `busybox` 이미지를 사용한다.

그래서 describe를 치면:

```bash
kubectl describe pod busybox-pod
```

출력에 이런 게 보인다.

```text
Containers:
  busybox:
    Image: busybox
    Command:
      sleep
      3600
```

여기서 `busybox`는 두 가지 의미로 나올 수 있다.

```text
컨테이너 이름: busybox
이미지 이름: busybox
```

---

# k describe pods에서 busybox가 나오는 위치

보통 이런 식으로 나온다.

```text
Containers:
  busybox:
    Container ID:   containerd://...
    Image:          busybox
    Image ID:       docker.io/library/busybox@sha256:...
    Command:
      sleep
      3600
```

여기서 보면 된다.

## Containers 아래의 busybox

```text
Containers:
  busybox:
```

이건 **컨테이너 이름**이다.

YAML에서 이렇게 정한 이름이다.

```yaml
name: busybox
```

---

## Image: busybox

```text
Image: busybox
```

이건 **컨테이너가 사용한 이미지 이름**이다.

YAML에서 이렇게 쓴 부분이다.

```yaml
image: busybox
```

즉, `kubectl describe pod`에서 busybox가 보인다는 건:

```text
이 Pod 안에 busybox라는 컨테이너가 있고,
그 컨테이너는 busybox 이미지를 사용하고 있다.
```

라는 뜻이다.

---

# 이미지랑 컨테이너 이름은 다를 수도 있다

꼭 둘 다 `busybox`일 필요는 없다.

예를 들어 이렇게 만들 수도 있다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
spec:
  containers:
    - name: test-container
      image: busybox
      command: ["sleep", "3600"]
```

그러면 describe에는 이렇게 나온다.

```text
Containers:
  test-container:
    Image: busybox
```

해석하면:

```text
컨테이너 이름은 test-container
사용한 이미지는 busybox
```

이다.

---

# 왜 sleep 3600이랑 같이 자주 나오냐?

busybox는 기본적으로 실행할 프로세스가 없으면 바로 종료된다.

컨테이너는 안에서 실행 중인 메인 프로세스가 끝나면 같이 종료된다.

그래서 그냥 이렇게 만들면:

```bash
kubectl run busybox --image=busybox
```

Pod가 바로 끝날 수 있다.

그래서 실습에서는 보통 이렇게 한다.

```bash
kubectl run busybox --image=busybox --command -- sleep 3600
```

뜻은:

```text
busybox 이미지로 Pod를 만들고,
컨테이너 안에서 sleep 3600 명령어를 실행해라.
```

그러면 컨테이너가 3600초 동안 살아 있으니까, 그동안 접속해서 테스트할 수 있다.

---

# busybox는 언제 쓰냐?

주로 이런 상황에서 쓴다.

```text
Pod 하나 임시로 띄워서 테스트할 때
DNS 확인할 때
Service 연결 확인할 때
네트워크 통신 테스트할 때
간단한 명령어 실행할 때
CKA 실습에서 빠르게 Pod 만들 때
```

예를 들면:

```bash
kubectl run busybox --image=busybox --command -- sleep 3600
```

그다음 안에 들어간다.

```bash
kubectl exec -it busybox -- sh
```

안에서 테스트한다.

```bash
wget 서비스이름:포트
nslookup 서비스이름
ping IP주소
```

---

# 한 줄로 정리하면

```text
busybox는 작은 리눅스 명령어 모음 이미지다.
```

`kubectl describe pods`에서 busybox가 나오는 이유는:

```text
그 Pod 안의 컨테이너 이름이 busybox이거나,
그 컨테이너가 busybox 이미지를 사용하고 있기 때문이다.
```

CKA식으로 보면 이렇게 이해하면 된다.

```text
busybox = 테스트용 가벼운 컨테이너 이미지
describe pod에서 Image: busybox = 이 Pod는 busybox 이미지로 실행됨
describe pod에서 Containers: busybox = 컨테이너 이름이 busybox
```
