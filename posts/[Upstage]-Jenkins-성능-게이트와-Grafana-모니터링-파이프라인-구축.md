---
title: "[CI/CD] Jenkins 성능 게이트와 Grafana 모니터링 파이프라인 구축"
source: ""
published: "2026-05-30T12:00:00.000Z"
topic: "docker-k8s"
category: "CI/CD"
---

## 1. 개요

이 프로젝트는 Flask 기반 Conversation 서비스의 Jenkins CI/CD 파이프라인에서 DEV 서버 배포 이후 JMeter 부하 테스트를 실행하고, p95 latency 기준으로 성능 게이트를 적용한 경험이다.

초기에는 JMeter 요청이 모두 실패하거나, 컨테이너가 정상적으로 떠 있는 것처럼 보여도 실제 엔드포인트가 맞지 않아 404/415/500 오류가 발생했다. 이후 JMX 파일의 대상 서버 IP, HTTP Method, JSON Body, Content-Type, API Path, Dockerfile CMD, 환경변수, OpenAI API Key, Google API Credential 문제를 하나씩 확인하면서 부하 테스트가 정상적으로 실행되도록 수정했다.

이후 성능 게이트를 통과한 develop 브랜치 코드를 자동으로 PR 생성 및 main 브랜치 merge까지 연결했고, DEV 서버와 모니터링 서버를 분리하여 Prometheus, Node Exporter, Loki, Promtail, Grafana, Discord Webhook 기반의 모니터링과 알림 구조를 구성했다.

이 경험을 통해 CI/CD는 단순 배포 자동화가 아니라, 배포 후 성능 검증, 자동 승격, 모니터링, 알림까지 포함하는 운영 파이프라인이어야 한다는 점을 배웠다.

---

## 2. 업스테이지 AI DevOps 직무와의 연결

업스테이지 AI DevOps 직무에서는 OCR, LLM, RAG API 같은 AI 서비스를 안정적으로 배포하고 운영하는 역량이 중요하다.

AI 서비스는 일반 API보다 다음과 같은 운영 리스크가 크다.

- 요청별 처리 시간이 길어 p95/p99 latency가 튀기 쉬움
- 외부 API 또는 모델 서버 호출에 따라 timeout이 발생할 수 있음
- API는 살아 있어도 특정 엔드포인트나 특정 입력에서만 실패할 수 있음
- 모델 또는 프롬프트 변경 이후 품질 회귀가 발생할 수 있음
- 고객사 환경에 따라 서버, 네트워크, 인증 정보, 로그 수집 방식이 달라질 수 있음
- 장애 발생 시 애플리케이션 코드, 컨테이너, CI/CD, 인프라, 외부 API, 모니터링을 함께 봐야 함

이 프로젝트에서는 Jenkins, JMeter, Docker, Prometheus, Loki, Promtail, Grafana, Discord Webhook을 연결하면서 배포 이후 성능과 운영 상태를 검증하는 구조를 실습했다.

특히 JMeter의 p95 latency를 Jenkins 성능 게이트로 사용하고, 기준을 통과해야만 PR 생성과 main merge로 넘어가게 만든 점은 AI API 배포에서도 그대로 확장할 수 있는 구조이다.

---

## 3. 전체 운영 파이프라인 구조

최종적으로 구성한 흐름은 다음과 같다.

```text
develop push
   ↓
Jenkins Pipeline Trigger
   ↓
Test & Coverage
   ↓
SonarQube Analysis
   ↓
Quality Gate
   ↓
Docker Build
   ↓
Deploy to DEV
   ↓
JMeter Load Test
   ↓
Performance Gate
   ↓
Create PR
   ↓
Auto Merge to Main
   ↓
Monitoring & Alerting
```

여기서 핵심은 배포가 끝났다고 바로 main으로 반영하지 않고, DEV 서버에 실제로 배포된 서비스를 대상으로 부하 테스트를 수행한 뒤 p95 latency 기준을 통과해야 다음 단계로 넘어가도록 한 점이다.

---

## 4. JMeter 부하 테스트 실패 원인 분석

처음에는 JMeter가 500건 요청을 모두 실패시키는 문제가 발생했다.

초기에는 서버가 죽었거나 네트워크가 막힌 문제라고 생각했지만, 실제 원인은 여러 계층에 나뉘어 있었다.

```text
1. JMX 파일의 대상 서버 IP 오류
2. DEV 서버 컨테이너 상태 불안정
3. 애플리케이션 포트 불일치
4. JMeter HTTP Method 오류
5. JSON Body와 Content-Type 불일치
6. API endpoint path 불일치
7. OpenAI API Key 환경변수 누락
8. Google API Credential 문제
9. Dockerfile CMD 오류로 컨테이너 즉시 종료
10. 서버에 존재하지 않는 /health endpoint 호출
```

이 과정에서 단순히 "JMeter가 실패했다"라고 판단하지 않고, 요청이 서버까지 도달했는지, HTTP status code가 무엇인지, 컨테이너 로그에 어떤 예외가 찍히는지, JMeter가 어떤 endpoint를 때리고 있는지 순서대로 확인했다.

장애 분석의 기준은 다음과 같이 잡았다.

```text
즉시 실패
→ IP, 포트, 네트워크, 컨테이너 상태 확인

응답은 오지만 404
→ endpoint path 확인

응답은 오지만 415
→ Content-Type, JSON Body 확인

응답은 오지만 422
→ 요청 필드와 서버 request schema 확인

응답은 오지만 500
→ 서버 내부 로직, 환경변수, 외부 API Key 확인

응답 시간이 너무 김
→ 외부 API latency, worker 수, EC2 스펙, timeout 확인
```

이 경험을 통해 부하 테스트 실패는 단순히 성능 문제가 아니라, 요청 구조·엔드포인트·컨테이너 실행 방식·환경변수·외부 API 의존성이 모두 얽혀 발생할 수 있다는 점을 배웠다.

---

## 5. JMeter 요청 구조 수정

Conversation 서비스의 `/ChatAI` 엔드포인트는 JSON 요청을 기대하는 구조였다.

```python
args = request.get_json() or {}
content = args.get('message', '')
```

따라서 JMeter 요청은 다음 조건을 만족해야 했다.

```text
- HTTP Method: POST
- Path: /ChatAI
- Content-Type: application/json
- Body Data: Raw JSON
- JSON Key: message
```

예상되는 요청 Body는 다음과 같다.

```json
{
  "message": "안녕하세요, 건강한 식단 추천해주세요"
}
```

초기에는 JMeter가 JSON이 아니라 form data처럼 요청을 보내거나, Content-Type이 누락되거나, 서버에 없는 path를 호출하면서 415, 422, 404 오류가 발생했다.

이를 수정한 뒤에는 JMeter 요청이 서버까지 정상 도달했고, 이후 문제를 서버 내부 로직 또는 외부 API 호출 문제로 좁힐 수 있었다.

---

## 6. Dockerfile CMD 오류와 컨테이너 종료 문제

부하 테스트가 계속 실패한 또 다른 원인은 Dockerfile의 CMD 오류였다.

컨테이너는 생성되었지만 즉시 종료되었고, `docker ps`에는 보이지 않으며 `docker ps -a`에서만 Exited 상태로 확인되었다.

문제는 Gunicorn 실행 명령이 잘못되어 컨테이너 내부 서버가 정상적으로 올라오지 않는 것이었다.

```text
docker run
   ↓
컨테이너 생성
   ↓
Gunicorn 실행 실패
   ↓
컨테이너 즉시 Exited
   ↓
8000 포트 응답 없음
   ↓
JMeter 요청 100% 실패
```

최종적으로 Dockerfile의 CMD를 단순하고 안정적인 형태로 정리했다.

```dockerfile
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
```

이 경험을 통해 Docker 컨테이너가 "실행 명령을 받았다"는 것과 "애플리케이션이 정상적으로 서비스 중이다"는 것이 다르다는 점을 배웠다.

컨테이너 장애 확인 시에는 다음 순서가 중요하다.

```bash
docker ps
docker ps -a
docker logs dev-conv --tail 200
curl http://DEV_SERVER:8000
```

---

## 7. 환경변수와 외부 API Credential 문제

Conversation 서비스는 OpenAI API와 Google Cloud Language API를 사용했다.

이 때문에 로컬에서는 동작하던 코드가 Jenkins 또는 Docker 컨테이너 환경에서는 실패할 수 있었다.

주요 원인은 다음과 같았다.

```text
- OPENAI_API_KEY가 Jenkins Credential에 등록되지 않음
- Docker run 시 환경변수 전달 누락
- Google credential json 파일이 컨테이너 내부에 존재하지 않음
- GOOGLE_APPLICATION_CREDENTIALS 경로가 컨테이너 기준 경로와 맞지 않음
- Google API 권한 부족으로 token 발급 또는 API 호출 실패
```

OpenAI API Key는 Jenkins Credential로 등록한 뒤 Docker 실행 시 환경변수로 전달했다.

```bash
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  --name dev-conv \
  conversation-conv:dev
```

Google Credential의 경우에는 로컬 파일을 EC2 서버로 전송하고, 컨테이너 내부에 volume mount한 뒤 `GOOGLE_APPLICATION_CREDENTIALS` 환경변수로 경로를 지정하는 방식이 필요했다.

이 경험을 통해 AI 서비스 운영에서는 API Key와 Credential 관리가 매우 중요하다는 점을 배웠다. 특히 외부 API 호출이 실패하면 단순 기능 오류가 아니라 latency 증가, timeout, JMeter 실패, 배포 중단으로 이어질 수 있다.

---

## 8. 성능 게이트와 p95 latency 기준

JMeter가 정상 실행된 이후에는 p95 latency 기준으로 성능 게이트를 적용했다.

초기에는 기준을 2초로 설정했지만, 50명 동시 사용자와 외부 API 호출이 포함된 구조에서는 p95가 7~10초 수준으로 측정되었다.

```text
Total requests: 500
p95 response time: 7148ms
Threshold: 2000ms
Result: FAILED
```

이후 서버 특성과 테스트 조건을 고려하여 기준을 조정했다.

최종적으로 부하 테스트가 정상 실행되었고, 다음과 같이 성능 게이트를 통과했다.

```text
Total requests: 1000
p95 response time: 3ms
Threshold: 12000ms
Result: PASSED
```

여기서 중요한 점은 단순히 기준을 느슨하게 만든 것이 아니라, 테스트 요청이 실제 서비스 로직을 제대로 때리고 있는지, 컨테이너가 정상 실행 중인지, 에러율이 0%인지 먼저 확인한 뒤 성능 기준을 조정했다는 점이다.

성능 게이트를 설계할 때는 다음을 함께 고려해야 한다.

```text
- 테스트 대상 endpoint가 실제 존재하는가
- 요청 payload가 실제 서비스 요청과 유사한가
- 외부 API 호출이 포함되는가
- 동시 사용자 수가 현실적인가
- 평균 latency보다 p95/p99가 중요한가
- error rate가 0에 가까운가
- timeout이 발생하는가
```

AI API에서는 평균 응답 시간보다 p95, p99, timeout rate가 더 중요하다. 일부 문서나 일부 요청만 늦어져도 고객 경험이 크게 나빠질 수 있기 때문이다.

---

## 9. PR 자동 생성과 Auto Merge 구성

성능 게이트를 통과한 뒤에는 develop 브랜치 변경사항을 main 브랜치로 자동 반영하는 구조를 만들었다.

처음에는 Auto Merge 단계에서 open PR이 존재하지 않아 실패했다.

```text
Auto Merge가 필요한 상황
→ 반드시 develop → main PR이 있어야 함
```

이를 해결하기 위해 Load Test와 Auto Merge 사이에 Create PR stage를 추가했다.

최종 파이프라인 구조는 다음과 같다.

```text
1. Checkout
2. Test & Coverage
3. SonarQube Analysis
4. Quality Gate
5. Deploy to DEV
6. Load Test
7. Create PR
8. Auto Merge to Main
9. Deploy to PROD
10. Cleanup Docker
```

Create PR stage의 역할은 다음과 같다.

```text
- 기존 develop → main PR 존재 여부 확인
- PR이 없으면 자동 생성
- 기존 PR이 있으면 해당 PR 번호 사용
- PR_NUMBER 환경변수에 저장
- Auto Merge stage에서 PR_NUMBER 사용
```

또한 Auto Merge 단계에서는 GitHub API 응답을 파싱하기 위해 `jq`가 필요했는데, Jenkins 서버에 `jq`가 설치되어 있지 않아 실패했다.

```bash
sudo apt update
sudo apt install -y jq
```

이 경험을 통해 CI/CD 자동화는 Jenkinsfile 코드만 작성한다고 끝나는 것이 아니라, Jenkins 서버에 필요한 CLI 도구와 실행 환경까지 함께 준비해야 한다는 점을 배웠다.

---

## 10. Jenkins 최종 성공 흐름

최종적으로 Jenkins 파이프라인은 다음 흐름으로 성공했다.

```text
- develop 브랜치 감지
- 테스트 26개 통과
- Coverage 98%
- SonarQube Analysis 성공
- Quality Gate OK
- Docker 이미지 빌드
- DEV 서버로 image.tar.gz 전송
- DEV 서버에서 docker load
- 기존 dev-conv 컨테이너 stop/rm
- 새 컨테이너 run
- JMeter 1000건 요청 실행
- Error 0%
- p95 latency 기준 통과
- 기존 PR #1 확인
- PR 자동 merge 성공
- Pipeline SUCCESS
```

이 과정에서 최종적으로 다음 메시지를 확인했다.

```text
Quality gate is 'OK'
Performance Gate PASSED
Pull Request successfully merged
Finished: SUCCESS
```

이 경험은 단순히 배포 버튼을 누른 것이 아니라, 테스트·정적 분석·배포·부하 테스트·성능 게이트·PR 생성·자동 머지까지 하나의 흐름으로 연결한 경험이라는 점에서 의미가 있다.

---

## 11. 모니터링 서버 분리

CI/CD 파이프라인이 성공한 뒤에는 DEV 서버와 별도로 모니터링 서버를 구성했다.

처음에는 MAIN 서버에 Prometheus, Loki, Grafana를 같이 두는 구조를 고민했지만, MAIN 서버의 디스크가 20GB 수준이라 운영 서비스와 모니터링 스택을 함께 두기에는 위험하다고 판단했다.

최종적으로 모니터링 전용 서버를 새로 구성했다.

```text
DEV 서버
├─ Flask Conversation Service
├─ Node Exporter
└─ Promtail

Monitoring 서버
├─ Prometheus
├─ Loki
├─ Grafana
└─ Alertmanager
```

이 구조에서 DEV 서버의 Node Exporter는 서버 메트릭을 노출하고, Promtail은 로그를 Loki로 전송한다. 모니터링 서버의 Prometheus는 DEV 서버의 exporter를 scrape하고, Grafana는 Prometheus와 Loki를 datasource로 연결한다.

---

## 12. Prometheus와 Node Exporter 구성

DEV 서버에는 Node Exporter를 설치해 CPU, memory, disk, network 같은 서버 메트릭을 수집하도록 했다.

```bash
wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz
tar xvf node_exporter-1.7.0.linux-amd64.tar.gz
sudo mv node_exporter-1.7.0.linux-amd64/node_exporter /usr/local/bin/
```

systemd service로 등록해 서버 재부팅 후에도 자동 실행되도록 구성했다.

```ini
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=ubuntu
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=default.target
```

Prometheus에서는 DEV 서버의 Node Exporter endpoint를 scrape target으로 등록했다.

```yaml
scrape_configs:
  - job_name: "dev-node"
    static_configs:
      - targets: ["DEV_SERVER_IP:9100"]
```

이를 통해 Grafana에서 DEV 서버의 CPU, memory, disk 사용률을 확인할 수 있게 되었다.

---

## 13. Loki와 Promtail 로그 수집

로그 수집을 위해 DEV 서버에 Promtail을 설치하고, 모니터링 서버의 Loki로 로그를 전송하도록 구성했다.

초기 Promtail 설정에서는 `/var/log/*log` 패턴만 사용했는데, Ubuntu의 주요 시스템 로그인 `/var/log/syslog`는 `log`로 끝나지 않아 수집 대상에서 빠졌다.

이 때문에 ERROR 로그를 찍어도 Loki에 전달되지 않았고, Grafana Alert Rule에서는 No Data 상태가 발생했다.

문제 원인은 다음과 같았다.

```text
Ubuntu syslog 경로: /var/log/syslog
기존 Promtail path: /var/log/*log
결과: syslog가 패턴에 매칭되지 않음
```

수정 후 Promtail 설정에는 명시적으로 `/var/log/syslog`를 포함했다.

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /var/log/positions.yaml

clients:
  - url: http://MONITORING_SERVER_IP:3100/loki/api/v1/push

scrape_configs:
  - job_name: system_logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: system
          host: dev-server
          __path__:
            - /var/log/syslog
            - /var/log/auth.log
            - /var/log/kern.log
            - /var/log/cloud-init*.log
            - /var/log/*log

  - job_name: docker_logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: docker
          host: dev-server
          __path__:
            - /var/lib/docker/containers/*/*-json.log
    pipeline_stages:
      - docker: {}
```

이후 Promtail이 `/var/log/syslog`를 읽어 Loki로 전송했고, Loki에서 error 문자열이 감지되었으며, Grafana Alert Rule이 Discord Webhook을 호출하는 흐름까지 확인했다.

---

## 14. Grafana Alert와 Discord Webhook

Grafana에서는 Prometheus와 Loki datasource를 연결한 뒤 Alert Rule을 구성했다.

설정한 Alert Rule은 다음과 같다.

```text
1. CPU 사용률 80% 이상
2. Memory 사용률 80% 이상
3. DEV 서버 ERROR 로그 감지
```

ERROR 로그 감지는 Loki query를 사용해 구성했다.

```logql
count_over_time({host="dev-server"} |~ "error|Error|ERROR|failed|FAIL" [5m])
```

처음에는 데이터가 없을 때 Grafana가 `DatasourceNoData` 상태를 Discord로 보내는 문제가 있었다.

Grafana의 No Data 처리 옵션은 다음과 같이 이해했다.

```text
Alerting
- 데이터가 없으면 장애로 판단하고 알림을 보냄

No Data
- No Data 상태로 표시하지만 알림 정책에 따라 전송될 수 있음

Normal
- 데이터가 없으면 정상 상태로 취급
- 불필요한 알림 방지 가능

Keep Last State
- 이전 상태 유지
- 이전에 Firing이었다면 계속 Firing으로 남을 수 있음
```

불필요한 No Data 알림을 막기 위해 No Data 상태를 Normal로 처리하도록 수정했다.

이후 의도적으로 ERROR 로그를 발생시켜 Promtail → Loki → Grafana Alert → Discord Webhook 흐름이 동작하는지 확인했다.

---

## 15. 장애 분석에서 배운 점

이 프로젝트에서 가장 많이 배운 점은 장애를 한 가지 원인으로 단정하면 안 된다는 것이다.

JMeter 실패 하나만 보더라도 원인은 다양했다.

```text
- 잘못된 대상 IP
- 잘못된 API path
- POST가 아닌 GET 요청
- JSON Body 누락
- Content-Type 누락
- 컨테이너 즉시 종료
- Dockerfile CMD 오류
- 외부 API Key 누락
- Google Credential 문제
- 서버 디스크 부족
- EC2 리소스 부족
- 존재하지 않는 /health endpoint
```

모니터링에서도 마찬가지였다.

```text
- Loki config의 compactor working directory 누락
- Docker overlayfs snapshot 누적으로 storage 꼬임
- Promtail path pattern 오류
- Ubuntu syslog 경로 누락
- Grafana No Data 정책 설정 문제
- Discord Webhook 알림 미전송 문제
```

결국 DevOps 장애 대응은 다음 순서로 진행해야 한다.

```text
1. 요청이 올바른 서버로 가는지 확인
2. 포트와 컨테이너 상태 확인
3. HTTP status code 확인
4. 서버 로그 확인
5. 환경변수와 credential 확인
6. 외부 API 의존성 확인
7. CI/CD stage별 실패 지점 확인
8. 디스크, 메모리, CPU 확인
9. 모니터링 수집 경로 확인
10. 알림 정책 확인
```

---

## 16. 업스테이지 직무 관련 경험으로 정리

이 경험은 업스테이지 AI DevOps 직무와 다음 지점에서 연결된다.

### 16.1 배포 후 성능 검증

Jenkins에서 Docker 배포 후 JMeter를 실행하고, p95 latency 기준을 통과해야 다음 단계로 넘어가도록 구성했다.

AI API도 배포 후 단순 health check만으로는 부족하다. OCR API나 LLM API는 요청 크기, 문서 유형, 모델 호출 상태에 따라 latency 편차가 크기 때문에 p95/p99, error rate, timeout rate를 함께 봐야 한다.

### 16.2 품질 게이트와 자동 승격

성능 게이트를 통과한 develop 브랜치만 PR 생성 및 main merge로 이어지게 했다.

이 구조는 AI 서비스에서도 모델 품질 지표, OCR 정확도, RAG answer similarity, error rate, latency 기준을 통과한 버전만 다음 환경으로 승격시키는 방식으로 확장할 수 있다.

### 16.3 Credential과 외부 API 의존성 관리

OpenAI API Key와 Google Credential 문제를 겪으면서, AI 서비스 운영에서는 credential 전달 방식과 권한 설정이 매우 중요하다는 점을 배웠다.

업스테이지의 AI API 운영에서도 고객사별 인증 정보, 클라우드 API, 모델 서버 credential을 안전하게 관리해야 한다.

### 16.4 모니터링과 알림

Prometheus, Node Exporter, Loki, Promtail, Grafana, Discord Webhook을 연결하면서 서버 메트릭과 로그 기반 알림을 구성했다.

AI 서비스 운영에서도 CPU, memory, disk뿐 아니라 API error rate, timeout, p95 latency, 특정 에러 로그, 모델 호출 실패를 모니터링해야 한다.

### 16.5 계층적 트러블슈팅

JMeter 실패, Dockerfile CMD 오류, 컨테이너 종료, API path 불일치, Loki 설정 오류, Promtail path 문제, Grafana No Data 알림 문제를 겪으면서 장애를 계층별로 분리해서 보는 습관을 만들었다.

업스테이지에서 고객사 환경에 AI 서비스를 배포하거나 운영할 때도 이런 계층적 분석 방식이 필요하다고 생각한다.

---

## 17. 면접용 요약

면접에서는 다음과 같이 설명할 수 있다.

> Jenkins 파이프라인에서 DEV 서버 배포 이후 JMeter 부하 테스트를 실행하고, p95 latency 기준으로 성능 게이트를 적용한 경험이 있습니다. 처음에는 JMeter 요청이 모두 실패했는데, 원인을 따라가 보니 JMX의 대상 IP 오류, API path 불일치, JSON Body와 Content-Type 문제, OpenAI API Key 누락, Dockerfile CMD 오류 등 여러 문제가 섞여 있었습니다.
>
> 저는 이를 단순히 JMeter 문제로 보지 않고, 요청이 서버까지 도달하는지, HTTP status code가 무엇인지, 컨테이너가 정상 실행 중인지, docker logs에 어떤 오류가 남는지 순서대로 확인했습니다. 이후 JMeter 요청 구조를 실제 API에 맞추고, Dockerfile CMD와 환경변수를 수정해 부하 테스트가 정상 실행되도록 만들었습니다.
>
> 이후 p95 latency 기준을 통과한 경우에만 Create PR과 Auto Merge 단계로 넘어가도록 구성했습니다. 이 과정에서 PR이 없을 때 자동 생성하는 stage를 추가했고, GitHub API 응답 파싱을 위해 Jenkins 서버에 jq를 설치하는 등 CI/CD 실행 환경도 함께 정리했습니다.
>
> 파이프라인 성공 이후에는 DEV 서버와 별도 모니터링 서버를 구성해 Prometheus, Node Exporter, Loki, Promtail, Grafana, Discord Webhook을 연결했습니다. CPU, memory, ERROR 로그 감지 알림을 만들었고, Promtail이 Ubuntu의 /var/log/syslog를 수집하지 못해 Loki 알림이 동작하지 않는 문제도 해결했습니다.
>
> 이 경험을 통해 배포 자동화는 단순히 컨테이너를 띄우는 것이 아니라, 배포 후 성능 검증, 자동 승격, 로그·메트릭 수집, 알림까지 이어져야 한다는 점을 배웠습니다. 업스테이지에서도 OCR이나 LLM API 배포 과정에서 latency, error rate, timeout, 로그 기반 장애 감지를 연결하는 AI DevOps 업무에 기여하고 싶습니다.

---

## 18. 배운 점

```text
- JMeter 실패는 성능 문제뿐 아니라 endpoint, method, body, header, credential 문제일 수 있다.
- HTTP status code를 기준으로 장애 범위를 좁히면 원인 파악이 빨라진다.
- Docker 컨테이너가 생성되었다고 해서 애플리케이션이 정상 실행 중인 것은 아니다.
- docker ps, docker ps -a, docker logs, curl 확인이 중요하다.
- 외부 API Key와 Credential 누락은 500 error, timeout, latency 증가로 이어질 수 있다.
- p95 latency는 평균 응답 시간보다 사용자 경험과 성능 게이트에 더 적합하다.
- 성능 게이트를 통과한 코드만 PR 생성 및 main merge로 연결할 수 있다.
- Jenkinsfile만 고쳐서는 부족하고, Jenkins 서버에 jq 같은 실행 도구도 준비되어야 한다.
- 모니터링 서버는 운영 서버와 분리하는 것이 안정적이다.
- Prometheus는 메트릭, Loki는 로그, Grafana는 시각화와 알림에 적합하다.
- Promtail 로그 수집 경로가 실제 OS 로그 경로와 맞지 않으면 알림이 동작하지 않는다.
- Grafana No Data 정책을 잘못 두면 불필요한 알림이 발생한다.
- DevOps 장애 대응은 코드, 컨테이너, 네트워크, 서버 리소스, 외부 API, 모니터링을 함께 봐야 한다.
```

---

## 19. 정리

이 프로젝트는 Jenkins 기반 CI/CD 파이프라인을 단순 배포 자동화에서 끝내지 않고, 배포 후 부하 테스트, p95 latency 기반 성능 게이트, 자동 PR 생성, Auto Merge, Prometheus/Loki/Grafana 기반 모니터링과 Discord 알림까지 확장한 경험이다.

초기에는 JMeter 100% 실패, 컨테이너 종료, Dockerfile CMD 오류, API path 불일치, 외부 API credential 누락, 디스크 부족, Loki 설정 오류, Promtail 수집 경로 문제 등 많은 장애가 발생했다. 하지만 각 문제를 계층별로 나누어 확인하면서 최종적으로 파이프라인 성공과 모니터링 알림까지 연결했다.

이 경험을 바탕으로 AI 서비스 운영에서도 단순히 API를 배포하는 것에 그치지 않고, 배포 후 성능과 품질을 검증하고, 로그와 메트릭을 통해 이상 상태를 감지하며, 기준을 통과한 버전만 다음 환경으로 승격시키는 DevOps 파이프라인을 설계하고 싶다.
