---
title: "[Kubernetes] base64는 왜 계속 나올까?"
source: ""
published: "2026-05-29T17:33:55.000Z"
---

쿠버네티스를 공부하다 보면 은근히 자주 보이는 게 있다.

```bash
base64
```

처음 보면 암호화처럼 느껴진다.

특히 Secret을 다룰 때 이런 값이 나온다.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  username: YWRtaW4=
  password: cGFzc3dvcmQ=
```

여기서 `YWRtaW4=`나 `cGFzc3dvcmQ=` 같은 값이 바로 base64로 인코딩된 값이다.

그런데 중요한 점이 있다.

> base64는 암호화가 아니다.

base64는 데이터를 숨기기 위한 기술이 아니라, **데이터를 안전하게 문자 형태로 표현하기 위한 인코딩 방식**이다.

---

## 1. base64란?

base64는 데이터를 문자로 바꿔주는 인코딩 방식이다.

예를 들어 `admin`이라는 문자열이 있다고 해보자.

```text
admin
```

이걸 base64로 바꾸면 이렇게 된다.

```text
YWRtaW4=
```

`password`는 이렇게 바뀐다.

```text
password
```

```text
cGFzc3dvcmQ=
```

즉, base64는 이런 역할을 한다.

```text
원본 데이터 → 문자 형태로 변환
```

반대로 다시 원래대로 되돌릴 수도 있다.

```text
base64 문자열 → 원본 데이터
```

그래서 base64는 **양방향 변환이 가능**하다.

---

## 2. 왜 굳이 base64로 바꿀까?

컴퓨터 데이터는 항상 사람이 읽을 수 있는 문자만 있는 게 아니다.

파일, 이미지, 인증서, 키 파일, 바이너리 데이터처럼 여러 종류의 데이터가 있다.

그런데 이런 데이터를 JSON, YAML, HTTP, 환경변수 같은 곳에 넣으려면 문제가 생긴다.

```text
줄바꿈이 깨질 수 있음
특수문자가 이상하게 해석될 수 있음
바이너리 데이터는 텍스트 파일에 그대로 넣기 어려움
전송 중에 데이터가 손상될 수 있음
```

그래서 데이터를 안전하게 문자 형태로 바꿔서 저장하거나 전송한다.

이때 많이 사용하는 방식이 base64다.

```text
복잡한 데이터
        ↓
base64 인코딩
        ↓
문자로 안전하게 저장
```

---

## 3. base64는 암호화가 아니다

이 부분이 제일 중요하다.

base64로 바꾸면 겉으로는 이상한 문자열처럼 보인다.

```text
cGFzc3dvcmQ=
```

그래서 처음에는 비밀번호가 숨겨진 것처럼 느껴진다.

하지만 이건 그냥 다시 되돌릴 수 있다.

```bash
echo "cGFzc3dvcmQ=" | base64 -d
```

결과는 다음과 같다.

```text
password
```

즉, 누구나 디코딩할 수 있다.

정리하면 이렇다.

| 구분  | 의미               | 다시 원본 확인 가능? |
| --- | ---------------- | ------------ |
| 인코딩 | 데이터 표현 방식 변경     | 가능           |
| 암호화 | 키를 사용해서 데이터를 숨김  | 키가 있어야 가능    |
| 해싱  | 원본을 고정 길이 값으로 변환 | 원칙적으로 복구 불가  |

base64는 이 중에서 **인코딩**이다.

```text
base64 = 숨기는 기술 X
base64 = 표현 방식을 바꾸는 기술 O
```

---

## 4. 쿠버네티스에서 base64가 나오는 이유

쿠버네티스에서 base64가 가장 자주 나오는 곳은 `Secret`이다.

Secret은 비밀번호, 토큰, 인증서 같은 민감한 값을 저장할 때 사용하는 리소스다.

예를 들어 이런 값이 있다고 해보자.

```text
username: admin
password: password
```

이걸 Secret에 넣으려면 `data` 필드에서는 base64로 인코딩해야 한다.

```bash
echo -n "admin" | base64
```

결과는 다음과 같다.

```text
YWRtaW4=
```

```bash
echo -n "password" | base64
```

결과는 다음과 같다.

```text
cGFzc3dvcmQ=
```

그래서 Secret YAML은 이렇게 작성된다.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  username: YWRtaW4=
  password: cGFzc3dvcmQ=
```

여기서 중요한 건 `data` 아래 값은 base64여야 한다는 점이다.

---

## 5. echo -n을 쓰는 이유

base64 인코딩할 때 자주 이런 명령어를 본다.

```bash
echo -n "password" | base64
```

여기서 `-n`이 중요하다.

`echo`는 기본적으로 문자열 뒤에 줄바꿈을 붙인다.

```bash
echo "password"
```

이건 실제로는 아래처럼 들어간다.

```text
password\n
```

즉, 줄바꿈 문자까지 포함될 수 있다.

반면 `echo -n`은 줄바꿈을 붙이지 않는다.

```bash
echo -n "password"
```

이건 딱 아래 값만 사용한다.

```text
password
```

그래서 Secret 값을 만들 때는 보통 `echo -n`을 쓴다.

```text
echo "password"    → password + 줄바꿈까지 인코딩될 수 있음
echo -n "password" → password만 인코딩
```

이 차이 때문에 디코딩했을 때 값이 미묘하게 달라질 수 있다.

---

## 6. base64 인코딩하기

문자열을 base64로 인코딩하는 명령어는 다음과 같다.

```bash
echo -n "admin" | base64
```

결과는 다음과 같다.

```text
YWRtaW4=
```

비밀번호도 인코딩해보자.

```bash
echo -n "password" | base64
```

결과는 다음과 같다.

```text
cGFzc3dvcmQ=
```

파일을 base64로 인코딩할 수도 있다.

```bash
base64 cert.pem
```

또는 결과를 파일로 저장할 수도 있다.

```bash
base64 cert.pem > cert.pem.base64
```

---

## 7. base64 디코딩하기

base64 값을 다시 원래 값으로 확인하려면 디코딩하면 된다.

```bash
echo "YWRtaW4=" | base64 -d
```

결과는 다음과 같다.

```text
admin
```

비밀번호도 확인해보자.

```bash
echo "cGFzc3dvcmQ=" | base64 -d
```

결과는 다음과 같다.

```text
password
```

macOS에서는 환경에 따라 `-D` 옵션을 쓰는 경우도 있다.

```bash
echo "cGFzc3dvcmQ=" | base64 -D
```

하지만 대부분의 Linux 환경에서는 `-d`를 사용한다.

---

## 8. Secret 만들 때 더 쉬운 방법

사실 Secret을 만들 때 매번 base64로 직접 바꾸는 건 귀찮다.

이럴 때는 `kubectl create secret` 명령어를 사용할 수 있다.

```bash
kubectl create secret generic my-secret \
  --from-literal=username=admin \
  --from-literal=password=password
```

이렇게 만들면 쿠버네티스가 알아서 Secret을 생성해준다.

생성된 Secret을 YAML로 보면 값이 base64로 들어가 있다.

```bash
kubectl get secret my-secret -o yaml
```

예상 형태는 이런 식이다.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  username: YWRtaW4=
  password: cGFzc3dvcmQ=
```

즉, 직접 base64로 바꿔도 되고, `kubectl create secret`을 써도 된다.

---

## 9. stringData를 쓰면 더 편하다

Secret YAML을 직접 작성할 때 `data` 대신 `stringData`를 사용할 수도 있다.

`stringData`는 사람이 읽을 수 있는 문자열을 그대로 넣을 수 있다.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
stringData:
  username: admin
  password: password
```

이렇게 작성하면 쿠버네티스가 내부적으로 알아서 base64로 변환해서 저장한다.

그래서 처음 공부할 때는 `stringData`가 더 이해하기 쉽다.

차이는 이렇게 보면 된다.

| 필드         | 값 형태          |
| ---------- | ------------- |
| data       | base64 인코딩된 값 |
| stringData | 일반 문자열        |

예를 들어 아래 둘은 비슷한 의미다.

```yaml
data:
  password: cGFzc3dvcmQ=
```

```yaml
stringData:
  password: password
```

다만 실제로 저장된 Secret을 조회하면 결국 `data` 형태의 base64 값으로 보인다.

---

## 10. Secret은 안전한가?

Secret이라는 이름 때문에 완전히 안전할 것 같지만, 주의해야 한다.

Secret의 값은 base64로 표현될 뿐이다.

즉, 아래처럼 쉽게 확인할 수 있다.

```bash
kubectl get secret my-secret -o yaml
```

```yaml
data:
  password: cGFzc3dvcmQ=
```

그리고 디코딩하면 원본이 나온다.

```bash
echo "cGFzc3dvcmQ=" | base64 -d
```

```text
password
```

그래서 Secret을 안전하게 쓰려면 RBAC가 중요하다.

```text
누가 Secret을 조회할 수 있는지 제한해야 함
```

예를 들어 아무 사용자나 Secret을 조회할 수 있으면 base64 디코딩으로 비밀번호를 바로 볼 수 있다.

```text
Secret 보안의 핵심
= base64가 아니라 접근 권한 제어
```

운영 환경에서는 추가로 이런 것도 고려한다.

```text
etcd encryption
RBAC 최소 권한
Secret 접근 로그 관리
External Secrets 사용
Vault 같은 외부 Secret Manager 연동
```

---

## 11. 쿠버네티스에서 자주 보는 예시

### 11.1 Docker registry 인증 정보

Private Docker Registry에 접근할 때 imagePullSecret을 사용한다.

```bash
kubectl create secret docker-registry regcred \
  --docker-server=<registry-server> \
  --docker-username=<username> \
  --docker-password=<password> \
  --docker-email=<email>
```

이 Secret도 내부적으로 인증 정보를 base64 형태로 저장한다.

Pod에서는 이렇게 사용한다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: private-app
spec:
  imagePullSecrets:
    - name: regcred
  containers:
    - name: app
      image: private-registry.example.com/app:1.0
```

이 구조는 이렇게 보면 된다.

```text
Private Registry 인증 정보
        ↓
Secret으로 저장
        ↓
Pod의 imagePullSecrets에서 참조
        ↓
이미지 pull 가능
```

---

### 11.2 TLS 인증서 Secret

Ingress에서 HTTPS를 붙일 때 TLS Secret을 사용한다.

```bash
kubectl create secret tls my-tls-secret \
  --cert=tls.crt \
  --key=tls.key
```

이 Secret 안에는 인증서와 개인키가 저장된다.

조회해보면 대략 이런 형태다.

```yaml
data:
  tls.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0t...
  tls.key: LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0t...
```

인증서와 키 파일도 결국 텍스트나 바이너리 데이터이기 때문에 Secret 안에서는 base64 형태로 표현된다.

---

## 12. 자주 하는 실수

### 12.1 base64를 암호화라고 생각하기

가장 흔한 실수다.

```text
base64로 되어 있으니까 안전하겠지
```

아니다.

base64는 누구나 디코딩할 수 있다.

```bash
echo "YWRtaW4=" | base64 -d
```

```text
admin
```

---

### 12.2 echo -n 없이 인코딩하기

```bash
echo "password" | base64
```

이렇게 하면 줄바꿈까지 포함될 수 있다.

그래서 Secret 값이 예상과 다르게 들어갈 수 있다.

보통은 이렇게 쓴다.

```bash
echo -n "password" | base64
```

---

### 12.3 Secret을 GitHub에 올리기

Secret YAML에 base64 값이 들어있다고 해서 안전한 게 아니다.

```yaml
data:
  password: cGFzc3dvcmQ=
```

이걸 GitHub에 올리면 사실상 비밀번호를 올린 것과 비슷하다.

왜냐하면 바로 디코딩할 수 있기 때문이다.

```text
base64 Secret을 GitHub에 올리는 것
= 비밀번호를 살짝 모양만 바꿔서 올리는 것
```

실무에서는 Secret을 Git에 직접 올리지 않도록 조심해야 한다.

---

## 13. 정리

base64는 데이터를 문자 형태로 안전하게 표현하기 위한 인코딩 방식이다.

쿠버네티스에서는 Secret의 `data` 필드에서 자주 사용된다.

```text
원본 문자열
        ↓
base64 인코딩
        ↓
Secret data에 저장
```

하지만 base64는 보안 기능이 아니다.

```text
base64 = 인코딩
base64 ≠ 암호화
```

쿠버네티스 Secret을 안전하게 쓰려면 base64 자체보다 접근 권한 관리가 중요하다.

```text
Secret을 누가 조회할 수 있는지
Secret을 Git에 올리지 않는지
운영 환경에서 etcd 암호화를 적용하는지
외부 Secret Manager를 쓰는지
```

마지막으로 이렇게 기억하면 된다.

> base64는 데이터를 숨기는 기술이 아니라, 데이터를 깨지지 않게 문자로 표현하는 기술이다. 쿠버네티스 Secret은 base64로 보이지만, 진짜 보안은 RBAC와 Secret 관리 방식에서 나온다.
