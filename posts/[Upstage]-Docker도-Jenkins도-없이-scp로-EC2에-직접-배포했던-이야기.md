---
title: "[DEPLOY] Docker도 Jenkins도 없이 scp로 EC2에 직접 배포했던 이야기"
source: "https://velog.io/@yorange50/DEPLOY-Docker도-Jenkins도-없이-scp로-EC2에-직접-배포했던-이야기"
published: "2026-05-17T09:53:06.866Z"
tags: ""
backup_date: "2026-05-29T14:52:52.737007"
---

1. scp 배포란?

`scp`는 Secure Copy의 줄임말이다. SSH를 기반으로 로컬 파일을 원격 서버에 안전하게 복사하는 명령어다. 쉽게 말하면 내 노트북에서 만든 파일을 EC2 서버로 보내는 방식이다.

```bash
scp -i key.pem app.jar ubuntu@EC2_PUBLIC_IP:/home/ubuntu/app/
```

이 명령어는 로컬에 있는 `app.jar` 파일을 EC2 서버의 `/home/ubuntu/app/` 디렉토리로 복사한다. Docker 이미지를 만들거나 Jenkins 파이프라인을 구성하는 것이 아니라, **빌드된 결과물을 서버에 직접 올리는 방식**이다.

## 2. 전체 배포 구조

scp로 모든 것을 배포했다는 가정하에 구조는 다음과 같다.

```text
개발자 로컬 PC
├─ 소스코드 수정
├─ 로컬에서 빌드
├─ 빌드 산출물 생성
└─ scp로 EC2에 전송

EC2 서버
├─ 애플리케이션 직접 실행
├─ MySQL 직접 설치
├─ Nginx 직접 설치
└─ 필요한 설정 파일 직접 수정
```

즉, 서버 안에서 Docker 컨테이너들이 떠 있는 구조가 아니라 EC2 서버 자체가 실행 환경이 된다.

```text
사용자
→ EC2 Public IP 또는 도메인
→ Nginx
→ 애플리케이션 프로세스
→ MySQL
```

이 구조에서는 EC2가 웹서버, 애플리케이션 서버, DB 서버 역할을 모두 맡는다.

## 3. 로컬에서 빌드하기

Spring Boot 프로젝트라면 먼저 로컬에서 빌드를 수행한다.

```bash
./gradlew clean build
```

또는 Maven 프로젝트라면 다음과 같이 빌드한다.

```bash
mvn clean package
```

빌드가 성공하면 보통 다음 위치에 jar 파일이 생성된다.

```text
build/libs/app.jar
```

이 jar 파일이 서버에서 실행할 실제 애플리케이션 산출물이다.

프론트엔드 프로젝트라면 다음처럼 빌드했을 수 있다.

```bash
npm install
npm run build
```

그러면 보통 `dist` 또는 `build` 디렉토리가 생성된다.

```text
dist/
├─ index.html
├─ assets/
└─ ...
```

이 파일들은 Nginx가 정적 파일로 서빙할 수 있다.

## 4. scp로 백엔드 배포하기

백엔드 jar 파일을 EC2로 보낸다.

```bash
scp -i key.pem build/libs/app.jar ubuntu@EC2_PUBLIC_IP:/home/ubuntu/app/app.jar
```

그다음 EC2에 접속한다.

```bash
ssh -i key.pem ubuntu@EC2_PUBLIC_IP
```

서버에서 애플리케이션을 실행한다.

```bash
cd /home/ubuntu/app
java -jar app.jar
```

이렇게 하면 Spring Boot 애플리케이션이 EC2 서버 위에서 직접 실행된다.

만약 기본 포트가 8080이라면 다음 주소로 접속할 수 있다.

```text
http://EC2_PUBLIC_IP:8080
```

이 방식은 단순하다. Dockerfile도 필요 없고, 이미지 빌드도 필요 없고, 컨테이너 네트워크도 고려하지 않아도 된다. 하지만 대신 서버에 Java가 직접 설치되어 있어야 한다.

```bash
java -version
```

서버에 Java가 없다면 직접 설치해야 한다.

```bash
sudo apt update
sudo apt install openjdk-17-jdk
```

## 5. scp로 프론트엔드 배포하기

프론트엔드 빌드 결과물도 scp로 보낼 수 있다.

```bash
scp -i key.pem -r dist/* ubuntu@EC2_PUBLIC_IP:/var/www/html/
```

이 경우 `/var/www/html/`은 Nginx가 기본적으로 정적 파일을 서빙하는 디렉토리다.

즉, 사용자가 EC2 IP로 접속하면 Nginx가 `/var/www/html/index.html`을 응답한다.

```text
사용자
→ http://EC2_PUBLIC_IP
→ Nginx
→ /var/www/html/index.html
```

이 구조에서는 프론트엔드 파일을 매번 새로 빌드하고, scp로 서버에 덮어씌우는 식으로 배포한다.

## 6. Nginx도 서버에 직접 설치하기

scp 기반 수동 배포에서는 Nginx도 Docker 컨테이너가 아니라 EC2에 직접 설치했을 가능성이 높다.

```bash
sudo apt update
sudo apt install nginx
```

Nginx 실행 상태를 확인한다.

```bash
sudo systemctl status nginx
```

Nginx를 시작하거나 재시작할 때는 다음 명령어를 사용한다.

```bash
sudo systemctl start nginx
sudo systemctl restart nginx
```

서버가 재부팅되어도 자동으로 실행되게 하려면 다음 명령어를 사용할 수 있다.

```bash
sudo systemctl enable nginx
```

Nginx 설정 파일은 보통 아래 경로에 있다.

```text
/etc/nginx/nginx.conf
/etc/nginx/sites-available/default
/etc/nginx/sites-enabled/default
```

프론트 정적 파일만 서빙한다면 기본 설정으로도 어느 정도 동작할 수 있다. 하지만 백엔드 API 서버로 요청을 넘기려면 reverse proxy 설정이 필요하다.

예를 들어 Spring Boot 서버가 8080 포트에서 실행 중이라면 Nginx 설정은 이런 식이 될 수 있다.

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

이렇게 하면 사용자는 `http://EC2_PUBLIC_IP`로 접속하지만, 실제 요청은 내부적으로 `localhost:8080`의 애플리케이션으로 전달된다.

```text
사용자
→ EC2:80
→ Nginx
→ localhost:8080
→ Spring Boot
```

Nginx를 쓰는 이유는 단순히 “웹서버라서”가 아니다. 사용자가 8080 같은 포트를 직접 입력하지 않게 하고, 80번 포트로 들어온 요청을 애플리케이션 서버에 넘겨주기 위해서다.

## 7. MySQL도 EC2에 직접 설치하기

이 구조에서는 MySQL도 컨테이너가 아니라 EC2에 직접 설치한다.

```bash
sudo apt update
sudo apt install mysql-server
```

MySQL 실행 상태를 확인한다.

```bash
sudo systemctl status mysql
```

MySQL을 시작하고 자동 실행되도록 설정한다.

```bash
sudo systemctl start mysql
sudo systemctl enable mysql
```

MySQL에 접속한다.

```bash
sudo mysql
```

데이터베이스와 계정을 생성한다.

```sql
CREATE DATABASE appdb;

CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'password';

GRANT ALL PRIVILEGES ON appdb.* TO 'appuser'@'localhost';

FLUSH PRIVILEGES;
```

애플리케이션 설정은 이런 식이 된다.

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/appdb
spring.datasource.username=appuser
spring.datasource.password=password
```

여기서 중요한 점은 `localhost`다. 애플리케이션도 EC2에서 직접 실행되고, MySQL도 같은 EC2에 직접 설치되어 있으므로 `localhost:3306`으로 연결할 수 있다.

하지만 나중에 애플리케이션을 Docker 컨테이너로 올리면 이 설정이 그대로 동작하지 않을 수 있다. 컨테이너 안에서 `localhost`는 EC2 서버가 아니라 컨테이너 자기 자신을 의미하기 때문이다.

그래서 scp 직접 배포에서는 잘 되던 DB 연결이 Docker 전환 과정에서 깨지는 경우가 많다.

## 8. 실제 배포 흐름 정리

scp 기반 배포 흐름을 순서대로 정리하면 다음과 같다.

```text
1. 로컬에서 코드 수정
2. 로컬에서 빌드
3. jar 또는 dist 산출물 생성
4. scp로 EC2에 전송
5. EC2 접속
6. 기존 프로세스 종료
7. 새 산출물 실행
8. Nginx 재시작
9. 접속 확인
```

명령어로 보면 다음과 같다.

```bash
./gradlew clean build
```

```bash
scp -i key.pem build/libs/app.jar ubuntu@EC2_PUBLIC_IP:/home/ubuntu/app/app.jar
```

```bash
ssh -i key.pem ubuntu@EC2_PUBLIC_IP
```

```bash
ps -ef | grep java
kill -9 <PID>
```

```bash
cd /home/ubuntu/app
nohup java -jar app.jar > app.log 2>&1 &
```

```bash
sudo systemctl restart nginx
```

```bash
curl http://localhost:8080
curl http://EC2_PUBLIC_IP
```

여기서 `nohup`을 쓰는 이유는 SSH 접속을 끊어도 애플리케이션이 계속 실행되게 하기 위해서다.

```bash
nohup java -jar app.jar > app.log 2>&1 &
```

이 명령어는 애플리케이션을 백그라운드에서 실행하고, 로그를 `app.log` 파일에 남긴다.

## 9. 이 방식의 장점

scp 기반 배포의 가장 큰 장점은 단순함이다.

```text
Jenkins 설정이 필요 없다
Dockerfile이 없어도 된다
Docker Compose 네트워크를 고민하지 않아도 된다
서버에 바로 올려서 실행할 수 있다
문제가 생겼을 때 로그를 바로 확인하기 쉽다
```

대회나 마감이 가까운 상황에서는 “완벽한 구조”보다 “일단 동작하는 구조”가 더 중요할 때가 있다.

이때 scp 배포는 현실적인 선택이 될 수 있다.

특히 초반에는 배포 자동화보다 다음을 먼저 이해하는 게 중요하다.

```text
애플리케이션이 어떤 포트에서 뜨는지
서버에서 프로세스가 어떻게 실행되는지
Nginx가 어떤 요청을 어디로 넘기는지
DB 연결 문자열이 어떻게 구성되는지
보안 그룹에서 어떤 포트를 열어야 하는지
```

scp 배포는 이런 기본 구조를 직접 체감하게 해준다.

## 10. 이 방식의 한계

하지만 scp 기반 배포는 명확한 한계가 있다.

첫 번째, 배포가 사람 손에 의존한다.

```text
빌드 명령어 직접 실행
scp 명령어 직접 실행
서버 접속 직접 수행
기존 프로세스 직접 종료
새 프로세스 직접 실행
```

이 과정에서 실수할 가능성이 높다.

두 번째, 배포 이력이 체계적으로 남지 않는다.

Jenkins나 GitHub Actions를 쓰면 어떤 커밋이 언제 배포되었는지 기록이 남는다. 하지만 scp 배포는 사람이 직접 파일을 덮어쓰기 때문에 추적이 어렵다.

세 번째, 서버 환경에 강하게 의존한다.

서버에 Java가 설치되어 있어야 하고, MySQL도 설치되어 있어야 하고, Nginx 설정도 직접 맞아 있어야 한다. 다른 서버로 옮기려면 같은 환경을 다시 손으로 만들어야 한다.

네 번째, 롤백이 어렵다.

이전 jar 파일을 따로 백업해두지 않았다면 문제가 생겼을 때 바로 이전 버전으로 되돌리기 어렵다.

다섯 번째, 운영 안정성이 떨어진다.

`nohup`으로 실행한 프로세스는 죽었을 때 자동으로 다시 살아나지 않는다. 운영 환경에서는 보통 systemd, Docker restart policy, Kubernetes 같은 방식으로 프로세스를 관리한다.

## 11. 그래서 Docker와 Jenkins가 필요한 이유

scp 배포를 해보면 오히려 Docker와 Jenkins가 왜 필요한지 이해하게 된다.

Docker는 실행 환경을 이미지로 고정한다.

```text
어떤 Java 버전을 쓰는지
어떤 파일을 포함하는지
어떤 포트로 실행하는지
어떤 명령어로 시작하는지
```

이런 내용을 Dockerfile에 기록할 수 있다.

Jenkins는 배포 절차를 자동화한다.

```text
Git pull
빌드
테스트
산출물 생성
서버 전송
실행
검증
```

사람이 매번 하던 일을 파이프라인으로 만들 수 있다.

즉, scp 배포는 나쁜 방식이라기보다 **자동화 이전 단계의 수동 배포 방식**이다. 이 방식을 겪어보면 왜 CI/CD가 필요한지 더 잘 이해할 수 있다.

## 12. 포트폴리오에 쓴다면

이 경험은 과장하지 않고 쓰는 게 중요하다. “Jenkins 기반 자동 배포를 완성했다”라고 쓰면 실제 경험과 다를 수 있다. 대신 이렇게 쓰는 게 좋다.

```text
초기에는 Jenkins 기반 자동 배포를 시도했으나, 일정과 설정 복잡도로 인해 최종 제출 시점에는 scp 기반 수동 배포 방식으로 전환했습니다. 로컬에서 빌드한 산출물을 EC2로 전송하고 서버에서 직접 실행했으며, Nginx와 MySQL도 EC2에 직접 설치하여 애플리케이션과 연결했습니다. 이 과정에서 수동 배포의 한계와 서버 환경 의존성을 체감했고, 이후 Docker와 CI/CD 기반 배포 구조의 필요성을 이해하게 되었습니다.
```

면접에서는 이렇게 말할 수 있다.

```text
이 프로젝트는 완성된 CI/CD 자동화 프로젝트라기보다는, EC2 서버에 직접 배포하면서 배포 구조를 익힌 경험에 가깝습니다. 처음에는 Jenkins 배포를 시도했지만 일정상 최종적으로는 scp로 산출물을 전송하고 서버에서 직접 실행했습니다. MySQL과 Nginx도 EC2에 직접 설치해 사용했고, 이 과정에서 수동 배포가 왜 반복성과 재현성 측면에서 한계가 있는지 체감했습니다.
```

이렇게 말하면 솔직하고 좋다. 오히려 어디까지 했고 어디까지 못 했는지 정확히 아는 사람처럼 보인다.

## 13. 정리

scp 기반 배포는 가장 화려한 방식은 아니다. Docker Compose나 Kubernetes, Jenkins 같은 자동화 도구를 사용한 것도 아니다. 하지만 서버 배포의 기본 구조를 이해하는 데는 매우 좋은 경험이다.

이 방식에서는 로컬에서 빌드한 산출물을 EC2로 직접 전송하고, 서버에서 직접 애플리케이션을 실행한다. MySQL과 Nginx도 EC2에 직접 설치해서 사용한다.

전체 흐름은 다음과 같다.

```text
로컬 빌드
→ scp 전송
→ EC2 접속
→ 기존 프로세스 종료
→ 새 애플리케이션 실행
→ Nginx 연결
→ MySQL 연결
→ 접속 확인
```

이 방식의 핵심은 단순하다.

```text
서버에 직접 올리고 직접 실행한다.
```

하지만 이 단순함 때문에 수동 작업이 많고, 재현성이 낮고, 실수 가능성이 높다. 그래서 이 경험을 통해 Docker와 Jenkins의 필요성을 더 명확히 이해할 수 있었다.

결국 이 트러블슈팅과 배포 경험은 이렇게 정리할 수 있다.

```text
scp 기반 수동 배포를 통해 EC2 서버에서 애플리케이션, Nginx, MySQL이 어떻게 연결되는지 직접 경험했고, 이후 컨테이너화와 CI/CD 자동화가 필요한 이유를 체감했다.
```