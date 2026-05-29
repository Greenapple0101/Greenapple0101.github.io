---
title: "[Spring/JPA] Repository는 왜 텅 비어 있는데 동작할까?"
source: "https://velog.io/@yorange50/SpringJPA-Repository는-왜-텅-비어-있는데-동작할까"
published: "2026-05-07T08:56:20.988Z"
tags: ""
backup_date: "2026-05-29T14:52:52.769697"
---

Spring Boot에서 JPA를 쓰다 보면 이런 코드를 자주 보게 된다.

```java
package com.board.api.repository;

import com.board.api.domain.Board;
import org.springframework.data.jpa.repository.JpaRepository;

public interface BoardRepository extends JpaRepository<Board, Long> {
}
```

처음 보면 이상하다.

안에 아무 코드도 없다.

`save()`도 없고,
`findAll()`도 없고,
`findById()`도 없고,
`delete()`도 없다.

그런데 Service에서는 이런 코드가 잘 동작한다.

```java
boardRepository.findAll();
boardRepository.findById(id);
boardRepository.save(board);
boardRepository.deleteById(id);
```

왜 그럴까?

핵심은 이것이다.

> BoardRepository가 JpaRepository를 상속받고 있기 때문이다.

사용자가 올린 코드에서도 `BoardRepository extends JpaRepository<Board, Long>` 구조로 되어 있고, `JpaRepository` 내부에는 `flush`, `saveAndFlush`, `deleteAllInBatch`, `getReferenceById`, `findAll`, `findAllById` 같은 메서드들이 이미 정의되어 있다. 그래서 `BoardRepository` 자체가 비어 있어도 상속받은 기능을 그대로 사용할 수 있다. 

---

# 1. Repository는 DB 접근 통로다

Repository는 말 그대로 저장소에 접근하는 계층이다.

게시판 예시로 보면 역할은 이렇다.

```text
Controller
→ Service
→ Repository
→ DB
```

Controller는 요청을 받고,
Service는 비즈니스 로직을 처리하고,
Repository는 DB에 접근한다.

즉, Repository는 이런 일을 담당한다.

```text
게시글 저장
게시글 전체 조회
게시글 단건 조회
게시글 삭제
게시글 수정 대상 조회
```

그런데 이걸 매번 직접 구현하면 너무 귀찮다.

예를 들어 원래라면 이런 메서드를 직접 만들어야 한다.

```java
public Board save(Board board) {
    // DB 저장 로직
}

public List<Board> findAll() {
    // DB 전체 조회 로직
}

public Optional<Board> findById(Long id) {
    // DB 단건 조회 로직
}
```

하지만 Spring Data JPA는 이 반복 코드를 줄여준다.

그래서 우리는 인터페이스 하나만 만들면 된다.

```java
public interface BoardRepository extends JpaRepository<Board, Long> {
}
```

---

# 2. 클래스와 인터페이스의 차이

여기서 중요한 게 있다.

`BoardRepository`는 class가 아니라 interface다.

```java
public interface BoardRepository extends JpaRepository<Board, Long> {
}
```

클래스와 인터페이스를 아주 단순하게 구분하면 이렇다.

```text
class      : 실제 동작을 가진 구현체
interface  : 이런 기능을 가져야 한다고 약속하는 통로
```

클래스는 직접 객체를 만들고 동작을 구현한다.

```java
public class BoardService {
    public void createBoard() {
        // 실제 코드
    }
}
```

인터페이스는 “이런 메서드가 있다”는 형태를 정의한다.

```java
public interface BoardRepository {
    Board save(Board board);
}
```

그런데 Spring Data JPA에서는 우리가 인터페이스만 만들어도, Spring이 실행 시점에 구현체를 자동으로 만들어준다.

그래서 우리는 이런 코드를 직접 만들지 않아도 된다.

```java
public class BoardRepositoryImpl implements BoardRepository {
    // save, findAll, findById 직접 구현
}
```

Spring Data JPA가 대신 만들어준다.

---

# 3. 왜 @Repository 어노테이션이 없을까?

보통 Repository라면 이렇게 써야 할 것 같다.

```java
@Repository
public interface BoardRepository extends JpaRepository<Board, Long> {
}
```

그런데 실제로는 이렇게만 써도 동작한다.

```java
public interface BoardRepository extends JpaRepository<Board, Long> {
}
```

왜냐하면 `JpaRepository`를 상속받은 인터페이스는 Spring Data JPA가 Repository로 인식하기 때문이다.

즉, `@Repository`를 직접 붙이지 않아도 Spring이 알아서 Bean으로 등록해준다.

정리하면 이렇다.

```text
일반 Repository 직접 구현
→ @Repository 필요할 수 있음

JpaRepository 상속
→ Spring Data JPA가 자동으로 Repository로 인식
```

그래서 `BoardRepository`에 어노테이션이 없어도 정상 동작한다.

---

# 4. JpaRepository 안에는 이미 메서드가 많다

우리가 만든 코드는 비어 있다.

```java
public interface BoardRepository extends JpaRepository<Board, Long> {
}
```

하지만 상속받은 `JpaRepository` 안으로 들어가 보면 여러 메서드가 이미 있다.

예를 들면 이런 메서드들이다.

```java
void flush();

<S extends T> S saveAndFlush(S entity);

<S extends T> List<S> saveAllAndFlush(Iterable<S> entities);

void deleteAllInBatch();

T getReferenceById(ID id);

List<T> findAll();

List<T> findAllById(Iterable<ID> ids);
```

그리고 `JpaRepository`는 또 다른 인터페이스들을 상속받고 있다.

```java
public interface JpaRepository<T, ID>
        extends ListCrudRepository<T, ID>,
                ListPagingAndSortingRepository<T, ID>,
                QueryByExampleExecutor<T> {
}
```

여기서 중요한 건 이것이다.

`JpaRepository` 하나만 상속받은 것처럼 보이지만, 실제로는 그 안에서 여러 Repository 기능을 줄줄이 상속받고 있다.

그래서 우리가 쓸 수 있는 기능이 많아지는 것이다.

---

# 5. BoardRepository가 비어 있어도 되는 이유

다시 이 코드를 보자.

```java
public interface BoardRepository extends JpaRepository<Board, Long> {
}
```

여기서 `<Board, Long>`은 의미가 있다.

```java
JpaRepository<Board, Long>
```

첫 번째 `Board`는 이 Repository가 다룰 Entity 타입이다.

두 번째 `Long`은 Entity의 ID 타입이다.

즉, 이 코드는 이렇게 해석할 수 있다.

```text
BoardRepository는 Board 엔티티를 다룬다.
Board의 기본키 타입은 Long이다.
그리고 JpaRepository가 제공하는 기본 DB 기능을 사용한다.
```

그래서 Service에서 이렇게 쓸 수 있다.

```java
boardRepository.save(board);
```

```java
boardRepository.findAll();
```

```java
boardRepository.findById(id);
```

```java
boardRepository.deleteById(id);
```

우리가 직접 구현한 적은 없지만, JpaRepository가 이미 제공하고 있기 때문이다.

---

# 6. “상속을 안 받음”이 아니라 “엄청 많이 받고 있음”

처음 보면 `BoardRepository` 안이 비어 있으니까 아무것도 안 받는 것처럼 보인다.

하지만 실제로는 반대다.

```java
public interface BoardRepository extends JpaRepository<Board, Long> {
}
```

이 한 줄 때문에 `BoardRepository`는 JpaRepository의 기능을 모두 물려받는다.

그리고 JpaRepository는 또 다른 인터페이스들을 물려받는다.

흐름으로 보면 이렇다.

```text
BoardRepository
→ JpaRepository
→ ListCrudRepository
→ Repository 계열 인터페이스들
```

그래서 `BoardRepository`는 비어 있지만, 실제로는 많은 메서드를 사용할 수 있다.

비어 있는 게 아니라, 이미 상속받은 기능이 충분해서 추가로 쓸 게 없는 것이다.

---

# 7. 그럼 언제 Repository 안에 메서드를 추가할까?

기본 CRUD만 할 거면 비워둬도 된다.

```java
public interface BoardRepository extends JpaRepository<Board, Long> {
}
```

하지만 특정 조건으로 조회하고 싶으면 메서드를 추가한다.

예를 들어 작성자로 게시글을 찾고 싶다면 이렇게 쓸 수 있다.

```java
List<Board> findByAuthor(String author);
```

제목에 특정 단어가 들어간 게시글을 찾고 싶다면 이렇게 쓸 수 있다.

```java
List<Board> findByTitleContaining(String keyword);
```

그러면 전체 코드는 이렇게 된다.

```java
public interface BoardRepository extends JpaRepository<Board, Long> {

    List<Board> findByAuthor(String author);

    List<Board> findByTitleContaining(String keyword);
}
```

이것도 구현 코드는 없다.

Spring Data JPA가 메서드 이름을 보고 쿼리를 만들어준다.

```text
findByAuthor
→ author 컬럼으로 조회

findByTitleContaining
→ title에 특정 문자열이 포함된 데이터 조회
```

이게 Spring Data JPA의 장점이다.

---

# 8. Repository를 직접 구현하지 않는 이유

직접 JDBC로 DB를 다룬다면 이런 코드가 필요하다.

```java
Connection connection = dataSource.getConnection();
PreparedStatement statement = connection.prepareStatement("select * from board");
ResultSet resultSet = statement.executeQuery();
```

그리고 결과를 다시 자바 객체로 바꿔야 한다.

```java
Board board = new Board();
board.setTitle(resultSet.getString("title"));
board.setContent(resultSet.getString("content"));
```

이런 코드는 반복이 많고 실수하기 쉽다.

JPA와 Spring Data JPA를 쓰면 이런 반복을 줄일 수 있다.

```java
List<Board> boards = boardRepository.findAll();
```

한 줄이면 된다.

그래서 Repository가 비어 있는 것처럼 보여도 실제로는 Spring Data JPA가 뒤에서 많은 일을 해주고 있는 것이다.

---

# 9. 정리

처음에는 이 코드가 이상해 보인다.

```java
public interface BoardRepository extends JpaRepository<Board, Long> {
}
```

왜냐하면 안에 아무것도 없기 때문이다.

하지만 핵심은 `extends JpaRepository<Board, Long>`이다.

이 한 줄 때문에 `BoardRepository`는 기본적인 DB 기능을 사용할 수 있다.

```text
save()
findAll()
findById()
deleteById()
flush()
saveAndFlush()
findAllById()
```

그리고 `@Repository`가 없어도 되는 이유는 Spring Data JPA가 `JpaRepository`를 상속한 인터페이스를 자동으로 Repository Bean으로 등록해주기 때문이다.

최종 정리하면 이렇다.

```text
BoardRepository는 비어 있는 게 아니다.
JpaRepository가 제공하는 기능을 상속받고 있는 것이다.

인터페이스는 DB 접근 통로 역할을 한다.
실제 구현체는 Spring Data JPA가 자동으로 만들어준다.

그래서 우리는 반복적인 CRUD 코드를 직접 만들지 않아도 된다.
```

한 줄로 말하면:

> Repository가 텅 비어 있어도 동작하는 이유는 JpaRepository를 상속받았고, Spring Data JPA가 구현체를 자동으로 만들어주기 때문이다.
