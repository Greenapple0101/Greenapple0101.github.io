---
title: "[Upstage] Prometheus, Loki, Grafana로 이해하는 모니터링과 관측 가능성"
source: ""
published: "2026-05-30T12:00:00.000Z"
---

## 1. 개요

서비스를 운영할 때 가장 중요한 질문은 단순히 “서버가 켜져 있는가?”가 아니다.

운영 환경에서는 다음 질문에 답할 수 있어야 한다.

```text
- API가 정상적으로 응답하고 있는가?
- 응답 시간이 평소보다 느려지지 않았는가?
- 에러율이 증가하지 않았는가?
- 특정 컨테이너가 CPU나 메모리를 과도하게 사용하고 있지 않은가?
- 디스크가 부족해지고 있지는 않은가?
- 장애가 발생했을 때 어떤 로그가 남았는가?
- 장애를 사람이 보기 전에 알림으로 받을 수 있는가?
````

이 질문에 답하기 위해 사용하는 대표적인 도구가 Prometheus, Loki, Grafana이다.

```text
Prometheus
→ 수치형 메트릭 수집 및 저장

Loki
→ 로그 수집 및 검색

Grafana
→ 메트릭과 로그 시각화, 대시보드, 알림
```

세 도구를 함께 사용하면 서비스의 상태를 수치와 로그 양쪽에서 관측할 수 있다.

---

## 2. 모니터링과 관측 가능성

모니터링은 시스템이 정상인지 확인하는 활동이다.

관측 가능성은 시스템 내부에서 무슨 일이 일어나고 있는지 외부 출력만으로 추론할 수 있는 능력이다.

운영 환경에서 자주 말하는 관측 가능성의 세 가지 축은 다음과 같다.

```text
Metrics
- 수치형 지표
- CPU 사용률, 메모리 사용량, 요청 수, 응답 시간, 에러율

Logs
- 이벤트 기록
- 애플리케이션 로그, 시스템 로그, 컨테이너 로그, 에러 스택트레이스

Traces
- 요청 흐름 추적
- 하나의 요청이 여러 서비스와 DB, 외부 API를 거치는 과정
```

Prometheus는 metrics에 강하고, Loki는 logs에 강하다. Grafana는 이 둘을 시각화하고 알림까지 연결하는 역할을 한다.

---

## 3. 전체 구조

Prometheus, Loki, Grafana를 함께 쓰는 기본 구조는 다음과 같다.

```text
[Application]
  ├─ /metrics endpoint
  └─ application log
          │
          │ metrics
          ▼
[Prometheus] ───────┐
                    │
                    ▼
                 [Grafana]
                    ▲
                    │
[Promtail] ── logs ─► [Loki]
```

서버 리소스와 컨테이너 리소스까지 함께 보면 구조는 다음처럼 확장된다.

```text
[FastAPI / Flask / Spring App]
  └─ /metrics
        ↓
[Prometheus]

[Node Exporter]
  └─ host CPU, memory, disk, network
        ↓
[Prometheus]

[cAdvisor]
  └─ container CPU, memory, disk, network
        ↓
[Prometheus]

[Promtail]
  └─ /var/log/syslog, docker container logs
        ↓
[Loki]

[Grafana]
  ├─ Prometheus datasource
  ├─ Loki datasource
  ├─ Dashboard
  └─ Alert Rule
```

---

# Part 1. Prometheus

## 4. Prometheus란?

Prometheus는 메트릭을 수집하고 저장하는 오픈소스 모니터링 시스템이다.

주로 다음과 같은 수치형 데이터를 수집한다.

```text
- HTTP 요청 수
- HTTP 응답 시간
- HTTP 에러 수
- CPU 사용률
- 메모리 사용량
- 디스크 사용량
- 네트워크 I/O
- 컨테이너별 리소스 사용량
```

Prometheus의 핵심 특징은 pull 방식이다.

즉, 애플리케이션이 Prometheus에게 데이터를 보내는 것이 아니라, Prometheus가 일정 주기마다 대상 endpoint에 직접 접근해서 메트릭을 가져온다.

```text
Application exposes /metrics
        ↑
        │ scrape
Prometheus
```

---

## 5. Pull 방식이란?

Prometheus는 설정 파일에 등록된 target을 주기적으로 scrape한다.

예를 들어 애플리케이션이 다음 endpoint를 제공한다고 하자.

```text
http://fastapi-app:5001/metrics
```

Prometheus는 이 주소에 일정 주기마다 요청을 보내고, 응답으로 받은 메트릭을 저장한다.

장점은 다음과 같다.

```text
- 어떤 target을 수집 중인지 Prometheus가 명확히 알고 있다.
- target이 죽으면 Prometheus targets 화면에서 DOWN으로 보인다.
- 서비스 디스커버리와 연결하기 좋다.
- 수집 주기와 timeout을 중앙에서 관리할 수 있다.
```

단점도 있다.

```text
- Prometheus가 target에 접근할 수 있어야 한다.
- 네트워크, 방화벽, Service 설정이 틀리면 수집이 안 된다.
- push가 필요한 짧은 batch job에는 별도 Pushgateway가 필요할 수 있다.
```

---

## 6. Prometheus 설정 파일

Prometheus의 핵심 설정 파일은 `prometheus.yml`이다.

예시는 다음과 같다.

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "fastapi"
    static_configs:
      - targets: ["fastapi-app:5001"]

  - job_name: "node"
    static_configs:
      - targets: ["node-exporter:9100"]

  - job_name: "cadvisor"
    static_configs:
      - targets: ["cadvisor:8080"]
```

각 항목의 의미는 다음과 같다.

```text
scrape_interval
- 메트릭을 몇 초마다 수집할지 설정

evaluation_interval
- alert rule을 몇 초마다 평가할지 설정

job_name
- 수집 대상 그룹 이름

targets
- 실제 메트릭 endpoint 주소
```

---

## 7. /metrics endpoint

Prometheus가 수집하는 endpoint는 보통 `/metrics`이다.

FastAPI에서는 `prometheus-fastapi-instrumentator` 같은 라이브러리를 사용해 자동으로 메트릭을 노출할 수 있다.

예시:

```python
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

Instrumentator().instrument(app).expose(app)
```

이렇게 하면 다음과 같은 endpoint가 생긴다.

```text
GET /metrics
```

Prometheus는 이 endpoint를 읽어 HTTP 요청 수, 응답 시간, 상태 코드별 요청 수 같은 지표를 수집한다.

---

## 8. Metric 타입

Prometheus의 주요 metric 타입은 다음과 같다.

### 8.1 Counter

계속 증가하는 값이다.

예시:

```text
http_requests_total
process_cpu_seconds_total
```

Counter는 감소하지 않는다.
요청 수, 에러 수, 처리된 작업 수처럼 누적되는 값에 사용한다.

자주 쓰는 PromQL:

```promql
rate(http_requests_total[5m])
```

5분 동안 초당 요청 수를 계산한다.

---

### 8.2 Gauge

증가할 수도 있고 감소할 수도 있는 값이다.

예시:

```text
memory_usage_bytes
cpu_usage_percent
queue_size
```

현재 메모리 사용량, 현재 큐 길이, 현재 연결 수처럼 상태값에 사용한다.

---

### 8.3 Histogram

값의 분포를 bucket 단위로 저장한다.

주로 latency 측정에 사용한다.

예시:

```text
http_request_duration_seconds_bucket
http_request_duration_seconds_sum
http_request_duration_seconds_count
```

p95 latency를 구할 때 자주 사용한다.

```promql
histogram_quantile(
  0.95,
  rate(http_request_duration_seconds_bucket[5m])
)
```

---

### 8.4 Summary

클라이언트 측에서 quantile을 계산해 노출한다.

Histogram보다 운영상 덜 선호되는 경우가 많다.
여러 인스턴스의 quantile을 집계하기 어렵기 때문이다.

---

## 9. PromQL 기본

PromQL은 Prometheus 데이터를 조회하는 쿼리 언어이다.

### 9.1 요청 수

```promql
rate(http_requests_total[5m])
```

최근 5분 동안 초당 요청 수를 계산한다.

---

### 9.2 에러율

```promql
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
```

전체 요청 중 5xx 비율을 계산한다.

---

### 9.3 p95 latency

```promql
histogram_quantile(
  0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)
```

최근 5분 기준 p95 응답 시간을 계산한다.

---

### 9.4 CPU 사용률

Node Exporter 기준 예시:

```promql
100 - (
  avg by(instance) (
    rate(node_cpu_seconds_total{mode="idle"}[5m])
  ) * 100
)
```

CPU idle 시간을 제외해 실제 사용률을 계산한다.

---

### 9.5 메모리 사용률

```promql
(
  1 -
  (
    node_memory_MemAvailable_bytes
    /
    node_memory_MemTotal_bytes
  )
) * 100
```

전체 메모리 중 사용 중인 비율을 계산한다.

---

### 9.6 디스크 사용률

```promql
(
  1 -
  (
    node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"}
    /
    node_filesystem_size_bytes{fstype!~"tmpfs|overlay"}
  )
) * 100
```

디스크 사용률을 계산한다.

---

## 10. Exporter란?

Exporter는 특정 시스템의 상태를 Prometheus가 읽을 수 있는 metric 형식으로 변환해주는 프로그램이다.

대표적인 exporter는 다음과 같다.

```text
Node Exporter
- Linux 서버의 CPU, memory, disk, network 지표 수집

cAdvisor
- Docker 컨테이너별 CPU, memory, disk, network 지표 수집

Blackbox Exporter
- HTTP, TCP, ICMP endpoint 상태 확인

Postgres Exporter
- PostgreSQL 상태 지표 수집

Redis Exporter
- Redis 상태 지표 수집
```

Prometheus가 모든 시스템을 직접 이해하는 것이 아니라, 각 시스템에 맞는 exporter가 메트릭을 노출하고 Prometheus가 이를 수집하는 구조이다.

---

## 11. Node Exporter

Node Exporter는 서버 자체의 상태를 수집한다.

주요 지표:

```text
- CPU 사용률
- Memory 사용량
- Disk 사용량
- Disk I/O
- Network 송수신량
- Load average
- Filesystem 상태
```

서버가 느려졌을 때 가장 먼저 확인할 수 있는 지표를 제공한다.

예를 들어 API latency가 증가했을 때 Node Exporter 지표를 보면 다음을 확인할 수 있다.

```text
- CPU가 포화되었는가?
- 메모리가 부족해 swap이 발생했는가?
- 디스크가 꽉 찼는가?
- 네트워크 송수신량이 급증했는가?
```

---

## 12. cAdvisor

cAdvisor는 컨테이너별 리소스 사용량을 수집한다.

주요 지표:

```text
- 컨테이너별 CPU 사용량
- 컨테이너별 memory 사용량
- 컨테이너별 network I/O
- 컨테이너별 filesystem 사용량
```

Docker Compose나 Kubernetes 환경에서 특히 유용하다.

서버 전체 CPU가 높을 때 Node Exporter만 보면 어떤 컨테이너가 원인인지 알기 어렵다.
cAdvisor를 사용하면 컨테이너 단위로 원인을 좁힐 수 있다.

---

# Part 2. Loki

## 13. Loki란?

Loki는 Grafana Labs에서 만든 로그 수집 및 검색 시스템이다.

Loki는 Prometheus와 비슷한 방식으로 label을 사용하지만, 모든 로그 본문을 인덱싱하지 않는다는 특징이 있다.

즉, Elasticsearch처럼 로그 전체 텍스트를 무겁게 인덱싱하는 방식이 아니라, label만 인덱싱하고 실제 로그 내용은 압축 저장한다.

이 때문에 Loki는 상대적으로 가볍고, Kubernetes나 Docker 로그 수집에 자주 사용된다.

---

## 14. Loki의 핵심 개념

Loki의 핵심은 다음 세 가지이다.

```text
Log stream
- 같은 label set을 가진 로그 흐름

Label
- 로그를 분류하는 메타데이터
- 예: job="docker", host="dev-server", container="fastapi-app"

Chunk
- 로그를 일정 단위로 묶어 저장한 덩어리
```

예를 들어 다음 label을 가진 로그들이 있다고 하자.

```text
{job="docker", host="dev-server", container="fastapi-app"}
```

이 label 조합이 하나의 log stream을 만든다.

---

## 15. Loki와 Elasticsearch 차이

두 도구 모두 로그 검색에 사용할 수 있지만 설계 철학이 다르다.

```text
Elasticsearch
- 로그 본문 전체를 인덱싱
- 복잡한 텍스트 검색에 강함
- 저장 비용과 리소스 사용량이 큼
- 대규모 검색 분석에 적합

Loki
- label만 인덱싱
- 로그 본문은 압축 저장
- 리소스 사용량이 상대적으로 낮음
- Prometheus/Grafana와 함께 쓰기 좋음
```

Loki는 “모든 로그를 자유롭게 검색하는 검색엔진”이라기보다, “label로 범위를 좁힌 뒤 필요한 로그를 확인하는 운영 로그 시스템”에 가깝다.

---

## 16. Promtail이란?

Promtail은 로그 파일을 읽어서 Loki로 전송하는 agent이다.

구조는 다음과 같다.

```text
/var/log/syslog
/var/log/auth.log
Docker container logs
        ↓
    Promtail
        ↓
      Loki
        ↓
     Grafana
```

Promtail은 다음 일을 한다.

```text
- 어떤 로그 파일을 읽을지 설정
- 로그에 label을 붙임
- 읽은 위치를 positions 파일에 저장
- Loki로 로그 push
```

Promtail은 Prometheus처럼 pull 방식이 아니라, Loki로 로그를 push한다.

---

## 17. Promtail 설정

기본 설정 예시는 다음과 같다.

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /var/log/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: system_logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: system
          host: dev-server
          __path__: /var/log/syslog

  - job_name: docker_logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: docker
          host: dev-server
          __path__: /var/lib/docker/containers/*/*-json.log
    pipeline_stages:
      - docker: {}
```

중요한 필드는 다음과 같다.

```text
clients.url
- 로그를 보낼 Loki endpoint

positions.filename
- Promtail이 어디까지 읽었는지 저장하는 파일

__path__
- 읽을 로그 파일 경로

labels
- Loki에서 검색할 때 사용할 label

pipeline_stages
- Docker JSON 로그 파싱 등 전처리 단계
```

---

## 18. Promtail path 문제

Promtail에서 자주 발생하는 문제는 로그 파일 경로가 실제 OS와 맞지 않는 것이다.

예를 들어 다음 설정은 `/var/log/auth.log`는 잡을 수 있지만, `/var/log/syslog`는 잡지 못할 수 있다.

```yaml
__path__: /var/log/*log
```

왜냐하면 `syslog`는 `.log`로 끝나지 않기 때문이다.

따라서 Ubuntu에서는 다음처럼 명시하는 것이 안전하다.

```yaml
__path__: /var/log/syslog
```

또는 여러 파일을 수집하려면 다음처럼 job을 나누거나 glob pattern을 신중하게 설정해야 한다.

```yaml
scrape_configs:
  - job_name: system_logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: system
          host: dev-server
          __path__: /var/log/{syslog,auth.log,kern.log}
```

운영에서 로그가 안 보이면 가장 먼저 확인할 것은 다음이다.

```text
- Promtail이 실행 중인가?
- Promtail이 해당 파일을 읽을 권한이 있는가?
- __path__가 실제 파일 경로와 일치하는가?
- positions 파일 때문에 이미 읽은 로그로 처리된 것은 아닌가?
- Loki endpoint로 push가 성공하는가?
```

---

## 19. LogQL 기본

LogQL은 Loki에서 로그를 조회하는 쿼리 언어이다.

PromQL과 비슷하지만 로그 검색에 특화되어 있다.

### 19.1 label로 검색

```logql
{job="docker"}
```

job label이 docker인 로그를 조회한다.

---

### 19.2 특정 host 로그 검색

```logql
{host="dev-server"}
```

host label이 dev-server인 로그를 조회한다.

---

### 19.3 문자열 포함 검색

```logql
{host="dev-server"} |= "error"
```

로그 본문에 error가 포함된 로그를 찾는다.

---

### 19.4 정규식 검색

```logql
{host="dev-server"} |~ "error|ERROR|failed|FAIL"
```

여러 에러 패턴을 한 번에 찾는다.

---

### 19.5 에러 로그 개수 집계

```logql
count_over_time(
  {host="dev-server"} |~ "error|ERROR|failed|FAIL" [5m]
)
```

최근 5분 동안 에러 로그가 몇 개 발생했는지 계산한다.

Grafana Alert에서 자주 사용하는 형태이다.

---

## 20. Label 설계 주의점

Loki에서는 label 설계가 매우 중요하다.

좋은 label:

```text
- job
- host
- app
- environment
- container
```

나쁜 label:

```text
- request_id
- user_id
- timestamp
- uuid
- error_message
```

나쁜 label의 공통점은 값의 종류가 너무 많다는 것이다.
이를 high cardinality라고 한다.

Loki는 label을 인덱싱하기 때문에 cardinality가 너무 높으면 성능과 저장 비용이 나빠진다.

따라서 변동이 큰 값은 label이 아니라 로그 본문에 남기는 것이 좋다.

---

# Part 3. Grafana

## 21. Grafana란?

Grafana는 메트릭과 로그를 시각화하는 대시보드 도구이다.

Grafana 자체가 데이터를 수집하는 것은 아니다.
Prometheus, Loki, InfluxDB, Elasticsearch 같은 datasource에서 데이터를 조회해 화면에 보여준다.

Grafana의 핵심 역할은 다음과 같다.

```text
- Prometheus metric 시각화
- Loki log 조회
- Dashboard 구성
- Alert Rule 설정
- Slack, Discord, Email, Webhook 알림 연동
```

---

## 22. Datasource

Grafana에서 데이터를 조회하려면 datasource를 등록해야 한다.

대표적인 datasource는 다음과 같다.

```text
Prometheus
- 메트릭 조회

Loki
- 로그 조회

InfluxDB
- time-series 데이터 조회

Elasticsearch
- 로그/검색 데이터 조회
```

Prometheus datasource URL 예시:

```text
http://prometheus:9090
```

Loki datasource URL 예시:

```text
http://loki:3100
```

Docker Compose 내부에서는 서비스 이름으로 접근할 수 있다.
하지만 브라우저에서 접근할 때와 컨테이너 내부에서 접근할 때의 주소가 다를 수 있으므로 주의해야 한다.

---

## 23. Dashboard

Dashboard는 여러 panel을 묶은 화면이다.

운영에서 기본적으로 필요한 panel은 다음과 같다.

```text
API
- Request rate
- Error rate
- p95 latency
- p99 latency
- Status code distribution

Container
- Container CPU usage
- Container memory usage
- Container network I/O
- Container restart count

Host
- CPU usage
- Memory usage
- Disk usage
- Network traffic

Logs
- Recent error logs
- Error count over time
- Application logs by container
```

Grafana에서는 이미 만들어진 dashboard를 import할 수도 있다.

자주 사용하는 예시는 다음과 같다.

```text
Node Exporter Full
- Linux 서버 지표 대시보드

Docker Monitoring with cAdvisor
- 컨테이너 지표 대시보드
```

---

## 24. Alert Rule

Grafana Alert는 특정 조건을 만족하면 알림을 보내는 기능이다.

예를 들어 다음 조건을 설정할 수 있다.

```text
- CPU 사용률 80% 이상
- Memory 사용률 80% 이상
- Disk 사용률 85% 이상
- 5xx error rate 5% 이상
- p95 latency 2초 이상
- 최근 5분간 ERROR 로그 1개 이상
```

Prometheus 기반 alert 예시:

```promql
(
  1 -
  (
    node_memory_MemAvailable_bytes
    /
    node_memory_MemTotal_bytes
  )
) * 100
```

Loki 기반 alert 예시:

```logql
count_over_time({host="dev-server"} |~ "error|ERROR|failed|FAIL" [5m])
```

---

## 25. No Data 처리

Grafana Alert에서 중요한 설정 중 하나가 No Data 처리이다.

No Data는 쿼리 결과가 없다는 뜻이다.

No Data는 두 가지 의미일 수 있다.

```text
정상적인 No Data
- 최근 5분간 ERROR 로그가 없음
- 즉, 좋은 상태일 수 있음

문제 상황의 No Data
- Prometheus가 target을 scrape하지 못함
- Loki datasource 연결이 끊김
- Promtail이 로그를 보내지 못함
```

Grafana의 No Data 처리 옵션은 다음과 같다.

```text
Alerting
- 데이터가 없으면 장애로 판단

No Data
- No Data 상태로 표시

Normal
- 데이터가 없으면 정상으로 처리

Keep Last State
- 이전 상태 유지
```

ERROR 로그 감지 알림에서는 No Data를 Normal로 두는 경우가 많다.
에러 로그가 없다는 것은 정상일 수 있기 때문이다.

하지만 CPU 사용률이나 서비스 UP 여부 같은 지표에서 No Data가 발생하면 수집 장애일 수 있으므로 Alerting으로 두는 것이 맞을 수 있다.

---

## 26. Discord Webhook 알림

Grafana는 Slack, Email, Webhook, Discord 등으로 알림을 보낼 수 있다.

Discord Webhook을 사용할 때 흐름은 다음과 같다.

```text
Grafana Alert Rule
   ↓
Contact Point
   ↓
Discord Webhook URL
   ↓
Discord Channel
```

운영에서는 다음 알림을 설정할 수 있다.

```text
- CPU 80% 이상
- Memory 80% 이상
- Disk 85% 이상
- 5xx error rate 증가
- p95 latency 증가
- ERROR 로그 감지
- Prometheus target DOWN
```

알림을 너무 많이 보내면 피로도가 높아지므로, 처음에는 중요한 알림만 설정하는 것이 좋다.

---

# Part 4. 실전 운영 체크리스트

## 27. 서비스 배포 후 확인할 것

서비스를 배포한 뒤에는 다음 순서로 확인한다.

```text
1. 컨테이너 상태 확인
   docker ps
   docker compose ps

2. 애플리케이션 응답 확인
   curl http://server:port/

3. metrics endpoint 확인
   curl http://server:port/metrics

4. Prometheus target 확인
   http://prometheus:9090/targets

5. Grafana datasource 확인
   Prometheus datasource connected
   Loki datasource connected

6. 대시보드 확인
   API latency
   Error rate
   CPU
   Memory
   Disk

7. 로그 확인
   Loki Explore
   {host="dev-server"}

8. 알림 테스트
   CPU 부하 발생
   ERROR 로그 발생
```

---

## 28. Prometheus target DOWN일 때

Prometheus target이 DOWN이면 다음을 확인한다.

```text
1. target 주소가 맞는가?
2. Prometheus 컨테이너에서 해당 주소로 접근 가능한가?
3. 포트가 열려 있는가?
4. 애플리케이션이 /metrics를 제공하는가?
5. Docker Compose service name이 맞는가?
6. 네트워크가 같은 compose network에 묶여 있는가?
7. 방화벽이나 보안그룹이 막고 있지 않은가?
```

Docker Compose 내부에서 확인:

```bash
docker exec -it prometheus sh
wget -qO- http://fastapi-app:5001/metrics
```

---

## 29. Grafana에 데이터가 안 보일 때

```text
1. datasource URL이 맞는가?
2. Prometheus/Loki 컨테이너가 실행 중인가?
3. Grafana 컨테이너에서 datasource로 접근 가능한가?
4. Prometheus targets가 UP인가?
5. 쿼리 시간 범위가 맞는가?
6. label 이름이 맞는가?
7. metric 이름이 실제 존재하는가?
```

Prometheus에서는 쿼리가 되는데 Grafana에서 안 보이면 Grafana datasource 문제일 가능성이 높다.

Prometheus 자체에서 쿼리가 안 되면 scrape 설정이나 target 문제일 가능성이 높다.

---

## 30. Loki에 로그가 안 보일 때

```text
1. Promtail이 실행 중인가?
2. Promtail config의 clients.url이 맞는가?
3. Loki가 실행 중인가?
4. Promtail에서 Loki로 접근 가능한가?
5. __path__가 실제 로그 파일과 일치하는가?
6. Promtail이 로그 파일을 읽을 권한이 있는가?
7. positions 파일 때문에 새 로그를 안 읽는 것은 아닌가?
8. Grafana Explore에서 label selector가 맞는가?
```

Promtail 로그 확인:

```bash
docker logs promtail --tail 100
```

Loki label 확인:

```logql
{job="system"}
```

또는 Grafana Explore에서 label browser를 사용한다.

---

## 31. CPU 알림이 너무 자주 울릴 때

CPU 사용률은 순간적으로 튈 수 있다.

따라서 alert 조건에는 보통 지속 시간을 둔다.

```text
CPU > 80%
for 5 minutes
```

이렇게 설정하면 80%를 잠깐 넘는 경우에는 알림이 가지 않고, 5분 이상 지속될 때만 알림이 발생한다.

---

## 32. ERROR 로그 알림이 너무 자주 울릴 때

ERROR 로그 alert는 너무 민감할 수 있다.

개선 방법:

```text
- error 키워드를 더 구체화
- 특정 app label만 대상으로 설정
- count 기준을 1개 이상이 아니라 5개 이상으로 설정
- 5분이 아니라 10분 윈도우로 조정
- No Data를 Normal로 처리
- debug/test 로그는 수집 대상에서 제외
```

예시:

```logql
count_over_time(
  {app="fastapi"} |~ "ERROR|Traceback|Exception" [5m]
) > 3
```

---

# Part 5. AI DevOps 관점

## 33. AI API에서 봐야 할 지표

일반 API와 AI API는 모니터링 관점이 조금 다르다.

일반 API에서 보는 지표:

```text
- request rate
- error rate
- latency
- CPU
- memory
- disk
```

AI API에서 추가로 봐야 할 지표:

```text
- model inference latency
- p95/p99 latency
- timeout rate
- retry count
- input size
- output token count
- token usage
- GPU utilization
- GPU memory
- OCR document page count
- OCR processing time
- document type별 error rate
- RAG retrieval latency
- vector DB latency
- answer generation latency
```

AI 서비스는 같은 endpoint라도 입력 크기와 모델 상태에 따라 응답 시간이 크게 달라진다.

따라서 평균 latency보다 p95, p99 latency를 봐야 한다.

---

## 34. OCR API 모니터링 예시

OCR API라면 다음 지표를 볼 수 있다.

```text
System metrics
- CPU
- memory
- disk
- network
- container restart

API metrics
- request count
- error rate
- p95 latency
- timeout rate
- file upload size
- page count

OCR quality metrics
- character error rate
- word error rate
- field extraction F1
- table structure accuracy
- document type별 failure rate
```

운영에서는 품질 지표와 시스템 지표를 같이 봐야 한다.

예를 들어 CPU와 latency는 정상인데 특정 문서 유형의 field extraction F1이 떨어질 수 있다.
이 경우 인프라 장애가 아니라 모델 품질 회귀에 가깝다.

---

## 35. RAG API 모니터링 예시

RAG API라면 다음 지표가 중요하다.

```text
Retrieval metrics
- recall@k
- nDCG@k
- retrieval latency
- vector DB query latency
- top-k result count

Generation metrics
- answer similarity
- hallucination indicator
- token usage
- LLM latency
- timeout rate

System metrics
- API latency
- error rate
- CPU/memory
- queue length
```

RAG는 API가 200 OK를 반환해도 검색 품질이나 답변 품질이 떨어질 수 있다.
따라서 Prometheus/Grafana 같은 운영 지표에 더해 품질 평가 지표도 함께 관리해야 한다.

---

## 36. 좋은 대시보드 구성

AI API 운영 대시보드는 다음처럼 구성할 수 있다.

```text
상단
- 전체 요청 수
- error rate
- p95 latency
- p99 latency
- timeout rate

중단
- endpoint별 latency
- status code 분포
- container CPU/memory
- GPU utilization

하단
- 최근 ERROR 로그
- 모델 호출 실패 로그
- 외부 API timeout 로그
- 고객사별 요청 실패율

별도 품질 탭
- OCR CER/WER
- field extraction F1
- RAG recall@k
- answer similarity
```

---

# 37. 정리

Prometheus, Loki, Grafana는 각각 역할이 다르다.

```text
Prometheus
- 수치형 metric 수집
- pull 방식
- PromQL 사용
- alert 조건의 기반

Loki
- log 수집 및 검색
- label 기반 인덱싱
- LogQL 사용
- Promtail로 로그 전송

Grafana
- metric과 log 시각화
- dashboard 구성
- alert rule 설정
- Discord/Slack/Webhook 알림 연동
```

운영에서는 이 셋을 함께 사용해 다음을 확인한다.

```text
- 서비스가 살아 있는지
- 응답 시간이 느려졌는지
- 에러율이 증가했는지
- 서버 리소스가 부족한지
- 어떤 로그가 남았는지
- 장애가 발생했을 때 알림을 받을 수 있는지
```

DevOps에서 중요한 것은 도구 이름을 아는 것이 아니라, 장애가 났을 때 어떤 지표와 로그를 어떤 순서로 볼지 아는 것이다.

Prometheus로 이상 징후를 수치로 확인하고, Loki로 관련 로그를 찾아 원인을 좁히며, Grafana로 대시보드와 알림을 구성하는 흐름을 이해하면 운영 가능한 시스템에 한 걸음 가까워질 수 있다.
