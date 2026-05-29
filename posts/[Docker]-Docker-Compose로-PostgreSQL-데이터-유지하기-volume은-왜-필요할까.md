---
title: "[DOCKER] Docker Compose로 PostgreSQL 데이터 유지하기: volume은 왜 필요할까?"
source: "https://velog.io/@yorange50/DOCKER-Docker-Compose로-PostgreSQL-데이터-유지하기-volume은-왜-필요할까"
published: "2026-05-13T03:58:40.642Z"
tags: ""
backup_date: "2026-05-29T14:52:52.751675"
---

Docker로 PostgreSQL을 띄우면 처음에는 굉장히 편하다. `docker compose up` 한 번이면 DB 컨테이너가 실행되고, 포트만 연결하면 DBeaver 같은 DB 클라이언트에서도 바로 접속할 수 있다. 그런데 여기서 가장 자주 헷갈리는 문제가 있다.

> docker compose down 했더니 DB 데이터가 사라졌다

이 문제는 Docker 컨테이너의 특징을 이해하면 자연스럽게 이해된다. 컨테이너는 기본적으로 언제든 지우고 다시 만들 수 있는 일회성 실행 환경이다. 즉, 컨테이너 안에만 데이터를 저장하면 컨테이너가 삭제될 때 데이터도 같이 사라질 수 있다. 데이터베이스처럼 데이터가 계속 남아 있어야 하는 서비스는 반드시 컨테이너 바깥에 데이터를 저장해야 한다. 이때 사용하는 것이 바로 Docker volume이다.

---

## 1. 컨테이너 안에 DB 데이터를 저장하면 왜 위험할까?

PostgreSQL 컨테이너를 실행하면 PostgreSQL은 내부적으로 데이터 파일을 특정 디렉터리에 저장한다.

PostgreSQL 공식 이미지 기준으로 데이터 저장 위치는 보통 다음 경로다.

```bash
/var/lib/postgresql/data
```

문제는 이 경로가 컨테이너 내부 파일시스템이라는 점이다.

예를 들어 PostgreSQL 컨테이너 안에서 테이블을 만들고 데이터를 넣었다고 해보자.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50)
);

INSERT INTO users (name) VALUES ('kim');
```

이 상태에서 컨테이너가 계속 살아 있으면 데이터는 유지된다. 하지만 컨테이너를 삭제하고 다시 만들면 이야기가 달라진다.

```bash
docker compose down
docker compose up -d
```

이때 volume을 설정하지 않았다면 PostgreSQL 컨테이너는 새로 만들어진다. 새 컨테이너는 이전 컨테이너 내부에 있던 데이터 파일을 알 수 없다. 그래서 테이블과 데이터가 사라진 것처럼 보인다.

정확히 말하면 DB가 데이터를 잃어버린 게 아니라, 이전 컨테이너 자체가 사라졌고 새 컨테이너가 빈 데이터 디렉터리로 다시 시작한 것이다.

---

## 2. Docker volume이 하는 일

Docker volume은 컨테이너 밖에 데이터를 저장하는 공간이다.

컨테이너는 삭제될 수 있지만, volume은 따로 삭제하지 않는 한 남아 있다. 그래서 PostgreSQL의 데이터 저장 경로를 volume과 연결해두면 컨테이너를 내렸다가 다시 올려도 데이터가 유지된다.

구조는 이렇게 생각하면 된다.

```text
PostgreSQL 컨테이너 내부
/var/lib/postgresql/data
        |
        | 연결
        v
Docker volume 또는 호스트 디렉터리
```

즉, PostgreSQL은 여전히 `/var/lib/postgresql/data`에 데이터를 저장한다고 생각하지만, 실제 데이터는 컨테이너 바깥의 volume에 저장된다.

---

## 3. Docker Compose에서 PostgreSQL volume 설정하기

가장 기본적인 PostgreSQL용 `docker-compose.yml` 예시는 다음과 같다.

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:16
    container_name: my-postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

여기서 중요한 부분은 두 군데다.

첫 번째는 서비스 내부의 `volumes`다.

```yaml
services:
  postgres:
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

이 부분은 PostgreSQL 컨테이너의 `/var/lib/postgresql/data` 경로를 `postgres_data`라는 Docker volume에 연결하겠다는 뜻이다.

두 번째는 최상위 `volumes`다.

```yaml
volumes:
  postgres_data:
```

이 부분은 `postgres_data`라는 이름의 volume을 Docker Compose가 관리하도록 선언하는 것이다.

---

## 4. 서비스 내부 volumes와 최상위 volumes는 다르다

Docker Compose를 처음 보면 `volumes`가 두 번 나와서 헷갈린다.

```yaml
services:
  postgres:
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

둘은 역할이 다르다.

서비스 내부의 `volumes`는 “이 컨테이너에 어떤 저장소를 어디에 연결할 것인가”를 의미한다.

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

이건 리스트 형태로 작성한다. 그래서 앞에 `-`가 붙는다.

반면 최상위 `volumes`는 “이 Compose 프로젝트에서 사용할 volume 이름을 선언한다”는 의미다.

```yaml
volumes:
  postgres_data:
```

이건 매핑 구조로 작성한다. 그래서 앞에 `-`를 붙이지 않고, 이름 뒤에 콜론을 붙인다.

---

## 5. `volumes must be a mapping` 오류가 나는 이유

Docker Compose에서 다음과 같은 오류가 날 수 있다.

```bash
volumes must be a mapping
```

이 오류는 대부분 YAML 문법 형식이 잘못되었을 때 발생한다. 특히 최상위 `volumes`를 리스트처럼 작성했을 때 자주 발생한다.

잘못된 예시는 다음과 같다.

```yaml
volumes:
  - postgres_data
```

겉으로 보기에는 자연스러워 보이지만, 최상위 `volumes`에서는 이렇게 쓰면 안 된다. 최상위 `volumes`는 리스트가 아니라 매핑이어야 한다.

올바른 형식은 다음과 같다.

```yaml
volumes:
  postgres_data:
```

즉, 최상위 `volumes` 아래에서는 `-`를 쓰지 않고 `볼륨이름:` 형태로 작성해야 한다.

---

## 6. 그런데 서비스 내부 volumes에서는 왜 `-`를 쓸까?

서비스 내부에서는 여러 개의 볼륨을 연결할 수 있다.

예를 들어 다음처럼 여러 경로를 연결할 수 있다.

```yaml
services:
  app:
    image: my-app
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
```

그래서 서비스 내부 `volumes`는 리스트 구조다. 리스트 구조이기 때문에 각 항목 앞에 `-`를 붙인다.

PostgreSQL 예시도 마찬가지다.

```yaml
services:
  postgres:
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

이건 “postgres 컨테이너에 연결할 volume 목록”이다. 지금은 하나만 있지만, 구조상 리스트이기 때문에 `-`를 붙인다.

정리하면 다음과 같다.

```yaml
services:
  postgres:
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

서비스 내부 `volumes`는 리스트.

```yaml
volumes:
  postgres_data:
```

최상위 `volumes`는 매핑.

이 차이를 모르면 `volumes must be a mapping` 오류가 난다.

---

## 7. 전체 PostgreSQL Compose 예시

실습용으로 사용할 수 있는 전체 파일은 다음과 같다.

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:16
    container_name: postgres-volume-test
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpass
      POSTGRES_DB: testdb
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

이 파일을 `docker-compose.yml`로 저장한 뒤 실행한다.

```bash
docker compose up -d
```

컨테이너가 잘 떴는지 확인한다.

```bash
docker ps
```

PostgreSQL 컨테이너에 접속한다.

```bash
docker exec -it postgres-volume-test psql -U testuser -d testdb
```

테이블을 만들고 데이터를 넣는다.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50)
);

INSERT INTO users (name) VALUES ('kim');
INSERT INTO users (name) VALUES ('lee');

SELECT * FROM users;
```

결과는 다음처럼 나온다.

```text
 id | name
----+------
  1 | kim
  2 | lee
```

이제 컨테이너를 내린다.

```bash
docker compose down
```

다시 올린다.

```bash
docker compose up -d
```

다시 PostgreSQL에 접속한다.

```bash
docker exec -it postgres-volume-test psql -U testuser -d testdb
```

그리고 데이터를 조회한다.

```sql
SELECT * FROM users;
```

volume 설정이 제대로 되어 있다면 데이터가 그대로 남아 있어야 한다.

```text
 id | name
----+------
  1 | kim
  2 | lee
```

이게 바로 volume을 사용하는 이유다.

---

## 8. `docker compose down`을 해도 데이터가 남는 이유

`docker compose down`은 기본적으로 컨테이너와 네트워크를 삭제한다. 하지만 named volume은 자동으로 삭제하지 않는다.

즉, 다음 명령어를 실행해도 volume은 남는다.

```bash
docker compose down
```

그래서 다시 `docker compose up -d`를 하면 기존 volume이 다시 연결되고, PostgreSQL 데이터도 그대로 유지된다.

하지만 다음 명령어를 사용하면 volume까지 삭제된다.

```bash
docker compose down -v
```

여기서 `-v`는 volume도 함께 삭제하겠다는 뜻이다.

따라서 DB 데이터를 유지하고 싶다면 실습 중에 습관적으로 `docker compose down -v`를 치면 안 된다.

정리하면 다음과 같다.

```bash
docker compose down
```

컨테이너 삭제, 네트워크 삭제, volume 유지.

```bash
docker compose down -v
```

컨테이너 삭제, 네트워크 삭제, volume 삭제.

DB 데이터까지 완전히 초기화하고 싶을 때만 `-v`를 사용한다.

---

## 9. named volume과 bind mount의 차이

Docker에서 데이터를 컨테이너 밖에 저장하는 방법은 크게 두 가지가 있다.

첫 번째는 named volume이다.

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

그리고 아래에 volume 이름을 선언한다.

```yaml
volumes:
  postgres_data:
```

이 방식은 Docker가 volume 저장 위치를 직접 관리한다. 개발자가 호스트의 정확한 경로를 몰라도 된다. DB 데이터 저장에는 이 방식이 가장 무난하다.

두 번째는 bind mount다.

```yaml
volumes:
  - ./postgres-data:/var/lib/postgresql/data
```

이 방식은 현재 프로젝트 폴더의 `postgres-data` 디렉터리를 컨테이너 내부의 PostgreSQL 데이터 디렉터리와 직접 연결한다.

구조는 다음과 같다.

```text
현재 프로젝트 폴더/postgres-data
        |
        v
컨테이너 내부 /var/lib/postgresql/data
```

bind mount는 로컬에서 파일을 직접 확인하기 쉽다는 장점이 있다. 하지만 DB 데이터 디렉터리는 권한 문제나 OS별 파일시스템 차이 때문에 named volume이 더 안정적인 경우가 많다.

실습이나 일반적인 PostgreSQL 컨테이너 운영에서는 보통 named volume을 추천한다.

---

## 10. DBeaver로 접속하기

Docker Compose로 PostgreSQL을 실행했다면 DBeaver에서도 접속할 수 있다.

위 예시 기준 접속 정보는 다음과 같다.

```text
Host: localhost
Port: 5432
Database: testdb
Username: testuser
Password: testpass
```

Compose 파일의 이 부분과 연결된다.

```yaml
ports:
  - "5432:5432"
environment:
  POSTGRES_USER: testuser
  POSTGRES_PASSWORD: testpass
  POSTGRES_DB: testdb
```

`5432:5432`는 내 노트북의 5432 포트를 컨테이너 내부의 5432 포트로 연결한다는 뜻이다.

즉, DBeaver가 `localhost:5432`로 접속하면 실제로는 Docker 컨테이너 안의 PostgreSQL 5432 포트로 연결된다.

---

## 11. 실습 흐름 정리

Docker Compose로 PostgreSQL volume 저장을 확인하는 흐름은 다음과 같다.

```bash
docker compose up -d
```

PostgreSQL 컨테이너 실행.

```bash
docker exec -it postgres-volume-test psql -U testuser -d testdb
```

컨테이너 내부 PostgreSQL 접속.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50)
);

INSERT INTO users (name) VALUES ('kim');
SELECT * FROM users;
```

테이블 생성, 데이터 삽입, 조회.

```bash
docker compose down
```

컨테이너 종료 및 삭제.

```bash
docker compose up -d
```

컨테이너 재생성.

```bash
docker exec -it postgres-volume-test psql -U testuser -d testdb
```

다시 PostgreSQL 접속.

```sql
SELECT * FROM users;
```

데이터가 그대로 남아 있는지 확인.

---

## 12. 자주 하는 실수

첫 번째 실수는 최상위 `volumes`에 `-`를 붙이는 것이다.

```yaml
volumes:
  - postgres_data
```

이렇게 쓰면 `volumes must be a mapping` 오류가 발생할 수 있다.

올바른 형식은 다음과 같다.

```yaml
volumes:
  postgres_data:
```

두 번째 실수는 서비스 내부 `volumes`를 문자열 하나로 작성하는 것이다.

```yaml
services:
  postgres:
    volumes: "postgres_data:/var/lib/postgresql/data"
```

서비스 내부 `volumes`는 리스트로 작성해야 한다.

```yaml
services:
  postgres:
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

세 번째 실수는 들여쓰기 오류다.

YAML은 들여쓰기에 민감하다. 다음처럼 들여쓰기가 틀리면 Compose가 의도와 다르게 해석하거나 오류를 낸다.

```yaml
services:
postgres:
  image: postgres:16
```

올바른 형식은 다음과 같다.

```yaml
services:
  postgres:
    image: postgres:16
```

YAML에서는 보통 공백 2칸 들여쓰기를 사용한다. 탭보다는 스페이스를 쓰는 것이 안전하다.

---

## 13. 최종 정리

Docker 컨테이너는 언제든 삭제되고 다시 만들어질 수 있다. 그래서 PostgreSQL 같은 데이터베이스를 컨테이너 안에서만 실행하면 데이터 유지 문제가 생긴다. 이 문제를 해결하기 위해 Docker volume을 사용한다.

PostgreSQL의 데이터 저장 경로인 `/var/lib/postgresql/data`를 Docker volume과 연결하면, 컨테이너를 내렸다가 다시 올려도 데이터가 유지된다.

Docker Compose에서 가장 중요한 문법은 다음 두 가지다.

```yaml
services:
  postgres:
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

서비스 내부 `volumes`는 리스트이므로 `-`를 사용한다.

```yaml
volumes:
  postgres_data:
```

최상위 `volumes`는 매핑이므로 `-`를 사용하지 않고 `볼륨이름:` 형태로 작성한다.

`volumes must be a mapping` 오류는 대부분 이 차이를 헷갈렸을 때 발생한다.

결국 핵심은 간단하다.

```text
컨테이너는 사라질 수 있다.
하지만 DB 데이터는 사라지면 안 된다.
그래서 데이터를 컨테이너 밖 volume에 저장한다.
```

Docker Compose로 DB를 띄울 때 volume 설정은 선택이 아니라 거의 필수에 가깝다. 특히 PostgreSQL, MySQL, Redis처럼 상태를 가진 서비스를 다룰 때는 컨테이너 실행보다 데이터가 어디에 저장되는지를 먼저 확인해야 한다.
