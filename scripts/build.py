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
              <div class="meta">{esc(page.get('category', 'General'))} · {esc(page.get('date', ''))}</div>
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
              <div class="meta">{esc(link.get('category', 'Reference'))}</div>
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
    categories = sorted({p.get("category", "General") for p in pages} | {l.get("category", "Reference") for l in links})
    category_chips = "".join(f"<button class='chip' data-filter='{esc(c.lower())}'>{esc(c)}</button>" for c in categories)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Providence Knowledge Base</title>
  <meta name="description" content="A private, curated knowledge base of in-depth learning pages and high-signal references. Designed for repeated study.">
  <style>
    :root {{
      --bg: #ffffff;
      --fg: #1d1d1f;
      --muted: #6e6e73;
      --border: #d2d2d7;
      --surface: #ffffff;
      --accent: #007aff;
      --chip: #f5f5f7;
      --shadow: 0 1px 2px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
      --radius: 12px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--fg);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }}
    a {{ color: var(--accent); text-underline-offset: 2px; text-decoration-thickness: 1px; }}
    a:hover {{ text-decoration-thickness: 1.5px; }}
    .wrap {{ width: min(1080px, calc(100vw - 48px)); margin: 0 auto; }}
    header {{
      padding: 72px 0 48px;
    }}
    .eyebrow {{
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 8px;
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: clamp(42px, 7vw, 64px);
      line-height: 1.05;
      font-weight: 700;
      letter-spacing: -0.02em;
      max-width: 22ch;
    }}
    .lead {{
      max-width: 620px;
      color: var(--muted);
      font-size: 18px;
      margin: 0 0 32px;
      line-height: 1.55;
    }}
    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      margin-bottom: 8px;
    }}
    input[type="search"] {{
      flex: 1 1 320px;
      min-width: 220px;
      border: 1px solid var(--border);
      background: var(--surface);
      border-radius: 10px;
      padding: 12px 16px;
      font: inherit;
      font-size: 15px;
      outline: none;
      transition: border-color .15s, box-shadow .15s;
    }}
    input[type="search"]:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.12);
    }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .chip {{
      border: 1px solid var(--border);
      background: var(--chip);
      border-radius: 999px;
      padding: 6px 14px;
      font-size: 13px;
      font-weight: 600;
      color: var(--fg);
      cursor: pointer;
      transition: all .1s ease;
    }}
    .chip:hover {{ background: #eeeef0; }}
    .chip.active {{
      background: var(--fg);
      color: #fff;
      border-color: var(--fg);
    }}
    main {{ padding-bottom: 40px; }}
    section {{
      padding: 48px 0 24px;
    }}
    h2 {{
      font-size: 21px;
      font-weight: 600;
      margin: 0 0 20px;
      letter-spacing: -0.01em;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;
    }}
    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 20px 20px 18px;
      transition: transform .12s ease, box-shadow .12s ease, border-color .12s;
    }}
    .card:hover {{
      transform: translateY(-1px);
      box-shadow: var(--shadow);
      border-color: #c7c7cc;
    }}
    .card.featured {{
      border-color: #c7d2ff;
    }}
    .meta {{
      color: var(--accent);
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 0.3px;
      margin-bottom: 8px;
      text-transform: uppercase;
    }}
    .card h3 {{
      font-size: 17px;
      font-weight: 600;
      margin: 0 0 6px;
      line-height: 1.3;
    }}
    .card h3 a {{
      color: inherit;
      text-decoration: none;
    }}
    .card h3 a:hover {{ color: var(--accent); }}
    .card p {{
      color: var(--muted);
      margin: 0 0 14px;
      font-size: 14.5px;
      line-height: 1.5;
    }}
    .tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}
    .tag {{
      font-size: 11px;
      color: #515154;
      background: #f5f5f7;
      border: 1px solid #e5e5e7;
      border-radius: 999px;
      padding: 2px 9px;
      font-weight: 500;
    }}
    .empty {{
      display: none;
      color: var(--muted);
      padding: 12px 0;
      font-size: 14px;
    }}
    footer {{
      padding: 40px 0 60px;
      color: var(--muted);
      font-size: 12px;
      border-top: 1px solid var(--border);
    }}
    @media (max-width: 720px) {{
      header {{ padding: 48px 0 32px; }}
      .grid {{ grid-template-columns: 1fr; }}
      .toolbar {{ flex-direction: column; align-items: stretch; }}
      input[type="search"] {{ width: 100%; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <div class="eyebrow">knowledge.prov1dence.top</div>
      <h1>Knowledge Base</h1>
      <p class="lead">A private collection of focused learning pages and references. Built for depth, clarity, and repeated returns.</p>
      <div class="toolbar">
        <input id="search" type="search" placeholder="Search pages, links, or tags (e.g. glucose, training)">
        <div class="chips">
          <button class="chip active" data-filter="">All</button>
          {category_chips}
        </div>
      </div>
    </div>
  </header>

  <main>
    <section>
      <div class="wrap">
        <h2>Articles</h2>
        <div class="grid searchable" id="pages">
          {page_cards}
        </div>
        <div class="empty" id="pagesEmpty">No matching articles.</div>
      </div>
    </section>

    <section>
      <div class="wrap">
        <h2>References</h2>
        <div class="grid searchable" id="links">
          {link_cards}
        </div>
        <div class="empty" id="linksEmpty">No matching references.</div>
      </div>
    </section>
  </main>

  <footer>
    <div class="wrap">Generated {esc(generated)} · Static site on GitHub Pages · All content in English</div>
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
        const empty = document.getElementById(group + 'Empty');
        if (empty) empty.style.display = visible ? 'none' : 'block';
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
