---
title: "[AI Infra] Latency는 도대체 뭘까? AI 추론에서 응답 시간이 중요한 이유"
source: "https://velog.io/@yorange50/AI-Infra-Latency는-도대체-뭘까-AI-추론에서-응답-시간이-중요한-이유"
published: "2026-05-07T06:45:10.924Z"
tags: ""
backup_date: "2026-05-29T14:52:52.771865"
---

AI 인프라나 백엔드, 네트워크 공부를 하다 보면 자주 나오는 단어가 있다.

```text
latency
throughput
response time
TTFT
TPS
```

여기서 `latency`는 특히 AI 추론 서버를 이해할 때 정말 중요하다.

한 줄로 말하면 이렇다.

```text
Latency = 요청을 보낸 뒤 응답을 받기까지 걸리는 시간
```

한국어로는 보통 **지연 시간**이라고 한다.

---

# 1. Latency 한 줄 정의

Latency는 사용자가 요청을 보낸 순간부터 결과를 받는 순간까지의 시간이다.

예를 들어 사용자가 AI 서비스에 질문을 보냈다고 하자.

```text
사용자 질문 전송
↓
서버가 요청 받음
↓
전처리
↓
모델 추론
↓
후처리
↓
응답 반환
```

이 전체 과정에 걸린 시간이 latency다.

```text
latency = 요청 1개가 처리되는 데 걸린 시간
```

예를 들어 응답이 0.8초 만에 오면 latency는 800ms다.

---

# 2. Latency는 왜 중요할까?

사용자 입장에서는 모델이 얼마나 똑똑한지도 중요하지만, **얼마나 빨리 답하느냐**도 중요하다.

예를 들어 챗봇이 답변을 1초 안에 주면 자연스럽다.

그런데 10초, 20초씩 걸리면 사용자는 답답함을 느낀다.

```text
latency 낮음 = 빠른 응답
latency 높음 = 느린 응답
```

AI 서비스에서는 latency가 높으면 이런 문제가 생긴다.

```text
사용자 경험 저하
타임아웃 발생
동시 요청 적체
GPU 자원 낭비
서버 비용 증가
```

그래서 inference serving에서는 latency를 계속 모니터링한다.

---

# 3. Latency와 Throughput 차이

Latency와 throughput은 같이 자주 나온다.

둘은 비슷해 보이지만 다르다.

```text
Latency = 요청 하나가 끝나는 데 걸리는 시간
Throughput = 일정 시간 동안 처리할 수 있는 요청 수
```

예를 들어 식당으로 비유하면 이렇다.

```text
Latency = 손님 한 명이 주문하고 음식을 받기까지 걸리는 시간
Throughput = 식당이 1시간 동안 처리할 수 있는 손님 수
```

AI 서버로 보면 이렇다.

```text
Latency = 요청 1개 응답 시간
Throughput = 초당 처리 가능한 요청 수
```

---

# 4. Latency와 Throughput 비교

| 구분        | Latency        | Throughput               |
| --------- | -------------- | ------------------------ |
| 의미        | 요청 1개의 응답 시간   | 단위 시간당 처리량               |
| 관심 대상     | 사용자 한 명의 체감 속도 | 서버 전체 처리 능력              |
| 단위        | ms, s          | requests/sec, tokens/sec |
| 낮을수록/높을수록 | 낮을수록 좋음        | 높을수록 좋음                  |
| 예시        | 응답까지 500ms     | 초당 100개 요청 처리            |

둘 다 중요하다.

실시간 서비스는 latency가 중요하고, 대량 배치 처리나 서버 효율은 throughput이 중요하다.

---

# 5. AI Inference에서 Latency 구성 요소

AI 추론 요청 하나가 처리되는 과정은 생각보다 여러 단계로 나뉜다.

```text
1. 네트워크 요청 도착
2. 입력 파싱
3. 전처리
4. CPU → GPU 데이터 이동
5. 모델 forward
6. GPU → CPU 결과 이동
7. 후처리
8. 응답 직렬화
9. 네트워크 반환
```

즉, latency는 모델 계산 시간만 의미하지 않는다.

```text
전체 latency = 네트워크 + 전처리 + 데이터 이동 + 모델 추론 + 후처리 + 응답 반환
```

그래서 모델 forward가 빨라도 전처리나 네트워크가 느리면 전체 응답은 느릴 수 있다.

---

# 6. PyTorch Inference에서 Latency

PyTorch inference 코드를 보면 보통 이런 구조다.

```python
import time
import torch

model.eval()

start = time.time()

with torch.inference_mode():
    output = model(x)

end = time.time()

print("latency:", end - start)
```

하지만 GPU를 사용할 때는 주의해야 한다.

CUDA 연산은 비동기적으로 실행될 수 있다.

그래서 정확하게 측정하려면 `torch.cuda.synchronize()`를 넣는 것이 좋다.

```python
import time
import torch

model.eval()

if torch.cuda.is_available():
    torch.cuda.synchronize()

start = time.time()

with torch.inference_mode():
    output = model(x)

if torch.cuda.is_available():
    torch.cuda.synchronize()

end = time.time()

print("latency:", end - start)
```

핵심은 이것이다.

```text
GPU 연산 시간 측정 시 torch.cuda.synchronize() 필요
```

안 그러면 실제 GPU 계산이 끝나기 전에 시간이 찍혀서 latency가 부정확하게 나올 수 있다.

---

# 7. LLM에서 Latency는 더 쪼개서 본다

LLM 추론에서는 latency를 더 세분화해서 본다.

대표적으로 이런 지표가 있다.

```text
TTFT
TPOT
E2E latency
```

하나씩 보면 이렇다.

```text
TTFT = Time To First Token
TPOT = Time Per Output Token
E2E latency = 전체 응답 완료까지 걸린 시간
```

---

# 8. TTFT란?

TTFT는 **Time To First Token**의 약자다.

사용자가 요청을 보낸 뒤, 첫 번째 토큰이 나오기까지 걸리는 시간이다.

```text
사용자 질문 입력
↓
모델 처리 시작
↓
첫 번째 토큰 생성
```

이 시간이 TTFT다.

채팅 서비스에서는 TTFT가 중요하다.

첫 토큰이 빨리 나오면 사용자는 “응답이 시작됐다”고 느낀다.

```text
TTFT 낮음 = 답변이 빨리 시작됨
TTFT 높음 = 사용자가 오래 기다리는 느낌
```

---

# 9. TPOT란?

TPOT는 **Time Per Output Token**이다.

첫 토큰 이후, 토큰 하나를 생성하는 데 걸리는 평균 시간이다.

LLM은 답변을 한 번에 통째로 만드는 게 아니라 토큰을 하나씩 생성한다.

```text
안
녕
하
세
요
```

이런 식으로 순차적으로 생성한다.

그래서 생성 속도는 토큰 단위로 측정한다.

```text
TPOT 낮음 = 토큰이 빠르게 생성됨
TPOT 높음 = 답변 생성이 느림
```

비슷하게 `tokens/sec`도 많이 본다.

```text
tokens/sec = 초당 생성하는 토큰 수
```

---

# 10. E2E Latency란?

E2E는 End-to-End의 약자다.

E2E latency는 요청 시작부터 최종 응답 완료까지 걸리는 전체 시간이다.

```text
요청 전송
↓
첫 토큰 생성
↓
토큰 반복 생성
↓
최종 응답 완료
```

이 전체 시간이 E2E latency다.

LLM에서는 답변 길이에 따라 E2E latency가 크게 달라진다.

짧은 답변은 빨리 끝나고, 긴 답변은 오래 걸린다.

---

# 11. Batch와 Latency의 관계

앞에서 batch는 “한 번에 처리하는 데이터 묶음”이라고 했다.

Inference에서 batch size를 키우면 GPU를 더 효율적으로 쓸 수 있다.

```text
batch size 증가
→ GPU 활용률 증가
→ throughput 증가 가능
```

하지만 latency는 나빠질 수 있다.

왜냐하면 요청을 모으기 위해 잠깐 기다려야 할 수 있기 때문이다.

```text
요청 1개 도착
↓
다른 요청 기다림
↓
batch 구성
↓
한 번에 추론
```

사용자 입장에서는 이 “기다리는 시간”도 latency에 포함된다.

그래서 inference serving에서는 batch size를 무작정 키우지 않는다.

```text
batch size 작음 = latency 유리, throughput 불리
batch size 큼 = throughput 유리, latency 불리
```

---

# 12. Latency를 줄이는 방법

AI inference에서 latency를 줄이는 방법은 여러 가지가 있다.

```text
모델 크기 줄이기
batch size 조정
GPU 사용
전처리 최적화
CPU-GPU 데이터 이동 줄이기
캐싱
양자화
TensorRT 사용
ONNX 변환
서빙 프레임워크 사용
```

하나씩 보면 이렇다.

---

# 13. 모델 크기 줄이기

모델이 클수록 계산량이 많다.

계산량이 많으면 latency가 증가한다.

```text
큰 모델 = 느리지만 성능 좋을 가능성
작은 모델 = 빠르지만 성능 낮을 가능성
```

그래서 서비스에서는 무조건 큰 모델만 쓰지 않는다.

응답 속도와 품질 사이에서 선택해야 한다.

---

# 14. 양자화

양자화는 모델의 숫자 표현을 더 가볍게 만드는 방식이다.

예를 들어 기존에 32비트 부동소수점을 쓰던 모델을 16비트나 8비트로 줄일 수 있다.

```text
FP32 → FP16
FP32 → INT8
```

이렇게 하면 메모리 사용량과 계산량이 줄어들 수 있다.

그 결과 latency가 낮아질 수 있다.

다만 정확도가 조금 떨어질 수도 있으므로 검증이 필요하다.

---

# 15. CPU-GPU 데이터 이동 줄이기

GPU inference에서는 데이터 이동도 비용이다.

```text
CPU 메모리 → GPU 메모리
GPU 메모리 → CPU 메모리
```

이 이동이 너무 자주 일어나면 latency가 증가한다.

그래서 가능하면 데이터를 GPU에 올린 뒤 연산을 GPU 안에서 이어가는 것이 좋다.

나쁜 예시는 이런 흐름이다.

```text
GPU에서 계산
↓
CPU로 가져옴
↓
다시 GPU로 보냄
↓
다시 계산
```

좋은 흐름은 이렇다.

```text
GPU에 올림
↓
GPU에서 계속 계산
↓
마지막 결과만 CPU로 가져옴
```

---

# 16. Warm-up도 중요하다

모델을 처음 실행할 때는 첫 요청이 유독 느릴 수 있다.

이유는 여러 가지가 있다.

```text
CUDA 초기화
커널 로딩
메모리 할당
JIT 컴파일
캐시 준비
```

그래서 실제 서버에서는 모델을 올린 직후 더미 입력으로 몇 번 추론을 돌려보는 경우가 있다.

이걸 warm-up이라고 한다.

```python
model.eval()

dummy = torch.randn(1, 3, 224, 224).to(device)

with torch.inference_mode():
    for _ in range(10):
        _ = model(dummy)
```

이렇게 하면 실제 사용자 요청 전에 초기 지연을 어느 정도 줄일 수 있다.

---

# 17. Latency 모니터링

운영 환경에서는 평균 latency만 보면 부족하다.

보통 이런 지표를 같이 본다.

```text
avg latency
p50 latency
p95 latency
p99 latency
max latency
```

여기서 p95, p99가 중요하다.

```text
p95 latency = 전체 요청 중 95%가 이 시간 안에 처리됨
p99 latency = 전체 요청 중 99%가 이 시간 안에 처리됨
```

평균은 괜찮아 보여도 p99가 크면 일부 사용자는 매우 느린 응답을 경험한다.

예를 들어 평균 latency는 500ms인데 p99가 8초면 문제가 있다.

```text
대부분은 빠름
하지만 일부 요청이 매우 느림
```

그래서 실무에서는 평균뿐만 아니라 tail latency도 본다.

---

# 18. Latency가 높아지는 흔한 원인

AI inference 서버에서 latency가 높아지는 이유는 다양하다.

```text
모델이 너무 큼
GPU 메모리 부족
batch 대기 시간이 김
전처리가 느림
이미지 디코딩이 느림
CPU 병목
GPU 활용률 낮음
네트워크 지연
DB 또는 외부 API 호출
요청 큐 적체
cold start
```

특히 AI 서비스에서는 모델 계산만 보지 말고 전체 파이프라인을 봐야 한다.

```text
입력 수신
전처리
모델 추론
후처리
응답 반환
```

어디서 시간이 많이 쓰이는지 나눠서 측정해야 한다.

---

# 19. FastAPI에서 간단히 Latency 찍기

Inference API에서는 요청 처리 시간을 로그로 남길 수 있다.

```python
import time
from fastapi import FastAPI

app = FastAPI()

@app.post("/predict")
def predict(data: InputData):
    start = time.time()

    x = preprocess(data)

    with torch.inference_mode():
        output = model(x)

    result = postprocess(output)

    end = time.time()

    latency_ms = (end - start) * 1000

    return {
        "result": result,
        "latency_ms": latency_ms
    }
```

더 좋게 하려면 구간별로 나눠서 찍는다.

```text
preprocess latency
model inference latency
postprocess latency
total latency
```

그래야 병목이 어디인지 알 수 있다.

---

# 20. 최종 정리

Latency는 요청 하나가 응답되기까지 걸리는 시간이다.

```text
latency = request 하나의 응답 시간
```

AI inference에서는 latency가 사용자 경험과 직접 연결된다.

```text
낮은 latency = 빠른 응답
높은 latency = 느린 응답
```

Training보다는 inference serving에서 특히 중요하다.

```text
Training = 모델을 학습시키는 단계
Inference = 사용자 요청에 응답하는 단계
Latency = inference 품질을 판단하는 핵심 지표
```

LLM에서는 latency를 더 세분화해서 본다.

```text
TTFT = 첫 토큰까지 걸린 시간
TPOT = 토큰 하나 생성 시간
E2E latency = 전체 응답 완료 시간
```

그리고 latency는 모델 forward 시간만 뜻하지 않는다.

```text
전체 latency
= 네트워크
+ 전처리
+ 데이터 이동
+ 모델 추론
+ 후처리
+ 응답 반환
```

한 문장으로 정리하면 이렇다.

```text
Latency는 사용자가 “느리다” 또는 “빠르다”고 느끼는 시간이다.
```

AI DevOps나 inference serving을 공부한다면 latency, throughput, batch, GPU memory를 같이 묶어서 이해하는 게 좋다.
