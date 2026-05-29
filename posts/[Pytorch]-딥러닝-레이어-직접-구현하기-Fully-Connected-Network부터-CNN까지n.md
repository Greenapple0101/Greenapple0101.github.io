---
title: "[PyTorch] 딥러닝 레이어 직접 구현하기: Fully Connected Network부터 CNN까지\n"
source: "https://velog.io/@yorange50/PyTorch-딥러닝-레이어-직접-구현하기-Fully-Connected-Network부터-CNN까지"
published: "2026-05-07T04:07:03.616Z"
tags: ""
backup_date: "2026-05-29T14:52:52.773384"
---

이번에는 PyTorch를 이용해서 딥러닝 모델의 핵심 구성요소를 직접 구현해보았다.

보통 PyTorch로 모델을 만들 때는 `torch.nn.Linear`, `torch.nn.ReLU`, `torch.nn.Conv2d`, `torch.optim.Adam` 같은 기능을 바로 사용한다.
하지만 이번 구현에서는 이런 기능들이 내부적으로 어떻게 동작하는지 이해하기 위해 **Linear layer, ReLU, Dropout, Optimizer, Convolution, Pooling, BatchNorm, CNN 구조**를 직접 작성했다.

이번 코드의 핵심은 단순히 모델을 “사용”하는 것이 아니라, 딥러닝 학습 과정의 내부 구조를 직접 확인하는 것이다.

```text id="fcf2gx"
입력 데이터
→ forward pass
→ loss 계산
→ backward pass
→ gradient 계산
→ parameter update
```

이 흐름이 Fully Connected Network와 Convolutional Network 모두에서 반복된다.

---

## 1. 딥러닝 구현의 핵심: Forward와 Backward

이번 코드에서 가장 중요한 구조는 모든 레이어가 `forward`와 `backward`를 가진다는 점이다.

```python id="jr7ijq"
out, cache = Layer.forward(x, w, b)
dx, dw, db = Layer.backward(dout, cache)
```

`forward`는 입력 데이터를 받아 출력값을 계산하는 과정이다.
`backward`는 loss에서부터 거꾸로 내려온 gradient를 이용해 각 파라미터의 gradient를 계산하는 과정이다.

즉 딥러닝 학습은 다음 흐름으로 진행된다.

```text id="ywknfe"
forward:
입력 → 예측값 계산

loss:
예측값과 정답 비교

backward:
loss를 줄이기 위해 각 파라미터가 어떻게 변해야 하는지 계산

update:
gradient를 이용해 파라미터 수정
```

이 구조를 이해하면 PyTorch가 내부에서 해주는 자동 미분과 optimizer의 역할도 훨씬 잘 보인다.

---

## 2. cache는 왜 필요할까?

코드에서 자주 등장하는 개념이 `cache`다.

```python id="52p87v"
cache = (x, w, b)
```

처음 보면 단순히 값을 저장하는 변수처럼 보이지만, 사실 `cache`는 backward를 위해 꼭 필요하다.

예를 들어 Linear layer의 backward를 계산하려면 forward 때 사용했던 입력 `x`, 가중치 `w`, bias `b`가 필요하다. 그래서 forward가 끝날 때 이 값들을 `cache`에 저장해두고, backward에서 다시 꺼내 쓴다.

정리하면 다음과 같다.

```text id="bxkr48"
cache = backward 계산을 위해 forward 때 남겨두는 중간 기록
```

딥러닝 구현에서는 forward 결과만 중요한 것이 아니라, backward에 필요한 중간값을 잘 저장하는 것도 중요하다.

---

## 3. Linear Layer 직접 구현하기

Fully Connected Network의 가장 기본이 되는 레이어는 Linear layer다.

코드에서는 입력을 2차원으로 펼친 뒤 행렬곱을 수행한다.

```python id="ir7jrf"
x_reshaped = x.view(N, D)
out = x_reshaped.mm(w) + b
```

여기서 shape는 다음과 같다.

```text id="tza18n"
x: (N, D)
w: (D, M)
b: (M,)
out: (N, M)
```

의미는 다음과 같다.

```text id="7v7h6u"
N = 데이터 개수
D = 입력 차원
M = 출력 차원
```

이미지 데이터는 원래 `(N, C, H, W)` 형태일 수 있다.
하지만 Linear layer에 넣기 위해서는 한 줄짜리 벡터로 펼쳐야 한다.

예를 들어 CIFAR-10 이미지는 보통 다음과 같은 형태다.

```text id="k0tvaj"
3 x 32 x 32 = 3072
```

따라서 이미지 한 장은 3072차원 벡터로 바뀐다.

Linear layer의 backward에서는 세 가지 gradient를 계산한다.

```text id="a2h34x"
dx: 입력 x에 대한 gradient
dw: 가중치 w에 대한 gradient
db: bias b에 대한 gradient
```

코드에서는 `db`, `dw`, `dx`를 각각 계산한 뒤 원래 입력 shape로 되돌린다. 

---

## 4. ReLU 직접 구현하기

ReLU는 딥러닝에서 가장 많이 쓰이는 활성화 함수 중 하나다.

```text id="2u96mr"
ReLU(x) = max(0, x)
```

코드에서는 `torch.clamp`를 이용해 음수를 0으로 바꾼다.

```python id="mzbfh3"
out = torch.clamp(x, min=0)
```

예를 들면 다음과 같다.

```text id="7gatye"
입력: [-3, 2, -1, 5]
출력: [0, 2, 0, 5]
```

backward에서는 forward 때 0보다 작았던 값에는 gradient를 흘리지 않는다.

```python id="4h0lw3"
dx = dout.clone()
dx[x < 0] = 0
```

즉 ReLU는 forward에서는 음수를 제거하고, backward에서는 음수였던 영역의 gradient를 막는다. 

ReLU가 중요한 이유는 신경망에 **비선형성**을 넣어주기 때문이다.

Linear layer만 여러 개 쌓으면 결국 하나의 큰 Linear layer와 비슷해진다.
하지만 중간에 ReLU를 넣으면 모델이 더 복잡한 패턴을 학습할 수 있다.

---

## 5. Linear_ReLU: 레이어를 묶어서 쓰기

코드에서는 `Linear`와 `ReLU`를 따로 구현한 뒤, 둘을 묶은 `Linear_ReLU`도 구현했다.

```python id="ycn2y9"
a, fc_cache = Linear.forward(x, w, b)
out, relu_cache = ReLU.forward(a)
cache = (fc_cache, relu_cache)
```

이 구조는 다음을 의미한다.

```text id="i2d2hs"
Linear → ReLU
```

backward는 반대로 진행된다.

```text id="7lrj4w"
ReLU backward → Linear backward
```

이런 식으로 여러 레이어를 하나의 묶음처럼 다루는 구조를 **sandwich layer** 또는 **convenience layer**처럼 볼 수 있다.

이렇게 하면 모델을 만들 때 코드가 훨씬 깔끔해진다.

---

## 6. TwoLayerNet 구현하기

`TwoLayerNet`은 가장 기본적인 2층 신경망이다.

구조는 다음과 같다.

```text id="c1z7fv"
Linear → ReLU → Linear → Softmax
```

코드에서는 `W1`, `b1`, `W2`, `b2` 네 개의 파라미터를 사용한다.

```python id="kh5cw7"
self.params['W1']
self.params['b1']
self.params['W2']
self.params['b2']
```

첫 번째 layer는 입력을 hidden representation으로 바꾼다.

```text id="2zxl4l"
입력 X → hidden layer
```

두 번째 layer는 hidden representation을 class score로 바꾼다.

```text id="1lrbf2"
hidden layer → class scores
```

forward 흐름은 다음과 같다.

```python id="42ylk5"
out1, cache1 = Linear_ReLU.forward(X, W1, b1)
scores, cache2 = Linear.forward(out1, W2, b2)
```

정답 라벨 `y`가 없으면 test mode이므로 score만 반환한다.

```python id="8s2zqs"
if y is None:
    return scores
```

정답 라벨이 있으면 train mode이므로 softmax loss를 계산하고 backward를 수행한다. 

---

## 7. Regularization 적용하기

모델이 학습 데이터에만 과하게 맞춰지는 현상을 overfitting이라고 한다.
이를 줄이기 위해 L2 regularization을 사용한다.

TwoLayerNet에서는 loss에 다음 항을 더한다.

```python id="0gpo26"
loss += self.reg * (torch.sum(W1 * W1) + torch.sum(W2 * W2))
```

그리고 gradient에도 regularization을 반영한다.

```python id="xbm064"
dW2 += 2 * self.reg * W2
dW1 += 2 * self.reg * W1
```

여기서 중요한 점은 loss에만 regularization을 더하면 안 된다는 것이다.
실제로 파라미터 업데이트가 바뀌려면 gradient에도 regularization 항이 들어가야 한다.

정리하면 다음과 같다.

```text id="68y8fh"
loss에 regularization 추가
gradient에도 regularization 추가
```

---

## 8. FullyConnectedNet 구현하기

`TwoLayerNet`은 hidden layer가 하나인 고정된 구조다.
반면 `FullyConnectedNet`은 원하는 만큼 hidden layer를 쌓을 수 있다.

```python id="6syp4h"
hidden_dims = [100, 100, 100]
```

이면 구조는 다음과 같다.

```text id="pbsme9"
Linear → ReLU
Linear → ReLU
Linear → ReLU
Linear → Softmax
```

코드에서는 layer 수를 다음처럼 계산한다.

```python id="8nshd4"
self.num_layers = 1 + len(hidden_dims)
```

그리고 반복문으로 `W1`, `b1`, `W2`, `b2` 등을 만든다.

```python id="jz77s9"
layer_dims = [input_dim] + hidden_dims + [num_classes]

for i in range(1, self.num_layers + 1):
    W = weight_scale * torch.randn(layer_dims[i-1], layer_dims[i])
    b = torch.zeros(layer_dims[i])
    self.params[f'W{i}'] = W
    self.params[f'b{i}'] = b
```

이 구조가 중요한 이유는 모델을 더 깊게 만들 수 있기 때문이다.
즉 `FullyConnectedNet`은 `TwoLayerNet`을 일반화한 버전이다. 

---

## 9. Dropout 이해하기

`FullyConnectedNet`에서는 dropout도 선택적으로 사용할 수 있다.

```python id="wr6p5h"
self.use_dropout = dropout != 0
```

Dropout은 학습 중 일부 뉴런을 랜덤하게 꺼서 모델이 특정 뉴런에만 의존하지 않도록 만드는 기법이다.

```text id="11c0g4"
train mode:
일부 뉴런을 랜덤하게 제거

test mode:
전체 뉴런 사용
```

코드에서는 dropout을 사용하는 경우 forward 중간에 dropout을 적용하고, backward 때도 dropout backward를 거친다.

```python id="x40oa0"
if self.use_dropout:
    out, dropout_cache = Dropout.forward(out, self.dropout_param)
```

Dropout에서 중요한 점은 train mode와 test mode의 동작이 다르다는 것이다.

학습 중에는 랜덤하게 일부 값을 제거하지만, 테스트 때는 제거하지 않는다.

---

## 10. Optimizer 직접 구현하기

이번 코드에서는 optimizer도 직접 구현했다.

가장 기본적인 방식은 SGD다.

```python id="y2swsq"
w = w - learning_rate * dw
```

의미는 단순하다.

```text id="m6zc8i"
현재 가중치에서
learning_rate × gradient 만큼 빼기
```

즉 loss를 줄이는 방향으로 파라미터를 이동시키는 것이다.

Momentum은 여기에 이전 이동 방향을 반영한다.

```python id="638klo"
v = config['momentum'] * v - config['learning_rate'] * dw
next_w = w + v
```

SGD는 현재 gradient만 보고 움직인다.
Momentum은 이전에 움직이던 방향까지 고려해서 더 부드럽게 이동한다. 

정리하면 다음과 같다.

```text id="4s42g1"
SGD:
현재 gradient만 보고 이동

Momentum:
이전 이동 방향을 기억하면서 이동

RMSProp / Adam:
gradient 크기에 따라 파라미터별 learning rate를 조절
```

---

# CNN 구현하기

Fully Connected Network는 입력 이미지를 모두 펼쳐서 처리한다.
하지만 이미지는 공간 구조가 중요하다.

예를 들어 이미지에서 “눈”, “모서리”, “질감”, “윤곽” 같은 정보는 위치와 주변 픽셀 관계가 중요하다.
이런 공간 정보를 더 잘 활용하는 모델이 CNN이다.

---

## 11. Convolution Layer 직접 구현하기

Convolution layer는 필터가 이미지를 훑으면서 특징을 추출하는 레이어다.

```text id="oi2wag"
입력 이미지
→ 필터 적용
→ feature map 생성
```

코드에서는 convolution output 크기를 다음처럼 계산한다.

```python id="981pv9"
H_out = 1 + (H + 2 * pad - HH) // stride
W_out = 1 + (W + 2 * pad - WW) // stride
```

여기서 중요한 값은 세 가지다.

```text id="t8m03c"
filter size
stride
padding
```

`filter size`는 필터의 크기다.
`stride`는 필터가 몇 칸씩 이동하는지다.
`padding`은 입력 주변을 0으로 감싸서 크기 감소를 조절하는 방식이다.

실제 convolution은 다음처럼 window를 잘라서 필터와 곱한 뒤 더하는 방식으로 구현된다.

```python id="ie4516"
window = x_padded[n, :, h_start:h_end, w_start:w_end]
out[n, f, i, j] = torch.sum(window * w[f]) + b[f]
```

이 구현은 반복문이 많아서 느리지만, convolution이 실제로 어떤 식으로 동작하는지 이해하기 좋다. 

---

## 12. Convolution Backward

Convolution backward에서는 세 가지 gradient를 계산한다.

```text id="s8x6j5"
dx: 입력 이미지에 대한 gradient
dw: 필터에 대한 gradient
db: bias에 대한 gradient
```

코드에서는 forward 때와 같은 window를 기준으로 `dw`와 `dx`를 누적한다.

```python id="3ofkzi"
dw[f] += window * dout[n, f, i, j]
dx_padded[n, :, h_start:h_end, w_start:w_end] += w[f] * dout[n, f, i, j]
```

padding이 들어갔던 경우에는 마지막에 padding 부분을 제거해서 원래 입력 크기의 `dx`를 만든다.

```python id="48l35f"
dx = dx_padded[:, :, pad:-pad, pad:-pad]
```

Convolution backward는 수식 자체보다 “각 window가 gradient를 어떻게 나눠 받는지”를 이해하는 게 중요하다.

---

## 13. FastConv

직접 구현한 convolution은 원리 이해에는 좋지만 실제 학습에는 너무 느리다.

그래서 빠른 버전에서는 PyTorch의 내장 함수를 사용한다.

```python id="fbpg2v"
out = torch.nn.functional.conv2d(
    x, w, b,
    stride=conv_param['stride'],
    padding=conv_param['pad']
)
```

backward는 `torch.autograd.grad`를 사용해서 계산한다.

```python id="j9uz42"
grads = torch.autograd.grad(
    outputs=out,
    inputs=(x, w, b),
    grad_outputs=dout
)
```

즉 FastConv는 직접 구현한 convolution과 같은 역할을 하지만, PyTorch 내부 최적화와 autograd를 이용해 훨씬 빠르게 동작한다. 

---

## 14. Max Pooling

Max Pooling은 feature map의 크기를 줄이면서 중요한 값만 남기는 연산이다.

예를 들어 2x2 영역에서 가장 큰 값만 선택한다.

```text id="g0fwvi"
[1, 3]
[2, 4]

→ 4
```

코드에서는 pooling window에서 최댓값을 찾는다.

```python id="u4lbp5"
window = x[n, c, h_start:h_end, w_start:w_end]
out[n, c, i, j] = torch.max(window)
```

backward에서는 최댓값이 있던 위치로만 gradient를 보낸다.

```python id="a1yb2w"
max_val = torch.max(window)
mask = (window == max_val)
dx[...] += mask.float() * dout[n, c, i, j]
```

정리하면 다음과 같다.

```text id="jh1jk3"
forward:
가장 큰 값만 선택

backward:
가장 큰 값이 있던 위치로만 gradient 전달
```



---

## 15. Batch Normalization

Batch Normalization은 layer의 출력을 정규화해서 학습을 안정화하는 기법이다.

흐름은 다음과 같다.

```text id="r0u78m"
1. batch 평균 계산
2. 평균 빼기
3. 분산 계산
4. 표준편차로 나누기
5. gamma, beta로 scale/shift
```

코드에서는 train mode일 때 현재 batch의 평균과 분산을 사용한다.

```python id="fhguv6"
sample_mean = torch.mean(x, dim=0)
sample_var = torch.var(x, dim=0, unbiased=False)
x_norm = x_centered * inv_std
out = gamma * x_norm + beta
```

그리고 running mean과 running variance를 업데이트한다.

```python id="m7dth8"
running_mean = momentum * running_mean + (1 - momentum) * sample_mean
running_var = momentum * running_var + (1 - momentum) * sample_var
```

test mode에서는 현재 batch 통계를 쓰지 않고, 학습 중 저장해둔 running mean과 running variance를 사용한다. 

```text id="51a5jw"
train mode:
현재 batch의 mean/var 사용

test mode:
running_mean/running_var 사용
```

이 차이가 BatchNorm에서 정말 중요하다.

---

## 16. Spatial Batch Normalization

일반 BatchNorm은 보통 `(N, D)` 형태의 데이터에 적용한다.
하지만 CNN feature map은 `(N, C, H, W)` 형태다.

그래서 Spatial BatchNorm에서는 데이터를 잠깐 변형한다.

```python id="bq4m4i"
x_transposed = x.permute(0, 2, 3, 1).reshape(-1, C)
```

형태 변화는 다음과 같다.

```text id="413byb"
(N, C, H, W)
→ (N, H, W, C)
→ (N*H*W, C)
```

이렇게 바꾸면 채널 `C`를 기준으로 BatchNorm을 적용할 수 있다.
적용 후에는 다시 원래 형태로 되돌린다.

```python id="nzj4iv"
out = out_transposed.reshape(N, H, W, C).permute(0, 3, 1, 2)
```

Spatial BatchNorm은 CNN에서 feature map의 채널별 분포를 안정화하는 역할을 한다. 

---

## 17. CNN용 Sandwich Layer

CNN에서도 여러 레이어를 묶어서 사용한다.

예를 들어 `Conv_ReLU`는 다음 구조다.

```text id="y5c0d6"
Conv → ReLU
```

`Conv_ReLU_Pool`은 다음 구조다.

```text id="5pj9bm"
Conv → ReLU → Pool
```

BatchNorm을 포함하면 다음과 같은 구조도 있다.

```text id="awh24k"
Conv → BatchNorm → ReLU
Conv → BatchNorm → ReLU → Pool
```

코드에서는 이런 묶음 레이어를 만들어 복잡한 CNN forward/backward를 간단하게 작성한다. 

이 구조가 좋은 이유는 모델을 만들 때 매번 Conv, ReLU, Pool을 따로 호출하지 않아도 되기 때문이다.

---

## 18. ThreeLayerConvNet

`ThreeLayerConvNet`은 가장 기본적인 CNN 구조다.

아키텍처는 다음과 같다.

```text id="tal1t2"
Conv → ReLU → 2x2 MaxPool → Linear → ReLU → Linear → Softmax
```

코드에서는 세 종류의 파라미터를 사용한다.

```text id="0t5xz2"
W1, b1: convolution layer
W2, b2: hidden linear layer
W3, b3: output linear layer
```

forward 흐름은 다음과 같다.

```python id="o1z77u"
out, cache1 = Conv_ReLU_Pool.forward(X, W1, b1, conv_param, pool_param)
out_flat = out.reshape(out.shape[0], -1)
out, cache2 = Linear_ReLU.forward(out_flat, W2, b2)
scores, cache3 = Linear.forward(out, W3, b3)
```

즉 이미지를 바로 펼쳐서 Linear에 넣는 것이 아니라, 먼저 Conv layer로 공간적 특징을 추출한 뒤 분류한다. 

흐름을 말로 풀면 이렇다.

```text id="kx8nvn"
이미지 입력
→ convolution으로 지역 특징 추출
→ pooling으로 크기 축소
→ fully connected layer로 분류
```

---

## 19. Kaiming Initialization

깊은 신경망에서는 weight 초기화가 중요하다.

weight가 너무 작으면 신호가 점점 사라지고, 너무 크면 값이 폭발할 수 있다.
특히 ReLU를 사용하는 네트워크에서는 ReLU에 맞는 초기화가 필요하다.

코드에서는 Kaiming initialization을 구현했다.

```python id="wuo9pp"
gain = 2. if relu else 1.
std = torch.sqrt(torch.tensor(gain / fan_in))
weight = torch.randn(...) * std
```

Linear layer일 때와 convolution layer일 때 fan-in 계산 방식이 다르다.

```text id="h2zs4w"
Linear:
fan_in = Din

Convolution:
fan_in = input channel × kernel size × kernel size
```

Kaiming initialization은 ReLU를 사용하는 깊은 네트워크에서 학습을 안정화하는 데 중요한 역할을 한다. 

---

## 20. DeepConvNet

`DeepConvNet`은 여러 개의 convolution layer를 쌓을 수 있는 일반화된 CNN이다.

```python id="isq7sj"
num_filters=[8, 64]
max_pools=[0, 1]
batchnorm=False
```

각 설정의 의미는 다음과 같다.

```text id="knwpvm"
num_filters:
각 convolution layer의 필터 개수

max_pools:
어떤 conv layer 뒤에 pooling을 넣을지

batchnorm:
batch normalization을 사용할지 여부
```

`ThreeLayerConvNet`이 고정된 구조라면, `DeepConvNet`은 설정값에 따라 더 깊은 CNN을 만들 수 있다.

forward에서는 convolution layer들을 반복문으로 통과시킨다.

```python id="r2pfei"
for i in range(1, self.num_layers):
    ...
```

각 layer마다 batchnorm 사용 여부와 pooling 적용 여부에 따라 다른 sandwich layer를 호출한다.

```text id="2z5cvx"
batchnorm X, pooling X:
Conv → ReLU

batchnorm X, pooling O:
Conv → ReLU → Pool

batchnorm O, pooling X:
Conv → BatchNorm → ReLU

batchnorm O, pooling O:
Conv → BatchNorm → ReLU → Pool
```

마지막에는 feature map을 펼쳐서 Linear layer에 넣고 class score를 계산한다.

```python id="c0f9i8"
out = out.reshape(out.shape[0], -1)
out, cache_final = Linear.forward(out, W, b)
scores = out
```

이 구조는 실제 CNN 모델들이 여러 Conv block을 쌓고 마지막에 classifier를 붙이는 방식과 비슷하다. 

---

# Fully Connected Network와 CNN의 차이

둘의 가장 큰 차이는 이미지를 바라보는 방식이다.

| 구분     | Fully Connected Network | Convolutional Network       |
| ------ | ----------------------- | --------------------------- |
| 입력 처리  | 이미지를 전부 펼침              | 이미지의 공간 구조 유지               |
| 핵심 연산  | Linear                  | Convolution                 |
| 장점     | 구조가 단순함                 | 이미지 특징 추출에 강함               |
| 단점     | 공간 정보 손실                | 구현이 더 복잡함                   |
| 주요 레이어 | Linear, ReLU, Dropout   | Conv, ReLU, Pool, BatchNorm |

Fully Connected Network는 이미지를 벡터로 펼쳐서 처리한다.

```text id="uz0h97"
3 x 32 x 32 → 3072차원 벡터
```

반면 CNN은 이미지의 채널, 높이, 너비 구조를 유지한 채 처리한다.

```text id="zaz60m"
(N, C, H, W) 형태 유지
```

그래서 CNN은 이미지 분류 문제에서 더 자연스럽게 동작한다.

---

# 이번 구현에서 가장 중요한 것 정리

이번 파트에서 꼭 기억해야 하는 핵심은 다음과 같다.

| 개념               | 핵심                            |
| ---------------- | ----------------------------- |
| Forward          | 입력으로 출력 계산                    |
| Backward         | gradient 계산                   |
| cache            | backward에 필요한 중간값 저장          |
| Linear           | 입력을 펼쳐 행렬곱 수행                 |
| ReLU             | 음수를 0으로 만들고 비선형성 추가           |
| Dropout          | 일부 뉴런을 꺼서 과적합 완화              |
| Regularization   | 가중치가 너무 커지는 것 방지              |
| Optimizer        | gradient로 파라미터 업데이트           |
| Conv             | 필터로 지역 특징 추출                  |
| Pooling          | feature map 크기 축소             |
| BatchNorm        | 학습 안정화                        |
| SpatialBatchNorm | CNN feature map에 BatchNorm 적용 |
| Kaiming Init     | ReLU 네트워크에 적합한 초기화            |
| DeepConvNet      | 여러 Conv layer를 쌓은 CNN         |

---

# 전체 흐름 정리

이번 구현은 크게 두 단계로 볼 수 있다.

첫 번째는 Fully Connected Network다.

```text id="jth2cq"
Linear
→ ReLU
→ Dropout
→ Softmax
→ Optimizer
```

두 번째는 Convolutional Network다.

```text id="xfk0k2"
Conv
→ ReLU
→ Pool
→ BatchNorm
→ Linear
→ Softmax
```

결국 두 구조 모두 핵심은 같다.

```text id="2sax0r"
forward로 score 계산
loss 계산
backward로 gradient 계산
optimizer로 parameter update
```

다만 CNN은 이미지의 공간 구조를 유지하면서 convolution과 pooling을 사용한다는 점이 다르다.

---

# 마무리

이번 구현을 통해 딥러닝 프레임워크가 내부에서 어떤 일을 하는지 직접 확인할 수 있었다.

평소에는 PyTorch의 `nn.Linear`, `nn.Conv2d`, `nn.BatchNorm2d`, `torch.optim.Adam` 같은 기능을 가져다 쓰지만, 내부적으로는 결국 다음 과정이 반복된다.

```text id="hl3hg0"
입력 계산
중간값 저장
loss 계산
gradient 계산
파라미터 업데이트
```

Fully Connected Network에서는 Linear, ReLU, Dropout, Optimizer의 역할을 이해했고, CNN에서는 Convolution, Pooling, Batch Normalization, DeepConvNet 구조까지 직접 구현했다.

이번 코드의 가장 큰 의미는 **딥러닝 모델을 블랙박스로 쓰는 것이 아니라, 내부 학습 흐름을 직접 따라가 봤다는 것**이다.

앞으로 PyTorch의 고수준 API를 사용하더라도, 내부에서 어떤 계산이 일어나는지 이해하고 있으면 모델 구조를 디버깅하거나 성능을 개선할 때 훨씬 더 명확하게 접근할 수 있을 것 같다.
