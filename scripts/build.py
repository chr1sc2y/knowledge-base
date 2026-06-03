#!/usr/bin/env python3
"""Build the Knowledge Base static site."""
from __future__ import annotations

import html
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def tag_list(tags: list[str]) -> str:
    return "".join(f"<span class='tag'>{esc(tag)}</span>" for tag in tags)


def render_page_cards(pages: list[dict]) -> str:
    cards = []
    for page in pages:
        tags = tag_list(page.get("tags", []))
        featured = " featured" if page.get("featured") else ""
        cards.append(
            f"""
            <article class="card page-card{featured}" data-search="{esc(' '.join([page.get('title',''), page.get('subtitle',''), page.get('category',''), ' '.join(page.get('tags', []))]).lower())}">
              <div class="meta">{esc(page.get('category', '未分类'))} · {esc(page.get('date', ''))}</div>
              <h3><a href="{esc(page.get('path', '#'))}">{esc(page.get('title', 'Untitled'))}</a></h3>
              <p>{esc(page.get('subtitle', ''))}</p>
              <div class="tags">{tags}</div>
            </article>
            """
        )
    return "\n".join(cards)


def render_links(links: list[dict]) -> str:
    items = []
    for link in links:
        tags = tag_list(link.get("tags", []))
        items.append(
            f"""
            <article class="card link-card" data-search="{esc(' '.join([link.get('title',''), link.get('note',''), link.get('category',''), ' '.join(link.get('tags', []))]).lower())}">
              <div class="meta">{esc(link.get('category', '链接'))}</div>
              <h3><a href="{esc(link.get('url', '#'))}" target="_blank" rel="noopener noreferrer">{esc(link.get('title', 'Untitled'))}</a></h3>
              <p>{esc(link.get('note', ''))}</p>
              <div class="tags">{tags}</div>
            </article>
            """
        )
    return "\n".join(items)


def render_index(pages: list[dict], links: list[dict]) -> str:
    generated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    page_cards = render_page_cards(pages)
    link_cards = render_links(links)
    categories = sorted({p.get("category", "未分类") for p in pages} | {l.get("category", "链接") for l in links})
    category_chips = "".join(f"<button class='chip' data-filter='{esc(c.lower())}'>{esc(c)}</button>" for c in categories)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Providence Knowledge Base</title>
  <meta name="description" content="私人知识入口：收藏 Codex 生成的系统学习页、有用链接和复习材料。">
  <style>
    :root {{
      --paper: #f8f4ea;
      --ink: #1f2728;
      --muted: #5d686a;
      --line: #d9d0bd;
      --panel: #fffaf0;
      --panel2: #edf6f2;
      --teal: #23736c;
      --blue: #315f9c;
      --amber: #a96714;
      --shadow: 0 14px 34px rgba(38, 32, 21, .09);
      --radius: 8px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.68;
    }}
    a {{ color: var(--blue); text-underline-offset: 3px; }}
    .wrap {{ width: min(1120px, calc(100vw - 32px)); margin: 0 auto; }}
    header {{
      padding: 48px 0 28px;
      border-bottom: 1px solid var(--line);
    }}
    .eyebrow {{
      color: var(--teal);
      font-size: 13px;
      font-weight: 900;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 10px 0 12px;
      font-size: clamp(36px, 6vw, 70px);
      line-height: 1.02;
      letter-spacing: 0;
      max-width: 980px;
    }}
    .lead {{
      max-width: 840px;
      color: #344244;
      font-size: 19px;
      margin: 0;
    }}
    .toolbar {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 12px;
      margin-top: 24px;
      align-items: center;
    }}
    input[type="search"] {{
      width: 100%;
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: var(--radius);
      padding: 13px 14px;
      font: inherit;
      box-shadow: var(--shadow);
    }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .chip {{
      border: 1px solid var(--line);
      background: #fff8e8;
      border-radius: 999px;
      padding: 8px 12px;
      font-weight: 800;
      cursor: pointer;
    }}
    .chip.active {{ background: var(--ink); color: white; border-color: var(--ink); }}
    section {{
      padding: 34px 0;
      border-bottom: 1px solid rgba(217, 208, 189, .8);
    }}
    h2 {{ font-size: clamp(26px, 3vw, 38px); margin: 0 0 14px; line-height: 1.15; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 18px;
      box-shadow: var(--shadow);
    }}
    .card.featured {{ border-left: 6px solid var(--teal); }}
    .meta {{ color: var(--teal); font-size: 13px; font-weight: 900; margin-bottom: 6px; }}
    .card h3 {{ font-size: 21px; margin: 0 0 8px; }}
    .card p {{ color: var(--muted); margin: 0 0 12px; }}
    .tags {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .tag {{
      border: 1px solid var(--line);
      background: rgba(255,255,255,.55);
      border-radius: 999px;
      padding: 3px 8px;
      font-size: 12px;
      color: #3d484a;
    }}
    .note {{
      background: var(--panel2);
      border: 1px solid #c7ddd4;
      border-radius: var(--radius);
      padding: 16px;
      margin-top: 18px;
    }}
    .empty {{ display: none; color: var(--muted); padding: 16px 0; }}
    footer {{ padding: 28px 0 48px; color: var(--muted); font-size: 14px; }}
    @media (max-width: 900px) {{
      .toolbar {{ grid-template-columns: 1fr; }}
      .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <div class="eyebrow">knowledge.prov1dence.top</div>
      <h1>Providence Knowledge Base</h1>
      <p class="lead">一个专门存放高价值学习页面和链接的私人知识入口。这里不是信息流，而是可以反复打开、复习、校准理解的系统化知识库。</p>
      <div class="toolbar">
        <input id="search" type="search" placeholder="搜索页面、链接、标签，例如：血糖、GitHub、营养">
        <div class="chips">
          <button class="chip active" data-filter="">全部</button>
          {category_chips}
        </div>
      </div>
    </div>
  </header>

  <main>
    <section>
      <div class="wrap">
        <h2>学习页面</h2>
        <div class="grid searchable" id="pages">
          {page_cards}
        </div>
        <div class="empty" id="pagesEmpty">没有匹配的学习页面。</div>
      </div>
    </section>

    <section>
      <div class="wrap">
        <h2>有用链接</h2>
        <div class="grid searchable" id="links">
          {link_cards}
        </div>
        <div class="empty" id="linksEmpty">没有匹配的链接。</div>
        <div class="note">添加新知识时：把 HTML 放进 <code>pages/</code>，在 <code>data/pages.json</code> 登记；把外部链接放进 <code>data/links.json</code>。push 后 GitHub Actions 会自动发布。</div>
      </div>
    </section>
  </main>

  <footer>
    <div class="wrap">Generated at {esc(generated)} · Static site on GitHub Pages</div>
  </footer>

  <script>
    const search = document.getElementById('search');
    const chips = document.querySelectorAll('.chip');
    let filter = '';

    function applyFilter() {{
      const query = search.value.trim().toLowerCase();
      for (const group of ['pages', 'links']) {{
        let visible = 0;
        document.querySelectorAll('#' + group + ' .card').forEach(card => {{
          const text = card.dataset.search || '';
          const okQuery = !query || text.includes(query);
          const okFilter = !filter || text.includes(filter);
          const show = okQuery && okFilter;
          card.style.display = show ? '' : 'none';
          if (show) visible += 1;
        }});
        document.getElementById(group + 'Empty').style.display = visible ? 'none' : 'block';
      }}
    }}

    search.addEventListener('input', applyFilter);
    chips.forEach(chip => {{
      chip.addEventListener('click', () => {{
        chips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        filter = chip.dataset.filter || '';
        applyFilter();
      }});
    }});
  </script>
</body>
</html>
"""


def build() -> None:
    pages = load_json(ROOT / "data" / "pages.json")
    links = load_json(ROOT / "data" / "links.json")
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    shutil.copytree(ROOT / "pages", DIST / "pages")
    for name in ("CNAME", ".nojekyll"):
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, DIST / name)
    (DIST / "index.html").write_text(render_index(pages, links), encoding="utf-8")


if __name__ == "__main__":
    build()
