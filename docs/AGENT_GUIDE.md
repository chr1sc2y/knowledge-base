# Agent Guide

This document is the single operating guide for agents maintaining this
Knowledge Base. Keep it concise and update it whenever the site architecture,
language rules, or project status changes.

## Product Goal

Build a public static Knowledge Base at `knowledge.prov1dence.top` for durable
learning pages. The site should feel calm, direct, and study-oriented. It should
not feel like a dashboard, blog feed, marketing page, or card-heavy template.

## Design Rules

- Use bilingual content for every public page: Simplified Chinese and English.
- Provide a language switch in the same location on every page, preferably the
  top-right corner of the viewport/header.
- Home page should be a quiet index, not a card grid.
- Home page should not show References. References belong at the bottom of an
  article or on a dedicated links page.
- Article pages should primarily use typography, spacing, headings, diagrams,
  lists, and tables. Avoid making every concept a card.
- Cards are reserved for truly framed tools, quizzes, warnings, or interactive
  elements. Do not use cards as the default content container.
- Simplicity means reducing friction and visual competition, not merely using
  white backgrounds and rounded rectangles.
- Prefer progressive learning structure: intuition, vocabulary, mechanism,
  regulation, practice, sources. Do not label learning depth as literal school
  stages such as elementary/middle/high/undergraduate/master unless the user
  explicitly asks for that metaphor on screen.

The selected visual direction is the warmer editorial template:

- paper background `#f7f3ea`
- serif display headings
- muted body text
- ink/accent palette (`#163d3a`, `#b24b2f`)
- article sections separated by rules, not floating cards

## Bilingual Architecture

Current URL shape:

```text
/
/en/
/articles/<slug>.html
/en/articles/<slug>.html
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
- Editorial learning template selected for production.
- Data files for pages and useful links.
- Two local design demos:
  - `demos/apple/` for an Apple-like minimal direction.
  - `demos/editorial/` for a warmer editorial learning direction.

Pending:

- Confirm DNS points `knowledge.prov1dence.top` to GitHub Pages.
- Enable HTTPS enforcement after GitHub issues the certificate.

## Maintenance Workflow

1. Add or edit content in both Chinese and English.
2. Keep language-pair links in sync.
3. Run the build script or local demo server.
4. Verify:
   - HTML parses.
   - JavaScript parses.
   - Language switch links resolve.
   - Homepage has no visible References section.
   - Article pages are not dominated by cards.
5. Commit only after verification.
