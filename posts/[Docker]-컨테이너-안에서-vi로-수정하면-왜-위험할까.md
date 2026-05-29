---
title: "[DOCKER] 컨테이너 안에서 vi로 수정하면 왜 위험할까?"
source: "https://velog.io/@yorange50/DOCKER-컨테이너-안에서-vi로-수정하면-왜-위험할까"
published: "2026-05-14T07:15:00.894Z"
tags: ""
backup_date: "2026-05-29T14:52:52.742092"
---

Docker를 처음 쓰다 보면 이런 생각을 하게 된다.

“컨테이너 안에 들어가서 설정 파일을 직접 고치면 되는 거 아닌가?”

예를 들어 Nginx 컨테이너가 떠 있고, 그 안에 `nginx.conf`나 `server.conf` 같은 설정 파일이 있다고 해보자.

```bash
docker exec -it nginx-container bash
vi /etc/nginx/conf.d/server.conf
```

이렇게 컨테이너 안으로 들어가서 직접 설정을 바꾼다.

겉으로 보면 잘 동작한다.
설정도 바뀌고, Nginx를 재시작하면 반영도 된다.

그런데 운영 환경에서는 이 방식이 꽤 위험하다.

---

## 1. 컨테이너 안에서 직접 수정하는 방식

컨테이너는 하나의 작은 서버처럼 보인다.

안에 Linux 파일 시스템도 있고, 설정 파일도 있고, 프로세스도 실행된다.

그래서 다음처럼 직접 들어갈 수 있다.

```bash
docker exec -it my-nginx bash
```

그리고 안에서 파일을 수정할 수도 있다.

```bash
vi /etc/nginx/conf.d/default.conf
```

문제는 여기서부터다.

이 수정은 **컨테이너 내부 파일 시스템에만 반영된 임시 변경사항**이다.

즉, 내가 수정한 내용이 Dockerfile에 남는 것도 아니고, docker-compose.yml에 남는 것도 아니고, Git에 남는 것도 아니다.

그냥 “현재 살아 있는 컨테이너 안”에만 존재한다.

---

## 2. 컨테이너는 영구 서버가 아니다

전통적인 서버 운영 방식에서는 서버에 직접 접속해서 설정 파일을 고쳤다.

```bash
ssh server
vi /etc/nginx/nginx.conf
systemctl restart nginx
```

이 방식은 서버 자체가 오래 유지된다는 전제가 있다.

하지만 Docker 컨테이너는 다르다.

컨테이너는 언제든지 삭제되고, 다시 생성될 수 있다.

```bash
docker rm my-nginx
docker compose up -d
```

이렇게 컨테이너를 다시 만들면, 이전 컨테이너 안에서 수정했던 내용은 사라질 수 있다.

왜냐하면 새 컨테이너는 기존 컨테이너를 복구하는 게 아니라, **이미지로부터 새로 생성되는 실행 단위**이기 때문이다.

수업 메모에서도 “컨테이너 안에 들어가서 vi로 수정하면 되지만, 컨테이너가 재시작되거나 재생성되면 설정했던 게 날아갈 수 있다”는 흐름으로 정리되어 있다. 

---

## 3. 재시작과 재생성은 다르다

여기서 헷갈리기 쉬운 게 있다.

`restart`와 `recreate`는 다르다.

---

## 컨테이너 재시작

```bash
docker restart my-nginx
```

재시작은 기존 컨테이너를 껐다가 다시 켜는 것이다.

이 경우에는 컨테이너 내부에서 수정한 파일이 남아 있을 수도 있다.

그래서 처음에는 이렇게 착각한다.

“어? 재시작해도 안 날아가는데?”

맞다. 단순 restart에서는 남을 수 있다.

---

## 컨테이너 재생성

```bash
docker compose down
docker compose up -d
```

또는

```bash
docker rm my-nginx
docker run ...
```

이 경우에는 기존 컨테이너를 버리고 새 컨테이너를 만든다.

그러면 컨테이너 안에서 직접 수정한 설정은 사라진다.

Docker 운영에서 진짜 위험한 지점은 바로 여기다.

운영 환경에서는 컨테이너가 단순히 재시작만 되는 게 아니라, 배포 과정에서 자주 새로 만들어진다.

이미지를 새로 빌드하거나, compose를 다시 올리거나, 서버를 이전하거나, 장애 복구를 하면 컨테이너는 다시 생성될 수 있다.

그때 컨테이너 안에서 vi로 고친 설정은 추적되지 않는다.

---

## 4. 직접 수정 방식의 가장 큰 문제

컨테이너 안에서 직접 수정하는 방식의 문제는 단순히 “날아갈 수 있다”가 아니다.

진짜 문제는 다음이다.

```text
누가
언제
무엇을
왜
어떻게
수정했는지
남지 않는다
```

운영 환경에서는 이게 치명적이다.

예를 들어 장애가 발생했다고 해보자.

Nginx 설정이 이상하다.

그런데 누군가 예전에 컨테이너 안에 들어가서 직접 수정해둔 상태였다.

Git에는 기록이 없다.
Dockerfile에도 없다.
docker-compose.yml에도 없다.
README에도 없다.
로컬 설정 파일에도 없다.

그럼 원인 추적이 어려워진다.

이런 상태를 흔히 “눈송이 서버”처럼 본다.

서버마다 직접 손으로 만져서 상태가 제각각인 상황이다.

Docker를 쓰는 이유는 환경을 일관되게 만들기 위해서인데, 컨테이너 안에서 직접 수정하면 다시 예전 서버 운영 방식으로 돌아가는 셈이다.

---

## 5. 운영 환경에서 왜 더 위험할까?

개발 환경에서는 컨테이너 안에서 잠깐 수정해볼 수 있다.

테스트 목적이라면 괜찮다.

하지만 운영 환경에서는 다르다.

운영 환경에서는 다음 상황이 자주 발생한다.

```text
이미지 재빌드
컨테이너 재배포
docker compose down/up
서버 장애 복구
스케일 아웃
다른 서버로 이전
CI/CD 자동 배포
```

이때 설정이 코드나 파일로 관리되고 있지 않으면 같은 환경을 다시 만들 수 없다.

예를 들어 운영 Nginx 설정을 컨테이너 안에서 직접 고쳤다고 해보자.

현재는 잘 돌아간다.

그런데 다음 배포 때 컨테이너가 새로 만들어진다.

그러면 이전에 고친 설정이 사라진다.

결과적으로 이런 문제가 생길 수 있다.

```text
갑자기 리버스 프록시 설정이 사라짐
CORS 설정이 원래대로 돌아감
업로드 용량 제한 설정이 사라짐
SSL 관련 설정이 누락됨
DB 설정 파일이 초기 상태로 돌아감
운영에서는 되던 게 재배포 후 안 됨
```

가장 무서운 건, 이 문제가 “배포 이후 갑자기” 나타난다는 점이다.

---

## 6. Docker에서는 설정을 어디서 관리해야 할까?

Docker에서는 컨테이너 안에서 직접 설정을 고치는 대신, 설정을 컨테이너 밖에서 관리하는 게 좋다.

대표적인 방식은 세 가지다.

```text
1. 호스트 파일을 컨테이너에 bind mount
2. Docker volume 사용
3. 커스텀 이미지로 설정 파일 포함
```

---

## 7. 방법 1: 호스트에서 설정 파일 관리하기

가장 이해하기 쉬운 방식은 호스트에 설정 파일을 두고, 컨테이너 안으로 연결하는 것이다.

예를 들어 프로젝트 구조를 이렇게 만든다.

```text
my-nginx/
├── docker-compose.yml
└── config/
    └── server.conf
```

그리고 `docker-compose.yml`에서 이 파일을 컨테이너 안으로 넣는다.

```yaml
services:
  nginx:
    image: nginx:latest
    container_name: my-nginx
    ports:
      - "80:80"
    volumes:
      - ./config/server.conf:/etc/nginx/conf.d/default.conf
```

이렇게 하면 컨테이너 안의 설정 파일을 직접 수정하는 게 아니라, 호스트의 `./config/server.conf`를 수정하면 된다.

```bash
vi ./config/server.conf
docker compose restart nginx
```

이 방식의 장점은 명확하다.

```text
설정 파일이 프로젝트 폴더에 남음
Git으로 관리 가능
누가 수정했는지 추적 가능
컨테이너를 다시 만들어도 설정 유지
다른 서버에서도 같은 설정 재현 가능
```

즉, 설정을 컨테이너 내부가 아니라 외부에서 관리하게 된다.

수업 메모에서도 `./config` 같은 호스트 폴더를 만들고, 그 안의 설정 파일을 컨테이너 안으로 넣어서 동기화하는 흐름이 언급되어 있다. 

---

## 8. 방법 2: Docker volume 사용하기

데이터나 설정을 컨테이너 생명주기와 분리하고 싶을 때는 volume을 쓴다.

예를 들어 PostgreSQL 데이터는 컨테이너 안에만 두면 안 된다.

컨테이너가 삭제되면 DB 데이터도 사라질 수 있기 때문이다.

그래서 보통 이렇게 한다.

```yaml
services:
  postgres:
    image: postgres:16
    container_name: my-postgres
    environment:
      POSTGRES_DB: hellodb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

여기서 핵심은 이것이다.

```text
컨테이너는 삭제되어도
volume은 별도로 남는다
```

DB 데이터처럼 중요한 것은 반드시 컨테이너와 분리해야 한다.

설정 파일도 필요에 따라 volume이나 bind mount로 분리할 수 있다.

다만 설정 파일처럼 사람이 직접 수정하고 Git으로 관리해야 하는 파일은 보통 named volume보다는 bind mount가 더 직관적이다.

---

## 9. 방법 3: 커스텀 이미지 만들기

설정 파일을 아예 이미지 안에 포함시키는 방법도 있다.

예를 들어 Nginx 설정을 포함한 이미지를 직접 만들 수 있다.

```dockerfile
FROM nginx:latest

COPY ./config/server.conf /etc/nginx/conf.d/default.conf
```

그리고 빌드한다.

```bash
docker build -t my-nginx:1.0 .
```

이 방식은 “설정까지 포함된 이미지”를 만드는 것이다.

장점은 배포할 때 이미지 하나만 있으면 같은 환경을 만들 수 있다는 점이다.

단점은 설정이 바뀔 때마다 이미지를 다시 빌드해야 한다는 점이다.

그래서 자주 바뀌는 설정은 bind mount로 빼고, 이미지에 고정해도 되는 설정이나 라이브러리는 Dockerfile에 포함시키는 식으로 나눌 수 있다.

예를 들어 컨테이너 안에 `curl` 같은 패키지를 추가해야 한다면 직접 컨테이너에 들어가서 설치하는 게 아니라 Dockerfile에 적어야 한다.

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y curl
```

이렇게 해야 다음에 이미지를 다시 만들어도 같은 환경이 유지된다.

수업 메모에서도 설정 파일은 volume으로 관리할 수 있고, 필요한 라이브러리나 도구가 있다면 Dockerfile로 커스텀 이미지를 만드는 방식까지 생각해야 한다는 흐름이 나온다. 

---

## 10. 컨테이너 안에서 vi 수정이 완전히 금지인가?

완전히 금지는 아니다.

개발 중에 빠르게 확인할 때는 할 수 있다.

예를 들어 이런 경우다.

```text
설정 경로가 맞는지 확인
임시로 값 바꿔서 테스트
컨테이너 내부 파일 구조 확인
긴급 디버깅
```

하지만 이 수정은 운영 반영 방식이 되면 안 된다.

컨테이너 안에서 직접 고쳐서 문제가 해결됐다면, 그 다음에는 반드시 외부 설정 파일이나 Dockerfile, compose 파일에 반영해야 한다.

즉, 컨테이너 안에서 vi로 고친 것은 “최종 수정”이 아니라 “임시 실험”이어야 한다.

---

## 11. 좋은 운영 방식

좋은 방식은 다음 흐름이다.

```text
1. 설정 파일을 호스트 프로젝트 폴더에 둔다
2. docker-compose.yml에서 컨테이너 내부 경로로 mount한다
3. 설정 변경은 호스트 파일에서 한다
4. Git으로 변경 이력을 관리한다
5. 컨테이너는 언제든지 지우고 다시 만들 수 있게 한다
```

예시는 다음과 같다.

```text
project/
├── docker-compose.yml
├── config/
│   └── nginx.conf
└── README.md
```

```yaml
services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf:ro
```

여기서 `:ro`는 read-only라는 뜻이다.

```yaml
./config/nginx.conf:/etc/nginx/nginx.conf:ro
```

즉, 컨테이너 안에서는 이 파일을 읽기만 하고 수정하지 못하게 하는 것이다.

운영에서는 오히려 이런 방식이 더 안전하다.

컨테이너 안에서 직접 수정하지 못하게 막고, 반드시 호스트 파일이나 Git을 통해 변경하게 만드는 것이다.

---

## 12. 핵심 정리

컨테이너 안에서 `vi`로 설정 파일을 수정하는 것은 빠르고 쉬워 보인다.

하지만 운영 관점에서는 위험하다.

이유는 간단하다.

```text
컨테이너는 영구 서버가 아니기 때문이다
```

컨테이너는 이미지로부터 만들어지는 실행 단위다.

언제든지 삭제되고 다시 생성될 수 있다.

따라서 컨테이너 안에서 직접 수정한 설정은 재배포 과정에서 사라질 수 있다.

운영에서는 설정을 컨테이너 밖에서 관리해야 한다.

```text
Nginx 설정 → 호스트 config 폴더에서 관리
PostgreSQL 데이터 → volume으로 관리
필요한 패키지 설치 → Dockerfile에 작성
환경 변수 → docker-compose.yml 또는 .env에서 관리
```

Docker의 핵심은 “지금 떠 있는 컨테이너를 소중히 보존하는 것”이 아니다.

언제든지 지우고 다시 만들어도 같은 환경이 재현되도록 만드는 것이다.

그래서 컨테이너 안에서 직접 수정하는 방식은 Docker답지 않은 운영 방식이다.

Docker에서는 컨테이너를 고치는 게 아니라, 컨테이너를 만드는 기준을 고쳐야 한다.

그 기준이 바로 Dockerfile, docker-compose.yml, volume, config 파일이다.
