# Greenapple0101.github.io

개발 학습 기록을 GitHub Pages로 보여주는 정적 블로그입니다.

- 사이트: https://greenapple0101.github.io/
- 원본 글: `../git-pages/` (마크다운 원본)

## 빌드

```bash
pip install markdown
python build.py
```

`git-pages`의 md를 `posts/`에 복사하고, 각 글 HTML과 `index.html`을 생성합니다.

## 구조

- `build.py` — 사이트 생성 스크립트
- `posts/*.md` — 마크다운 원본
- `posts/*.html` — 생성된 글 페이지
- `index.html` — 글 목록 (검색·태그 필터)
- `style.css` / `post.css` — 스타일
