---
title: "[PyTorch] Linear Classifier와 Two Layer Neural Network 직접 구현하기"
source: "https://velog.io/@yorange50/PyTorch-Linear-Classifier와-Two-Layer-Neural-Network-직접-구현하기"
published: "2026-05-07T04:03:42.398Z"
tags: ""
backup_date: "2026-05-29T14:52:52.773680"
---

이번에는 PyTorch로 **선형 분류기(Linear Classifier)** 와 **2층 신경망(Two Layer Neural Network)** 을 직접 구현해보았다.

이전 KNN은 학습 데이터를 그대로 기억하고, 테스트 데이터와의 거리를 비교해서 예측하는 방식이었다.
하지만 이번에는 조금 다르다.

이번에는 모델이 직접 **가중치 W** 를 가지고 있고, 이 가중치를 학습하면서 더 좋은 분류 기준을 찾아간다.

즉 흐름은 다음과 같다.

```text
입력 데이터 X
→ 가중치 W와 곱해서 점수 scores 계산
→ loss 계산
→ gradient 계산
→ W 업데이트
→ 예측 성능 개선
```

이번 구현에서 중요한 포인트는 크게 두 가지다.

```text
1. Linear Classifier
   - SVM
   - Softmax

2. Two Layer Neural Network
   - Linear layer
   - ReLU
   - Linear layer
   - Softmax loss
   - Backpropagation
```

---

## 1. Linear Classifier란?

Linear Classifier는 말 그대로 **선형 분류기**다.

입력 데이터 `X`와 가중치 `W`를 곱해서 각 클래스별 점수를 계산한다.

```python
scores = X.matmul(W)
```

여기서 shape를 보면 다음과 같다.

```text
X: (N, D)
W: (D, C)
scores: (N, C)
```

뜻은 이렇다.

```text
N = 데이터 개수
D = 입력 데이터의 차원
C = 클래스 개수
```

예를 들어 이미지 하나를 펼쳤을 때 3072차원이고, 클래스가 10개라면 `W`는 다음과 같은 형태가 된다.

```text
W: (3072, 10)
```

입력 이미지 하나가 들어오면 각 클래스에 대한 점수가 나온다.

```text
고양이 점수
자동차 점수
비행기 점수
개 점수
...
```

그리고 가장 점수가 높은 클래스를 예측값으로 선택한다.

```python
y_pred = torch.argmax(scores, dim=1)
```

즉 Linear Classifier의 예측은 단순하다.

```text
가장 높은 score를 가진 class를 고른다
```

---

## 2. LinearClassifier 클래스 구조

코드에서는 `LinearClassifier`라는 추상 클래스를 만들고, 이를 상속해서 `LinearSVM`과 `Softmax`를 구현했다.

```python
class LinearClassifier:
```

이 클래스는 공통 기능을 담당한다.

```text
1. 가중치 W 저장
2. train 함수 제공
3. predict 함수 제공
4. save/load 기능 제공
5. loss 함수는 자식 클래스에서 구현
```

여기서 중요한 점은 `loss` 함수가 추상 메서드라는 것이다.

```python
@abstractmethod
def loss(self, W, X_batch, y_batch, reg):
    raise NotImplementedError
```

왜 이렇게 했을까?

SVM과 Softmax는 둘 다 선형 분류기다.
하지만 loss 계산 방식이 다르다.

그래서 공통 학습 구조는 부모 클래스에 두고,
구체적인 loss만 자식 클래스에서 다르게 구현한다.

```python
class LinearSVM(LinearClassifier):
    def loss(self, W, X_batch, y_batch, reg):
        return svm_loss_vectorized(W, X_batch, y_batch, reg)
```

```python
class Softmax(LinearClassifier):
    def loss(self, W, X_batch, y_batch, reg):
        return softmax_loss_vectorized(W, X_batch, y_batch, reg)
```

즉 구조는 다음과 같다.

```text
LinearClassifier
├── LinearSVM
└── Softmax
```

이렇게 하면 SVM과 Softmax가 같은 `train`, `predict` 구조를 재사용할 수 있다.

---

## 3. SVM Loss 이해하기

SVM loss는 정답 클래스의 점수가 다른 클래스 점수보다 충분히 커지도록 학습한다.

공식 느낌은 다음과 같다.

```text
margin = wrong_class_score - correct_class_score + 1
```

만약 margin이 0보다 크면 loss가 생긴다.

```python
margin = scores[j] - correct_class_score + 1

if margin > 0:
    loss += margin
```

뜻은 이렇다.

```text
정답 클래스 점수가 오답 클래스 점수보다 최소 1 이상 커야 한다.
그렇지 않으면 벌점을 준다.
```

예를 들어 정답이 고양이라고 해보자.

```text
고양이 점수: 3.2
자동차 점수: 2.8
```

이 경우 margin은 다음과 같다.

```text
2.8 - 3.2 + 1 = 0.6
```

0보다 크므로 loss가 생긴다.
왜냐하면 고양이 점수가 자동차 점수보다 높긴 하지만, 충분히 높지는 않기 때문이다.

반대로,

```text
고양이 점수: 5.0
자동차 점수: 2.8
```

이면,

```text
2.8 - 5.0 + 1 = -1.2
```

0보다 작으므로 loss가 없다.

SVM은 이런 식으로 정답 클래스 점수가 오답 클래스보다 충분히 크도록 만든다.

---

## 4. SVM Gradient 계산

naive 방식에서는 반복문을 돌면서 loss와 gradient를 동시에 계산한다.

```python
if margin > 0:
    loss += margin
    dW[:, j] += X[i]
    dW[:, y[i]] -= X[i]
```

여기서 의미는 다음과 같다.

```text
오답 클래스 j의 점수가 너무 높다
→ 오답 클래스 방향의 W는 줄여야 한다

정답 클래스 y[i]의 점수가 상대적으로 낮다
→ 정답 클래스 방향의 W는 키워야 한다
```

코드상으로는 gradient descent를 하기 때문에,

```python
W -= learning_rate * grad
```

이렇게 업데이트된다.

즉 `dW[:, j] += X[i]`는 나중에 업데이트 과정에서 오답 클래스 가중치를 낮추는 방향으로 작용한다.

---

## 5. Vectorized SVM Loss

반복문으로 구현한 SVM loss는 이해하기 쉽지만 느리다.
그래서 벡터화 버전도 구현했다.

```python
scores = X.matmul(W)
correct_class_scores = scores[torch.arange(scores.shape[0]), y].unsqueeze(1)
margins = scores - correct_class_scores + 1
margins[torch.arange(scores.shape[0]), y] = 0
```

여기서는 모든 데이터에 대해 한 번에 score를 계산한다.

```text
X.matmul(W)
→ 모든 데이터의 모든 클래스 점수 계산
```

그다음 정답 클래스 점수만 뽑아서 전체 score와 비교한다.

```text
각 오답 클래스 점수 - 정답 클래스 점수 + 1
```

그리고 0보다 작은 margin은 버린다.

```python
margins_clipped = torch.clamp(margins, min=0)
```

loss는 모든 margin을 더한 뒤 평균을 낸다.

```python
loss = margins_clipped.sum() / X.shape[0]
```

여기에 정규화 항을 더한다.

```python
loss += reg * torch.sum(W * W)
```

정규화는 가중치가 너무 커지는 것을 막기 위한 장치다.

---

## 6. Softmax Loss 이해하기

Softmax는 SVM과 다르게 점수를 확률처럼 바꾼다.

먼저 score를 계산한다.

```python
scores = X.matmul(W)
```

그리고 softmax를 적용한다.

```python
exp_scores = torch.exp(scores)
probs = exp_scores / torch.sum(exp_scores, dim=1, keepdim=True)
```

Softmax는 각 클래스 점수를 확률처럼 바꿔준다.

```text
고양이: 0.72
자동차: 0.10
개: 0.08
비행기: 0.05
...
```

그리고 정답 클래스의 확률이 높아지도록 학습한다.

loss는 다음과 같이 계산한다.

```python
correct_logprobs = -torch.log(probs[torch.arange(num_train), y])
loss = torch.sum(correct_logprobs) / num_train
```

즉 정답 클래스의 확률이 낮으면 loss가 커진다.

예를 들어 정답 클래스 확률이 0.9라면,

```text
-log(0.9) → 작음
```

정답 클래스 확률이 0.01이라면,

```text
-log(0.01) → 큼
```

그래서 Softmax + Cross Entropy는 정답 클래스 확률을 높이는 방향으로 학습된다.

---

## 7. Numeric Stability가 필요한 이유

Softmax 구현에서 중요한 부분이 있다.

```python
scores -= torch.max(scores, dim=1, keepdim=True)[0]
```

이걸 하는 이유는 **수치 안정성(Numeric Stability)** 때문이다.

Softmax는 `exp()`를 사용한다.

```python
torch.exp(scores)
```

그런데 score 값이 너무 크면 `exp()` 결과가 지나치게 커져서 overflow가 날 수 있다.

예를 들어,

```text
exp(1000)
```

같은 값은 컴퓨터가 감당하기 어렵다.

그래서 각 행에서 가장 큰 score를 빼준다.

```text
scores - max(scores)
```

이렇게 해도 softmax 결과는 변하지 않는다.
하지만 계산은 훨씬 안정적으로 된다.

---

## 8. Mini-batch Sampling

전체 데이터를 한 번에 학습하면 계산량이 너무 크다.
그래서 매번 일부 데이터만 뽑아서 학습한다.

```python
indices = torch.randint(0, num_train, (batch_size,))
X_batch = X[indices]
y_batch = y[indices]
```

이게 mini-batch 학습이다.

```text
전체 데이터 중 일부만 랜덤으로 뽑음
→ 그 batch로 loss와 gradient 계산
→ W 업데이트
→ 반복
```

이 방식이 바로 SGD, Stochastic Gradient Descent의 기본 흐름이다.

---

## 9. Linear Classifier 학습 흐름

`train_linear_classifier` 함수는 전체 학습 과정을 담당한다.

```python
for it in range(num_iters):
    X_batch, y_batch = sample_batch(X, y, num_train, batch_size)

    loss, grad = loss_func(W, X_batch, y_batch, reg)
    loss_history.append(loss.item())

    W -= learning_rate * grad
```

흐름은 아주 중요하다.

```text
1. mini-batch를 뽑는다.
2. 현재 W로 loss를 계산한다.
3. loss에 대한 gradient를 계산한다.
4. W를 gradient 반대 방향으로 이동시킨다.
5. 이 과정을 num_iters만큼 반복한다.
```

딥러닝 학습의 기본 구조가 여기서 나온다.

```text
예측
→ loss 계산
→ gradient 계산
→ parameter update
```

---

## 10. Hyperparameter Search

모델 성능은 learning rate와 regularization strength에 크게 영향을 받는다.

SVM에서는 다음 후보들을 사용했다.

```python
learning_rates = [1e-4, 1e-3, 1e-2]
regularization_strengths = [0.1, 1, 10]
```

Softmax에서는 조금 더 세분화된 후보를 사용했다.

```python
learning_rates = [1e-4, 5e-4, 1e-3, 5e-3, 1e-2]
regularization_strengths = [0.01, 0.1, 1, 10]
```

이렇게 여러 조합을 실험해서 validation accuracy가 좋은 조합을 찾는다.

```text
learning_rate가 너무 작으면 학습이 느림
learning_rate가 너무 크면 loss가 튈 수 있음

regularization이 너무 작으면 overfitting 위험
regularization이 너무 크면 underfitting 위험
```

그래서 하이퍼파라미터는 직접 여러 개 돌려보면서 찾아야 한다.

---

# Two Layer Neural Network 구현하기

이번에는 선형 분류기보다 조금 더 복잡한 모델인 **2층 신경망**을 구현했다.

구조는 다음과 같다.

```text
입력 X
→ Linear layer
→ ReLU
→ Linear layer
→ scores
→ Softmax loss
```

코드에서는 `TwoLayerNet` 클래스로 구현했다.

---

## 11. TwoLayerNet의 파라미터

2층 신경망에는 가중치와 bias가 2세트 필요하다.

```python
self.params["W1"]
self.params["b1"]
self.params["W2"]
self.params["b2"]
```

각 shape는 다음과 같다.

```text
W1: (D, H)
b1: (H,)

W2: (H, C)
b2: (C,)
```

여기서 의미는 다음과 같다.

```text
D = 입력 차원
H = hidden layer 크기
C = 클래스 개수
```

예를 들어 입력 데이터가 3072차원이고, hidden size가 100, 클래스가 10개라면 다음과 같다.

```text
W1: (3072, 100)
b1: (100,)

W2: (100, 10)
b2: (10,)
```

---

## 12. Forward Pass

forward pass는 입력이 들어왔을 때 예측 점수를 계산하는 과정이다.

```python
hidden = X.mm(W1) + b1
hidden = hidden.clamp(min=0)
scores = hidden.mm(W2) + b2
```

흐름은 다음과 같다.

```text
1. X와 W1을 곱하고 b1을 더한다.
2. ReLU를 적용한다.
3. hidden 값과 W2를 곱하고 b2를 더한다.
4. 최종 class score를 얻는다.
```

여기서 ReLU는 음수를 0으로 바꾸는 활성화 함수다.

```text
ReLU(x) = max(0, x)
```

코드에서는 `torch.relu`를 쓰지 않고 직접 구현했다.

```python
hidden = hidden.clamp(min=0)
```

예를 들면 다음과 같다.

```text
[-3, 2, -1, 5]
→ [0, 2, 0, 5]
```

ReLU를 넣으면 모델이 단순 선형 변환 하나보다 더 복잡한 패턴을 학습할 수 있다.

---

## 13. Loss 계산

2층 신경망에서도 마지막 loss는 Softmax loss를 사용한다.

```python
scores -= torch.max(scores, dim=1, keepdim=True)[0]
exp_scores = torch.exp(scores)
probs = exp_scores / torch.sum(exp_scores, dim=1, keepdim=True)
correct_logprobs = -torch.log(probs[torch.arange(N), y])
data_loss = torch.sum(correct_logprobs) / N
```

여기까지는 Softmax classifier와 비슷하다.

다만 2층 신경망은 가중치가 두 개다.

```text
W1
W2
```

그래서 regularization도 두 가중치에 대해 적용한다.

```python
reg_loss = reg * (torch.sum(W1 * W1) + torch.sum(W2 * W2))
loss = data_loss + reg_loss
```

bias에는 보통 regularization을 적용하지 않는다.

---

## 14. Backward Pass

Backward pass는 loss를 줄이기 위해 각 파라미터가 어느 방향으로 바뀌어야 하는지 계산하는 과정이다.

먼저 scores에 대한 gradient를 계산한다.

```python
dscores = probs.clone()
dscores[torch.arange(N), y] -= 1
dscores /= N
```

그다음 두 번째 layer의 gradient를 계산한다.

```python
dW2 = h1.t().mm(dscores)
db2 = torch.sum(dscores, dim=0)
```

그리고 hidden layer 쪽으로 gradient를 넘긴다.

```python
dhidden = dscores.mm(W2.t())
```

ReLU를 통과한 부분도 고려해야 한다.

```python
dhidden[h1 <= 0] = 0
```

ReLU는 forward 때 0 이하 값을 0으로 만들었다.
그래서 backward 때도 0 이하였던 부분은 gradient가 흐르지 않는다.

마지막으로 첫 번째 layer의 gradient를 계산한다.

```python
dW1 = X.t().mm(dhidden)
db1 = torch.sum(dhidden, dim=0)
```

그리고 regularization gradient도 더한다.

```python
dW2 += 2 * reg * W2
dW1 += 2 * reg * W1
```

최종적으로 gradient는 딕셔너리에 저장된다.

```python
grads["W1"] = dW1
grads["b1"] = db1
grads["W2"] = dW2
grads["b2"] = db2
```

---

## 15. Two Layer Net 학습 흐름

학습 함수인 `nn_train`도 Linear Classifier와 구조가 거의 같다.

```python
for it in range(num_iters):
    X_batch, y_batch = sample_batch(X, y, num_train, batch_size)

    loss, grads = loss_func(params, X_batch, y=y_batch, reg=reg)
    loss_history.append(loss.item())

    for param_name in params:
        params[param_name] -= learning_rate * grads[param_name]
```

흐름은 다음과 같다.

```text
1. mini-batch를 뽑는다.
2. forward pass로 scores를 계산한다.
3. softmax loss를 계산한다.
4. backward pass로 gradient를 계산한다.
5. W1, b1, W2, b2를 업데이트한다.
```

여기서 Linear Classifier와 다른 점은 업데이트할 파라미터가 하나가 아니라 여러 개라는 것이다.

Linear Classifier는 `W` 하나만 업데이트했다.

```text
W
```

Two Layer Net은 네 개를 업데이트한다.

```text
W1, b1, W2, b2
```

---

## 16. Learning Rate Decay

2층 신경망 학습에서는 learning rate decay도 사용했다.

```python
learning_rate *= learning_rate_decay
```

이건 학습이 진행될수록 learning rate를 조금씩 줄이는 방식이다.

처음에는 크게 이동하면서 빠르게 학습하고,
나중에는 작게 이동하면서 세밀하게 조정하는 느낌이다.

```text
초반: 큰 보폭
후반: 작은 보폭
```

예를 들어 learning rate가 0.1이고 decay가 0.95라면, epoch마다 다음처럼 줄어든다.

```text
0.1
0.095
0.09025
...
```

---

## 17. Prediction

예측은 forward pass를 한 뒤 가장 높은 score를 고르면 된다.

```python
scores, _ = nn_forward_pass(params, X)
y_pred = torch.argmax(scores, dim=1)
```

즉 학습 때는 loss와 gradient가 필요하지만,
예측 때는 gradient가 필요 없다.

```text
학습: scores → loss → gradient → update
예측: scores → argmax
```

---

## 18. Best Net 찾기

`find_best_net` 함수에서는 여러 하이퍼파라미터 조합을 돌려보면서 validation accuracy가 가장 높은 모델을 찾는다.

후보는 다음과 같다.

```python
learning_rates = [1e-1, 5e-1, 1e0]
hidden_sizes = [50, 100, 200]
regularization_strengths = [1e-4, 1e-3, 1e-2]
learning_rate_decays = [0.95, 0.9]
```

전체 조합을 돌면서 모델을 학습한다.

```python
for lr in learning_rates:
    for hs in hidden_sizes:
        for reg in regularization_strengths:
            for lr_decay in learning_rate_decays:
```

각 조합마다 모델을 새로 만들고 학습한 뒤 validation accuracy를 확인한다.

```python
if val_acc > best_val_acc:
    best_val_acc = val_acc
    best_net = net
    best_stat = stats
```

즉 이 함수의 목적은 단순하다.

```text
여러 설정으로 학습해보고
검증 성능이 가장 좋은 모델을 선택한다
```

---

# Linear Classifier와 Two Layer Net 차이

둘의 가장 큰 차이는 hidden layer가 있느냐 없느냐다.

| 구분    | Linear Classifier | Two Layer Neural Network    |
| ----- | ----------------- | --------------------------- |
| 구조    | X → W → scores    | X → W1 → ReLU → W2 → scores |
| 파라미터  | W                 | W1, b1, W2, b2              |
| 비선형성  | 없음                | ReLU 있음                     |
| 표현력   | 비교적 단순            | 더 복잡한 패턴 학습 가능              |
| 학습 방식 | SGD               | SGD                         |
| Loss  | SVM 또는 Softmax    | Softmax                     |

Linear Classifier는 입력을 바로 class score로 바꾼다.

```text
X → scores
```

Two Layer Net은 중간에 hidden representation을 만든다.

```text
X → hidden → scores
```

이 hidden layer 덕분에 단순 선형 분류기보다 더 복잡한 데이터 구조를 표현할 수 있다.

---

# 전체 흐름 정리

이번 구현의 전체 흐름은 다음과 같다.

```text
1. Linear Classifier 구현
2. SVM loss naive/vectorized 구현
3. Softmax loss naive/vectorized 구현
4. mini-batch sampling 구현
5. SGD 학습 루프 구현
6. predict 함수 구현
7. Two Layer Neural Network 구현
8. forward pass 구현
9. softmax loss 계산
10. backward pass로 gradient 계산
11. W1, b1, W2, b2 업데이트
12. validation accuracy 기준으로 best model 선택
```

핵심은 결국 이 구조다.

```text
scores 계산
→ loss 계산
→ gradient 계산
→ parameter update
```

KNN에서는 학습 데이터와의 거리를 비교했다면,
이번에는 모델이 직접 가중치를 가지고 학습한다.

그리고 Linear Classifier에서 Two Layer Net으로 넘어가면서,
단순한 선형 모델에서 hidden layer와 ReLU를 가진 신경망 구조로 확장된다.

---

# 마무리

이번 구현을 통해 머신러닝 모델 학습의 기본 흐름을 직접 확인할 수 있었다.

처음에는 SVM, Softmax, gradient, backpropagation 같은 단어가 복잡하게 느껴질 수 있다.
하지만 코드 흐름만 놓고 보면 구조는 반복된다.

```text
입력 데이터를 넣는다
점수를 계산한다
loss를 계산한다
gradient를 구한다
가중치를 업데이트한다
성능을 확인한다
```

Linear Classifier는 이 구조를 가장 단순한 형태로 보여준다.
Two Layer Neural Network는 여기에 hidden layer와 ReLU가 추가된 구조다.

즉 이번 코드는 딥러닝 프레임워크가 내부에서 해주는 일을 직접 구현해보는 과정이라고 볼 수 있다.

PyTorch의 `nn.Module`, `CrossEntropyLoss`, `optimizer.step()` 같은 기능을 쓰면 훨씬 짧게 구현할 수 있지만,
한 번쯤 이렇게 직접 구현해보면 모델이 실제로 어떻게 학습되는지 훨씬 명확하게 이해할 수 있다.
