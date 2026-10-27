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
  <title>Spring2 · GitLab에 매일 push하며 /post CRUD API 만들기</title>
  <meta name="description" content="VS Code에서 Spring Initializr 프로젝트를 GitLab에 처음 올리고 매일 commit·push하는 가이드. GET /post, GET /post/{id}, POST /post, PUT /post/{id}, DELETE /post/{id}를 하나씩 구현하고 검증합니다.">
  <link rel="stylesheet" href="guide.css">
</head>
<body>
  <nav class="topbar" aria-label="블로그 이동"><a href="../index.html">← Greenapple0101 · 홈</a><a href="../topics/spring.html">기존 Spring 글 보기</a></nav>
  <header class="hero"><div class="hero-inner">
    <div class="eyebrow">SPRING2 / GITLAB · CRUD 실습</div>
    <h1>GitLab에 매일 기록하고,<br>/post CRUD 완성하기.</h1>
    <p class="lead">VS Code에서 Initializr 프로젝트를 시작합니다.<br>API 5개를 하나씩 구현하고, 확인한 작업을 매일 commit·push합니다.</p>
    <div class="tags"><span>VS Code</span><span>GitLab · commit · push</span><span>Spring Boot 4.1.2</span><span>Java 21 · Maven</span><span>CRUD API 5개</span><span>2026.10.27</span></div>
  </div></header>
  <main class="layout">
    <nav class="toc" aria-label="가이드 목차"><strong>이 순서대로 따라 하세요</strong><ol>
      <li><a href="#before">과제 요구조건 확인</a></li><li><a href="#settings">Initializr ZIP 다운로드</a></li>
      <li><a href="#ide">VS Code 개발 환경</a></li><li><a href="#gitlab">GitLab 최초 업로드</a></li>
      <li><a href="#database">DB와 공통 코드</a></li><li><a href="#get-list">GET /post · 목록</a></li>
      <li><a href="#get-detail">GET /post/{id} · 상세</a></li><li><a href="#create">POST /post · 등록</a></li>
      <li><a href="#update">PUT /post/{id} · 수정</a></li><li><a href="#delete">DELETE /post/{id} · 삭제</a></li>
      <li><a href="#verify">CRUD 요청·응답 검증</a></li><li><a href="#frontend">JavaScript 화면 연결</a></li>
      <li><a href="#daily">매일 commit·push</a></li><li><a href="#react-vue">React/Vue 연결</a></li>
      <li><a href="#next">완료 기준과 오류 해결</a></li>
    </ol></nav>
    <article class="article">''' + body + '''</article>
  </main>
  <footer class="footer"><span>© 2026 Greenapple0101 · Spring2</span><span><a href="guide.md">가이드 원문</a> · <a href="../index.html">홈으로 돌아가기</a></span></footer>
</body>
</html>
'''
(root / 'index.html').write_text(page, encoding='utf-8')
print('Built spring2/index.html')
