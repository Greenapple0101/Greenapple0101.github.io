---
title: "[AI Infra] vLLM은 도대체 뭘까? LLM 추론을 빠르고 효율적으로 서빙하는 엔진\n"
source: "https://velog.io/@yorange50/AI-Infra-vLLM은-도대체-뭘까-LLM-추론을-빠르고-효율적으로-서빙하는-엔진"
published: "2026-05-07T09:09:49.933Z"
tags: ""
backup_date: "2026-05-29T14:52:52.768775"
---

지금까지 흐름을 보면 이렇게 이어진다.

```text
PyTorch
↓
Inference
↓
Batch
↓
Latency / Throughput
↓
ONNX
↓
TensorRT
↓
Triton Inference Server
```

여기서 `vLLM`은 특히 **LLM 추론 서빙**에 특화된 엔진이다.

한 줄로 말하면 이렇다.

```text
vLLM = LLM을 빠르고 메모리 효율적으로 inference/serving하기 위한 오픈소스 엔진
```

vLLM 공식 GitHub에서도 vLLM을 **high-throughput and memory-efficient inference and serving engine for LLMs**라고 설명하고, 핵심 기능으로 PagedAttention, continuous batching, chunked prefill, prefix caching, quantization 등을 제시한다. ([GitHub][1])

---

## 1. vLLM 한 줄 정의

vLLM은 일반적인 모델 서버라기보다 **대규모 언어 모델 추론에 특화된 serving engine**이다.

```text
vLLM
= LLM inference를 빠르게 처리하기 위한 엔진
= 여러 사용자 요청을 효율적으로 batch 처리
= KV cache 메모리를 효율적으로 관리
= OpenAI-compatible API 서버 제공
```

즉, vLLM은 이런 상황에서 나온다.

```text
LLM을 직접 서빙하고 싶다
Hugging Face 모델을 API로 띄우고 싶다
동시 요청을 많이 처리하고 싶다
GPU 메모리를 효율적으로 쓰고 싶다
OpenAI API처럼 호출하고 싶다
tokens/sec를 높이고 싶다
```

---

## 2. 왜 vLLM이 필요할까?

LLM 추론은 일반 이미지 분류 모델 추론보다 훨씬 까다롭다.

이미지 분류는 보통 입력 한 번 넣고 출력 한 번 받으면 끝난다.

```text
image
↓
model forward
↓
class prediction
```

그런데 LLM은 토큰을 하나씩 생성한다.

```text
prompt 입력
↓
첫 번째 token 생성
↓
두 번째 token 생성
↓
세 번째 token 생성
↓
...
↓
최종 응답 완성
```

즉, LLM inference는 긴 반복 과정이다.

```text
LLM inference
= prefill + decode 반복
```

그래서 LLM serving에서는 다음 문제가 중요해진다.

```text
동시 요청 처리
KV cache 메모리 관리
batch scheduling
첫 토큰 지연 시간
토큰 생성 속도
GPU memory fragmentation
throughput
```

vLLM은 이 문제를 해결하기 위해 나온 LLM serving 엔진이다.

---

## 3. vLLM이 해결하려는 핵심 문제

vLLM의 핵심은 크게 두 가지로 잡으면 된다.

```text
1. PagedAttention
2. Continuous Batching
```

공식 문서와 GitHub에서도 vLLM의 대표 기능으로 **PagedAttention을 통한 attention key/value memory 관리**와 **continuous batching of incoming requests**를 강조한다. ([GitHub][1])

입문 단계에서는 이렇게 이해하면 된다.

```text
PagedAttention
= LLM의 KV cache 메모리를 효율적으로 관리하는 기술

Continuous Batching
= 들어오는 요청을 계속 동적으로 묶어서 GPU를 놀리지 않는 스케줄링 방식
```

---

## 4. LLM에서 KV Cache가 뭔데?

LLM은 다음 토큰을 만들 때 이전 토큰들의 정보를 계속 참고한다.

예를 들어 이런 문장이 있다고 하자.

```text
나는 오늘 회사에서 Kubernetes를 공부했다
```

모델이 다음 토큰을 생성할 때, 앞에서 나온 토큰들의 key/value 정보를 계속 사용한다.

이때 이전 토큰들에 대한 attention 계산 결과 일부를 저장해두는 것이 **KV cache**다.

```text
KV cache
= 이전 토큰들의 Key / Value 정보를 저장해두는 캐시
```

왜 저장할까?

매번 처음부터 다시 계산하면 너무 느리기 때문이다.

```text
캐시 없음
= 매 토큰마다 이전 문맥을 다시 계산
= 느림

KV cache 사용
= 이전 계산 결과를 재사용
= 빠름
```

LLM 추론에서는 KV cache가 매우 중요하다.

---

## 5. 그런데 KV Cache가 문제를 만든다

KV cache는 빠르게 만들어주지만, 메모리를 많이 먹는다.

특히 요청이 많고 문맥이 길면 GPU 메모리를 크게 차지한다.

```text
사용자 A: 짧은 질문
사용자 B: 긴 질문
사용자 C: 긴 답변 생성 중
사용자 D: 긴 문맥 유지 중
```

각 요청마다 KV cache가 생긴다.

문제는 요청마다 길이가 다르다는 것이다.

```text
요청 A = 50 tokens
요청 B = 2,000 tokens
요청 C = 8,000 tokens
```

이러면 GPU 메모리 관리가 어려워진다.

```text
길이가 제각각
↓
메모리 낭비 발생
↓
fragmentation 발생
↓
동시 처리 가능한 요청 수 감소
↓
throughput 감소
```

vLLM의 PagedAttention은 이 문제를 해결하려는 기술이다.

---

## 6. PagedAttention이란?

PagedAttention은 vLLM의 대표 기술이다.

이름에서 알 수 있듯이 OS의 virtual memory paging 아이디어와 비슷하게, KV cache를 고정 크기 block 단위로 나누어 관리한다.

```text
기존 방식
= 요청마다 연속된 큰 메모리 공간을 잡는 느낌

PagedAttention
= KV cache를 작은 block/page 단위로 나누어 관리
```

비유하면 이렇다.

```text
기존 방식
= 긴 책상 하나를 통째로 예약

PagedAttention
= 작은 책상 여러 개를 필요한 만큼 배정
```

요청마다 필요한 토큰 수가 다르기 때문에, 작은 block 단위로 관리하면 메모리 낭비를 줄일 수 있다.

```text
필요한 만큼만 KV cache block 사용
↓
GPU 메모리 효율 증가
↓
더 많은 요청 동시 처리 가능
↓
throughput 증가 가능
```

vLLM 공식 자료도 PagedAttention을 attention key/value memory를 효율적으로 관리하는 핵심 기능으로 설명한다. ([GitHub][1])

---

## 7. Continuous Batching이란?

일반적인 batching은 요청을 모아서 한 번에 처리한다.

```text
요청 A
요청 B
요청 C
요청 D
↓
batch로 묶음
↓
모델 실행
```

그런데 LLM에서는 문제가 있다.

요청마다 생성 길이가 다르다.

```text
A 요청 = 10 tokens 생성 후 종료
B 요청 = 100 tokens 생성 필요
C 요청 = 300 tokens 생성 필요
```

기존 static batching 방식이면 짧은 요청이 끝나도 긴 요청이 끝날 때까지 batch 자리가 비효율적으로 묶일 수 있다.

```text
A는 이미 끝났는데
B, C가 아직 생성 중
↓
batch 안에 빈 자리 발생
↓
GPU 활용률 저하
```

Continuous batching은 이걸 개선한다.

```text
끝난 요청은 batch에서 제거
대기 중인 새 요청을 즉시 batch에 추가
```

즉, batch가 고정된 묶음이 아니라 계속 살아 움직인다.

```text
decode step 1:
[A, B, C]

A 종료

decode step 2:
[B, C, D]

B 종료

decode step 3:
[C, D, E]
```

이렇게 하면 GPU가 더 꾸준히 바쁘게 일할 수 있다.

vLLM은 incoming requests에 대한 continuous batching을 핵심 기능으로 제공한다고 공식 GitHub에서 설명한다. ([GitHub][1])

---

## 8. Static Batching vs Continuous Batching

| 구분         | Static Batching  | Continuous Batching |
| ---------- | ---------------- | ------------------- |
| batch 구성   | 처음 묶으면 끝날 때까지 고정 | 생성 중에도 계속 교체        |
| LLM에 적합성   | 낮을 수 있음          | 높음                  |
| 짧은 요청 처리   | 긴 요청 때문에 대기 가능   | 끝나면 바로 반환           |
| GPU 활용률    | 떨어질 수 있음         | 높아질 수 있음            |
| throughput | 제한적일 수 있음        | 증가 가능               |

정리하면 이렇다.

```text
Static batching
= 한 번 태운 버스가 종점까지 같이 감

Continuous batching
= 중간 정류장에서 내리고 새 승객이 계속 탐
```

LLM 서빙에서는 continuous batching이 특히 중요하다.

---

## 9. Prefill과 Decode

LLM inference는 크게 두 단계로 나눠서 볼 수 있다.

```text
1. Prefill
2. Decode
```

### Prefill

Prefill은 사용자가 넣은 prompt를 한 번에 처리하는 단계다.

```text
사용자 입력 prompt
↓
모델이 전체 prompt를 읽음
↓
KV cache 생성
↓
첫 토큰 생성 준비
```

이 단계는 prompt 길이에 영향을 많이 받는다.

```text
prompt가 길수록 prefill 비용 증가
```

### Decode

Decode는 출력 토큰을 하나씩 생성하는 단계다.

```text
첫 번째 토큰 생성
↓
두 번째 토큰 생성
↓
세 번째 토큰 생성
↓
...
```

LLM 응답이 길수록 decode 시간이 길어진다.

```text
응답이 길수록 decode 비용 증가
```

vLLM은 chunked prefill 같은 기능도 제공해서 prefill이 너무 길 때 스케줄링 효율을 높일 수 있다. vLLM GitHub는 continuous batching과 함께 chunked prefill, prefix caching을 주요 기능으로 소개한다. ([GitHub][1])

---

## 10. vLLM과 Latency

vLLM에서도 latency는 중요하다.

LLM에서는 latency를 보통 이렇게 나눠서 본다.

```text
TTFT = Time To First Token
TPOT = Time Per Output Token
E2E latency = 전체 응답 완료 시간
```

vLLM은 PagedAttention과 continuous batching으로 GPU 메모리와 스케줄링 효율을 높여, 특히 많은 요청이 동시에 들어오는 상황에서 throughput을 높이는 데 강점이 있다.

다만 batch를 많이 묶으면 개별 요청 latency와 trade-off가 생길 수 있다.

```text
throughput 최적화
= GPU를 바쁘게 함
= 많은 요청 처리
= 일부 요청 latency는 늘 수 있음
```

그래서 운영에서는 vLLM을 쓴다고 끝이 아니라 이런 값을 같이 봐야 한다.

```text
TTFT
TPOT
E2E latency
tokens/sec
GPU memory usage
concurrency
queue time
```

---

## 11. vLLM과 Throughput

vLLM이 특히 강조하는 쪽은 throughput이다.

LLM 서버에서는 throughput을 보통 이렇게 본다.

```text
requests/sec
tokens/sec
output tokens/sec
GPU당 tokens/sec
```

vLLM의 목표는 같은 GPU로 더 많은 요청과 토큰을 처리하는 것이다.

```text
PagedAttention
→ KV cache 메모리 효율 증가

Continuous batching
→ GPU idle 감소

Optimized kernels
→ 토큰 생성 속도 개선

결과
→ throughput 증가 가능
```

공식 GitHub도 vLLM의 장점으로 state-of-the-art serving throughput과 memory-efficient inference를 내세운다. ([GitHub][1])

---

## 12. vLLM과 OpenAI-compatible API

vLLM의 실무 장점 중 하나는 OpenAI-compatible server를 제공한다는 점이다.

즉, OpenAI API를 호출하던 코드와 비슷한 방식으로 vLLM 서버를 호출할 수 있다.

vLLM 공식 문서에 따르면 vLLM은 OpenAI의 Completions API, Chat Completions API, Responses API 등과 호환되는 서버를 제공하며, 공식 OpenAI Python client로도 상호작용할 수 있다. ([vLLM][2])

예를 들어 서버를 띄우면 클라이언트에서는 이런 식으로 호출하는 구조가 가능하다.

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY"
)

response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[
        {"role": "user", "content": "CUDA가 뭐야?"}
    ]
)

print(response.choices[0].message.content)
```

핵심은 이것이다.

```text
OpenAI API 스타일 클라이언트
↓
base_url만 vLLM 서버로 변경
↓
로컬 또는 사내 LLM 호출
```

이게 운영과 개발에서 꽤 편하다.

---

## 13. vLLM 서버 실행 예시

vLLM은 OpenAI-compatible API server 형태로 띄울 수 있다.

```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct
```

또는 Docker로 띄우는 흐름도 많이 쓴다.

```bash
docker run --gpus all \
  -p 8000:8000 \
  vllm/vllm-openai \
  --model meta-llama/Llama-3.1-8B-Instruct
```

실제 환경에서는 모델 라이선스, Hugging Face token, GPU 메모리, CUDA 버전, 컨테이너 이미지 버전을 함께 맞춰야 한다.

---

## 14. vLLM과 Hugging Face 모델

vLLM은 Hugging Face 생태계와 잘 맞는다.

보통 이런 모델들을 서빙할 때 쓴다.

```text
Llama 계열
Qwen 계열
Mistral 계열
Mixtral 계열
Gemma 계열
DeepSeek 계열
```

흐름은 대략 이렇다.

```text
Hugging Face model id 지정
↓
vLLM이 모델 로드
↓
GPU 메모리에 올림
↓
OpenAI-compatible API로 요청 처리
```

즉, 직접 PyTorch inference loop를 짜지 않아도 LLM 서버를 띄울 수 있다.

---

## 15. vLLM과 Quantization

vLLM은 다양한 quantization도 지원한다.

공식 GitHub는 FP8, INT8, INT4, GPTQ, AWQ, GGUF, compressed-tensors, TorchAO 등 여러 quantization 형식을 지원한다고 설명한다. ([GitHub][1])

quantization을 쓰는 이유는 같다.

```text
모델 메모리 감소
↓
더 작은 GPU에서 실행 가능
↓
더 큰 batch/concurrency 가능
↓
throughput 증가 가능
```

하지만 quantization은 항상 검증이 필요하다.

```text
속도는 빨라졌는가?
GPU 메모리는 줄었는가?
응답 품질은 유지되는가?
긴 문맥에서 이상 없는가?
```

---

## 16. vLLM과 TensorRT-LLM 차이

LLM inference를 공부하면 TensorRT-LLM도 나온다.

둘 다 LLM 추론 최적화에 쓰인다.

아주 단순히 보면 이렇다.

| 구분   | vLLM                                          | TensorRT-LLM              |
| ---- | --------------------------------------------- | ------------------------- |
| 성격   | LLM serving engine                            | NVIDIA 중심 LLM 최적화 라이브러리   |
| 강점   | 사용 편의성, OpenAI-compatible API, PagedAttention | NVIDIA GPU 최적화, 고성능 엔진 빌드 |
| 접근   | 비교적 빠르게 서버 띄우기 쉬움                             | 최적화와 빌드 과정이 더 복잡할 수 있음    |
| 주 사용 | 운영형 LLM API 서버                                | NVIDIA GPU 극한 최적화         |

입문 단계에서는 이렇게 잡으면 된다.

```text
vLLM
= LLM을 쉽게, 빠르게 서빙하기 좋은 엔진

TensorRT-LLM
= NVIDIA GPU에 더 깊게 맞춘 LLM 최적화 스택
```

---

## 17. vLLM과 Triton 차이

Triton과 vLLM도 헷갈릴 수 있다.

둘 다 inference serving과 관련이 있다.

하지만 초점이 다르다.

| 구분    | Triton Inference Server                     | vLLM                                                |
| ----- | ------------------------------------------- | --------------------------------------------------- |
| 주 대상  | 다양한 AI 모델                                   | LLM 중심                                              |
| 지원 모델 | TensorRT, ONNX, PyTorch, Python 등           | 주로 Transformer 기반 LLM                               |
| 강점    | 범용 모델 서빙, ensemble, backend 다양성             | LLM KV cache, continuous batching, OpenAI API       |
| 핵심 기능 | model repository, dynamic batching, metrics | PagedAttention, continuous batching, prefix caching |
| 사용 예  | 이미지 모델, 추천 모델, OCR, 여러 모델 서빙                | Llama/Qwen/Mistral 같은 LLM API 서빙                    |

정리하면 이렇다.

```text
Triton
= 다양한 모델을 운영 서버로 서빙하는 범용 inference server

vLLM
= LLM을 고효율로 서빙하는 특화 엔진
```

그래서 LLM API 서버를 빠르게 띄우고 싶으면 vLLM이 자연스럽고, 여러 종류의 모델을 한 서버에서 관리해야 하면 Triton이 더 어울릴 수 있다.

---

## 18. vLLM을 쓰면 좋은 상황

vLLM이 잘 맞는 상황은 이렇다.

```text
LLM을 직접 API로 서빙하고 싶을 때
OpenAI-compatible API가 필요할 때
동시 요청이 많을 때
GPU 메모리를 효율적으로 쓰고 싶을 때
tokens/sec를 높이고 싶을 때
Hugging Face 모델을 빠르게 배포하고 싶을 때
streaming output이 필요할 때
```

특히 이런 서비스에 잘 맞는다.

```text
사내 챗봇
RAG 챗봇
코드 어시스턴트
문서 요약 API
LLM 기반 질의응답 API
Agent backend
```

---

## 19. vLLM이 항상 정답은 아니다

vLLM이 좋지만 항상 필요한 것은 아니다.

조심해야 하는 상황도 있다.

```text
LLM이 아니라 이미지/음성/추천 모델 중심인 경우
작은 PoC라서 단순 Transformers pipeline이면 충분한 경우
GPU가 없거나 로컬 CPU 실험만 하는 경우
모델이 vLLM에서 지원되지 않는 구조인 경우
전처리/후처리 비즈니스 로직이 훨씬 중요한 경우
정교한 TensorRT-LLM 최적화가 필요한 경우
```

즉, vLLM은 **LLM serving에 특화된 도구**다.

범용 AI 모델 서버 전체를 대체한다기보다, LLM API 서버 쪽에서 강한 선택지라고 보는 게 맞다.

---

## 20. vLLM 운영에서 봐야 할 지표

vLLM을 운영한다면 다음 지표를 봐야 한다.

```text
TTFT
TPOT
E2E latency
requests/sec
tokens/sec
GPU memory usage
GPU utilization
running requests
waiting requests
KV cache usage
error rate
```

특히 LLM은 “응답 하나가 빠른가”와 “동시에 얼마나 많이 처리하는가”를 같이 봐야 한다.

```text
latency
= 사용자 한 명의 체감 속도

throughput
= 서버 전체 처리량

KV cache usage
= 동시 요청과 긴 문맥을 버티는 힘
```

---

## 21. 전체 그림으로 정리

지금까지 공부한 개념을 연결하면 이렇게 된다.

```text
[Training]
PyTorch
loss.backward()
optimizer.step()

        ↓

[Inference 기본]
model.eval()
torch.inference_mode()

        ↓

[LLM Serving 문제]
토큰 단위 생성
KV cache
동시 요청
긴 문맥
latency / throughput

        ↓

[vLLM]
PagedAttention
Continuous Batching
Prefix Caching
Chunked Prefill
OpenAI-compatible API
Quantization

        ↓

[Operation]
FastAPI / Gateway
RAG pipeline
Kubernetes
Prometheus / Grafana
GPU monitoring
```

즉, vLLM은 이 전체 흐름에서 **LLM inference serving 엔진**에 해당한다.

---

## 22. 최종 정리

vLLM은 LLM을 빠르고 메모리 효율적으로 서빙하기 위한 오픈소스 inference engine이다.

```text
vLLM
= LLM 전용 고효율 inference/serving 엔진
```

핵심 기능은 두 가지로 먼저 잡으면 된다.

```text
PagedAttention
= KV cache 메모리를 block 단위로 효율적으로 관리

Continuous Batching
= 들어오는 요청을 계속 동적으로 batch에 넣어 GPU 활용률을 높임
```

Triton과 비교하면 이렇게 정리할 수 있다.

```text
Triton
= 다양한 AI 모델을 서빙하는 범용 inference server

vLLM
= LLM을 고효율로 서빙하는 특화 inference engine
```

TensorRT와 비교하면 이렇게 볼 수 있다.

```text
TensorRT
= NVIDIA GPU에서 모델을 최적화하는 엔진

vLLM
= LLM 요청 스케줄링, KV cache 관리, OpenAI-compatible API까지 포함한 serving 엔진
```

한 문장으로 정리하면 이렇다.

```text
vLLM은 LLM 서버가 GPU 메모리를 덜 낭비하고, 동시 요청을 더 많이 처리하며, OpenAI API처럼 쉽게 서빙되도록 만든 LLM 추론 엔진이다.
```

AI DevOps 관점에서는 vLLM을 단순 라이브러리로 보면 안 된다.

```text
LLM 모델을 올리고
요청을 batch 처리하고
KV cache를 관리하고
tokens/sec를 높이고
latency를 모니터링하는
LLM serving 핵심 컴포넌트
```

그래서 RAG 챗봇이나 사내 LLM API 서버를 직접 운영하려면 vLLM은 꼭 한 번 이해해볼 만한 기술이다.

[1]: https://github.com/vllm-project/vllm?utm_source=chatgpt.com "vllm-project/vllm: A high-throughput and memory-efficient ..."
[2]: https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html?utm_source=chatgpt.com "OpenAI-Compatible Server - vLLM"
