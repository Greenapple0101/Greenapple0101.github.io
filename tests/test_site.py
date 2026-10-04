import json
import re
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

import build


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href', '')
            if href:
                self.links.append(href)


class BlogTests(unittest.TestCase):
    def test_explicit_folder_wins_over_old_filename(self):
        meta = {'topic': 'spring', 'category': 'Spring'}
        entry = build.collect_entry('[Upstage]-ddl-auto', meta, '본문')
        self.assertEqual((entry['topic'], entry['category']), ('spring', 'Spring'))
        with self.assertRaises(ValueError):
            build.collect_entry('example', {'topic': 'typo'}, '본문')

    def test_generic_rag_is_ai_and_upstage_stays_upstage(self):
        self.assertEqual(build.topic_for_entry('RAG/MLOps', '[RAG]-품질-평가'), 'ai')
        self.assertEqual(build.topic_for_entry('Upstage', '[Upstage]-Solar'), 'upstage')

    def test_frontmatter_decodes_quoted_titles_without_corrupting_korean(self):
        raw = '쿠버네티스 "ReplicaSet"과 `kubectl`\n'
        meta, _ = build.parse_frontmatter('---\ntitle: ' + json.dumps(raw, ensure_ascii=False) + '\n---\n본문')
        self.assertEqual(meta['title'], '쿠버네티스 "ReplicaSet"과 kubectl')

    def test_redirects_require_a_real_canonical_article(self):
        good = [({}, '내용', 'canonical'), ({'redirect_to': 'canonical'}, '보존본', 'old')]
        self.assertEqual(build.validate_redirects(good), {'old': 'canonical'})
        for bad in [
            [({'redirect_to': 'missing'}, '', 'old')],
            [({'redirect_to': 'self'}, '', 'self')],
            [({'redirect_to': 'b'}, '', 'a'), ({'redirect_to': 'a'}, '', 'b')],
            [({}, '', 'same'), ({}, '', 'same')],
        ]:
            with self.assertRaises(ValueError):
                build.validate_redirects(bad)

    def test_excerpt_does_not_leak_markdown_or_link_urls(self):
        body = '# 제목\n\n```text\n출력 예제\n```\n\n---\n\n[공식 문서](https://example.com)에 정리한 **설명**입니다.'
        self.assertEqual(build.excerpt(body), '공식 문서에 정리한 설명입니다.')

    def test_sources_are_read_in_place_without_deletion(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'sample.md'
            source.write_text('원본 내용', encoding='utf-8')
            sentinel = root / 'keep.html'
            sentinel.write_text('기존 파일', encoding='utf-8')
            with patch.object(build, 'POSTS_DIR', root):
                self.assertEqual(build.sync_markdown(), [source])
            self.assertEqual(source.read_text(encoding='utf-8'), '원본 내용')
            self.assertEqual(sentinel.read_text(encoding='utf-8'), '기존 파일')
            with patch.object(build, 'POSTS_DIR', root / 'missing'):
                with self.assertRaises(SystemExit):
                    build.sync_markdown()
            self.assertTrue(source.exists())

    def test_repaired_export_fences_are_balanced_and_rendered(self):
        for path in build.POSTS_DIR.glob('*.md'):
            with self.subTest(post=path.name):
                meta, body = build.parse_frontmatter(path.read_text(encoding='utf-8'))
                self.assertIn(build.entry_classification(path.stem, meta)[1], build.TOPIC_BY_ID)
                fence = None
                for line in body.splitlines():
                    match = re.fullmatch(r'(`{3,}|~{3,})(.*)', line)
                    if not match:
                        continue
                    marks, info = match.groups()
                    if fence is None:
                        self.assertNotIn('id=', info)
                        fence = marks
                    else:
                        self.assertEqual((marks, info.strip()), (fence, ''))
                        fence = None
                self.assertIsNone(fence)
                rendered = path.with_suffix('.html').read_text(encoding='utf-8')
                if meta.get('redirect_to'):
                    self.assertIn('<link rel="canonical"', rendered)
                    continue
                article = rendered.split('<article class="post-content">')[1].split('</article>')[0]
                self.assertNotIn('```', article)
                self.assertNotIn('\ufffd', article)
                self.assertNotRegex(article, r'<p>(?:title|categories|tags):')

    def test_information_extract_heading_is_outside_code(self):
        path = next(build.POSTS_DIR.glob('*Information-Extract*.html'))
        text = path.read_text(encoding='utf-8')
        self.assertIn('<h1>Information Extract API란?</h1>', text)
        code = re.findall(r'<pre><code[^>]*>(.*?)</code></pre>', text, re.S)
        self.assertTrue(code)
        self.assertNotIn('Information Extract API란?', code[0])
        self.assertNotIn('이 문서들에는 업무에 필요한 정보', code[0])

    def test_archive_and_internal_navigation_are_complete(self):
        entries = json.loads((build.ROOT / 'posts.json').read_text(encoding='utf-8'))
        expected = set()
        for path in build.POSTS_DIR.glob('*.md'):
            meta, _ = build.parse_frontmatter(path.read_text(encoding='utf-8'))
            if meta.get('redirect_to'):
                text = path.with_suffix('.html').read_text(encoding='utf-8')
                self.assertIn('http-equiv="refresh"', text)
                self.assertIn(meta['redirect_to'], {p['slug'] for p in entries})
                continue
            expected.add(meta.get('slug', path.stem))
        self.assertEqual({p['slug'] for p in entries}, expected)
        self.assertEqual(len(entries), len(expected))
        titles = []
        for entry in entries:
            self.assertNotRegex(entry['title'], r'\\[nrt"]|`|\ufffd')
            title = re.sub(r'^\[[^]]+\]\s*', '', entry['title']).strip().casefold()
            titles.append(title)
        self.assertEqual(len(titles), len(set(titles)), 'Duplicate visible titles')
        paths = [build.ROOT / 'index.html', *build.TOPICS_DIR.glob('*.html'), *build.POSTS_DIR.glob('*.html')]
        for path in paths:
            parser = Links()
            parser.feed(path.read_text(encoding='utf-8'))
            for href in parser.links:
                url = urlsplit(href)
                # Article examples can contain application routes (e.g. /boards/write).
                # Validate this archive's generated HTML navigation.
                if url.scheme or url.netloc or not url.path.endswith('.html'):
                    continue
                target = path.parent / unquote(url.path)
                with self.subTest(page=path.name, link=href):
                    self.assertTrue(target.exists(), f'Missing local link: {target}')
        by_slug = {p['slug']: p for p in entries}
        for entry in entries:
            text = (build.POSTS_DIR / (entry['slug'] + '.html')).read_text(encoding='utf-8')
            self.assertIn(f'../topics/{entry["topic"]}.html', text)
            nav = re.search(r'<nav class="post-nav".*?</nav>', text, re.S)
            parser = Links()
            parser.feed(nav.group(0))
            for href in parser.links:
                if href.startswith('../'):
                    continue
                self.assertEqual(by_slug[unquote(href.removesuffix('.html'))]['topic'], entry['topic'])


if __name__ == '__main__':
    unittest.main()
