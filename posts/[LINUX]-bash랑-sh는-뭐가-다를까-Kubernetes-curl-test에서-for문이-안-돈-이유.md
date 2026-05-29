---
title: "[LINUX] bash랑 sh는 뭐가 다를까? Kubernetes curl-test에서 for문이 안 돈 이유"
source: "https://velog.io/@yorange50/LINUX-bash랑-sh는-뭐가-다를까-Kubernetes-curl-test에서-for문이-안-돈-이유"
published: "2026-05-19T03:50:53.895Z"
tags: ""
backup_date: "2026-05-29T14:52:52.727169"
---

Kubernetes에서 `ClusterIP` Service가 로드밸런싱을 하는지 확인하려고 `curl-test` Pod를 띄웠다.

```bash
kubectl run curl-test --image=curlimages/curl -it --rm -- sh
```

그리고 Service IP로 1000번 요청을 보내려고 아래처럼 입력했다.

```bash
for i in {1..1000}
do
  curl http://10.43.144.200
  echo " (${i})"
  sleep 1
done
```

그런데 결과가 이상했다.

```bash
curl: (7) Failed to connect to 10.43.144.200 port 80 after 75005 ms: Could not connect to server
 ({1..1000})
```

원래 기대한 결과는 이런 식이었다.

```text
nginx-1 (1)
nginx-2 (2)
nginx-3 (3)
...
```

그런데 실제로는 숫자가 `1`, `2`, `3`으로 증가하지 않고 그대로 `{1..1000}`이라고 출력됐다.

이 문제는 크게 두 가지 때문이다.

```text
1. curl-test Pod 안에서 실행한 shell이 bash가 아니라 sh였음
2. {1..1000} 문법은 sh에서 동작하지 않을 수 있음
```

## 1. 내가 들어간 곳은 bash가 아니라 sh였다

처음 실행한 명령어를 다시 보면 끝에 `sh`가 붙어 있다.

```bash
kubectl run curl-test --image=curlimages/curl -it --rm -- sh
```

이 명령은 `curl-test`라는 임시 Pod를 만들고, 그 안에서 `sh`를 실행하라는 뜻이다.

즉, 나는 컨테이너 안에서 `bash`를 쓰고 있던 게 아니라 `sh`를 쓰고 있었다.

```text
kubectl run curl-test
→ curl-test Pod 생성

--image=curlimages/curl
→ curl이 설치된 이미지 사용

-it
→ 터미널로 접속

--rm
→ 나가면 Pod 자동 삭제

-- sh
→ 컨테이너 안에서 sh 실행
```

그래서 프롬프트도 보통 이렇게 나온다.

```bash
~ $
```

이 상태는 bash가 아니라 sh일 가능성이 높다.

## 2. bash와 sh의 차이

`sh`는 기본적인 shell이다. POSIX shell이라고 생각하면 된다.

반면 `bash`는 `sh`보다 기능이 더 많은 shell이다.

```text
sh
→ 더 기본적인 shell
→ 가볍고 단순함
→ 최소 이미지에 자주 들어 있음
→ 문법 지원이 제한적일 수 있음

bash
→ sh보다 기능이 많은 shell
→ 배열, brace expansion, 편의 문법 지원
→ 리눅스 서버에서 많이 사용
→ 하지만 가벼운 컨테이너 이미지에는 없을 수 있음
```

컨테이너 이미지는 보통 최대한 가볍게 만들기 때문에 `bash`가 없는 경우가 많다.

그래서 `curlimages/curl` 같은 디버깅용 이미지에서도 기본 shell이 `sh`일 수 있다.

## 3. 문제가 된 문법: `{1..1000}`

내가 처음 쓴 반복문은 이거였다.

```bash
for i in {1..1000}
do
  curl http://10.43.188.207
  echo " (${i})"
  sleep 1
done
```

여기서 핵심은 이 부분이다.

```bash
{1..1000}
```

이 문법은 bash에서 자주 쓰는 brace expansion이다.

bash에서는 `{1..5}`를 이렇게 펼쳐준다.

```bash
1 2 3 4 5
```

그래서 bash에서는 아래 반복문이 잘 동작한다.

```bash
for i in {1..5}
do
  echo $i
done
```

결과:

```text
1
2
3
4
5
```

하지만 sh에서는 `{1..5}`를 숫자 범위로 펼쳐주지 않을 수 있다.

그럼 sh는 이걸 그냥 문자열 하나로 본다.

```text
{1..5}
```

그래서 반복이 1000번 도는 게 아니라 딱 한 번만 돈다.

```bash
for i in {1..1000}
```

이게 sh에서는 사실상 이렇게 해석될 수 있다.

```bash
for i in "{1..1000}"
```

그래서 출력도 이렇게 나온 것이다.

```text
({1..1000})
```

즉, 숫자가 증가하지 않은 이유는 `i`에 `1`, `2`, `3`이 들어간 게 아니라 `{1..1000}`이라는 문자열 자체가 들어갔기 때문이다.

## 4. sh에서 안전하게 쓰는 방식

sh에서는 `{1..1000}` 대신 `while`문을 쓰는 게 안전하다.

```bash
i=1
while [ $i -le 1000 ]
do
  curl http://10.43.188.207
  echo " ($i)"
  i=$((i+1))
  sleep 1
done
```

이 방식은 bash뿐만 아니라 sh에서도 잘 동작한다.

하나씩 보면 다음과 같다.

```bash
i=1
```

반복을 시작할 숫자를 1로 설정한다.

```bash
while [ $i -le 1000 ]
```

`i`가 1000보다 작거나 같은 동안 반복한다.

여기서 `-le`는 `less than or equal`의 의미다.

```text
-le = less than or equal
즉, 작거나 같다
```

```bash
curl http://10.43.188.207
```

Service의 ClusterIP로 요청을 보낸다.

```bash
echo " ($i)"
```

현재 몇 번째 요청인지 출력한다.

```bash
i=$((i+1))
```

`i` 값을 1 증가시킨다.

```bash
sleep 1
```

1초 쉬고 다음 요청을 보낸다.

## 5. 두 반복문 비교

처음에 쓴 방식은 이거였다.

```bash
for i in {1..1000}
do
  curl http://10.43.188.207
  echo " (${i})"
  sleep 1
done
```

이건 bash에서는 잘 동작할 수 있다.

하지만 sh에서는 `{1..1000}`이 숫자로 펼쳐지지 않을 수 있다.

그래서 sh에서는 아래 방식이 더 안전하다.

```bash
i=1
while [ $i -le 1000 ]
do
  curl http://10.43.188.207
  echo " ($i)"
  i=$((i+1))
  sleep 1
done
```

차이를 표로 정리하면 다음과 같다.

| 구분          | bash용 for문                    | sh에서도 안전한 while문        |
| ----------- | ----------------------------- | ----------------------- |
| 코드          | `for i in {1..1000}`          | `while [ $i -le 1000 ]` |
| 핵심 문법       | brace expansion               | 조건 반복                   |
| bash 지원     | 가능                            | 가능                      |
| sh 지원       | 안 될 수 있음                      | 가능                      |
| 결과          | sh에서는 `{1..1000}` 그대로 나올 수 있음 | 1부터 1000까지 정상 증가        |
| 컨테이너 실습 안정성 | 낮음                            | 높음                      |

## 6. 왜 컨테이너에서는 sh 기준으로 생각하는 게 좋을까?

컨테이너 안에서 실습할 때는 bash가 없을 수 있다.

특히 이런 이미지들은 가볍게 만들어져 있어서 기본 도구가 많이 빠져 있다.

```text
alpine
busybox
curlimages/curl
distroless 계열 이미지
```

앱 컨테이너에 들어갔을 때도 이런 문제가 자주 생긴다.

```bash
bash: command not found
curl: command not found
vi: command not found
```

이건 이상한 게 아니다.

운영용 컨테이너 이미지는 보통 필요한 실행 파일만 넣고, 불필요한 디버깅 도구는 빼는 경우가 많기 때문이다.

그래서 Kubernetes 실습에서는 이런 감각이 중요하다.

```text
컨테이너 안에 bash가 있다고 가정하지 않기
컨테이너 안에 curl이 있다고 가정하지 않기
컨테이너 안에 vi가 있다고 가정하지 않기
```

그래서 `curl-test`처럼 디버깅용 Pod를 따로 띄우는 것이다.

```bash
kubectl run curl-test --image=curlimages/curl -it --rm -- sh
```

## 7. IP 문제도 같이 확인해야 한다

이번에 나온 에러에는 반복문 문제 말고 IP 문제도 있었다.

에러 메시지는 다음과 같았다.

```text
Failed to connect to 10.43.144.200 port 80
```

이건 `10.43.144.200`이라는 Service IP에 연결하지 못했다는 뜻이다.

그런데 실제로 성공했던 IP는 다음이었다.

```bash
curl http://10.43.188.207
```

즉, 문서에 적힌 IP와 현재 내 클러스터에서 생성된 Service IP가 달랐을 가능성이 있다.

ClusterIP는 Service를 만들 때 자동으로 할당되기 때문에 사람마다, 환경마다 다를 수 있다.

그래서 문서의 IP를 그대로 복붙하면 안 된다.

항상 내 환경에서 직접 확인해야 한다.

```bash
kubectl get svc
```

예를 들어 이렇게 나온다면:

```text
NAME        TYPE        CLUSTER-IP      PORT(S)
nginx-svc   ClusterIP   10.43.188.207   80/TCP
```

curl은 이렇게 해야 한다.

```bash
curl http://10.43.188.207
```

## 8. 최종적으로 써야 하는 명령

`curl-test` Pod 안에서 안정적으로 반복 요청을 보내려면 이렇게 쓰면 된다.

```bash
i=1
while [ $i -le 1000 ]
do
  curl http://10.43.188.207
  echo " ($i)"
  i=$((i+1))
  sleep 1
done
```

한 줄로 쓰고 싶으면 이렇게도 가능하다.

```bash
i=1; while [ $i -le 1000 ]; do curl http://10.43.188.207; echo " ($i)"; i=$((i+1)); sleep 1; done
```

실행 결과는 이런 식으로 나올 수 있다.

```text
nginx-2
 (1)
nginx-1
 (2)
nginx-3
 (3)
nginx-2
 (4)
```

이렇게 응답이 `nginx-1`, `nginx-2`, `nginx-3`으로 바뀌면 Service가 뒤에 있는 여러 Pod로 요청을 분산하고 있다는 뜻이다.

## 9. 정리

이번 실습에서 헷갈린 핵심은 `bash`와 `sh`의 차이였다.

```text
bash
→ 기능이 많은 shell
→ {1..1000} 같은 brace expansion 지원

sh
→ 더 기본적인 shell
→ {1..1000}이 숫자로 펼쳐지지 않을 수 있음
```

처음 쓴 코드는 bash 기준으로는 자연스럽다.

```bash
for i in {1..1000}
do
  curl http://10.43.188.207
  echo " (${i})"
  sleep 1
done
```

하지만 `curl-test` Pod에서는 `sh`로 들어갔기 때문에 `{1..1000}`이 숫자로 펼쳐지지 않았다.

그래서 sh에서도 안전하게 동작하는 방식으로 바꿔야 한다.

```bash
i=1
while [ $i -le 1000 ]
do
  curl http://10.43.188.207
  echo " ($i)"
  i=$((i+1))
  sleep 1
done
```

한 문장으로 정리하면 다음과 같다.

```text
컨테이너 안에서는 bash가 아니라 sh일 수 있으므로, 반복문도 sh에서 동작하는 문법으로 작성하는 게 안전하다.
```
