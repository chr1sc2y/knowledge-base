#!/usr/bin/env python3
"""Rebuild bilingual, screenshot-friendly vegetable comparison tables."""
from pathlib import Path
import html
import json
import re
from decimal import Decimal, ROUND_HALF_UP

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/vegetable-nutrients.json').read_text())
FOODS = sorted(DATA['foods'], key=lambda f: -f['values']['fibre'])
NUTRIENTS = DATA['nutrients']


def esc(s):
    return html.escape(str(s), quote=True)


def number(v, unit):
    rounded = str(Decimal(str(v)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
    return rounded if unit == 'g' else rounded.rstrip('0').rstrip('.')


def food_image(f, lang):
    prefix = 'assets/' if lang == 'cn' else '../../articles/assets/'
    return f'<img class="food-thumbnail" src="{prefix}foods/{f["image_slug"]}.png" width="64" height="64" loading="lazy" alt="">'


def food_label(f, lang):
    name = 'zh' if lang == 'cn' else 'en'
    return f'<div class="vitamin-food-label">{food_image(f, lang)}<span><a href="https://fdc.nal.usda.gov/food-details/{f["fdc_id"]}/nutrients">{esc(f[name])}</a><small>{esc(f[name + "_state"])}</small></span></div>'


def table(headers, rows, classes=''):
    head = ''.join(f'<th scope="col">{h}</th>' for h in headers)
    body = ''.join('<tr><th scope="row">' + row[0] + '</th>' + ''.join(f'<td>{v}</td>' for v in row[1:]) + '</tr>' for row in rows)
    return f'<div class="table-wrap"><table class="nutrition-table {classes}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


PALETTE = ('#b7654f', '#c49a36', '#88a166', '#386e54')


def bar_color(ratio):
    # The same four bands apply to the explicitly named scale of each table.
    return PALETTE[sum(ratio >= edge for edge in (0.25, 0.5, 0.75))]


def legend(lang, basis):
    labels = ('<25%', '25–<50%', '50–<75%', '≥75%')
    items = ''.join(f'<span><i style="background:{color}" aria-hidden="true"></i>{esc(label)}</span>' for color, label in zip(PALETTE, labels))
    note = '颜色按未四舍五入的比例分档，不表示健康等级。' if lang == 'cn' else 'Colour bands use unrounded proportions, not health ratings.'
    return f'<div class="scale-legend"><span>{basis}</span>{items}</div><p class="small">{note}</p>'


def broccoli_note(lang):
    text = ('西兰花维 C 的来源差异：本表 USDA 生西兰花为 89.2 mg/100 g；《中国食物成分表 2009 版》为 51 mg/100 g（卫健委标准附录 B 转引）。两者是不同数据库条目，不能把 89.2 mg 视为所有品种、批次或烹调后的固定值。为保持同表口径一致，此处保留 USDA 数据。' if lang == 'cn' else 'Broccoli vitamin C varies across sources: this USDA raw entry contains 89.2 mg/100 g; the Chinese Food Composition Table (2009), reproduced in NHC Appendix B, lists 51 mg/100 g. These are different database entries, not fixed values for every cultivar, batch or cooked portion. The table retains USDA values for consistency.')
    return f'<p class="source-note">{text} <a href="#ref-13">[13]</a>, <a href="#ref-15">[15]</a></p>'


def amount(value, unit, maximum):
    width = min(value / maximum * 100, 100)
    color = bar_color(value / maximum)
    return f'<strong class="amount">{number(value, unit)}<small>{unit}</small></strong><div class="vitamin-track" aria-hidden="true"><i style="width:{width:.4f}%;background:{color}"></i></div>'


def overview_section(lang):
    zh = lang == 'cn'; name = 'zh' if zh else 'en'
    heading = '六项营养含量' if zh else 'Six nutrient amounts'
    headers = [('食材与状态' if zh else 'Food and preparation')] + [f'{n[name]}<small>{n["unit"]} / 100 g</small>' for n in NUTRIENTS]
    maxima = {n['key']: max(f['values'][n['key']] for f in FOODS) for n in NUTRIENTS}
    rows = [[food_label(f, lang)] + [amount(f['values'][n['key']], n['unit'], maxima[n['key']]) for n in NUTRIENTS] for f in FOODS]
    intro = '每 100 g 可食部；柱条只在同一列内比较，各列独立缩放，不计算综合得分。食材名称对应 USDA 的具体品种与生熟状态。' if zh else 'Per 100 g edible portion. Bars compare values within each column, using independent scales and no combined score. Food names identify the USDA entry and preparation state.'
    note = '豆类为标注状态的熟重，其余为可食部生重；数值是成分含量，不代表吸收量。食材图片为 AI 生成示意。' if zh else 'Legumes use the specified prepared weight; other foods use edible raw weight. Nutrient content is not absorption. AI-generated ingredient illustrations.'
    return f'<section id="overview"><h2>{heading}</h2><p>{intro}</p>{legend(lang, "占本列最大值：" if zh else "Share of column maximum:")}{table(headers, rows, "overview-table")}{broccoli_note(lang)}<p class="small">{note} <a href="#ref-13">[13]</a></p></section>'


def fibre_section(lang):
    zh = lang == 'cn'; name = 'zh' if zh else 'en'
    heading = '纤维含量与食用份量' if zh else 'Fibre content and serving size'
    headers = ['食材与状态', '每 100 g 的纤维', '示例份量的纤维'] if zh else ['Food and preparation', 'Fibre per 100 g', 'Fibre in an example portion']
    rows = []
    for f in FOODS:
        v = f['values']['fibre']; weight = f['example_portion_g']
        serving = amount(v * weight / 100, 'g', 6) + f'<small class="portion-weight">{weight} g '+('食材' if zh else 'food')+'</small>'
        rows.append([food_label(f, lang), amount(v, 'g', 6), serving])
    intro = '采用总膳食纤维数据，生菜仅保留罗马生菜作为代表。两列柱条均以 6 g 为上限、从零开始；右列份量只是换算示例。' if zh else 'Total dietary fibre, with romaine as one lettuce example. Both columns use a zero-based 6 g scale. Right-hand portions illustrate the calculation only.'
    definition = '数据库可能记录总膳食纤维或仅不溶性纤维，数值比较需采用同一口径；生菜品种也会影响结果。' if zh else 'Databases may report total dietary fibre or only insoluble fibre. Comparisons require matching definitions, and lettuce cultivars also differ.'
    formula = '一份的贡献 = 每 100 g 含量 × 可食份量 ÷ 100。' if zh else 'Serving contribution = amount per 100 g × edible portion ÷ 100.'
    example = '200 g 生西兰花与 100 g 熟毛豆仁合计约 10.4 g 纤维，仍只覆盖全天参考量的一部分。生熟数据用于配餐估算，不能推断烹调提高了纤维含量。' if zh else '200 g raw broccoli plus 100 g prepared edamame supplies about 10.4 g fibre, only part of the daily reference range. Raw and prepared entries support meal estimates, not conclusions about the effect of cooking.'
    return f'<section id="fibre"><h2>{heading}</h2><p>{intro} <a href="#ref-13">[13]</a></p>{legend(lang, "占 6 g 刻度上限：" if zh else "Share of the 6 g scale:")}{table(headers, rows, "fibre-table")}<p class="small">{definition} <a href="#ref-2">[2]</a></p><p><strong>{formula}</strong> {example}</p></section>'


def vitamin_section(lang):
    zh=lang=='cn';name='zh' if zh else 'en'
    nutrients=DATA['vitamin_profile']['nutrients']
    heading='三种维生素供给比例' if zh else 'Three-vitamin profile'
    rows=[]; raw_rows=[]
    for f in FOODS:
        cells=[];raw=[]
        for n in nutrients:
            value=f['values'][n['key']];pct=value/n['dv']*100
            color=bar_color(pct / 100)
            cells.append(f'<td><strong>{int(pct + 0.5)}<small>%</small></strong><div class="vitamin-track" aria-hidden="true"><i style="width:{min(pct,100):.4f}%;background:{color}"></i></div></td>')
            raw.append(f'<td>{number(value,"mg")}</td>')
        state=esc(f[name+'_state'])
        rows.append(f'<tr><th scope="row"><div class="vitamin-food-label">{food_image(f,lang)}<span>{esc(f[name])}<small>{state}</small></span></div></th>'+''.join(cells)+'</tr>')
        raw_rows.append(f'<tr><td>{esc(f[name])} · {state}</td>'+''.join(raw)+'</tr>')
    headers=''.join(f'<th scope="col">{n[name]}<small>100% = {n["dv"]} {n["unit"]}</small></th>' for n in nutrients)
    rawheaders=''.join(f'<th>{n[name]} / {n["unit"]}</th>' for n in nutrients)
    return f'''<section id="vitamin-profile"><h2>{heading}</h2><div class="data-table-group vitamin-profile"><div class="figure-head"><div><p>{'每 100 g 可食部 · 相对于同一套 FDA 标签参考值的百分比' if zh else 'Per 100 g edible portion · percentage of the same FDA reference system'}</p></div></div><p class="small">{'西兰花维 C：89.2 mg ÷ 90 mg ≈ 99% DV，仅对应此 USDA 生食条目；中国成分表的 51 mg 按同一 DV 换算约为 57%，不是本表取值。' if zh else 'Broccoli vitamin C: 89.2 mg ÷ 90 mg ≈ 99% DV for this USDA raw entry. The Chinese entry of 51 mg would equal about 57% of the same DV; it is not the value used here.'} <a href="#ref-13">[13]</a>, <a href="#ref-15">[15]</a></p>{legend(lang, "占 FDA DV：" if zh else "Share of FDA DV:")}<div class="vitamin-scroll" tabindex="0" role="region" aria-label="{'维生素组合比较' if zh else 'Vitamin profile comparison'}"><table class="nutrition-table"><thead><tr><th scope="col">{'食材与状态' if zh else 'Food and preparation'}</th>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table></div><p class="small">{'百分比四舍五入。三列均采用 0–100% 的相同比例尺；超过 100% 时柱条封顶，数值保留实际百分比。FDA DV 是美国成人及 4 岁以上儿童标签比较值，不是中国推荐摄入量或个体营养处方。这里只展示 A、C、叶酸，不代表全部维生素的覆盖率。' if zh else 'Percentages are rounded. All columns use the same 0–100% scale; bars stop at 100% while labels retain the actual percentage. FDA DVs are US label references for adults and children aged 4 and older, not Chinese recommendations or individual targets. This profiles A, C and folate, not all vitamins.'} <a href="#ref-13">[13]</a>, <a href="#ref-14">[14]</a></p></div><p><strong>{'表格要点：' if zh else 'Reading the table: '}</strong>{'胡萝卜偏重维生素 A 原；红彩椒、西兰花偏重维生素 C；菠菜同时提供维生素 A 与叶酸；毛豆在叶酸和蛋白质上有贡献。不同食材的优势分布，构成搭配依据；三个百分比不相加为总分。' if zh else 'Carrots emphasize provitamin A; red pepper and broccoli emphasize vitamin C; spinach contributes both vitamin A and folate; edamame contributes folate and protein. These patterns support complementary combinations; the three percentages are not added into a score.'} <a href="#ref-7">[7]</a>, <a href="#ref-13">[13]</a></p><details class="data-details"><summary>{'查看原始含量与计算口径' if zh else 'View absolute amounts and calculation basis'}</summary><p class="small">{'百分比 = 每 100 g 的营养素含量 ÷ 对应 DV × 100%。维生素 A 已采用 RAE，叶酸采用 DFE；不直接把胡萝卜素重量当维生素 A。生熟状态与前表一致。' if zh else 'Percentage = amount per 100 g ÷ the corresponding DV × 100. Vitamin A uses RAE and folate uses DFE; carotene mass is not equated directly to vitamin A. Preparation states match the preceding table.'}</p><div class="table-wrap"><table class="nutrition-table"><thead><tr><th>{'食材' if zh else 'Food'}</th>{rawheaders}</tr></thead><tbody>{''.join(raw_rows)}</tbody></table></div></details><p class="small">{'现有每 100 kcal 营养密度评分提供另一种综合比较口径，但排名依赖所选营养素、权重与能量分母，不能替代实际份量与吸收条件。' if zh else 'Nutrient-density scores per 100 kcal offer another composite comparison, but results depend on selected nutrients, weights and energy denominators. They do not replace serving and availability information.'} <a href="#ref-4">[4]</a></p></section>'''


def replace_section(s, section_id, replacement):
    # Generated blocks live inside a single top-level nutrition section.
    pattern = rf'<!-- generated:{section_id} -->.*?<!-- /generated:{section_id} -->'
    replacement = replacement.replace('<section ', '<div class="nutrition-subsection" ', 1).replace('<h2>', '<h3>', 1).replace('</h2>', '</h3>', 1)
    replacement = replacement.removesuffix('</section>') + '</div>'
    assert re.search(pattern, s, re.S), f'Missing generated block: {section_id}'
    return re.sub(pattern, lambda _: f'<!-- generated:{section_id} -->{replacement}<!-- /generated:{section_id} -->', s, flags=re.S)


def build():
    for lang in ['cn', 'en']:
        path = ROOT / 'articles' / lang / 'vegetable-nutrition-and-selection.html'
        s = path.read_text()
        for section_id, render in [('overview', overview_section), ('vitamin-profile', vitamin_section), ('fibre', fibre_section)]:
            s = replace_section(s, section_id, render(lang))
        path.write_text(s)


if __name__=='__main__':
    build()
