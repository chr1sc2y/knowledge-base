#!/usr/bin/env python3
"""Rebuild bilingual vegetable charts from the checked USDA SR Legacy snapshot."""
from pathlib import Path
import html
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
    highlights=[('纤维 / FIBRE' if zh else 'FIBRE','豌豆仁 5.5 g' if zh else 'Green peas 5.5 g'),('维生素 C / VITAMIN C' if zh else 'VITAMIN C','红彩椒 127.7 mg' if zh else 'Red pepper 127.7 mg'),('钾 / POTASSIUM' if zh else 'POTASSIUM','菠菜 558 mg' if zh else 'Spinach 558 mg')]
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
        text(64,y+3,f[name],23,weight=650)
        text(64,y+25,f[f'{name}_state'],12,'muted')
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
    parts.append('</svg>')
    return '\n'.join(parts)


def fibre_figure(lang):
    zh=lang=='cn';name='zh' if zh else 'en'
    rows=[]
    for f in FOODS:
        v=f['values']['fibre'];portion=f['example_portion_g']
        rows.append(f'<div class="fibre-row" data-value="{v}" data-portion="{portion}"><span class="food-symbol" aria-hidden="true">{f["icon"]}</span><span class="food-name">{esc(f[name])}<small>{esc(f[name+"_state"])}</small></span><div class="fibre-track"><div class="fibre-fill" style="width:{v/6*100:.4f}%"></div></div><strong class="fibre-value">{v:.1f}<small>g</small></strong><span class="portion-label">100 g</span></div>')
    return '<figure class="data-figure fibre-chart"><div class="figure-head"><div><span class="figure-index">01 / FIBRE</span><h3>'+('十二种常见食材的纤维比较' if zh else 'Fibre across twelve everyday ingredients')+'</h3><p>'+('总膳食纤维 · 可食部 · 生菜仅保留罗马生菜作为代表' if zh else 'Total dietary fibre · edible portions · romaine as the single lettuce example')+'</p></div><div class="chart-controls" role="group" aria-label="'+('比较份量' if zh else 'Comparison portions')+'" hidden><button type="button" data-mode="100" aria-pressed="true">'+('每 100 g' if zh else 'Per 100 g')+'</button><button type="button" data-mode="portion" aria-pressed="false">'+('示例份量' if zh else 'Example portions')+'</button></div></div><div class="fibre-axis" aria-hidden="true"><span>0</span><span>2</span><span>4</span><span>6 g</span></div><div class="fibre-bars">'+''.join(rows)+'</div><figcaption><span data-chart-note>'+('每 100 g 比较；比例尺从 0 开始。' if zh else 'Comparison per 100 g; scale begins at zero.')+'</span> <a href="#ref-13">USDA SR Legacy [13]</a></figcaption><p class="chart-announcement sr-only" aria-live="polite"></p></figure>'


def overview_section(lang):
    zh=lang=='cn';name='zh' if zh else 'en'
    asset=('assets/' if zh else '../../articles/assets/')+f'vegetable-nutrient-overview-{lang}.svg'
    png=asset.replace('.svg','.png')
    heading='一张图比较六项营养' if zh else 'Six nutrients in one overview'
    cells=''.join('<tr><td><a href="https://fdc.nal.usda.gov/food-details/'+str(f['fdc_id'])+'/nutrients">'+esc(f[name])+'</a><br><small>'+esc(f[name+'_state'])+'</small></td>'+''.join('<td>'+number(f['values'][n['key']],n['unit'])+'</td>' for n in NUTRIENTS)+'</tr>' for f in FOODS)
    headers='<th>'+('食材与状态' if zh else 'Food and preparation')+'</th>'+''.join('<th>'+esc(n[name])+' / '+n['unit']+'</th>' for n in NUTRIENTS)
    return f'''<section id="overview"><h2>{heading}</h2><p>{'每行一种食材，每列一种营养素。先按需要查列，再比较同列数值；柱长分别按各列最大值缩放，不计算综合得分。' if zh else 'One food per row, one nutrient per column. Compare values within a column; each column scales to its own maximum, with no combined score.'}</p><figure class="data-figure overview-figure"><div class="overview-scroll" tabindex="0" role="region" aria-label="{heading}"><img src="{asset}" width="1440" height="1330" loading="lazy" alt="{'12种食材的纤维、蛋白质、维生素C、钙、钾、镁总览。豌豆仁纤维5.5克，红彩椒维生素C127.7毫克，菠菜钾558毫克；完整数字见下方数据表。' if zh else 'Overview of fibre, protein, vitamin C, calcium, potassium and magnesium for 12 foods. Peas have 5.5 g fibre, red pepper 127.7 mg vitamin C, spinach 558 mg potassium. Full values are available in the table below.'}"></div><figcaption>{'手机可横向滑动；豆类为标注状态的熟重，其余为可食部生重。数值是成分含量，不代表吸收量。' if zh else 'Scroll horizontally on mobile. Legumes use the specified prepared weight; other foods use edible raw weight. Values show nutrient content, not absorption.'} <a href="#ref-13">[13]</a> · <a href="{png}" download="vegetable-nutrition-{lang}.png">{'下载 PNG' if zh else 'Download PNG'}</a> · <a href="{asset}" download="vegetable-nutrition-{lang}.svg">SVG</a></figcaption></figure><details class="data-details"><summary>{'查看完整数据与来源条目' if zh else 'View full data and source entries'}</summary><div class="table-wrap"><table><thead><tr>{headers}</tr></thead><tbody>{cells}</tbody></table></div></details><p class="small">{'生菜使用罗马生菜单一条目，不代表所有生菜。毛豆、豌豆含有的蛋白质与能量也计入整餐；菠菜的钙利用率仍受草酸影响。' if zh else 'Romaine is a single lettuce example, not a proxy for all cultivars. Edamame and peas also contribute protein and meal energy; spinach calcium availability remains affected by oxalate.'}</p></section>'''


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
