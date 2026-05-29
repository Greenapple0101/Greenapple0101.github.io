---
title: "[LINUX] 시스템 운영과 네트워크 트러블슈팅 기본 역량"
source: "https://velog.io/@yorange50/LINUX-시스템-운영과-네트워크-트러블슈팅-기본-역량"
published: "2026-05-12T18:45:40.876Z"
tags: ""
backup_date: "2026-05-29T14:52:52.754485"
---

## 1. 왜 Linux와 Network를 같이 봐야 할까?

서버를 운영하다 보면 문제는 보통 한 군데에서만 터지지 않는다.

예를 들어 웹 서버가 안 열린다고 해보자.

```bash
curl localhost:8080
```

했는데 응답이 안 온다.

이때 원인은 여러 가지일 수 있다.

```text
애플리케이션이 안 떠 있음
프로세스는 떴는데 포트를 안 열었음
포트는 열렸는데 방화벽이 막고 있음
컨테이너 포트 매핑이 잘못됨
DNS가 안 풀림
서버는 정상인데 네트워크 라우팅이 안 됨
인증 문제로 401/403이 남
```

그래서 실무에서 Linux 기반 시스템 운영 역량과 네트워크 트러블슈팅 역량은 거의 붙어 다닌다.

단순히 명령어를 외우는 게 아니라, 문제가 생겼을 때 다음 순서로 볼 수 있어야 한다.

```text
프로세스가 떠 있는가?
포트를 열고 있는가?
내부에서 접근 가능한가?
외부에서 접근 가능한가?
DNS는 정상인가?
HTTP 응답은 어떤 상태인가?
로그에는 뭐라고 찍히는가?
```

이 흐름을 잡는 게 핵심이다.

---

## 2. Linux 기반 시스템 운영이란?

Linux 기반 시스템 운영은 서버 위에서 서비스가 정상적으로 돌아가도록 관리하는 일이다.

여기서 서버는 보통 Ubuntu, CentOS, Rocky Linux, Amazon Linux 같은 Linux OS를 의미한다.

시스템 운영에서 자주 보는 항목은 다음과 같다.

```text
프로세스
포트
로그
파일 권한
디스크 용량
메모리 사용량
CPU 사용량
서비스 상태
네트워크 연결 상태
```

개발자는 코드를 짜고 끝나는 게 아니라, 그 코드가 실제 서버에서 어떻게 실행되는지도 알아야 한다.

특히 백엔드, DevOps, Cloud, MLOps 쪽으로 가면 Linux를 피하기 어렵다.

---

## 3. 프로세스 확인

프로세스는 실행 중인 프로그램이다.

Spring Boot 애플리케이션을 실행하면 Java 프로세스가 뜬다.

Nginx를 실행하면 nginx 프로세스가 뜬다.

Docker를 실행하면 docker 관련 프로세스가 뜬다.

현재 실행 중인 프로세스를 확인할 때는 보통 `ps`를 쓴다.

```bash
ps aux
```

너무 많이 나오기 때문에 보통 `grep`이랑 같이 쓴다.

```bash
ps aux | grep java
```

이 명령어는 실행 중인 프로세스 중에서 `java`라는 문자열이 들어간 것을 찾는다.

예를 들어 Spring Boot 앱이 정상적으로 떠 있다면 이런 식으로 보일 수 있다.

```text
user  12345  5.0  3.2  java -jar app.jar
```

여기서 중요한 건 PID다.

PID는 프로세스 ID다.

특정 프로세스를 종료하고 싶으면 PID를 이용한다.

```bash
kill 12345
```

강제로 종료해야 할 때는 다음처럼 쓴다.

```bash
kill -9 12345
```

하지만 `kill -9`는 최후의 수단에 가깝다. 정상 종료 기회를 주지 않고 바로 죽이는 방식이기 때문이다.

---

## 4. 포트 확인

서버 애플리케이션은 보통 특정 포트를 연다.

예를 들어 Spring Boot는 기본적으로 8080 포트를 사용한다.

```text
Spring Boot → 8080
Nginx → 80 또는 443
PostgreSQL → 5432
MySQL → 3306
Prometheus → 9090
Grafana → 3000
```

포트가 열려 있는지 확인하려면 다음 명령어를 쓴다.

```bash
lsof -i :8080
```

또는

```bash
netstat -tulnp
```

요즘 Linux에서는 `ss`를 많이 쓴다.

```bash
ss -tulnp
```

여기서 옵션 의미는 대략 이렇다.

```text
-t : TCP
-u : UDP
-l : listening 상태
-n : 숫자로 출력
-p : 프로세스 정보 출력
```

8080 포트를 누가 쓰고 있는지 보고 싶으면 이렇게 본다.

```bash
ss -tulnp | grep 8080
```

만약 이미 8080 포트를 다른 프로세스가 쓰고 있다면 새 애플리케이션이 뜨지 못한다.

이때 흔히 보는 에러가 이런 것이다.

```text
Port 8080 was already in use
Address already in use
```

이 경우 해야 할 일은 둘 중 하나다.

```text
기존 프로세스를 종료한다
새 애플리케이션의 포트를 바꾼다
```

---

## 5. curl로 응답 확인하기

서버가 진짜 응답하는지 확인할 때는 `curl`을 많이 쓴다.

```bash
curl localhost:8080
```

이 명령어는 현재 서버 안에서 8080 포트로 요청을 보내는 것이다.

만약 Spring Boot가 정상적으로 떠 있고 `/` 경로가 있다면 응답이 온다.

하지만 이런 에러가 날 수도 있다.

```bash
curl: (7) Failed to connect to localhost port 8080
```

이 말은 보통 다음 의미다.

```text
8080 포트에 아무 서비스도 안 떠 있음
애플리케이션 실행 실패
포트가 다름
컨테이너 내부에는 떠 있는데 호스트 포트 매핑이 안 됨
```

반대로 응답은 오는데 이런 게 나올 수 있다.

```text
404 Not Found
```

이건 서버 자체는 떠 있다는 뜻이다. 다만 요청한 경로에 해당하는 API나 페이지가 없는 것이다.

즉, `connection refused`와 `404`는 다르다.

```text
connection refused → 서버/포트 접근 자체 실패
404 → 서버는 살아있지만 해당 경로 없음
```

이 차이를 아는 게 중요하다.

---

## 6. HTTP Status Code 이해

네트워크 트러블슈팅에서 HTTP 상태 코드는 매우 중요하다.

자주 보는 상태 코드는 다음과 같다.

| 상태 코드     | 의미         |
| --------- | ---------- |
| 200       | 성공         |
| 201       | 생성 성공      |
| 301 / 302 | 리다이렉트      |
| 400       | 잘못된 요청     |
| 401       | 인증 필요      |
| 403       | 권한 없음      |
| 404       | 경로 없음      |
| 405       | 메서드 불일치    |
| 500       | 서버 내부 오류   |
| 502       | 게이트웨이 오류   |
| 503       | 서비스 사용 불가  |
| 504       | 게이트웨이 타임아웃 |

예를 들어 `GET /boards`는 되는데 `POST /boards`가 안 된다면 405가 날 수 있다.

```text
405 Method Not Allowed
```

이건 경로는 있는데 HTTP 메서드가 맞지 않는 경우다.

예를 들어 컨트롤러에는 이렇게 되어 있는데

```java
@GetMapping("/boards")
```

클라이언트가 POST로 보내면 맞지 않는다.

```bash
curl -X POST localhost:8080/boards
```

이런 식으로 HTTP 상태 코드를 보면 문제가 어디에 있는지 좁혀갈 수 있다.

---

## 7. 로그 확인

실무에서는 로그를 봐야 한다.

서버가 안 뜨거나 API가 실패할 때, 화면만 보고는 원인을 알기 어렵다.

Linux에서 로그를 볼 때 자주 쓰는 명령어는 다음과 같다.

```bash
tail -f app.log
```

`tail -f`는 로그 파일의 마지막 부분을 계속 따라가면서 보여준다.

Spring Boot를 직접 실행한다면 터미널에 로그가 바로 찍힌다.

```bash
java -jar app.jar
```

systemd로 서비스화되어 있다면 `journalctl`을 쓴다.

```bash
journalctl -u my-app
```

실시간으로 보고 싶으면 다음처럼 쓴다.

```bash
journalctl -u my-app -f
```

Docker 컨테이너 로그는 이렇게 본다.

```bash
docker logs 컨테이너명
```

실시간으로 보려면

```bash
docker logs -f 컨테이너명
```

Kubernetes에서는 다음처럼 본다.

```bash
kubectl logs pod명
```

실시간 로그는

```bash
kubectl logs -f pod명
```

결국 환경이 달라져도 핵심은 같다.

```text
문제가 생기면 로그를 본다
로그에서 에러 메시지를 찾는다
에러 메시지를 기준으로 원인을 좁힌다
```

---

## 8. ping으로 네트워크 연결 확인

`ping`은 상대 서버까지 네트워크 연결이 되는지 확인할 때 쓴다.

```bash
ping google.com
```

또는 특정 IP로 보낼 수 있다.

```bash
ping 8.8.8.8
```

여기서 중요한 건 DNS 문제와 네트워크 문제를 구분하는 것이다.

예를 들어

```bash
ping google.com
```

은 안 되는데

```bash
ping 8.8.8.8
```

은 된다면 DNS 문제일 가능성이 있다.

즉, 인터넷 연결 자체는 되지만 도메인 이름을 IP로 바꾸는 과정이 안 되는 것이다.

---

## 9. DNS 확인

DNS는 도메인 이름을 IP 주소로 바꿔주는 시스템이다.

예를 들어 사용자가 브라우저에 다음 주소를 입력한다고 하자.

```text
example.com
```

컴퓨터는 실제로 `example.com`이라는 문자열로 서버를 찾는 게 아니라, 이 도메인에 연결된 IP 주소를 찾아서 접속한다.

DNS 확인에는 다음 명령어를 쓴다.

```bash
nslookup example.com
```

또는

```bash
dig example.com
```

DNS 문제는 은근히 자주 나온다.

```text
도메인 오타
DNS 레코드 설정 오류
내부 DNS 문제
캐시 문제
사설망 DNS 문제
```

특히 회사 내부망, VPN, Kubernetes, 클라우드 환경에서는 DNS가 중요한 트러블슈팅 포인트가 된다.

---

## 10. 인증과 인가 문제

API 요청이 실패했을 때 항상 네트워크 문제는 아니다.

인증과 인가 문제일 수도 있다.

```text
인증 Authentication → 너 누구야?
인가 Authorization → 너 이거 해도 돼?
```

대표적인 상태 코드는 다음과 같다.

```text
401 Unauthorized → 로그인 안 됨, 토큰 없음, 토큰 만료
403 Forbidden → 로그인은 됐지만 권한 없음
```

예를 들어 JWT 토큰이 필요한 API에 토큰 없이 요청하면 401이 날 수 있다.

```bash
curl localhost:8080/api/users
```

토큰을 넣어서 요청할 때는 보통 이렇게 한다.

```bash
curl -H "Authorization: Bearer 토큰값" localhost:8080/api/users
```

실무에서는 401과 403을 구분할 줄 알아야 한다.

```text
401 → 인증 자체가 안 됨
403 → 인증은 됐지만 권한이 없음
```

---

## 11. JSON 요청 확인

백엔드 API는 보통 JSON으로 데이터를 주고받는다.

POST 요청을 보낼 때는 `Content-Type`을 명시해야 한다.

```bash
curl -X POST localhost:8080/boards \
  -H "Content-Type: application/json" \
  -d '{"title":"hello","content":"world"}'
```

여기서 중요한 부분은 두 가지다.

```text
-H "Content-Type: application/json"
-d '{"title":"hello","content":"world"}'
```

`Content-Type`을 안 보내면 서버가 요청 본문을 제대로 해석하지 못할 수 있다.

Spring Boot에서는 JSON 요청을 받을 때 보통 `@RequestBody`를 쓴다.

```java
@PostMapping("/boards")
public Board createBoard(@RequestBody Board board) {
    return boardService.save(board);
}
```

이때 클라이언트가 JSON 형식을 잘못 보내면 400 Bad Request가 날 수 있다.

---

## 12. 포트, 프로세스, 로그를 같이 봐야 하는 이유

서버가 안 된다고 했을 때 한 가지만 보면 안 된다.

예를 들어 이런 상황을 보자.

```bash
curl localhost:8080
```

결과가 실패했다.

그러면 순서대로 확인한다.

첫 번째, 프로세스가 떠 있는지 확인한다.

```bash
ps aux | grep java
```

두 번째, 포트가 열려 있는지 확인한다.

```bash
ss -tulnp | grep 8080
```

세 번째, 로그를 확인한다.

```bash
tail -f app.log
```

Docker라면 이렇게 본다.

```bash
docker ps
docker logs -f 컨테이너명
```

이 흐름이 실무에서 매우 중요하다.

```text
프로세스 확인
포트 확인
로그 확인
요청 확인
응답 코드 확인
```

이걸 반복하면서 원인을 좁히는 것이다.

---

## 13. 자주 나오는 트러블슈팅 시나리오

### 1. 서버가 아예 안 뜨는 경우

증상:

```text
curl: Failed to connect
```

확인할 것:

```bash
ps aux | grep java
ss -tulnp | grep 8080
```

가능한 원인:

```text
애플리케이션 실행 실패
포트 충돌
환경변수 누락
빌드 실패
DB 연결 실패로 애플리케이션 종료
```

---

### 2. 서버는 떴는데 404가 나는 경우

증상:

```text
404 Not Found
```

확인할 것:

```text
요청 URL이 맞는가?
Controller 매핑이 맞는가?
GET/POST 경로가 맞는가?
context-path가 설정되어 있지는 않은가?
```

예를 들어 서버는 살아있지만 `/` 경로가 없으면 404가 날 수 있다.

```bash
curl localhost:8080
```

하지만 실제 API가 `/boards`라면 이렇게 해야 한다.

```bash
curl localhost:8080/boards
```

---

### 3. 500 에러가 나는 경우

증상:

```text
500 Internal Server Error
```

확인할 것:

```text
서버 로그
예외 메시지
DB 연결
NullPointerException
SQL 에러
외부 API 호출 실패
```

500은 서버 내부에서 예외가 터진 것이다.

이때는 거의 무조건 로그를 봐야 한다.

---

### 4. 401 또는 403이 나는 경우

증상:

```text
401 Unauthorized
403 Forbidden
```

확인할 것:

```text
토큰이 있는가?
토큰이 만료되었는가?
Authorization 헤더 형식이 맞는가?
권한 Role이 맞는가?
```

---

### 5. DNS가 안 되는 경우

증상:

```text
도메인으로 접속 안 됨
IP로는 접속 됨
```

확인할 것:

```bash
ping 도메인
ping IP주소
nslookup 도메인
dig 도메인
```

가능한 원인:

```text
DNS 설정 오류
도메인 오타
내부 DNS 장애
VPN/DNS 충돌
```

---

## 14. 실무에서 중요한 사고방식

Linux와 네트워크 트러블슈팅은 명령어 암기가 전부가 아니다.

중요한 건 순서다.

무작정 이것저것 치는 게 아니라, 계층적으로 내려가야 한다.

```text
1. 애플리케이션은 실행 중인가?
2. 프로세스가 살아 있는가?
3. 포트가 열려 있는가?
4. 같은 서버 내부에서 curl이 되는가?
5. 외부에서 접근이 되는가?
6. DNS는 정상인가?
7. HTTP 상태 코드는 무엇인가?
8. 로그에는 어떤 에러가 있는가?
9. 인증/인가 문제는 아닌가?
10. 요청 JSON 형식은 맞는가?
```

이 순서대로 보면 문제를 훨씬 빨리 좁힐 수 있다.

---

## 15. 기본 명령어 정리

| 목적               | 명령어                      |
| ---------------- | ------------------------ |
| 프로세스 확인          | `ps aux`                 |
| 특정 프로세스 검색       | `ps aux \| grep java`    |
| 포트 확인            | `ss -tulnp`              |
| 특정 포트 확인         | `ss -tulnp \| grep 8080` |
| HTTP 요청 테스트      | `curl localhost:8080`    |
| 네트워크 연결 확인       | `ping google.com`        |
| DNS 확인           | `nslookup example.com`   |
| DNS 상세 확인        | `dig example.com`        |
| 로그 확인            | `tail -f app.log`        |
| systemd 로그 확인    | `journalctl -u 서비스명 -f`  |
| Docker 컨테이너 확인   | `docker ps`              |
| Docker 로그 확인     | `docker logs -f 컨테이너명`   |
| Kubernetes 로그 확인 | `kubectl logs -f pod명`   |

---

## 16. 결론

Linux 기반 시스템 운영과 네트워크 트러블슈팅은 백엔드, 클라우드, DevOps 직무에서 기본 체력에 가깝다.

처음에는 명령어가 많아 보여서 어렵지만, 결국 핵심은 단순하다.

```text
프로세스가 떠 있는지 본다
포트가 열렸는지 본다
curl로 응답을 본다
HTTP 상태 코드를 해석한다
로그를 본다
DNS와 네트워크 연결을 확인한다
인증/인가와 JSON 요청 형식을 확인한다
```

문제가 생겼을 때 당황하지 않고 이 순서대로 확인할 수 있으면 된다.

실무에서 중요한 사람은 모든 명령어를 외운 사람이 아니라, 장애 상황에서 어디부터 봐야 하는지 아는 사람이다.