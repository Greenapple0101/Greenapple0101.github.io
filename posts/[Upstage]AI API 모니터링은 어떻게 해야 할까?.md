# AI API 모니터링은 어떻게 해야 할까?

AI DevOps 관점에서 중요한 질문이 있다.

```text
Solar LLM API를 붙였습니다.
OCR API를 붙였습니다.
Embedding API를 붙였습니다.

그럼 이제 끝인가?
```

아니다.

API를 붙이는 것보다 더 중요한 건 **운영 중에 이 API들이 잘 돌고 있는지 보는 것**이다.

서비스는 로컬에서 한 번 성공했다고 끝나는 게 아니다.

실제 사용자가 들어오면 요청이 몰리고, 외부 API가 느려지고, 토큰 비용이 늘고, timeout이 나고, 특정 문서에서 OCR이 실패할 수 있다.

그래서 DevOps는 이렇게 질문해야 한다.

```text
지금 서비스가 살아 있는가?
사용자가 체감하기에 빠른가?
어느 API에서 실패하고 있는가?
비용이 갑자기 늘고 있지는 않은가?
재시도가 장애를 더 키우고 있지는 않은가?
답변 품질이 떨어지고 있지는 않은가?
```

이걸 확인하는 과정이 모니터링이다.

---

# 먼저 전체 구조를 보자

예를 들어 업스테이지 API를 활용한 RAG 서비스를 만든다고 해보자.

전체 흐름은 대충 이렇다.

```text
사용자 질문
  ↓
내 백엔드 서버
  ↓
질문 Embedding API 호출
  ↓
Vector DB 검색
  ↓
검색된 context 구성
  ↓
Solar LLM API 호출
  ↓
답변 반환
```

문서 업로드까지 포함하면 앞단에 이런 흐름도 있다.

```text
문서 업로드
  ↓
OCR / Document Parse API 호출
  ↓
텍스트 추출
  ↓
청킹
  ↓
Embedding API 호출
  ↓
Vector DB 저장
```

여기서 모니터링해야 할 지점은 하나가 아니다.

```text
내 백엔드 서버
OCR / Parse API
Embedding API
Vector DB
Solar LLM API
전체 RAG 응답 시간
토큰 사용량
에러율
재시도 횟수
```

즉, “서버 CPU 몇 퍼센트냐”만 보면 부족하다.

AI API를 붙인 서비스에서는 **각 API 호출 구간별로 쪼개서 봐야 한다.**

---

# 모니터링은 크게 세 가지로 나눠서 보면 된다

나는 AI API 모니터링을 이렇게 나눠서 보면 이해하기 쉽다고 생각한다.

```text
1. 시스템 모니터링
2. API 호출 모니터링
3. AI 품질 모니터링
```

각각 보는 게 다르다.

```text
시스템 모니터링
→ 서버, Pod, CPU, Memory, Disk, Network

API 호출 모니터링
→ latency, error rate, timeout, retry, token usage

AI 품질 모니터링
→ 검색 품질, 답변 품질, hallucination, groundedness
```

일반 DevOps에서는 1번과 2번을 많이 본다.

AI DevOps에서는 여기에 3번이 추가된다.

왜냐하면 AI 서비스는 서버가 정상이어도 답변 품질이 망가질 수 있기 때문이다.

---

# 1. 시스템 모니터링

가장 기본은 시스템 상태다.

Kubernetes 위에서 서비스가 돈다면 이런 것들을 본다.

```text
Pod가 살아 있는가?
Pod가 재시작되고 있지는 않은가?
CPU 사용량이 높은가?
Memory 사용량이 높은가?
OOMKilled가 발생했는가?
Disk가 꽉 차고 있지는 않은가?
네트워크 에러가 있는가?
```

예를 들어 RAG 백엔드 Pod가 계속 재시작된다면 API 품질 이전에 서버 안정성 문제다.

```text
Pod Restart Count 증가
→ 애플리케이션 crash 가능성

Memory 사용량 급증
→ 대용량 PDF 처리 중 메모리 부족 가능성

CPU 사용량 급증
→ 청킹/전처리/검색 부하 가능성

Disk 사용량 증가
→ 업로드 파일, 로그, 임베딩 캐시 누적 가능성
```

이 부분은 Prometheus와 Grafana로 많이 본다.

구조는 이런 식이다.

```text
애플리케이션 / Node / Kubernetes
        ↓
Prometheus가 metrics 수집
        ↓
Grafana에서 dashboard 시각화
        ↓
Alertmanager로 알림
```

---

# 2. API 호출 모니터링

AI 서비스에서 진짜 중요한 건 API 호출 구간이다.

업스테이지 API를 쓴다고 하면 이런 API들이 있을 수 있다.

```text
Document Parse API
OCR API
Embedding API
Solar LLM API
Groundedness Checker API
```

각 API마다 최소한 이 지표를 봐야 한다.

```text
요청 수
성공 수
실패 수
error rate
latency
p95 latency
timeout 수
retry 수
응답 크기
token usage
```

예를 들어 Solar LLM API 호출을 모니터링한다면 이런 식이다.

```text
solar_requests_total
solar_requests_success_total
solar_requests_error_total
solar_latency_seconds
solar_timeout_total
solar_retry_total
solar_prompt_tokens_total
solar_completion_tokens_total
solar_total_tokens_total
```

Embedding API라면 이런 식으로 볼 수 있다.

```text
embedding_requests_total
embedding_latency_seconds
embedding_error_total
embedding_vector_count_total
embedding_input_text_length
```

OCR / Document Parse라면 이런 지표가 중요하다.

```text
parse_requests_total
parse_latency_seconds
parse_error_total
parse_file_size_bytes
parse_page_count
parse_timeout_total
parse_success_total
```

즉, API마다 특성에 맞는 지표를 따로 둬야 한다.

---

# latency는 단계별로 쪼개야 한다

사용자가 “답변이 느려요”라고 했을 때 전체 응답 시간만 보면 원인을 모른다.

RAG 응답 하나를 단계별로 쪼개야 한다.

```text
전체 응답 시간
= 질문 전처리 시간
+ Embedding API 호출 시간
+ Vector DB 검색 시간
+ Prompt 구성 시간
+ Solar LLM API 호출 시간
+ 후처리 시간
```

그래서 이런 식으로 latency를 나눠서 봐야 한다.

```text
rag_total_latency
embedding_latency
vector_search_latency
prompt_build_latency
solar_llm_latency
postprocess_latency
```

예를 들어 전체 응답 시간이 8초라고 하자.

```text
embedding_latency: 0.3초
vector_search_latency: 0.1초
prompt_build_latency: 0.1초
solar_llm_latency: 7.2초
postprocess_latency: 0.3초
```

이러면 병목은 Solar LLM 호출 구간이다.

반대로:

```text
embedding_latency: 0.2초
vector_search_latency: 5.5초
solar_llm_latency: 1.8초
```

이러면 Vector DB 검색이 문제다.

그래서 모니터링은 “전체가 느리다”에서 끝나면 안 된다.

**어느 단계가 느린지 보여줘야 한다.**

---

# p95 latency를 봐야 하는 이유

평균 latency만 보면 위험하다.

예를 들어 평균 응답 시간이 2초라고 해보자.

겉으로는 괜찮아 보인다.

그런데 실제 요청 분포가 이럴 수 있다.

```text
대부분 요청: 1초
일부 요청: 15초
평균: 2초
```

평균만 보면 문제가 숨어버린다.

그래서 p95를 본다.

```text
p95 latency = 전체 요청 중 95%가 이 시간 안에 끝났다는 값
```

예를 들어:

```text
avg latency: 2초
p95 latency: 12초
```

이러면 평균은 괜찮지만, 일부 사용자는 12초 가까이 기다린다는 뜻이다.

AI API는 특히 p95가 중요하다.

왜냐하면 LLM 답변 길이, 문서 길이, context 크기, 외부 API 상태에 따라 일부 요청이 유난히 느려질 수 있기 때문이다.

면접에서는 이렇게 말하면 좋다.

```text
평균 latency만 보면 tail latency가 가려질 수 있기 때문에 p95 latency를 같이 봐야 한다고 생각합니다.
특히 LLM API는 입력 토큰과 출력 토큰에 따라 응답 시간이 달라질 수 있어서 p95 기준으로 사용자 체감 성능을 관리하는 것이 중요합니다.
```

---

# error rate는 API별로 봐야 한다

에러율도 전체만 보면 안 된다.

전체 error rate가 3%라고 해도, 어느 API에서 나는지 모르면 대응이 어렵다.

```text
전체 error rate: 3%
```

이걸 쪼개보면 다를 수 있다.

```text
OCR API error rate: 12%
Embedding API error rate: 0.5%
Solar LLM API error rate: 1%
Vector DB error rate: 0%
```

그러면 문제는 OCR 쪽이다.

OCR API 에러가 높다면 이런 원인을 볼 수 있다.

```text
지원하지 않는 파일 형식
파일 크기 초과
스캔 품질 문제
페이지 수 과다
timeout
외부 API 장애
```

Solar LLM API 에러가 높다면 이런 원인을 볼 수 있다.

```text
API Key 문제
rate limit 초과
요청 body 형식 오류
토큰 길이 초과
timeout
외부 API 장애
```

Embedding API 에러가 높다면 이런 원인을 볼 수 있다.

```text
입력 텍스트가 너무 김
batch 크기 과도함
API limit 초과
네트워크 오류
```

그래서 error rate는 API별, status code별로 나눠야 한다.

```text
error_rate_by_api
error_rate_by_status_code
error_rate_by_model
error_rate_by_endpoint
```

---

# timeout은 반드시 따로 세야 한다

timeout은 그냥 실패 중 하나로 묻히면 안 된다.

왜냐하면 timeout은 “느려서 실패한 것”이기 때문이다.

```text
400 Bad Request
→ 요청 형식 문제

401 Unauthorized
→ 인증 문제

429 Too Many Requests
→ 요청 제한 문제

500 Internal Server Error
→ 서버 문제

timeout
→ 응답 지연 문제
```

timeout이 늘면 latency 문제와 연결된다.

예를 들어 Solar LLM API timeout이 증가했다.

```text
solar_timeout_total 증가
solar_p95_latency 증가
```

그러면 이런 원인을 의심할 수 있다.

```text
프롬프트가 너무 길어짐
검색 context가 너무 많이 들어감
출력 max_tokens가 너무 큼
외부 API 응답 지연
동시 요청 증가
네트워크 문제
```

RAG에서는 특히 context 길이가 중요하다.

```text
top_k를 10개로 늘림
chunk 크기가 커짐
대화 히스토리를 전부 넣음
```

이렇게 되면 prompt token이 늘고, Solar 응답 시간이 늘고, timeout이 증가할 수 있다.

---

# retry는 성공률을 높이지만 조심해야 한다

retry는 실패한 요청을 다시 시도하는 것이다.

일시적인 장애에는 도움이 된다.

```text
1번째 요청 → timeout
2번째 요청 → 성공
```

하지만 retry를 무조건 많이 하면 오히려 장애를 키울 수 있다.

```text
외부 API가 느려짐
→ 요청 실패
→ 모든 서버가 retry
→ 호출량 증가
→ 외부 API 더 느려짐
→ timeout 더 증가
```

이런 상황을 retry storm이라고 볼 수 있다.

그래서 retry도 모니터링해야 한다.

```text
retry_count
retry_success_count
retry_failure_count
retry_by_api
```

그리고 정책이 필요하다.

```text
최대 재시도 횟수 제한
exponential backoff 적용
429 에러는 Retry-After 확인
400/401/403은 재시도하지 않음
timeout/502/503/504는 제한적으로 재시도
```

면접에서는 이렇게 말하면 좋다.

```text
일시적인 5xx나 timeout은 제한적으로 retry하되, 400번대 요청 오류나 인증 오류는 재시도하지 않도록 분리해야 한다고 생각합니다.
또한 retry 횟수 자체를 metric으로 남겨서 retry가 장애를 완화하는지, 오히려 외부 API 부하를 키우는지 확인해야 합니다.
```

---

# token usage는 LLM 모니터링의 핵심이다

LLM API에서는 token usage를 꼭 봐야 한다.

일반 API에는 없는 지표다.

```text
prompt_tokens
completion_tokens
total_tokens
```

뜻은 이렇다.

```text
prompt_tokens
→ 모델에 넣은 입력 토큰 수

completion_tokens
→ 모델이 생성한 답변 토큰 수

total_tokens
→ 전체 사용 토큰 수
```

이걸 왜 보냐면 비용과 속도 때문이다.

```text
토큰 증가
→ 비용 증가
→ 응답 시간 증가 가능성
```

RAG에서는 prompt token이 쉽게 커진다.

왜냐하면 사용자의 질문만 넣는 게 아니라, 검색된 context도 넣기 때문이다.

```text
사용자 질문
+ 시스템 프롬프트
+ 검색된 chunk 5개
+ 이전 대화 히스토리
+ 출력 형식 안내
```

이게 다 prompt token이다.

그래서 token usage를 보면 이런 문제를 잡을 수 있다.

```text
검색 context를 너무 많이 넣고 있는가?
chunk 크기가 너무 큰가?
대화 히스토리를 너무 오래 들고 가는가?
프롬프트 템플릿이 불필요하게 긴가?
사용자별 비용이 비정상적으로 높은가?
```

운영 지표로는 이런 것들을 둘 수 있다.

```text
llm_prompt_tokens_total
llm_completion_tokens_total
llm_total_tokens_total
llm_tokens_by_user
llm_tokens_by_endpoint
llm_tokens_by_model
average_tokens_per_request
```

---

# 비용 모니터링도 필요하다

LLM API는 비용이 중요하다.

트래픽이 늘면 비용도 늘 수 있다.

하지만 트래픽이 그대로인데도 비용이 늘 수 있다.

예를 들어:

```text
요청 수는 그대로
그런데 total_tokens가 3배 증가
```

이러면 원인은 요청 수가 아니라 프롬프트 길이다.

가능한 원인은 이런 것들이다.

```text
검색 chunk 개수 증가
chunk size 증가
대화 히스토리 누적
프롬프트 템플릿 변경
max_tokens 증가
비정상 사용자 요청
```

그래서 비용은 요청 수만 보면 안 된다.

```text
요청 수
토큰 수
사용자별 토큰 수
endpoint별 토큰 수
모델별 토큰 수
```

이렇게 같이 봐야 한다.

---

# AI 품질 모니터링도 필요하다

AI 서비스는 서버가 멀쩡해도 답변이 틀릴 수 있다.

그래서 품질 지표도 봐야 한다.

RAG에서는 이런 지표가 중요하다.

```text
검색 품질
- recall@k
- nDCG
- hit rate

답변 품질
- answer similarity
- groundedness
- hallucination rate
- user feedback

운영 품질
- latency
- error rate
- timeout
- token usage
```

예를 들어 배포 후 latency는 그대로인데 답변 품질이 떨어질 수 있다.

```text
청킹 전략 변경
임베딩 모델 변경
검색 top_k 변경
reranker 설정 변경
프롬프트 변경
```

이런 변화는 서버 지표만 보면 모른다.

그래서 RAG에서는 배포 전에 evaluation을 돌리고, 운영 중에도 샘플링해서 품질을 봐야 한다.

```text
배포 전
→ offline evaluation
→ recall@k, nDCG, answer similarity 확인
→ gate 통과 시 배포

배포 후
→ 사용자 질문 샘플링
→ 검색 결과와 답변 품질 확인
→ feedback 수집
```

이 부분이 MLOps와 DevOps가 만나는 지점이다.

---

# Prometheus로 어떻게 수집할까?

FastAPI 서버를 예로 들면 `/metrics` endpoint를 열어 Prometheus가 가져가게 할 수 있다.

구조는 이렇게 된다.

```text
FastAPI RAG Server
  ↓ /metrics
Prometheus
  ↓
Grafana
  ↓
Alertmanager
```

애플리케이션 안에서는 이런 metric을 기록한다.

```text
요청이 들어올 때 request_count 증가
API 호출 시작 시간 기록
API 응답 오면 latency 기록
에러 발생 시 error_count 증가
timeout 발생 시 timeout_count 증가
retry할 때 retry_count 증가
LLM 응답 usage에서 token 수 기록
```

예를 들어 개념적으로는 이런 식이다.

```python
start = time.time()

try:
    response = call_solar_api(...)
    latency = time.time() - start

    solar_latency.observe(latency)
    solar_success_total.inc()

    usage = response.usage
    solar_prompt_tokens.inc(usage.prompt_tokens)
    solar_completion_tokens.inc(usage.completion_tokens)
    solar_total_tokens.inc(usage.total_tokens)

except TimeoutError:
    solar_timeout_total.inc()
    solar_error_total.labels(type="timeout").inc()

except Exception as e:
    solar_error_total.labels(type="unknown").inc()
```

핵심은 “API 호출 전후로 시간을 재고, 성공/실패/토큰을 기록한다”는 것이다.

---

# Grafana 대시보드는 어떻게 구성할까?

대시보드는 너무 복잡하면 안 된다.

면접에서 말할 때는 이런 식으로 구성한다고 하면 좋다.

```text
1. 전체 서비스 상태
2. API별 latency
3. API별 error rate
4. timeout / retry
5. token usage / cost
6. RAG 품질 지표
```

예를 들면:

```text
[Overview]
- 전체 요청 수
- 전체 성공률
- 전체 error rate
- 전체 p95 latency

[API Latency]
- OCR p95 latency
- Parse p95 latency
- Embedding p95 latency
- Vector Search p95 latency
- Solar LLM p95 latency

[Error]
- API별 error rate
- status code별 에러
- timeout 수
- retry 수

[LLM Usage]
- prompt tokens
- completion tokens
- total tokens
- endpoint별 token usage
- 사용자별 token usage

[RAG Quality]
- recall@k
- nDCG
- answer similarity
- groundedness score
```

이렇게 나누면 운영자가 어디가 문제인지 빠르게 볼 수 있다.

---

# Alert는 어떻게 걸까?

모니터링은 보는 것에서 끝나면 안 된다.

문제가 생기면 알림이 와야 한다.

예를 들어 이런 alert rule을 만들 수 있다.

```text
5분 동안 error rate 5% 초과
→ 알림

p95 latency 10초 초과
→ 알림

timeout 수 급증
→ 알림

retry 수 급증
→ 알림

429 rate limit 에러 증가
→ 알림

token usage가 평소 대비 2배 이상 증가
→ 알림

Pod restart 증가
→ 알림

Vector DB 검색 실패 증가
→ 알림
```

중요한 건 알림을 너무 많이 만들면 안 된다는 것이다.

알림이 너무 많으면 사람은 안 보게 된다.

그래서 진짜 장애로 이어질 수 있는 지표부터 잡는 게 좋다.

```text
사용자 영향 있음
비용 폭증 가능성 있음
장애 확산 가능성 있음
보안 위험 있음
```

이 기준으로 alert를 잡아야 한다.

---

# 로그는 어떻게 남겨야 할까?

메트릭은 숫자다.

로그는 원인을 찾기 위한 기록이다.

AI API 호출 로그에는 이런 정보가 있으면 좋다.

```text
request_id
user_id 또는 tenant_id
endpoint
model
latency
status
error_code
retry_count
prompt_tokens
completion_tokens
total_tokens
top_k
chunk_count
```

예를 들어 이런 식이다.

```json
{
  "request_id": "req_123",
  "endpoint": "/rag/query",
  "model": "solar-pro3",
  "latency_ms": 4200,
  "status": "success",
  "retry_count": 0,
  "prompt_tokens": 1800,
  "completion_tokens": 350,
  "total_tokens": 2150,
  "top_k": 5,
  "chunk_count": 5
}
```

그런데 주의할 점이 있다.

프롬프트 원문과 문서 원문을 그대로 로그에 남기면 위험하다.

왜냐하면 개인정보나 회사 기밀이 들어갈 수 있기 때문이다.

```text
주민등록번호
계좌번호
계약서 내용
고객 이름
주소
전화번호
내부 문서
```

그래서 로그에는 원문 대신 필요한 메타데이터만 남기는 게 안전하다.

```text
나쁜 로그
→ prompt 전체 저장

좋은 로그
→ prompt 길이, token 수, request_id, error code 저장
```

필요하다면 민감정보 마스킹을 해야 한다.

---

# Tracing도 있으면 좋다

RAG 요청 하나는 여러 단계를 거친다.

```text
사용자 요청
→ embedding
→ vector search
→ solar llm
→ groundedness
→ response
```

이때 request_id나 trace_id가 없으면 로그를 따라가기 어렵다.

그래서 tracing을 붙이면 좋다.

```text
trace_id: abc123

span 1: /rag/query
span 2: embedding_api_call
span 3: vector_search
span 4: solar_llm_call
span 5: response_build
```

이렇게 하면 한 요청이 어디서 오래 걸렸는지 볼 수 있다.

예를 들어:

```text
embedding: 200ms
vector_search: 150ms
solar_llm: 7200ms
response_build: 50ms
```

이러면 Solar LLM 호출이 병목이다.

Tracing은 특히 MSA나 외부 API가 많은 구조에서 유용하다.

---

# 모니터링 시나리오 예시

## 상황 1. 답변이 느려졌다

확인 순서:

```text
1. 전체 p95 latency 확인
2. 단계별 latency 확인
3. Solar LLM latency 확인
4. token usage 확인
5. context chunk 개수 확인
6. 최근 프롬프트 변경 확인
```

가능한 원인:

```text
검색 chunk를 너무 많이 넣음
프롬프트가 길어짐
출력 max_tokens가 큼
Solar API 응답 지연
retry로 인한 지연 증가
```

해결 방향:

```text
top_k 조정
chunk 크기 조정
prompt 압축
max_tokens 제한
timeout/retry 정책 조정
```

---

## 상황 2. 에러율이 올라갔다

확인 순서:

```text
1. API별 error rate 확인
2. status code별 분리
3. timeout인지 4xx인지 5xx인지 확인
4. 최근 배포 확인
5. API Key / rate limit 확인
```

가능한 원인:

```text
요청 형식 변경
API Key 만료
rate limit 초과
외부 API 장애
네트워크 문제
토큰 길이 초과
```

해결 방향:

```text
요청 body 검증
API Key 확인
rate limit 대응
retry/backoff 적용
fallback 응답 제공
```

---

## 상황 3. 비용이 갑자기 늘었다

확인 순서:

```text
1. 요청 수 증가 여부 확인
2. total token 증가 여부 확인
3. endpoint별 token usage 확인
4. 사용자별 token usage 확인
5. prompt template 변경 확인
```

가능한 원인:

```text
RAG context 과다
대화 히스토리 과다
max_tokens 증가
비정상 사용자 요청
batch 작업 폭주
```

해결 방향:

```text
사용자별 rate limit
token budget 설정
context 압축
top_k 제한
max_tokens 제한
비정상 요청 차단
```

---

# 면접에서는 이렇게 말하면 좋다

AI API를 운영한다면 단순히 서버가 살아 있는지만 보는 것이 아니라, 각 API 호출 구간을 나누어 모니터링해야 한다고 생각합니다. 예를 들어 RAG 서비스라면 OCR 또는 Document Parse, Embedding, Vector Search, Solar LLM 호출 구간의 latency와 error rate를 각각 수집하고, 전체 응답 시간뿐 아니라 p95 latency를 통해 사용자 체감 성능을 확인해야 합니다.

LLM API의 경우 token usage도 중요한 지표입니다. prompt token과 completion token은 비용과 응답 시간에 영향을 줄 수 있기 때문에 endpoint별, 사용자별, 모델별로 집계해야 합니다. 또한 timeout과 retry 횟수를 별도로 모니터링해서 일시적 장애를 복구하고 있는지, 아니면 retry가 오히려 장애를 키우고 있는지 확인해야 한다고 생각합니다.

구현 관점에서는 애플리케이션에서 Prometheus metric을 노출하고, Grafana 대시보드에서 API별 latency, p95, error rate, timeout, retry, token usage를 시각화하겠습니다. 장애 조건은 Alertmanager로 알림을 걸고, 로그에는 request_id, model, latency, status, error_code, token usage 같은 메타데이터를 남기되, 프롬프트 원문이나 개인정보는 그대로 남기지 않도록 마스킹하겠습니다.

---

# 한 문장으로 정리하면

AI API 모니터링은 **서버가 켜져 있는지 보는 것이 아니라, 사용자가 안정적으로 답변을 받고 있는지 확인하는 것**이다.

그래서 봐야 할 것은 이것이다.

```text
시스템 상태
→ Pod, CPU, Memory, Disk, Restart

API 상태
→ latency, p95, error rate, timeout, retry

LLM 사용량
→ prompt_tokens, completion_tokens, total_tokens, cost

RAG 품질
→ recall@k, nDCG, answer similarity, groundedness

보안/로그
→ request_id, error_code, 메타데이터, 민감정보 마스킹
```

결국 DevOps 관점에서 중요한 건 하나다.

```text
문제가 생겼을 때
어느 단계에서
왜 느려졌고
왜 실패했고
비용이 왜 늘었고
사용자에게 어떤 영향을 줬는지
빠르게 찾을 수 있어야 한다
```

그걸 가능하게 만드는 게 모니터링이다.
