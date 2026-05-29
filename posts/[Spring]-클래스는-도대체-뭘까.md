---
title: "[SPRING] 클래스는 도대체 뭘까?"
source: "https://velog.io/@yorange50/SPRING-클래스는-도대체-뭘까"
published: "2026-04-28T05:56:22.952Z"
tags: "Spring"
backup_date: "2026-05-29T14:52:52.789093"
---

스프링을 공부하다 보면 이런 코드를 자주 보게 된다.

```java
public class BoardService {
    
    public List<String> getBoards() {
        return List.of("게시글1", "게시글2", "게시글3");
    }

    public String createBoard(String title) {
        return "생성됨: " + title;
    }
}
```

처음 보면 이런 생각이 든다.

“클래스가 뭔데 자꾸 나오는 거지?”

## 클래스는 기능을 담아두는 상자다

클래스를 아주 쉽게 말하면 **기능들을 담아두는 상자**다.

예를 들어 게시판과 관련된 기능이 있다고 해보자.

게시글 목록을 보여주는 기능
게시글을 만드는 기능
게시글을 삭제하는 기능
게시글을 수정하는 기능

이런 기능들이 여기저기 흩어져 있으면 나중에 찾기도 어렵고 고치기도 어렵다.

그래서 게시판과 관련된 기능은 하나의 상자에 담아둔다.

그 상자의 이름이 `BoardService`다.

```java
public class BoardService {
}
```

이 코드는 이렇게 읽으면 된다.

> BoardService라는 이름의 상자를 만들겠다

## 클래스 안에는 기능을 넣을 수 있다

상자만 만들면 아무 일도 하지 못한다.
그래서 그 안에 기능을 넣는다.

```java
public class BoardService {

    public List<String> getBoards() {
        return List.of("게시글1", "게시글2", "게시글3");
    }
}
```

여기서 `getBoards()`는 게시글 목록을 가져오는 기능이다.

즉,

```java
public class BoardService
```

는 게시판 기능을 담는 상자이고,

```java
getBoards()
```

는 그 상자 안에 들어 있는 기능이다.

## 메서드는 클래스 안에 들어 있는 기능이다

자바에서는 기능을 보통 **메서드**라고 부른다.

```java
public String createBoard(String title) {
    return "생성됨: " + title;
}
```

이건 게시글을 만드는 기능이다.

그래서 이렇게 볼 수 있다.

```text
BoardService 클래스
 ├── getBoards() 기능
 └── createBoard() 기능
```

즉, 클래스는 여러 기능을 묶어두는 공간이고,
메서드는 그 안에 들어 있는 실제 기능이다.

## 왜 굳이 클래스로 묶을까?

만약 클래스가 없으면 게시판 기능, 회원 기능, 댓글 기능, 주문 기능이 전부 섞일 수 있다.

그러면 코드를 읽을 때 이런 문제가 생긴다.

“게시판 기능이 어디 있지?”
“회원 기능은 어디에 있지?”
“이 함수는 누가 쓰는 거지?”

그래서 자바는 기능들을 역할별로 묶는다.

게시판 기능은 `BoardService`
회원 기능은 `UserService`
댓글 기능은 `CommentService`

이렇게 이름을 붙여서 정리한다.

## 비유하면 폴더와 비슷하다

컴퓨터에서 사진 파일, 문서 파일, 음악 파일을 전부 바탕화면에 두면 지저분하다.

그래서 보통 폴더를 만든다.

```text
사진 폴더
문서 폴더
음악 폴더
```

클래스도 비슷하다.

```text
BoardService → 게시판 기능 폴더
UserService → 회원 기능 폴더
CommentService → 댓글 기능 폴더
```

관련 있는 기능들을 한곳에 모아두기 위한 것이다.

## 클래스와 객체는 뭐가 다를까?

여기서 하나 더 헷갈리는 단어가 나온다.
바로 **객체**다.

클래스는 설계도이고,
객체는 그 설계도로 실제로 만든 것이다.

예를 들어 붕어빵 틀이 있다고 해보자.

붕어빵 틀은 클래스다.
그 틀로 찍어낸 붕어빵은 객체다.

```text
클래스 = 붕어빵 틀
객체 = 실제 붕어빵
```

자바 코드로 보면 이렇게 된다.

```java
BoardService boardService = new BoardService();
```

여기서

```text
BoardService = 클래스
boardService = 객체
new BoardService() = 클래스로 객체를 만드는 것
```

## 스프링에서는 객체를 직접 만들지 않는 경우가 많다

일반 자바에서는 보통 이렇게 객체를 만든다.

```java
BoardService boardService = new BoardService();
```

그런데 스프링에서는 이런 코드를 직접 많이 쓰지 않는다.

대신 클래스 위에 이런 표시를 붙인다.

```java
@Service
public class BoardService {
}
```

이 뜻은 간단히 말하면 이거다.

> 이 클래스는 스프링이 알아서 객체로 만들어서 관리해줘

그래서 스프링에서는 클래스가 더 중요해진다.
왜냐하면 클래스가 있어야 스프링이 그걸 보고 객체를 만들 수 있기 때문이다.

## 정리

클래스는 어렵게 생각할 필요가 없다.

클래스는 **관련 있는 기능들을 묶어두는 상자**다.

게시판 기능은 게시판 클래스에,
회원 기능은 회원 클래스에,
댓글 기능은 댓글 클래스에 넣는다.

그리고 그 클래스 안에 들어 있는 실제 기능을 메서드라고 부른다.

마지막으로 클래스와 객체의 차이는 이렇게 이해하면 된다.

```text
클래스 = 설계도
객체 = 설계도로 실제 만든 것
메서드 = 클래스 안에 들어 있는 기능
```

## 한 줄 결론

> 클래스는 관련 있는 기능들을 한곳에 모아두기 위한 자바의 기본 상자다.
