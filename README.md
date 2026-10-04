# Greenapple0101.github.io

개발 학습 기록을 GitHub Pages로 보여주는 정적 블로그입니다.

- 사이트: https://greenapple0101.github.io/
- 원본 글: 이 저장소의 `posts/*.md`

## 빌드와 검증

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python build.py
.venv/bin/python -m unittest discover -s tests -v
```

빌드는 `posts/`의 원본을 보존하며 HTML, 홈, 주제별 목록과 `posts.json`을 갱신합니다.
별도의 로컬 폴더나 외부 백업 파일에 의존하지 않습니다.

## 글 분류

프런트매터의 `topic`과 `category`로 글의 폴더와 배지를 지정합니다.
파일명에 예전 분류가 남아 있어도 이 설정이 우선하며, 기존 글 주소는 유지됩니다.

```yaml
---
title: "[Spring] API 개발 기록"
topic: "spring"
category: "Spring"
---
```

`topic`은 `docker-k8s`, `ai`, `upstage`, `spring`, `algorithm`, `web` 중 하나입니다.
업스테이지 폴더에는 사업·제품·Solar API 활용과 회사 기술면접 글을 넣고,
일반 RAG·OCR 개념은 AI, 배포 자동화는 Docker & Kubernetes 등으로 분류합니다.
분류가 없으면 기존 태그·파일명 규칙을 사용합니다.
기존 주소의 Unicode 표현을 고정해야 하는 글은 `slug`를 명시할 수 있습니다.

코드 블록은 시작과 끝의 백틱 개수를 맞추고, 언어명 뒤의 편집 도구용 `id`는 제거합니다.

## 구조

- `build.py` — 사이트 생성 스크립트
- `posts/*.md` — 마크다운 원본
- `posts/*.html` — 생성된 글 페이지
- `topics/*.html` — 폴더별 목록·검색·페이지 이동
- `index.html` / `posts.json` — 폴더 목록·글 메타데이터
- `style.css` / `post.css` — 스타일
- `tests/` — 분류, 렌더링, 원본 보존, 내부 링크 검증
