---
title: "[Upstage] 업스테이지 AI DevOps 심화 기술면접 예상 질문 정리"
source: ""
published: "2026-05-30T12:00:00.000Z"
---

업스테이지 AI DevOps 심화 기술 인터뷰에서는 단순 개념 암기보다, **AI 제품을 실제 고객사 환경에 어떻게 배포하고 운영할 것인가**를 중심으로 질문이 나올 가능성이 높다.

특히 공고와 업스테이지 제품군을 기준으로 보면 다음 영역이 중요하다.

```text
Docker
Kubernetes
CI/CD
Linux / Network
HTTP / JSON / OAuth
RDBMS / NoSQL
Prometheus / Grafana
RAG
OCR / Document Parse
Information Extract
LLM Gateway
B2B 고객사 연동
장애 대응
품질 회귀 탐지
배포 통제
````

AI DevOps는 단순 운영 조직이 아니라, AI 제품이 고객사 환경에서 안정적으로 동작하도록 **개발, 배포, 운영, 모니터링, 고객 대응을 연결하는 엔지니어링 역할**이다.

---

# 1. AI DevOps 직무 이해

## Q1. AI DevOps는 일반 DevOps와 무엇이 다른가요?

일반 DevOps는 웹 서비스나 백엔드 시스템의 배포 자동화, 인프라 운영, 모니터링, 장애 대응에 집중한다.

AI DevOps는 여기에 AI 특화 요소가 추가된다.

```text
일반 DevOps
- 서버 배포
- CI/CD
- 로그 수집
- 모니터링
- 장애 대응
- 인프라 자동화

AI DevOps
- 모델/API 배포
- OCR/RAG/LLM 파이프라인 운영
- 모델 버전 관리
- 품질 회귀 탐지
- token usage / 비용 관리
- RAG 검색 품질 모니터링
- Document Parse 품질 관리
- 고객사 환경별 배포 표준화
```

즉, AI DevOps는 단순히 서버가 살아 있는지만 보는 것이 아니라, **AI 결과물이 업무적으로 신뢰 가능한지도 함께 운영해야 하는 역할**이다.

면접 답변:

> 일반 DevOps가 서비스의 배포와 안정성을 담당한다면, AI DevOps는 여기에 AI 품질 관리가 추가된 역할이라고 생각합니다. 예를 들어 OCR 파싱 실패율, RAG 검색 품질, LLM token usage, 모델 버전 변경에 따른 품질 회귀까지 함께 봐야 합니다. 결국 AI 제품이 고객사 업무에서 안정적으로 가치가 나도록 배포와 운영 체계를 만드는 역할이라고 이해했습니다.

---

## Q2. 업스테이지 AI DevOps에서 왜 B2B 구축 경험이 중요한가요?

업스테이지는 기업 고객에게 Document AI, LLM, RAG 기반 솔루션을 제공한다.

B2B 환경에서는 고객사마다 조건이 다르다.

```text
클라우드 환경
온프레미스 환경
망분리 환경
고객사 VPC
보안 정책
방화벽 정책
기존 레거시 시스템
고객사 DB
고객사 인증 체계
```

따라서 단순히 API 하나를 만드는 것이 아니라, 고객사 환경에 맞춰 연동 구조를 설계해야 한다.

면접 답변:

> B2B AI 서비스에서는 고객사마다 인프라, 보안 정책, 네트워크, 인증 방식, 데이터 반출 가능 여부가 다르기 때문에 표준화된 배포와 유연한 연동 설계가 중요하다고 생각합니다. AI DevOps는 제품을 고객사 환경에 맞게 안정적으로 구축하고, 이후 유지보수와 모니터링까지 가능하게 만드는 역할이라고 이해했습니다.

---

# 2. Docker

## Q3. Docker를 왜 사용하나요?

Docker는 애플리케이션과 실행 환경을 이미지로 묶어 어디서든 동일하게 실행할 수 있도록 한다.

```text
개발 환경
테스트 환경
운영 환경
고객사 환경
```

이 환경들이 달라도 동일한 이미지로 실행할 수 있기 때문에 배포 안정성이 높아진다.

AI DevOps에서는 다음 컴포넌트를 각각 컨테이너화할 수 있다.

```text
OCR API
Document Parse API
Information Extract API
RAG API
LLM Gateway
Embedding Worker
Batch Worker
Monitoring Agent
```

면접 답변:

> Docker는 애플리케이션과 실행 환경을 이미지로 묶어 배포 환경 차이를 줄이기 위해 사용합니다. AI DevOps에서는 OCR, RAG, LLM Gateway, Worker 같은 컴포넌트를 각각 컨테이너화해 독립적으로 배포하고 운영할 수 있다는 점이 중요하다고 생각합니다.

---

## Q4. Docker 이미지와 컨테이너의 차이는 무엇인가요?

```text
Image
- 실행 가능한 템플릿
- 코드, 라이브러리, 환경 설정 포함
- 불변에 가까운 배포 단위

Container
- 이미지를 실행한 인스턴스
- 실제 프로세스가 실행되는 환경
- 생성, 중지, 삭제 가능
```

면접 답변:

> 이미지는 애플리케이션을 실행하기 위한 템플릿이고, 컨테이너는 그 이미지를 실제로 실행한 인스턴스입니다. 같은 이미지에서 여러 컨테이너를 띄울 수 있습니다.

---

## Q5. Docker와 VM의 차이는 무엇인가요?

```text
VM
- 하이퍼바이저 위에 게스트 OS 전체 실행
- 격리 수준 높음
- 무겁고 시작 속도 느림

Docker Container
- 호스트 OS 커널 공유
- 애플리케이션 실행 환경만 격리
- 가볍고 빠름
```

면접 답변:

> VM은 OS 전체를 가상화하고, Docker는 호스트 커널을 공유하면서 애플리케이션 실행 환경을 격리합니다. 그래서 Docker는 더 가볍고 빠르게 배포할 수 있지만, 커널 공유 구조이므로 보안 설정과 권한 관리가 중요합니다.

---

## Q6. Dockerfile에서 자주 쓰는 명령어는 무엇인가요?

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

주요 명령어:

```text
FROM: base image 지정
WORKDIR: 작업 디렉토리 지정
COPY: 파일 복사
RUN: 이미지 빌드 시 실행할 명령
EXPOSE: 컨테이너가 사용할 포트 명시
CMD: 컨테이너 실행 시 기본 명령
ENTRYPOINT: 컨테이너 실행 진입점
```

---

## Q7. Docker 이미지 크기를 줄이는 방법은 무엇인가요?

```text
slim/alpine base image 사용
불필요한 패키지 제거
멀티스테이지 빌드 사용
캐시 파일 삭제
.dockerignore 사용
레이어 수 최적화
```

면접 답변:

> 이미지 크기가 커지면 빌드와 배포 시간이 길어지고, 네트워크 전송 비용도 증가합니다. 그래서 slim 이미지를 사용하거나 멀티스테이지 빌드를 적용하고, 불필요한 파일은 .dockerignore로 제외하는 방식으로 최적화할 수 있습니다.

---

# 3. Kubernetes 기본 개념

## Q8. Kubernetes를 왜 사용하나요?

Kubernetes는 컨테이너화된 애플리케이션을 배포, 확장, 운영하기 위한 오케스트레이션 플랫폼이다.

AI DevOps에서 Kubernetes가 중요한 이유:

```text
여러 AI 컴포넌트 배포
서비스별 독립 확장
장애 발생 시 자동 복구
Rolling Update
Service Discovery
Ingress Routing
Config/Secret 관리
HPA 기반 Auto Scaling
```

면접 답변:

> Kubernetes는 여러 컨테이너 기반 서비스를 안정적으로 배포하고 운영하기 위해 사용합니다. AI 서비스에서는 OCR API, RAG API, LLM Gateway, Worker처럼 여러 컴포넌트가 존재할 수 있고, 이들을 독립적으로 배포·확장·복구하기 위해 Kubernetes가 유용하다고 생각합니다.

---

## Q9. Pod란 무엇인가요?

Pod는 Kubernetes에서 컨테이너가 실행되는 최소 배포 단위다.

```text
Pod
- 하나 이상의 컨테이너 포함
- 같은 네트워크 namespace 공유
- 같은 storage volume 공유 가능
- 일시적이며 언제든 재생성 가능
```

면접 답변:

> Pod는 Kubernetes에서 컨테이너가 실행되는 최소 단위입니다. 보통 하나의 Pod에 하나의 애플리케이션 컨테이너를 넣지만, 로그 수집이나 프록시 같은 사이드카 컨테이너를 함께 둘 수도 있습니다.

---

## Q10. Deployment란 무엇인가요?

Deployment는 Pod의 원하는 상태를 유지하는 컨트롤러다.

```text
Deployment 역할
- Replica 수 유지
- Rolling Update
- Rollback
- Pod 장애 시 재생성
```

면접 답변:

> Pod는 직접 관리하기보다 Deployment로 관리합니다. Deployment는 원하는 replica 수를 유지하고, 업데이트나 롤백을 지원하기 때문에 운영 환경에서 안정적인 배포 단위로 사용됩니다.

---

## Q11. ReplicaSet과 Deployment의 차이는 무엇인가요?

```text
ReplicaSet
- 지정한 수의 Pod 유지

Deployment
- ReplicaSet을 관리
- Rolling Update, Rollback 제공
```

면접 답변:

> ReplicaSet은 Pod 개수를 유지하는 역할이고, Deployment는 ReplicaSet을 관리하면서 업데이트와 롤백 같은 배포 기능까지 제공합니다. 실제 운영에서는 보통 Deployment를 직접 사용합니다.

---

## Q12. Service란 무엇인가요?

Pod는 재생성될 때 IP가 바뀔 수 있다.
Service는 이런 Pod 집합에 안정적인 접근 지점을 제공한다.

```text
Service 역할
- Pod IP 변경 문제 해결
- Label Selector로 Pod 묶음
- 내부 DNS 이름 제공
- 로드밸런싱
```

Service 종류:

```text
ClusterIP
NodePort
LoadBalancer
ExternalName
```

면접 답변:

> Service는 동적으로 변하는 Pod들 앞에 고정된 접근 지점을 제공하는 리소스입니다. Pod IP가 바뀌어도 Service를 통해 안정적으로 접근할 수 있습니다.

---

## Q13. ClusterIP, NodePort, LoadBalancer 차이는 무엇인가요?

```text
ClusterIP
- 클러스터 내부에서만 접근 가능
- 기본 Service 타입

NodePort
- 각 Node의 특정 포트를 통해 외부 접근 가능
- 테스트나 제한적 외부 노출에 사용

LoadBalancer
- 클라우드 로드밸런서를 생성해 외부 트래픽 연결
- AWS/GCP/Azure 환경에서 자주 사용
```

---

## Q14. Ingress란 무엇인가요?

Ingress는 클러스터 외부 HTTP/HTTPS 트래픽을 내부 Service로 라우팅하는 리소스다.

```text
example.com/ocr → OCR Service
example.com/rag → RAG Service
example.com/llm → LLM Gateway Service
```

Ingress 자체는 규칙이고, 실제 동작은 Ingress Controller가 수행한다.

면접 답변:

> Ingress는 외부 HTTP/HTTPS 요청을 내부 Service로 라우팅하는 규칙입니다. 실제 트래픽 처리는 Nginx Ingress Controller 같은 Ingress Controller가 담당합니다.

---

## Q15. Service와 Ingress 차이는 무엇인가요?

```text
Service
- Pod 집합에 대한 안정적인 접근 지점
- 클러스터 내부 통신 중심

Ingress
- 외부 HTTP/HTTPS 트래픽을 내부 Service로 라우팅
- 도메인, path, TLS 처리 가능
```

면접 답변:

> Service는 내부적으로 Pod에 접근하기 위한 고정 엔드포인트이고, Ingress는 외부에서 들어오는 HTTP 요청을 어떤 Service로 보낼지 정의하는 라우팅 규칙입니다.

---

## Q16. ConfigMap과 Secret 차이는 무엇인가요?

```text
ConfigMap
- 일반 설정값 저장
- 환경변수, 설정 파일로 주입

Secret
- 민감 정보 저장
- 비밀번호, API Key, Token 등
- base64 인코딩되어 저장
```

주의점:

```text
Secret은 암호화가 아니라 base64 인코딩
etcd 암호화, RBAC, 접근 통제 필요
```

면접 답변:

> ConfigMap은 일반 설정값을, Secret은 비밀번호나 API Key 같은 민감정보를 저장할 때 사용합니다. 다만 Secret도 기본적으로 base64 인코딩일 뿐이므로 RBAC와 etcd 암호화 같은 추가 보안 설정이 중요합니다.

---

## Q17. Namespace는 왜 사용하나요?

Namespace는 클러스터 내부 리소스를 논리적으로 분리하는 단위다.

```text
dev
staging
prod
monitoring
customer-a
customer-b
```

사용 목적:

```text
환경 분리
팀별 리소스 분리
고객사별 리소스 분리
권한 분리
리소스 quota 적용
```

면접 답변:

> Namespace는 하나의 클러스터 안에서 환경이나 팀, 고객사별로 리소스를 논리적으로 분리하기 위해 사용합니다. B2B 환경에서는 고객사별 namespace를 나눠 운영할 수도 있다고 생각합니다.

---

# 4. Kubernetes 운영과 장애 대응

## Q18. Pod가 Pending 상태면 어떻게 확인하나요?

Pending은 Pod가 아직 Node에 스케줄링되지 않았거나, 필요한 리소스를 확보하지 못한 상태다.

확인 순서:

```bash
kubectl describe pod <pod-name>
kubectl get nodes
kubectl describe node <node-name>
```

가능한 원인:

```text
CPU/Memory 부족
Node selector 조건 불일치
Taint/Toleration 문제
PVC 바인딩 실패
이미지 pull 전 단계
GPU 리소스 부족
```

면접 답변:

> Pending 상태라면 먼저 describe pod로 이벤트를 확인합니다. 리소스 부족인지, nodeSelector나 taint/toleration 문제인지, PVC 바인딩 문제인지 확인하고, 필요하다면 Node 리소스 상태와 스케줄링 조건을 함께 봅니다.

---

## Q19. Pod가 CrashLoopBackOff 상태면 어떻게 확인하나요?

확인 명령어:

```bash
kubectl logs <pod-name>
kubectl logs <pod-name> --previous
kubectl describe pod <pod-name>
```

가능한 원인:

```text
애플리케이션 실행 오류
환경변수 누락
ConfigMap/Secret 문제
DB 연결 실패
포트 설정 오류
권한 문제
OOMKilled
```

면접 답변:

> CrashLoopBackOff는 컨테이너가 실행 후 반복적으로 죽는 상태입니다. logs와 describe pod를 확인하고, 직전 컨테이너 로그는 --previous 옵션으로 봅니다. 환경변수, 설정 파일, DB 연결, OOMKilled 여부를 순서대로 확인할 것 같습니다.

---

## Q20. ImagePullBackOff는 무엇인가요?

컨테이너 이미지를 가져오지 못하는 상태다.

가능한 원인:

```text
이미지 이름 오류
tag 오류
private registry 인증 실패
네트워크 문제
registry 장애
imagePullSecret 누락
```

대응:

```bash
kubectl describe pod <pod-name>
docker pull <image>
kubectl get secret
```

---

## Q21. OOMKilled는 무엇인가요?

컨테이너가 memory limit을 초과해 종료된 상태다.

확인:

```bash
kubectl describe pod <pod-name>
kubectl top pod
```

대응:

```text
memory limit 조정
애플리케이션 메모리 누수 확인
요청량 확인
worker concurrency 조정
batch size 조정
```

AI 문서 처리에서는 대용량 PDF, 이미지 처리, embedding batch 처리에서 OOM이 발생할 수 있다.

---

## Q22. Readiness Probe와 Liveness Probe 차이는 무엇인가요?

```text
Readiness Probe
- 트래픽을 받을 준비가 되었는지 확인
- 실패하면 Service endpoint에서 제외

Liveness Probe
- 애플리케이션이 살아 있는지 확인
- 실패하면 컨테이너 재시작
```

면접 답변:

> Readiness는 트래픽을 받아도 되는 상태인지 확인하는 것이고, Liveness는 프로세스가 정상적으로 살아 있는지 확인하는 것입니다. 예를 들어 모델 로딩이 끝나기 전에는 readiness가 실패해야 하고, 애플리케이션이 deadlock에 빠지면 liveness 실패로 재시작할 수 있습니다.

---

## Q23. HPA는 무엇인가요?

HPA는 Horizontal Pod Autoscaler로, CPU/Memory 또는 custom metric을 기반으로 Pod 수를 자동 조절한다.

```text
트래픽 증가
→ CPU 상승
→ HPA가 replica 증가
→ 부하 분산
```

AI 서비스에서는 CPU보다 custom metric이 더 적합할 수 있다.

```text
queue length
request latency
GPU utilization
document processing backlog
LLM request count
```

면접 답변:

> HPA는 부하에 따라 Pod 수를 자동으로 늘리거나 줄이는 기능입니다. AI 문서 처리 서비스에서는 CPU뿐 아니라 queue length나 처리 지연 시간 같은 custom metric을 기반으로 autoscaling하는 것이 더 적절할 수 있다고 생각합니다.

---

## Q24. Rolling Update와 Rollback은 어떻게 동작하나요?

Deployment는 새 ReplicaSet을 만들고 기존 Pod를 점진적으로 교체한다.

```text
old pod 일부 종료
new pod 일부 생성
readiness 통과
트래픽 전환
반복
```

문제 발생 시:

```bash
kubectl rollout undo deployment/<name>
```

면접 답변:

> Rolling Update는 서비스 중단을 줄이기 위해 기존 Pod를 조금씩 새 Pod로 교체하는 방식입니다. 문제가 생기면 rollout undo로 이전 ReplicaSet으로 롤백할 수 있습니다.

---

## Q25. Helm은 왜 사용하나요?

Helm은 Kubernetes 리소스를 패키징하고 배포하는 도구다.

```text
Deployment
Service
Ingress
ConfigMap
Secret
HPA
```

이런 리소스를 Chart로 묶고 values.yaml로 환경별 설정을 분리한다.

```text
dev values
staging values
prod values
customer-a values
customer-b values
```

면접 답변:

> Helm은 Kubernetes 리소스를 템플릿화하고 패키징해서 배포하기 위한 도구입니다. 고객사별 설정이나 dev/prod 환경별 설정을 values.yaml로 분리할 수 있어 B2B 배포 표준화에 유용하다고 생각합니다.

---

# 5. CI/CD

## Q26. CI/CD란 무엇인가요?

```text
CI: Continuous Integration
- 코드 변경 시 자동 빌드/테스트
- 통합 오류 조기 발견

CD: Continuous Delivery/Deployment
- 검증된 결과물을 자동 배포 가능한 상태로 만듦
- 또는 실제 운영까지 자동 배포
```

AI DevOps에서는 CI/CD가 모델, 프롬프트, RAG 인덱스, API 서버에도 연결된다.

---

## Q27. Jenkins 파이프라인을 어떻게 구성할 수 있나요?

기본 구조:

```text
Git Push
→ Checkout
→ Test
→ Build
→ Docker Image Build
→ Image Push
→ Deploy
→ Health Check
→ Notify
```

AI 파이프라인 확장:

```text
Git Push
→ Unit Test
→ RAG Evaluation
→ Quality Gate
→ Docker Build
→ Deploy
→ Health Check
→ Monitoring Check
```

면접 답변:

> AI 서비스에서는 일반 테스트뿐 아니라 RAG 품질 평가나 LLM 응답 형식 검증을 배포 전에 수행할 수 있다고 생각합니다. 품질 기준을 통과하지 못하면 배포를 차단하는 구조가 필요합니다.

---

## Q28. 품질 게이트란 무엇인가요?

품질 게이트는 배포 전에 반드시 통과해야 하는 기준이다.

일반 서비스:

```text
테스트 통과
빌드 성공
보안 스캔 통과
성능 기준 통과
```

AI 서비스:

```text
Recall@k 기준 통과
nDCG@k 기준 통과
Answer similarity 기준 통과
Latency 기준 통과
JSON format success rate 기준 통과
Groundedness 기준 통과
```

네 논문에서는 baseline reference 대비 상대 기준을 사용했고, Recall@3, nDCG@3, answer similarity, latency를 함께 품질 게이트 기준으로 정의했다. 

면접 답변:

> 품질 게이트는 배포 전에 품질 기준을 만족하는지 확인하는 장치입니다. AI 서비스에서는 테스트 성공 여부만으로는 부족하고, RAG 검색 품질이나 답변 품질이 기준 이하로 떨어지면 배포를 막아야 한다고 생각합니다. 제 프로젝트에서는 Recall, nDCG, answer similarity, latency를 기준으로 품질 게이트를 정의했습니다.

---

## Q29. 배포 실패 시 어떻게 대응하나요?

확인 순서:

```text
Jenkins stage 확인
빌드 로그 확인
Docker image build 실패 여부
Registry push 실패 여부
Kubernetes deploy 실패 여부
Pod 상태 확인
Health check 실패 여부
최근 변경사항 확인
Rollback 여부 판단
```

면접 답변:

> 먼저 CI/CD 파이프라인의 어느 단계에서 실패했는지 확인합니다. 빌드, 테스트, 이미지 빌드, 배포, 헬스체크 중 실패 지점을 구분하고, 배포 후 장애라면 이전 정상 이미지로 롤백할 수 있어야 한다고 생각합니다.

---

## Q30. Blue-Green, Canary, Rolling 배포 차이는 무엇인가요?

```text
Rolling
- 기존 Pod를 조금씩 새 버전으로 교체
- Kubernetes 기본 배포 방식

Blue-Green
- 기존 환경 Blue, 새 환경 Green
- 검증 후 트래픽 전환
- 롤백 명확

Canary
- 일부 트래픽만 새 버전에 전달
- 지표 확인 후 점진 확대
```

AI 모델 전환에는 Canary가 유리하다.

```text
1% 요청만 새 모델
품질/latency/비용 확인
문제 없으면 확대
```

---

# 6. 모니터링

## Q31. Prometheus와 Grafana 차이는 무엇인가요?

```text
Prometheus
- 메트릭 수집 및 저장
- Pull 방식
- PromQL로 질의
- Alertmanager와 연동 가능

Grafana
- 메트릭 시각화
- 대시보드 구성
- 다양한 데이터 소스 연결
```

면접 답변:

> Prometheus는 메트릭을 수집하고 저장하는 시스템이고, Grafana는 그 메트릭을 시각화해 운영자가 보기 쉽게 대시보드로 보여주는 도구입니다.

---

## Q32. 어떤 메트릭을 봐야 하나요?

일반 API:

```text
request_count
error_rate
latency
p95 latency
p99 latency
CPU usage
memory usage
disk usage
network traffic
```

AI API:

```text
OCR processing time
Document Parse failure rate
Information Extract schema validation failure
RAG retrieval hit rate
Vector DB query latency
LLM input/output token usage
LLM timeout
Agent task completion rate
Evidence match rate
Human review rate
```

면접 답변:

> AI 서비스에서는 일반적인 API 지표뿐 아니라 AI 품질 지표를 함께 봐야 합니다. 예를 들어 OCR 파싱 실패율, RAG 검색 hit rate, LLM token usage, Evidence match rate 같은 지표가 운영 품질과 직접 연결된다고 생각합니다.

---

## Q33. p95 latency는 왜 중요한가요?

평균 latency는 일부 느린 요청을 숨길 수 있다.

```text
평균 latency: 전체 평균
p95 latency: 95% 요청이 이 시간 이하로 처리됨
p99 latency: 최악에 가까운 tail latency 확인
```

면접 답변:

> 평균만 보면 일부 느린 요청이 가려질 수 있기 때문에 p95, p99를 봐야 합니다. AI 문서 처리나 LLM 호출은 요청별 처리 시간이 크게 다를 수 있어 tail latency 관리가 중요하다고 생각합니다.

---

## Q34. Alert는 어떻게 잡을 수 있나요?

예시:

```text
5xx error rate > 5%
p95 latency > 3s
Pod restart count 증가
Queue length > threshold
LLM timeout 증가
RAG 품질 게이트 실패
Document Parse failure rate 증가
Token usage 급증
```

주의점:

```text
너무 민감하면 alert fatigue 발생
너무 둔감하면 장애 감지 지연
중요도별 severity 분리 필요
```

---

# 7. Linux / Network

## Q35. Linux에서 포트가 열려 있는지 어떻게 확인하나요?

```bash
ss -tulnp
netstat -tulnp
lsof -i :8000
```

외부 연결 확인:

```bash
curl http://localhost:8000/health
nc -vz host 8000
telnet host 8000
```

---

## Q36. DNS 문제는 어떻게 확인하나요?

```bash
nslookup example.com
dig example.com
cat /etc/resolv.conf
```

Kubernetes 내부 DNS:

```bash
kubectl exec -it <pod> -- nslookup <service-name>
kubectl exec -it <pod> -- curl http://<service-name>:<port>
```

---

## Q37. HTTP 상태코드 401, 403, 404, 500 차이는요?

```text
401 Unauthorized
- 인증 실패
- token 없음/만료

403 Forbidden
- 인증은 됐지만 권한 없음

404 Not Found
- 리소스 없음
- route/path 오류

500 Internal Server Error
- 서버 내부 오류
```

B2B 연동에서는 401/403이 인증·권한 문제일 가능성이 높다.

---

## Q38. Timeout과 Retry는 어떻게 설계해야 하나요?

Timeout:

```text
외부 API 응답을 무한정 기다리지 않도록 제한
```

Retry:

```text
일시적 장애에 대해 재시도
```

주의점:

```text
무제한 retry 금지
exponential backoff 적용
idempotency 고려
retry storm 방지
```

면접 답변:

> Timeout은 장애 확산을 막기 위해 필요하고, Retry는 일시적 실패 복구를 위해 필요합니다. 다만 재시도는 무제한으로 하면 안 되고, exponential backoff와 최대 횟수 제한을 두어야 합니다. 결제나 데이터 변경 API라면 idempotency도 고려해야 합니다.

---

# 8. HTTP / JSON / OAuth / 보안

## Q39. REST API란 무엇인가요?

REST는 자원을 URI로 표현하고 HTTP method로 행위를 표현하는 방식이다.

```text
GET /documents
POST /documents
GET /documents/{id}
DELETE /documents/{id}
```

HTTP method:

```text
GET: 조회
POST: 생성
PUT: 전체 수정
PATCH: 일부 수정
DELETE: 삭제
```

---

## Q40. JSON과 XML 차이는 무엇인가요?

```text
JSON
- 가볍고 읽기 쉬움
- 웹 API에서 많이 사용
- JavaScript와 친화적

XML
- 태그 기반
- 스키마 표현 가능
- 레거시/공공/금융 시스템에서 사용되는 경우 있음
```

업스테이지 공고에 XML/JSON이 포함된 이유는 고객사 레거시 연동 가능성 때문이다.

---

## Q41. OAuth는 무엇인가요?

OAuth는 비밀번호를 직접 공유하지 않고 접근 권한을 위임하는 프로토콜이다.

```text
사용자
→ 인증 서버
→ access token 발급
→ API 서버 접근
```

주요 개념:

```text
Access Token
Refresh Token
Scope
Client ID
Client Secret
Authorization Server
Resource Server
```

면접 답변:

> OAuth는 사용자의 비밀번호를 직접 전달하지 않고, access token을 통해 제한된 권한을 위임하는 방식입니다. B2B 시스템 연동에서는 API 접근 권한과 scope를 안전하게 관리하기 위해 중요하다고 생각합니다.

---

## Q42. API Key와 OAuth 차이는 무엇인가요?

```text
API Key
- 단순한 식별/인증 키
- 구현 쉬움
- 권한 범위 세분화 어려움

OAuth
- 권한 위임 프로토콜
- scope 기반 권한 제어 가능
- token 만료/갱신 구조
```

---

# 9. Database

## Q43. RDBMS와 NoSQL 차이는 무엇인가요?

```text
RDBMS
- 정해진 스키마
- 테이블과 관계
- SQL 사용
- 트랜잭션 강함

NoSQL
- 유연한 스키마
- 문서/키-값/그래프/컬럼 기반
- 대규모 분산 처리에 유리
```

AI 문서 처리에서는 둘 다 쓸 수 있다.

```text
RDBMS
- 고객 정보
- 작업 상태
- 권한 정보
- billing 정보

NoSQL
- 문서 메타데이터
- 비정형 결과
- JSON 추출 결과
```

---

## Q44. Index는 왜 사용하나요?

Index는 검색 속도를 높이기 위한 자료구조다.

장점:

```text
조회 속도 향상
WHERE 조건 검색 최적화
ORDER BY/GROUP BY 성능 개선
```

단점:

```text
쓰기 성능 저하
저장공간 증가
인덱스 관리 비용
```

---

## Q45. 트랜잭션 ACID란 무엇인가요?

```text
Atomicity
- 모두 성공하거나 모두 실패

Consistency
- 데이터 정합성 유지

Isolation
- 동시에 실행되는 트랜잭션 간 격리

Durability
- 커밋된 데이터는 영구 보존
```

문서 처리 파이프라인에서는 작업 상태 업데이트에 중요하다.

```text
uploaded
processing
succeeded
failed
human_review
```

---

## Q46. 대용량 문서 처리에서 DB 설계 시 고려할 점은?

```text
문서 원본은 object storage에 저장
DB에는 metadata 저장
작업 상태 테이블 분리
고객사별 tenant 분리
인덱스 설계
처리 로그 저장
결과 JSON 저장 방식 결정
아카이빙 정책
```

면접 답변:

> 대용량 문서를 DB에 직접 저장하기보다는 S3 같은 object storage에 저장하고, DB에는 경로와 메타데이터, 처리 상태, 추출 결과를 저장하는 방식이 적절하다고 생각합니다.

---

# 10. OCR / Document Parse / Information Extract

## Q47. OCR과 Document Parse의 차이는 무엇인가요?

```text
OCR
- 이미지/PDF에서 글자 추출

Document Parse
- 텍스트뿐 아니라 문서 구조 인식
- 제목, 표, 문단, 다단 레이아웃, 체크박스 등 처리
```

면접 답변:

> OCR은 글자를 추출하는 기술이고, Document Parse는 문서의 레이아웃과 구조까지 인식해 RAG나 AI Agent가 사용할 수 있는 형태로 만드는 기술이라고 이해했습니다.

---

## Q48. Document Parse Enhanced가 필요한 이유는 무엇인가요?

복잡한 문서에는 단순 OCR로 처리하기 어려운 요소가 많다.

```text
줄이 없는 테이블
멀티페이지 테이블
차트
도표
체크박스
다단 레이아웃
스캔 품질이 낮은 문서
```

이 구조가 깨지면 RAG 검색과 Information Extract 품질도 떨어진다.

---

## Q49. Information Extract는 무엇인가요?

Information Extract는 문서에서 필요한 필드를 JSON Schema에 맞춰 추출하는 API다.

```text
계약서
→ 계약 시작일, 종료일, 금액, 당사자

청구서
→ 청구 금액, 납부일, 계좌번호

신청서
→ 이름, 주소, 체크박스 선택 여부
```

면접 답변:

> Document Parse가 문서를 읽고 구조화하는 단계라면, Information Extract는 그 문서에서 필요한 필드를 JSON Schema에 맞춰 추출해 업무 시스템에 연결할 수 있게 만드는 단계라고 이해했습니다.

---

## Q50. Information Extract 운영 시 중요한 점은?

```text
API latency
error rate
timeout
schema validation failure
필수 필드 누락률
타입 오류율
문서 유형별 실패율
사람 수정률
비용
```

면접 답변:

> Information Extract는 JSON을 반환하더라도 결과를 바로 DB에 넣으면 안 되고, 스키마 검증과 타입 정규화, 필수 필드 확인이 필요합니다. 또한 스키마 버전 관리가 중요하다고 생각합니다.

---

# 11. RAG

## Q51. RAG란 무엇인가요?

RAG는 Retrieval-Augmented Generation의 약자다.

```text
사용자 질문
→ 관련 문서 검색
→ 검색 결과를 LLM에 제공
→ 근거 기반 답변 생성
```

장점:

```text
최신/사내 문서 활용 가능
근거 기반 답변 가능
모델 재학습 없이 지식 확장 가능
```

---

## Q52. RAG 파이프라인은 어떻게 구성되나요?

```text
문서 수집
→ 전처리
→ chunking
→ embedding
→ vector DB 저장
→ query embedding
→ top-k retrieval
→ reranking
→ prompt 구성
→ LLM 답변
→ evidence 제공
```

---

## Q53. Chunking이 왜 중요한가요?

Chunk가 너무 작으면 문맥이 부족하고, 너무 크면 검색 정확도가 떨어지거나 불필요한 정보가 섞인다.

```text
작은 chunk
- 장점: 세밀한 검색
- 단점: 문맥 부족

큰 chunk
- 장점: 문맥 보존
- 단점: 노이즈 증가, 검색 정밀도 저하
```

네 논문에서도 chunk 크기 변화가 retrieval 지표는 유지하면서도 answer similarity를 크게 떨어뜨린 실험이 있었다. 이는 검색 결과가 겉으로 유지되어도 최종 응답 품질은 나빠질 수 있다는 점을 보여준다. 

면접 답변:

> Chunk 크기는 RAG 품질에 큰 영향을 줍니다. 너무 작으면 답변에 필요한 문맥이 부족하고, 너무 크면 검색 결과에 노이즈가 섞일 수 있습니다. 그래서 retrieval 지표뿐 아니라 최종 answer quality도 함께 봐야 한다고 생각합니다.

---

## Q54. Embedding이란 무엇인가요?

Embedding은 텍스트를 의미를 담은 벡터로 변환하는 것이다.

```text
"계약 종료일은 언제인가요?"
→ [0.12, -0.34, 0.91, ...]
```

비슷한 의미의 문장은 벡터 공간에서 가까운 위치에 놓인다.

---

## Q55. Vector DB는 왜 사용하나요?

Vector DB는 embedding 벡터를 저장하고 유사도 검색을 수행하기 위해 사용한다.

```text
FAISS
Milvus
Pinecone
Weaviate
OpenSearch Vector
pgvector
```

검색 방식:

```text
cosine similarity
dot product
euclidean distance
```

---

## Q56. Top-k란 무엇인가요?

Top-k는 검색 결과 중 유사도가 높은 상위 k개 문서를 가져오는 설정이다.

```text
top_k=3 → 상위 3개 문서
top_k=5 → 상위 5개 문서
```

top_k가 너무 작으면 필요한 문서를 놓칠 수 있고, 너무 크면 노이즈가 늘 수 있다.

---

## Q57. Reranker는 왜 사용하나요?

1차 vector search는 빠르지만 정확도가 부족할 수 있다.
Reranker는 검색된 후보 문서를 다시 정렬해 더 관련성 높은 문서를 상위에 배치한다.

```text
Vector Search
→ 후보 20개
→ Reranker
→ 최종 top 5개
```

---

## Q58. Recall@k는 무엇인가요?

Recall@k는 정답 문서가 상위 k개 검색 결과 안에 포함되었는지를 보는 지표다.

```text
정답 문서가 top-5 안에 있으면 성공
```

RAG 검색 품질 평가에 사용된다.

---

## Q59. nDCG@k는 무엇인가요?

nDCG는 검색 결과의 순위 품질을 평가하는 지표다.

정답 문서가 상위에 있을수록 높은 점수를 받는다.

```text
정답이 1등 → 더 높은 점수
정답이 5등 → 낮은 점수
```

---

## Q60. Answer Similarity는 무엇인가요?

Answer similarity는 생성된 답변과 기준 답변이 얼마나 유사한지 보는 지표다.

문자열 기반, embedding 기반, LLM judge 기반 등 여러 방식이 있다.

주의점:

```text
문자열 유사도는 의미적 정답성을 완전히 보장하지 않음
보조 지표로 사용해야 함
human evaluation이나 groundedness와 함께 보는 것이 좋음
```

네 논문에서도 answer similarity는 최종 정답성 판단 지표가 아니라 retrieval 지표만으로 잡기 어려운 generation 품질 변화의 보조 신호로 사용했다고 정리했다. 

---

## Q61. RAG 품질 회귀란 무엇인가요?

RAG 시스템에서 모델, 문서, chunk 전략, embedding 모델, reranker 설정 등이 바뀌면서 기존보다 답변 품질이 나빠지는 현상이다.

```text
chunk size 변경
embedding 모델 변경
top_k 변경
문서 추가/삭제
reranker 제거
LLM 버전 변경
prompt 변경
```

품질 회귀는 단순 장애보다 위험할 수 있다.

```text
서비스는 정상 응답
하지만 답변 품질이 나빠짐
사용자는 잘못된 답변을 받음
```

---

## Q62. RAG 품질 회귀를 어떻게 탐지하나요?

```text
고정 평가셋 구성
baseline 결과 저장
변경 후 자동 평가
Recall@k, nDCG@k, answer similarity 측정
기준 미달 시 배포 차단
```

면접 답변:

> RAG 품질 회귀는 일반 API 테스트로는 잡기 어렵기 때문에, 고정된 평가셋과 기준 결과를 두고 retrieval 지표와 generation 지표를 함께 비교해야 한다고 생각합니다. 기준 미달 시 CI/CD에서 배포를 차단하는 품질 게이트를 둘 수 있습니다.

---

# 12. LLM / Solar Pro / Agent

## Q63. LLM Gateway는 왜 필요한가요?

LLM Gateway는 애플리케이션과 LLM API 사이의 중간 계층이다.

역할:

```text
인증 관리
모델 라우팅
rate limit
retry
timeout
logging
token usage 측정
비용 추적
fallback 모델 설정
prompt version 관리
```

면접 답변:

> LLM Gateway를 두면 애플리케이션이 특정 모델 API에 직접 강하게 결합되지 않고, 모델 라우팅, 비용 관리, timeout, retry, 로깅을 중앙에서 관리할 수 있다고 생각합니다.

---

## Q64. LLM 운영에서 중요한 지표는 무엇인가요?

```text
request count
error rate
timeout
p95 latency
input tokens
output tokens
cost
rate limit
JSON format success rate
instruction following rate
human escalation rate
```

---

## Q65. 모델 버전을 바꿀 때 무엇을 확인해야 하나요?

```text
API 호환성
응답 형식
latency
token usage
비용
품질 회귀
RAG groundedness
JSON 출력 성공률
고객사 주요 시나리오
rollback 가능성
```

배포 전략:

```text
offline evaluation
shadow test
canary release
gradual rollout
rollback
```

---

## Q66. AI Agent는 일반 챗봇과 무엇이 다른가요?

```text
챗봇
- 질문에 답변

AI Agent
- 목표 이해
- 계획 수립
- 도구 호출
- 중간 결과 해석
- 오류 수정
- 최종 작업 완수
```

AI Agent 운영 지표:

```text
task completion rate
tool call success rate
tool call error rate
step failure rate
human escalation rate
latency per step
```

---

## Q67. Function Calling에서 문제가 생기는 경우는?

```text
잘못된 함수 선택
필수 argument 누락
argument type 오류
도구 결과 오해
중간 단계 context 손실
외부 API timeout
```

대응:

```text
함수 schema 명확화
argument validation
timeout/retry
tool result logging
step-by-step trace 저장
fallback/human review
```

---

# 13. 재색인 / 운영형 RAG

## Q68. Reindexing은 왜 필요한가요?

문서 코퍼스가 바뀌면 기존 embedding index가 최신 상태가 아니게 된다.

```text
문서 추가
문서 삭제
문서 수정
chunk 전략 변경
embedding 모델 변경
metadata 변경
```

이때 vector DB를 다시 색인해야 한다.

---

## Q69. Manual, Periodic, Condition 기반 재색인 차이는?

```text
Manual
- 사람이 필요할 때 직접 재색인
- 비용 낮을 수 있음
- 누락 위험 있음

Periodic
- 정해진 주기로 재색인
- 단순하고 예측 가능
- 불필요한 비용 발생 가능

Condition
- 변화율이나 품질 기준에 따라 재색인
- 비용과 품질 균형 가능
- 조건 설계 필요
```

네 논문에서는 manual, periodic, condition 정책을 비교했고, 조건 기반 정책이 제한된 실험 시나리오에서 가장 적은 재색인 횟수와 짧은 재색인 시간으로 품질 지표를 유지했다. 

면접 답변:

> 재색인은 문서 변화나 품질 저하가 있을 때 수행해야 합니다. 주기 기반은 단순하지만 불필요한 비용이 생길 수 있고, 수동 방식은 누락 위험이 있습니다. 조건 기반은 코퍼스 변화율이나 품질 게이트 실패 여부를 기준으로 재색인을 수행해 비용과 품질의 균형을 맞출 수 있다고 생각합니다.

---

## Q70. 재색인 비용에는 무엇이 포함되나요?

```text
문서 파싱 비용
chunk 생성 비용
embedding 생성 비용
vector DB write 비용
CPU/GPU 사용량
처리 시간
서비스 영향
스토리지 비용
```

---

# 14. 장애 대응 시나리오

## Q71. OCR API가 갑자기 느려지면 어떻게 대응하나요?

확인 순서:

```text
요청량 증가 여부
p95 latency 증가 여부
Pod CPU/Memory
Queue length
문서 크기 증가 여부
특정 문서 유형 문제
외부 API timeout
DB/Storage latency
최근 배포 여부
```

대응:

```text
worker scale-out
queue 기반 비동기 처리
문서 크기 제한
timeout 조정
retry/backoff
문제 문서 샘플 격리
```

---

## Q72. RAG 답변 품질이 갑자기 나빠지면 어떻게 확인하나요?

확인 순서:

```text
최근 문서 변경
reindex 여부
embedding 모델 변경
chunk 설정 변경
top_k/reranker 변경
LLM 모델 변경
prompt 변경
검색 결과 확인
answer groundedness 확인
```

면접 답변:

> RAG 품질 저하는 검색 문제인지 생성 문제인지 분리해서 봐야 합니다. 먼저 Top-K 검색 결과가 적절한지 확인하고, 그다음 LLM이 검색 결과를 근거로 답했는지 봐야 합니다. 최근 변경된 chunk, embedding, reranker, prompt, 모델 버전도 함께 확인합니다.

---

## Q73. LLM API 비용이 갑자기 증가하면 어떻게 확인하나요?

```text
요청 수 증가
input token 증가
output token 증가
retry 증가
긴 문서 입력 증가
특정 고객사 사용량 증가
prompt에 불필요한 context 포함
RAG top_k 과도하게 큼
```

대응:

```text
max_tokens 제한
prompt 압축
top_k 조정
캐싱
고객사별 quota
비용 알림
retry 제한
```

---

## Q74. 고객사가 “결과가 틀렸다”고 하면 어떻게 대응하나요?

확인 순서:

```text
입력 문서 원본 확인
Document Parse 결과 확인
Information Extract 결과 확인
RAG 검색 결과 확인
LLM 답변 확인
근거 문서 확인
로그 trace 확인
동일 입력 재현
```

면접 답변:

> 먼저 어느 단계에서 틀렸는지 분리해야 합니다. 문서를 잘못 읽은 문제인지, 필요한 필드를 잘못 추출한 문제인지, RAG가 잘못 검색한 문제인지, LLM이 근거와 다르게 답한 문제인지 확인하고, 각 단계의 중간 결과와 로그를 확인하겠습니다.

---

# 15. B2B 고객사 연동

## Q75. 고객사 시스템과 연동할 때 확인해야 할 것은?

```text
배포 환경
클라우드/온프레미스 여부
망분리 여부
방화벽
인증 방식
API 방식
파일 배치 방식
JSON/XML 포맷
데이터 암호화
로그 마스킹
SLA
장애 대응 프로세스
```

---

## Q76. 레거시 시스템과 연동할 때 어려운 점은?

```text
문서화 부족
XML/SOAP 기반 API
인증 방식 오래됨
에러 코드 불명확
네트워크 제한
배치 파일 기반 연동
운영 담당자 의존성
변경 어려움
```

대응:

```text
인터페이스 명세 정리
adapter layer 구성
입출력 validation
로그 강화
재처리 구조
고객사 담당자와 장애 대응 플로우 합의
```

---

# 16. 본인 프로젝트 기반 심화 질문

## Q77. 본인 RAG MLOps 프로젝트의 핵심은 무엇인가요?

답변:

> 운영형 RAG 시스템에서 품질 회귀를 자동 탐지하고, 이를 CI/CD 배포 통제와 재색인 전략에 연결하는 MLOps 파이프라인을 설계한 것입니다. 단순히 RAG를 만드는 것이 아니라, 검색 품질과 답변 품질이 기준 이하로 떨어졌을 때 배포를 차단하고, 코퍼스 변화에 따라 재색인을 판단하는 운영 구조를 실험했습니다.

---

## Q78. 왜 Recall/nDCG만으로 부족하다고 생각했나요?

답변:

> Recall과 nDCG는 검색 결과에 정답 문서가 포함되었는지와 순위가 적절한지를 보여줍니다. 하지만 검색 결과가 좋아 보여도 chunk 크기나 문맥 구성 문제로 최종 답변 품질이 떨어질 수 있습니다. 그래서 answer similarity 같은 generation 품질 보조 지표를 함께 사용했습니다.

---

## Q79. answer similarity의 한계는 무엇인가요?

답변:

> 문자열 기반 answer similarity는 의미적으로 맞는 답변을 낮게 평가하거나, 표현만 비슷한 틀린 답변을 높게 평가할 수 있습니다. 그래서 최종 정답성 판단 지표라기보다 retrieval 지표만으로 잡기 어려운 generation 품질 변화의 보조 신호로 보는 것이 적절하다고 생각합니다. 향후에는 semantic similarity, LLM judge, human evaluation, task success rate를 함께 보는 것이 좋다고 생각합니다.

---

## Q80. Jenkins와 품질 게이트를 어떻게 연결했나요?

답변:

> 평가 스크립트가 Recall, nDCG, answer similarity, latency를 계산하고, 기준값을 만족하는지 판단하도록 했습니다. Jenkins 파이프라인에서는 이 결과를 조건 분기로 사용해서 gate가 통과되면 Docker 이미지 빌드와 배포 단계로 진행하고, 실패하면 이후 배포 단계를 skipped 처리하는 구조로 연결했습니다.

---

## Q81. 이 프로젝트를 업스테이지 AI DevOps와 어떻게 연결할 수 있나요?

답변:

> 업스테이지의 Document Parse, Information Extract, RAG, LLM 기반 솔루션도 운영 중 모델이나 문서, 파라미터가 바뀌면 품질 회귀가 생길 수 있다고 생각합니다. 제 프로젝트의 품질 게이트 구조는 이런 변경이 실제 고객사 배포 전에 품질 기준을 만족하는지 검증하고, 기준 미달 시 배포를 막는 방식으로 연결될 수 있습니다.

---

# 17. 마지막 핵심 암기 문장

## AI DevOps 정의

```text
AI DevOps는 모델을 단순히 배포하는 일이 아니라,
Document Parse, Information Extract, RAG, LLM 같은 AI 컴포넌트가
고객사 환경에서 안정적으로 연결되고 운영되도록
배포 자동화, 모니터링, 장애 대응, 품질 검증 체계를 만드는 역할이라고 이해했습니다.
```

## Kubernetes 중요성

```text
B2B AI 서비스에서는 고객사마다 클라우드, 온프레미스, 망분리 등 배포 조건이 다를 수 있습니다.
OCR, RAG, LLM Gateway, Worker 같은 컴포넌트를 컨테이너 기반으로 안정적으로 배포하고 확장하려면 Kubernetes 기반 운영 감각이 중요하다고 생각합니다.
```

## RAG 품질 게이트

```text
RAG 시스템은 API가 정상 응답하더라도 검색 품질이나 답변 품질이 떨어질 수 있습니다.
그래서 Recall, nDCG 같은 retrieval 지표와 answer similarity, groundedness 같은 generation 지표를 함께 보고,
기준 미달 시 CI/CD에서 배포를 차단하는 품질 게이트가 필요하다고 생각합니다.
```

## 모니터링 관점

```text
AI 서비스에서는 latency, error rate, CPU, memory뿐 아니라
OCR 파싱 실패율, Information Extract 스키마 검증 실패율,
RAG 검색 hit rate, LLM token usage, agent task completion rate 같은 AI 특화 지표를 함께 봐야 합니다.
```

## 부족한 부분 방어

```text
Kubernetes는 아직 실무 운영 경험은 없지만,
Pod, Deployment, Service, Ingress, HPA, Helm 등 기본 리소스를 실습했고,
AI DevOps 업무에서 왜 중요한지 이해하고 있습니다.
실제 업무에서는 로그와 지표를 기반으로 원인을 좁혀가며 빠르게 배우겠습니다.
```

---

# 최종 정리

업스테이지 AI DevOps 심화 기술면접의 핵심은 다음이다.

```text
1. AI 제품을 실제 운영 시스템으로 이해하는가
2. Docker/Kubernetes 기반 배포 흐름을 아는가
3. CI/CD와 품질 게이트를 연결해 설명할 수 있는가
4. Prometheus/Grafana로 무엇을 볼지 아는가
5. RAG/OCR/LLM 파이프라인에서 장애 지점을 분리할 수 있는가
6. B2B 고객사 환경에서 배포·연동·유지보수 관점을 가지고 있는가
7. 본인 프로젝트를 업스테이지 업무와 연결할 수 있는가
```

한 줄로 요약하면,

```text
업스테이지 AI DevOps는 AI 모델을 잘 아는 사람보다,
AI 제품이 고객사 환경에서 안정적으로 배포되고 관측되고 개선되도록
운영 구조를 설계할 수 있는 사람을 원할 가능성이 높다.
