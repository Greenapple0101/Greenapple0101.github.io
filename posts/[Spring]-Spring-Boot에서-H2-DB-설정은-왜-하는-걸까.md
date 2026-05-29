---
title: "[SPRING] Spring Boot에서 H2 DB 설정은 왜 하는 걸까?"
source: "https://velog.io/@yorange50/SPRING-Spring-Boot에서-H2-DB-설정은-왜-하는-걸까"
published: "2026-05-03T09:37:08.967Z"
tags: "Spring"
backup_date: "2026-05-29T14:52:52.781315"
---

# [SPRING] Spring Boot에서 H2 DB 설정은 왜 하는 걸까?

Spring Boot로 게시판 API를 만들다 보면 `application.properties`에 이런 설정을 넣게 된다.

```properties
spring.application.name=board_api

spring.datasource.url=jdbc:h2:mem:boarddb
spring.datasource.driver-class-name=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=

spring.h2.console.enabled=true
spring.h2.console.path=/h2-console

spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
```

처음 보면 단순히 복붙하는 설정처럼 보이지만, DevOps 관점에서는 꽤 중요한 의미가 있다. 이 설정은 한마디로 말하면 **Spring Boot 애플리케이션을 임시 개발용 DB에 연결하고, JPA가 테이블을 자동으로 관리하게 하며, SQL 로그를 확인할 수 있게 하는 설정**이다.

먼저 앱 이름을 설정한다.

```properties
spring.application.name=board_api
```

이 설정은 현재 Spring Boot 애플리케이션의 이름을 `board_api`로 지정하는 것이다. 단순한 이름처럼 보이지만, 로그나 모니터링 환경에서는 서비스 이름처럼 쓰일 수 있다. DevOps 관점에서는 나중에 여러 서비스를 운영할 때 “이 로그가 어느 애플리케이션에서 나온 것인지” 구분하는 데 도움이 된다.

다음은 DB 연결 설정이다.

```properties
spring.datasource.url=jdbc:h2:mem:boarddb
spring.datasource.driver-class-name=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=
```

여기서는 H2 데이터베이스를 사용한다. H2는 가볍게 사용할 수 있는 Java 기반 데이터베이스다. 특히 중요한 부분은 이 설정이다.

```properties
spring.datasource.url=jdbc:h2:mem:boarddb
```

`jdbc:h2:mem:boarddb`에서 `mem`은 메모리 데이터베이스를 의미한다. 즉, 애플리케이션이 실행될 때 메모리 위에 DB가 만들어지고, 애플리케이션이 종료되면 데이터가 사라진다. 그래서 이 설정은 운영용 DB가 아니라 개발이나 테스트용으로 적합하다.

DevOps 관점에서는 이렇게 이해하면 된다.

```text
H2 mem DB는 임시 DB다.
서버를 재시작하면 데이터가 사라진다.
컨테이너가 내려갔다 올라오면 데이터도 초기화된다.
운영 환경에서 사용할 DB는 아니다.
```

예를 들어 게시글을 저장하고 서버를 껐다 켜면, 이전에 저장했던 게시글이 사라질 수 있다. 이것은 오류가 아니라 메모리 DB의 특성이다.

다음 설정은 H2 콘솔을 켜는 설정이다.

```properties
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console
```

이 설정을 넣으면 브라우저에서 H2 DB를 직접 확인할 수 있다.

```text
http://localhost:8080/h2-console
```

접속할 때 JDBC URL에는 다음 값을 넣으면 된다.

```text
jdbc:h2:mem:boarddb
```

User Name은 보통 `sa`, Password는 비워두면 된다.

이 기능은 개발할 때 매우 편하다. API로 게시글을 생성한 뒤 실제로 DB에 데이터가 들어갔는지 브라우저에서 바로 확인할 수 있기 때문이다. 하지만 DevOps 관점에서는 주의해야 한다.

```text
로컬 개발 환경에서는 편리하다.
운영 환경에서는 보통 비활성화해야 한다.
외부에서 접근 가능하게 열리면 보안 문제가 될 수 있다.
```

즉 `/h2-console`은 개발 중에는 유용하지만, 실제 서비스 환경에서는 열어두면 안 되는 설정에 가깝다.

다음은 JPA와 Hibernate 설정이다.

```properties
spring.jpa.hibernate.ddl-auto=update
```

이 설정은 JPA가 Entity 클래스를 보고 DB 테이블을 자동으로 만들거나 수정하게 한다. 예를 들어 `Board`라는 Entity 클래스가 있으면, Spring Boot가 실행될 때 Hibernate가 이를 보고 `board` 테이블을 만들어줄 수 있다.

`ddl-auto=update`는 기존 테이블을 유지하면서 Entity 변경사항을 DB에 반영하려고 한다. 개발할 때는 편하다. 테이블을 직접 만들지 않아도 되고, Entity를 수정하면 어느 정도 자동으로 DB 구조가 따라오기 때문이다.

하지만 운영 환경에서는 조심해야 한다.

```text
개발용으로는 편하다.
운영 DB에서는 위험할 수 있다.
애플리케이션 실행 시점에 테이블 구조가 자동으로 바뀔 수 있다.
```

운영 환경에서는 보통 `update`보다 `validate`를 사용하거나, Flyway, Liquibase 같은 DB 마이그레이션 도구를 사용한다.

예를 들어 운영에서는 이런 식으로 더 보수적으로 설정할 수 있다.

```properties
spring.jpa.hibernate.ddl-auto=validate
```

`validate`는 Entity와 DB 테이블 구조가 맞는지 확인만 하고, DB 구조를 자동으로 바꾸지는 않는다. 운영에서는 데이터가 중요하기 때문에 자동 변경보다 명시적인 마이그레이션이 더 안전하다.

마지막으로 SQL 로그 설정이다.

```properties
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
```

`show-sql=true`는 JPA가 실행하는 SQL을 콘솔에 출력하게 한다. 예를 들어 게시글을 저장하면 `insert`, 조회하면 `select`, 수정하면 `update`, 삭제하면 `delete` SQL이 로그에 나타난다.

`format_sql=true`는 SQL을 보기 좋게 줄바꿈해서 출력해준다.

개발 중에는 이 설정이 꽤 유용하다. 내가 호출한 API가 실제로 어떤 SQL을 발생시키는지 확인할 수 있기 때문이다.

예를 들어 게시글 목록 조회 API를 호출했을 때 콘솔에 `select` 쿼리가 찍힌다면, Controller → Service → Repository → DB 흐름이 정상적으로 동작하고 있다는 것을 확인할 수 있다.

하지만 운영에서는 이 설정도 조심해야 한다.

```text
개발/디버깅용으로는 좋다.
운영에서는 로그가 너무 많이 쌓일 수 있다.
쿼리나 데이터가 로그에 노출될 수 있다.
```

DevOps 입장에서 이 설정 전체를 정리하면 다음과 같다.

```text
Spring Boot 게시판 API를 H2 메모리 DB에 연결한다.
H2 콘솔을 통해 브라우저에서 DB를 확인할 수 있게 한다.
JPA가 Entity 기준으로 테이블을 자동 생성/수정하게 한다.
실행되는 SQL을 로그로 확인할 수 있게 한다.
```

다만 운영 관점에서 기억해야 할 점은 명확하다.

```text
H2 메모리 DB는 재시작하면 데이터가 사라진다.
h2-console은 운영 환경에서 열어두면 위험하다.
ddl-auto=update는 운영 DB에서 위험할 수 있다.
show-sql=true는 운영 로그 관리 측면에서 주의해야 한다.
```

결론적으로 이 설정은 **Spring Boot와 DB 연결 흐름을 빠르게 익히기 위한 개발용 설정**이다. 지금 게시판 CRUD를 연습하는 단계에서는 매우 적절하다. 기존에 `List<Board>`로 메모리에 게시글을 저장하던 방식에서 한 단계 나아가, 실제 DB 연결 구조를 경험할 수 있기 때문이다.

즉 지금 이 설정을 이해한다는 것은 단순히 Spring 설정을 외우는 것이 아니라, 개발 환경과 운영 환경의 차이를 구분하기 시작했다는 뜻이다. DevOps 관점에서는 바로 이 구분이 중요하다.
