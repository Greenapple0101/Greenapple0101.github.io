---
title: "[NETWORK] TLS/HTTPS는 왜 안전한가"
source: "https://velog.io/@yorange50/NETWORK-TLSHTTPS는-왜-안전한가"
published: "2026-05-11T14:44:24.620Z"
tags: ""
backup_date: "2026-05-29T14:52:52.761699"
---



우리는 매일:

```text id="l9i9vx"
https://google.com
https://github.com
https://aws.amazon.com
```

같은 사이트에 접속한다.

근데 왜:

```text id="9knjmv"
HTTPS는 안전하다
```

고 하는 걸까?

오늘은:

* TLS
* HTTPS
* 인증서
* 공개키
* Handshake

흐름을 한 번에 이해해보자.

---

# 1. HTTP는 왜 위험한가?

원래 웹은:

```text id="9v66zf"
HTTP
```

를 사용했다.

문제는:

```text id="j1krqt"
암호화가 없음
```

이라는 것이다.

즉:

```text id="ltcy3d"
브라우저
↓
인터넷
↓
서버
```

사이 데이터를 중간에서 보면:

```text id="oq0mns"
아이디
비밀번호
쿠키
```

전부 그대로 보일 수 있었다.

---

# 2. HTTPS란?

HTTPS는:

```text id="l62b3y"
HTTP + TLS
```

이다.

즉:

```text id="ykay5l"
HTTP를 TLS로 보호한 것
```

이다.

---

# 3. TLS란?

TLS는:

```text id="mq0v0n"
Transport Layer Security
```

의 약자다.

쉽게 말하면:

> 인터넷 통신을 암호화하는 보안 프로토콜

이다.

예전에는 SSL이라고 불렀는데,
현재는 대부분 TLS를 사용한다.

---

# 4. TLS가 해결하는 것

TLS는 크게 3가지를 해결한다.

---

## 1) 암호화

중간에서 내용을 봐도 해석 불가.

---

## 2) 무결성

데이터가 중간에서 변조되지 않았는지 확인.

---

## 3) 인증

접속한 서버가 진짜인지 확인.

---

# 5. HTTPS의 핵심 문제

근데 여기서 문제가 생긴다.

```text id="e2y0f7"
암호화는 어떻게 시작할 건데?
```

이다.

---

# 6. 대칭키의 문제

대칭키는 빠르다.

하지만:

```text id="lv9yb3"
키를 안전하게 전달하기 어렵다
```

라는 문제가 있다.

---

# 7. 그래서 TLS는 공개키를 사용한다

TLS는 처음 연결할 때:

```text id="j7y0yc"
공개키 암호화(RSA 등)
```

를 사용한다.

그리고:

```text id="8w7xj6"
대칭키를 안전하게 교환
```

한다.

---

# 8. 이후는 대칭키 사용

대칭키는 빠르기 때문에:

```text id="g2r0pw"
실제 데이터 통신
```

은 대칭키로 한다.

즉 TLS는:

```text id="0e8ldg"
공개키 = 키 교환
대칭키 = 실제 통신
```

구조다.

---

# 9. HTTPS 연결 흐름

실제 브라우저는 대략 이렇게 동작한다.

---

# 10. 1단계 — 브라우저 접속

사용자가:

```text id="m2cz06"
https://google.com
```

접속.

---

# 11. 2단계 — 서버 인증서 전달

서버는 브라우저에게:

```text id="7g16a2"
인증서(Certificate)
```

를 보낸다.

여기 안에는:

```text id="u8h1ot"
서버 공개키
도메인 정보
인증기관 정보
```

등이 들어있다.

---

# 12. 3단계 — 브라우저가 인증서 검증

브라우저는:

```text id="4h00v8"
"이 인증서 진짜인가?"
```

를 확인한다.

---

# 13. CA(Certificate Authority)

이때 등장하는 게:

```text id="ls2y6t"
CA
```

다.

대표적으로:

* DigiCert
* GlobalSign
* Let's Encrypt

같은 기관.

---

# 14. CA 역할

CA는:

> “이 공개키는 진짜 이 서버 것입니다”

를 증명한다.

즉 브라우저는:

```text id="b1s7v6"
CA를 신뢰
↓
CA가 서명한 인증서도 신뢰
```

하게 된다.

---

# 15. 4단계 — 대칭키 생성

브라우저는:

```text id="jlwmz4"
세션용 대칭키
```

를 만든다.

---

# 16. 5단계 — 공개키로 암호화

브라우저는 서버 공개키로:

```text id="ww1y2m"
대칭키 암호화
```

후 서버로 전달한다.

---

# 17. 6단계 — 서버 복호화

서버는 자기 개인키로:

```text id="zyl2f4"
대칭키 복호화
```

한다.

이제:

```text id="2x0n7x"
브라우저와 서버만
같은 대칭키 공유
```

상태가 된다.

---

# 18. 7단계 — 실제 HTTPS 통신

이후부터는:

```text id="5bdjzq"
대칭키 기반 암호화 통신
```

을 한다.

즉:

```text id="pkm3z0"
로그인 정보
쿠키
API 요청
```

등이 암호화된다.

---

# 19. 왜 안전한가?

중간 공격자가 패킷을 봐도:

```text id="6hdy6k"
대칭키 없음
```

이라 복호화 불가능하다.

또 서버 개인키도 모르기 때문에:

```text id="a1nq0z"
대칭키 탈취 불가
```

하다.

---

# 20. Handshake란?

TLS에서:

```text id="s0cgvl"
처음 보안 연결 만드는 과정
```

을:

```text id="k6xovq"
TLS Handshake
```

라고 한다.

즉:

```text id="r5xq6f"
인증서 교환
키 교환
암호화 설정 협상
```

과정 전체다.

---

# 21. 자물쇠 아이콘 의미

브라우저 주소창의:

```text id="e0lgdz"
자물쇠 아이콘
```

은:

```text id="m3vrhy"
TLS 연결 성공
```

의 의미다.

즉:

```text id="jdh8qf"
HTTPS 통신 중
```

이라는 뜻이다.

---

# 22. HTTPS 없으면 위험한가?

매우 위험하다.

HTTP라면 중간에서:

* 로그인 탈취
* 쿠키 탈취
* 패킷 변조

가능하다.

그래서 현대 서비스는 거의 전부 HTTPS를 강제한다.

---

# 23. HTTPS와 실무

실무에서는:

* Nginx
* ALB
* Ingress
* CloudFront

등에서 TLS 종료(TLS Termination)를 자주 한다.

예:

```text id="s3o89q"
사용자
↓ HTTPS
ALB/Nginx
↓ HTTP
내부 API 서버
```

구조.

---

# 24. 정리

## HTTP

암호화 없음

---

## HTTPS

```text id="xgrg3s"
HTTP + TLS
```

---

## TLS 역할

```text id="qocljc"
암호화
무결성
인증
```

---

## 공개키 역할

안전한 대칭키 교환

---

## 대칭키 역할

실제 데이터 암호화

---

## 인증서

서버 공개키 증명

---

## CA

인증서 신뢰 기관

---

## Handshake

보안 연결 생성 과정

---

# 한 줄 핵심

```text id="e9vx84"
HTTPS는 TLS를 이용해
서버를 검증하고,
안전하게 암호화 통신을 만드는 기술이다.
```