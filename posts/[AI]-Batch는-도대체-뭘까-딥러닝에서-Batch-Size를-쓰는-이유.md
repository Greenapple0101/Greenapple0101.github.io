---
title: "[AI] Batch는 도대체 뭘까? 딥러닝에서 Batch Size를 쓰는 이유"
source: "https://velog.io/@yorange50/AI-Batch는-도대체-뭘까-딥러닝에서-Batch-Size를-쓰는-이유"
published: "2026-05-07T06:30:43.784Z"
tags: ""
backup_date: "2026-05-29T14:52:52.772196"
---

딥러닝을 공부하다 보면 계속 나오는 단어가 있다.

```text
batch
batch size
mini-batch
DataLoader
```

처음에는 그냥 “데이터 묶음” 정도로 보이는데, 실제로는 학습 속도, GPU 메모리, 성능, 추론 처리량과 연결되는 중요한 개념이다.

---

## 1. Batch 한 줄 정의

Batch는 **한 번에 모델에 넣는 데이터 묶음**이다.

예를 들어 이미지 데이터가 1,000장 있다고 하자.

이걸 한 장씩 모델에 넣을 수도 있고, 32장씩 묶어서 넣을 수도 있다.

```text
전체 데이터: 1000장
batch size: 32

한 번에 32장씩 모델에 넣음
```

즉, batch size는 이런 뜻이다.

```text
batch size = 한 번의 forward/backward에 사용하는 데이터 개수
```

---

## 2. 왜 한 장씩 안 넣고 묶어서 넣을까?

이미지 한 장씩 넣으면 이런 방식이다.

```text
이미지 1장 넣기
예측
loss 계산
가중치 업데이트

이미지 1장 넣기
예측
loss 계산
가중치 업데이트
```

이 방식은 너무 자주 업데이트한다.

반대로 전체 데이터 1,000장을 한 번에 넣으면 GPU 메모리가 부족할 수 있다.

그래서 보통 중간 방식을 쓴다.

```text
전체 데이터도 아니고
한 장씩도 아니고
적당히 묶어서 넣기
```

이게 mini-batch 학습이다.

실무에서 그냥 batch라고 하면 대부분 mini-batch를 의미하는 경우가 많다.

---

## 3. Batch Size 예시

데이터가 1,000개 있고 batch size가 100이면 이렇게 나뉜다.

```text
Batch 1: 1~100번 데이터
Batch 2: 101~200번 데이터
Batch 3: 201~300번 데이터
...
Batch 10: 901~1000번 데이터
```

즉, 한 epoch 동안 총 10번의 batch가 돈다.

```text
전체 데이터 개수 / batch size = 한 epoch의 step 수
1000 / 100 = 10 steps
```

---

## 4. Epoch, Batch, Iteration 관계

이 셋이 자주 헷갈린다.

```text
Epoch = 전체 데이터셋을 한 번 다 학습하는 것
Batch = 한 번에 모델에 넣는 데이터 묶음
Iteration/Step = batch 하나를 처리하는 한 번의 학습 과정
```

예를 들어 데이터가 1,000개이고 batch size가 100이면

```text
1 epoch = 전체 1000개를 한 번 다 봄
1 batch = 100개
1 epoch = 10 iterations
```

정리하면 이렇다.

```text
데이터 1000개
batch size 100
epoch 1

=> batch 10개
=> iteration 10번
=> 전체 데이터 1번 학습
```

---

## 5. PyTorch에서 Batch는 어떻게 생겼을까?

이미지 한 장의 shape이 이렇게 생겼다고 하자.

```text
[3, 32, 32]
```

의미는 이렇다.

```text
3 = channel
32 = height
32 = width
```

이미지 한 장이면 `[C, H, W]` 형태다.

그런데 batch size가 64라면 입력 shape은 이렇게 된다.

```text
[64, 3, 32, 32]
```

앞에 batch 차원이 붙는다.

```text
[N, C, H, W]
```

여기서 N이 batch size다.

```text
N = 64
C = 3
H = 32
W = 32
```

즉, 모델은 이미지 한 장이 아니라 **이미지 64장을 한 번에 받는 것**이다.

---

## 6. 코드로 보는 Batch

PyTorch에서는 보통 `DataLoader`가 batch를 만들어준다.

```python
from torch.utils.data import DataLoader

train_loader = DataLoader(
    train_dataset,
    batch_size=64,
    shuffle=True
)
```

이제 반복문을 돌면 `x`, `y`가 한 개 샘플이 아니라 batch 단위로 나온다.

```python
for x, y in train_loader:
    print(x.shape)
    print(y.shape)
    break
```

이미지 데이터라면 보통 이런 식으로 나온다.

```text
x.shape = [64, 3, 32, 32]
y.shape = [64]
```

의미는 이렇다.

```text
x = 이미지 64장
y = 정답 라벨 64개
```

---

## 7. Training에서 Batch가 하는 일

학습 코드는 보통 이렇게 생겼다.

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

여기서 `x`는 데이터 하나가 아니다.

```text
x = batch 단위 입력
```

즉, 모델은 한 번에 여러 데이터를 예측한다.

```text
64개 입력
↓
모델 forward
↓
64개 예측 결과
↓
64개 정답과 비교
↓
평균 loss 계산
↓
gradient 계산
↓
가중치 업데이트
```

대부분 loss 함수는 batch 안의 loss를 평균내서 하나의 loss 값으로 만든다.

---

## 8. Batch Size가 크면 좋은가?

무조건 좋은 것은 아니다.

Batch size가 크면 장점이 있다.

```text
GPU 병렬 연산을 잘 활용함
한 번에 많은 데이터를 처리함
학습 속도가 빨라질 수 있음
gradient가 안정적일 수 있음
```

하지만 단점도 있다.

```text
GPU 메모리를 많이 사용함
너무 크면 일반화 성능이 떨어질 수 있음
업데이트 횟수가 줄어듦
메모리 부족 에러가 날 수 있음
```

예를 들어 batch size를 크게 잡으면 이런 에러가 날 수 있다.

```text
CUDA out of memory
```

이건 GPU 메모리가 부족하다는 뜻이다.

이럴 때 가장 먼저 해볼 수 있는 것은 batch size를 줄이는 것이다.

```text
batch_size = 128
↓
batch_size = 64
↓
batch_size = 32
↓
batch_size = 16
```

---

## 9. Batch Size가 작으면?

Batch size가 작으면 장점도 있다.

```text
GPU 메모리를 적게 사용함
더 자주 가중치를 업데이트함
작은 GPU에서도 학습 가능함
```

하지만 단점도 있다.

```text
학습이 불안정할 수 있음
GPU 활용률이 낮을 수 있음
학습 시간이 길어질 수 있음
gradient가 noisy할 수 있음
```

여기서 noisy하다는 것은 batch마다 gradient 방향이 흔들릴 수 있다는 뜻이다.

예를 들어 한 batch에는 고양이 이미지가 많고, 다음 batch에는 자동차 이미지가 많으면 loss와 gradient가 출렁일 수 있다.

그래서 보통 데이터를 섞는다.

```python
DataLoader(train_dataset, batch_size=64, shuffle=True)
```

`shuffle=True`는 매 epoch마다 데이터를 섞어서 batch 구성을 다양하게 만드는 역할을 한다.

---

## 10. Batch와 GPU의 관계

GPU는 병렬 연산에 강하다.

그래서 데이터 하나만 넣는 것보다 여러 개를 묶어서 넣을 때 GPU를 더 잘 활용할 수 있다.

```text
batch size 1
= GPU에 일감을 조금만 줌

batch size 64
= GPU에 한 번에 많은 일감을 줌
```

하지만 너무 크게 넣으면 GPU 메모리가 터진다.

```text
batch size가 너무 작음
=> GPU가 덜 바쁨

batch size가 너무 큼
=> GPU 메모리 부족
```

그래서 실무에서는 GPU 메모리가 허용하는 범위 안에서 적절한 batch size를 찾는다.

---

## 11. Inference에서 Batch는 또 다르다

Batch는 training에서만 쓰는 게 아니다.

Inference에서도 batch를 쓴다.

예를 들어 사용자 요청 1개씩 처리하면 batch size 1이다.

```text
요청 1개
모델 추론
응답 1개
```

하지만 여러 요청을 모아서 한 번에 처리할 수도 있다.

```text
요청 8개 모음
모델 추론 1번
응답 8개 반환
```

이걸 batching이라고 한다.

Inference batching은 throughput을 높이는 데 도움이 된다.

```text
throughput = 일정 시간 동안 처리할 수 있는 요청 수
```

특히 GPU 서버에서는 요청을 하나씩 처리하는 것보다, 여러 요청을 묶어서 처리하는 것이 효율적일 때가 많다.

---

## 12. Latency와 Throughput의 충돌

Inference batch를 키우면 throughput은 좋아질 수 있다.

하지만 latency는 나빠질 수 있다.

```text
batch를 만들기 위해 요청을 잠깐 기다림
↓
사용자 입장에서는 응답이 늦어짐
```

정리하면 이렇다.

```text
batch size 증가
=> GPU 효율 증가
=> throughput 증가 가능
=> 개별 요청 latency 증가 가능
```

그래서 실시간 서비스에서는 batch size를 무작정 크게 잡지 않는다.

사용자 응답 속도와 서버 처리량 사이에서 균형을 잡아야 한다.

---

## 13. Training Batch vs Inference Batch

| 구분       | Training Batch         | Inference Batch             |
| -------- | ---------------------- | --------------------------- |
| 목적       | 학습 효율과 gradient 계산     | 추론 처리량 향상                   |
| 정답 y     | 있음                     | 보통 없음                       |
| backward | 있음                     | 없음                          |
| 가중치 업데이트 | 있음                     | 없음                          |
| 중요 포인트   | loss, gradient, memory | latency, throughput, memory |
| 너무 크면    | CUDA OOM               | latency 증가, CUDA OOM        |
| 너무 작으면   | 학습 느림, 불안정             | GPU 활용률 낮음                  |

---

## 14. Batch Size와 Gradient

Training에서 batch size는 gradient 계산에 직접 영향을 준다.

batch size가 1이면 데이터 하나 기준으로 gradient를 계산한다.

```text
데이터 1개 보고
loss 계산
gradient 계산
업데이트
```

batch size가 64이면 데이터 64개 기준으로 평균 loss를 계산하고 gradient를 계산한다.

```text
데이터 64개 보고
평균 loss 계산
gradient 계산
업데이트
```

즉, batch size가 크면 더 많은 데이터의 평균 방향으로 업데이트한다.

```text
작은 batch
= 자주 움직이지만 방향이 흔들릴 수 있음

큰 batch
= 덜 자주 움직이지만 방향이 안정적일 수 있음
```

---

## 15. Batch Size를 정하는 기준

처음 실험할 때는 보통 이런 식으로 잡는다.

```text
이미지 모델: 32, 64, 128
작은 모델: 64 이상도 가능
큰 모델: 1, 2, 4, 8도 가능
LLM fine-tuning: 매우 작은 batch + gradient accumulation 사용
```

현실적으로는 가장 먼저 GPU 메모리가 기준이 된다.

```text
1. batch size를 적당히 잡는다.
2. CUDA out of memory가 나는지 본다.
3. OOM이 나면 줄인다.
4. GPU 메모리가 많이 남으면 조금 키워본다.
5. 학습 안정성과 성능을 같이 본다.
```

---

## 16. Gradient Accumulation은 왜 나올까?

큰 batch size를 쓰고 싶은데 GPU 메모리가 부족할 수 있다.

예를 들어 batch size 64 효과를 내고 싶은데 GPU에는 16밖에 안 올라간다고 하자.

이때 gradient accumulation을 쓴다.

```text
batch 16으로 4번 forward/backward
optimizer.step()은 한 번만
```

그러면 효과적으로는 batch size 64처럼 동작한다.

```text
16 × 4 = 64
```

코드 느낌은 이렇다.

```python
accumulation_steps = 4

for step, (x, y) in enumerate(train_loader):
    x = x.to(device)
    y = y.to(device)

    output = model(x)
    loss = criterion(output, y)
    loss = loss / accumulation_steps

    loss.backward()

    if (step + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

핵심은 매 batch마다 업데이트하지 않고, gradient를 몇 번 모은 뒤 업데이트하는 것이다.

---

## 17. Batch 관련 자주 나는 에러

### 1. Shape mismatch

```text
Expected input shape [N, C, H, W]
but got [C, H, W]
```

이미지 한 장을 넣을 때 batch 차원을 빼먹은 경우다.

```python
x = x.unsqueeze(0)
```

---

### 2. CUDA out of memory

```text
CUDA out of memory
```

batch size가 너무 클 가능성이 크다.

```python
batch_size = 64
```

에서 안 되면

```python
batch_size = 32
```

로 줄여본다.

---

### 3. 마지막 batch 크기가 다름

데이터 개수가 batch size로 딱 나누어떨어지지 않으면 마지막 batch는 작을 수 있다.

예를 들어 데이터 100개, batch size 32면

```text
32
32
32
4
```

마지막 batch는 4개다.

특정 코드가 batch size를 고정값으로 가정하면 에러가 날 수 있다.

필요하면 DataLoader에서 이렇게 설정할 수 있다.

```python
DataLoader(dataset, batch_size=32, drop_last=True)
```

`drop_last=True`는 마지막 남는 batch를 버린다는 뜻이다.

---

## 18. 최종 정리

Batch는 딥러닝에서 “한 번에 처리하는 데이터 묶음”이다.

```text
batch = 모델에 한 번에 넣는 데이터 묶음
batch size = 그 묶음 안의 데이터 개수
```

Training에서는 batch가 loss와 gradient 계산 단위가 된다.

```text
batch 입력
forward
loss 계산
backward
optimizer step
```

Inference에서는 batch가 GPU 처리 효율과 throughput에 영향을 준다.

```text
여러 요청을 묶어서
한 번에 forward
여러 결과 반환
```

결국 batch를 이해하면 PyTorch 코드가 훨씬 잘 보인다.

```python
for x, y in train_loader:
    output = model(x)
```

여기서 `x`는 데이터 하나가 아니라 batch다.

그리고 shape의 맨 앞 차원은 대부분 batch size다.

```text
[N, C, H, W]
N = batch size
```

한 문장으로 정리하면 이렇다.

```text
Batch는 GPU에게 한 번에 줄 일감의 크기다.
```

너무 작으면 GPU가 덜 바쁘고, 너무 크면 메모리가 터진다.
그래서 batch size는 성능, 메모리, 속도 사이에서 맞춰야 하는 중요한 조절값이다.
