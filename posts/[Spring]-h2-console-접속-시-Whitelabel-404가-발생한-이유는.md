---
title: "[SPRING] /h2-console 접속 시 Whitelabel 404가 발생한 이유는?"
source: "https://velog.io/@yorange50/SPRING-h2-console-접속-시-Whitelabel-404가-발생한-이유는"
published: "2026-05-03T10:34:52.861Z"
tags: ""
backup_date: "2026-05-29T14:52:52.780955"
---


Spring Boot 게시판 CRUD API를 만들면서 H2 인메모리 DB를 연결하려고 했다. `application.properties`에는 H2 설정을 추가했고, 브라우저에서 `http://localhost:8080/h2-console`로 접속했지만 Whitelabel Error Page가 발생했다.

```text
Whitelabel Error Page

This application has no explicit mapping for /error, so you are seeing this as a fallback.

There was an unexpected error (type=Not Found, status=404).
```

처음에는 Controller 매핑 문제라고 생각했다. 기존 `BoardController`는 다음과 같이 `/boards` 주소를 메서드마다 직접 지정하고 있었다.

```java
@RestController
@RequestMapping
@CrossOrigin(origins = "http://localhost:5173")
public class BoardController {

    @GetMapping("/boards")
    public List<Board> getBoards(){
        return boardService.getBoards();
    }

    @GetMapping("/boards/{id}")
    public Board getBoard(@PathVariable Long id){
        return boardService.getBoard(id);
    }
}
```

이 구조도 동작은 가능하지만, 주소를 더 명확하게 관리하기 위해 클래스 레벨에 `/boards`를 묶는 방식으로 변경했다.

```java
@RestController
@RequestMapping("/boards")
@CrossOrigin(origins = "http://localhost:5173")
public class BoardController {

    private final BoardService boardService;

    public BoardController(BoardService boardService){
        this.boardService = boardService;
    }

    @GetMapping
    public List<Board> getBoards(){
        return boardService.getBoards();
    }

    @GetMapping("/{id}")
    public Board getBoard(@PathVariable Long id){
        return boardService.getBoard(id);
    }

    @PostMapping
    public Board createBoard(@RequestBody Board board){
        return boardService.createBoard(board);
    }

    @PutMapping("/{id}")
    public Board updateBoard(@PathVariable Long id, @RequestBody Board board){
        return boardService.updateBoard(id, board);
    }

    @DeleteMapping("/{id}")
    public String deleteBoard(@PathVariable Long id){
        boardService.deleteBoard(id);
        return "삭제됨: " + id;
    }
}
```

이렇게 바꾼 뒤 게시판 API의 최종 주소는 다음과 같이 정리되었다.

```text
GET     /boards
GET     /boards/{id}
POST    /boards
PUT     /boards/{id}
DELETE  /boards/{id}
```

하지만 중요한 점은 이 수정이 H2 콘솔 문제를 직접 해결하는 것은 아니라는 점이었다. `/boards`는 내가 만든 게시판 API 주소이고, `/h2-console`은 Spring Boot가 H2 콘솔을 자동 등록해주는 별도 주소이기 때문이다.

즉 문제를 이렇게 구분해야 했다.

```text
/boards 404 발생      → Controller 매핑 또는 패키지 스캔 문제
/h2-console 404 발생  → H2 콘솔 자동 등록 문제
```

이후 `pom.xml`을 확인해보니 처음에는 `spring-boot-starter-web`, `lombok`, `spring-boot-starter-test` 정도만 들어가 있었다. H2와 JPA를 사용하려면 다음 의존성이 필요했다.

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>

<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>runtime</scope>
</dependency>
```

의존성을 추가한 뒤 서버를 다시 실행하자 JPA와 H2 DB 연결은 정상적으로 초기화되었다.

로그에서는 다음 내용을 확인할 수 있었다.

```text
Database version: 2.4.240
Default catalog/schema: BOARDDB/PUBLIC
Initialized JPA EntityManagerFactory for persistence unit 'default'
Tomcat started on port 8080 (http) with context path '/'
Started BoardApiApplication
```

이 로그를 통해 알 수 있었던 것은 다음과 같다.

```text
Spring Boot 애플리케이션 정상 실행
Tomcat 8080 포트 정상 실행
H2 DataSource 연결 성공
JPA EntityManagerFactory 초기화 성공
```

하지만 여전히 `/h2-console`은 404가 발생했다. 이 시점에서 DB 연결 자체는 성공했지만, H2 콘솔 웹 화면이 등록되지 않았다는 것을 알 수 있었다.

`application.properties` 위치도 확인했다.

```text
src/main/resources/application.properties
```

설정 내용은 다음과 같았다.

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

위치와 설정은 맞았다. 따라서 남은 원인은 Spring Boot 버전 차이였다. 현재 프로젝트는 Spring Boot `4.0.6`을 사용하고 있었다.

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>4.0.6</version>
</parent>
```

Spring Boot 4에서는 기존처럼 `com.h2database:h2` 의존성과 `spring.h2.console.enabled=true` 설정만으로 H2 콘솔이 바로 열리지 않는 경우가 있었다. 그래서 H2 콘솔 전용 의존성을 추가하는 방식으로 접근했다.

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-h2console</artifactId>
</dependency>
```

최종적으로 H2 관련 의존성은 다음과 같이 정리된다.

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>

<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>runtime</scope>
</dependency>

<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-h2console</artifactId>
</dependency>
```

수정 후에는 Maven 프로젝트를 다시 빌드하고 실행해야 한다.

```powershell
mvn clean spring-boot:run
```

또는 Maven Wrapper를 사용한다면 다음 명령어를 사용할 수 있다.

```powershell
.\mvnw.cmd clean spring-boot:run
```

그리고 브라우저에서 H2 콘솔에 접속한다.

```text
http://localhost:8080/h2-console
```

로그인 정보는 다음과 같다.

```text
JDBC URL: jdbc:h2:mem:boarddb
User Name: sa
Password: 비워두기
```

이번 트러블슈팅에서 헷갈렸던 지점은 `/boards`와 `/h2-console`의 책임이 다르다는 점이었다. `/boards`는 내가 직접 만든 Controller가 처리하는 API 주소이고, `/h2-console`은 Spring Boot가 H2 콘솔 기능을 자동 등록해야 열리는 주소다.

따라서 `/h2-console`에서 404가 난다고 해서 무조건 Controller 매핑을 고칠 필요는 없다. 오히려 H2 의존성, JPA 의존성, `application.properties` 위치, Spring Boot 버전을 먼저 확인해야 한다.

이번 문제의 결론은 다음과 같다.

```text
원인:
Spring Boot 애플리케이션과 H2 DB 연결은 성공했지만,
Spring Boot 4 환경에서 H2 Console 웹 매핑이 자동 등록되지 않아 /h2-console에서 404가 발생함

해결:
pom.xml에 JPA, H2, H2 Console 관련 의존성을 추가하고,
application.properties의 H2 콘솔 설정을 확인한 뒤,
Maven clean 후 서버를 재실행함
```

DevOps 관점에서 이 문제는 단순한 Spring 오류가 아니라 **애플리케이션 실행, 의존성 관리, 설정 파일 적용, 런타임 로그 확인을 통해 원인을 분리한 사례**라고 볼 수 있다. 서버가 떠 있는지, DB 연결이 되었는지, 웹 매핑이 등록되었는지를 로그로 나눠 확인한 것이 핵심이었다.
![](https://velog.velcdn.com/images/yorange50/post/192b6a50-845a-4998-80d3-1c08d9b94607/image.png)
