---
title: "[AI Infra] TensorRT는 도대체 뭘까? NVIDIA GPU에서 추론을 빠르게 돌리는 엔진\n"
source: "https://velog.io/@yorange50/AI-Infra-TensorRT는-도대체-뭘까-NVIDIA-GPU에서-추론을-빠르게-돌리는-엔진"
published: "2026-05-07T07:08:56.768Z"
tags: ""
backup_date: "2026-05-29T14:52:52.770886"
---

PyTorch inference, ONNX, latency, throughput을 공부하다 보면 결국 이 단어가 나온다.

```text
TensorRT
```

처음 보면 이런 느낌이다.

```text
CUDA랑 뭐가 다르지?
ONNX랑 뭐가 다르지?
PyTorch 모델을 TensorRT로 바꾸면 뭐가 좋아지지?
```

한 줄로 말하면 이렇다.

```text
TensorRT = NVIDIA GPU에서 딥러닝 추론을 빠르게 돌리기 위한 최적화 엔진
```

NVIDIA 공식 문서에서도 TensorRT를 **NVIDIA GPU에서 딥러닝 inference를 최적화하고 가속하는 SDK**라고 설명한다. PyTorch, TensorFlow, ONNX 같은 프레임워크에서 만든 학습된 모델을 받아 고성능 배포용으로 최적화할 수 있다. ([NVIDIA Docs][1])

---

## 1. TensorRT 한 줄 정의

TensorRT는 학습용 도구라기보다 **추론 최적화 도구**다.

```text
Training용:
PyTorch
TensorFlow

Inference 최적화용:
TensorRT
ONNX Runtime
Triton Inference Server
```

쉽게 말하면 PyTorch로 학습한 모델을 그대로 서비스에 올릴 수도 있지만, 더 빠르게 돌리고 싶을 때 TensorRT를 쓴다.

```text
PyTorch 모델
↓
ONNX 변환
↓
TensorRT Engine 생성
↓
NVIDIA GPU에서 고속 inference
```

---

## 2. TensorRT는 왜 필요할까?

PyTorch로도 inference는 가능하다.

```python
model.eval()

with torch.inference_mode():
    output = model(x)
```

그런데 운영 환경에서는 이런 요구가 생긴다.

```text
latency를 줄이고 싶다
throughput을 높이고 싶다
GPU 메모리를 아끼고 싶다
동일 GPU로 더 많은 요청을 처리하고 싶다
FP16/INT8로 최적화하고 싶다
NVIDIA GPU에 맞게 모델을 컴파일하고 싶다
```

이때 TensorRT가 등장한다.

TensorRT는 모델을 그대로 실행하는 것이 아니라, NVIDIA GPU에서 더 잘 돌도록 **최적화된 engine**을 만든다.

---

## 3. TensorRT는 모델을 어떻게 빠르게 만들까?

TensorRT가 하는 일은 크게 보면 이렇다.

```text
1. 모델 그래프 분석
2. 불필요한 연산 제거
3. 연산 합치기
4. GPU에 맞는 kernel 선택
5. FP16/INT8 같은 낮은 정밀도 사용
6. 메모리 사용 최적화
7. 최적화된 TensorRT Engine 생성
```

대표적인 최적화는 다음과 같다.

```text
Layer Fusion
Precision Calibration
Kernel Auto-Tuning
Tensor Memory Optimization
Dynamic Tensor Memory
```

입문 단계에서는 전부 외울 필요 없다. 핵심은 이것이다.

```text
TensorRT는 모델 그래프를 NVIDIA GPU에 맞게 다시 최적화해서 inference를 빠르게 만든다.
```

---

## 4. Layer Fusion이란?

Layer Fusion은 여러 연산을 하나로 합치는 최적화다.

예를 들어 모델 안에 이런 연산이 있다고 하자.

```text
Convolution
↓
BatchNorm
↓
ReLU
```

일반적으로는 각각 따로 실행될 수 있다.

```text
Conv 실행
메모리에 결과 저장
BatchNorm 실행
메모리에 결과 저장
ReLU 실행
메모리에 결과 저장
```

그런데 TensorRT는 이걸 하나의 연산처럼 합칠 수 있다.

```text
Conv + BatchNorm + ReLU
```

이렇게 하면 중간 결과를 계속 메모리에 쓰고 읽는 비용이 줄어든다.

```text
메모리 접근 감소
kernel launch 감소
latency 감소 가능
throughput 증가 가능
```

즉, Layer Fusion은 “여러 단계를 하나의 빠른 단계로 합치는 것”이다.

---

## 5. Precision 최적화: FP32, FP16, INT8

TensorRT를 공부하면 이런 단어가 자주 나온다.

```text
FP32
FP16
BF16
FP8
INT8
```

TensorRT 공식 문서도 TensorRT가 FP32, FP16, BF16, FP8, INT8 같은 mixed precision을 지원한다고 설명한다. ([NVIDIA Docs][1])

일단 입문 단계에서는 이렇게 보면 된다.

| 정밀도  | 의미         | 특징             |
| ---- | ---------- | -------------- |
| FP32 | 32비트 부동소수점 | 정확하지만 무거움      |
| FP16 | 16비트 부동소수점 | 더 빠르고 메모리 적게 씀 |
| INT8 | 8비트 정수     | 매우 가볍지만 검증 필요  |

딥러닝 모델의 가중치와 activation은 숫자다.

기본적으로 FP32를 쓰면 정확도는 안정적이지만 무겁다.

```text
FP32 = 숫자를 더 정밀하게 표현
```

FP16이나 INT8을 쓰면 숫자 표현을 가볍게 만든다.

```text
FP16 = 메모리 절약 + 속도 향상 가능
INT8 = 더 큰 메모리 절약 + 더 빠른 추론 가능
```

하지만 숫자를 가볍게 만들면 정확도 손실이 생길 수 있다.

그래서 TensorRT 최적화 후에는 반드시 원래 모델 결과와 비교해야 한다.

---

## 6. TensorRT와 ONNX의 관계

ONNX 글에서 봤던 흐름을 다시 가져오면 이렇다.

```text
PyTorch
↓
ONNX
↓
TensorRT
```

ONNX는 모델 포맷이다.

TensorRT는 추론 최적화 엔진이다.

```text
ONNX = 모델을 옮기기 위한 공통 포맷
TensorRT = ONNX 모델을 NVIDIA GPU용으로 최적화해서 실행하는 엔진
```

NVIDIA 문서에서도 TensorRT로 모델을 가져오는 가장 흔한 방식은 프레임워크에서 ONNX로 export한 뒤, TensorRT의 ONNX parser를 사용해 network definition을 만드는 방식이라고 설명한다. ([NVIDIA Docs][2])

즉, 실무에서 가장 흔한 흐름은 이것이다.

```text
PyTorch에서 학습
↓
torch.onnx.export()
↓
model.onnx 생성
↓
trtexec 또는 TensorRT API로 engine 생성
↓
engine 파일로 inference
```

---

## 7. TensorRT Engine이란?

TensorRT에서 중요한 결과물이 **engine**이다.

```text
TensorRT Engine = 특정 GPU와 입력 조건에 맞게 최적화된 실행 파일 같은 것
```

보통 확장자를 이렇게 쓴다.

```text
model.plan
model.engine
model.trt
```

정해진 표준 확장자가 하나로 고정된 것은 아니지만, TensorRT engine 또는 plan file이라고 부르는 경우가 많다.

흐름은 이렇다.

```text
ONNX 모델
↓
TensorRT Builder
↓
TensorRT Engine 생성
↓
Runtime에서 Engine 로드
↓
Execution Context 생성
↓
Inference 실행
```

공식 문서에서도 TensorRT의 build phase에서 Builder가 모델을 최적화하고 Engine을 생성한다고 설명한다. ([NVIDIA Docs][2])

---

## 8. trtexec이란?

TensorRT를 처음 만질 때 가장 많이 보는 도구가 `trtexec`이다.

```text
trtexec = TensorRT 모델 변환/벤치마크용 CLI 도구
```

ONNX 파일을 TensorRT engine으로 바꾸는 기본 예시는 이렇다.

```bash
trtexec --onnx=model.onnx --saveEngine=model.engine
```

NVIDIA Quick Start 문서에서도 ONNX 모델을 TensorRT engine으로 변환하는 예시로 `trtexec --onnx=... --saveEngine=...` 형태를 보여준다. ([NVIDIA Docs][3])

FP16을 켜고 싶으면 이렇게 한다.

```bash
trtexec \
  --onnx=model.onnx \
  --saveEngine=model_fp16.engine \
  --fp16
```

입력 shape을 지정하고 싶으면 이렇게 한다.

```bash
trtexec \
  --onnx=model.onnx \
  --saveEngine=model.engine \
  --shapes=input:1x3x224x224
```

TensorRT 공식 benchmarking 문서도 `--onnx`는 ONNX 파일 경로, `--shapes`는 입력 텐서 shape, `--fp16`은 FP16 tactic 사용을 의미한다고 설명한다. ([NVIDIA Docs][4])

---

## 9. TensorRT 변환 흐름 예시

PyTorch 모델을 TensorRT까지 가져가는 흐름은 보통 이렇다.

### 1단계: PyTorch 모델 준비

```python
model.eval()

with torch.inference_mode():
    output = model(x)
```

### 2단계: ONNX export

```python
import torch

dummy_input = torch.randn(1, 3, 224, 224).to("cuda")

torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    input_names=["input"],
    output_names=["output"],
    opset_version=17,
    dynamic_axes={
        "input": {0: "batch_size"},
        "output": {0: "batch_size"}
    }
)
```

### 3단계: TensorRT engine 생성

```bash
trtexec \
  --onnx=model.onnx \
  --saveEngine=model.engine \
  --fp16 \
  --minShapes=input:1x3x224x224 \
  --optShapes=input:8x3x224x224 \
  --maxShapes=input:16x3x224x224
```

### 4단계: TensorRT runtime에서 engine 실행

이 단계에서는 Python API나 C++ API로 engine을 로드해서 inference를 수행한다.

```text
engine load
↓
execution context 생성
↓
input buffer 준비
↓
output buffer 준비
↓
CUDA stream에서 enqueue
↓
결과 반환
```

TensorRT C++ API 문서에서도 inference를 수행하려면 input/output buffer 주소를 TensorRT에 알려주고, dynamic shape engine이라면 input shape도 지정한 뒤 `enqueueV3`로 CUDA stream에서 inference를 시작한다고 설명한다. ([NVIDIA Docs][5])

---

## 10. Dynamic Shape와 Optimization Profile

ONNX export에서 batch size를 dynamic으로 만든 경우가 있다.

```text
input shape = [N, 3, 224, 224]
```

여기서 `N`은 batch size다.

실제 서비스에서는 batch size가 바뀔 수 있다.

```text
batch size 1
batch size 4
batch size 8
batch size 16
```

TensorRT는 dynamic shape를 지원하지만, 아무 shape나 무한정 허용하는 방식은 아니다.

보통 optimization profile을 지정한다.

```text
min shape = 최소 입력 크기
opt shape = 가장 자주 쓰는 입력 크기
max shape = 최대 입력 크기
```

예시는 이렇다.

```bash
trtexec \
  --onnx=model.onnx \
  --saveEngine=model.engine \
  --minShapes=input:1x3x224x224 \
  --optShapes=input:8x3x224x224 \
  --maxShapes=input:16x3x224x224
```

NVIDIA 문서도 dynamic shape engine을 만들 때 runtime dimension에는 `-1`을 사용하고, build time에 허용 범위와 최적화할 dimension을 optimization profile로 지정한다고 설명한다. ([NVIDIA Docs][6])

---

## 11. TensorRT가 무조건 정답일까?

아니다.

TensorRT는 강력하지만 항상 편한 도구는 아니다.

좋은 경우는 이런 상황이다.

```text
NVIDIA GPU에서 inference해야 함
latency를 낮춰야 함
throughput을 높여야 함
모델 구조가 TensorRT에서 잘 지원됨
입력 shape 범위가 비교적 명확함
운영 배포에서 성능 최적화가 중요함
```

반대로 이런 경우에는 부담이 될 수 있다.

```text
모델이 자주 바뀜
지원하지 않는 연산이 있음
dynamic shape가 복잡함
정확도 검증 파이프라인이 없음
CPU 배포가 목적임
NVIDIA GPU가 아님
개발 속도가 더 중요함
```

특히 ONNX 변환은 되었는데 TensorRT 변환에서 실패하는 경우도 있다.

이유는 보통 이렇다.

```text
TensorRT가 해당 ONNX operator를 지원하지 않음
custom layer가 있음
shape 추론이 어려움
opset 버전 문제
dynamic shape profile이 없음
plugin이 필요함
```

NVIDIA Quick Start 문서도 ONNX conversion은 모델의 모든 operation이 TensorRT에서 지원되거나, 지원되지 않는 연산에 대해 custom plugin을 제공해야 한다고 설명한다. ([NVIDIA Docs][3])

---

## 12. TensorRT와 CUDA의 차이

CUDA와 TensorRT는 다르다.

```text
CUDA = NVIDIA GPU에서 병렬 계산을 하기 위한 플랫폼
TensorRT = CUDA 위에서 딥러닝 inference를 최적화하는 엔진
```

비유하면 이렇다.

```text
CUDA = GPU를 움직이는 기반 도로
TensorRT = 딥러닝 추론 전용 고속도로 설계자
```

PyTorch도 내부적으로 CUDA를 사용해서 GPU 연산을 한다.

TensorRT도 NVIDIA GPU에서 실행되므로 CUDA를 기반으로 한다.

하지만 TensorRT는 단순히 GPU를 쓰는 것이 아니라, 모델 그래프를 분석해서 더 빠르게 실행할 수 있는 engine을 만든다.

---

## 13. TensorRT와 ONNX Runtime 차이

ONNX Runtime도 ONNX 모델을 실행할 수 있다.

TensorRT도 ONNX 모델을 실행할 수 있다.

둘의 차이를 아주 단순히 보면 이렇다.

| 구분    | ONNX Runtime           | TensorRT                  |
| ----- | ---------------------- | ------------------------- |
| 역할    | ONNX 모델 실행 엔진          | NVIDIA GPU 추론 최적화 엔진      |
| 지원 환경 | CPU, GPU, 다양한 provider | NVIDIA GPU 중심             |
| 입력    | ONNX 모델                | ONNX 또는 TensorRT network  |
| 강점    | 범용성                    | NVIDIA GPU 최적화            |
| 사용 목적 | 프레임워크 독립 추론            | 낮은 latency, 높은 throughput |

ONNX Runtime도 CUDA Execution Provider나 TensorRT Execution Provider를 사용할 수 있다.

즉, 실무에서는 이렇게 연결될 수도 있다.

```text
ONNX Runtime + CUDA Provider
ONNX Runtime + TensorRT Provider
TensorRT Native Runtime
```

---

## 14. TensorRT와 Triton Inference Server

이름이 비슷해서 헷갈릴 수 있다.

```text
TensorRT
Triton Inference Server
```

둘은 다르다.

```text
TensorRT = 모델 하나를 GPU에서 빠르게 돌리기 위한 최적화 엔진
Triton = 여러 모델을 API 서버 형태로 서빙하기 위한 inference server
```

관계는 이렇게 볼 수 있다.

```text
TensorRT engine 생성
↓
Triton Inference Server에 올림
↓
HTTP/gRPC 요청 처리
↓
dynamic batching
↓
GPU inference
```

즉, TensorRT가 “엔진”이라면 Triton은 “서빙 서버”에 가깝다.

---

## 15. TensorRT에서 성능 지표

TensorRT를 쓰는 이유는 결국 inference 성능 때문이다.

주로 보는 지표는 다음과 같다.

```text
latency
throughput
GPU utilization
GPU memory usage
batch size
p50 / p95 / p99 latency
FP32 vs FP16 vs INT8 정확도 차이
```

`trtexec`으로도 간단한 benchmark를 볼 수 있다.

```bash
trtexec \
  --onnx=model.onnx \
  --shapes=input:8x3x224x224 \
  --fp16
```

NVIDIA 문서는 TensorRT 성능 최적화에서 batching을 가장 중요한 최적화 중 하나로 설명하며, batch는 같은 shape으로 균일하게 처리될 수 있는 입력들의 모음이고 병렬 계산에 적합하다고 설명한다. ([NVIDIA Docs][7])

---

## 16. TensorRT 사용 전후 검증

TensorRT로 engine을 만들었다고 바로 배포하면 안 된다.

반드시 원본 모델과 결과를 비교해야 한다.

```text
PyTorch output
ONNX Runtime output
TensorRT output
```

이 세 가지가 충분히 비슷한지 확인한다.

검증 기준은 모델마다 다르지만 보통 이런 것을 본다.

```text
출력 shape 동일한가
예측 class가 같은가
logit 차이가 허용 범위 안인가
FP16 변환 후 성능 저하가 없는가
INT8 변환 후 정확도 손실이 허용 가능한가
latency가 실제로 줄었는가
throughput이 실제로 늘었는가
```

특히 INT8은 calibration이 필요할 수 있고, 정확도 손실 가능성이 더 크기 때문에 더 꼼꼼히 봐야 한다.

---

## 17. TensorRT를 한 장 그림으로 정리

```text
[Training]
PyTorch / TensorFlow
loss.backward()
optimizer.step()
가중치 업데이트

        ↓ export

[Model Format]
ONNX
프레임워크 독립 모델 포맷

        ↓ build

[Optimization]
TensorRT Builder
Layer fusion
FP16 / INT8
Kernel selection
Memory optimization

        ↓

[Runtime]
TensorRT Engine
Execution Context
CUDA Stream
NVIDIA GPU Inference

        ↓

[Serving]
FastAPI / C++ Server / Triton / Kubernetes
latency, throughput, GPU memory monitoring
```

---

## 18. 최종 정리

TensorRT는 NVIDIA GPU에서 딥러닝 inference를 빠르게 돌리기 위한 최적화 엔진이다.

```text
TensorRT = NVIDIA GPU용 inference optimizer + runtime
```

PyTorch와 비교하면 이렇게 볼 수 있다.

```text
PyTorch
= 모델 개발과 학습에 강함
= inference도 가능

ONNX
= 모델을 다른 환경으로 옮기기 위한 포맷

TensorRT
= ONNX 같은 모델을 NVIDIA GPU에 맞게 최적화해서 빠르게 실행
```

가장 흔한 배포 흐름은 이렇다.

```text
PyTorch
↓
ONNX
↓
TensorRT Engine
↓
Triton / FastAPI / C++ Server
```

TensorRT가 줄이려는 것은 주로 이것이다.

```text
latency
GPU memory usage
불필요한 연산
메모리 접근 비용
kernel launch overhead
```

TensorRT가 높이려는 것은 이것이다.

```text
throughput
GPU utilization
GPU당 처리량
요청당 비용 효율
```

한 문장으로 정리하면 이렇다.

```text
TensorRT는 학습된 모델을 NVIDIA GPU에서 더 빠르고 가볍게 서빙하기 위해 컴파일하고 최적화하는 도구다.
```

AI DevOps 관점에서는 TensorRT를 단순 라이브러리로 보면 안 된다.
**PyTorch 학습 코드와 실제 GPU 추론 서버 사이를 이어주는 성능 최적화 단계**로 이해하는 게 가장 정확하다.

[1]: https://docs.nvidia.com/deeplearning/tensorrt/latest/?utm_source=chatgpt.com "NVIDIA TensorRT Documentation"
[2]: https://docs.nvidia.com/deeplearning/tensorrt/latest/architecture/capabilities.html?utm_source=chatgpt.com "TensorRT's Capabilities"
[3]: https://docs.nvidia.com/deeplearning/tensorrt/latest/getting-started/quick-start-guide.html?utm_source=chatgpt.com "Quick Start Guide — NVIDIA TensorRT"
[4]: https://docs.nvidia.com/deeplearning/tensorrt/latest/performance/benchmarking.html?utm_source=chatgpt.com "Performance Benchmarking using trtexec"
[5]: https://docs.nvidia.com/deeplearning/tensorrt/latest/inference-library/c-api-docs.html?utm_source=chatgpt.com "C++ API Documentation — NVIDIA TensorRT"
[6]: https://docs.nvidia.com/deeplearning/tensorrt/latest/inference-library/work-dynamic-shapes.html?utm_source=chatgpt.com "Working with Dynamic Shapes — NVIDIA TensorRT"
[7]: https://docs.nvidia.com/deeplearning/tensorrt/latest/performance/optimization.html?utm_source=chatgpt.com "Optimizing TensorRT Performance"
