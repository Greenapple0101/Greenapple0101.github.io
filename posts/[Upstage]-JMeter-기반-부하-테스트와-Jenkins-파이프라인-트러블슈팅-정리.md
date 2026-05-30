---
title: "[Upstage] JMeter 기반 부하 테스트와 Jenkins 파이프라인 트러블슈팅 정리"
source: ""
published: "2026-05-30T21:40:00.000Z"
---

FastAPI Todo 서비스를 EC2에 배포하고, Jenkins 파이프라인에서 테스트·빌드·배포·JMeter 부하 테스트·HTML Report 생성·InfluxDB/Grafana 연동까지 구성하는 과정에서 발생한 문제들을 정리한 문서이다.

이번 트러블슈팅의 핵심은 단순히 JMeter가 실패한 것이 아니라, 다음 요소들이 서로 얽혀 있었다는 점이다.

- FastAPI 프로젝트 실행 경로 문제
- Docker 컨테이너 import path 문제
- Jenkins 파이프라인 설정 문제
- JMeter JMX 시나리오와 실제 API 불일치
- JMeter HTML Dashboard 생성 조건
- Jenkins HTML Report 렌더링 차단 문제
- InfluxDB apt repository 문제
- Telegraf 대신 JMeter Backend Listener를 사용하는 구조 전환

---

# 1. 전체 실습 구조

## 1-1. 목표

이번 실습의 목표는 FastAPI 애플리케이션을 Jenkins를 통해 자동 배포하고, JMeter로 부하 테스트를 실행한 뒤, 결과를 HTML Report 또는 InfluxDB/Grafana로 확인하는 것이었다.

전체 흐름은 다음과 같다.

```text
GitHub
  ↓
Jenkins Pipeline
  ↓
pytest / coverage
  ↓
Docker build
  ↓
DockerHub push
  ↓
EC2 deploy
  ↓
JMeter load test
  ↓
HTML Report 생성
  ↓
InfluxDB / Grafana 실시간 시각화
````

## 1-2. 사용한 주요 구성 요소

* FastAPI
* Docker
* DockerHub
* EC2
* Jenkins
* JMeter
* JMeter HTML Dashboard
* InfluxDB
* Grafana
* Jenkins HTML Publisher Plugin

---

# 2. FastAPI 로컬 실행 문제

## 2-1. 발생한 증상

로컬에서 FastAPI를 실행하는 과정에서 여러 오류가 발생했다.

```text
Internal Server Error
Address already in use
ModuleNotFoundError: No module named 'app'
pydantic / pydantic-core version conflict
```

## 2-2. 원인

주요 원인은 다음과 같았다.

* 이미 사용 중인 포트에서 uvicorn을 다시 실행함
* 가상환경에 설치된 패키지 버전이 꼬임
* 실행 위치와 import 경로가 맞지 않음
* `app` 디렉토리가 Python package로 인식되지 않음
* `static`, `templates` 경로 계산이 실제 프로젝트 구조와 맞지 않음

## 2-3. 해결 방향

기존 uvicorn 프로세스를 종료한 뒤, 프로젝트 루트가 아니라 실제 FastAPI 앱 기준 경로에서 실행해야 했다.

```bash
cd fastapi-app
uvicorn app.main:app --reload
```

또한 패키지 충돌이 있을 경우 가상환경을 새로 생성하고 의존성을 다시 설치했다.

```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2-4. 정리

FastAPI에서 `ModuleNotFoundError: No module named 'app'` 오류가 발생하면 대부분 실행 위치와 import path 문제다.

즉, 아래 두 가지를 반드시 맞춰야 한다.

```text
1. 현재 명령어를 실행하는 위치
2. uvicorn에 넘기는 app import 경로
```

---

# 3. FastAPI 프로젝트 구조 문제

## 3-1. 실제 프로젝트 구조

실제 프로젝트 구조는 대략 다음과 같았다.

```text
project-root/
├── Jenkinsfile
├── fastapi-app/
│   ├── Dockerfile
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── static/
│   └── templates/
└── jmeter/
    ├── Dockerfile
    └── fastapi_test_plan.jmx
```

## 3-2. static / templates 경로 문제

FastAPI에서 HTML 템플릿과 정적 파일을 사용할 때는 경로 계산이 중요하다.

로컬에서는 다음 구조처럼 보이지만,

```text
fastapi-app/static
fastapi-app/templates
```

Docker 컨테이너 내부에서는 `WORKDIR` 설정에 따라 다음처럼 보일 수 있다.

```text
/app/static
/app/templates
```

또는 잘못 구성하면 다음처럼 꼬일 수 있다.

```text
/app/fastapi-app/static
/app/fastapi-app/templates
```

## 3-3. 해결 방향

`main.py`에서 현재 파일 기준으로 경로를 계산하도록 수정했다.

예시:

```python
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

templates = Jinja2Templates(directory=BASE_DIR / "templates")
```

## 3-4. 정리

FastAPI에서 템플릿이나 정적 파일이 깨질 때는 코드 자체보다 경로 기준점이 문제인 경우가 많다.

특히 로컬과 Docker 환경을 모두 고려해야 한다.

---

# 4. Dockerfile 문제

## 4-1. 발생한 증상

Docker 이미지 빌드 후 컨테이너를 실행하면 바로 종료되었다.

로그를 확인하면 다음 오류가 있었다.

```text
ModuleNotFoundError: No module named 'fastapi-app'
```

## 4-2. 원인

Dockerfile의 uvicorn 실행 경로가 잘못되어 있었다.

잘못된 예시는 다음과 같다.

```dockerfile
CMD ["uvicorn", "fastapi-app.app.main:app", "--host", "0.0.0.0", "--port", "5001"]
```

Python import path에서 `fastapi-app`처럼 하이픈이 들어간 디렉토리명은 모듈명으로 사용할 수 없다.

## 4-3. 해결

`WORKDIR /app` 기준으로 `app.main:app`을 실행하도록 수정했다.

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5001"]
```

## 4-4. 정리

Docker 컨테이너 내부에서 Python 모듈을 찾을 때는 로컬 폴더명이 아니라 컨테이너 내부의 `WORKDIR` 기준으로 import path가 결정된다.

---

# 5. EC2 배포 문제

## 5-1. 발생한 증상

EC2에서 컨테이너를 실행했지만, `docker ps`에는 보이지 않고 `docker ps -a`에서만 `Exited` 상태로 보였다.

```bash
docker ps
docker ps -a
docker logs FastApi-app
```

로그에는 다음과 같은 오류가 있었다.

```text
ModuleNotFoundError: No module named 'fastapi-app'
```

## 5-2. 원인

로컬에서 발생한 Dockerfile import path 문제가 EC2 배포 환경에서도 동일하게 발생한 것이다.

## 5-3. 해결

Dockerfile을 수정한 뒤 이미지를 다시 빌드하고 DockerHub에 push했다.

```bash
docker build -t <dockerhub-username>/<image-name>:latest .
docker push <dockerhub-username>/<image-name>:latest
```

EC2에서는 기존 컨테이너를 제거하고 새 이미지로 다시 실행했다.

```bash
docker rm -f FastApi-app || true
docker pull <dockerhub-username>/<image-name>:latest

docker run -d \
  --name FastApi-app \
  -p 5001:5001 \
  <dockerhub-username>/<image-name>:latest
```

## 5-4. 최종 상태

다음 주소에서 FastAPI 서비스 접속이 성공했다.

```text
http://<EC2_PUBLIC_IP>:5001
```

Daily Records 화면이 정상 렌더링되었고, `static`과 `templates`도 정상 동작했다.

---

# 6. Jenkins 접속 문제

## 6-1. EC2 인스턴스 상태 확인

처음에는 Jenkins 웹 UI에 접속이 되지 않아 서버 상태부터 확인했다.

확인한 내용은 다음과 같다.

```bash
sudo systemctl status jenkins
sudo lsof -i :8080
```

결과적으로 Jenkins 서비스는 정상 실행 중이었다.

```text
active (running)
```

또한 Jenkins는 `8080` 포트에서 정상적으로 LISTEN 중이었다.

## 6-2. 브라우저 접속 문제

브라우저에서 IP만 입력하거나 Safari가 자동으로 `www.`를 붙이면서 잘못된 주소로 열리는 문제가 있었다.

Jenkins 접속 주소는 반드시 다음 형태여야 한다.

```text
http://<EC2_PUBLIC_IP>:8080
```

## 6-3. 정리

Jenkins가 정상 실행 중인데 웹 접속이 안 될 때는 다음 순서로 확인한다.

```bash
sudo systemctl status jenkins
sudo lsof -i :8080
```

그리고 브라우저에는 반드시 프로토콜과 포트를 포함해서 입력한다.

```text
http://서버IP:8080
```

---

# 7. Jenkins Pipeline 기본 구조

## 7-1. 파이프라인 흐름

Jenkinsfile의 전체 흐름은 다음과 같았다.

```text
Checkout
  ↓
Setup Environment & Install Dependencies
  ↓
Test & Coverage
  ↓
Docker Build
  ↓
Docker Push
  ↓
Deploy to EC2
  ↓
Build JMeter Image
  ↓
Run JMeter Load Test
  ↓
Publish HTML Reports
```

## 7-2. Checkout 문제

처음에는 GitHub 저장소 주소가 혼동되었다.

예를 들어 다음과 같은 저장소명이 혼동되었다.

```text
FASTAPI-APP.git
FastApi_Todos.git
```

이 때문에 로컬에서 수정한 내용과 Jenkins가 가져오는 코드가 다르게 보였다.

## 7-3. 정리

Jenkins에서 계속 옛날 코드가 실행되는 것처럼 보이면 먼저 확인해야 할 것은 다음이다.

```text
1. Jenkinsfile이 바라보는 GitHub repository 주소
2. branch 이름
3. 실제 push가 되었는지
4. Jenkins workspace가 최신 상태인지
```

---

# 8. Jenkins Pytest 단계 문제

## 8-1. 발생한 증상

Jenkins에서 pytest 실행 중 다음 오류가 발생했다.

```text
ModuleNotFoundError: No module named 'app'
```

## 8-2. 원인

Jenkins workspace 기준으로 Python이 `fastapi-app/app`을 모듈로 인식하지 못했다.

## 8-3. 해결

pytest 실행 전에 `PYTHONPATH`를 추가했다.

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/fastapi-app
```

예시:

```groovy
stage('Test & Coverage') {
    steps {
        sh '''
            python3 -m venv venv
            . venv/bin/activate
            pip install -r fastapi-app/requirements.txt
            export PYTHONPATH=$PYTHONPATH:$(pwd)/fastapi-app
            pytest fastapi-app/tests --cov=fastapi-app/app
        '''
    }
}
```

## 8-4. 정리

Jenkins에서만 pytest import 오류가 나는 경우는 대부분 로컬 실행 위치와 Jenkins workspace 구조가 다르기 때문이다.

---

# 9. Jenkins 배포 단계 문제

## 9-1. SSH Credential 문제

EC2 배포 단계에서 SSH credential 오류가 발생했다.

Jenkins에서 EC2에 접속하려면 다음이 정확히 맞아야 한다.

```text
1. Jenkins Credentials ID
2. pem key
3. EC2 username
4. EC2 public IP
5. security group SSH 허용
```

## 9-2. 컨테이너 이름 충돌

배포 단계에서 다음 오류가 발생했다.

```text
docker: Conflict. The container name "/FastApi-app" is already in use
```

## 9-3. 해결

새 컨테이너 실행 전에 기존 컨테이너를 제거하도록 했다.

```bash
docker rm -f FastApi-app || true
```

배포 스크립트 예시는 다음과 같다.

```bash
docker pull <dockerhub-username>/<image-name>:latest
docker rm -f FastApi-app || true

docker run -d \
  --name FastApi-app \
  -p 5001:5001 \
  <dockerhub-username>/<image-name>:latest
```

## 9-4. Health Check 추가

배포 직후 바로 JMeter를 실행하면 FastAPI가 아직 준비되지 않은 상태일 수 있다.

그래서 `/health` 엔드포인트를 확인하는 대기 로직을 추가했다.

```bash
for i in {1..10}; do
  if curl -f http://localhost:5001/health; then
    echo "FastAPI is ready"
    exit 0
  fi
  echo "Waiting for FastAPI..."
  sleep 3
done

echo "FastAPI health check failed"
exit 1
```

---

# 10. JMeter 이미지 문제

## 10-1. 발생한 문제

JMeter Docker 이미지를 구성하는 과정에서 여러 문제가 발생했다.

```text
image not found
403 forbidden
permission 문제
ARM / AMD64 architecture mismatch
exec format error
```

## 10-2. 원인

JMeter 베이스 이미지가 환경과 맞지 않거나, EC2 아키텍처와 이미지 아키텍처가 맞지 않았다.

특히 로컬 Mac이 ARM 계열이고 EC2가 AMD64인 경우, Docker 이미지 아키텍처가 꼬일 수 있다.

## 10-3. 정리

JMeter 이미지를 직접 빌드할 때는 다음을 확인해야 한다.

```bash
docker build --platform linux/amd64 -t jmeter-custom .
```

또는 Jenkins/EC2 환경에서 직접 빌드하는 방식으로 아키텍처 문제를 줄일 수 있다.

---

# 11. JMX 파일 문제

## 11-1. 발생한 증상

JMeter 실행 중 JMX 파일 로딩 오류가 발생했다.

```text
XML loading error
SummaryReport deserialize error
```

## 11-2. 원인

JMeter GUI에서 만든 JMX 파일과 Jenkins에서 사용하는 JMeter 버전이 맞지 않거나, 특정 Listener가 CLI 환경에서 deserialize되지 않는 문제가 있었다.

## 11-3. 해결 방향

JMeter CLI 실행용 JMX는 최대한 단순하게 구성하는 것이 좋다.

권장 구성은 다음과 같다.

```text
Test Plan
  └── Thread Group
        └── HTTP Request
        └── Backend Listener
```

GUI 확인용 Listener인 Summary Report, View Results Tree 등은 Jenkins용 JMX에서는 제거하는 편이 안전하다.

## 11-4. 정리

Jenkins에서 JMeter를 실행할 때는 GUI용 Listener를 많이 넣지 않는 것이 좋다.

HTML Dashboard는 JTL 결과 파일을 기반으로 따로 생성하면 된다.

---

# 12. JMeter 테스트 요청 실패

## 12-1. 발생한 증상

JMeter 테스트 결과가 전부 실패로 표시되었다.

```text
Err: 30 (100.00%)
```

요청 로그를 보면 `/users` 요청이 404를 반환했다.

```text
/users -> 404
/ -> 200
```

## 12-2. 원인

JMX에 설정한 API 경로와 실제 FastAPI 서비스에 존재하는 API 경로가 달랐다.

즉, 인프라 문제가 아니라 테스트 시나리오가 실제 애플리케이션과 맞지 않았던 것이다.

## 12-3. 해결

실제 존재하는 API 기준으로 JMX를 수정해야 한다.

예를 들어 `/`가 정상 동작한다면 첫 테스트는 다음처럼 단순하게 구성할 수 있다.

```text
GET /
```

헬스체크 엔드포인트가 있다면 다음도 사용할 수 있다.

```text
GET /health
```

## 12-4. 정리

JMeter에서 404가 많이 발생하면 서버가 죽은 것이 아니라, JMeter가 없는 API를 때리고 있을 가능성이 높다.

먼저 curl로 실제 API를 확인해야 한다.

```bash
curl -i http://<EC2_PUBLIC_IP>:5001/
curl -i http://<EC2_PUBLIC_IP>:5001/health
curl -i http://<EC2_PUBLIC_IP>:5001/users
```

---

# 13. JMeter HTML Report 문제

## 13-1. 처음 증상

Jenkins에서 JMeter HTML Report 페이지는 열렸지만 내용이 비어 보였다.

비어 있던 영역은 다음과 같았다.

```text
Statistics
Errors
Top 5 Errors by sampler
```

## 13-2. 처음 의심한 원인

처음에는 다음 문제들을 의심했다.

```text
1. JMeter 실행 실패
2. HTML Publisher 설정 문제
3. report 경로 문제
4. JMeter Dockerfile 문제
5. LoadFocus 플러그인 문제
6. 브라우저 문제
```

## 13-3. 확인된 사실

JMeter 자체는 실행되었다.

```text
요청 30건
에러 20건
```

즉, 테스트가 아예 실행되지 않은 것은 아니었다.

## 13-4. CSV / XML 포맷 문제

JMeter HTML Dashboard를 만들려면 `results.jtl`이 CSV 포맷이어야 한다.

`output_format=xml`로 바꾸면 다음 오류가 발생했다.

```text
Report generation requires csv output format
```

## 13-5. 해결

Jenkinsfile의 JMeter 실행 옵션에서 CSV 포맷을 유지해야 한다.

```bash
-Jjmeter.save.saveservice.output_format=csv
```

예시:

```bash
jmeter -n \
  -t /jmeter/fastapi_test_plan.jmx \
  -l /jmeter/results.jtl \
  -e \
  -o /jmeter/report \
  -Jjmeter.save.saveservice.output_format=csv
```

## 13-6. 정리

JMeter HTML Dashboard 생성 조건은 다음과 같다.

```text
1. JMeter 실행 성공
2. results.jtl 생성
3. results.jtl은 CSV 포맷
4. report 출력 폴더는 비어 있어야 함
5. index.html이 report 폴더 안에 생성되어야 함
```

---

# 14. JMeter report 폴더 문제

## 14-1. 발생한 증상

JMeter HTML Report 생성 시 다음 오류가 발생했다.

```text
Cannot write to 'report' as folder is not empty
```

## 14-2. 원인

JMeter는 HTML Dashboard를 생성할 때 출력 폴더가 비어 있기를 요구한다.

이미 이전 실행 결과가 남아 있으면 실패한다.

## 14-3. 해결

JMeter 실행 전에 기존 결과물을 삭제한다.

```bash
rm -rf jmeter/report jmeter/results.jtl jmeter/jmeter.log
mkdir -p jmeter/report
```

## 14-4. 권한 문제

Jenkins가 삭제하려고 할 때 다음 오류가 발생할 수도 있다.

```text
Permission denied
```

이 경우 이전에 Docker 컨테이너가 root 권한으로 report 파일을 생성했을 가능성이 있다.

해결 방법은 다음과 같다.

```bash
sudo rm -rf jmeter/report jmeter/results.jtl jmeter/jmeter.log
```

또는 Docker 실행 시 Jenkins workspace에 root 소유 파일이 남지 않도록 주의해야 한다.

---

# 15. Jenkins HTML Report가 비어 보이는 문제

## 15-1. 발생한 증상

JMeter와 Pytest HTML Report가 Jenkins에서 열리기는 하지만 화면이 비어 보였다.

브라우저 개발자 도구 콘솔에는 다음과 같은 오류가 있었다.

```text
Blocked script execution because the document's frame is sandboxed
Refused to apply stylesheet because of Content Security Policy
```

CSS, JS, font 리소스도 차단되었다.

## 15-2. 핵심 원인

문제는 JMeter 리포트 생성 실패가 아니었다.

핵심 원인은 Jenkins의 보안 정책이었다.

```text
Jenkins CSP(Content Security Policy)
Jenkins iframe sandbox 정책
```

Jenkins가 HTML Report 내부의 CSS, JavaScript, font 로딩을 차단하고 있었기 때문에 리포트가 비어 보인 것이다.

## 15-3. 중요한 구분

이 문제는 다음 두 가지를 분리해서 봐야 한다.

```text
1. report 파일이 생성되었는가?
2. Jenkins 화면에서 그 report를 정상 렌더링하는가?
```

이번 경우에는 1번은 성공했고, 2번에서 막힌 것이다.

## 15-4. 확인 방법

Jenkins workspace 또는 archived report에서 `index.html`이 실제로 존재하는지 확인한다.

```bash
ls -al jmeter/report
cat jmeter/report/index.html | head
```

파일이 정상이라면 브라우저 콘솔을 확인한다.

```text
F12 또는 개발자 도구
Console 탭
CSP / sandbox / stylesheet / script 차단 여부 확인
```

## 15-5. 정리

HTML Report가 비어 보인다고 해서 항상 JMeter 실패는 아니다.

Jenkins가 보안 정책으로 HTML/CSS/JS 렌더링을 막는 경우도 있다.

---

# 16. HTML Publisher Plugin 점검

## 16-1. 확인한 내용

Jenkins Installed Plugins에서 다음 플러그인을 확인했다.

```text
HTML Publisher plugin 427
OWASP Markup Formatter Plugin
```

## 16-2. 결론

HTML Publisher Plugin은 설치되어 있었고, report를 publish하는 기능 자체는 동작했다.

따라서 플러그인 미설치나 플러그인 자체 오류가 핵심 원인은 아니었다.

## 16-3. 정리

HTML Publisher가 설치되어 있는데도 화면이 깨지면 플러그인보다 Jenkins CSP 정책을 먼저 의심해야 한다.

````

---

# 17. Jenkins CSP / Sandbox 해제 시도

## 17-1. Script Console 시도

Jenkins Script Console에서 다음 설정을 시도했다.

```groovy
System.setProperty("hudson.model.DirectoryBrowserSupport.CSP", "")
System.setProperty("hudson.model.DirectoryBrowserSupport.SANDBOX_FULL", "false")
System.setProperty("hudson.model.DirectoryBrowserSupport.SANDBOX", "")
````

실행은 되었지만 브라우저에서는 여전히 리소스가 차단되었다.

## 17-2. /etc/default/jenkins 수정 시도

다음처럼 JVM 옵션을 넣으려고 했다.

```bash
JAVA_ARGS="$JAVA_ARGS -Dhudson.model.DirectoryBrowserSupport.CSP="
JAVA_ARGS="$JAVA_ARGS -Dhudson.model.DirectoryBrowserSupport.SANDBOX_FULL=true"
```

하지만 `ps -ef | grep jenkins` 결과 실제 Jenkins 프로세스에 옵션이 반영되지 않았다.

## 17-3. systemd override 시도

다음 명령어로 systemd override 설정도 시도했다.

```bash
sudo systemctl edit jenkins
```

하지만 설정 저장이나 반영이 제대로 되지 않아, 실제 프로세스에는 옵션이 보이지 않았다.

## 17-4. 현재 결론

현재 핵심은 Jenkins가 실제로 어떤 systemd service 정의로 실행되는지 확인하는 것이다.

확인 명령어는 다음과 같다.

```bash
systemctl cat jenkins
ps -ef | grep jenkins
```

JVM 옵션이 실제 프로세스에 보여야 한다.

```text
-Dhudson.model.DirectoryBrowserSupport.CSP=
```

## 17-5. 정리

Jenkins 설정 파일을 수정했다고 해서 반드시 반영되는 것은 아니다.

최종 확인은 항상 프로세스 기준으로 해야 한다.

```bash
ps -ef | grep jenkins
```

---

# 18. InfluxDB 도입 시도

## 18-1. 목적

JMeter 결과를 단순 HTML Report로 보는 것에서 끝내지 않고, InfluxDB와 Grafana로 실시간 메트릭을 시각화하려고 했다.

목표 구조는 다음과 같다.

```text
JMeter
  ↓
InfluxDB
  ↓
Grafana
```

## 18-2. InfluxDB 컨테이너 실행

InfluxDB 2.7 컨테이너 실행을 시도했다.

```bash
docker run ...
```

하지만 다음과 같은 conflict가 발생했다.

```text
Conflict. The container name "influxdb" is already in use
```

## 18-3. 확인

```bash
docker ps -a | grep influxdb
```

확인 결과 기존 `influxdb` 컨테이너가 이미 실행 중이었다.

## 18-4. 결론

InfluxDB는 새로 만들 필요가 없었다.

이미 실행 중인 컨테이너를 그대로 사용하면 된다.

---

# 19. InfluxDB org 개념

## 19-1. org란?

InfluxDB에서 `org`는 bucket을 포함하는 상위 조직 단위다.

실습에서는 보통 다음처럼 사용했다.

```text
org = sca
```

## 19-2. InfluxDB 구조

InfluxDB의 기본 구조는 다음과 같다.

```text
Organization
  └── Bucket
        └── Measurement
              ├── Fields
              └── Tags
```

## 19-3. 예시

```text
Organization: sca
Bucket: jmeter
Measurement: jmeter
Field: responseTime, count, errorCount
Tag: application, transaction
```

## 19-4. 정리

JMeter에서 InfluxDB로 데이터를 보낼 때는 최소한 다음 값들이 필요하다.

```text
InfluxDB URL
org
bucket
token
measurement
application name
```

---

# 20. Telegraf 설치 실패

## 20-1. 발생한 증상

Jenkins 서버에서 Telegraf 설치를 시도했다.

```bash
sudo apt-get install -y telegraf
```

하지만 다음 오류가 발생했다.

```text
Unable to locate package telegraf
```

## 20-2. 원인

Ubuntu 24.04 Noble 환경에서 InfluxData 공식 apt 저장소가 제대로 지원되지 않았다.

오류는 다음과 같았다.

```text
https://repos.influxdata.com/ubuntu noble Release 404 Not Found
```

## 20-3. 문제의 영향

Telegraf 설치 실패 자체보다 더 큰 문제는, 잘못 추가된 InfluxData apt repository가 Jenkins 파이프라인의 `apt-get update`까지 실패시키기 시작했다는 점이다.

## 20-4. 결론

현재 환경에서는 Telegraf 설치 방식은 비추천이다.

대신 JMeter Backend Listener를 사용해서 InfluxDB로 직접 메트릭을 전송하는 방식이 더 단순하다.

---

# 21. Jenkins 파이프라인 apt-get update 실패

## 21-1. 발생한 증상

Jenkins 파이프라인의 다음 단계에서 실패했다.

```text
Setup Environment & Install Dependencies
```

오류는 다음과 같았다.

```text
ERROR: script returned exit code 100
```

이후 단계는 모두 skipped 되었다.

```text
Test skipped
Build skipped
Push skipped
Deploy skipped
JMeter skipped
```

## 21-2. 원인

Jenkins 서버 OS에 수동으로 추가한 InfluxData apt repository 파일이 남아 있었다.

문제 파일은 다음이었다.

```text
/etc/apt/sources.list.d/influxdata.list
```

이 파일 때문에 `apt-get update`를 할 때마다 Noble repository 404 오류가 발생했다.

## 21-3. 해결

Jenkins 서버에서 문제 repository 파일을 삭제했다.

```bash
sudo rm -f /etc/apt/sources.list.d/influxdata.list
sudo apt-get update
```

## 21-4. 정리

Jenkinsfile 자체가 문제가 아니라 Jenkins 서버의 apt repository 설정이 문제였다.

즉, 파이프라인 실패 원인은 코드가 아니라 서버 환경 오염이었다.

---

# 22. JMeter + InfluxDB 연동 방식

## 22-1. 최종 선택한 방식

Telegraf를 사용하지 않고 JMeter Backend Listener를 사용하는 방식으로 전환했다.

구조는 다음과 같다.

```text
JMeter Backend Listener
  ↓
InfluxDB HTTP API
  ↓
InfluxDB Bucket
  ↓
Grafana Dashboard
```

## 22-2. Backend Listener 클래스

JMeter에서 사용하는 Backend Listener implementation은 다음이다.

```text
org.apache.jmeter.visualizers.backend.influxdb.InfluxdbBackendListenerClient
```

## 22-3. 주요 파라미터

Backend Listener에 필요한 주요 값은 다음과 같다.

```text
influxdbMetricsSender
influxdbUrl
application
measurement
testTitle
token
summaryOnly
samplersRegex
```

## 22-4. 예시 설정

```text
influxdbUrl = http://<EC2_PUBLIC_IP>:8086/api/v2/write?org=sca&bucket=jmeter
application = fastapi-todo
measurement = jmeter
testTitle = fastapi-load-test
token = 실제 InfluxDB Token
summaryOnly = false
samplersRegex = .*
```

## 22-5. 정리

Telegraf가 없어도 JMeter는 Backend Listener를 통해 InfluxDB로 직접 메트릭을 보낼 수 있다.

---

# 23. JMX 파일 병합

## 23-1. 기존 상태

기존에는 다음 두 가지가 따로 있었다.

```text
1. fastapi_test_plan.jmx 전체 XML
2. InfluxDB Backend Listener XML 조각
```

## 23-2. 처리 방향

기존 Test Plan 내부의 적절한 위치에 Backend Listener를 삽입했다.

구조는 다음과 같이 맞췄다.

```text
Test Plan
  └── Thread Group
        ├── HTTP Request
        └── Backend Listener
```

## 23-3. 남은 작업

JMX 파일에서 실제로 바꿔야 하는 값은 InfluxDB token이다.

```text
token = 실제 토큰으로 교체
```

## 23-4. 정리

JMX는 XML 구조가 조금만 깨져도 실행되지 않는다.

따라서 조각을 아무 위치에 붙이는 것이 아니라, JMeter Test Plan 구조 안에 맞게 삽입해야 한다.

---

# 24. Grafana 연결

## 24-1. 목표

InfluxDB에 들어간 JMeter 메트릭을 Grafana에서 시각화한다.

확인하고 싶은 지표는 다음과 같다.

```text
response time
throughput
error count
error rate
active threads
requests per second
```

## 24-2. 필요한 값

Grafana에서 InfluxDB datasource를 추가하려면 다음 값이 필요하다.

```text
URL: http://<EC2_PUBLIC_IP>:8086
Organization: sca
Bucket: jmeter
Token: InfluxDB token
```

## 24-3. 확인 순서

```text
1. InfluxDB 컨테이너 실행 확인
2. InfluxDB UI 접속
3. org / bucket / token 확인
4. JMeter Backend Listener에 token 반영
5. Jenkins에서 JMeter 재실행
6. InfluxDB bucket에 데이터 들어오는지 확인
7. Grafana datasource 연결
8. dashboard panel 생성
```

---

# 25. 최종 Jenkinsfile에서 신경 쓴 부분

## 25-1. Influx 관련 apt 설치 제거

Telegraf 설치 과정에서 apt repository 문제가 발생했기 때문에 Jenkinsfile에서 Influx 관련 apt 설치는 제거했다.

## 25-2. JMeter 결과 포맷 CSV 유지

JMeter HTML Dashboard 생성을 위해 CSV 포맷을 유지했다.

```bash
-Jjmeter.save.saveservice.output_format=csv
```

## 25-3. HTML Report 경로 유지

HTML Publisher 설정은 다음 경로 기준으로 유지했다.

```text
jmeter/report/index.html
```

## 25-4. Docker build/push/deploy 유지

기존 FastAPI Docker build, push, deploy 흐름은 유지했다.

## 25-5. report 폴더 초기화

JMeter 실행 전 기존 report 폴더를 정리했다.

```bash
rm -rf jmeter/report jmeter/results.jtl jmeter/jmeter.log
mkdir -p jmeter/report
```

---

# 26. 최종적으로 확인된 것

## 26-1. 해결된 항목

* 로컬 FastAPI 실행 성공
* Docker 이미지 빌드 성공
* DockerHub push 성공
* EC2 FastAPI 컨테이너 실행 성공
* FastAPI UI 정상 렌더링
* Jenkins 웹 UI 접속 성공
* Jenkins 기본 배포 성공
* JMeter 실행 자체는 성공
* JMeter HTML Report 생성 조건 확인
* InfluxDB 컨테이너 실행 확인
* JMeter + InfluxDB 연동용 JMX 준비

## 26-2. 원인 파악 완료 항목

* FastAPI import path 문제
* Docker CMD 경로 문제
* Jenkins repository 주소 혼동
* Jenkins SSH credential 문제
* 컨테이너 이름 충돌 문제
* JMeter JMX와 실제 API 불일치 문제
* JMeter HTML Dashboard CSV 요구사항
* Jenkins CSP/Sandbox로 인한 HTML Report 렌더링 차단 문제
* InfluxData Noble repository 404 문제
* Telegraf 설치 비추천 판단

---

# 27. 아직 남은 작업

## 27-1. Jenkins 서버 apt repository 정리

먼저 Jenkins 서버에서 잘못된 InfluxData repository 파일을 삭제해야 한다.

```bash
sudo rm -f /etc/apt/sources.list.d/influxdata.list
sudo apt-get update
```

## 27-2. InfluxDB Token 확인

InfluxDB UI에 접속해서 실제 token을 확인한다.

```text
http://<EC2_PUBLIC_IP>:8086
```

## 27-3. JMX 파일 token 교체

`fastapi_test_plan.jmx` 안의 token 값을 실제 token으로 교체한다.

```text
token = 실제 InfluxDB token
```

## 27-4. Jenkins 재실행

Jenkins에서 파이프라인을 다시 실행한다.

확인할 것은 다음이다.

```text
1. pytest 성공
2. docker build 성공
3. docker push 성공
4. EC2 deploy 성공
5. JMeter 실행 성공
6. results.jtl 생성
7. report/index.html 생성
8. InfluxDB에 데이터 적재
```

## 27-5. Grafana 대시보드 생성

Grafana에서 InfluxDB datasource를 연결하고 JMeter 지표를 시각화한다.

최종 제출용으로는 다음 화면을 캡처하면 좋다.

```text
1. Jenkins Pipeline Success 화면
2. EC2 FastAPI 서비스 접속 화면
3. JMeter HTML Report 화면
4. InfluxDB bucket 데이터 확인 화면
5. Grafana dashboard 화면
```

---

# 28. 이번 트러블슈팅의 핵심 교훈

## 28-1. JMeter 문제는 세 단계로 나눠서 봐야 한다

JMeter 문제가 생기면 다음을 분리해서 봐야 한다.

```text
1. JMeter가 실행되었는가?
2. JTL 결과 파일이 생성되었는가?
3. HTML Report가 생성되었는가?
4. Jenkins에서 HTML Report가 제대로 렌더링되는가?
```

이번 문제에서는 JMeter 실행과 report 생성은 되었지만, Jenkins 보안 정책 때문에 화면 표시가 깨지는 문제가 있었다.

## 28-2. HTML Report가 비어 보인다고 report 생성 실패는 아니다

Jenkins에서 HTML Report가 비어 보이면 반드시 브라우저 콘솔을 확인해야 한다.

```text
CSP
sandbox
blocked script
blocked stylesheet
```

이런 메시지가 있으면 JMeter가 아니라 Jenkins 렌더링 정책 문제다.

## 28-3. JMeter HTML Dashboard는 CSV 기반이다

JMeter Dashboard 생성에는 CSV 형식의 JTL이 필요하다.

```text
output_format=xml 사용 시 실패
output_format=csv 사용 필요
```

## 28-4. 없는 API를 때리면 인프라 문제가 아닌 시나리오 문제다

JMeter에서 404가 많이 나온다면 서버나 Jenkins보다 JMX 요청 경로를 먼저 확인해야 한다.

```bash
curl -i http://<서버IP>:5001/
curl -i http://<서버IP>:5001/health
curl -i http://<서버IP>:5001/users
```

## 28-5. Jenkins 서버 환경 오염도 파이프라인 실패 원인이 된다

이번에는 Jenkinsfile이 아니라 Jenkins 서버의 apt repository 설정이 문제였다.

```text
/etc/apt/sources.list.d/influxdata.list
```

이 파일 하나 때문에 `apt-get update`가 실패했고, 이후 모든 stage가 skipped 되었다.

## 28-6. Telegraf 없이도 JMeter + InfluxDB 연동은 가능하다

JMeter Backend Listener를 사용하면 Telegraf 없이도 InfluxDB로 직접 메트릭을 보낼 수 있다.

```text
JMeter → InfluxDB → Grafana
```

이 구조가 현재 실습 환경에서는 더 단순하고 안정적이다.

---

# 29. 최종 요약

이번 트러블슈팅은 JMeter 하나의 문제가 아니라 FastAPI, Docker, Jenkins, EC2, JMeter, InfluxDB, Grafana가 연결된 전체 DevOps 파이프라인 문제였다.

가장 큰 원인은 다음과 같이 정리할 수 있다.

```text
1. FastAPI 실행 경로와 Docker import path 불일치
2. Jenkins GitHub repository 주소 혼동
3. EC2 컨테이너 이름 충돌
4. JMeter JMX 시나리오와 실제 API 불일치
5. JMeter HTML Dashboard의 CSV 포맷 요구사항
6. Jenkins CSP/Sandbox로 인한 HTML Report 렌더링 차단
7. InfluxData Noble repository 404로 인한 apt-get update 실패
8. Telegraf 대신 Backend Listener로 구조 전환 필요
```

결국 이번 실습에서 중요한 것은 단순히 “JMeter를 돌렸다”가 아니다.

실제로 중요한 경험은 다음이다.

```text
FastAPI 서비스를 배포하고,
Jenkins로 CI/CD를 구성하고,
JMeter로 부하 테스트를 실행하고,
HTML Report와 InfluxDB/Grafana로 결과를 관찰하며,
문제가 생겼을 때 실행 실패와 렌더링 실패와 서버 환경 문제를 분리해서 디버깅한 것
```

이 경험은 단순 부하 테스트 실습이 아니라, 실제 운영 환경에서 장애 원인을 좁혀가는 DevOps식 문제 해결 과정에 가깝다.
