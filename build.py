#!/usr/bin/env python3
"""Velog markdown → GitHub Pages static site builder."""

from __future__ import annotations

import html
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
POSTS_SRC = ROOT.parent / "velog-posts"
POSTS_DIR = ROOT / "posts"
MD = markdown.Markdown(
    extensions=["fenced_code", "tables", "sane_lists", "smarty"],
    output_format="html5",
)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
FIELD_RE = re.compile(r'^(\w+):\s*(?:"((?:\\.|[^"\\])*)"|\'((?:\\.|[^\'\\])*)\'|(.+))$', re.MULTILINE)

KUBERNETES_CATEGORY = "Kubernetes"

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
        "helm",
        "argo",
        "argocd",
        "dockerk3d",
    }
)

CATEGORY_COLORS = {
    "SPRING": "#16a34a",
    "Spring": "#16a34a",
    "DOCKER": "#0ea5e9",
    "Docker": "#0ea5e9",
    "Kubernetes": "#7c3aed",
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


def category_color(category: str) -> str:
    for key, color in CATEGORY_COLORS.items():
        if category.lower().startswith(key.lower()) or key.lower() in category.lower():
            return color
    return "#64748b"


def format_date(iso: str) -> str:
    if not iso:
        return ""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y.%m.%d")
    except ValueError:
        return iso[:10].replace("-", ".")


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
    <a class="back-link" href="../index.html">← 글 목록</a>
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
<body>
  <header>
    <p class="small-title">Greenapple0101</p>
    <h1>Dev Blog Archive</h1>
    <p class="description">
      Velog에서 백업한 학습 기록 {count}편 — Spring, Kubernetes, Docker, AI, 네트워크, 알고리즘 등.
    </p>
    <div class="stats">
      <span class="stat"><strong>{count}</strong> posts</span>
      <span class="stat"><strong>{category_count}</strong> topics</span>
    </div>
  </header>

  <main>
    <div class="toolbar">
      <input type="search" id="search" placeholder="제목·태그 검색…" autocomplete="off" />
      <div class="filter-tags" id="filter-tags"></div>
    </div>
    <p class="result-count" id="result-count"></p>
    <div class="post-list" id="post-list">
{cards}
    </div>
    <p class="empty-state" id="empty-state" hidden>검색 결과가 없습니다.</p>
    <nav class="pagination" id="pagination" aria-label="페이지" hidden></nav>
  </main>

  <footer>
    <p>© 2026 <a href="https://github.com/Greenapple0101">Greenapple0101</a> · Velog backup archive</p>
  </footer>
  <script src="app.js"></script>
</body>
</html>
"""

CARD_TEMPLATE = """      <a class="post-card" href="posts/{slug}.html" data-title="{title_lower}" data-tags="{tags_lower}" data-category="{category}" data-published="{published}">
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

  parts.append('<a class="post-nav-home" href="../index.html">목록</a>')

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
    published = meta.get("published", "")
    return {
        "slug": slug,
        "title": title,
        "category": category,
        "tags": tags,
        "published": published,
        "date": format_date(published),
        "excerpt": excerpt(body),
        "tag_color": category_color(category),
    }


def build_post(
    slug: str,
    meta: dict[str, str],
    body: str,
    *,
    prev_entry: dict | None = None,
    next_entry: dict | None = None,
) -> None:
    title = meta.get("title", slug.replace("-", " "))
    tags = meta.get("tags", "")
    category = category_from_slug(slug, tags)
    tag_color = category_color(category)
    published = meta.get("published", "")
    source = meta.get("source", "")

    MD.reset()
    content_html = MD.convert(body)

    date_html = ""
    if published:
        date_html = f'<time datetime="{html.escape(published)}">{format_date(published)}</time>'

    source_html = ""
    if source:
        source_html = (
            f'<a class="velog-link" href="{html.escape(source)}" target="_blank" rel="noopener">Velog 원문</a>'
        )

    description = html.escape(excerpt(body, 160))
    page = POST_HTML.format(
        title=html.escape(title),
        description=description,
        tag_color=tag_color,
        category=html.escape(category),
        date_html=date_html,
        source_html=source_html,
        content=content_html,
        post_nav=post_nav_html(prev_entry, next_entry),
    )

    out_path = POSTS_DIR / f"{slug}.html"
    out_path.write_text(page, encoding="utf-8")


def build_index(entries: list[dict]) -> None:
    entries.sort(key=lambda e: e.get("published") or "", reverse=True)

    cards = []
    for e in entries:
        cards.append(
            CARD_TEMPLATE.format(
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
        )

    categories = sorted({e["category"] for e in entries}, key=str.lower)
    index = INDEX_HTML.format(
        count=len(entries),
        category_count=len(categories),
        cards="\n".join(cards),
    )
    (ROOT / "index.html").write_text(index, encoding="utf-8")

    posts_json = [
        {
            "slug": e["slug"],
            "title": e["title"],
            "category": e["category"],
            "tags": e.get("tags", ""),
            "date": e.get("date", ""),
            "excerpt": e.get("excerpt", ""),
            "tag_color": e["tag_color"],
        }
        for e in entries
    ]
    (ROOT / "posts.json").write_text(
        json.dumps(posts_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def sync_markdown() -> list[Path]:
    if POSTS_DIR.exists():
        shutil.rmtree(POSTS_DIR)
    POSTS_DIR.mkdir(parents=True)

    if not POSTS_SRC.is_dir():
        raise SystemExit(f"Source not found: {POSTS_SRC}")

    files = sorted(POSTS_SRC.glob("*.md"))
    for src in files:
        shutil.copy2(src, POSTS_DIR / src.name)
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

    prepared.sort(key=lambda item: item[0].get("published") or "", reverse=True)

    entries: list[dict] = []
    for i, (meta, body, slug) in enumerate(prepared):
        entry = collect_entry(slug, meta, body)
        entries.append(entry)

    for i, (meta, body, slug) in enumerate(prepared):
        older = entries[i + 1] if i + 1 < len(entries) else None
        newer = entries[i - 1] if i > 0 else None
        prev_nav = {"slug": older["slug"], "title": older["title"]} if older else None
        next_nav = {"slug": newer["slug"], "title": newer["title"]} if newer else None
        build_post(slug, meta, body, prev_entry=prev_nav, next_entry=next_nav)

    print("Building index...")
    build_index(entries)
    print(f"Done. {len(entries)} posts → {ROOT}")


if __name__ == "__main__":
    main()
