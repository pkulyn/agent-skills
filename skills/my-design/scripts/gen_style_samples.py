#!/usr/bin/env python3
"""Generate 20 design style sample slides (3 pages each: cover, content, ending)."""
import os, json

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'demos', 'style_samples')
os.makedirs(OUT_DIR, exist_ok=True)

TITLE = "如何用好 OpenClaw 的 PPT"
SUBTITLE = "打字，回车，一份能交付的设计"
SLIDE_TITLE = "核心工作流"
STEPS = [("01","选风格，定 Grammar"), ("02","说内容，批量生产"), ("03","交付与迭代")]
STEPS_D = ["描述你的场景，我推荐差异化方向", "大纲、文档、口述要点都行", "HTML预览 + PPTX导出 + 品牌套壳"]
ENDING_TITLE = "开始你的第一份设计"
ENDING_SUB = "打字，回车，交付。"

# Shared styles data - each style has id, name, colors, fonts, etc.
# Styles data defined below after the functions

def make_slide_css(s):
    return f"""
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:100%;height:100%;overflow:hidden;background:{s.get('body_bg', s['bg'])}}}
body{{display:flex;align-items:center;justify-content:center;font-family:{s['font_d']};color:{s['fg']}}}
#dw{{width:1920px;height:1080px;position:relative;transform-origin:center center}}
.s{{width:1920px;height:1080px;position:absolute;top:0;left:0;background:{s['bg']};display:none;overflow:hidden;padding:80px 100px}}
.s.on{{display:flex}}
.c{{background:{s['card']};border:1px solid {s['border']};border-radius:{s['radius']};padding:36px 32px;position:relative;overflow:hidden;box-shadow:{s['shadow']}}}
"""

def gen_cover(s):
    sid = s['id']
    # Different cover layouts per style group
    if sid in ("01","02","03","04"):
        # 信息建筑派: structured, data-driven
        accent_line = f'<div style="width:80px;height:4px;background:{s["accent"]};margin-top:40px;border-radius:2px"></div>' if sid != "04" else f'<div style="width:60px;height:1px;background:{s["accent"]};margin-top:32px"></div>'
        title_size = "120px" if sid == "01" else "56px"
        title_word = "PPT" if sid == "01" else TITLE
        return f'''<section class="s on" style="flex-direction:column;justify-content:center">
      <div style="font-size:{title_size};font-weight:700;font-family:{s["font_d"]};color:{s["fg"]};line-height:1.1;margin-bottom:24px">{title_word}</div>
      <div style="font-size:18px;font-family:{s["font_b"]};color:{s["muted"]};letter-spacing:2px;line-height:1.7">{SUBTITLE if sid != "01" else TITLE}</div>
      {accent_line}
    </section>'''
    elif sid in ("05","06","07","08"):
        # 运动诗学派: immersive, tech
        if sid == "06":  # Apple
            return f'''<section class="s on" style="flex-direction:column;justify-content:center;align-items:center;text-align:center">
      <div style="font-size:96px;font-weight:300;font-family:{s["font_d"]};color:{s["fg"]};line-height:1.1;margin-bottom:32px">{TITLE}</div>
      <div style="font-size:24px;font-weight:300;font-family:{s["font_b"]};color:{s["muted"]};line-height:1.6">{SUBTITLE}</div>
    </section>'''
        elif sid == "07":  # Frog warm tech
            return f'''<section class="s on" style="flex-direction:row;align-items:center">
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding-right:60px">
        <div style="font-size:14px;font-weight:600;color:{s["accent2"]};letter-spacing:2px;margin-bottom:28px;font-family:{s["font_d"]};background:rgba(42,168,158,0.1);padding:6px 16px;border-radius:6px;display:inline-block;width:fit-content">MY DESIGN</div>
        <div style="font-size:64px;font-weight:700;font-family:{s["font_d"]};color:{s["fg"]};line-height:1.15;margin-bottom:28px">{TITLE}</div>
        <div style="font-size:22px;font-family:{s["font_b"]};color:{s["muted"]};line-height:1.7;max-width:500px">{SUBTITLE}</div>
      </div>
      <div style="flex:0 0 400px;height:100%;display:flex;align-items:center;justify-content:center;position:relative">
        <div style="width:280px;height:280px;border-radius:50%;border:3px solid {s["accent2"]};opacity:.3;animation:spin 20s linear infinite"></div>
        <div style="position:absolute;width:180px;height:180px;border-radius:50%;border:3px solid {s["accent"]};opacity:.4;animation:spin 14s linear infinite reverse"></div>
      </div>
    </section>'''
        else:  # 05, 08 - dark glow
            glow1 = f'<div style="position:absolute;top:20%;left:30%;width:300px;height:300px;border-radius:50%;background:radial-gradient(circle,{s["accent"]}22,transparent 70%);filter:blur(40px)"></div>'
            glow2 = f'<div style="position:absolute;bottom:20%;right:25%;width:250px;height:250px;border-radius:50%;background:radial-gradient(circle,{s["accent2"]}22,transparent 70%);filter:blur(40px)"></div>'
            tag = f'<div style="font-size:14px;font-family:{s["font_b"]};color:{s["accent"]};letter-spacing:3px;margin-bottom:24px">// STYLE_{sid}</div>' if sid == "08" else ''
            return f'''<section class="s on" style="flex-direction:column;justify-content:center;align-items:center;text-align:center;position:relative">
      {glow1}{glow2}
      {tag}
      <div style="font-size:72px;font-weight:700;font-family:{s["font_d"]};color:{s["fg"]};margin-bottom:20px;position:relative;z-index:1">{TITLE}</div>
      <div style="font-size:22px;font-family:{s["font_b"]};color:{s["accent"]};position:relative;z-index:1">{SUBTITLE}</div>
    </section>'''
    elif sid in ("09","10","11","12"):
        # 极简主义派: order, whitespace
        if sid == "09":  # Muji
            return f'''<section class="s on" style="flex-direction:column;justify-content:center">
      <div style="font-size:28px;font-weight:300;font-family:{s["font_d"]};color:{s["fg"]};margin-bottom:60px;line-height:2">{TITLE}</div>
      <div style="width:40px;height:1px;background:{s["accent"]};margin-bottom:40px"></div>
      <div style="font-size:16px;font-family:{s["font_b"]};color:{s["muted"]};line-height:2">{SUBTITLE}</div>
    </section>'''
        elif sid == "10":  # Magazine
            return f'''<section class="s on" style="flex-direction:column;justify-content:center">
      <div style="font-size:12px;font-family:{s["font_b"]};color:{s["muted"]};letter-spacing:3px;margin-bottom:24px">2026 春季刊</div>
      <div style="font-size:68px;font-weight:700;font-family:{s["font_d"]};color:{s["fg"]};line-height:1.1;margin-bottom:32px">{TITLE}</div>
      <div style="width:100%;height:0.5px;background:{s["accent"]};margin-bottom:20px"></div>
      <div style="font-size:18px;font-family:{s["font_b"]};color:{s["muted"]};line-height:1.8">{SUBTITLE}</div>
    </section>'''
        elif sid == "11":  # Noma Bar
            return f'''<section class="s on" style="flex-direction:row;align-items:center">
      <div style="flex:0 0 55%;display:flex;flex-direction:column;justify-content:center;padding-right:80px">
        <div style="font-size:56px;font-weight:700;font-family:{s["font_d"]};color:{s["fg"]};line-height:1.15;margin-bottom:28px">{TITLE}</div>
        <div style="font-size:20px;font-family:{s["font_b"]};color:{s["muted"]};line-height:1.7">{SUBTITLE}</div>
      </div>
      <div style="flex:0 0 45%;height:100%;display:flex;align-items:center;justify-content:center;position:relative">
        <div style="width:320px;height:320px;background:{s["fg"]};border-radius:50%"></div>
        <div style="position:absolute;width:200px;height:200px;background:{s["accent"]};border-radius:50%"></div>
      </div>
    </section>'''
        else:  # 12 - White whisper
            return f'''<section class="s on" style="flex-direction:column;justify-content:center">
      <div style="font-size:36px;font-weight:300;font-family:{s["font_d"]};color:{s["fg"]};margin-bottom:80px;letter-spacing:2px">{TITLE}</div>
      <div style="width:30px;height:0.25px;background:{s["accent"]};margin-bottom:60px"></div>
      <div style="font-size:15px;font-family:{s["font_b"]};color:{s["muted"]};line-height:2.2">{SUBTITLE}</div>
    </section>'''
    elif sid in ("13","14","15","16"):
        # 实验先锋派: bold, experimental
        if sid == "13":  # Sagmeister
            return f'''<section class="s on" style="flex-direction:column;justify-content:center;position:relative">
      <div style="font-size:80px;font-weight:900;font-family:{s["font_d"]};color:{s["fg"]};line-height:1;transform:rotate(-3deg);margin-bottom:24px">{TITLE}</div>
      <div style="font-size:22px;font-family:{s["font_b"]};color:{s["accent"]};transform:rotate(1deg)">{SUBTITLE}</div>
    </section>'''
        elif sid == "14":  # Bauhaus
            return f'''<section class="s on" style="flex-direction:row;align-items:center">
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding-right:60px">
        <div style="font-size:52px;font-weight:700;font-family:{s["font_d"]};color:{s["fg"]};line-height:1.15;margin-bottom:24px">{TITLE}</div>
        <div style="font-size:18px;font-family:{s["font_b"]};color:{s["muted"]};line-height:1.7">{SUBTITLE}</div>
      </div>
      <div style="flex:0 0 400px;height:100%;display:flex;align-items:center;justify-content:center;position:relative">
        <div style="width:180px;height:180px;border-radius:50%;background:{s["accent"]};opacity:.85"></div>
        <div style="position:absolute;top:180px;left:200px;width:150px;height:150px;background:{s["accent2"]};opacity:.7"></div>
        <div style="position:absolute;top:300px;left:100px;width:0;height:0;border-left:80px solid transparent;border-right:80px solid transparent;border-bottom:140px solid #F9A825;opacity:.7"></div>
      </div>
    </section>'''
        elif sid == "15":  # Memphis
            return f'''<section class="s on" style="flex-direction:column;justify-content:center;position:relative;overflow:hidden">
      <div style="position:absolute;top:-40px;right:-40px;width:200px;height:200px;border-radius:50%;background:{s["accent"]};opacity:.3;border:3px solid #000"></div>
      <div style="position:absolute;bottom:60px;left:60px;width:120px;height:120px;background:#FFD600;opacity:.3;border:3px solid #000;transform:rotate(15deg)"></div>
      <div style="font-size:64px;font-weight:900;font-family:{s["font_d"]};color:{s["fg"]};position:relative;z-index:1;margin-bottom:20px">{TITLE}</div>
      <div style="font-size:22px;font-family:{s["font_b"]};color:{s["accent"]};position:relative;z-index:1">{SUBTITLE}</div>
    </section>'''
        else:  # 16 - Generative
            circles = ''.join(f'<circle cx="{200+i*160}" cy="{540+int(200*((i%5)/5-0.5))}" r="{20+i*3}" fill="none" stroke="{s["accent"]}" stroke-width="1" opacity="{0.3+i*0.05}"/>' for i in range(10))
            return f'''<section class="s on" style="flex-direction:column;justify-content:center;position:relative">
      <svg style="position:absolute;top:0;left:0;width:100%;height:100%;opacity:.15" viewBox="0 0 1920 1080">{circles}</svg>
      <div style="font-size:14px;font-family:{s["font_b"]};color:{s["accent"]};letter-spacing:3px;margin-bottom:20px;position:relative">// generate(style_16)</div>
      <div style="font-size:68px;font-weight:700;font-family:{s["font_d"]};color:{s["fg"]};margin-bottom:16px;position:relative">{TITLE}</div>
      <div style="font-size:20px;font-family:{s["font_b"]};color:{s["muted"]};position:relative">{SUBTITLE}</div>
    </section>'''
    else:
        # 东方哲学派: poetic, zen
        if sid == "17":  # Hara void
            return f'''<section class="s on" style="flex-direction:column;justify-content:center">
      <div style="font-size:40px;font-weight:400;font-family:{s["font_d"]};color:{s["fg"]};margin-bottom:120px;letter-spacing:4px">{TITLE}</div>
      <div style="font-size:15px;font-family:{s["font_b"]};color:{s["muted"]};line-height:2.5;max-width:400px">{SUBTITLE}</div>
    </section>'''
        elif sid == "18":  # Mandala
            return f'''<section class="s on" style="flex-direction:column;justify-content:center;align-items:center;text-align:center;position:relative">
      <div style="position:absolute;width:500px;height:500px;border-radius:50%;border:2px solid {s["accent"]};opacity:.2"></div>
      <div style="position:absolute;width:350px;height:350px;border-radius:50%;border:1px solid {s["accent2"]};opacity:.15"></div>
      <div style="position:absolute;width:200px;height:200px;border-radius:50%;border:2px solid {s["accent"]};opacity:.25"></div>
      <div style="font-size:60px;font-weight:700;font-family:{s["font_d"]};color:{s["fg"]};margin-bottom:20px;position:relative;z-index:1">{TITLE}</div>
      <div style="font-size:20px;font-family:{s["font_b"]};color:{s["accent"]};position:relative;z-index:1">{SUBTITLE}</div>
    </section>'''
        elif sid == "19":  # Receipt
            return f'''<section class="s on" style="flex-direction:column;justify-content:center">
      <div style="font-size:12px;font-family:{s["font_b"]};color:{s["muted"]};margin-bottom:12px;border-bottom:1px dashed {s["accent"]};padding-bottom:8px">收据 No.20260428</div>
      <div style="font-size:36px;font-weight:700;font-family:{s["font_d"]};color:{s["fg"]};margin-bottom:16px">{TITLE}</div>
      <div style="font-size:15px;font-family:{s["font_b"]};color:{s["muted"]};line-height:1.8;border-bottom:1px dashed {s["accent"]};padding-bottom:16px">{SUBTITLE}</div>
    </section>'''
        else:  # 20 - Scholar
            return f'''<section class="s on" style="flex-direction:column;justify-content:center;position:relative">
      <div style="font-size:48px;font-weight:400;font-family:{s["font_d"]};color:{s["fg"]};line-height:1.5;margin-bottom:32px;letter-spacing:4px">{TITLE}</div>
      <div style="font-size:18px;font-family:{s["font_b"]};color:{s["muted"]};line-height:2">{SUBTITLE}</div>
      <div style="position:absolute;bottom:80px;right:100px;width:56px;height:56px;border:3px solid {s["accent"]};display:flex;align-items:center;justify-content:center;font-family:{s["font_d"]};color:{s["accent"]};font-size:18px;font-weight:700">印</div>
    </section>'''


def gen_content(s):
    sid = s['id']
    cards = ""
    for i, (num, step) in enumerate(STEPS):
        delay = f"{0.2 + i*0.15:.2f}s"
        accent_bar = f'<div style="position:absolute;top:0;left:0;right:0;height:3px;background:{s["accent"]}"></div>'
        cards += f'''
        <div class="c" style="flex:1;display:flex;flex-direction:column">
          {accent_bar}
          <div style="font-size:32px;margin-bottom:16px;color:{s["accent"]}">◈</div>
          <div style="font-size:22px;font-weight:700;font-family:{s["font_d"]};color:{s["fg"]};margin-bottom:12px">{step}</div>
          <div style="font-size:16px;color:{s["muted"]};line-height:1.6;font-family:{s["font_b"]}">{STEPS_D[i]}</div>
          <div style="position:absolute;bottom:8px;right:16px;font-size:72px;font-weight:700;opacity:.04;color:{s["fg"]};font-family:{s["font_d"]}">{num}</div>
        </div>'''
    
    return f'''<section class="s" style="flex-direction:column">
      <div style="display:inline-block;font-size:14px;font-weight:600;color:{s["accent"]};letter-spacing:1.5px;margin-bottom:16px;text-transform:uppercase">{s["group"]}</div>
      <div style="font-size:46px;font-weight:700;font-family:{s["font_d"]};color:{s["fg"]};line-height:1.15">{SLIDE_TITLE}</div>
      <div style="display:flex;gap:28px;flex:1;margin-top:48px;align-items:stretch">
        {cards}
      </div>
    </section>'''


def gen_ending(s):
    sid = s['id']
    line = f'<div style="width:300px;height:3px;border-radius:2px;background:{s["accent"]};margin-bottom:24px"></div>'
    return f'''<section class="s" style="flex-direction:column;align-items:center;justify-content:center;text-align:center;position:relative">
      <div style="font-size:82px;font-weight:700;font-family:{s["font_d"]};color:{s["fg"]};line-height:1.15;margin-bottom:32px">{ENDING_TITLE}</div>
      <div style="font-size:24px;color:{s["muted"]};font-family:{s["font_b"]};line-height:1.6;max-width:600px;margin-bottom:60px">{ENDING_SUB}</div>
      {line}
      <div style="font-size:15px;color:{s["muted"]};font-family:{s["font_d"]};letter-spacing:2px">STYLE {s["id"]} · {s["name"]}</div>
    </section>'''


def gen_html(s):
    cover = gen_cover(s)
    content = gen_content(s)
    ending = gen_ending(s)
    nav_js = """
<script>
let cur=0;const slides=document.querySelectorAll('.s');const total=slides.length;
function show(i){slides.forEach(s=>s.classList.remove('on'));if(slides[i])slides[i].classList.add('on');document.getElementById('pi').textContent=(i+1)+'/'+total}
document.addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key===' '){cur=(cur+1)%total;show(cur)}else if(e.key==='ArrowLeft'){cur=(cur-1+total)%total;show(cur)}});
</script>"""
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Style {s["id"]} - {s["name"]}</title>
<style>{make_slide_css(s)}</style>
</head>
<body>
<div id="dw">
{cover}
{content}
{ending}
</div>
<div id="pi">1/3</div>
{nav_js}
</body></html>'''


# Generate styles data
styles_data = [
    {"id":"01","name":"Pentagram式信息建筑","group":"信息建筑派","bg":"#E8E4DF","card":"#FFFFFF","fg":"#1A1A1A","muted":"#6B6B6B","accent":"#C4161C","accent2":"#C4161C","border":"rgba(26,26,26,0.08)","font_d":"'Helvetica Neue','Noto Sans SC',sans-serif","font_b":"'Georgia','Noto Serif SC',serif","radius":"2px","shadow":"0 1px 8px rgba(26,26,26,0.08)","body_bg":"#D8D4CF"},
    {"id":"02","name":"Swiss/International风格","group":"信息建筑派","bg":"#FFFFFF","card":"#F7F7F7","fg":"#000000","muted":"#666666","accent":"#E30613","accent2":"#E30613","border":"rgba(0,0,0,0.1)","font_d":"'Helvetica Neue','Noto Sans SC',sans-serif","font_b":"'Helvetica Neue','Noto Sans SC',sans-serif","radius":"0px","shadow":"none","body_bg":"#E8E8E8"},
    {"id":"03","name":"数据叙事派","group":"信息建筑派","bg":"#FAFAF5","card":"#FFFFFF","fg":"#333333","muted":"#777777","accent":"#2171B5","accent2":"#2171B5","border":"rgba(51,51,51,0.08)","font_d":"'Georgia','Noto Serif SC',serif","font_b":"'Georgia','Noto Serif SC',serif","radius":"2px","shadow":"0 1px 6px rgba(51,51,51,0.06)","body_bg":"#E8E8E0"},
    {"id":"04","name":"Dieter Rams式功能主义","group":"信息建筑派","bg":"#FFFFFF","card":"#FFFFFF","fg":"#1A1A1A","muted":"#888888","accent":"#FF6B00","accent2":"#FF6B00","border":"rgba(26,26,26,0.06)","font_d":"'Helvetica Neue','Noto Sans SC',sans-serif","font_b":"'Helvetica Neue','Noto Sans SC',sans-serif","radius":"4px","shadow":"none","body_bg":"#E0E0E0"},
    {"id":"05","name":"Field.io运动美学","group":"运动诗学派","bg":"#0A0A0F","card":"#14141F","fg":"#F0F0F5","muted":"#8888AA","accent":"#00FFC8","accent2":"#FF3366","border":"rgba(0,255,200,0.1)","font_d":"'Space Grotesk','Noto Sans SC',sans-serif","font_b":"'Inter','Noto Sans SC',sans-serif","radius":"8px","shadow":"0 0 20px rgba(0,255,200,0.08)","body_bg":"#050508"},
    {"id":"06","name":"Apple发布会极简叙事","group":"运动诗学派","bg":"#000000","card":"#0A0A0A","fg":"#F5F5F7","muted":"#86868B","accent":"#0071E3","accent2":"#0071E3","border":"rgba(245,245,247,0.08)","font_d":"'SF Pro Display','PingFang SC',sans-serif","font_b":"'SF Pro Text','PingFang SC',sans-serif","radius":"12px","shadow":"none","body_bg":"#000000"},
    {"id":"07","name":"Frog Design技术人文","group":"运动诗学派","bg":"#F7F5F2","card":"#FFFFFF","fg":"#1B2838","muted":"#4A5B6E","accent":"#FF6B35","accent2":"#2AA89E","border":"rgba(27,40,56,0.08)","font_d":"'DM Sans','Noto Sans SC',sans-serif","font_b":"'Noto Serif SC',serif","radius":"12px","shadow":"0 2px 12px rgba(27,40,56,0.06)","body_bg":"#E8E4DF"},
    {"id":"08","name":"Wired式数据未来主义","group":"运动诗学派","bg":"#0D0221","card":"#150633","fg":"#E0E0F0","muted":"#7777AA","accent":"#00F0FF","accent2":"#FF00FF","border":"rgba(0,240,255,0.12)","font_d":"'Space Mono','Noto Sans SC',monospace","font_b":"'Roboto Mono','Noto Sans SC',monospace","radius":"4px","shadow":"0 0 15px rgba(0,240,255,0.1)","body_bg":"#060114"},
    {"id":"09","name":"Muji式无印良品","group":"极简主义派","bg":"#F5F0EB","card":"#EDE8E1","fg":"#5C534A","muted":"#8C8279","accent":"#C8B8A4","accent2":"#C8B8A4","border":"rgba(92,83,74,0.08)","font_d":"'Avenir Next','Noto Sans SC',sans-serif","font_b":"'Avenir Next','Noto Sans SC',sans-serif","radius":"2px","shadow":"none","body_bg":"#E0DAD2"},
    {"id":"10","name":"Johnston/Markwick极简编辑","group":"极简主义派","bg":"#FFFFFF","card":"#FAFAFA","fg":"#1A1A1A","muted":"#8C8C8C","accent":"#8C8C8C","accent2":"#1A1A1A","border":"rgba(26,26,26,0.06)","font_d":"'Playfair Display','Noto Serif SC',serif","font_b":"'Georgia','Noto Serif SC',serif","radius":"0px","shadow":"none","body_bg":"#E0E0E0"},
    {"id":"11","name":"Noma Bar负空间叙事","group":"极简主义派","bg":"#FFFDF7","card":"#FFFDF7","fg":"#1D1D1B","muted":"#888888","accent":"#E8422F","accent2":"#1D1D1B","border":"rgba(29,29,27,0.08)","font_d":"'Futura','Noto Sans SC',sans-serif","font_b":"'Futura','Noto Sans SC',sans-serif","radius":"0px","shadow":"none","body_bg":"#E8E6D8"},
    {"id":"12","name":"原研哉白派","group":"极简主义派","bg":"#F8F6F1","card":"#F8F6F1","fg":"#999999","muted":"#BBBBBB","accent":"#D4D0C8","accent2":"#CCCCCC","border":"rgba(0,0,0,0.03)","font_d":"'Noto Serif SC',serif","font_b":"'Noto Serif SC',serif","radius":"0px","shadow":"none","body_bg":"#E8E6DF"},
    {"id":"13","name":"Sagmeister实验先锋","group":"实验先锋派","bg":"#FFEA00","card":"#FFFFFF","fg":"#000000","muted":"#333333","accent":"#FF2D00","accent2":"#000000","border":"rgba(0,0,0,0.15)","font_d":"'Impact','Noto Sans SC',sans-serif","font_b":"'Helvetica Neue','Noto Sans SC',sans-serif","radius":"0px","shadow":"3px 3px 0 #000","body_bg":"#CCBA00"},
    {"id":"14","name":"Bauhaus新构成","group":"实验先锋派","bg":"#F4F4F4","card":"#FFFFFF","fg":"#1A1A1A","muted":"#666666","accent":"#DD0100","accent2":"#0D47A1","border":"rgba(0,0,0,0.1)","font_d":"'ITC Bauhaus','Noto Sans SC',sans-serif","font_b":"'Helvetica Neue','Noto Sans SC',sans-serif","radius":"0px","shadow":"none","body_bg":"#D4D4D4"},
    {"id":"15","name":"Memphis后现代","group":"实验先锋派","bg":"#FFF8E1","card":"#FFFFFF","fg":"#1A1A1A","muted":"#555555","accent":"#FF6B9D","accent2":"#00C853","border":"3px solid #000","font_d":"'Cooper Black','Noto Sans SC',sans-serif","font_b":"'Avenir','Noto Sans SC',sans-serif","radius":"16px","shadow":"4px 4px 0 #000","body_bg":"#E8D8A0"},
    {"id":"16","name":"Generative Art生成美学","group":"实验先锋派","bg":"#0B0B0F","card":"#141420","fg":"#E0E0F0","muted":"#6666AA","accent":"#6C63FF","accent2":"#00E5FF","border":"rgba(108,99,255,0.15)","font_d":"'JetBrains Mono','Noto Sans SC',monospace","font_b":"'Space Mono','Noto Sans SC',monospace","radius":"6px","shadow":"0 0 20px rgba(108,99,255,0.12)","body_bg":"#060608"},
    {"id":"17","name":"Kenya Hara东方极简","group":"东方哲学派","bg":"#F7F5F0","card":"#F7F5F0","fg":"#4A4A4A","muted":"#8A8A8A","accent":"#B8A99A","accent2":"#B8A99A","border":"rgba(74,74,74,0.06)","font_d":"'Noto Serif SC',serif","font_b":"'Noto Serif SC',serif","radius":"2px","shadow":"none","body_bg":"#E4E0D8"},
    {"id":"18","name":"杉浦康平亚洲图腾","group":"东方哲学派","bg":"#1A0A2E","card":"#220E40","fg":"#F0E8D8","muted":"#9988AA","accent":"#FF6B35","accent2":"#FFD700","border":"rgba(255,107,53,0.15)","font_d":"'Noto Serif SC',serif","font_b":"'Noto Serif SC',serif","radius":"4px","shadow":"0 0 20px rgba(255,107,53,0.08)","body_bg":"#0E0520"},
    {"id":"19","name":"朱锷日常设计","group":"东方哲学派","bg":"#F5F2ED","card":"#EFEBE4","fg":"#2D2D2D","muted":"#8B7E6A","accent":"#8B7E6A","accent2":"#2D2D2D","border":"rgba(45,45,45,0.08)","font_d":"'Helvetica Neue','Noto Sans SC',sans-serif","font_b":"'Courier New','Noto Sans SC',monospace","radius":"0px","shadow":"none","body_bg":"#E0DCD4"},
    {"id":"20","name":"王澍文人建筑","group":"东方哲学派","bg":"#E8DCC8","card":"#E2D5BF","fg":"#3D2B1F","muted":"#6B5D4F","accent":"#8B4513","accent2":"#8B4513","border":"rgba(61,43,31,0.1)","font_d":"'FangSong','KaiTi',serif","font_b":"'KaiTi',serif","radius":"0px","shadow":"none","body_bg":"#C8B898"},
]

# Save styles data for reference
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'styles_data.json'), 'w') as f:
    json.dump(styles_data, f, ensure_ascii=False, indent=2)

# Generate all HTML files
for s in styles_data:
    html = gen_html(s)
    fname = f"style_{s['id'].zfill(2)}_{s['name'].replace('/','_')}.html"
    outpath = os.path.join(OUT_DIR, fname)
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated: {fname}")

print(f"\nDone! {len(styles_data)} style samples generated in {OUT_DIR}")
