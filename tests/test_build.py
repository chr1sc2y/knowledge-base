import unittest
from html.parser import HTMLParser
from pathlib import Path

from scripts import build


class BuildIndexTests(unittest.TestCase):
    def test_index_orders_modules_by_latest_article_and_opens_first(self):
        pages = [
            {
                "slug": "older-ai",
                "zh_title": "旧 AI 文章",
                "en_title": "Older AI Article",
                "zh_subtitle": "旧内容",
                "en_subtitle": "Older content",
                "zh_category": "Agent 工程",
                "en_category": "Agent Engineering",
                "zh_path": "articles/older.html",
                "en_path": "articles/older.html",
                "date": "2025-01-01",
            },
            {
                "slug": "newer-photo",
                "zh_title": "新摄影文章",
                "en_title": "Newer Photo Article",
                "zh_subtitle": "新内容",
                "en_subtitle": "Newer content",
                "zh_category": "旅行与摄影",
                "en_category": "Travel & Photography",
                "zh_path": "articles/newer.html",
                "en_path": "articles/newer.html",
                "date": "2026-01-01",
            },
        ]

        html = build.render_index(pages, "en")

        self.assertIn('<details class="module photo" id="photo" open>', html)
        self.assertIn('<details class="module ai" id="ai">', html)
        self.assertLess(html.index('id="photo"'), html.index('id="ai"'))
        self.assertLess(html.index('<a href="#photo">Photo</a>'), html.index('<a href="#ai">AI</a>'))

    def test_index_keeps_future_categories_in_more_module(self):
        pages = [
            {
                "slug": "future",
                "zh_title": "未来主题",
                "en_title": "Future Topic",
                "zh_subtitle": "未来内容",
                "en_subtitle": "Future content",
                "zh_category": "新模块",
                "en_category": "New Module",
                "zh_path": "articles/future.html",
                "en_path": "articles/future.html",
                "date": "2026-01-01",
            }
        ]

        html = build.render_index(pages, "zh")

        self.assertIn('<details class="module more" id="more" open>', html)
        self.assertIn("更多主题", html)
        self.assertIn("未来主题", html)
        self.assertIn('<nav class="module-jump" aria-label="快速导航">', html)
        self.assertIn('<a href="#more">更多</a>', html)

    def test_index_keeps_module_navigation_near_content(self):
        pages = [
            {
                "slug": "ai",
                "zh_title": "AI 文章",
                "en_title": "AI Article",
                "zh_subtitle": "内容",
                "en_subtitle": "Content",
                "zh_category": "Agent 工程",
                "en_category": "Agent Engineering",
                "zh_path": "articles/ai.html",
                "en_path": "articles/ai.html",
                "date": "2026-01-01",
            }
        ]

        html = build.render_index(pages, "en")

        self.assertNotIn('class="top"', html)
        self.assertNotIn('class="brand"', html)
        self.assertNotIn("Providence KB", html)
        self.assertIn('<nav class="module-jump" aria-label="Quick Navigation">', html)
        self.assertLess(html.index('class="module-jump"'), html.index('class="modules"'))


class ArticleTocParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_toc = False
        self.section_ids = set()
        self.toc_hrefs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set(attrs.get("class", "").split())
        if tag == "nav" and "toc" in classes:
            self.in_toc = True
        if tag == "section" and attrs.get("id"):
            self.section_ids.add(attrs["id"])
        if self.in_toc and tag == "a" and attrs.get("href", "").startswith("#"):
            self.toc_hrefs.append(attrs["href"][1:])

    def handle_endtag(self, tag):
        if tag == "nav" and self.in_toc:
            self.in_toc = False


class ArticleTocTests(unittest.TestCase):
    def test_every_article_has_toc_links_to_sections(self):
        article_paths = sorted(Path("articles").glob("*/*.html"))
        self.assertGreater(article_paths, [])

        for path in article_paths:
            with self.subTest(path=str(path)):
                parser = ArticleTocParser()
                parser.feed(path.read_text(encoding="utf-8"))

                self.assertGreater(parser.toc_hrefs, [], "missing TOC links")
                self.assertTrue(
                    set(parser.toc_hrefs).issubset(parser.section_ids),
                    "TOC contains links without matching sections",
                )
                self.assertNotIn(
                    ".toc ol{columns:",
                    path.read_text(encoding="utf-8"),
                    "TOC should remain single-column",
                )


if __name__ == "__main__":
    unittest.main()
