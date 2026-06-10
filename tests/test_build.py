import unittest

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


if __name__ == "__main__":
    unittest.main()
