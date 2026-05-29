---
title: "[Kubernetes] ConfigMap이란? 설정값을 컨테이너 밖으로 빼내는 방법"
source: "https://velog.io/@yorange50/Kubernetes-ConfigMap이란-설정값을-컨테이너-밖으로-빼내는-방법"
published: "2026-05-20T06:19:27.366Z"
tags: ""
backup_date: "2026-05-29T14:52:52.717837"
---

Kubernetes를 공부하다 보면 `ConfigMap`이라는 리소스가 자주 나온다.

처음에는 이름부터 헷갈린다.

```text
ConfigMap?
설정 지도?
설정 파일?
환경변수?
```

대충 이런 느낌인데, 쉽게 말하면 ConfigMap은 **애플리케이션 설정값을 Pod 밖에서 관리하게 해주는 Kubernetes 리소스**다.

공식 문서에서도 ConfigMap은 다른 오브젝트가 사용할 설정 정보를 저장하는 API 오브젝트라고 설명한다. ConfigMap은 일반적인 Kubernetes 리소스처럼 `spec` 중심이 아니라, `data`와 `binaryData` 필드에 key-value 형태로 데이터를 저장한다. ([Kubernetes][1])

---

## 1. ConfigMap이 왜 필요할까?

예를 들어 Spring Boot 애플리케이션이 있다고 해보자.

개발 환경에서는 DB 주소가 이럴 수 있다.

```text
localhost:3306
```

운영 환경에서는 DB 주소가 다를 수 있다.

```text
prod-db.example.com:3306
```

만약 이 값을 코드 안에 박아두면 어떻게 될까?

```java
String dbUrl = "localhost:3306";
```

운영 환경으로 갈 때 코드를 수정해야 한다.

문제는 여기서 끝나지 않는다.

```text
개발 환경 설정
테스트 환경 설정
운영 환경 설정
로그 레벨
외부 API 주소
Nginx 설정
feature flag
```

이런 값들이 전부 코드 안에 들어가 있으면, 설정 하나 바꿀 때마다 이미지를 다시 빌드해야 한다.

```text
설정 변경
→ 코드 수정
→ 이미지 빌드
→ 이미지 푸시
→ 다시 배포
```

너무 번거롭다.

그래서 설정값을 애플리케이션 코드나 컨테이너 이미지에서 분리한다.

이때 사용하는 것이 ConfigMap이다.

공식 문서에서도 ConfigMap을 사용하는 이유를 컨테이너 이미지 내용과 설정 정보를 분리해서 애플리케이션을 더 이식 가능하게 만들기 위함이라고 설명한다. ([Kubernetes][2])

---

## 2. ConfigMap을 한 문장으로 말하면

```text
ConfigMap은 Pod가 사용할 설정값을 Kubernetes 안에 따로 저장해두는 리소스다.
```

조금 더 쉽게 말하면 이렇다.

```text
코드에 박아두기 애매한 설정값을 Kubernetes에 따로 저장해두는 상자
```

예를 들면 이런 값들이 ConfigMap에 들어갈 수 있다.

```text
LOG_LEVEL=DEBUG
APP_MODE=dev
API_URL=http://api-service:8080
nginx.conf
application.yml
```

즉 ConfigMap은 단순한 환경변수 저장소처럼 쓸 수도 있고, 설정 파일 자체를 담는 용도로도 쓸 수 있다.

---

## 3. ConfigMap 기본 YAML 구조

ConfigMap은 보통 이렇게 생겼다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_MODE: dev
  LOG_LEVEL: debug
```

구조를 보면 어렵지 않다.

```text
apiVersion: v1
kind: ConfigMap
metadata: ConfigMap 이름 정보
data: 실제 설정값
```

핵심은 `data`다.

`data` 안에는 key-value 형태로 설정값이 들어간다.

```yaml
data:
  APP_MODE: dev
  LOG_LEVEL: debug
```

이건 이렇게 이해하면 된다.

```text
APP_MODE라는 이름의 설정값은 dev
LOG_LEVEL이라는 이름의 설정값은 debug
```

---

## 4. ConfigMap은 네임스페이스 리소스다

ConfigMap은 네임스페이스 안에 존재한다.

예를 들어 `nginx-static` 네임스페이스 안에 `nginx-config`라는 ConfigMap이 있을 수 있다.

```bash
kubectl get cm -n nginx-static
```

또는 전체 이름으로 쓸 수도 있다.

```bash
kubectl get configmap -n nginx-static
```

여기서 `cm`은 `configmap`의 축약형이다.

```text
cm = configmap
```

특정 ConfigMap을 확인하려면 다음처럼 쓴다.

```bash
kubectl get cm nginx-config -n nginx-static
```

내용까지 자세히 보고 싶으면 `describe`를 쓴다.

```bash
kubectl describe cm nginx-config -n nginx-static
```

YAML 형태로 보고 싶으면 이렇게 한다.

```bash
kubectl get cm nginx-config -n nginx-static -o yaml
```

---

## 5. ConfigMap을 Pod에서 쓰는 방법

ConfigMap은 만들어두기만 하면 의미가 없다.

Pod가 그 ConfigMap을 가져다 써야 한다.

대표적인 방식은 두 가지다.

```text
환경변수로 주입하기
파일처럼 마운트하기
```

---

## 6. 방법 1: 환경변수로 사용하기

ConfigMap이 이렇게 있다고 해보자.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_MODE: dev
  LOG_LEVEL: debug
```

Pod에서는 이 값을 환경변수로 가져올 수 있다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
    - name: app
      image: nginx
      env:
        - name: APP_MODE
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: APP_MODE
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: LOG_LEVEL
```

이렇게 하면 컨테이너 안에서는 환경변수처럼 사용할 수 있다.

```bash
echo $APP_MODE
echo $LOG_LEVEL
```

즉 ConfigMap의 값을 컨테이너 내부 환경변수로 넣어주는 방식이다.

이 방식은 이런 설정에 적합하다.

```text
로그 레벨
실행 모드
간단한 URL
간단한 옵션값
```

---

## 7. 방법 2: 파일처럼 마운트하기

ConfigMap은 파일처럼 Pod 안에 넣을 수도 있다.

예를 들어 Nginx 설정 파일을 ConfigMap에 담을 수 있다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  nginx.conf: |
    server {
        listen 80;
        location / {
            return 200 "hello nginx";
        }
    }
```

여기서 `nginx.conf`가 key이고, 그 아래 내용이 value다.

이걸 Pod에 볼륨으로 마운트하면 컨테이너 안에서 실제 파일처럼 보인다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
    - name: nginx
      image: nginx
      volumeMounts:
        - name: config-volume
          mountPath: /etc/nginx/conf.d
  volumes:
    - name: config-volume
      configMap:
        name: nginx-config
```

그러면 ConfigMap 안에 있던 설정이 컨테이너 내부 경로에 파일로 들어간다.

```text
/etc/nginx/conf.d/nginx.conf
```

이 방식은 이런 설정에 자주 쓰인다.

```text
nginx.conf
application.yml
prometheus.yml
설정 파일 전체
```

---

## 8. ConfigMap 수정하기

이미 존재하는 ConfigMap을 수정하려면 `edit`을 쓸 수 있다.

```bash
kubectl edit cm nginx-config -n nginx-static
```

그러면 클러스터 안에 있는 ConfigMap YAML이 열린다.

예를 들어 Nginx 설정이 이런 식으로 들어 있을 수 있다.

```yaml
data:
  nginx.conf: |
    server {
        listen 443 ssl;
        ssl_protocols TLSv1.2 TLSv1.3;
    }
```

TLSv1.3만 허용해야 한다면 이렇게 바꾼다.

```yaml
data:
  nginx.conf: |
    server {
        listen 443 ssl;
        ssl_protocols TLSv1.3;
    }
```

수정 후 저장하면 ConfigMap 자체는 변경된다.

---

## 9. ConfigMap을 수정하면 Pod에 바로 반영될까?

여기서 중요한 포인트가 있다.

```text
ConfigMap을 수정했다고 해서 애플리케이션이 무조건 즉시 새 설정을 읽는 것은 아니다.
```

특히 환경변수로 주입한 ConfigMap 값은 Pod가 시작될 때 들어간다.

즉 이미 실행 중인 Pod의 환경변수가 자동으로 바뀌지 않는다.

그래서 ConfigMap을 수정한 뒤에는 Pod를 다시 띄워야 하는 경우가 많다.

Deployment가 관리하는 Pod라면 보통 이렇게 한다.

```bash
kubectl rollout restart deploy nginx-static -n nginx-static
```

이 명령어는 Deployment가 관리하는 Pod를 다시 생성하게 한다.

```text
ConfigMap 수정
→ Deployment rollout restart
→ 새 Pod 생성
→ 새 Pod가 수정된 ConfigMap을 읽음
```

시험에서는 이 흐름을 정말 많이 쓴다.

---

## 10. ConfigMap과 Secret 차이

ConfigMap과 비슷하게 생긴 리소스로 Secret이 있다.

둘 다 설정값을 저장할 수 있다.

하지만 용도가 다르다.

```text
ConfigMap: 일반 설정값 저장
Secret: 민감한 값 저장
```

ConfigMap에 넣어도 되는 예시는 다음과 같다.

```text
LOG_LEVEL=debug
APP_MODE=prod
API_URL=http://api-service
nginx.conf
```

Secret에 넣어야 하는 예시는 다음과 같다.

```text
DB_PASSWORD
API_KEY
TOKEN
인증서 private key
```

즉 비밀번호나 토큰 같은 민감한 값은 ConfigMap에 넣으면 안 된다.

---

## 11. ConfigMap 생성 명령어

ConfigMap은 YAML로 만들 수도 있고, 명령어로 바로 만들 수도 있다.

간단한 key-value 형태라면 이렇게 만들 수 있다.

```bash
kubectl create configmap app-config \
  --from-literal=APP_MODE=dev \
  --from-literal=LOG_LEVEL=debug
```

파일을 ConfigMap으로 만들 수도 있다.

```bash
kubectl create configmap nginx-config \
  --from-file=nginx.conf
```

네임스페이스를 지정하려면 `-n`을 붙인다.

```bash
kubectl create configmap nginx-config \
  --from-file=nginx.conf \
  -n nginx-static
```

YAML로 보고 싶으면 `--dry-run=client -o yaml`을 붙여서 뼈대를 만들 수도 있다.

```bash
kubectl create configmap app-config \
  --from-literal=APP_MODE=dev \
  --dry-run=client -o yaml
```

이렇게 하면 실제로 만들지는 않고 YAML만 출력한다.

---

## 12. CKA에서 ConfigMap 문제를 만났을 때 흐름

CKA에서는 ConfigMap 문제가 이런 식으로 나온다.

```text
어떤 Deployment가 ConfigMap을 사용 중이다
ConfigMap을 수정해라
필요하면 Pod를 재시작해라
명령어로 테스트해라
```

이때 흐름은 거의 고정이다.

```bash
kubectl get cm -n <namespace>
```

```bash
kubectl get deploy,pod -n <namespace>
```

```bash
kubectl edit cm <configmap-name> -n <namespace>
```

```bash
kubectl rollout restart deploy <deployment-name> -n <namespace>
```

```bash
kubectl rollout status deploy <deployment-name> -n <namespace>
```

```bash
kubectl get pod -n <namespace>
```

즉 ConfigMap 문제는 이렇게 외우면 된다.

```text
찾고
수정하고
재시작하고
확인한다
```

---

## 13. Nginx 문제에 대입해보기

예를 들어 문제에서 이렇게 나왔다고 하자.

```text
Deployment: nginx-static
Namespace: nginx-static
ConfigMap: nginx-config
TLSv1.3만 허용
```

그러면 명령어 흐름은 다음과 같다.

```bash
kubectl get deploy,pod,cm -n nginx-static
```

ConfigMap 수정.

```bash
kubectl edit cm nginx-config -n nginx-static
```

안에서 Nginx 설정을 찾는다.

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
```

이렇게 바꾼다.

```nginx
ssl_protocols TLSv1.3;
```

Deployment 재시작.

```bash
kubectl rollout restart deploy nginx-static -n nginx-static
```

상태 확인.

```bash
kubectl rollout status deploy nginx-static -n nginx-static
```

Pod 확인.

```bash
kubectl get pod -n nginx-static
```

테스트.

```bash
curl --tls-max 1.2 https://web.k8s.local
```

TLSv1.3만 허용했다면 TLSv1.2까지만 쓰겠다는 요청은 실패해야 한다.

---

## 14. ConfigMap을 공부할 때 헷갈리는 지점

처음에는 이런 부분이 헷갈린다.

```text
ConfigMap은 Pod인가? 아니다
ConfigMap은 파일인가? 파일처럼 쓸 수는 있지만 리소스다
ConfigMap은 Secret이랑 같은가? 아니다
ConfigMap 수정하면 바로 반영되나? 경우에 따라 다르다
```

정리하면 이렇다.

```text
ConfigMap은 설정값 저장소
Pod는 ConfigMap을 가져다 씀
환경변수로 쓸 수도 있음
파일처럼 마운트할 수도 있음
민감한 값은 ConfigMap이 아니라 Secret에 넣어야 함
ConfigMap 수정 후 Pod 재시작이 필요할 수 있음
```

---

## 15. 한 줄 요약

```text
ConfigMap은 애플리케이션 설정값을 컨테이너 이미지 밖에서 관리하게 해주는 Kubernetes 리소스다.
```

조금 더 실전적으로 말하면 이렇게 기억하면 된다.

```text
코드나 이미지에 박기 싫은 설정값을 Kubernetes에 따로 저장하고, Pod가 환경변수나 파일 형태로 가져다 쓰게 하는 것
```

CKA에서는 ConfigMap을 만나면 이 흐름을 떠올리면 된다.

```text
ConfigMap 확인
→ ConfigMap 수정
→ 사용하는 Pod 또는 Deployment 재시작
→ 동작 확인
```

[1]: https://kubernetes.io/docs/concepts/configuration/configmap/?utm_source=chatgpt.com "ConfigMaps"
[2]: https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/?utm_source=chatgpt.com "Configure a Pod to Use a ConfigMap"
