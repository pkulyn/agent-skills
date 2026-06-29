#!/usr/bin/env python3
"""Generate gold price chart PPTs for 流派1 (01-04) and 流派3 (09-12)."""
import os

OUT_DIR = "/home/clawbot/.openclaw/workspace/skills/my-design/demos/gold_chart_samples"
os.makedirs(OUT_DIR, exist_ok=True)

GOLD_YEARS = [2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025]
GOLD_PRICES = [1160,1251,1257,1269,1393,1770,1799,1800,1940,2386,2850]
MIN_PRICE = min(GOLD_PRICES)
MAX_PRICE = max(GOLD_PRICES)

def bar_svg(s, chart_x=100, chart_y=60, chart_w=1520, chart_h=700, bar_gap=16):
    """Generate SVG bar chart for a style."""
    n = len(GOLD_YEARS)
    bar_w = (chart_w - (n-1)*bar_gap) / n
    # Y range: round to nice numbers
    y_min = 1000
    y_max = 3000
    y_range = y_max - y_min
    
    svg = f'<svg viewBox="0 0 {chart_w+chart_x+60} {chart_h+chart_y+80}" style="width:100%;height:100%">'
    
    # Grid lines
    for val in range(1000, 3001, 500):
        y = chart_y + chart_h - (val - y_min) / y_range * chart_h
        svg += f'<line x1="{chart_x}" y1="{y:.0f}" x2="{chart_x+chart_w}" y2="{y:.0f}" stroke="{s["grid_color"]}" stroke-width="0.5" stroke-dasharray="4,4"/>'
        svg += f'<text x="{chart_x-10}" y="{y+4:.0f}" text-anchor="end" fill="{s["muted"]}" font-size="13" font-family="{s["font_b"]}">{val}</text>'
    
    # Bars
    for i, (year, price) in enumerate(zip(GOLD_YEARS, GOLD_PRICES)):
        x = chart_x + i * (bar_w + bar_gap)
        bar_h = (price - y_min) / y_range * chart_h
        y = chart_y + chart_h - bar_h
        
        # Highlight 2024-2025 with accent2
        fill = s["bar_accent"] if year >= 2024 else s["bar_color"]
        svg += f'<rect x="{x:.0f}" y="{y:.0f}" width="{bar_w:.0f}" height="{bar_h:.0f}" fill="{fill}" rx="{s["bar_radius"]}"/>'
        
        # Price label on top
        svg += f'<text x="{x+bar_w/2:.0f}" y="{y-8:.0f}" text-anchor="middle" fill="{s["fg"]}" font-size="13" font-weight="600" font-family="{s["font_d"]}">${price}</text>'
        
        # Year label
        svg += f'<text x="{x+bar_w/2:.0f}" y="{chart_y+chart_h+24:.0f}" text-anchor="middle" fill="{s["muted"]}" font-size="13" font-family="{s["font_b"]}">{year}</text>'
    
    svg += '</svg>'
    return svg


styles = {
    "01": {
        "name": "01 Pentagram式信息建筑", "group": "流派1·信息建筑派",
        "bg": "#E8E4DF", "card": "#FFFFFF", "fg": "#1A1A1A", "muted": "#6B6B6B",
        "accent": "#C4161C", "accent2": "#C4161C", "border": "rgba(26,26,26,0.08)",
        "font_d": "'Helvetica Neue','Noto Sans SC',sans-serif",
        "font_b": "'Georgia','Noto Serif SC',serif",
        "radius": "2px", "shadow": "0 1px 8px rgba(26,26,26,0.08)",
        "body_bg": "#D8D4CF",
        "bar_color": "#C4161C", "bar_accent": "#8B0000", "bar_radius": "2",
        "grid_color": "rgba(26,26,26,0.1)",
    },
    "02": {
        "name": "02 Swiss/International风格", "group": "流派1·信息建筑派",
        "bg": "#FFFFFF", "card": "#F7F7F7", "fg": "#000000", "muted": "#666666",
        "accent": "#E30613", "accent2": "#E30613", "border": "rgba(0,0,0,0.1)",
        "font_d": "'Helvetica Neue','Noto Sans SC',sans-serif",
        "font_b": "'Helvetica Neue','Noto Sans SC',sans-serif",
        "radius": "0px", "shadow": "none",
        "body_bg": "#E8E8E8",
        "bar_color": "#E30613", "bar_accent": "#A00000", "bar_radius": "0",
        "grid_color": "rgba(0,0,0,0.08)",
    },
    "03": {
        "name": "03 数据叙事派", "group": "流派1·信息建筑派",
        "bg": "#FAFAF5", "card": "#FFFFFF", "fg": "#333333", "muted": "#777777",
        "accent": "#2171B5", "accent2": "#2171B5", "border": "rgba(51,51,51,0.08)",
        "font_d": "'Georgia','Noto Serif SC',serif",
        "font_b": "'Georgia','Noto Serif SC',serif",
        "radius": "2px", "shadow": "0 1px 6px rgba(51,51,51,0.06)",
        "body_bg": "#E8E8E0",
        "bar_color": "#2171B5", "bar_accent": "#08519C", "bar_radius": "2",
        "grid_color": "rgba(51,51,51,0.06)",
    },
    "04": {
        "name": "04 Dieter Rams式功能主义", "group": "流派1·信息建筑派",
        "bg": "#FFFFFF", "card": "#FFFFFF", "fg": "#1A1A1A", "muted": "#888888",
        "accent": "#FF6B00", "accent2": "#FF6B00", "border": "rgba(26,26,26,0.06)",
        "font_d": "'Helvetica Neue','Noto Sans SC',sans-serif",
        "font_b": "'Helvetica Neue','Noto Sans SC',sans-serif",
        "radius": "4px", "shadow": "none",
        "body_bg": "#E0E0E0",
        "bar_color": "#FF6B00", "bar_accent": "#CC5500", "bar_radius": "2",
        "grid_color": "rgba(26,26,26,0.05)",
    },
    "09": {
        "name": "09 Muji式无印良品", "group": "流派3·极简主义派",
        "bg": "#F5F0EB", "card": "#EDE8E1", "fg": "#5C534A", "muted": "#8C8279",
        "accent": "#C8B8A4", "accent2": "#5C534A", "border": "rgba(92,83,74,0.08)",
        "font_d": "'Avenir Next','Noto Sans SC',sans-serif",
        "font_b": "'Avenir Next','Noto Sans SC',sans-serif",
        "radius": "2px", "shadow": "none",
        "body_bg": "#E0DAD2",
        "bar_color": "#C8B8A4", "bar_accent": "#5C534A", "bar_radius": "2",
        "grid_color": "rgba(92,83,74,0.08)",
    },
    "10": {
        "name": "10 Johnston/Markwick极简编辑", "group": "流派3·极简主义派",
        "bg": "#FFFFFF", "card": "#FAFAFA", "fg": "#1A1A1A", "muted": "#8C8C8C",
        "accent": "#8C8C8C", "accent2": "#1A1A1A", "border": "rgba(26,26,26,0.06)",
        "font_d": "'Playfair Display','Noto Serif SC',serif",
        "font_b": "'Georgia','Noto Serif SC',serif",
        "radius": "0px", "shadow": "none",
        "body_bg": "#E0E0E0",
        "bar_color": "#1A1A1A", "bar_accent": "#8C8C8C", "bar_radius": "0",
        "grid_color": "rgba(26,26,26,0.05)",
    },
    "11": {
        "name": "11 Noma Bar负空间叙事", "group": "流派3·极简主义派",
        "bg": "#FFFDF7", "card": "#FFFDF7", "fg": "#1D1D1B", "muted": "#888888",
        "accent": "#E8422F", "accent2": "#1D1D1B", "border": "rgba(29,29,27,0.08)",
        "font_d": "'Futura','Noto Sans SC',sans-serif",
        "font_b": "'Futura','Noto Sans SC',sans-serif",
        "radius": "0px", "shadow": "none",
        "body_bg": "#E8E6D8",
        "bar_color": "#1D1D1B", "bar_accent": "#E8422F", "bar_radius": "0",
        "grid_color": "rgba(29,29,27,0.06)",
    },
    "12": {
        "name": "12 原研哉白派", "group": "流派3·极简主义派",
        "bg": "#F8F6F1", "card": "#F8F6F1", "fg": "#999999", "muted": "#BBBBBB",
        "accent": "#D4D0C8", "accent2": "#999999", "border": "rgba(0,0,0,0.03)",
        "font_d": "'Noto Serif SC',serif",
        "font_b": "'Noto Serif SC',serif",
        "radius": "0px", "shadow": "none",
        "body_bg": "#E8E6DF",
        "bar_color": "#D4D0C8", "bar_accent": "#999999", "bar_radius": "2",
        "grid_color": "rgba(0,0,0,0.02)",
    },
}


for sid, s in styles.items():
    chart = bar_svg(s)
    
    # Cover page
    cover = f'''<section class="s on" style="flex-direction:column;justify-content:center">
      <div style="font-size:52px;font-weight:700;font-family:{s["font_d"]};color:{s["fg"]};line-height:1.15;margin-bottom:24px">过去十年黄金价格</div>
      <div style="width:80px;height:3px;background:{s["accent"]};margin-bottom:24px;border-radius:2px"></div>
      <div style="font-size:20px;font-family:{s["font_b"]};color:{s["muted"]};line-height:1.7">2015–2025 年均价格（美元/盎司）</div>
    </section>'''
    
    # Chart page
    chart_page = f'''<section class="s" style="flex-direction:column">
      <div style="display:flex;align-items:baseline;gap:16px;margin-bottom:8px">
        <div style="font-size:36px;font-weight:700;font-family:{s["font_d"]};color:{s["fg"]}">黄金价格走势</div>
        <div style="font-size:16px;font-family:{s["font_b"]};color:{s["muted"]}">2015–2025 年均价格（美元/盎司）</div>
      </div>
      <div style="flex:1;display:flex;align-items:center;justify-content:center">
        {chart}
      </div>
      <div style="display:flex;gap:24px;font-size:13px;color:{s["muted"]};font-family:{s["font_b"]}">
        <span>数据来源：World Gold Council / LBMA</span>
        <span>2025年为Q1均值估算</span>
      </div>
    </section>'''
    
    # Key insight page
    insight = f'''<section class="s" style="flex-direction:column;justify-content:center">
      <div style="font-size:14px;font-family:{s["font_d"]};color:{s["accent"]};letter-spacing:1.5px;margin-bottom:24px">关键发现</div>
      <div style="font-size:56px;font-weight:700;font-family:{s["font_d"]};color:{s["fg"]};line-height:1.2;margin-bottom:40px">10年涨幅<br/><span style="color:{s["accent"]}">+146%</span></div>
      <div style="font-size:20px;font-family:{s["font_b"]};color:{s["muted"]};line-height:1.8;max-width:600px">
        从2015年的$1,160到2025年的$2,850，黄金价格在过去十年持续攀升。<br/>
        2020年突破$1,700，2024年加速至$2,386。
      </div>
      <div style="width:60px;height:3px;background:{s["accent"]};margin-top:40px;border-radius:2px"></div>
    </section>'''
    
    # Ending page
    ending = f'''<section class="s" style="flex-direction:column;align-items:center;justify-content:center;text-align:center">
      <div style="font-size:64px;font-weight:700;font-family:{s["font_d"]};color:{s["fg"]};line-height:1.15;margin-bottom:32px">STYLE {sid}</div>
      <div style="width:300px;height:3px;border-radius:2px;background:{s["accent"]};margin-bottom:24px"></div>
      <div style="font-size:22px;color:{s["muted"]};font-family:{s["font_b"]};line-height:1.6">{s["name"]}</div>
    </section>'''
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Gold Chart - {s["name"]}</title>
<style>
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:100%;height:100%;overflow:hidden;background:{s["body_bg"]}}}
body{{display:flex;align-items:center;justify-content:center;font-family:{s["font_d"]};color:{s["fg"]}}}
#dw{{width:1920px;height:1080px;position:relative;transform-origin:center center}}
.s{{width:1920px;height:1080px;position:absolute;top:0;left:0;background:{s["bg"]};display:none;overflow:hidden;padding:80px 100px}}
.s.on{{display:flex}}
#pi{{position:fixed;bottom:24px;right:40px;font-family:{s["font_d"]};font-size:16px;color:{s["muted"]};z-index:100;opacity:.7}}
</style>
</head>
<body>
<div id="dw">
{cover}
{chart_page}
{insight}
{ending}
</div>
<div id="pi">1/4</div>
<script>
let cur=0;const slides=document.querySelectorAll('.s');const total=slides.length;
function show(i){{slides.forEach(s=>s.classList.remove('on'));if(slides[i])slides[i].classList.add('on');document.getElementById('pi').textContent=(i+1)+'/'+total}}
document.addEventListener('keydown',e=>{{if(e.key==='ArrowRight'||e.key===' '){{cur=(cur+1)%total;show(cur)}}else if(e.key==='ArrowLeft'){{cur=(cur-1+total)%total;show(cur)}}}});
</script>
</body></html>'''
    
    fname = f"gold_{sid}.html"
    with open(os.path.join(OUT_DIR, fname), 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated: {fname}")

print(f"\nDone! {len(styles)} chart samples in {OUT_DIR}")
