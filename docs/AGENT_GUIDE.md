# Agent Guide

This document is the single operating guide for agents maintaining this
Knowledge Base. Keep it concise and update it whenever the site architecture,
language rules, or project status changes.

**Important**: All article content must also follow the stricter rules in [ARTICLE_WRITING_STANDARDS.md](./ARTICLE_WRITING_STANDARDS.md). That document takes precedence on matters of factual objectivity, tone, and what may or may not appear in public pages.

## Product Goal

Build a public static Knowledge Base at `knowledge.prov1dence.top` for clear,
structured explanatory pages. The site should feel calm, direct, and reference-oriented. It should
not feel like a dashboard, blog feed, marketing page, or card-heavy template.

## Design Rules

- Use bilingual content for every public page: Simplified Chinese and English.
- Provide a language switch in the same location on every page, preferably the
  top-right corner of the viewport/header.
- Home page should be a quiet index, not a card grid.
- Home page hero title should stay concise: Chinese uses `知识库`, English uses
  `Knowledge Base`. Update Chinese and English home pages together.
- Avoid a sticky top category menu on the home page. Put module jump links
  near the expandable modules and generate them from the module data so future
  categories are included automatically.
- Order home page modules by the newest article inside each module. The newest
  module appears first and is the only module opened by default.
- Home page should not show References. References belong at the bottom of an
  article or on a dedicated links page.
- Article pages should primarily use typography, spacing, headings, diagrams,
  lists, and tables. Avoid making every concept a card.
- Every article page must include a table of contents immediately after the
  header and before the main article body. The TOC should link to each top-level
  `section id` / `h2` section in the article. Keep the TOC as a single-column
  list on all viewport sizes.
- Cards are reserved for truly framed tools, quizzes, warnings, or interactive
  elements. Do not use cards as the default content container.
- Simplicity means reducing friction and visual competition, not merely using
  white backgrounds and rounded rectangles.
- Use a publication-oriented type system on the home page: `Noto Serif SC` for
  Chinese display text, `Newsreader` for English display text, and system sans
  for body/UI text. Keep module surfaces light, with soft borders and subtle
  open-state emphasis rather than heavy card grids.
- Prefer progressive explanatory structure: basic concepts, terminology, mechanism,
  regulation, application, sources. Do not label depth of explanation as literal school
  stages such as elementary/middle/high/undergraduate/master unless the user
  explicitly asks for that metaphor on screen.

The selected visual direction is the warmer editorial template:

- paper background `#f7f3ea`
- serif display headings
- muted body text
- ink/accent palette (`#163d3a`, `#b24b2f`)
- article sections separated by rules, not floating cards

## Bilingual Architecture

Public URL shape (unchanged):

```text
/
/en/
/articles/<slug>.html
/en/articles/<slug>.html
```

Source layout (consolidated):

```
articles/cn/<slug>.html   # Chinese
articles/en/<slug>.html   # English
```

Each language page is a real HTML page. The language button links to the
matching page in the other language. Avoid relying only on JavaScript text
replacement for production content because it makes editing and indexing harder.

## Technical Stack

- Static HTML/CSS/JavaScript.
- Python stdlib build script.
- GitHub Pages deployment through GitHub Actions.
- No frontend framework unless the project grows beyond static pages.
- No external fonts by default; use system fonts for speed and stability.

## Current Status

Implemented:

- GitHub Pages workflow using `actions/upload-pages-artifact` and
  `actions/deploy-pages`.
- Custom domain file: `CNAME` set to `knowledge.prov1dence.top`.
- Bilingual home pages: `/` and `/en/`.
- Bilingual blood glucose article: `/articles/blood-glucose.html` and
  `/en/articles/blood-glucose.html`.
- Editorial template selected for production.
- Data files for pages and useful links.
- Two local design demos:
  - `demos/apple/` for an Apple-like minimal direction.
  - `demos/editorial/` for a warmer editorial direction.

Pending:

- Confirm DNS points `knowledge.prov1dence.top` to GitHub Pages.
- Enable HTTPS enforcement after GitHub issues the certificate.
- Extract shared home page CSS and template fragments from `scripts/build.py`
  once the home page design stabilizes. The current inline template is still
  acceptable, but future category pages and additional demos should not copy
  large CSS blocks by hand.

## Maintenance Workflow

1. Add or edit Chinese content in `articles/cn/` and the matching English version in `articles/en/`.
2. Ensure the content fully complies with [ARTICLE_WRITING_STANDARDS.md](./ARTICLE_WRITING_STANDARDS.md) (objective facts only, no subjective language, no privacy leaks).
3. Keep language-pair links (in nav and index data) in sync.
4. Run the build script or local demo server.
5. Verify:
   - HTML parses.
   - JavaScript parses.
   - Language switch links resolve.
   - Homepage has no visible References section.
   - Article pages are not dominated by cards.
   - Content passes the standards checklist in ARTICLE_WRITING_STANDARDS.md.
6. Commit only after verification.

## Privacy & Public Content Guidelines

When creating or editing public articles based on personal travel, experiences, or private documents (e.g. Notion notes or diaries):

- **Strip all itinerary details**: Remove any day-by-day sequencing, specific trip structure, "Day 1", "after visiting X then Y", loop descriptions, or references to how the places were visited in order.
- **Remove all time-sensitive and personal information**: No specific dates, years, flight times, costs, budgets, return details, or any personally identifying logistics.
- **Focus only on the destinations themselves** (for travel) or **only on generalizable knowledge** (for other personal sources): Articles must read as standalone explanatory resources. Do not frame content around any individual's journey, decisions, or realizations.
- The less privacy-related information, the better. Treat every public page as if it could be read by anyone on the open internet.
- Apply this rule to titles, subtitles, metadata, body text, tables, notes, and footers.

See [ARTICLE_WRITING_STANDARDS.md](./ARTICLE_WRITING_STANDARDS.md) for the full, stricter rules on factual objectivity, prohibited language, and tone.

Update this AGENT_GUIDE.md whenever the high-level privacy rules change.
