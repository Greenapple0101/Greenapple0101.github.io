---
title: "[CKA] ConfigMap으로 Nginx TLS 버전 제한하기: TLSv1.3만 허용하는 문제 풀이"
source: "https://velog.io/@yorange50/CKA-ConfigMap으로-Nginx-TLS-버전-제한하기-TLSv1.3만-허용하는-문제-풀이"
published: "2026-05-18T01:59:19.030Z"
tags: ""
backup_date: "2026-05-29T14:52:52.730412"
---



CKA 문제를 풀다 보면 Kubernetes 리소스만 다루는 것처럼 보이지만, 실제로는 애플리케이션 설정까지 같이 이해해야 하는 문제가 자주 나온다. 이번 문제도 겉으로는 `Deployment`, `Namespace`, `ConfigMap` 문제처럼 보이지만, 안쪽으로 들어가면 Nginx의 TLS 설정을 수정하는 문제다.

문제는 다음과 같다.

```text
An Nginx Deploy named nginx-static is Running in the nginx-static NS.
It is configured using a ConfigMap named nginx-config.
Update the nginx-config ConfigMap to allow only TLSv1.3 connections.
re-create, restart, or scale resources as necessary.
By using command to test the changes.

[candidate@cka2025] $ curl --tls-max 1.2 https://web.k8s.local
```

이 문장을 하나씩 해석하면 이렇다.

```text
nginx-static 네임스페이스에 nginx-static이라는 Deployment가 실행 중이다.
이 Deployment는 nginx-config라는 ConfigMap을 사용해서 설정되어 있다.
nginx-config ConfigMap을 수정해서 TLSv1.3 연결만 허용하도록 만들어라.
필요하면 리소스를 다시 만들거나, 재시작하거나, 스케일링해라.
그리고 curl 명령어로 변경 사항을 테스트해라.
```

핵심은 이거다.

```text
Nginx 설정이 들어 있는 ConfigMap을 수정해서
ssl_protocols를 TLSv1.3만 허용하도록 바꾸는 문제
```

---

# 1. 문제에서 봐야 하는 리소스

문제에 나온 리소스는 세 가지다.

```text
Namespace: nginx-static
Deployment: nginx-static
ConfigMap: nginx-config
```

여기서 `nginx-static NS`라고 했으므로, 모든 `kubectl` 명령어에는 거의 항상 네임스페이스 옵션을 붙여야 한다.

```bash
-n nginx-static
```

먼저 리소스가 있는지 확인한다.

```bash
kubectl get deploy -n nginx-static
kubectl get cm -n nginx-static
```

줄여서 쓰면 이렇게도 가능하다.

```bash
k get deploy -n nginx-static
k get cm -n nginx-static
```

여기서 `cm`은 `configmap`의 줄임말이다.

```bash
kubectl get configmap
kubectl get cm
```

둘은 같은 의미다.

---

# 2. ConfigMap 내용 확인하기

문제에서 `nginx-config ConfigMap`을 수정하라고 했으므로, 먼저 내용을 확인해야 한다.

```bash
kubectl get cm nginx-config -n nginx-static -o yaml
```

여기서 옵션을 하나씩 보면 다음과 같다.

```text
cm
= ConfigMap의 줄임말

-n nginx-static
= nginx-static 네임스페이스에서 찾겠다는 뜻

-o yaml
= 출력 결과를 YAML 형식으로 보여달라는 뜻
```

`-o`는 output의 줄임말이다.

자주 쓰는 출력 옵션은 이런 것들이 있다.

```bash
-o yaml
-o json
-o wide
-o name
```

예를 들어:

```bash
kubectl get pod -o wide
```

는 Pod 목록을 더 자세히 보여준다. Pod IP, 올라간 Node 같은 정보까지 볼 수 있다.

```bash
kubectl get pod -o name
```

은 `pod/nginx-xxxx` 같은 리소스 이름만 출력한다.

이번 문제에서는 ConfigMap 안에 실제 Nginx 설정이 들어 있을 수 있으므로 `-o yaml`로 전체 내용을 보는 것이 중요하다.

---

# 3. Nginx TLS 설정 찾기

ConfigMap을 YAML로 보면 대략 이런 형태일 수 있다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
  namespace: nginx-static
data:
  nginx.conf: |
    server {
        listen 443 ssl;
        server_name web.k8s.local;

        ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;

        ssl_certificate /etc/nginx/certs/tls.crt;
        ssl_certificate_key /etc/nginx/certs/tls.key;

        location / {
            root /usr/share/nginx/html;
        }
    }
```

여기서 중요한 줄은 이 부분이다.

```nginx
ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
```

`ssl_protocols`는 Nginx에서 허용할 TLS 버전을 지정하는 설정이다.

현재 설정은 이런 뜻이다.

```text
TLSv1, TLSv1.1, TLSv1.2, TLSv1.3을 모두 허용한다.
```

하지만 문제는 이렇게 요구한다.

```text
allow only TLSv1.3 connections
```

즉 TLSv1.3만 허용해야 한다.

그래서 설정을 이렇게 바꿔야 한다.

```nginx
ssl_protocols TLSv1.3;
```

이 한 줄이 이 문제의 핵심이다.

---

# 4. ConfigMap 수정하기

가장 빠른 방법은 `kubectl edit`을 사용하는 것이다.

```bash
kubectl edit cm nginx-config -n nginx-static
```

이 명령어는 `nginx-static` 네임스페이스에 있는 `nginx-config` ConfigMap을 편집기로 열어준다.

열리면 `ssl_protocols` 줄을 찾는다.

기존 설정이 이런 식이라면:

```nginx
ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
```

또는 이런 식이라면:

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
```

아래처럼 수정한다.

```nginx
ssl_protocols TLSv1.3;
```

저장하고 나오면 ConfigMap 수정은 끝난다.

---

# 5. `kubectl edit`은 언제 쓸 수 있을까?

`kubectl edit`은 이미 존재하는 Kubernetes 리소스를 빠르게 수정할 때 쓴다.

예를 들어 다음 리소스들은 모두 수정할 수 있다.

```bash
kubectl edit cm nginx-config -n nginx-static
kubectl edit deploy nginx-static -n nginx-static
kubectl edit svc nginx-service -n nginx-static
kubectl edit ingress web-ingress -n nginx-static
kubectl edit secret my-secret -n nginx-static
```

다만 모든 필드가 자유롭게 수정되는 것은 아니다.

ConfigMap은 설정값을 바꾸는 리소스이기 때문에 `edit`하기 좋다.

```bash
kubectl edit cm nginx-config -n nginx-static
```

Deployment도 자주 수정한다.

```bash
kubectl edit deploy nginx-static -n nginx-static
```

예를 들어 컨테이너 이미지, 환경변수, replicas, volumeMount 등을 수정할 수 있다.

Service도 수정 가능하다.

```bash
kubectl edit svc nginx-service -n nginx-static
```

하지만 일부 필드는 변경이 제한될 수 있다. 예를 들어 Service의 `clusterIP` 같은 값은 이미 만들어진 뒤에는 직접 바꾸기 어렵다.

Pod도 `edit` 자체는 가능하지만 조심해야 한다.

```bash
kubectl edit pod my-pod
```

Pod는 이미 실행 중인 단일 실행 단위이기 때문에 많은 필드가 수정 불가능하다. 컨테이너 이미지나 volume 같은 핵심 설정을 바꾸려고 하면 막히는 경우가 많다.

그래서 보통은 Pod를 직접 수정하지 않고, 그 Pod를 만든 상위 리소스를 수정한다.

```text
Pod 직접 수정 X
Deployment 수정 O
```

이번 문제에서는 Nginx 설정이 ConfigMap에 들어 있으므로 Deployment가 아니라 ConfigMap을 수정하면 된다.

---

# 6. ConfigMap만 수정하면 바로 반영될까?

여기서 중요한 포인트가 있다.

ConfigMap을 수정했다고 해서 Nginx가 무조건 즉시 새 설정으로 동작하는 것은 아니다.

ConfigMap이 볼륨으로 마운트되어 있다면 파일 내용 자체는 시간이 지나면 Pod 안에 반영될 수 있다. 하지만 Nginx 프로세스는 설정 파일을 다시 읽어야 한다.

즉 ConfigMap 파일이 바뀌어도, Nginx가 설정을 reload하거나 Pod가 재시작되지 않으면 이전 설정으로 계속 동작할 수 있다.

그래서 문제에서 이런 말을 한 것이다.

```text
re-create, restart, or scale resources as necessary
```

필요하면 다시 만들거나, 재시작하거나, 스케일 조정하라는 뜻이다.

시험에서는 가장 간단하게 Deployment를 재시작하면 된다.

```bash
kubectl rollout restart deploy nginx-static -n nginx-static
```

그다음 정상적으로 재시작되었는지 확인한다.

```bash
kubectl rollout status deploy nginx-static -n nginx-static
```

---

# 7. `rollout`이란?

`rollout`은 Deployment 같은 워크로드 리소스의 배포 상태를 관리하는 명령어다.

Deployment를 새 버전으로 배포하거나, 재시작하거나, 롤백하거나, 배포 상태를 확인할 때 사용한다.

CKA에서 자주 쓰는 `rollout` 명령어는 다음과 같다.

---

## 7-1. rollout status

```bash
kubectl rollout status deploy nginx-static -n nginx-static
```

뜻은 다음과 같다.

```text
nginx-static Deployment의 배포가 정상 완료되었는지 확인해라.
```

정상이라면 대략 이런 메시지가 나온다.

```text
deployment "nginx-static" successfully rolled out
```

---

## 7-2. rollout restart

```bash
kubectl rollout restart deploy nginx-static -n nginx-static
```

뜻은 다음과 같다.

```text
nginx-static Deployment의 Pod들을 다시 만들어라.
```

이번 문제에서 가장 중요한 명령어다.

ConfigMap을 수정한 뒤 Nginx가 새 설정을 읽도록 하기 위해 Deployment를 재시작하는 것이다.

---

## 7-3. rollout history

```bash
kubectl rollout history deploy nginx-static -n nginx-static
```

뜻은 다음과 같다.

```text
이 Deployment의 배포 이력을 보여줘라.
```

예시는 다음과 같다.

```text
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
```

---

## 7-4. rollout undo

```bash
kubectl rollout undo deploy nginx-static -n nginx-static
```

뜻은 다음과 같다.

```text
이전 버전으로 롤백해라.
```

특정 revision으로 돌아가고 싶다면 이렇게 쓴다.

```bash
kubectl rollout undo deploy nginx-static -n nginx-static --to-revision=1
```

---

## 7-5. rollout pause

```bash
kubectl rollout pause deploy nginx-static -n nginx-static
```

뜻은 다음과 같다.

```text
Deployment 변경 반영을 잠시 멈춰라.
```

---

## 7-6. rollout resume

```bash
kubectl rollout resume deploy nginx-static -n nginx-static
```

뜻은 다음과 같다.

```text
멈춰둔 rollout을 다시 진행해라.
```

이번 문제에서는 사실상 두 개만 알면 충분하다.

```bash
kubectl rollout restart deploy nginx-static -n nginx-static
kubectl rollout status deploy nginx-static -n nginx-static
```

---

# 8. curl로 TLS 설정 테스트하기

문제에서 테스트 명령어를 줬다.

```bash
curl --tls-max 1.2 https://web.k8s.local
```

여기서 `--tls-max 1.2`의 의미가 중요하다.

`--tls-max`는 curl이 사용할 수 있는 TLS 버전의 최대치를 제한하는 옵션이다.

```bash
curl --tls-max 1.2 https://web.k8s.local
```

이 명령어는 이런 뜻이다.

```text
TLS 1.2까지만 사용해서 접속해라.
TLS 1.3은 사용하지 마라.
```

그런데 우리는 서버를 TLSv1.3만 허용하도록 바꿨다.

그러면 TLS 1.2까지만 사용하겠다는 클라이언트는 접속에 실패해야 한다.

즉 이 명령어는 실패해야 정상이다.

```bash
curl --tls-max 1.2 https://web.k8s.local
```

실패 메시지는 환경마다 다를 수 있다.

예를 들면 이런 식이다.

```text
curl: (35) OpenSSL/SSL_connect: SSL_ERROR_SYSCALL
```

또는:

```text
curl: (35) error:0A00042E:SSL routines::tlsv1 alert protocol version
```

정확한 에러 문구보다 중요한 것은 접속이 성공하면 안 된다는 것이다.

---

# 9. `-k` 옵션은 왜 붙일까?

실습 환경이나 CKA 환경에서는 HTTPS 인증서가 공인 인증서가 아니라 self-signed certificate인 경우가 많다.

그럴 때 curl을 날리면 TLS 버전 문제가 아니라 인증서 검증 문제로 먼저 실패할 수 있다.

예를 들어 이런 오류가 날 수 있다.

```text
SSL certificate problem: self-signed certificate
```

이 경우에는 `-k` 옵션을 붙인다.

```bash
curl -k https://web.k8s.local
```

`-k`는 인증서 검증을 무시하겠다는 뜻이다.

긴 옵션은 다음과 같다.

```bash
--insecure
```

즉 이 명령어는:

```bash
curl -k --tls-max 1.2 https://web.k8s.local
```

이런 의미다.

```text
인증서 검증은 무시하고,
TLS는 최대 1.2까지만 사용해서 접속해라.
```

이번 문제에서는 TLSv1.3만 허용해야 하므로 이 명령어는 실패해야 한다.

```bash
curl -k --tls-max 1.2 https://web.k8s.local
```

반대로 TLSv1.3으로 접속하면 성공해야 한다.

```bash
curl -k --tlsv1.3 https://web.k8s.local
```

정리하면 다음과 같다.

```text
TLS 1.2 이하 접속 테스트
→ 실패해야 정상

TLS 1.3 접속 테스트
→ 성공해야 정상
```

---

# 10. 전체 풀이 흐름

시험장에서 실제로 푸는 흐름은 다음과 같다.

먼저 리소스를 확인한다.

```bash
kubectl get deploy -n nginx-static
kubectl get cm -n nginx-static
```

ConfigMap 내용을 확인한다.

```bash
kubectl get cm nginx-config -n nginx-static -o yaml
```

ConfigMap을 수정한다.

```bash
kubectl edit cm nginx-config -n nginx-static
```

Nginx 설정에서 `ssl_protocols` 줄을 찾고 아래처럼 수정한다.

```nginx
ssl_protocols TLSv1.3;
```

수정 후 Deployment를 재시작한다.

```bash
kubectl rollout restart deploy nginx-static -n nginx-static
```

재시작 상태를 확인한다.

```bash
kubectl rollout status deploy nginx-static -n nginx-static
```

Pod 상태도 확인할 수 있다.

```bash
kubectl get pod -n nginx-static
```

이제 TLS 1.2 이하 접속이 막히는지 확인한다.

```bash
curl -k --tls-max 1.2 https://web.k8s.local
```

이 명령어는 실패해야 한다.

TLSv1.3 접속은 성공하는지 확인한다.

```bash
curl -k --tlsv1.3 https://web.k8s.local
```

이 명령어는 성공해야 한다.

---

# 11. 이 문제에서 나온 옵션 정리

마지막으로 문제에 나온 명령어와 옵션들을 정리하면 다음과 같다.

| 명령어/옵션               | 의미                       |
| -------------------- | ------------------------ |
| `cm`                 | ConfigMap의 줄임말           |
| `-n`                 | namespace 지정             |
| `-o`                 | 출력 형식 지정                 |
| `kubectl edit`       | 기존 Kubernetes 리소스를 직접 수정 |
| `rollout restart`    | Deployment의 Pod 재시작      |
| `rollout status`     | Deployment 배포 상태 확인      |
| `rollout history`    | 배포 이력 확인                 |
| `rollout undo`       | 이전 버전으로 롤백               |
| `curl --tls-max 1.2` | TLS 최대 버전을 1.2로 제한해서 접속  |
| `curl -k`            | HTTPS 인증서 검증 무시          |
| `curl --tlsv1.3`     | TLSv1.3으로 접속 시도          |

---

# 12. 최종 정답 명령어

최종적으로 정답 흐름만 압축하면 다음과 같다.

```bash
kubectl get cm nginx-config -n nginx-static -o yaml
kubectl edit cm nginx-config -n nginx-static
```

ConfigMap 안의 Nginx 설정을 수정한다.

```nginx
ssl_protocols TLSv1.3;
```

Deployment를 재시작한다.

```bash
kubectl rollout restart deploy nginx-static -n nginx-static
kubectl rollout status deploy nginx-static -n nginx-static
```

TLS 1.2 이하 접속이 실패하는지 확인한다.

```bash
curl -k --tls-max 1.2 https://web.k8s.local
```

TLS 1.3 접속이 성공하는지 확인한다.

```bash
curl -k --tlsv1.3 https://web.k8s.local
```

---

# 마무리

이 문제는 단순히 ConfigMap을 수정하는 문제가 아니다. 정확히는 Kubernetes의 ConfigMap이 애플리케이션 설정을 관리하고, 그 설정을 Nginx가 읽고 있으며, 설정 변경 후에는 Pod나 Deployment를 재시작해야 할 수 있다는 흐름을 묻는 문제다.

핵심은 다음 세 가지다.

```text
1. nginx-config ConfigMap 안에서 ssl_protocols 설정을 찾는다.
2. ssl_protocols TLSv1.3; 으로 수정한다.
3. Deployment를 재시작하고 curl로 TLS 1.2 접속이 실패하는지 확인한다.
```

정답의 핵심 한 줄은 이것이다.

```nginx
ssl_protocols TLSv1.3;
```

검증의 핵심 명령어는 이것이다.

```bash
curl -k --tls-max 1.2 https://web.k8s.local
```

이 명령어가 실패해야 TLSv1.2 이하가 차단된 것이고, TLSv1.3만 허용되도록 설정이 제대로 반영된 것이다.
