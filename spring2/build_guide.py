"""Rebuild the standalone Spring2 tutorial from its Markdown source."""
from pathlib import Path
import markdown

root = Path(__file__).resolve().parent
body = markdown.markdown((root / 'guide.md').read_text(encoding='utf-8'), extensions=['fenced_code', 'tables', 'attr_list', 'sane_lists'])
page = '''<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Spring2 · 게시판을 위한 Spring Initializr 설정 가이드</title>
  <meta name="description" content="실제 화면 캡처로 따라 하는 게시판 프로젝트 설정. Spring Initializr에서 생성한 Spring Boot 프로젝트를 VS Code에서 열고 Java 21, Maven, Thymeleaf, JPA, H2로 실행합니다.">
  <link rel="stylesheet" href="guide.css">
</head>
<body>
  <nav class="topbar" aria-label="블로그 이동"><a href="../index.html">← Greenapple0101 · 홈</a><a href="../topics/spring.html">기존 Spring 글 보기</a></nav>
  <header class="hero"><div class="hero-inner">
    <div class="eyebrow">SPRING2 / 첫 번째 실습</div>
    <h1>게시판 만들기, <br>Spring Initializr 설정부터</h1>
    <p class="lead">Spring Initializr 설정부터 VS Code에서 첫 실행까지.<br>실제 화면 캡처 4장과 함께 게시판 프로젝트의 시작을 준비합니다.</p>
    <div class="tags"><span>VS Code</span><span>Spring Boot 4.1.2</span><span>Java 21 · Maven</span><span>Thymeleaf · JPA · H2</span><span>2026.10.27</span></div>
  </div></header>
  <main class="layout">
    <nav class="toc" aria-label="가이드 목차"><strong>이 순서대로 따라 하세요</strong><ol>
      <li><a href="#before">실습 목표와 준비물</a></li><li><a href="#settings">프로젝트 기본값</a></li>
      <li><a href="#dependencies">의존성 6개 추가</a></li><li><a href="#generate">미리보기와 ZIP 다운로드</a></li>
      <li><a href="#ide">VS Code 설정과 프로젝트 열기</a></li><li><a href="#database">로컬 DB 설정</a></li>
      <li><a href="#run">첫 화면과 실행 확인</a></li><li><a href="#next">오류 해결과 다음 단계</a></li>
    </ol></nav>
    <article class="article">''' + body + '''</article>
  </main>
  <footer class="footer"><span>© 2026 Greenapple0101 · Spring2</span><span><a href="guide.md">가이드 원문</a> · <a href="../index.html">홈으로 돌아가기</a></span></footer>
</body>
</html>
'''
(root / 'index.html').write_text(page, encoding='utf-8')
print('Built spring2/index.html')
