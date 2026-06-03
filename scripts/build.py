#!/usr/bin/env python3
"""Build the Providence Knowledge Base static site."""
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


def page_value(page: dict, key: str, lang: str) -> str:
    localized = f"{lang}_{key}"
    if localized in page:
        return str(page[localized])
    value = page.get(key, "")
    if isinstance(value, dict):
        return str(value.get(lang, value.get("en", "")))
    return str(value)


def render_rows(pages: list[dict], lang: str) -> str:
    rows = []
    for page in pages:
        path = page_value(page, "path", lang)
        title = page_value(page, "title", lang)
        subtitle = page_value(page, "subtitle", lang)
        category = page_value(page, "category", lang)
        search = " ".join(
            [
                title,
                subtitle,
                category,
                " ".join(page.get("tags", [])),
                page_value(page, "search", lang),
            ]
        ).lower()
        go = "进入" if lang == "zh" else "Enter"
        rows.append(
            f"""
      <a class="row" href="{esc(path)}" data-search="{esc(search)}">
        <div class="meta">{esc(category)}</div>
        <div>
          <h2>{esc(title)}</h2>
          <p>{esc(subtitle)}</p>
        </div>
        <div class="go">{go}</div>
      </a>"""
        )
    return "\n".join(rows)


def render_index(pages: list[dict], lang: str) -> str:
    generated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    is_zh = lang == "zh"
    rows = render_rows(pages, lang)
    latest = max((page.get("date", "") for page in pages), default="")
    count_text = f"{len(pages)} 个主题 · 最近更新 {latest}" if is_zh else f"{len(pages)} topic · Last updated {latest}"
    title = "Providence Knowledge Base"
    description = (
        "双语知识库，提供结构化、清晰的解释。"
        if is_zh
        else "A bilingual knowledge base of structured explanations."
    )
    h1 = "知识库" if is_zh else "Knowledge Base"
    lead = (
        "页面从基本概念出发，逐步介绍机制与实践策略。搜索或浏览主题。"
        if is_zh
        else "Pages present concepts from basic ideas through mechanisms to practical strategies. Search or browse topics."
    )
    placeholder = "搜索主题、标签或概念" if is_zh else "Search topics, tags, or concepts"
    aria = "搜索页面" if is_zh else "Search pages"
    lang_href = "en/" if is_zh else "../"
    lang_label = "English" if is_zh else "中文"
    html_lang = "zh-CN" if is_zh else "en"

    return f"""<!doctype html>
<html lang="{html_lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <style>
    :root {{ --bg:#f7f3ea; --fg:#202523; --muted:#68716d; --line:#d8cfbf; --ink:#163d3a; --accent:#b24b2f; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--fg); font-family:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; line-height:1.68; -webkit-font-smoothing:antialiased; }}
    a {{ color:inherit; }}
    .wrap {{ width:min(1040px, calc(100vw - 40px)); margin:0 auto; }}
    .lang {{ position:fixed; top:18px; right:22px; z-index:5; text-decoration:none; color:var(--ink); border:1px solid var(--line); background:rgba(247,243,234,.88); backdrop-filter:blur(16px); border-radius:999px; padding:7px 12px; font-size:13px; font-weight:800; }}
    .lang:focus-visible, .row:focus-visible {{ outline:2px solid var(--accent); outline-offset:6px; }}
    header {{ padding:88px 0 54px; }}
    .kicker {{ color:var(--accent); font-size:13px; font-weight:900; letter-spacing:.04em; text-transform:uppercase; }}
    h1 {{ font-family:Georgia,"Times New Roman",serif; font-size:clamp(44px, 8vw, 86px); line-height:.98; letter-spacing:-.035em; margin:14px 0 20px; max-width:11ch; }}
    .lead {{ font-size:21px; color:var(--muted); max-width:700px; margin:0; }}
    .tools {{ margin-top:36px; border-top:1px solid var(--line); border-bottom:1px solid var(--line); padding:18px 0; display:flex; gap:14px; align-items:center; flex-wrap:wrap; }}
    .tools input {{ flex:1 1 360px; border:0; border-bottom:1px solid var(--line); background:transparent; padding:10px 0; font:inherit; font-size:18px; outline:none; color:var(--fg); }}
    .tools input:focus {{ border-color:var(--accent); }}
    .tools span {{ font-size:14px; color:var(--muted); }}
    main {{ padding-bottom:80px; }}
    .list {{ border-top:1px solid var(--line); }}
    .row {{ display:grid; grid-template-columns:140px 1fr auto; gap:24px; align-items:baseline; padding:28px 0; border-bottom:1px solid var(--line); text-decoration:none; }}
    .row .meta {{ color:var(--accent); font-size:13px; font-weight:900; }}
    .row h2 {{ font-family:Georgia,"Times New Roman",serif; font-size:34px; line-height:1.08; margin:0 0 8px; letter-spacing:-.025em; }}
    .row p {{ color:var(--muted); margin:0; max-width:720px; }}
    .row .go {{ color:var(--ink); font-weight:900; }}
    .empty {{ display:none; color:var(--muted); padding:24px 0; }}
    footer {{ border-top:1px solid var(--line); color:var(--muted); font-size:12px; padding:30px 0 50px; }}
    @media(max-width:760px) {{ header {{ padding-top:70px; }} .row {{ grid-template-columns:1fr; gap:8px; }} .row h2 {{ font-size:29px; }} .tools input {{ flex-basis:100%; }} }}
  </style>
</head>
<body>
  <a class="lang" href="{lang_href}">{lang_label}</a>
  <header class="wrap">
    <div class="kicker">Providence Knowledge Base</div>
    <h1>{esc(h1)}</h1>
    <p class="lead">{esc(lead)}</p>
    <div class="tools"><input id="q" type="search" placeholder="{esc(placeholder)}" aria-label="{esc(aria)}"><span>{esc(count_text)}</span></div>
  </header>
  <main class="wrap">
    <div class="list" id="list">
{rows}
    </div>
    <div class="empty" id="empty">{'没有匹配的主题。' if is_zh else 'No matching topics.'}</div>
  </main>
  <footer><div class="wrap">{'生成时间' if is_zh else 'Generated'} {esc(generated)} · knowledge.prov1dence.top</div></footer>
  <script>
    const q = document.getElementById('q');
    const empty = document.getElementById('empty');
    q.addEventListener('input', () => {{
      const s = q.value.trim().toLowerCase();
      let visible = 0;
      document.querySelectorAll('.row').forEach((row) => {{
        const show = !s || row.dataset.search.toLowerCase().includes(s);
        row.style.display = show ? 'grid' : 'none';
        if (show) visible += 1;
      }});
      empty.style.display = visible ? 'none' : 'block';
    }});
  </script>
</body>
</html>
"""


def copy_tree(src_name: str, dest_name: str | None = None) -> None:
    src = ROOT / src_name
    if not src.exists():
        return
    dest = DIST / (dest_name or src_name)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def build() -> None:
    pages = load_json(ROOT / "data" / "pages.json")
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    copy_tree("articles/cn", "articles")
    copy_tree("articles/en", "en/articles")
    (DIST / "en").mkdir(exist_ok=True)
    for name in ("CNAME", ".nojekyll"):
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, DIST / name)
    (DIST / "index.html").write_text(render_index(pages, "zh"), encoding="utf-8")
    (DIST / "en" / "index.html").write_text(render_index(pages, "en"), encoding="utf-8")


if __name__ == "__main__":
    build()
