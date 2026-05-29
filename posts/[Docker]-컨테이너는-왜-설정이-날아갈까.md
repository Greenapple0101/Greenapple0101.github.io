---
title: "[DOCKER] 컨테이너는 왜 설정이 날아갈까?"
source: "https://velog.io/@yorange50/DOCKER-컨테이너는-왜-설정이-날아갈까"
published: "2026-05-14T06:43:50.898Z"
tags: ""
backup_date: "2026-05-29T14:52:52.742766"
---

Docker를 쓰다 보면 이런 상황을 자주 만난다.

Nginx 컨테이너 안에 들어간다.

```bash
docker exec -it nginx bash
vi /etc/nginx/conf.d/default.conf
```

설정 파일을 수정한다.

```bash
docker restart nginx
```

처음에는 잘 되는 것처럼 보인다.

그런데 컨테이너를 지웠다가 다시 만들면?

수정한 설정이 사라진다.

이때 많은 사람들이 이렇게 생각한다.

“분명히 내가 컨테이너 안에서 수정했는데 왜 날아갔지?”

결론부터 말하면 Docker 컨테이너는 원래 그렇게 쓰라고 만든 대상이 아니기 때문이다.

컨테이너 안에서 직접 수정한 내용은 컨테이너의 임시 파일시스템에 기록된다. 컨테이너가 살아있는 동안에는 남아 있을 수 있지만, 컨테이너를 삭제하고 다시 만들면 새 이미지 기준으로 다시 생성된다. 그래서 설정을 컨테이너 안에서 직접 고치는 방식은 위험하다.

## 1. 컨테이너는 실행 중인 이미지다

Docker에서 가장 먼저 구분해야 할 것은 이미지와 컨테이너다.

이미지는 실행 설계도다.

컨테이너는 그 이미지를 실제로 실행한 인스턴스다.

예를 들어 `postgres:16` 이미지를 실행하면 PostgreSQL 컨테이너가 만들어진다. `nginx` 이미지를 실행하면 Nginx 컨테이너가 만들어진다.

이미지는 기본적으로 변하지 않는 기준점이다.

컨테이너는 그 기준점 위에서 실행된다.

즉 컨테이너 안에서 파일을 수정해도 원본 이미지가 바뀌는 것은 아니다.

## 2. 컨테이너의 휘발성

컨테이너는 언제든지 죽고, 다시 뜨고, 새로 만들어질 수 있는 존재다.

그래서 컨테이너 내부에 직접 들어가서 설정을 바꾸는 방식은 안정적인 운영 방식이 아니다.

예를 들어 Nginx 설정 파일을 컨테이너 안에서 직접 수정했다고 해보자.

```bash
docker exec -it nginx bash
vi /etc/nginx/conf.d/default.conf
```

이 수정은 “현재 실행 중인 컨테이너” 안에만 존재한다.

컨테이너를 삭제하면 이 변경사항도 같이 사라진다.

```bash
docker rm nginx
docker run nginx
```

이렇게 다시 만들면 Docker는 기존에 수정했던 컨테이너를 되살리는 것이 아니라, `nginx` 이미지에서 새 컨테이너를 만든다.

그래서 수정사항이 없다.

## 3. 재시작과 재생성은 다르다

여기서 헷갈리기 쉬운 포인트가 있다.

재시작과 재생성은 다르다.

### 재시작

```bash
docker restart nginx
```

재시작은 같은 컨테이너를 껐다가 다시 켜는 것이다.

이 경우 컨테이너 자체가 삭제된 것은 아니기 때문에, 컨테이너 내부에서 수정한 파일이 그대로 남아 있을 수 있다.

### 재생성

```bash
docker rm nginx
docker run nginx
```

또는

```bash
docker compose down
docker compose up
```

재생성은 기존 컨테이너를 지우고 새 컨테이너를 만드는 것이다.

이때는 이미지 기준으로 다시 만들어진다.

그래서 컨테이너 안에서 직접 수정한 내용은 사라진다.

즉 핵심은 이거다.

`restart`는 같은 컨테이너를 다시 켜는 것.

`recreate`는 새 컨테이너를 다시 만드는 것.

운영 환경에서는 컨테이너가 재생성될 일이 많다. 배포, 장애 복구, 스케일링, 이미지 업데이트, 서버 재부팅 이후 복구 과정에서 새 컨테이너가 뜰 수 있다.

그래서 컨테이너 내부 수정에 의존하면 안 된다.

## 4. 왜 수정사항이 사라지는가

컨테이너는 이미지 위에 얇은 쓰기 레이어를 올려서 실행된다.

이미지 레이어는 읽기 전용이다.

컨테이너가 실행되면 그 위에 쓰기 가능한 레이어가 하나 붙는다.

컨테이너 안에서 파일을 수정하면 이 쓰기 레이어에 기록된다.

하지만 이 쓰기 레이어는 해당 컨테이너에 종속된다.

컨테이너를 삭제하면 쓰기 레이어도 같이 사라진다.

그래서 설정을 컨테이너 안에서 직접 수정하면, 그 변경은 컨테이너 생명주기에 묶인다.

컨테이너가 사라지면 설정도 사라진다.

## 5. 그럼 설정은 어디에 둬야 할까?

설정 파일은 컨테이너 안에서 직접 수정하는 것이 아니라, 컨테이너 밖에 두고 주입하는 방식이 좋다.

대표적인 방법은 두 가지다.

첫 번째는 볼륨 마운트다.

두 번째는 커스텀 이미지 빌드다.

## 6. 방법 1: 볼륨으로 설정 파일 주입하기

가장 쉬운 방법은 호스트에 설정 파일을 두고, 컨테이너 안으로 연결하는 것이다.

예를 들어 내 로컬 또는 서버에 이런 구조를 만든다.

```bash
project/
  docker-compose.yml
  config/
    default.conf
```

그리고 `docker-compose.yml`에서 설정 파일을 컨테이너 안으로 마운트한다.

```yaml
services:
  nginx:
    image: nginx:latest
    container_name: my-nginx
    ports:
      - "80:80"
    volumes:
      - ./config/default.conf:/etc/nginx/conf.d/default.conf
```

이렇게 하면 컨테이너 안의 `/etc/nginx/conf.d/default.conf` 파일은 실제로는 호스트의 `./config/default.conf`를 바라보게 된다.

이제 설정을 바꾸고 싶으면 컨테이너 안에 들어갈 필요가 없다.

호스트의 파일만 수정하면 된다.

```bash
vi ./config/default.conf
docker compose restart nginx
```

이 방식의 장점은 설정이 컨테이너 안에 갇히지 않는다는 것이다.

컨테이너를 지웠다가 다시 만들어도, 설정 파일은 호스트에 남아 있다.

```bash
docker compose down
docker compose up -d
```

그래도 `./config/default.conf`가 다시 컨테이너 안으로 연결된다.

## 7. PostgreSQL 설정도 같은 원리다

PostgreSQL도 마찬가지다.

PostgreSQL 컨테이너 안에는 여러 설정 파일이 있다.

예를 들어 다음과 같은 파일들이 있다.

```text
postgresql.conf
pg_hba.conf
```

이 파일들을 컨테이너 안에서 직접 수정하면 컨테이너 재생성 시 사라질 수 있다.

그래서 설정 파일을 호스트에 두고 컨테이너 안으로 마운트할 수 있다.

예시:

```yaml
services:
  postgres:
    image: postgres:16
    container_name: my-postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: hellodb
      POSTGRES_USER: hello
      POSTGRES_PASSWORD: hello
    volumes:
      - ./postgres-data:/var/lib/postgresql/data
      - ./config/postgresql.conf:/etc/postgresql/postgresql.conf
```

여기서 중요한 점은 데이터와 설정을 구분하는 것이다.

데이터는 보통 `/var/lib/postgresql/data` 같은 위치에 저장된다.

설정 파일은 별도의 경로에 있다.

그래서 데이터 볼륨과 설정 파일 마운트를 따로 관리하는 것이 좋다.

강의 메모에서도 설정 파일을 호스트의 `./config` 같은 폴더에 두고 컨테이너 안으로 넣으면, 로컬에서 수정하고 컨테이너를 재시작하는 방식으로 관리할 수 있다고 정리되어 있다. 

## 8. 방법 2: 커스텀 이미지로 만들기

설정을 항상 포함한 이미지를 만들 수도 있다.

예를 들어 Nginx 설정 파일을 이미지 안에 넣고 싶다면 Dockerfile을 만든다.

```dockerfile
FROM nginx:latest

COPY ./config/default.conf /etc/nginx/conf.d/default.conf
```

그리고 이미지를 빌드한다.

```bash
docker build -t my-nginx:1.0 .
```

그 다음 이 이미지를 실행한다.

```bash
docker run -d -p 80:80 my-nginx:1.0
```

이 방식은 설정이 이미지 안에 포함된다.

즉 컨테이너를 새로 만들어도 같은 이미지로 만들면 동일한 설정이 들어간다.

이 방법은 단순 설정뿐 아니라 패키지 설치에도 쓸 수 있다.

예를 들어 기본 이미지에 `curl`이 없어서 매번 컨테이너 안에서 설치하고 있었다면, 그건 좋은 방식이 아니다.

```bash
apt update
apt install curl
```

이걸 컨테이너 안에서 매번 하면 컨테이너가 새로 만들어질 때마다 사라진다.

그럴 때는 Dockerfile에 넣어야 한다.

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y curl
```

이렇게 하면 `curl`이 포함된 나만의 이미지가 만들어진다.

## 9. 볼륨과 커스텀 이미지 중 뭐가 맞을까?

보통 기준은 이렇다.

설정 파일처럼 자주 바뀌고 환경별로 달라지는 것은 볼륨이나 환경변수로 빼는 것이 좋다.

애플리케이션 실행에 필요한 패키지, 라이브러리, jar 파일, 기본 설정처럼 이미지와 함께 고정되어야 하는 것은 Dockerfile로 이미지에 포함시키는 것이 좋다.

예를 들어 Spring Boot 애플리케이션이라면 보통 jar 파일은 이미지에 넣는다.

```dockerfile
FROM eclipse-temurin:21-jre

WORKDIR /app

COPY ./target/*.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
```

하지만 DB 비밀번호, 운영 환경 주소, 외부 API 키 같은 것은 이미지에 박아넣지 않는다.

이런 값은 환경변수나 별도 설정으로 주입한다.

```yaml
environment:
  SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/hellodb
  SPRING_DATASOURCE_USERNAME: hello
  SPRING_DATASOURCE_PASSWORD: hello
```

## 10. immutable infrastructure란?

여기서 immutable infrastructure라는 개념이 나온다.

직역하면 “변하지 않는 인프라”다.

전통적인 서버 운영 방식은 서버에 직접 들어가서 설정을 바꾸는 방식이었다.

```bash
ssh server
vi nginx.conf
systemctl restart nginx
```

이 방식은 당장은 편하다.

하지만 시간이 지나면 문제가 생긴다.

누가 어떤 설정을 바꿨는지 추적하기 어렵다.

서버마다 설정이 조금씩 달라진다.

장애가 났을 때 같은 환경을 다시 만들기 어렵다.

immutable infrastructure는 반대로 생각한다.

서버나 컨테이너에 직접 들어가서 수정하지 않는다.

수정이 필요하면 코드, 설정 파일, Dockerfile, compose 파일을 바꾼다.

그 다음 새 이미지나 새 컨테이너를 만든다.

즉 인프라를 직접 고치는 것이 아니라, 선언된 파일을 기준으로 다시 만든다.

이 방식에서는 컨테이너가 일회용에 가깝다.

컨테이너 안에 들어가서 고치는 것이 아니라, 컨테이너 밖의 정의를 고친다.

## 11. 왜 이 방식이 중요한가?

컨테이너를 운영할 때 중요한 것은 “지금 이 컨테이너가 어떻게 생겼는가”가 아니다.

중요한 것은 “이 컨테이너를 언제든 다시 만들 수 있는가”다.

운영 환경에서는 컨테이너가 죽을 수 있다.

서버가 재부팅될 수 있다.

새 버전으로 배포될 수 있다.

스케일 아웃으로 컨테이너가 여러 개 생길 수 있다.

이때 컨테이너 안에서 손으로 수정한 설정에 의존하면 같은 환경을 재현할 수 없다.

A 컨테이너는 수정되어 있고, B 컨테이너는 수정되지 않은 상태가 될 수도 있다.

그래서 Docker에서는 이런 마인드가 중요하다.

컨테이너 안에서 직접 고치지 않는다.

고칠 내용은 Dockerfile, docker-compose.yml, config 파일, env 파일에 남긴다.

컨테이너는 언제든 지우고 다시 만들 수 있어야 한다.

## 12. 정리

컨테이너 안에서 수정한 설정이 사라지는 이유는 컨테이너가 이미지 위에 임시 쓰기 레이어를 붙여 실행되기 때문이다.

재시작은 같은 컨테이너를 다시 켜는 것이므로 수정사항이 남아 있을 수 있다.

하지만 재생성은 기존 컨테이너를 삭제하고 이미지에서 새 컨테이너를 만드는 것이므로 컨테이너 내부 수정사항이 사라진다.

그래서 설정 파일은 컨테이너 안에서 직접 수정하지 않는 것이 좋다.

자주 바뀌는 설정은 볼륨으로 호스트에서 주입한다.

이미지에 포함되어야 하는 파일이나 패키지는 Dockerfile로 커스텀 이미지를 만든다.

이런 방식이 Docker에서 말하는 immutable infrastructure에 가깝다.

컨테이너는 손으로 고쳐서 오래 쓰는 서버가 아니다.

언제든 버리고 다시 만들 수 있어야 하는 실행 단위다.
