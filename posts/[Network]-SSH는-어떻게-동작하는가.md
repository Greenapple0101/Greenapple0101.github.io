---
title: "[NETWORK] SSH는 어떻게 동작하는가"
source: "https://velog.io/@yorange50/NETWORK-SSH는-어떻게-동작하는가"
published: "2026-05-11T14:45:04.235Z"
tags: ""
backup_date: "2026-05-29T14:52:52.761303"
---

개발이나 DevOps를 하다 보면 정말 많이 보게 되는 명령어가 있다.

```bash
ssh ubuntu@10.0.0.5
```

그리고 같이 등장하는 것들:

```text id="5h8w6s"
pem 키
id_rsa
authorized_keys
22번 포트
```

처음엔:

```text id="yz8nzc"
"그냥 원격 접속 아닌가?"
```

싶다.

근데 SSH는:

* 공개키 암호화
* 인증
* 암호화 통신

개념이 다 들어간 꽤 중요한 기술이다.

오늘은 SSH가 실제로 어떻게 동작하는지 흐름으로 이해해보자.

---

# 1. SSH란?

SSH는:

```text id="l0vrk1"
Secure Shell
```

의 약자다.

쉽게 말하면:

> 안전하게 원격 서버에 접속하는 기술

이다.

---

# 2. 왜 SSH가 필요한가?

예전에는:

```text id="bxu73w"
Telnet
```

을 많이 썼다.

근데 문제는:

```text id="6poh8f"
암호화가 없었다
```

는 것이다.

즉 비밀번호가 인터넷에 그대로 날아갔다.

그래서 등장한 게:

```text id="l0v9q6"
SSH
```

다.

---

# 3. SSH의 핵심 기능

SSH는 크게 3가지를 제공한다.

---

## 1) 원격 접속

```bash
ssh user@server
```

---

## 2) 암호화 통신

중간에서 패킷을 봐도 해석 불가.

---

## 3) 인증

접속자가 진짜 허용된 사용자인지 확인.

---

# 4. SSH 기본 구조

예를 들어:

```text id="1htw2d"
내 노트북
↓
인터넷
↓
리눅스 서버
```

가 있다고 해보자.

SSH는:

```text id="g5sz1y"
암호화된 터미널 연결
```

을 만든다.

즉:

```text id="86o4s8"
내가 입력하는 명령어
```

가 안전하게 서버까지 전달된다.

---

# 5. SSH는 몇 번 포트를 사용할까?

기본적으로:

```text id="n7wxks"
22번 포트
```

를 사용한다.

예:

```bash
ssh -p 22 ubuntu@10.0.0.5
```

---

# 6. SSH 로그인 방식

SSH는 크게 두 가지 인증 방식을 많이 쓴다.

---

# 7. 1) 비밀번호 로그인

가장 단순한 방식.

```text id="yrg9mq"
아이디 + 비밀번호
```

입력.

---

## 문제점

비밀번호 공격 위험이 크다.

예:

* 브루트포스 공격
* 비밀번호 유출
* 사전 공격

그래서 실무에서는 점점 안 쓰는 추세다.

---

# 8. 2) SSH Key 로그인

실무에서 가장 많이 사용하는 방식.

---

## 핵심

```text id="gny79r"
공개키 암호화 기반 인증
```

이다.

---

# 9. SSH Key 생성

보통 이런 명령어를 사용한다.

```bash
ssh-keygen
```

그러면 보통:

```text id="ax7u7f"
~/.ssh/id_rsa
~/.ssh/id_rsa.pub
```

파일이 생성된다.

---

# 10. 각각 의미

## id_rsa

```text id="j4tfgu"
개인키(Private Key)
```

절대 유출되면 안 된다.

---

## id_rsa.pub

```text id="4xrfcz"
공개키(Public Key)
```

서버에 등록 가능.

---

# 11. SSH Key 인증 흐름

---

# 12. 1단계 — 서버에 공개키 등록

서버에는:

```text id="mjlwm4"
~/.ssh/authorized_keys
```

파일이 있다.

여기에:

```text id="mxmcb6"
내 공개키
```

를 넣는다.

---

# 13. 2단계 — SSH 접속 시도

내 PC가 서버에 접속한다.

```bash
ssh ubuntu@server
```

---

# 14. 3단계 — 서버가 검증 요청

서버는:

```text id="m92m4f"
"그 공개키에 대응되는 개인키 진짜 가지고 있음?"
```

을 확인한다.

---

# 15. 4단계 — 개인키로 응답

내 컴퓨터는:

```text id="jzjlwm"
개인키로 서명
```

을 생성한다.

---

# 16. 5단계 — 서버가 공개키로 검증

서버는 저장된 공개키로:

```text id="mev4x3"
서명 검증
```

을 한다.

일치하면:

```text id="h9twdm"
접속 허용
```

한다.

---

# 17. 핵심 구조

즉 SSH는:

```text id="ufjlwm"
개인키 가진 사용자만
접속 가능
```

구조다.

---

# 18. 왜 안전한가?

핵심은:

```text id="1a6i1v"
개인키는 네 PC 밖으로 안 나감
```

이다.

즉 인터넷 중간에서 누가 봐도:

```text id="kjlwmv"
개인키 탈취 불가
```

하다.

---

# 19. pem 파일은 뭔가?

AWS EC2 만들면:

```text id="e3u1o5"
my-key.pem
```

같은 걸 준다.

이건 사실:

```text id="7jlwmx"
개인키 파일
```

이다.

즉:

```text id="b9m3uj"
pem = SSH 개인키
```

라고 생각해도 된다.

---

# 20. 왜 pem 잃어버리면 접속 못하나?

서버는:

```text id="hjlwmr"
공개키만 저장
```

하고 있다.

근데 개인키를 잃어버리면:

```text id="djlwmc"
"내가 진짜 사용자다"
```

를 증명할 방법이 없다.

그래서 접속이 막힌다.

---

# 21. authorized_keys란?

리눅스 서버의:

```text id="rjlwmq"
~/.ssh/authorized_keys
```

파일은:

> “접속 허용할 공개키 목록”

이다.

즉:

```text id="djlwmf"
여기 등록된 공개키의 개인키 가진 사람만
접속 허용
```

이다.

---

# 22. known_hosts는 뭔가?

클라이언트 쪽에는:

```text id="vjlwmr"
~/.ssh/known_hosts
```

파일이 있다.

이건:

```text id="6jlwmn"
"예전에 접속했던 서버 목록"
```

이다.

---

# 23. 왜 처음 접속하면 물어보는가?

처음 SSH 접속 시:

```text
Are you sure you want to continue connecting?
```

가 뜬다.

이건:

```text id="3jlwmv"
서버 공개키 신뢰 여부
```

를 묻는 것이다.

---

# 24. SSH와 TLS 차이

둘 다 암호화 통신이지만 목적이 다르다.

| 기술  | 목적       |
| --- | -------- |
| TLS | 웹 통신 보호  |
| SSH | 원격 서버 접속 |

---

# 25. 실무에서 SSH 쓰는 곳

엄청 많다.

예:

```text id="8jlwmc"
EC2 접속
리눅스 서버 관리
Git 인증
배포 서버 접근
Docker/K8s 노드 접근
```

---

# 26. 정리

## SSH

안전한 원격 접속 기술

---

## 기본 포트

```text id="ljlwmq"
22
```

---

## SSH Key

```text id="jjlwmn"
공개키 + 개인키
```

기반 인증

---

## id_rsa

개인키

---

## id_rsa.pub

공개키

---

## authorized_keys

접속 허용 공개키 목록

---

## pem 파일

SSH 개인키 파일

---

## 핵심 구조

```text id="7jlwmz"
개인키로 인증
↓
서버가 공개키로 검증
```

---

# 한 줄 핵심

```text id="2jlwmx"
SSH는 공개키 암호화를 이용해,
인터넷에서도 안전하게 서버에 접속할 수 있게 만든 기술이다.
```