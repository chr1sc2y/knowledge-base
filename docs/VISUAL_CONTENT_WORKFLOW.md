# Visual Content Workflow

For Knowledge Base food and nutrition articles, the preferred format is concise
prose, readable HTML tables, and consistent generated ingredient photography.
Quantitative comparisons use tables directly in the page, following the vegetable
article's three-vitamin table. Readers can select, search, or screenshot the data.

## Separate the layers

| Layer | Source of truth | Production method |
| --- | --- | --- |
| Nutrient values and units | Checked public data, exact food entries and preparation states | A committed JSON snapshot |
| Values, percentages, labels and small comparison bars | Snapshot values and explicit calculation rules | Native HTML tables with CSS bars inside cells |
| Ingredient appearance | An ingredient-specific visual brief | Built-in imagegen, followed by visual inspection |

Generate food imagery, not quantitative tables. Keep numbers and labels in code.
Do not replace a table with a standalone infographic image or generate a second
PNG/SVG chart export by default. A table can include inline bars, but the numerical
value, unit, portion and source remain readable text without JavaScript.

## Table conventions

| Question | Preferred table | Required conditions |
| --- | --- | --- |
| How much of one nutrient? | Ingredient, amount per 100 g, amount in an example portion | Show both portions at once; no mode switch needed for screenshots |
| How do several nutrients compare? | One ingredient per row, one nutrient per column | Independent column scales and units are explicit |
| How do vitamin profiles differ? | A few representative vitamins as percentages of one reference system | Name the reference system and population; retain absolute amounts |
| How is a meal divided? | Ingredient, edible weight, percentage of total | Show the total and explain rounding |
| How does absorption change the contribution? | Food, equal input, reference fraction, estimated absorbed amount | Explicit assumptions; no individual prediction |

- Use semantic headers and readable text. Make the primary comparison visible,
  rather than hiding it inside a collapsed details panel.
- Follow the existing vitamin table: restrained rules, large numerical values,
  a small food image beside its name, and optional small bars inside cells.
- Values, labels, units and food images must remain sharp in screenshots.
- Wide tables scroll within their own container on mobile, not across the page.
- Choose distinct common ingredients. A single named lettuce entry is preferable
  to several similar cultivars; include relevant foods such as spinach.
- Do not add arbitrary nutrient percentages into a universal food score. Describe
  complementarity across fibre, vitamins, minerals and actual portions instead.
- Use unrounded source values in calculations and round only the display. A bar
  capped at 100% retains the actual percentage in its label, with the cap explained.

- Use a restrained sequential palette to distinguish magnitudes within a table.
  Current bands are <25%, 25–<50%, 50–<75%, and ≥75%, in muted red-brown,
  yellow, light green and dark green. Name the denominator next to each legend:
  column maximum, FDA DV, or a fixed gram scale. Colour is not a health grade.
- Explain material differences between authoritative food databases beside the
  affected table; retain one consistent source within the main comparison.
- Group related tables and notes into about 4–6 top-level modules. Use subsection
  headings for individual tables rather than expanding the main contents list.

## Image treatment

- Use recognizable ingredient images rather than emoji stand-ins. Similar foods,
  such as garden peas and edamame, need distinct images with accurate morphology.
- Generate chart/table cutouts with the built-in imagegen tool, using a shared
  photography style and one subject-specific prompt per ingredient. Read the
  available imagegen skill before starting a new generation task.
- Cutouts use true transparency, soft light, natural colour, and clear margins.
  Keep the lighting, perspective and treatment consistent across the set.
- Editorial header photographs use a warm ivory surface and show the range of
  foods covered by the article. Expand the composition when more food categories
  are added; keep all ingredient groups visible rather than cropping them away.
- Inspect identity, anatomy, edges, transparency and legibility at display size.
- Copy selected results into the repository. Keep original generated files and
  create optimized derivatives without changing their aspect ratio or alpha.
  Current ingredient thumbnails use a maximum edge of 256 px.
- Save exact prompts and the production method beside assets. Mark generated
  imagery as illustrative; it does not depict measured portions or nutrient values.

Exact cutout prompts:
[`assets/foods/generation.json`](../articles/cn/assets/foods/generation.json).
Current 12-ingredient editorial image prompt:
[`vegetable-editorial-v2.prompt.txt`](../articles/cn/assets/vegetable-editorial-v2.prompt.txt).
Older editorial artwork remains available as prior source material.

## Source files and rebuild

- [`data/vegetable-nutrients.json`](../data/vegetable-nutrients.json): checked USDA
  entries, FDC and nutrient identifiers, preparation states, values and FDA references.
- [`scripts/build_vegetable_visuals.py`](../scripts/build_vegetable_visuals.py):
  bilingual nutrient, vitamin and portion tables, generated from that snapshot.
- [`vegetable-nutrition.css`](../articles/cn/vegetable-nutrition.css): shared table
  treatment, ingredient thumbnails and responsive overflow.
- [`assets/foods/`](../articles/cn/assets/foods/): ingredient images reused by both
  languages. Localize text, not the ingredient artwork.

```bash
python3 scripts/build_vegetable_visuals.py
python3 scripts/build.py
python3 -m unittest discover -s tests
```

The comparison tables require no chart library, JavaScript, Quick Look or Pillow.
The normal build uses committed food images; it does not regenerate them.

## Verification

- Compare every image with its label and inspect it on the actual page background.
- Check units, edible weights, raw/cooked states, percentages and table totals.
- Check both languages and all local built-page asset links.
- Confirm the only large image is editorial artwork, not a rasterized data table.
- Check a narrow viewport: tables scroll locally and the page stays within its width.
- Keep all primary comparison data visible and legible without JavaScript.
- Verify generation is repeatable and screenshot the relevant table during visual QA.
- Follow the task's existing commit/push authorization after checks pass.
