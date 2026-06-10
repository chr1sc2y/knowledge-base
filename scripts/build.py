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

CATEGORY_MODULES = [
    {
        "key": "ai",
        "zh_label": "AI",
        "en_label": "AI",
        "zh_title": "Agent 工程与 AI 系统",
        "en_title": "Agent Engineering and AI Systems",
        "zh_description": "模型之外的工程外壳：harness、工具权限、评测、部署、状态恢复和开源框架。",
        "en_description": "The engineering around models: harnesses, tool permissions, evals, deployment, recovery, and open-source frameworks.",
        "zh_role": "技术系统类内容入口，后续可继续容纳 OpenAI API、MCP、agent 评测、部署架构和工具链。",
        "en_role": "A home for technical systems content, including OpenAI APIs, MCP, agent evals, deployment architecture, and tooling.",
        "zh_categories": {"Agent 工程"},
        "en_categories": {"Agent Engineering"},
    },
    {
        "key": "health",
        "zh_label": "健康",
        "en_label": "Health",
        "zh_title": "身体指标、营养与日常实践",
        "en_title": "Health Signals, Nutrition, and Daily Practice",
        "zh_description": "把健康问题拆成可理解、可执行、可长期维护的知识框架。",
        "en_description": "Health topics broken into understandable, practical, and maintainable frameworks.",
        "zh_role": "承载血糖、营养、训练、睡眠、体检指标和生活方式实验；重点是清晰解释和实践框架。",
        "en_role": "For glucose, nutrition, training, sleep, biomarkers, and lifestyle experiments, with clear explanations and practical framing.",
        "zh_categories": {"健康与营养"},
        "en_categories": {"Health & Nutrition"},
    },
    {
        "key": "photo",
        "zh_label": "摄影",
        "en_label": "Photo",
        "zh_title": "路线、审美、器材与后期",
        "en_title": "Routes, Taste, Gear, and Editing",
        "zh_description": "旅行摄影、镜头选择、视觉主题、调色风格和成片工作流。",
        "en_description": "Travel photography, focal-length choices, visual themes, color style, and final-edit workflows.",
        "zh_role": "路线指南、镜头策略、调色风格、AI 出样、Lightroom 工作流和成片复盘都放在这里。",
        "en_role": "A place for route guides, lens strategy, color style, AI samples, Lightroom workflows, and final-image reviews.",
        "zh_categories": {"旅行与摄影"},
        "en_categories": {"Travel & Photography"},
    },
    {
        "key": "cognition",
        "zh_label": "认知",
        "en_label": "Cognition",
        "zh_title": "决策系统与长期框架",
        "en_title": "Decision Systems and Long-Term Frameworks",
        "zh_description": "资产配置、判断、复盘、行动纪律和个人系统设计。",
        "en_description": "Asset allocation, judgment, reviews, execution discipline, and personal system design.",
        "zh_role": "沉淀可复用的决策方法、长期主义框架和个人系统设计。",
        "en_role": "Reusable decision methods, long-term frameworks, and personal operating systems.",
        "zh_categories": {"个人系统与决策"},
        "en_categories": {"Personal Systems & Decision Making"},
    },
]


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


def newest_first(pages: list[dict]) -> list[dict]:
    return sorted(pages, key=lambda page: page.get("date", ""), reverse=True)


def module_for_page(page: dict) -> dict | None:
    zh_category = page_value(page, "category", "zh")
    en_category = page_value(page, "category", "en")
    for module in CATEGORY_MODULES:
        if zh_category in module["zh_categories"] or en_category in module["en_categories"]:
            return module
    return None


def group_pages(pages: list[dict]) -> list[dict]:
    grouped = {module["key"]: {**module, "pages": []} for module in CATEGORY_MODULES}
    extras: list[dict] = []
    for page in newest_first(pages):
        module = module_for_page(page)
        if module is None:
            extras.append(page)
        else:
            grouped[module["key"]]["pages"].append(page)
    modules = [grouped[module["key"]] for module in CATEGORY_MODULES if grouped[module["key"]]["pages"]]
    if extras:
        modules.append(
            {
                "key": "more",
                "zh_label": "更多",
                "en_label": "More",
                "zh_title": "更多主题",
                "en_title": "More Topics",
                "zh_description": "新主题会先出现在这里，再按内容增长整理为独立模块。",
                "en_description": "New topics appear here first, then move into dedicated modules as they grow.",
                "zh_role": "预留给未来新增的大类，避免当前首页结构被四个模块锁死。",
                "en_role": "Reserved for future categories so the homepage is not locked to the current module set.",
                "pages": extras,
            }
        )
    return modules


def latest_module_key(modules: list[dict]) -> str:
    dated_modules = [
        (max((page.get("date", "") for page in module["pages"]), default=""), module["key"])
        for module in modules
    ]
    return max(dated_modules, default=("", ""))[1]


def render_tags(page: dict, limit: int = 4) -> str:
    tags = page.get("tags", [])[:limit]
    return "".join(f"<span>{esc(tag)}</span>" for tag in tags)


def render_article_card(page: dict, lang: str) -> str:
    category = page_value(page, "category", lang)
    title = page_value(page, "title", lang)
    subtitle = page_value(page, "subtitle", lang)
    path = page_value(page, "path", lang)
    enter = "进入文章" if lang == "zh" else "Read article"
    return f"""
          <a class="article" href="{esc(path)}">
            <div class="article-top"><span>{esc(category)}</span><span>{esc(page.get("date", ""))}</span></div>
            <h3>{esc(title)}</h3>
            <p>{esc(subtitle)}</p>
            <div class="tags">{render_tags(page)}</div>
            <span class="go">{enter}</span>
          </a>"""


def render_modules(modules: list[dict], lang: str) -> str:
    latest_key = latest_module_key(modules)
    role_label = "Module" if lang == "en" else "模块"
    rendered = []
    for module in modules:
        label = page_value(module, "label", lang)
        title = page_value(module, "title", lang)
        description = page_value(module, "description", lang)
        role = page_value(module, "role", lang)
        open_attr = " open" if module["key"] == latest_key else ""
        cards = "\n".join(render_article_card(page, lang) for page in module["pages"])
        rendered.append(
            f"""
      <details class="module {esc(module["key"])}" id="{esc(module["key"])}"{open_attr}>
        <summary>
          <div class="code">{esc(label)}</div>
          <div class="summary-copy"><h2>{esc(title)}</h2><p>{esc(description)}</p></div>
          <div class="indicator" aria-hidden="true"></div>
        </summary>
        <div class="panel">
          <div class="panel-note"><b>{esc(role_label)}</b>{esc(role)}</div>
          <div class="article-list">
{cards}
          </div>
        </div>
      </details>"""
        )
    return "\n".join(rendered)


def render_nav(modules: list[dict], lang: str) -> str:
    return "".join(
        f'<a href="#{esc(module["key"])}">{esc(page_value(module, "label", lang))}</a>'
        for module in modules
    )


def render_index(pages: list[dict], lang: str) -> str:
    generated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    modules = group_pages(pages)
    is_zh = lang == "zh"
    latest = max((page.get("date", "") for page in pages), default="")
    title = "Providence Knowledge Base"
    description = (
        "按主题模块组织的双语知识库。"
        if is_zh
        else "A bilingual knowledge base organized by expandable topic modules."
    )
    h1 = "知识有结构，阅读有入口" if is_zh else "Structured Knowledge, Clear Entry Points"
    lead = (
        "AI、健康、摄影、认知。按主题展开，找到当前最值得读的一篇。"
        if is_zh
        else "AI, health, photography, and cognition. Expand a topic and start with the most useful article."
    )
    lang_href = "en/" if is_zh else "../"
    lang_label = "English" if is_zh else "中文"
    html_lang = "zh-CN" if is_zh else "en"
    module_count_label = "模块" if is_zh else "Modules"
    article_count_label = "文章" if is_zh else "Articles"
    latest_label = "最近更新" if is_zh else "Latest"
    expand_label = "点击展开" if is_zh else "Click to expand"

    return f"""<!doctype html>
<html lang="{html_lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <style>
    :root{{--bg:#f6f1e8;--paper:#fffaf1;--fg:#1d2420;--muted:#69716c;--line:#d9ceb9;--green:#173f3a;--rust:#a9462d;--gold:#b98f45;--blue:#2f5b72}}
    *{{box-sizing:border-box}}
    html{{scroll-behavior:smooth}}
    body{{margin:0;background:var(--bg);color:var(--fg);font-family:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.64;-webkit-font-smoothing:antialiased}}
    a{{color:inherit;text-decoration:none}}
    .wrap{{width:min(1160px,calc(100vw - 40px));margin:0 auto}}
    .top{{position:sticky;top:0;z-index:3;border-bottom:1px solid var(--line);background:rgba(246,241,232,.9);backdrop-filter:blur(16px)}}
    .nav{{min-height:58px;display:flex;align-items:center;justify-content:space-between;gap:18px}}
    .brand{{font-family:Georgia,"Times New Roman",serif;font-size:20px;font-weight:700}}
    .nav nav{{display:flex;gap:16px;color:var(--muted);font-size:14px;flex-wrap:wrap;justify-content:flex-end}}
    .lang{{border:1px solid var(--line);border-radius:999px;padding:6px 11px;color:var(--green);font-weight:800;font-size:13px;white-space:nowrap}}
    header{{padding:70px 0 34px}}
    .hero{{display:grid;grid-template-columns:1.05fr .95fr;gap:40px;align-items:end}}
    .kicker{{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--rust);font-weight:900}}
    h1{{font-family:Georgia,"Times New Roman",serif;font-size:clamp(46px,8vw,98px);line-height:.92;letter-spacing:-.04em;margin:14px 0 18px}}
    .lead{{font-size:21px;color:var(--muted);max-width:660px;margin:0}}
    .overview{{border:1px solid var(--line);background:var(--paper);padding:22px;display:grid;grid-template-columns:1fr 1fr;gap:12px}}
    .metric{{border-top:1px solid var(--line);padding-top:14px}}
    .metric b{{display:block;font-family:Georgia,"Times New Roman",serif;font-size:38px;line-height:1;color:var(--green)}}
    .metric span{{color:var(--muted);font-size:13px}}
    main{{padding:12px 0 80px}}
    .modules{{display:grid;gap:12px;margin-top:22px}}
    details.module{{border:1px solid var(--line);background:var(--paper)}}
    details.module[open]{{background:#fffdf8}}
    summary{{list-style:none;cursor:pointer;display:grid;grid-template-columns:160px 1fr auto;gap:22px;align-items:center;padding:24px}}
    summary::-webkit-details-marker{{display:none}}
    .code{{font-family:Georgia,"Times New Roman",serif;font-size:52px;line-height:1;color:var(--green);letter-spacing:-.04em}}
    .summary-copy h2{{font-family:Georgia,"Times New Roman",serif;font-size:32px;line-height:1.08;margin:0 0 8px;letter-spacing:-.02em}}
    .summary-copy p{{color:var(--muted);margin:0;max-width:720px}}
    .indicator{{width:34px;height:34px;border:1px solid var(--line);border-radius:999px;display:grid;place-items:center;color:var(--green);font-weight:900}}
    details[open] .indicator{{background:var(--green);color:white;border-color:var(--green)}}
    details[open] .indicator::before{{content:"-"}}
    .indicator::before{{content:"+"}}
    .panel{{border-top:1px solid var(--line);display:grid;grid-template-columns:.8fr 1.2fr;gap:24px;padding:24px}}
    .panel-note{{color:var(--muted)}}
    .panel-note b{{display:block;color:var(--rust);font-size:13px;letter-spacing:.06em;text-transform:uppercase;margin-bottom:10px}}
    .article-list{{display:grid;gap:12px}}
    .article{{border:1px solid var(--line);background:#fff;padding:18px;display:grid;gap:12px}}
    .article:hover{{border-color:var(--green)}}
    .article-top{{display:flex;justify-content:space-between;gap:14px;color:var(--muted);font-size:12px}}
    .article h3{{font-family:Georgia,"Times New Roman",serif;font-size:30px;line-height:1.05;margin:0;letter-spacing:-.02em}}
    .article p{{margin:0;color:var(--muted)}}
    .tags{{display:flex;gap:6px;flex-wrap:wrap}}
    .tags span{{border:1px solid var(--line);border-radius:999px;padding:4px 8px;color:var(--muted);font-size:12px}}
    .go{{display:inline-flex;width:max-content;align-items:center;gap:8px;color:var(--green);font-weight:900;border-bottom:1px solid var(--green)}}
    .module.ai .code,.module.ai .go{{color:var(--blue)}}
    .module.health .code,.module.health .go{{color:#2f6b4f}}
    .module.photo .code,.module.photo .go{{color:var(--rust)}}
    .module.cognition .code,.module.cognition .go{{color:var(--gold)}}
    footer{{border-top:1px solid var(--line);color:var(--muted);font-size:13px;padding:28px 0 46px}}
    @media(max-width:900px){{.hero,.panel{{grid-template-columns:1fr}}.overview{{grid-template-columns:1fr 1fr}}summary{{grid-template-columns:1fr auto}}.code{{font-size:46px}}.summary-copy{{grid-column:1 / -1;grid-row:2}}}}
    @media(max-width:560px){{header{{padding-top:46px}}.nav nav{{display:none}}.overview{{grid-template-columns:1fr}}summary{{padding:19px}}.panel{{padding:19px}}.article h3{{font-size:26px}}}}
  </style>
</head>
<body>
  <div class="top">
    <div class="nav wrap">
      <a class="brand" href="./">Providence KB</a>
      <nav>{render_nav(modules, lang)}</nav>
      <a class="lang" href="{esc(lang_href)}">{esc(lang_label)}</a>
    </div>
  </div>
  <header class="wrap">
    <div class="hero">
      <div>
        <div class="kicker">Providence Knowledge Base</div>
        <h1>{esc(h1)}</h1>
        <p class="lead">{esc(lead)}</p>
      </div>
      <div class="overview">
        <div class="metric"><b>{len(modules)}</b><span>{esc(module_count_label)}</span></div>
        <div class="metric"><b>{len(pages)}</b><span>{esc(article_count_label)}</span></div>
        <div class="metric"><b>{esc(latest)}</b><span>{esc(latest_label)}</span></div>
        <div class="metric"><b>+</b><span>{esc(expand_label)}</span></div>
      </div>
    </div>
  </header>
  <main class="wrap">
    <section class="modules">
{render_modules(modules, lang)}
    </section>
  </main>
  <footer><div class="wrap">{'生成时间' if is_zh else 'Generated'} {esc(generated)} · knowledge.prov1dence.top</div></footer>
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
