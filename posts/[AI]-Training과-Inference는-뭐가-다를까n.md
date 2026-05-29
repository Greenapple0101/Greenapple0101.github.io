---
title: "[AI] Training과 Inference는 뭐가 다를까?\n"
source: "https://velog.io/@yorange50/AI-Training과-Inference는-뭐가-다를까"
published: "2026-05-07T06:22:08.429Z"
tags: ""
backup_date: "2026-05-29T14:52:52.772506"
---

딥러닝을 공부하면 자주 나오는 말이 있다.

```text
training
inference
```

한국어로는 보통 이렇게 부른다.

```text
training = 학습
inference = 추론
```

처음에는 둘 다 “모델을 돌리는 것”처럼 보인다.
하지만 실제로는 목적도 다르고, 계산 방식도 다르고, 인프라에서 중요하게 보는 포인트도 다르다.

---

## 1. 한 줄 정의

먼저 아주 짧게 정리하면 이렇다.

```text
Training = 모델이 정답을 보고 가중치를 배우는 과정
Inference = 학습된 모델이 새로운 입력에 대해 결과를 예측하는 과정
```

예를 들어 고양이/강아지 분류 모델이 있다고 하자.

학습은 이런 과정이다.

```text
이미지 입력
정답: 고양이
모델 예측: 강아지
틀렸으니까 가중치 수정
다시 반복
```

추론은 이런 과정이다.

```text
새 이미지 입력
모델 예측: 고양이
결과 반환
```

즉, 학습은 **모델을 만드는 과정**이고, 추론은 **만들어진 모델을 사용하는 과정**이다.

---

## 2. Training이란?

Training은 모델이 데이터를 보고 패턴을 배우는 과정이다.

모델은 처음부터 똑똑하지 않다.
처음에는 가중치가 거의 랜덤에 가깝다.

그래서 입력을 넣으면 이상한 답을 낸다.

```text
입력: 고양이 사진
정답: 고양이
모델 예측: 자동차
```

이때 모델은 정답과 자신의 예측을 비교한다.

```text
오차 = 모델 예측값 - 실제 정답
```

그리고 이 오차를 줄이기 위해 내부 가중치를 조금씩 바꾼다.

이 과정을 엄청 많이 반복한다.

```text
예측
오차 계산
역전파
가중치 업데이트
다시 예측
다시 오차 계산
다시 업데이트
```

이게 Training이다.

---

## 3. Training의 핵심 흐름

학습 과정은 보통 이렇게 진행된다.

```text
1. 데이터를 준비한다
2. 모델에 입력을 넣는다
3. 모델이 예측한다
4. 정답과 비교해서 loss를 계산한다
5. loss를 줄이는 방향으로 gradient를 계산한다
6. optimizer가 가중치를 업데이트한다
7. 이 과정을 여러 epoch 동안 반복한다
```

코드로 보면 대략 이런 느낌이다.

```python
for x, y in train_loader:
    x = x.to(device)
    y = y.to(device)

    optimizer.zero_grad()

    output = model(x)
    loss = criterion(output, y)

    loss.backward()
    optimizer.step()
```

여기서 중요한 부분은 이것이다.

```python
loss.backward()
optimizer.step()
```

이 두 줄이 학습의 핵심이다.

```text
loss.backward() = 오차를 줄이기 위한 gradient 계산
optimizer.step() = 계산된 gradient로 가중치 업데이트
```

즉, Training에서는 모델의 파라미터가 계속 바뀐다.

---

## 4. Inference란?

Inference는 이미 학습된 모델을 사용해서 결과를 예측하는 과정이다.

이때는 정답을 보고 배우는 것이 아니다.

모델에게 새로운 입력을 주고, 결과만 얻는다.

예를 들어 이런 식이다.

```text
입력: 새로운 이미지
모델 출력: 강아지일 확률 92%
```

또는 LLM이라면 이런 식이다.

```text
입력: "CUDA가 뭐야?"
모델 출력: "CUDA는 NVIDIA GPU에서 병렬 연산을..."
```

Inference에서는 모델의 가중치를 수정하지 않는다.

이미 학습된 모델을 그대로 사용한다.

---

## 5. Inference의 핵심 흐름

추론 과정은 보통 이렇게 진행된다.

```text
1. 학습된 모델을 불러온다
2. 입력 데이터를 받는다
3. 모델에 입력을 넣는다
4. 결과를 계산한다
5. 결과를 사용자에게 반환한다
```

코드로 보면 이런 느낌이다.

```python
model.eval()

with torch.no_grad():
    output = model(x)
    prediction = torch.argmax(output, dim=1)
```

여기서 중요한 부분은 두 가지다.

```python
model.eval()
```

```python
with torch.no_grad():
```

`model.eval()`은 모델을 추론 모드로 바꾸는 것이다.

`torch.no_grad()`는 gradient 계산을 하지 않겠다는 뜻이다.

추론에서는 가중치를 업데이트하지 않기 때문에 gradient가 필요 없다.

그래서 메모리도 덜 쓰고, 속도도 더 빨라진다.

---

## 6. Training vs Inference 비교

| 구분              | Training          | Inference         |
| --------------- | ----------------- | ----------------- |
| 한국어             | 학습                | 추론                |
| 목적              | 모델이 패턴을 배우게 함     | 학습된 모델로 결과 예측     |
| 정답 데이터          | 필요함               | 보통 필요 없음          |
| Loss 계산         | 함                 | 보통 안 함            |
| Gradient 계산     | 함                 | 안 함               |
| Backpropagation | 함                 | 안 함               |
| 가중치 업데이트        | 함                 | 안 함               |
| 연산량             | 매우 큼              | 상대적으로 작음          |
| 메모리 사용량         | 큼                 | 상대적으로 작음          |
| 대표 코드           | `loss.backward()` | `torch.no_grad()` |
| 결과물             | 학습된 모델 파일         | 예측 결과             |

---

## 7. 가장 큰 차이는 가중치 업데이트다

Training과 Inference를 가르는 가장 핵심적인 차이는 이것이다.

```text
Training은 가중치를 바꾼다.
Inference는 가중치를 바꾸지 않는다.
```

Training에서는 모델이 틀릴 때마다 내부 파라미터를 수정한다.

```text
이 예측은 틀렸네
어느 가중치가 문제였지?
이 방향으로 조금 수정하자
```

Inference에서는 그런 수정이 없다.

```text
입력이 들어왔다
현재 가중치로 계산한다
결과를 반환한다
```

그래서 inference는 “학습된 모델을 사용하는 단계”라고 보면 된다.

---

## 8. 식당 비유로 이해하기

비유하면 이렇다.

```text
Training = 요리사가 레시피를 연습하고 수정하는 과정
Inference = 완성된 레시피로 손님에게 음식을 만들어주는 과정
```

Training에서는 계속 시도하고 수정한다.

```text
간이 너무 짜다
소금을 줄이자
불 조절을 바꾸자
조리 시간을 수정하자
```

Inference에서는 이미 정해진 레시피대로 빠르게 만들어낸다.

```text
주문 들어옴
레시피대로 조리
음식 제공
```

즉, 학습은 “실력 향상 과정”이고, 추론은 “서비스 제공 과정”이다.

---

## 9. GPU 관점에서의 차이

Training도 GPU를 많이 쓰고, Inference도 GPU를 쓸 수 있다.

하지만 사용 방식이 다르다.

Training에서는 다음 연산이 필요하다.

```text
forward pass
loss 계산
backward pass
gradient 계산
optimizer update
```

Inference에서는 보통 이것만 필요하다.

```text
forward pass
```

여기서 forward pass는 입력을 넣고 출력까지 계산하는 과정이다.

Training은 forward 이후에 backward까지 해야 한다.

그래서 Training이 훨씬 무겁다.

```text
Training = forward + backward + update
Inference = forward only
```

이게 핵심이다.

---

## 10. 메모리 관점에서의 차이

Training은 메모리를 많이 쓴다.

왜냐하면 backward를 하기 위해 중간 계산 결과를 저장해야 하기 때문이다.

예를 들어 모델이 여러 레이어로 구성되어 있다면, 각 레이어의 중간 결과를 기억해둬야 한다.

그래야 나중에 gradient를 계산할 수 있다.

```text
입력
Layer 1 결과 저장
Layer 2 결과 저장
Layer 3 결과 저장
Loss 계산
Backward 때 저장된 값 사용
```

Inference는 backward를 하지 않는다.

그래서 중간 결과를 학습용으로 오래 저장할 필요가 적다.

그래서 일반적으로 inference가 training보다 메모리를 덜 쓴다.

---

## 11. 속도 관점에서의 차이

Training은 느리다.

이유는 단순하다.

```text
예측만 하는 게 아니라
틀린 정도를 계산하고
어떻게 고칠지도 계산하고
실제로 가중치도 수정해야 하기 때문
```

Inference는 상대적으로 빠르다.

```text
입력 넣고
출력 계산하고
결과 반환
```

그래서 AI 서비스를 운영할 때는 inference 속도가 매우 중요하다.

사용자가 질문했는데 답변이 너무 늦게 오면 서비스 품질이 떨어진다.

---

## 12. AI 서비스에서는 Inference가 운영의 핵심이다

회사에서 AI 서비스를 운영한다고 하면, 대부분 사용자 요청을 받는 단계는 inference다.

예를 들어 ChatGPT 같은 서비스도 사용자가 질문하면 그 순간 모델을 새로 학습하는 것이 아니다.

이미 학습된 모델이 있고, 사용자의 입력에 대해 출력을 생성한다.

```text
사용자 요청
토큰화
모델 추론
응답 생성
결과 반환
```

이때 중요한 것은 다음과 같다.

```text
응답 속도
GPU 메모리 사용량
동시 요청 처리
배치 처리
모델 로딩 시간
서빙 안정성
모니터링
비용 최적화
```

그래서 AI DevOps나 MLOps에서는 inference serving이 매우 중요한 주제가 된다.

---

## 13. Training 인프라에서 중요한 것

Training에서는 이런 것들이 중요하다.

```text
대용량 데이터 처리
GPU 성능
분산 학습
스토리지 속도
체크포인트 저장
실험 추적
학습 재현성
장시간 작업 안정성
```

학습은 오래 걸릴 수 있다.

몇 시간, 며칠, 큰 모델은 몇 주 이상 걸릴 수도 있다.

그래서 중간에 죽지 않게 관리하고, 죽어도 이어서 학습할 수 있게 checkpoint를 저장한다.

```text
checkpoint = 학습 중간 저장 파일
```

Training의 핵심은 “좋은 모델을 만들어내는 것”이다.

---

## 14. Inference 인프라에서 중요한 것

Inference에서는 이런 것들이 중요하다.

```text
낮은 latency
높은 throughput
GPU 메모리 효율
모델 최적화
동시 요청 처리
오토스케일링
장애 복구
모니터링
```

여기서 자주 나오는 단어가 latency와 throughput이다.

```text
latency = 요청 하나가 들어와서 응답이 나오기까지 걸리는 시간
throughput = 일정 시간 동안 처리할 수 있는 요청 수
```

Inference 서버는 사용자와 직접 연결되는 경우가 많다.

그래서 느리거나 자주 죽으면 바로 문제가 된다.

---

## 15. LLM 기준으로 보면 더 이해가 쉽다

LLM에서는 Training과 Inference 차이가 더 선명하다.

Training은 모델이 언어 패턴을 배우는 과정이다.

```text
대량의 텍스트 데이터
다음 토큰 예측
loss 계산
backpropagation
가중치 업데이트
```

Inference는 사용자의 프롬프트에 대해 답변을 생성하는 과정이다.

```text
사용자 프롬프트 입력
토큰 생성
다음 토큰 예측
반복 생성
응답 반환
```

LLM 추론에서는 특히 다음 요소가 중요하다.

```text
prefill
decode
KV cache
batching
quantization
TensorRT-LLM
vLLM
Triton Inference Server
```

처음에는 다 몰라도 된다.

핵심은 이것이다.

```text
LLM Training = 모델이 언어 패턴을 배우는 단계
LLM Inference = 학습된 모델이 답변을 생성하는 단계
```

---

## 16. 실무에서 자주 헷갈리는 지점

### 1. Fine-tuning은 Training인가?

맞다.

Fine-tuning도 Training이다.

이미 학습된 모델을 가져와서 특정 데이터로 추가 학습하는 것이기 때문이다.

```text
기존 모델
추가 데이터
loss 계산
gradient 계산
가중치 업데이트
```

가중치가 업데이트되면 training 계열로 보면 된다.

---

### 2. RAG는 Training인가 Inference인가?

RAG 자체는 보통 inference 파이프라인에 가깝다.

RAG는 모델 가중치를 바꾸는 것이 아니라, 외부 문서를 검색해서 프롬프트에 넣고 답변을 생성한다.

```text
사용자 질문
문서 검색
관련 문서 삽입
LLM 추론
답변 생성
```

즉, 일반적인 RAG는 모델을 새로 학습시키는 게 아니다.

```text
RAG = inference 시점에 외부 지식을 붙여주는 방식
```

물론 RAG 시스템의 retriever나 reranker를 따로 학습시키면 그 부분은 training이 될 수 있다.

---

### 3. Prompt engineering은 Training인가?

아니다.

Prompt engineering은 보통 inference 단계의 입력을 잘 설계하는 것이다.

모델 가중치를 바꾸지 않는다.

```text
Prompt engineering = inference 입력 설계
Fine-tuning = training으로 가중치 수정
```

---

## 17. 코드로 보는 차이

Training 코드의 핵심은 이렇다.

```python
model.train()

for x, y in train_loader:
    x = x.to(device)
    y = y.to(device)

    optimizer.zero_grad()

    output = model(x)
    loss = criterion(output, y)

    loss.backward()
    optimizer.step()
```

Inference 코드의 핵심은 이렇다.

```python
model.eval()

with torch.no_grad():
    output = model(x)
    prediction = torch.argmax(output, dim=1)
```

차이를 보면 training에는 이것이 있다.

```text
loss
backward
optimizer
가중치 업데이트
```

inference에는 이것이 없다.

```text
gradient 계산 없음
가중치 업데이트 없음
결과만 반환
```

---

## 18. 최종 정리

Training과 Inference의 차이는 이렇게 잡으면 된다.

```text
Training
= 모델을 학습시키는 과정
= 정답을 보고 loss를 계산함
= gradient를 계산함
= 가중치를 업데이트함
= 비용과 시간이 많이 듦

Inference
= 학습된 모델을 사용하는 과정
= 입력에 대해 결과를 예측함
= gradient를 계산하지 않음
= 가중치를 업데이트하지 않음
= 서비스 운영에서 중요함
```

더 짧게 말하면 이렇다.

```text
Training = 모델을 만드는 단계
Inference = 모델을 사용하는 단계
```

AI 인프라 관점에서는 이렇게도 볼 수 있다.

```text
Training infra = 좋은 모델을 안정적으로 학습시키는 환경
Inference infra = 학습된 모델을 빠르고 안정적으로 서비스하는 환경
```

결국 AI 서비스는 보통 이렇게 흘러간다.

```text
데이터 수집
모델 Training
모델 저장
모델 배포
Inference Serving
모니터링
재학습 또는 개선
```

이 흐름을 이해하면 GPU, CUDA, MLOps, AI DevOps가 왜 연결되는지도 자연스럽게 보인다.
