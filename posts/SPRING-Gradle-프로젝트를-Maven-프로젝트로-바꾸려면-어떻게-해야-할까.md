---
title: "[SPRING] Gradle 프로젝트를 Maven 프로젝트로 바꾸려면 어떻게 해야 할까?"
source: "https://velog.io/@yorange50/SPRING-Gradle-프로젝트를-Maven-프로젝트로-바꾸려면-어떻게-해야-할까"
published: "2026-05-03T10:38:17.206Z"
tags: ""
backup_date: "2026-05-29T14:52:52.780645"
---

현재 프로젝트를 Gradle이 아니라 Maven으로 관리하기로 했다. 따라서 `build.gradle`에 의존성을 추가하는 방식이 아니라, 프로젝트 루트의 `pom.xml`을 기준으로 의존성을 관리해야 했다.

Gradle과 Maven의 가장 큰 차이는 의존성을 선언하는 파일이다.

```text id="0301ew"
Gradle  → build.gradle
Maven   → pom.xml
```

즉 Gradle에서 Maven으로 바꾼다는 것은 단순히 파일 이름만 바꾸는 것이 아니라, 의존성 선언 방식과 빌드 명령어를 Maven 방식으로 변경하는 것이다.

먼저 기존 Gradle 프로젝트에서 사용하던 핵심 의존성을 확인했다.

```gradle id="e1m8a6"
implementation 'org.springframework.boot:spring-boot-starter-web'
implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
runtimeOnly 'com.h2database:h2'
testImplementation 'org.springframework.boot:spring-boot-starter-test'
```

이 의존성들은 Maven에서는 다음과 같이 바꿔서 작성해야 한다.

```xml id="wzglwy"
<dependencies>
    <!-- Spring Web: REST API 개발용 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <!-- Spring Data JPA: Entity, Repository, Hibernate 사용 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>

    <!-- H2 Database: 개발용 인메모리 DB -->
    <dependency>
        <groupId>com.h2database</groupId>
        <artifactId>h2</artifactId>
        <scope>runtime</scope>
    </dependency>

    <!-- Test -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

Gradle의 `implementation`은 Maven에서는 보통 별도의 `scope` 없이 작성한다.

```gradle id="uswdti"
implementation 'org.springframework.boot:spring-boot-starter-web'
```

Maven에서는 다음과 같다.

```xml id="gddv7p"
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

Gradle의 `runtimeOnly`는 Maven에서는 `scope`를 `runtime`으로 지정한다.

```gradle id="udtruh"
runtimeOnly 'com.h2database:h2'
```

Maven에서는 다음과 같다.

```xml id="4v5yn8"
<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>runtime</scope>
</dependency>
```

Gradle의 `testImplementation`은 Maven에서는 `scope`를 `test`로 지정한다.

```gradle id="j7c02g"
testImplementation 'org.springframework.boot:spring-boot-starter-test'
```

Maven에서는 다음과 같다.

```xml id="m4oaz8"
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

그다음 Maven 프로젝트의 기본 구조를 맞췄다.

```text id="02n6r3"
board_api
 ├─ pom.xml
 ├─ src
 │   ├─ main
 │   │   ├─ java
 │   │   │   └─ com
 │   │   │       └─ board
 │   │   │           └─ api
 │   │   │               └─ BoardApiApplication.java
 │   │   └─ resources
 │   │       └─ application.properties
 │   └─ test
 │       └─ java
```

Maven에서는 `src/main/java` 아래에 Java 코드가 들어가고, `src/main/resources` 아래에 설정 파일이 들어간다. Spring Boot 설정 파일인 `application.properties`도 반드시 이 위치에 있어야 한다.

```text id="3j9pz2"
src/main/resources/application.properties
```

이후 Gradle 관련 파일은 더 이상 사용하지 않는다. Maven으로 완전히 전환하려면 보통 다음 파일들은 제거하거나 사용하지 않도록 정리한다.

```text id="tfshh9"
build.gradle
settings.gradle
gradlew
gradlew.bat
gradle/
```

반대로 Maven 프로젝트에서 중심이 되는 파일은 다음이다.

```text id="08tmxe"
pom.xml
```

Maven Wrapper를 사용한다면 다음 파일들도 함께 둘 수 있다.

```text id="1l9v73"
mvnw
mvnw.cmd
.mvn/
```

빌드와 실행 명령어도 Gradle에서 Maven으로 바뀐다.

Gradle에서는 보통 다음 명령어를 사용한다.

```bash id="6vlxph"
./gradlew bootRun
```

Windows에서는 다음과 같이 실행할 수 있다.

```powershell id="1gn0wo"
gradlew.bat bootRun
```

Maven에서는 다음 명령어를 사용한다.

```bash id="9gsjvk"
mvn spring-boot:run
```

Windows PowerShell에서 Maven Wrapper를 사용한다면 다음과 같이 실행한다.

```powershell id="0c31c7"
.\mvnw.cmd spring-boot:run
```

빌드 명령어도 다르다.

Gradle:

```bash id="rw9p8a"
./gradlew build
```

Maven:

```bash id="z96lzo"
mvn clean package
```

Maven Wrapper 사용 시:

```powershell id="ksww6d"
.\mvnw.cmd clean package
```

이번 전환에서 최종적으로 사용한 `pom.xml`의 핵심 구조는 다음과 같다.

```xml id="q7l86u"
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">

    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>board_api</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>board_api</name>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>4.0.6</version>
        <relativePath/>
    </parent>

    <properties>
        <java.version>21</java.version>
        <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

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
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

전환 후에는 VS Code나 IDE에서도 Maven 프로젝트로 다시 인식시켜야 한다. VS Code에서는 Maven 탭에서 프로젝트를 새로고침하거나, 터미널에서 다음 명령어로 의존성을 다시 내려받을 수 있다.

```powershell id="n3enml"
mvn clean package
```

또는 실행까지 바로 확인한다.

```powershell id="sufo21"
mvn spring-boot:run
```

정리하면 Gradle에서 Maven으로 전환하는 과정은 다음과 같다.

```text id="kcelqi"
1. build.gradle에 있던 의존성을 확인한다.
2. 같은 의존성을 pom.xml의 dependency 형식으로 옮긴다.
3. runtimeOnly는 <scope>runtime</scope>으로 바꾼다.
4. testImplementation은 <scope>test</scope>로 바꾼다.
5. 프로젝트 구조를 src/main/java, src/main/resources 기준으로 맞춘다.
6. application.properties를 src/main/resources 아래에 둔다.
7. Gradle 명령어 대신 Maven 명령어를 사용한다.
8. IDE에서 Maven 프로젝트로 다시 로드한다.
```

결론적으로 Gradle에서 Maven으로 바꾼다는 것은 “빌드 도구를 바꾼다”는 뜻이다. 코드 자체의 Controller, Service, Domain 구조가 바뀌는 것은 아니다. 바뀌는 핵심은 **의존성 선언 파일, 빌드 명령어, 프로젝트 인식 방식**이다.
