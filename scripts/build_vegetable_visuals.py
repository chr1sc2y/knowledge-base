#!/usr/bin/env python3
"""Rebuild bilingual vegetable charts from the checked USDA SR Legacy snapshot."""
from pathlib import Path
import html
import base64
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/vegetable-nutrients.json').read_text())
FOODS = sorted(DATA['foods'], key=lambda f: -f['values']['fibre'])
NUTRIENTS = DATA['nutrients']
ASSETS = ROOT / 'articles/cn/assets'


def esc(s):
    return html.escape(str(s), quote=True)


def number(v, unit):
    return f'{v:.1f}' if unit == 'g' else f'{v:.1f}'.rstrip('0').rstrip('.')


def food_image(f, lang):
    prefix='assets/' if lang=='cn' else '../../articles/assets/'
    return f'<img class="food-thumbnail" src="{prefix}foods/{f["image_slug"]}.png" width="64" height="64" loading="lazy" alt="">'


def overview_svg(lang):
    zh = lang == 'cn'
    name = 'zh' if zh else 'en'
    maxima = {n['key']: max(f['values'][n['key']] for f in FOODS) for n in NUTRIENTS}
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1330" viewBox="0 0 1440 1330" role="img" aria-labelledby="title desc">',
             f'<title id="title">{esc("12 种常见食材的六项营养比较" if zh else "Six nutrients across 12 everyday ingredients")}</title>',
             f'<desc id="desc">{esc("每100克可食部，生熟分别标注；每列独立缩放，数值为营养含量，不代表吸收量。" if zh else "Per 100 g edible portion, preparation labelled. Each column uses its own scale. Values describe content, not absorption.")}</desc>',
             '<rect width="1440" height="1330" fill="#f5f1e8"/>',
             '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Noto Sans SC","PingFang SC",sans-serif;fill:#203d34}.muted{fill:#68716c}.unit{fill:#8b7665;font-size:17px}.value{font-size:24px;font-variant-numeric:tabular-nums}a{text-decoration:none}</style>']
    def text(x,y,value,size=20,cls='',weight='',anchor='start'):
        parts.append(f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}" font-weight="{weight or 400}" text-anchor="{anchor}">{esc(value)}</text>')
    text(64,60,'FOOD COMPARISON / 12 × 6',16,'unit',700)
    text(64,119,'常见蔬菜，一张图比较' if zh else 'Everyday vegetables, compared',44,weight=650)
    text(64,160,'每 100 g 可食部 · 同版 USDA 数据 · 仅比较图中 12 种食材' if zh else 'Per 100 g edible portion · one USDA release · only these 12 ingredients',20,'muted')
    highlights=[]
    for key,label in [('fibre','纤维 / FIBRE' if zh else 'FIBRE'),('vitamin_c','维生素 C / VITAMIN C' if zh else 'VITAMIN C'),('potassium','钾 / POTASSIUM' if zh else 'POTASSIUM')]:
        food=max(FOODS,key=lambda f:f['values'][key])
        nutrient=next(n for n in NUTRIENTS if n['key']==key)
        value=f"{food[name]} {number(food['values'][key],nutrient['unit'])} {nutrient['unit']}"
        highlights.append((label,value))
    for i,(label,value) in enumerate(highlights):
        x=64+i*450
        parts.append(f'<line x1="{x}" y1="202" x2="{x}" y2="260" stroke="#a6b394" stroke-width="3"/>')
        text(x+17,219,label,15,'unit',600);text(x+17,251,value,25,weight=650)
    parts.append('<line x1="64" y1="286" x2="1376" y2="286" stroke="#cfc5b3"/>')
    text(64,324,'食材 / 状态' if zh else 'Food / preparation',18,'muted')
    for col,n in enumerate(NUTRIENTS):
        x=340+col*172
        text(x,317,n[name],20,weight=650)
        text(x,342,n['unit'],15,'unit')
    for i,f in enumerate(FOODS):
        y=378+i*65
        if i%2 == 0: parts.append(f'<rect x="48" y="{y-19}" width="1344" height="65" rx="3" fill="#eee8db"/>')
        parts.append(f'<a href="https://fdc.nal.usda.gov/food-details/{f["fdc_id"]}/nutrients"><title>{esc(f["usda_description"])}; FDC {f["fdc_id"]}</title>')
        image=base64.b64encode((ASSETS/'foods'/f'{f["image_slug"]}.png').read_bytes()).decode('ascii')
        parts.append(f'<image href="data:image/png;base64,{image}" x="62" y="{y-21}" width="52" height="52"/>')
        text(128,y+3,f[name],23,weight=650)
        text(128,y+25,f[f'{name}_state'],12,'muted')
        parts.append('</a>')
        for col,n in enumerate(NUTRIENTS):
            x=340+col*172;v=f['values'][n['key']];maxv=maxima[n['key']]
            text(x,y+3,number(v,n['unit']),24,'value',700 if v==maxv else 450)
            parts.append(f'<rect x="{x}" y="{y+16}" width="132" height="7" rx="2" fill="#ddd7c9"/>')
            parts.append(f'<rect x="{x}" y="{y+16}" width="{132*v/maxv:.4f}" height="7" rx="2" fill="{"#ad5437" if v==maxv else "#688164"}"/>')
    parts.append('<line x1="64" y1="1180" x2="1376" y2="1180" stroke="#cfc5b3"/>')
    text(64,1215,'柱长仅在同一列内比较；橙色表示本图该列最大值，不代表综合营养排名。' if zh else 'Compare bar lengths within a column only. Rust marks that column’s maximum, not overall nutritional rank.',18,'muted')
    text(64,1245,'豌豆、毛豆为熟食数据，其余为生食数据；钙含量不等于吸收量。' if zh else 'Peas and edamame use prepared values; other foods use raw values. Calcium content is not absorbed calcium.',18,'muted')
    text(64,1280,'USDA FoodData Central · SR Legacy · April 2018 · knowledge.prov1dence.top',16,'muted')
    text(64,1310,'食材图片为 AI 生成示意，不代表定量份量。' if zh else 'AI-generated ingredient illustrations; images do not depict measured portions.',14,'muted')
    parts.append('</svg>')
    return '\n'.join(parts)


def fibre_figure(lang):
    zh=lang=='cn';name='zh' if zh else 'en'
    rows=[]
    for f in FOODS:
        v=f['values']['fibre'];portion=f['example_portion_g']
        rows.append(f'<div class="fibre-row" data-value="{v}" data-portion="{portion}">{food_image(f, lang)}<span class="food-name">{esc(f[name])}<small>{esc(f[name+"_state"])}</small></span><div class="fibre-track"><div class="fibre-fill" style="width:{v/6*100:.4f}%"></div></div><strong class="fibre-value">{v:.1f}<small>g</small></strong><span class="portion-label">100 g</span></div>')
    return '<figure class="data-figure fibre-chart"><div class="figure-head"><div><span class="figure-index">02 / FIBRE</span><h3>'+('十二种常见食材的纤维比较' if zh else 'Fibre across twelve everyday ingredients')+'</h3><p>'+('总膳食纤维 · 可食部 · 生菜仅保留罗马生菜作为代表' if zh else 'Total dietary fibre · edible portions · romaine as the single lettuce example')+'</p></div><div class="chart-controls" role="group" aria-label="'+('比较份量' if zh else 'Comparison portions')+'" hidden><button type="button" data-mode="100" aria-pressed="true">'+('每 100 g' if zh else 'Per 100 g')+'</button><button type="button" data-mode="portion" aria-pressed="false">'+('示例份量' if zh else 'Example portions')+'</button></div></div><div class="fibre-axis" aria-hidden="true"><span>0</span><span>2</span><span>4</span><span>6 g</span></div><div class="fibre-bars">'+''.join(rows)+'</div><figcaption><span data-chart-note>'+('每 100 g 比较；比例尺从 0 开始。食材图片为 AI 生成示意。' if zh else 'Comparison per 100 g; scale begins at zero. AI-generated ingredient illustrations.')+'</span> <a href="#ref-13">USDA SR Legacy [13]</a></figcaption><p class="chart-announcement sr-only" aria-live="polite"></p></figure>'


def overview_section(lang):
    zh=lang=='cn';name='zh' if zh else 'en'
    asset=('assets/' if zh else '../../articles/assets/')+f'vegetable-nutrient-overview-{lang}.svg'
    png=asset.replace('.svg','.png')
    heading='一张图比较六项营养' if zh else 'Six nutrients in one overview'
    cells=''.join('<tr><td><a href="https://fdc.nal.usda.gov/food-details/'+str(f['fdc_id'])+'/nutrients">'+esc(f[name])+'</a><br><small>'+esc(f[name+'_state'])+'</small></td>'+''.join('<td>'+number(f['values'][n['key']],n['unit'])+'</td>' for n in NUTRIENTS)+'</tr>' for f in FOODS)
    headers='<th>'+('食材与状态' if zh else 'Food and preparation')+'</th>'+''.join('<th>'+esc(n[name])+' / '+n['unit']+'</th>' for n in NUTRIENTS)
    return f'''<section id="overview"><h2>{heading}</h2><p>{'每行一种食材，每列一种营养素。先按需要查列，再比较同列数值；柱长分别按各列最大值缩放，不计算综合得分。' if zh else 'One food per row, one nutrient per column. Compare values within a column; each column scales to its own maximum, with no combined score.'}</p><figure class="data-figure overview-figure"><div class="overview-scroll" tabindex="0" role="region" aria-label="{heading}"><img src="{asset}" width="1440" height="1330" loading="lazy" alt="{'12种食材的纤维、蛋白质、维生素C、钙、钾、镁总览。豌豆仁纤维5.5克，红彩椒维生素C127.7毫克，菠菜钾558毫克；完整数字见下方数据表。' if zh else 'Overview of fibre, protein, vitamin C, calcium, potassium and magnesium for 12 foods. Peas have 5.5 g fibre, red pepper 127.7 mg vitamin C, spinach 558 mg potassium. Full values are available in the table below.'}"></div><figcaption>{'手机可横向滑动；豆类为标注状态的熟重，其余为可食部生重。数值是成分含量，不代表吸收量。' if zh else 'Scroll horizontally on mobile. Legumes use the specified prepared weight; other foods use edible raw weight. Values show nutrient content, not absorption.'} <a href="#ref-13">[13]</a> · <a href="{png}" download="vegetable-nutrition-{lang}.png">{'下载 PNG' if zh else 'Download PNG'}</a> · <a href="{asset}" download="vegetable-nutrition-{lang}.svg">SVG</a></figcaption></figure><details class="data-details"><summary>{'查看完整数据与来源条目' if zh else 'View full data and source entries'}</summary><div class="table-wrap"><table><thead><tr>{headers}</tr></thead><tbody>{cells}</tbody></table></div></details><p class="small">{'生菜使用罗马生菜单一条目，不代表所有生菜。毛豆、豌豆含有的蛋白质与能量也计入整餐；菠菜的钙利用率仍受草酸影响。' if zh else 'Romaine is a single lettuce example, not a proxy for all cultivars. Edamame and peas also contribute protein and meal energy; spinach calcium availability remains affected by oxalate.'}</p></section>'''


def vitamin_section(lang):
    zh=lang=='cn';name='zh' if zh else 'en'
    nutrients=DATA['vitamin_profile']['nutrients']
    heading='综合评价：看营养组合与互补' if zh else 'A combined view: nutritional roles and complementarity'
    dimensions=[('纤维供给','Fibre supply','总膳食纤维与一份食用量','Total fibre and serving size'),('维生素组合','Vitamin profile','维生素 A、C 与叶酸的不同分布','Different patterns of vitamins A, C and folate'),('矿物质来源','Mineral sources','钙、钾、镁含量与吸收条件','Calcium, potassium and magnesium; availability matters'),('实际膳食贡献','Contribution to the diet','食用份量、生熟状态与整餐能量','Portions, preparation and total meal energy')]
    roles='<div class="nutrition-roles">'+''.join(f'<div><strong>{z if zh else e}</strong><span>{detail if zh else edetail}</span></div>' for z,e,detail,edetail in dimensions)+'</div>'
    rows=[]; table=[]
    for f in FOODS:
        cells=[];raw=[]
        for n in nutrients:
            value=f['values'][n['key']];pct=value/n['dv']*100
            color={'vitamin_a_rae':'#a78637','vitamin_c':'#ad5437','folate_dfe':'#446d52'}[n['key']]
            cells.append(f'<td><strong>{int(pct + 0.5)}<small>%</small></strong><div class="vitamin-track"><i style="width:{min(pct,100):.4f}%;background:{color}"></i></div></td>')
            raw.append(f'<td>{number(value,"mg")}</td>')
        state=esc(f[name+'_state'])
        rows.append(f'<tr><th scope="row"><div class="vitamin-food-label">{food_image(f,lang)}<span>{esc(f[name])}<small>{state}</small></span></div></th>'+''.join(cells)+'</tr>')
        table.append(f'<tr><td>{esc(f[name])} · {state}</td>'+''.join(raw)+'</tr>')
    headers=''.join(f'<th scope="col">{n[name]}<small>100% = {n["dv"]} {n["unit"]}</small></th>' for n in nutrients)
    rawheaders=''.join(f'<th>{n[name]} / {n["unit"]}</th>' for n in nutrients)
    return f'''<section id="vitamin-profile"><h2>{heading}</h2><p>{'综合评价可以拆成四个问题，分别保留指标；避免某一项特别高，就被解释成整种食物“全面胜出”。' if zh else 'A combined assessment can retain four separate questions. An exceptional value for one nutrient does not establish overall superiority.'}</p>{roles}<figure class="data-figure vitamin-profile"><div class="figure-head"><div><span class="figure-index">01 / VITAMIN PROFILE</span><h3>{'三种代表维生素的供给比例' if zh else 'Three representative vitamins: contribution per 100 g'}</h3><p>{'每 100 g 可食部 · 相对于同一套 FDA 标签参考值的百分比' if zh else 'Per 100 g edible portion · percentage of the same FDA reference system'}</p></div></div><div class="vitamin-scroll" tabindex="0" role="region" aria-label="{'维生素组合比较' if zh else 'Vitamin profile comparison'}"><table><thead><tr><th scope="col">{'食材与状态' if zh else 'Food and preparation'}</th>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table></div><figcaption>{'百分比四舍五入。三列均采用 0–100% 的相同比例尺；超过 100% 时柱条封顶，数值保留实际百分比。FDA DV 是美国成人及 4 岁以上儿童标签比较值，不是中国推荐摄入量或个体营养处方。这里只展示 A、C、叶酸，不代表全部维生素的覆盖率。' if zh else 'Percentages are rounded. All columns use the same 0–100% scale; bars stop at 100% while labels retain the actual percentage. FDA DVs are US label references for adults and children aged 4 and older, not Chinese recommendations or individual targets. This profiles A, C and folate, not all vitamins.'} <a href="#ref-13">[13]</a>, <a href="#ref-14">[14]</a></figcaption></figure><p><strong>{'读图结论：' if zh else 'Reading the profile: '}</strong>{'胡萝卜偏重维生素 A 原；红彩椒、西兰花偏重维生素 C；菠菜同时提供维生素 A 与叶酸；毛豆在叶酸和蛋白质上有贡献。不同食材的优势分布，构成搭配依据；三个百分比不相加为总分。' if zh else 'Carrots emphasize provitamin A; red pepper and broccoli emphasize vitamin C; spinach contributes both vitamin A and folate; edamame contributes folate and protein. These patterns support complementary combinations; the three percentages are not added into a score.'} <a href="#ref-7">[7]</a>, <a href="#ref-13">[13]</a></p><details class="data-details"><summary>{'查看原始含量与计算口径' if zh else 'View absolute amounts and calculation basis'}</summary><p class="small">{'百分比 = 每 100 g 的营养素含量 ÷ 对应 DV × 100%。维生素 A 已采用 RAE，叶酸采用 DFE；不直接把胡萝卜素重量当维生素 A。生熟状态与前图一致。' if zh else 'Percentage = amount per 100 g ÷ the corresponding DV × 100. Vitamin A uses RAE and folate uses DFE; carotene mass is not equated directly to vitamin A. Preparation states match the preceding chart.'}</p><div class="table-wrap"><table><thead><tr><th>{'食材' if zh else 'Food'}</th>{rawheaders}</tr></thead><tbody>{''.join(table)}</tbody></table></div></details><p class="small">{'现有每 100 kcal 营养密度评分提供另一种综合比较口径，但排名依赖所选营养素、权重与能量分母，不能替代实际份量与吸收条件。' if zh else 'Nutrient-density scores per 100 kcal offer another composite comparison, but results depend on selected nutrients, weights and energy denominators. They do not replace serving and availability information.'} <a href="#ref-4">[4]</a></p></section>'''


def build():
    ASSETS.mkdir(exist_ok=True)
    for lang in ['cn','en']:
        zh=lang=='cn';name='zh' if zh else 'en'
        (ASSETS/f'vegetable-nutrient-overview-{lang}.svg').write_text(overview_svg(lang))
        path=ROOT/'articles'/lang/'vegetable-nutrition-and-selection.html'
        s=path.read_text()
        s=re.sub(r'<figure class="data-figure fibre-chart">.*?</figure>',lambda _:fibre_figure(lang),s,flags=re.S)
        # Keep the exact data table synchronized with the plotted records.
        start=s.index('<section id="fibre">');end=s.index('</section>',start)
        chunk=s[start:end]
        rowhtml=''.join(f'<tr><td>{esc(f[name])} · {esc(f[name+"_state"])}</td><td>{f["values"]["fibre"]:.1f}</td></tr>' for f in FOODS)
        chunk=re.sub(r'(<tbody>).*?(</tbody>)',lambda m:m[1]+rowhtml+m[2],chunk,flags=re.S)
        chunk=chunk.replace('USDA 总膳食纤维数据','USDA SR Legacy 同版总膳食纤维数据').replace('The chart uses the USDA total-fibre table.', 'The chart uses the USDA SR Legacy snapshot.')
        # Retain the previous fibre reference for its definition; add the exact snapshot reference.
        chunk=chunk.replace('href="#ref-3">[3]</a>', 'href="#ref-13">[13]</a>')
        s=s[:start]+chunk+s[end:]
        section=overview_section(lang)
        if '<section id="overview">' in s:
            s=re.sub(r'<section id="overview">.*?</section>',lambda _:section,s,flags=re.S)
        else:
            pos=s.index('<section id="fibre">');s=s[:pos]+section+'\n'+s[pos:]
            toc='<li><a href="#overview">'+('一张图比较六项营养' if zh else 'Six nutrients in one overview')+'</a></li>'
            s=s.replace('<li><a href="#fibre">',toc+'<li><a href="#fibre">',1)
        if 'id="ref-13"' not in s:
            at=s.index('</ol>',s.index('<section id="sources">'))
            ref='<li id="ref-13"><a href="https://fdc.nal.usda.gov/download-datasets/">'+('USDA FoodData Central：SR Legacy 2018 年 4 月数据；完整表内链接至各 FDC 条目' if zh else 'USDA FoodData Central: SR Legacy April 2018; full table links to individual FDC records')+'</a></li>'
            s=s[:at]+ref+s[at:]
        profile=vitamin_section(lang)
        if '<section id="vitamin-profile">' in s:
            s=re.sub(r'<section id="vitamin-profile">.*?</section>',lambda _:profile,s,flags=re.S)
        else:
            pos=s.index('<section id="fibre">');s=s[:pos]+profile+'\n'+s[pos:]
            toc='<li><a href="#vitamin-profile">'+('综合评价：看营养组合与互补' if zh else 'A combined view: nutritional roles and complementarity')+'</a></li>'
            s=s.replace('<li><a href="#fibre">',toc+'<li><a href="#fibre">',1)
        if 'id="ref-14"' not in s:
            pos=s.index('</ol>',s.index('<section id="sources">'))
            reference='<li id="ref-14"><a href="'+DATA['vitamin_profile']['reference_url']+'">'+('FDA：营养标签每日参考值 DV（维生素 A、C、叶酸）' if zh else 'FDA: Daily Values for nutrition labels (vitamins A, C and folate)')+'</a></li>'
            s=s[:pos]+reference+s[pos:]
        path.write_text(s)


def export_png():
    # Optional macOS export; ordinary SVG/HTML generation uses only the stdlib.
    import subprocess
    import tempfile
    from PIL import Image
    with tempfile.TemporaryDirectory(prefix='vegetable-overview-') as directory:
        tmp = Path(directory)
        for lang in ['cn', 'en']:
            source = ASSETS / f'vegetable-nutrient-overview-{lang}.svg'
            square = source.read_text().replace('height="1330" viewBox="0 0 1440 1330"', 'height="1440" viewBox="0 0 1440 1440"').replace('<rect width="1440" height="1330"', '<rect width="1440" height="1440"')
            intermediate = tmp / source.name
            intermediate.write_text(square)
            subprocess.run(['qlmanage', '-t', '-s', '1800', '-o', str(tmp), str(intermediate)], check=True, stdout=subprocess.DEVNULL)
            image = Image.open(tmp / (source.name + '.png'))
            # Remove only the export padding; chart content remains unchanged.
            image.crop((0, 0, image.width, round(image.height * 1330 / 1440))).save(source.with_suffix('.png'), optimize=True)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--png', action='store_true', help='Also export PNGs with macOS Quick Look and Pillow')
    args=parser.parse_args()
    build()
    if args.png:
        export_png()
