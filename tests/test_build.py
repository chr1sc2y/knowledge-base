import unittest
from html.parser import HTMLParser
from pathlib import Path

from scripts import build


class BuildIndexTests(unittest.TestCase):
    def test_index_lists_newest_pages_first(self):
        pages = [
            {
                "slug": "older",
                "zh_title": "旧文章",
                "en_title": "Older Article",
                "zh_subtitle": "旧内容",
                "en_subtitle": "Older content",
                "zh_category": "测试",
                "en_category": "Test",
                "zh_path": "articles/older.html",
                "en_path": "articles/older.html",
                "date": "2025-01-01",
            },
            {
                "slug": "newer",
                "zh_title": "新文章",
                "en_title": "Newer Article",
                "zh_subtitle": "新内容",
                "en_subtitle": "Newer content",
                "zh_category": "测试",
                "en_category": "Test",
                "zh_path": "articles/newer.html",
                "en_path": "articles/newer.html",
                "date": "2026-01-01",
            },
        ]

        html = build.render_index(pages, "en")

        self.assertLess(html.index("Newer Article"), html.index("Older Article"))


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


if __name__ == "__main__":
    unittest.main()
