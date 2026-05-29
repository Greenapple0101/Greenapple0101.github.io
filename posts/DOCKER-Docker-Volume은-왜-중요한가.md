---
title: "[DOCKER] Docker Volume은 왜 중요한가?"
source: "https://velog.io/@yorange50/DOCKER-Docker-Volume은-왜-중요한가"
published: "2026-05-14T07:01:57.426Z"
tags: ""
backup_date: "2026-05-29T14:52:52.742449"
---

Docker를 쓰다 보면 처음에는 이런 식으로 생각하기 쉽다.

“컨테이너 안에 PostgreSQL이 떠 있으니까 데이터도 컨테이너 안에 있겠지?”

맞다.

그런데 문제는 컨테이너가 영구적인 존재가 아니라는 점이다.

컨테이너는 언제든지 꺼질 수 있고, 삭제될 수 있고, 다시 만들어질 수 있다.

그래서 컨테이너 안에만 데이터를 저장하면 컨테이너를 지우는 순간 데이터도 같이 사라질 수 있다.

이 문제를 해결하기 위해 Docker에서 아주 중요한 개념이 나온다.

바로 Volume이다.

## 1. Volume이란?

Volume은 컨테이너 밖에 데이터를 저장하기 위한 공간이다.

컨테이너는 휘발적이다.

하지만 데이터는 휘발되면 안 된다.

예를 들어 PostgreSQL 컨테이너를 띄웠다고 해보자.

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
```

이 상태로 PostgreSQL을 실행하면 DB는 잘 뜬다.

DBeaver로 접속도 된다.

테이블도 만들 수 있다.

데이터도 insert할 수 있다.

그런데 컨테이너를 삭제하면?

```bash
docker rm my-postgres
```

컨테이너 내부에만 있던 데이터는 사라질 수 있다.

그래서 데이터 저장 위치를 컨테이너 바깥으로 빼야 한다.

그 역할을 하는 것이 Volume이다.

## 2. 컨테이너 안의 데이터는 왜 위험할까?

컨테이너는 이미지로부터 만들어진 실행 단위다.

이미지는 변하지 않는 기준이고, 컨테이너는 그 이미지를 실행한 결과다.

컨테이너 안에서 생기는 파일 변경사항은 해당 컨테이너에 묶인다.

즉 컨테이너를 삭제하면 그 안에 있던 변경사항도 같이 사라진다.

PostgreSQL 입장에서 보면 데이터베이스 파일은 보통 컨테이너 내부의 특정 디렉터리에 저장된다.

대표적으로 PostgreSQL 공식 이미지는 데이터를 아래 경로에 저장한다.

```text
/var/lib/postgresql/data
```

이 경로가 컨테이너 안에만 있으면 컨테이너 생명주기에 데이터가 묶인다.

그래서 컨테이너를 다시 만들면 DB도 초기화된 것처럼 보일 수 있다.

## 3. Volume을 쓰면 뭐가 달라질까?

Volume을 쓰면 컨테이너 내부 경로와 컨테이너 외부 저장공간을 연결할 수 있다.

예를 들어 이렇게 쓴다.

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
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```

여기서 핵심은 이 부분이다.

```yaml
volumes:
  - postgres-data:/var/lib/postgresql/data
```

뜻은 이렇다.

`postgres-data`라는 Docker Volume을 만들고, 그걸 컨테이너 안의 `/var/lib/postgresql/data`에 연결한다.

이제 PostgreSQL이 데이터를 `/var/lib/postgresql/data`에 저장하면, 실제 데이터는 Docker가 관리하는 Volume에 저장된다.

컨테이너를 삭제했다가 다시 만들어도 같은 Volume을 연결하면 데이터가 남아 있다.

## 4. Host ↔ Container 동기화

Docker에서 Volume을 이해하려면 Host와 Container의 관계를 봐야 한다.

Host는 내 컴퓨터 또는 서버다.

Container는 Host 위에서 격리되어 실행되는 작은 실행 환경이다.

기본적으로 컨테이너는 자기만의 파일시스템을 가진다.

그래서 Host의 파일과 Container의 파일은 자동으로 같은 것이 아니다.

하지만 mount를 걸면 Host와 Container 사이에 특정 경로를 연결할 수 있다.

예를 들어 아래처럼 작성할 수 있다.

```yaml
volumes:
  - ./config/nginx.conf:/etc/nginx/nginx.conf
```

이 뜻은 이렇다.

Host의 `./config/nginx.conf` 파일을 Container의 `/etc/nginx/nginx.conf` 위치에 연결한다.

그러면 Host에서 파일을 수정하면 Container 안에서도 그 변경이 반영된다.

즉 컨테이너 안에 들어가서 `vi`로 직접 수정할 필요가 없다.

Host에서 설정 파일을 관리하고, 컨테이너는 그 파일을 가져다 쓰게 만들면 된다.

이게 Host ↔ Container 동기화의 핵심이다.

## 5. bind mount란?

bind mount는 Host의 특정 파일이나 디렉터리를 Container 안으로 직접 연결하는 방식이다.

예를 들어 현재 프로젝트 폴더에 `config` 디렉터리가 있다고 하자.

```text
my-project/
  docker-compose.yml
  config/
    postgresql.conf
```

그리고 compose 파일에 이렇게 쓴다.

```yaml
services:
  postgres:
    image: postgres:16
    volumes:
      - ./config/postgresql.conf:/etc/postgresql/postgresql.conf
```

이것이 bind mount다.

왼쪽은 Host 경로다.

```text
./config/postgresql.conf
```

오른쪽은 Container 경로다.

```text
/etc/postgresql/postgresql.conf
```

즉 Host에 있는 설정 파일을 Container 안의 특정 위치에 그대로 꽂아 넣는 것이다.

bind mount는 개발 환경에서 많이 쓴다.

이유는 간단하다.

Host에서 파일을 바로 수정할 수 있기 때문이다.

설정 파일을 바꾸고 컨테이너를 재시작하면 된다.

```bash
docker compose restart postgres
```

## 6. Docker Volume이란?

Docker Volume은 Docker가 직접 관리하는 저장공간이다.

bind mount는 내가 Host 경로를 직접 지정한다.

반면 Docker Volume은 Docker가 저장 위치를 관리한다.

예시는 이렇게 생겼다.

```yaml
services:
  postgres:
    image: postgres:16
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```

여기서 `postgres-data`는 named volume이다.

Docker가 알아서 Host 내부 어딘가에 저장공간을 만들고 관리한다.

보통 사용자는 그 실제 경로를 직접 만질 필요가 없다.

확인하고 싶으면 아래 명령어를 쓸 수 있다.

```bash
docker volume ls
```

특정 볼륨 정보를 보려면 이렇게 한다.

```bash
docker volume inspect postgres-data
```

## 7. bind mount vs volume

둘 다 Host와 Container 사이에 저장공간을 연결하는 방식이다.

하지만 목적이 조금 다르다.

| 구분    | bind mount                 | Docker volume                 |
| ----- | -------------------------- | ----------------------------- |
| 관리 주체 | 사용자가 Host 경로 직접 관리         | Docker가 관리                    |
| 경로 지정 | `./config:/container/path` | `volume-name:/container/path` |
| 주 사용처 | 설정 파일, 개발 코드, 로컬 수정        | DB 데이터, 영구 데이터                |
| 장점    | 파일을 직접 보고 수정하기 쉬움          | 컨테이너 삭제와 분리되어 데이터 보존에 좋음      |
| 단점    | Host 경로 의존성이 큼             | 실제 저장 위치를 직접 다루기엔 덜 직관적       |

정리하면 이렇다.

설정 파일처럼 사람이 직접 수정해야 하는 것은 bind mount가 편하다.

DB 데이터처럼 안정적으로 보존해야 하는 것은 Docker volume이 적합하다.

## 8. 데이터와 설정파일은 분리해야 한다

여기서 중요한 운영 감각이 하나 있다.

데이터와 설정 파일은 같은 성격이 아니다.

데이터는 애플리케이션이 계속 쌓아가는 결과물이다.

예를 들어 PostgreSQL의 테이블, row, index, transaction log 같은 것들이 데이터다.

설정 파일은 애플리케이션이나 DB가 어떻게 동작할지 정하는 파일이다.

예를 들어 PostgreSQL에서는 이런 파일들이 설정에 가깝다.

```text
postgresql.conf
pg_hba.conf
```

Nginx에서는 이런 파일들이 설정이다.

```text
nginx.conf
default.conf
```

데이터와 설정을 섞어서 관리하면 나중에 헷갈린다.

DB 데이터는 볼륨에 넣고, 설정 파일은 별도의 `config` 디렉터리에서 관리하는 식으로 나누는 게 좋다.

예를 들면 이런 구조다.

```text
my-project/
  docker-compose.yml
  config/
    postgresql.conf
    pg_hba.conf
  init/
    init.sql
```

compose 파일은 이렇게 나눌 수 있다.

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
      - postgres-data:/var/lib/postgresql/data
      - ./config/postgresql.conf:/etc/postgresql/postgresql.conf
      - ./config/pg_hba.conf:/etc/postgresql/pg_hba.conf
      - ./init/init.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  postgres-data:
```

이렇게 보면 역할이 분명해진다.

```text
postgres-data
```

DB 데이터 보존용.

```text
./config/postgresql.conf
./config/pg_hba.conf
```

설정 파일 주입용.

```text
./init/init.sql
```

초기 테이블 생성 또는 초기 데이터 삽입용.

## 9. PostgreSQL 데이터 보존 예시

PostgreSQL에서 가장 중요한 볼륨 마운트는 보통 이 부분이다.

```yaml
volumes:
  - postgres-data:/var/lib/postgresql/data
```

이 설정을 넣고 컨테이너를 실행한다.

```bash
docker compose up -d
```

DB에 접속해서 테이블을 만든다.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

INSERT INTO users (name) VALUES ('kim');
```

이제 컨테이너를 삭제해보자.

```bash
docker compose down
```

다시 실행한다.

```bash
docker compose up -d
```

같은 named volume이 연결되어 있다면 데이터가 남아 있다.

```sql
SELECT * FROM users;
```

결과가 그대로 보이면 Volume이 데이터를 보존하고 있는 것이다.

단, 주의할 점이 있다.

```bash
docker compose down
```

은 기본적으로 named volume을 삭제하지 않는다.

하지만 아래 명령어는 volume까지 삭제한다.

```bash
docker compose down -v
```

`-v` 옵션은 volume까지 지우겠다는 뜻이다.

그래서 DB 데이터를 보존해야 하는 상황에서는 조심해야 한다.

## 10. 설정 파일은 왜 bind mount가 좋을까?

설정 파일은 사람이 직접 수정할 일이 많다.

예를 들어 Nginx 설정을 바꾸고 싶다고 해보자.

컨테이너 안에 들어가서 수정하는 방식은 좋지 않다.

```bash
docker exec -it nginx bash
vi /etc/nginx/conf.d/default.conf
```

이렇게 하면 현재 컨테이너에만 수정이 남는다.

컨테이너를 재생성하면 사라질 수 있다.

대신 Host에 설정 파일을 둔다.

```text
config/
  default.conf
```

그리고 컨테이너에 연결한다.

```yaml
services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./config/default.conf:/etc/nginx/conf.d/default.conf
```

이제 설정 수정은 Host에서 한다.

```bash
vi ./config/default.conf
docker compose restart nginx
```

이렇게 하면 설정 파일이 프로젝트에 남는다.

Git으로 관리하기도 쉽다.

나중에 다른 서버에 올릴 때도 같은 설정을 재현하기 쉽다.

## 11. Volume을 쓰면 컨테이너를 버릴 수 있다

Docker에서 좋은 구조는 컨테이너 자체에 집착하지 않는 구조다.

컨테이너는 언제든 삭제하고 다시 만들 수 있어야 한다.

중요한 것은 컨테이너가 아니라 컨테이너 밖에 있는 정의와 데이터다.

정의는 이런 파일에 있다.

```text
Dockerfile
docker-compose.yml
.env
config/*.conf
```

데이터는 volume에 있다.

```text
postgres-data
```

이렇게 분리하면 컨테이너를 지워도 무섭지 않다.

```bash
docker rm my-postgres
```

다시 만들면 된다.

```bash
docker compose up -d
```

같은 설정과 같은 volume을 연결하면 원래 환경을 복구할 수 있다.

## 12. 실무적으로 중요한 이유

Volume이 중요한 이유는 단순히 데이터가 안 날아가서가 아니다.

더 큰 이유는 재현 가능한 환경을 만들기 위해서다.

컨테이너 안에서 직접 수정하는 방식은 기록이 남지 않는다.

누가 언제 어떤 파일을 바꿨는지 알기 어렵다.

하지만 설정 파일을 Host에 두고 Git으로 관리하면 변경 이력이 남는다.

DB 데이터는 volume으로 보존하면 컨테이너 생명주기와 분리된다.

즉 Docker Volume을 쓰면 다음이 가능해진다.

컨테이너를 지워도 데이터 보존.

설정 파일을 코드처럼 관리.

로컬과 서버 환경을 비슷하게 구성.

컨테이너 재생성에 강한 구조.

운영 환경에 가까운 개발 환경 구성.

## 13. 자주 헷갈리는 명령어

현재 volume 목록 보기.

```bash
docker volume ls
```

특정 volume 정보 보기.

```bash
docker volume inspect postgres-data
```

사용하지 않는 volume 정리.

```bash
docker volume prune
```

컨테이너만 내리기.

```bash
docker compose down
```

컨테이너와 volume까지 같이 삭제하기.

```bash
docker compose down -v
```

여기서 가장 조심해야 하는 것은 이 명령어다.

```bash
docker compose down -v
```

PostgreSQL 데이터를 named volume에 저장하고 있었다면, 이 명령어로 데이터가 삭제될 수 있다.

## 14. 정리

Docker Volume은 컨테이너 밖에 데이터를 저장하기 위한 방법이다.

컨테이너는 삭제되고 재생성될 수 있는 존재이기 때문에, 컨테이너 내부에만 데이터를 저장하면 위험하다.

Host와 Container는 기본적으로 분리되어 있지만, mount를 사용하면 특정 경로를 연결할 수 있다.

bind mount는 Host의 파일이나 디렉터리를 Container에 직접 연결하는 방식이다.

Docker volume은 Docker가 관리하는 저장공간을 Container에 연결하는 방식이다.

설정 파일처럼 사람이 직접 수정하고 Git으로 관리할 파일은 bind mount가 편하다.

PostgreSQL 데이터처럼 컨테이너가 사라져도 보존되어야 하는 데이터는 Docker volume이 적합하다.

결국 핵심은 이것이다.

컨테이너는 버릴 수 있어야 한다.

설정은 파일로 남겨야 한다.

데이터는 volume에 남겨야 한다.

이 구조를 잡아야 Docker를 단순 실행 도구가 아니라 운영 가능한 환경 관리 도구로 쓸 수 있다.
