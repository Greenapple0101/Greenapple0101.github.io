---
title: "[Linux] systemctl이 뭐길래 서버에서 계속 나올까?"
source: "https://velog.io/@yorange50/Linux-systemctl이-뭐길래-서버에서-계속-나올까"
published: "2026-05-22T03:35:07.697Z"
tags: ""
backup_date: "2026-05-29T14:52:52.716253"
---

리눅스 서버를 만지다 보면 이런 명령어를 자주 보게 된다.

```bash
systemctl status nginx
systemctl restart docker
systemctl status kubelet
```

처음 보면 `systemctl`이 뭔가 싶다.

쿠버네티스 공부할 때도 나오고, Docker 설치할 때도 나오고, Nginx 설정할 때도 나온다.

결론부터 말하면 `systemctl`은 **리눅스에서 서비스를 관리하는 명령어**다.

---

## systemctl이란?

`systemctl`은 `systemd`를 조작하는 명령어다.

여기서 `systemd`는 리눅스 시스템에서 여러 서비스를 관리하는 프로그램이다.

쉽게 말하면:

```text
systemd = 리눅스 서비스 관리자
systemctl = 그 관리자에게 명령을 내리는 도구
```

라고 보면 된다.

---

## 서비스가 뭐야?

서버에서는 여러 프로그램이 백그라운드에서 계속 실행된다.

예를 들면:

```text
nginx
docker
containerd
kubelet
mysql
ssh
```

이런 것들이다.

사용자가 직접 실행하지 않아도 서버가 켜지면 자동으로 실행되거나, 계속 뒤에서 떠 있어야 하는 프로그램들이 있다.

이런 프로그램들을 보통 **서비스**라고 부른다.

---

## systemctl은 뭘 할 수 있을까?

`systemctl`로 서비스의 상태를 확인하거나, 시작하거나, 중지하거나, 재시작할 수 있다.

대표 명령어는 다음과 같다.

| 명령어                      | 의미            |
| ------------------------ | ------------- |
| `systemctl status 서비스명`  | 서비스 상태 확인     |
| `systemctl start 서비스명`   | 서비스 시작        |
| `systemctl stop 서비스명`    | 서비스 중지        |
| `systemctl restart 서비스명` | 서비스 재시작       |
| `systemctl enable 서비스명`  | 서버 부팅 시 자동 실행 |
| `systemctl disable 서비스명` | 자동 실행 해제      |

---

## 예시 1. nginx 상태 확인하기

```bash
systemctl status nginx
```

이 명령어는 Nginx가 현재 실행 중인지 확인한다.

결과에서 중요한 부분은 보통 이거다.

```text
Active: active (running)
```

이렇게 나오면 Nginx가 정상 실행 중이라는 뜻이다.

반대로 이런 식으로 나오면 문제가 있는 상태다.

```text
Active: inactive
Active: failed
```

---

## 예시 2. nginx 재시작하기

Nginx 설정 파일을 수정한 뒤에는 보통 서비스를 다시 시작해야 한다.

```bash
systemctl restart nginx
```

이 명령어는 Nginx를 껐다가 다시 켠다.

설정 파일을 바꿨는데 적용이 안 되는 것처럼 보이면, 재시작을 안 했을 가능성이 있다.

---

## 예시 3. Docker 상태 확인하기

Docker도 리눅스에서는 서비스로 동작한다.

```bash
systemctl status docker
```

Docker가 제대로 떠 있으면 컨테이너를 실행할 수 있다.

만약 Docker가 죽어 있으면:

```bash
systemctl start docker
```

로 다시 시작할 수 있다.

---

## 쿠버네티스에서 systemctl이 중요한 이유

쿠버네티스 노드에서는 `kubelet`이라는 중요한 서비스가 실행된다.

`kubelet`은 각 노드에서 Pod를 실제로 관리하는 역할을 한다.

그래서 노드에 문제가 생겼을 때 이런 명령어를 많이 쓴다.

```bash
systemctl status kubelet
```

kubelet이 정상인지 확인하는 명령어다.

만약 kubelet이 꼬였거나 설정을 바꿨다면:

```bash
systemctl restart kubelet
```

로 재시작할 수 있다.

즉, 쿠버네티스가 잘 안 될 때도 결국 리눅스 서비스 상태를 봐야 하는 경우가 많다.

---

## enable과 start의 차이

여기서 헷갈리는 게 있다.

```bash
systemctl start nginx
systemctl enable nginx
```

둘 다 실행과 관련 있어 보이지만 의미가 다르다.

`start`는 **지금 당장 실행**이다.

```bash
systemctl start nginx
```

현재 Nginx를 켠다.

반면 `enable`은 **서버가 재부팅될 때 자동으로 실행되게 등록**하는 것이다.

```bash
systemctl enable nginx
```

즉, 지금 실행한다는 뜻이 아니라 앞으로 서버가 켜질 때 자동으로 켜지게 만드는 것이다.

둘을 같이 쓰는 경우도 많다.

```bash
systemctl enable nginx
systemctl start nginx
```

의미는:

```text
앞으로 부팅 시 자동 실행되게 하고,
지금도 바로 실행해라
```

이다.

---

## status에서 자주 보는 표현

`systemctl status`를 보면 여러 상태가 나온다.

자주 보는 것만 정리하면 다음과 같다.

| 상태                 | 의미             |
| ------------------ | -------------- |
| `active (running)` | 정상 실행 중        |
| `inactive`         | 꺼져 있음          |
| `failed`           | 실행 실패          |
| `enabled`          | 부팅 시 자동 실행 설정됨 |
| `disabled`         | 자동 실행 설정 안 됨   |

예를 들어:

```text
Active: active (running)
Loaded: loaded (...; enabled; ...)
```

이런 식이면:

```text
현재 실행 중이고,
부팅 시 자동 실행도 설정되어 있음
```

이라는 뜻이다.

---

## 로그는 journalctl로 본다

`systemctl status`만으로 부족할 때가 있다.

그럴 때는 `journalctl`을 같이 쓴다.

예를 들어 kubelet 로그를 보고 싶으면:

```bash
journalctl -u kubelet
```

최근 로그만 보고 싶으면:

```bash
journalctl -u kubelet -f
```

여기서 `-f`는 로그를 실시간으로 따라가면서 보겠다는 뜻이다.

정리하면:

```text
systemctl = 서비스 상태와 실행 제어
journalctl = 서비스 로그 확인
```

이다.

이 둘은 서버 운영할 때 거의 세트처럼 같이 나온다.

---

## 자주 쓰는 명령어 모음

```bash
# 서비스 상태 확인
systemctl status nginx

# 서비스 시작
systemctl start nginx

# 서비스 중지
systemctl stop nginx

# 서비스 재시작
systemctl restart nginx

# 부팅 시 자동 실행 설정
systemctl enable nginx

# 부팅 시 자동 실행 해제
systemctl disable nginx

# kubelet 상태 확인
systemctl status kubelet

# kubelet 재시작
systemctl restart kubelet

# kubelet 로그 확인
journalctl -u kubelet

# kubelet 로그 실시간 확인
journalctl -u kubelet -f
```

---

## 한 줄 정리

`systemctl`은 리눅스에서 `nginx`, `docker`, `kubelet` 같은 서비스를 시작, 중지, 재시작, 상태 확인할 때 사용하는 명령어다.

쿠버네티스나 Docker를 공부하다 보면 결국 서버 위에서 돌아가는 서비스들을 봐야 하기 때문에, `systemctl`은 인프라 공부에서 거의 기본기라고 보면 된다.
