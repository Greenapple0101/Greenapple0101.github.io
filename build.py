#!/usr/bin/env python3
"""Markdown → GitHub Pages static site builder."""

from __future__ import annotations

import html
import json
import re
import shutil
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
POSTS_SRC = ROOT.parent / "git-pages"
POSTS_DIR = ROOT / "posts"
MD = markdown.Markdown(
    extensions=["fenced_code", "tables", "sane_lists", "smarty"],
    output_format="html5",
)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
FIELD_RE = re.compile(r'^(\w+):\s*(?:"((?:\\.|[^"\\])*)"|\'((?:\\.|[^\'\\])*)\'|(.+))$', re.MULTILINE)

KUBERNETES_CATEGORY = "Kubernetes"
TOPICS_DIR = ROOT / "topics"

# Folder groups shown on the home page (order matters).
TOPIC_FOLDERS: list[dict[str, str]] = [
    {
        "id": "docker-k8s",
        "title": "Docker & Kubernetes",
        "description": "Docker, Kubernetes, CKA, Helm, k3d, Argo CD 등 인프라·컨테이너",
        "color": "#7c3aed",
    },
    {
        "id": "ai",
        "title": "AI",
        "description": "AI Infra, 딥러닝, PyTorch, RAG, MLOps 등",
        "color": "#db2777",
    },
    {
        "id": "upstage",
        "title": "Upstage",
        "description": "Solar LLM, Document Parse, Embedding, RAG, API 모니터링 등",
        "color": "#0d9488",
    },
    {
        "id": "spring",
        "title": "Spring",
        "description": "Spring Boot, JPA, API, 배포 실습 등",
        "color": "#16a34a",
    },
    {
        "id": "algorithm",
        "title": "알고리즘",
        "description": "LeetCode, 투포인터, 자료구조 등",
        "color": "#ca8a04",
    },
    {
        "id": "web",
        "title": "웹 · 기타",
        "description": "네트워크, DB, 보안, NGINX, HA, Linux, CI/CD 등",
        "color": "#ea580c",
    },
]

TOPIC_BY_ID = {t["id"]: t for t in TOPIC_FOLDERS}

# Filename/tag prefixes that should appear under one Kubernetes filter.
KUBERNETES_PREFIXES = frozenset(
    {
        "kubernetes",
        "kuberentes",
        "k8s",
        "cka",
        "ckakubernetes",
        "k3dkubernetes",
        "k3d",
        "k3d-kubernetes",
        "helm",
        "argo",
        "argocd",
        "argo-cd",
        "dockerk3d",
        "docker-k3d",
        "network",
    }
)

CATEGORY_COLORS = {
    "SPRING": "#16a34a",
    "Spring": "#16a34a",
    "DOCKER": "#0ea5e9",
    "Docker": "#0ea5e9",
    "CI/CD": "#64748b",
    "CI-CD": "#64748b",
    "Kubernetes": "#7c3aed",
    "AI Infra": "#db2777",
    "AI-Infra": "#db2777",
    "Argo CD": "#7c3aed",
    "Argo-CD": "#7c3aed",
    "AI": "#db2777",
    "DL": "#db2777",
    "PyTorch": "#db2777",
    "CS": "#db2777",
    "NETWORK": "#ea580c",
    "SECURITY": "#dc2626",
    "DATABASE": "#0891b2",
    "HA": "#0891b2",
    "CICD": "#64748b",
    "CICDFROM": "#64748b",
    "알고리즘": "#ca8a04",
    "LeetCode": "#ca8a04",
    "Thymeleaf": "#16a34a",
    "Upstage": "#0d9488",
    "hello": "#64748b",
}


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text

    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        m = FIELD_RE.match(line.strip())
        if not m:
            continue
        key = m.group(1)
        value = m.group(2) or m.group(3) or (m.group(4) or "").strip()
        meta[key] = value

    body = text[match.end() :]
    return meta, body


def slug_from_filename(path: Path) -> str:
    return path.stem


def _slug_prefix(slug: str) -> str:
    bracket = re.match(r"^\[([^\]]+)\]", slug)
    if bracket:
        return bracket.group(1).strip()
    return slug.split("-")[0].strip()


def normalize_category(category: str) -> str:
    key = re.sub(r"^\[|\]$", "", category.strip()).lower()
    if key in KUBERNETES_PREFIXES or "kubernetes" in key:
        return KUBERNETES_CATEGORY
    return category.strip() or "기타"


def category_from_slug(slug: str, tags: str) -> str:
    if tags:
        first = tags.split(",")[0].strip()
        if first:
            return normalize_category(first)
    prefix = _slug_prefix(slug)
    return normalize_category(prefix) if prefix else "기타"


def topic_for_entry(category: str, slug: str) -> str:
    """Map a post to one of the topic folder groups on the home page."""
    prefix = _slug_prefix(slug).lower()
    cat_key = re.sub(r"^\[|\]$", "", category.strip()).lower()

    upstage_keys = frozenset(
        {"upstage", "업스테이지", "rag", "rag/mlops", "rag-mlops", "ragmlops"}
    )
    if cat_key in upstage_keys or prefix in upstage_keys:
        return "upstage"

    algorithm_keys = frozenset({"알고리즘", "leetcode", "algorithm", "알고리즘"})
    if cat_key in algorithm_keys or prefix in algorithm_keys:
        return "algorithm"
    if "알고리즘" in cat_key or cat_key == "알고리즘":
        return "algorithm"

    spring_keys = frozenset({"spring", "springjpa", "thymeleaf"})
    if cat_key in spring_keys or prefix in spring_keys or cat_key.startswith("spring"):
        return "spring"

    ai_keys = frozenset({"ai", "ai-infra", "dl", "pytorch", "ml", "cs"})
    if cat_key in ai_keys or prefix in ai_keys:
        return "ai"

    docker_k8s_keys = KUBERNETES_PREFIXES | frozenset(
        {
            "docker",
            "kubernetes",
            "k8s",
            "dockerdocker",
            "cicdfrom",
            "argo-cd",
            "ci-cd",
            "ci/cd",
            "helm",
            "cka",
            "network",
            "docker-k3d",
        }
    )
    if (
        cat_key in docker_k8s_keys
        or prefix in docker_k8s_keys
        or normalize_category(category) == KUBERNETES_CATEGORY
    ):
        return "docker-k8s"

    return "web"


def category_color(category: str) -> str:
    for key, color in CATEGORY_COLORS.items():
        if category.lower().startswith(key.lower()) or key.lower() in category.lower():
            return color
    return "#64748b"


def parse_published_date(value: str) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        pass
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        pass
    return None


def published_sort_key(entry: dict) -> float:
    dt = parse_published_date(entry.get("published", ""))
    if dt is None:
        return 0.0
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def format_date(iso: str) -> str:
    dt = parse_published_date(iso)
    if dt is None:
        return ""
    return dt.strftime("%Y.%m.%d")


def excerpt(body: str, limit: int = 120) -> str:
    text = re.sub(r"```[\s\S]*?```", " ", body)
    text = re.sub(r"[#>*`\[\]()]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


POST_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} | Greenapple0101</title>
  <meta name="description" content="{description}" />
  <link rel="stylesheet" href="../style.css" />
  <link rel="stylesheet" href="../post.css" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css" />
</head>
<body class="post-page">
  <header class="post-header">
    <nav class="breadcrumb" aria-label="경로">
      <a href="../index.html">홈</a>
      <span aria-hidden="true">/</span>
      <a href="../topics/{topic_id}.html">{topic_title}</a>
    </nav>
    <span class="tag" style="--tag-color: {tag_color}">{category}</span>
    <h1>{title}</h1>
    <div class="post-meta">
      {date_html}
      {source_html}
    </div>
  </header>
  <article class="post-content">
{content}
  </article>
{post_nav}
  <footer>
    <p><a href="../index.html">Greenapple0101 Blog</a></p>
  </footer>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <script>hljs.highlightAll();</script>
</body>
</html>
"""

INDEX_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Greenapple0101 | Dev Blog Archive</title>
  <meta name="description" content="Spring, Kubernetes, Docker, AI Infra 등 개발 학습 기록 아카이브" />
  <link rel="stylesheet" href="style.css" />
</head>
<body class="home-page">
  <header>
    <p class="small-title">Greenapple0101</p>
    <h1>Dev Blog Archive</h1>
    <p class="description">
      학습 기록 {count}편 — 주제 폴더를 선택해 글을 찾아보세요.
    </p>
    <div class="stats">
      <span class="stat"><strong>{count}</strong> posts</span>
      <span class="stat"><strong>{folder_count}</strong> folders</span>
    </div>
  </header>

  <main>
    <p class="folder-hint">주제별 폴더</p>
    <div class="folder-grid">
{folders}
    </div>
  </main>

  <footer>
    <p>© 2026 <a href="https://github.com/Greenapple0101">Greenapple0101</a> · Dev Blog</p>
  </footer>
</body>
</html>
"""

TOPIC_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{topic_title} | Greenapple0101</title>
  <meta name="description" content="{topic_description}" />
  <link rel="stylesheet" href="../style.css" />
</head>
<body class="topic-page">
  <header class="topic-header" style="--topic-color: {topic_color}">
    <a class="back-link" href="../index.html">← 홈</a>
    <p class="small-title">폴더</p>
    <h1>{topic_title}</h1>
    <p class="description">{topic_description}</p>
    <span class="stat"><strong>{count}</strong> posts</span>
  </header>

  <main>
    <div class="toolbar">
      <input type="search" id="search" placeholder="이 폴더에서 제목 검색…" autocomplete="off" />
    </div>
    <p class="result-count" id="result-count"></p>
    <div class="post-list" id="post-list">
{cards}
    </div>
    <p class="empty-state" id="empty-state" hidden>검색 결과가 없습니다.</p>
    <nav class="pagination" id="pagination" aria-label="페이지" hidden></nav>
  </main>

  <footer>
    <p>© 2026 <a href="https://github.com/Greenapple0101">Greenapple0101</a> · Dev Blog</p>
  </footer>
  <script src="../topic.js"></script>
</body>
</html>
"""

FOLDER_CARD_TEMPLATE = """      <a class="folder-card" href="topics/{id}.html" style="--folder-color: {color}">
        <div class="folder-card-top">
          <span class="folder-badge">{count}편</span>
        </div>
        <h2>{title}</h2>
        <p>{description}</p>
      </a>
"""

CARD_TEMPLATE = """      <a class="post-card" href="{post_href}" data-title="{title_lower}" data-tags="{tags_lower}" data-category="{category}" data-published="{published}">
        <div class="card-top">
          <span class="tag" style="--tag-color: {tag_color}">{category}</span>
          <time>{date}</time>
        </div>
        <h2>{title}</h2>
        <p>{excerpt}</p>
      </a>
"""


def post_nav_html(prev_entry: dict | None, next_entry: dict | None) -> str:
  """prev = older post, next = newer post (chronological)."""
  parts = ['<nav class="post-nav" aria-label="글 이동">']

  if prev_entry:
    parts.append(
      f'<a class="post-nav-link prev" href="{html.escape(prev_entry["slug"])}.html">'
      f'<span class="post-nav-label">이전 글</span>'
      f'<span class="post-nav-title">{html.escape(prev_entry["title"])}</span></a>'
    )
  else:
    parts.append('<span class="post-nav-link prev disabled" aria-hidden="true"></span>')

  parts.append('<a class="post-nav-home" href="../index.html">홈</a>')

  if next_entry:
    parts.append(
      f'<a class="post-nav-link next" href="{html.escape(next_entry["slug"])}.html">'
      f'<span class="post-nav-label">다음 글</span>'
      f'<span class="post-nav-title">{html.escape(next_entry["title"])}</span></a>'
    )
  else:
    parts.append('<span class="post-nav-link next disabled" aria-hidden="true"></span>')

  parts.append("</nav>")
  return "\n  ".join(parts)


def collect_entry(slug: str, meta: dict[str, str], body: str) -> dict:
    title = meta.get("title", slug.replace("-", " "))
    tags = meta.get("tags", "")
    category = category_from_slug(slug, tags)
    topic = topic_for_entry(category, slug)
    published = meta.get("published", "")
    return {
        "slug": slug,
        "title": title,
        "category": category,
        "topic": topic,
        "tags": tags,
        "published": published,
        "date": format_date(published),
        "excerpt": excerpt(body),
        "tag_color": category_color(category),
    }


def render_card(e: dict, *, post_href_prefix: str = "posts/") -> str:
    return CARD_TEMPLATE.format(
        post_href=html.escape(f"{post_href_prefix}{e['slug']}.html"),
        slug=html.escape(e["slug"]),
        title=html.escape(e["title"]),
        title_lower=html.escape(e["title"].lower()),
        tags_lower=html.escape((e.get("tags") or "").lower()),
        category=html.escape(e["category"]),
        tag_color=e["tag_color"],
        date=html.escape(e.get("date") or ""),
        published=html.escape(e.get("published") or ""),
        excerpt=html.escape(e.get("excerpt") or ""),
    )


def build_post(
    slug: str,
    meta: dict[str, str],
    body: str,
    *,
    topic_id: str,
    prev_entry: dict | None = None,
    next_entry: dict | None = None,
) -> None:
    title = meta.get("title", slug.replace("-", " "))
    tags = meta.get("tags", "")
    category = category_from_slug(slug, tags)
    tag_color = category_color(category)
    topic_meta = TOPIC_BY_ID[topic_id]
    published = meta.get("published", "")
    MD.reset()
    content_html = MD.convert(body)

    date_html = ""
    if published:
        date_html = f'<time datetime="{html.escape(published)}">{format_date(published)}</time>'

    source_html = ""

    description = html.escape(excerpt(body, 160))
    page = POST_HTML.format(
        title=html.escape(title),
        description=description,
        tag_color=tag_color,
        category=html.escape(category),
        topic_id=html.escape(topic_id),
        topic_title=html.escape(topic_meta["title"]),
        date_html=date_html,
        source_html=source_html,
        content=content_html,
        post_nav=post_nav_html(prev_entry, next_entry),
    )

    out_path = POSTS_DIR / f"{slug}.html"
    out_path.write_text(page, encoding="utf-8")


def build_index(entries: list[dict]) -> None:
    counts = {t["id"]: 0 for t in TOPIC_FOLDERS}
    for e in entries:
        counts[e["topic"]] = counts.get(e["topic"], 0) + 1

    folders = []
    for topic in TOPIC_FOLDERS:
        folders.append(
            FOLDER_CARD_TEMPLATE.format(
                id=html.escape(topic["id"]),
                title=html.escape(topic["title"]),
                description=html.escape(topic["description"]),
                color=topic["color"],
                count=counts.get(topic["id"], 0),
            )
        )

    index = INDEX_HTML.format(
        count=len(entries),
        folder_count=len(TOPIC_FOLDERS),
        folders="\n".join(folders),
    )
    (ROOT / "index.html").write_text(index, encoding="utf-8")

    sorted_entries = sorted(entries, key=published_sort_key, reverse=True)
    posts_json = [
        {
            "slug": e["slug"],
            "title": e["title"],
            "category": e["category"],
            "topic": e["topic"],
            "tags": e.get("tags", ""),
            "date": e.get("date", ""),
            "excerpt": e.get("excerpt", ""),
            "tag_color": e["tag_color"],
        }
        for e in sorted_entries
    ]
    (ROOT / "posts.json").write_text(
        json.dumps(posts_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def build_topic_pages(entries: list[dict]) -> None:
    TOPICS_DIR.mkdir(parents=True, exist_ok=True)

    by_topic: dict[str, list[dict]] = {t["id"]: [] for t in TOPIC_FOLDERS}
    for e in entries:
        by_topic.setdefault(e["topic"], []).append(e)

    for topic in TOPIC_FOLDERS:
        topic_id = topic["id"]
        topic_entries = sorted(
            by_topic.get(topic_id, []),
            key=published_sort_key,
            reverse=True,
        )
        cards = [render_card(e, post_href_prefix="../posts/") for e in topic_entries]
        page = TOPIC_HTML.format(
            topic_title=html.escape(topic["title"]),
            topic_description=html.escape(topic["description"]),
            topic_color=topic["color"],
            count=len(topic_entries),
            cards="\n".join(cards),
        )
        (TOPICS_DIR / f"{topic_id}.html").write_text(page, encoding="utf-8")


def sync_markdown() -> list[Path]:
    if POSTS_DIR.exists():
        shutil.rmtree(POSTS_DIR)
    POSTS_DIR.mkdir(parents=True)

    if not POSTS_SRC.is_dir():
        raise SystemExit(f"Source not found: {POSTS_SRC}")

    files = source_markdown_files()
    for src in files:
        dest_name = src.name if src.suffix == ".md" else f"{src.name}.md"
        shutil.copy2(src, POSTS_DIR / dest_name)
    return [POSTS_DIR / (f.name if f.suffix == ".md" else f"{f.name}.md") for f in files]


def source_markdown_files() -> list[Path]:
    """Collect markdown sources from git-pages."""
    files: list[Path] = []
    for path in sorted(POSTS_SRC.iterdir()):
        if path.is_file() and path.suffix == ".md" and not path.name.startswith("."):
            files.append(path)
    return files


def main() -> None:
    print("Syncing markdown files...")
    md_files = sync_markdown()
    print(f"  {len(md_files)} files → {POSTS_DIR}")

    prepared: list[tuple[dict[str, str], str, str]] = []
    for path in md_files:
        text = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)
        slug = slug_from_filename(path)
        prepared.append((meta, body, slug))

    entries: list[dict] = []
    slug_to_prepared: dict[str, tuple[dict[str, str], str]] = {}
    for meta, body, slug in prepared:
        entry = collect_entry(slug, meta, body)
        entries.append(entry)
        slug_to_prepared[slug] = (meta, body)

    by_topic: dict[str, list[dict]] = {t["id"]: [] for t in TOPIC_FOLDERS}
    for e in entries:
        by_topic.setdefault(e["topic"], []).append(e)
    for topic_id in by_topic:
        by_topic[topic_id].sort(key=published_sort_key, reverse=True)

    for e in entries:
        topic_entries = by_topic[e["topic"]]
        idx = next(i for i, x in enumerate(topic_entries) if x["slug"] == e["slug"])
        older = topic_entries[idx + 1] if idx + 1 < len(topic_entries) else None
        newer = topic_entries[idx - 1] if idx > 0 else None
        prev_nav = {"slug": older["slug"], "title": older["title"]} if older else None
        next_nav = {"slug": newer["slug"], "title": newer["title"]} if newer else None
        meta, body = slug_to_prepared[e["slug"]]
        build_post(
            e["slug"],
            meta,
            body,
            topic_id=e["topic"],
            prev_entry=prev_nav,
            next_entry=next_nav,
        )

    print("Building index & topic folders...")
    build_index(entries)
    build_topic_pages(entries)
    print(f"Done. {len(entries)} posts → {ROOT}")


if __name__ == "__main__":
    main()
