---
title: "[AI Infra] KServe는 도대체 뭘까? Kubernetes 위에서 모델 서빙을 운영화하는 플랫폼"
source: "https://velog.io/@yorange50/AI-Infra-KServe는-도대체-뭘까-Kubernetes-위에서-모델-서빙을-운영화하는-플랫폼"
published: "2026-05-07T09:11:00.926Z"
tags: ""
backup_date: "2026-05-29T14:52:52.768448"
---

지금까지 정리한 흐름을 보면 이렇게 이어진다.

```text
PyTorch
↓
Inference
↓
Batch / Latency / Throughput
↓
ONNX
↓
TensorRT
↓
Triton Inference Server
↓
vLLM
```

여기까지는 주로 **모델을 어떻게 빠르게 실행하고 서빙할 것인가**에 가까웠다.

그런데 실제 운영에서는 한 단계 더 큰 문제가 생긴다.

```text
모델 서버를 Kubernetes에 어떻게 배포하지?
트래픽이 늘어나면 어떻게 자동 확장하지?
모델 버전은 어떻게 관리하지?
새 모델을 일부 트래픽에만 테스트하려면?
Triton, vLLM, sklearn, PyTorch 모델을 통일된 방식으로 배포하려면?
GPU 리소스는 어떻게 요청하지?
```

이때 등장하는 것이 **KServe**다.

---

## 1. KServe 한 줄 정의

KServe는 **Kubernetes 위에서 AI 모델을 배포, 확장, 라우팅, 관리하기 위한 모델 서빙 플랫폼**이다.

```text
KServe
= Kubernetes-native AI inference platform
= 모델 서빙을 위한 Kubernetes CRD 기반 플랫폼
```

공식 문서에서도 KServe는 predictive AI와 generative AI 모델을 Kubernetes에서 표준 방식으로 서빙하기 위한 플랫폼이며, autoscaling, networking, health check, server configuration 같은 복잡도를 감싸주는 역할을 한다고 설명한다. ([KServe][1])

쉽게 말하면 이렇다.

```text
Triton / vLLM / PyTorch 서버
= 모델을 실제로 실행하는 서버

KServe
= 그 모델 서버들을 Kubernetes 위에서 배포하고 운영하는 관리자
```

---

## 2. 왜 KServe가 필요할까?

모델 하나를 직접 띄우는 건 FastAPI나 Triton으로도 가능하다.

예를 들어 FastAPI로 직접 모델을 띄우면 이런 식이다.

```text
FastAPI 서버 실행
↓
모델 로드
↓
/predict API 호출
↓
결과 반환
```

그런데 운영 환경에서는 직접 챙겨야 할 게 많다.

```text
Deployment 작성
Service 작성
Ingress 작성
GPU resource 설정
HPA 설정
health check 설정
모델 버전 관리
canary rollout
metrics 연결
model storage 연결
```

모델이 하나면 버틸 수 있다.

하지만 모델이 여러 개가 되면 점점 복잡해진다.

```text
image-classifier
text-classifier
reranker
embedding-model
llm-chat
fraud-detector
recommendation-model
```

이걸 매번 직접 Kubernetes YAML로 관리하면 운영 부담이 커진다.

KServe는 이 복잡도를 `InferenceService`라는 하나의 Kubernetes 리소스로 추상화한다.

---

## 3. InferenceService란?

KServe의 핵심은 **InferenceService**다.

```text
InferenceService
= 모델 서빙을 표현하는 KServe의 핵심 Kubernetes Custom Resource
```

공식 문서에서도 InferenceService는 ML 모델 배포를 단순화하고, 자동 scaling, networking, health check를 제공하는 core Kubernetes custom resource라고 설명한다. ([KServe][1])

예를 들면 이런 YAML 하나로 모델을 배포할 수 있다.

```yaml
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: "sklearn-iris"
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn
      storageUri: "gs://kfserving-examples/models/sklearn/1.0/model"
```

이 YAML의 의미는 이렇다.

```text
sklearn-iris라는 모델 서비스를 만든다.
모델 포맷은 sklearn이다.
모델 파일은 storageUri 위치에서 가져온다.
KServe가 이 모델을 서빙 가능한 서비스로 띄운다.
```

즉, 사용자는 “어떤 모델을 어디서 가져와서 어떤 런타임으로 띄울지”만 선언한다.

나머지 Kubernetes 배포, 네트워킹, 스케일링은 KServe가 관리한다.

---

## 4. KServe는 Kubernetes CRD다

KServe를 이해하려면 CRD를 알아야 한다.

```text
CRD = Custom Resource Definition
```

Kubernetes에는 기본 리소스가 있다.

```text
Pod
Deployment
Service
Ingress
ConfigMap
Secret
```

그런데 KServe는 여기에 새로운 리소스를 추가한다.

```text
InferenceService
ServingRuntime
ClusterServingRuntime
InferenceGraph
```

즉, KServe는 Kubernetes에게 이런 말을 할 수 있게 만든다.

```text
"이건 그냥 Deployment가 아니라 모델 서빙 서비스야."
```

사용자는 `InferenceService`를 만들고, KServe Controller가 이를 보고 실제 Kubernetes 리소스를 생성한다.

```text
InferenceService YAML
↓
KServe Controller
↓
Deployment / Service / Route / Autoscaler / Model Server
↓
Inference API 제공
```

---

## 5. KServe의 큰 구조

KServe 구조는 크게 두 가지로 볼 수 있다.

```text
Control Plane
Data Plane
```

### Control Plane

Control Plane은 모델 서빙 리소스의 생명주기를 관리한다.

```text
InferenceService 생성 감지
모델 서버 생성
revision 관리
canary rollout
A/B testing
autoscaling 설정
health check 관리
```

공식 문서에서도 KServe control plane은 모델 lifecycle을 관리하고 revision tracking, canary rollout, A/B testing을 제공한다고 설명한다. ([KServe][1])

### Data Plane

Data Plane은 실제 inference 요청이 흐르는 부분이다.

```text
HTTP/gRPC 요청
↓
KServe endpoint
↓
model server
↓
model inference
↓
응답 반환
```

공식 문서에 따르면 KServe data plane은 predictive와 generative model을 위한 표준 inference protocol과 request/response API를 제공한다. ([KServe][1])

---

## 6. KServe와 Triton의 차이

Triton과 KServe는 헷갈리기 쉽다.

둘 다 모델 서빙과 관련 있기 때문이다.

하지만 역할이 다르다.

| 구분    | Triton Inference Server                    | KServe                                        |
| ----- | ------------------------------------------ | --------------------------------------------- |
| 역할    | 모델을 실제로 실행하는 inference server              | Kubernetes 위에서 모델 서빙을 배포/운영하는 platform        |
| 관심사   | dynamic batching, backend, model execution | autoscaling, rollout, routing, CRD, lifecycle |
| 위치    | 모델 서버                                      | 모델 서빙 운영 계층                                   |
| 실행 대상 | TensorRT, ONNX, PyTorch 등                  | Triton, vLLM, MLServer, sklearn server 등      |
| 비유    | 엔진                                         | 배차/운영 시스템                                     |

관계는 이렇게 볼 수 있다.

```text
TensorRT engine
↓
Triton Inference Server
↓
KServe InferenceService
↓
Kubernetes
```

즉, Triton은 **모델을 실행하는 서버**고, KServe는 **그 서버를 Kubernetes에서 운영하는 플랫폼**이다.

---

## 7. KServe와 vLLM의 차이

vLLM은 LLM inference serving engine이다.

KServe는 그 vLLM 서버를 Kubernetes 위에서 배포하고 관리할 수 있다.

```text
vLLM
= LLM을 빠르게 서빙하는 엔진

KServe
= vLLM 같은 모델 서버를 Kubernetes에서 운영하는 플랫폼
```

공식 KServe 문서도 GenAI model serving을 강조하고 있으며, OpenAI-compatible API, streaming response, embeddings 같은 LLM serving 기능을 지원한다고 설명한다. ([KServe][2])

예를 들어 KServe로 Hugging Face LLM을 배포하는 YAML은 이런 식의 구조를 가질 수 있다.

```yaml
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: "llm-service"
spec:
  predictor:
    model:
      modelFormat:
        name: huggingface
      resources:
        limits:
          cpu: "6"
          memory: 24Gi
          nvidia.com/gpu: "1"
      storageUri: "hf://meta-llama/Llama-3.1-8B-Instruct"
```

공식 KServe 메인 문서에도 Hugging Face 모델을 `storageUri: "hf://..."`로 지정하고 GPU resource limit을 설정하는 LLM InferenceService 예시가 나온다. ([KServe][1])

---

## 8. KServe가 지원하는 모델 종류

KServe는 특정 프레임워크 하나만 위한 도구가 아니다.

공식 문서와 GitHub 설명에 따르면 KServe는 predictive AI와 generative AI를 모두 지원하며, TensorFlow, PyTorch, scikit-learn, XGBoost, ONNX, Hugging Face 같은 다양한 모델을 Kubernetes에서 서빙할 수 있다. ([GitHub][3])

예를 들면 이런 모델들을 올릴 수 있다.

```text
TensorFlow model
PyTorch model
ONNX model
Scikit-learn model
XGBoost model
Hugging Face LLM
Custom container model
Triton model
vLLM backend model
```

그래서 KServe는 모델 종류가 많아질수록 의미가 커진다.

```text
모델마다 배포 방식이 다름
↓
운영 복잡도 증가
↓
KServe가 표준 InferenceService로 추상화
```

---

## 9. Predictor, Transformer, Explainer

KServe의 고전적인 구조에서 자주 나오는 개념이 있다.

```text
Predictor
Transformer
Explainer
```

### Predictor

Predictor는 실제 모델 추론을 담당한다.

```text
입력 tensor
↓
모델 실행
↓
예측 결과
```

예를 들어 sklearn, PyTorch, ONNX, TensorRT 모델 서버가 predictor가 된다.

### Transformer

Transformer는 전처리와 후처리를 담당할 수 있다.

```text
원본 요청
↓
전처리
↓
Predictor 호출
↓
후처리
↓
응답 반환
```

예를 들어 이미지 base64를 tensor로 바꾸거나, 모델 출력을 label 이름으로 바꾸는 역할을 할 수 있다.

### Explainer

Explainer는 모델 결과를 설명하는 컴포넌트다.

```text
왜 이런 예측이 나왔는가?
어떤 feature가 영향을 줬는가?
```

공식 KServe 소개에서도 pre/post processing과 explainability를 기능으로 제공한다고 설명한다. ([KServe][1])

---

## 10. KServe와 Autoscaling

KServe의 중요한 장점 중 하나는 autoscaling이다.

모델 서비스는 트래픽이 일정하지 않다.

```text
낮에는 요청 많음
밤에는 요청 적음
특정 이벤트 때 요청 폭증
평소에는 거의 없음
```

KServe는 Kubernetes 환경에서 모델 서버를 자동으로 확장하거나 줄일 수 있게 한다.

```text
요청 증가
↓
Pod 증가
↓
처리량 증가

요청 감소
↓
Pod 감소
↓
비용 절감
```

KServe 공식 문서는 autoscaling, networking, health checking을 InferenceService가 감싸준다고 설명한다. ([KServe][1])

특히 GenAI 문서에서는 token throughput, queue depth, GPU utilization 같은 metric 기반 autoscaling도 언급한다. ([KServe][2])

즉, LLM serving에서는 단순 CPU 사용률이 아니라 이런 지표가 중요해진다.

```text
tokens/sec
waiting requests
GPU utilization
queue depth
KV cache usage
```

---

## 11. Canary Rollout과 A/B Testing

모델은 코드보다 더 조심스럽게 배포해야 한다.

새 모델이 성능이 더 좋을 수도 있지만, 특정 케이스에서 이상한 결과를 낼 수도 있다.

```text
기존 모델 v1
새 모델 v2
```

새 모델을 바로 100% 배포하면 위험하다.

그래서 일부 트래픽만 새 모델로 보내는 방식이 필요하다.

```text
90% traffic → model v1
10% traffic → model v2
```

이게 canary rollout이다.

KServe 공식 문서에서도 canary rollout과 A/B testing을 제공한다고 설명한다. ([KServe][1])

이 기능은 AI 모델 운영에서 중요하다.

```text
새 모델을 일부 사용자에게만 테스트
성능 지표 확인
문제 없으면 점진적으로 확대
문제 있으면 롤백
```

---

## 12. KServe와 Model Storage

모델 파일은 보통 컨테이너 이미지 안에 직접 넣지 않는다.

대신 외부 저장소에 둔다.

```text
S3
GCS
Azure Blob
PVC
Hugging Face Hub
```

KServe의 `storageUri`는 모델 파일 위치를 가리킨다.

```yaml
storageUri: "s3://my-bucket/models/resnet"
```

또는 Hugging Face 모델이면 이런 식이다.

```yaml
storageUri: "hf://meta-llama/Llama-3.1-8B-Instruct"
```

KServe는 이 위치에서 모델을 가져와서 적절한 model server에 올린다.

이 구조는 모델과 서버 이미지를 분리하는 데 도움이 된다.

```text
컨테이너 이미지
= 서빙 런타임

모델 파일
= 외부 저장소

InferenceService
= 둘을 연결하는 선언
```

---

## 13. KServe와 ServingRuntime

KServe에는 `ServingRuntime`이라는 개념도 있다.

```text
ServingRuntime
= 특정 모델 포맷을 어떤 서버 이미지로 실행할지 정의하는 리소스
```

예를 들어 ONNX 모델은 ONNX Runtime 기반 서버로 띄울 수 있고, sklearn 모델은 sklearn server로 띄울 수 있다.

```text
modelFormat: onnx
↓
ONNX Runtime ServingRuntime

modelFormat: sklearn
↓
SKLearn ServingRuntime
```

즉, InferenceService는 “이 모델을 서빙해줘”라고 말하고, ServingRuntime은 “이 모델 포맷은 이 서버로 실행할게”를 정의한다.

---

## 14. KServe와 RawDeployment / Serverless

KServe는 배포 모드에 따라 동작 방식이 달라질 수 있다.

크게 보면 이런 흐름이다.

```text
Serverless mode
RawDeployment mode
ModelMesh mode
```

다만 2026년 기준 일부 배포판에서는 Serverless나 ModelMesh 관련 정책이 달라지고 있다. 예를 들어 Red Hat OpenShift AI 3.x 문서에서는 ModelMesh와 Serverless Deployment Mode가 deprecated되어 RawDeployment mode로 마이그레이션해야 한다고 안내한다. ([Red Hat Customer Portal][4])

그래서 실무에서는 “KServe는 무조건 Knative serverless다”라고 외우기보다, 현재 사용하는 배포판과 버전에서 어떤 deployment mode를 권장하는지 확인해야 한다.

입문 단계에서는 이렇게 잡으면 충분하다.

```text
RawDeployment
= 일반 Kubernetes Deployment 방식에 가까움

Serverless
= Knative 기반 scale-to-zero와 request 기반 autoscaling 활용

ModelMesh
= 많은 수의 모델을 효율적으로 올리기 위한 multi-model serving 계열
```

---

## 15. KServe와 Kubernetes 리소스

KServe를 쓰더라도 결국 Kubernetes 위에서 돈다.

즉, 아래 개념은 여전히 중요하다.

```text
Pod
Deployment
Service
Ingress / Gateway
Namespace
Resource Request / Limit
GPU Device Plugin
ConfigMap
Secret
PVC
HPA / KEDA
```

KServe는 이것들을 완전히 없애는 게 아니다.

사용자가 직접 다 작성하지 않아도 되게 추상화한다.

```text
사용자:
InferenceService 작성

KServe:
필요한 Kubernetes 리소스 생성/관리
```

그래서 Kubernetes 기본기가 있으면 KServe 이해가 훨씬 쉬워진다.

---

## 16. KServe를 쓰는 전체 흐름

예를 들어 ONNX 모델을 KServe로 배포한다고 하면 흐름은 이렇다.

```text
1. PyTorch로 모델 학습
2. ONNX로 export
3. 모델 파일을 S3/GCS/PVC 등에 업로드
4. KServe InferenceService YAML 작성
5. kubectl apply
6. KServe Controller가 모델 서버 생성
7. endpoint로 inference 요청
8. latency / throughput / error rate 모니터링
```

명령어는 대략 이런 느낌이다.

```bash
kubectl apply -f inferenceservice.yaml
```

상태 확인은 이런 식으로 한다.

```bash
kubectl get inferenceservice
kubectl describe inferenceservice sklearn-iris
kubectl get pods
kubectl logs <pod-name>
```

KServe도 결국 Kubernetes 리소스이기 때문에 `kubectl`로 확인한다.

---

## 17. KServe와 MLOps 관점

MLOps에서 중요한 것은 모델을 한 번 띄우는 것이 아니다.

운영 가능한 흐름을 만드는 것이다.

```text
모델 학습
↓
모델 검증
↓
모델 저장
↓
모델 배포
↓
트래픽 라우팅
↓
모니터링
↓
롤백 / 재배포
```

KServe는 이 중 **모델 배포와 서빙 운영**을 담당한다.

```text
KServe가 담당하는 영역
= 모델 서버 배포
= endpoint 생성
= autoscaling
= canary rollout
= model runtime 연결
= inference request handling
```

즉, KServe는 MLflow 같은 실험/모델 레지스트리 도구와도 같이 쓸 수 있고, Argo CD 같은 GitOps 도구와도 연결될 수 있다.

```text
MLflow
= 모델 저장/등록

KServe
= 모델 서빙

Argo CD
= InferenceService YAML GitOps 배포

Prometheus/Grafana
= 운영 모니터링
```

---

## 18. KServe와 기존에 공부한 개념 연결

지금까지 배운 개념을 KServe와 연결하면 이렇게 된다.

```text
PyTorch
= 모델 학습/개발

ONNX
= 모델 교환 포맷

TensorRT
= NVIDIA GPU 추론 최적화

Triton
= 다양한 모델을 실행하는 inference server

vLLM
= LLM 특화 inference engine

KServe
= Kubernetes 위에서 이런 모델 서버들을 배포/운영하는 serving platform
```

한 장으로 보면 이렇다.

```text
[Training]
PyTorch

    ↓

[Export / Optimize]
ONNX
TensorRT
Quantization

    ↓

[Model Server]
Triton
vLLM
MLServer
TorchServe
Custom FastAPI

    ↓

[Serving Platform]
KServe

    ↓

[Infrastructure]
Kubernetes
GPU Node
Gateway / Ingress
Prometheus / Grafana
Autoscaling
```

---

## 19. KServe를 쓰면 좋은 상황

KServe가 잘 맞는 상황은 이렇다.

```text
Kubernetes 위에서 모델을 운영해야 할 때
모델이 여러 개일 때
팀마다 모델 포맷이 다를 때
표준화된 inference 배포 방식이 필요할 때
autoscaling이 필요할 때
canary rollout이 필요할 때
Triton/vLLM 같은 서버를 Kubernetes에서 관리하고 싶을 때
MLOps 플랫폼을 만들고 싶을 때
```

특히 AI 플랫폼 팀이나 DevOps/MLOps 팀 입장에서는 KServe가 의미 있다.

```text
개발자는 모델과 YAML만 제공
플랫폼은 KServe로 배포 표준화
운영팀은 Kubernetes와 모니터링으로 관리
```

---

## 20. KServe가 항상 필요한 건 아니다

KServe는 강력하지만, 무조건 필요한 도구는 아니다.

이런 상황에서는 오히려 복잡할 수 있다.

```text
모델 하나만 간단히 테스트하는 PoC
Kubernetes를 아직 쓰지 않는 환경
트래픽이 거의 없는 내부 실험
FastAPI 하나로 충분한 작은 서비스
팀에 Kubernetes 운영 경험이 없는 경우
```

이럴 때는 처음부터 KServe로 가기보다 이렇게 시작해도 된다.

```text
1단계: PyTorch + FastAPI
2단계: ONNX / TensorRT 최적화
3단계: Triton 또는 vLLM으로 모델 서버 분리
4단계: Kubernetes 배포
5단계: KServe로 표준화
```

즉, KServe는 “처음 모델을 돌리는 도구”라기보다 “운영 환경에서 모델 서빙을 표준화하는 도구”에 가깝다.

---

## 21. 최종 정리

KServe는 Kubernetes 위에서 AI 모델을 운영하기 위한 모델 서빙 플랫폼이다.

```text
KServe
= Kubernetes-native model serving platform
```

핵심 리소스는 InferenceService다.

```text
InferenceService
= 모델 서빙을 선언하는 Kubernetes Custom Resource
```

KServe가 해주는 일은 다음과 같다.

```text
모델 서버 배포
모델 runtime 연결
endpoint 생성
autoscaling
health check
traffic routing
canary rollout
A/B testing
predictive / generative model serving
```

Triton, vLLM과 비교하면 이렇게 정리할 수 있다.

```text
Triton
= 다양한 모델을 실제로 실행하는 inference server

vLLM
= LLM을 고효율로 실행하는 inference engine

KServe
= Triton/vLLM 같은 모델 서버를 Kubernetes에서 운영하는 serving platform
```

한 문장으로 정리하면 이렇다.

```text
KServe는 모델 서버를 Kubernetes 위에서 운영 가능한 서비스로 만들어주는 AI inference 운영 플랫폼이다.
```

AI DevOps 관점에서는 KServe를 이렇게 보면 좋다.

```text
모델을 잘 만드는 것
= PyTorch / Training

모델을 빠르게 실행하는 것
= TensorRT / vLLM / Triton

모델을 운영 환경에 안정적으로 배포하는 것
= KServe / Kubernetes
```

즉, KServe는 모델 자체를 빠르게 만드는 기술이라기보다, **모델 서빙을 Kubernetes 운영 체계 안으로 넣어주는 플랫폼**이다.

[1]: https://kserve.github.io/website/?utm_source=chatgpt.com "KServe"
[2]: https://kserve.github.io/website/docs/intro?utm_source=chatgpt.com "Welcome to KServe"
[3]: https://github.com/kserve/kserve?utm_source=chatgpt.com "KServe"
[4]: https://access.redhat.com/articles/7134025?utm_source=chatgpt.com "Converting ModelMesh and Serverless InferenceServices ..."
