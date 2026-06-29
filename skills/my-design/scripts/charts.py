#!/usr/bin/env python3
"""charts: 风格化图表生成器。输入 data + style_id → 输出 SVG。

支持的图表类型：
  chart_bar       柱状图
  chart_line      折线图
  chart_pie       饼图
  chart_doughnut  环形图
  chart_scatter   散点图
  chart_bubble    气泡图
  chart_radar     雷达图
  chart_spark     sparkline（嵌入式小图）
"""
import math

# ── 风格图表配置 ──

CHART_STYLES = {
    "03": {
        "bar_fill": "#2171B5", "bar_highlight": "#08519C", "bar_radius": 2,
        "line_stroke": "#2171B5", "line_width": 3, "line_dot": True, "line_area": True,
        "grid": True, "grid_dash": "4,4", "grid_color": "rgba(51,51,51,0.06)",
        "axis_color": "#777777", "label_color": "#333333",
        "annotation": True, "sparkline": True,
        # 饼图/环形图
        "pie_colors": ["#2171B5","#4292C6","#6BAED6","#9ECAE1","#C6DBEF","#DEEBF7"],
        "donut_width": 0.35,
        # 散点/气泡
        "scatter_fill": "#2171B5", "scatter_size": 5,
        "bubble_fill": "rgba(33,113,181,0.5)", "bubble_stroke": "#2171B5",
        # 雷达
        "radar_fill": "rgba(33,113,181,0.15)", "radar_stroke": "#2171B5",
    },
    "04": {
        "bar_fill": "#FF6B00", "bar_highlight": "#CC5500", "bar_radius": 2,
        "line_stroke": "#FF6B00", "line_width": 2, "line_dot": False, "line_area": False,
        "grid": False, "grid_dash": "", "grid_color": "transparent",
        "axis_color": "#888888", "label_color": "#1A1A1A",
        "annotation": False, "sparkline": False,
        "pie_colors": ["#FF6B00","#FF8C33","#FFa966","#FFC699","#FFE0CC","#FFF2E6"],
        "donut_width": 0.3,
        "scatter_fill": "#FF6B00", "scatter_size": 5,
        "bubble_fill": "rgba(255,107,0,0.4)", "bubble_stroke": "#FF6B00",
        "radar_fill": "rgba(255,107,0,0.12)", "radar_stroke": "#FF6B00",
    },
    "default": {
        "bar_fill": "#2171B5", "bar_highlight": "#08519C", "bar_radius": 2,
        "line_stroke": "#2171B5", "line_width": 2, "line_dot": True, "line_area": False,
        "grid": True, "grid_dash": "4,4", "grid_color": "rgba(0,0,0,0.06)",
        "axis_color": "#888888", "label_color": "#333333",
        "annotation": False, "sparkline": False,
        "pie_colors": ["#4E79A7","#F28E2B","#E15759","#76B7B2","#59A14F","#EDC948"],
        "donut_width": 0.35,
        "scatter_fill": "#4E79A7", "scatter_size": 5,
        "bubble_fill": "rgba(78,121,167,0.4)", "bubble_stroke": "#4E79A7",
        "radar_fill": "rgba(78,121,167,0.15)", "radar_stroke": "#4E79A7",
    },
}


def _cs(style_id):
    return CHART_STYLES.get(style_id, CHART_STYLES["default"])

def _nice_range(values, step=500):
    lo = min(values); hi = max(values)
    lo = (lo // step) * step; hi = ((hi + step - 1) // step) * step
    return lo, hi

def _wrap(inner, w, h):
    return f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:100%">\n{inner}\n</svg>'


# ── 柱状图 ──

def chart_bar(data, style_id="default", w=1520, h=680, pad_l=70, pad_b=40, pad_t=20, pad_r=20):
    cs = _cs(style_id)
    labels, values, unit = data["labels"], data["values"], data.get("unit", "")
    n = len(values); gap = max(12, 24 - n)
    cw = w - pad_l - pad_r; ch = h - pad_b - pad_t
    bw = (cw - (n - 1) * gap) / n
    y_lo, y_hi = _nice_range(values); yr = max(y_hi - y_lo, 1)
    p = []
    if cs["grid"]:
        for v in range(y_lo, y_hi + 1, 500):
            y = pad_t + ch - (v - y_lo) / yr * ch
            p.append(f'<line x1="{pad_l}" y1="{y:.0f}" x2="{w-pad_r}" y2="{y:.0f}" stroke="{cs["grid_color"]}" stroke-width="0.5" stroke-dasharray="{cs["grid_dash"]}"/>')
            p.append(f'<text x="{pad_l-8}" y="{y+4:.0f}" text-anchor="end" fill="{cs["axis_color"]}" font-size="12">{unit}{v}</text>')
    mx = max(values)
    for i, (label, val) in enumerate(zip(labels, values)):
        x = pad_l + i * (bw + gap); bh = (val - y_lo) / yr * ch
        y = pad_t + ch - bh; fill = cs["bar_highlight"] if val == mx else cs["bar_fill"]
        p.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw:.0f}" height="{bh:.0f}" fill="{fill}" rx="{cs["bar_radius"]}"/>')
        if cs["annotation"] or val == mx:
            p.append(f'<text x="{x+bw/2:.0f}" y="{y-6:.0f}" text-anchor="middle" fill="{cs["label_color"]}" font-size="12" font-weight="600">{unit}{val}</text>')
        p.append(f'<text x="{x+bw/2:.0f}" y="{h-pad_b+18:.0f}" text-anchor="middle" fill="{cs["axis_color"]}" font-size="12">{label}</text>')
    if style_id == "03" and n > 1:
        pts = " ".join(f'{pad_l+i*(bw+gap)+bw/2:.0f},{pad_t+ch-(val-y_lo)/yr*ch:.0f}' for i, val in enumerate(values))
        p.append(f'<polyline points="{pts}" fill="none" stroke="{cs["line_stroke"]}" stroke-width="2" stroke-dasharray="6,3" opacity="0.6"/>')
    return _wrap("\n".join(p), w, h)


# ── 折线图 ──

def chart_line(data, style_id="default", w=1520, h=680, pad_l=70, pad_b=40, pad_t=20, pad_r=20):
    cs = _cs(style_id)
    labels, values, unit = data["labels"], data["values"], data.get("unit", "")
    n = len(values)
    cw = w - pad_l - pad_r; ch = h - pad_b - pad_t; sx = cw / max(n - 1, 1)
    y_lo, y_hi = _nice_range(values); yr = max(y_hi - y_lo, 1)
    p = []
    if cs["grid"]:
        for v in range(y_lo, y_hi + 1, 500):
            y = pad_t + ch - (v - y_lo) / yr * ch
            p.append(f'<line x1="{pad_l}" y1="{y:.0f}" x2="{w-pad_r}" y2="{y:.0f}" stroke="{cs["grid_color"]}" stroke-width="0.5" stroke-dasharray="{cs["grid_dash"]}"/>')
            p.append(f'<text x="{pad_l-8}" y="{y+4:.0f}" text-anchor="end" fill="{cs["axis_color"]}" font-size="12">{unit}{v}</text>')
    pts_list = [(pad_l + i * sx, pad_t + ch - (v - y_lo) / yr * ch) for i, v in enumerate(values)]
    if cs["line_area"] and len(pts_list) > 1:
        area = f"M{pts_list[0][0]:.0f},{pad_t+ch:.0f}" + "".join(f" L{x:.0f},{y:.0f}" for x, y in pts_list) + f" L{pts_list[-1][0]:.0f},{pad_t+ch:.0f} Z"
        p.append(f'<path d="{area}" fill="{cs["line_stroke"]}" opacity="0.08"/>')
    poly = " ".join(f"{x:.0f},{y:.0f}" for x, y in pts_list)
    p.append(f'<polyline points="{poly}" fill="none" stroke="{cs["line_stroke"]}" stroke-width="{cs["line_width"]}" stroke-linejoin="round"/>')
    for i, (x, y) in enumerate(pts_list):
        if cs["line_dot"]:
            p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="4" fill="{cs["line_stroke"]}"/>')
        p.append(f'<text x="{x:.0f}" y="{h-pad_b+18:.0f}" text-anchor="middle" fill="{cs["axis_color"]}" font-size="12">{labels[i]}</text>')
    return _wrap("\n".join(p), w, h)


# ── 饼图 ──

def chart_pie(data, style_id="default", w=600, h=600, cx=None, cy=None, r=None):
    cs = _cs(style_id)
    labels, values = data["labels"], data["values"]
    total = sum(values)
    cx = cx or w // 2; cy = cy or h // 2; r = r or min(w, h) // 2 - 40
    p = []
    angle = -90  # start from top
    for i, (label, val) in enumerate(zip(labels, values)):
        sweep = val / total * 360
        x1 = cx + r * math.cos(math.radians(angle))
        y1 = cy + r * math.sin(math.radians(angle))
        x2 = cx + r * math.cos(math.radians(angle + sweep))
        y2 = cy + r * math.sin(math.radians(angle + sweep))
        large = 1 if sweep > 180 else 0
        fill = cs["pie_colors"][i % len(cs["pie_colors"])]
        p.append(f'<path d="M{cx},{cy} L{x1:.1f},{y1:.1f} A{r},{r} 0 {large},1 {x2:.1f},{y2:.1f} Z" fill="{fill}"/>')
        # Label
        mid = angle + sweep / 2
        lx = cx + (r * 0.65) * math.cos(math.radians(mid))
        ly = cy + (r * 0.65) * math.sin(math.radians(mid))
        pct = val / total * 100
        p.append(f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle" dominant-baseline="central" fill="#fff" font-size="13" font-weight="600">{pct:.0f}%</text>')
        # External label
        elx = cx + (r + 24) * math.cos(math.radians(mid))
        ely = cy + (r + 24) * math.sin(math.radians(mid))
        p.append(f'<text x="{elx:.0f}" y="{ely:.0f}" text-anchor="middle" fill="{cs["axis_color"]}" font-size="12">{label}</text>')
        angle += sweep
    return _wrap("\n".join(p), w, h)


# ── 环形图 ──

def chart_doughnut(data, style_id="default", w=600, h=600, cx=None, cy=None, r=None):
    cs = _cs(style_id)
    labels, values = data["labels"], data["values"]
    total = sum(values)
    cx = cx or w // 2; cy = cy or h // 2; r = r or min(w, h) // 2 - 40
    ir = r * cs["donut_width"]  # inner radius
    p = []
    angle = -90
    for i, (label, val) in enumerate(zip(labels, values)):
        sweep = val / total * 360
        # Outer arc
        ox1 = cx + r * math.cos(math.radians(angle))
        oy1 = cy + r * math.sin(math.radians(angle))
        ox2 = cx + r * math.cos(math.radians(angle + sweep))
        oy2 = cy + r * math.sin(math.radians(angle + sweep))
        # Inner arc
        ix1 = cx + ir * math.cos(math.radians(angle + sweep))
        iy1 = cy + ir * math.sin(math.radians(angle + sweep))
        ix2 = cx + ir * math.cos(math.radians(angle))
        iy2 = cy + ir * math.sin(math.radians(angle))
        large = 1 if sweep > 180 else 0
        fill = cs["pie_colors"][i % len(cs["pie_colors"])]
        d = f"M{ox1:.1f},{oy1:.1f} A{r},{r} 0 {large},1 {ox2:.1f},{oy2:.1f} L{ix1:.1f},{iy1:.1f} A{ir},{ir} 0 {large},0 {ix2:.1f},{iy2:.1f} Z"
        p.append(f'<path d="{d}" fill="{fill}"/>')
        # Label
        mid = angle + sweep / 2
        lr = (r + ir) / 2
        lx = cx + lr * math.cos(math.radians(mid))
        ly = cy + lr * math.sin(math.radians(mid))
        pct = val / total * 100
        if pct > 5:
            p.append(f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle" dominant-baseline="central" fill="#fff" font-size="13" font-weight="600">{pct:.0f}%</text>')
        elx = cx + (r + 24) * math.cos(math.radians(mid))
        ely = cy + (r + 24) * math.sin(math.radians(mid))
        p.append(f'<text x="{elx:.0f}" y="{ely:.0f}" text-anchor="middle" fill="{cs["axis_color"]}" font-size="12">{label}</text>')
        angle += sweep
    # Center text
    p.append(f'<text x="{cx}" y="{cy-8}" text-anchor="middle" fill="{cs["label_color"]}" font-size="28" font-weight="700">{total}</text>')
    p.append(f'<text x="{cx}" y="{cy+16}" text-anchor="middle" fill="{cs["axis_color"]}" font-size="13">总计</text>')
    return _wrap("\n".join(p), w, h)


# ── 散点图 ──

def chart_scatter(data, style_id="default", w=1520, h=680, pad_l=70, pad_b=40, pad_t=20, pad_r=20):
    cs = _cs(style_id)
    # data: {"points": [[x1,y1],[x2,y2],...], "x_label":"", "y_label":"", "x_unit":"", "y_unit":""}
    points = data["points"]
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    cw = w - pad_l - pad_r; ch = h - pad_b - pad_t
    x_lo, x_hi = min(xs), max(xs); xr = max(x_hi - x_lo, 1)
    y_lo, y_hi = _nice_range(ys, 200); yr = max(y_hi - y_lo, 1)
    p = []
    if cs["grid"]:
        for v in range(y_lo, y_hi + 1, 200):
            y = pad_t + ch - (v - y_lo) / yr * ch
            p.append(f'<line x1="{pad_l}" y1="{y:.0f}" x2="{w-pad_r}" y2="{y:.0f}" stroke="{cs["grid_color"]}" stroke-width="0.5" stroke-dasharray="{cs["grid_dash"]}"/>')
            p.append(f'<text x="{pad_l-8}" y="{y+4:.0f}" text-anchor="end" fill="{cs["axis_color"]}" font-size="12">{data.get("y_unit","")}{v}</text>')
    for pt in points:
        sx = pad_l + (pt[0] - x_lo) / xr * cw
        sy = pad_t + ch - (pt[1] - y_lo) / yr * ch
        p.append(f'<circle cx="{sx:.0f}" cy="{sy:.0f}" r="{cs["scatter_size"]}" fill="{cs["scatter_fill"]}" opacity="0.7"/>')
    # Axis labels
    p.append(f'<text x="{w/2:.0f}" y="{h-4:.0f}" text-anchor="middle" fill="{cs["axis_color"]}" font-size="13">{data.get("x_label","")}</text>')
    p.append(f'<text x="14" y="{h/2:.0f}" text-anchor="middle" fill="{cs["axis_color"]}" font-size="13" transform="rotate(-90,14,{h/2})">{data.get("y_label","")}</text>')
    return _wrap("\n".join(p), w, h)


# ── 气泡图 ──

def chart_bubble(data, style_id="default", w=1520, h=680, pad_l=70, pad_b=40, pad_t=20, pad_r=20):
    cs = _cs(style_id)
    # data: {"bubbles": [[x,y,r,label],...], "x_label":"", "y_label":""}
    bubbles = data["bubbles"]
    xs = [b[0] for b in bubbles]; ys = [b[1] for b in bubbles]; rs = [b[2] for b in bubbles]
    cw = w - pad_l - pad_r; ch = h - pad_b - pad_t
    x_lo, x_hi = min(xs), max(xs); xr = max(x_hi - x_lo, 1)
    y_lo, y_hi = _nice_range(ys, 200); yr = max(y_hi - y_lo, 1)
    r_max = max(rs); r_scale = min(cw, ch) * 0.08  # max bubble radius in pixels
    p = []
    if cs["grid"]:
        for v in range(y_lo, y_hi + 1, 200):
            y = pad_t + ch - (v - y_lo) / yr * ch
            p.append(f'<line x1="{pad_l}" y1="{y:.0f}" x2="{w-pad_r}" y2="{y:.0f}" stroke="{cs["grid_color"]}" stroke-width="0.5" stroke-dasharray="{cs["grid_dash"]}"/>')
            p.append(f'<text x="{pad_l-8}" y="{y+4:.0f}" text-anchor="end" fill="{cs["axis_color"]}" font-size="12">{v}</text>')
    for b in bubbles:
        sx = pad_l + (b[0] - x_lo) / xr * cw
        sy = pad_t + ch - (b[1] - y_lo) / yr * ch
        br = max(b[2] / r_max * r_scale, 8)
        p.append(f'<circle cx="{sx:.0f}" cy="{sy:.0f}" r="{br:.0f}" fill="{cs["bubble_fill"]}" stroke="{cs["bubble_stroke"]}" stroke-width="1.5"/>')
        if len(b) > 3:
            p.append(f'<text x="{sx:.0f}" y="{sy+4:.0f}" text-anchor="middle" fill="{cs["label_color"]}" font-size="11">{b[3]}</text>')
    p.append(f'<text x="{w/2:.0f}" y="{h-4:.0f}" text-anchor="middle" fill="{cs["axis_color"]}" font-size="13">{data.get("x_label","")}</text>')
    return _wrap("\n".join(p), w, h)


# ── 雷达图 ──

def chart_radar(data, style_id="default", w=600, h=600, cx=None, cy=None, r=None):
    cs = _cs(style_id)
    # data: {"labels":["A","B",...], "values":[0.8,0.6,...], "max":1.0}
    labels = data["labels"]; values = data["values"]
    mx = data.get("max", max(values) * 1.2)
    n = len(labels)
    cx = cx or w // 2; cy = cy or h // 2; r = r or min(w, h) // 2 - 60
    angle_step = 360 / n
    p = []
    # Grid rings
    for ring in [0.25, 0.5, 0.75, 1.0]:
        pts = []
        for i in range(n):
            a = math.radians(-90 + i * angle_step)
            pts.append(f"{cx + r * ring * math.cos(a):.0f},{cy + r * ring * math.sin(a):.0f}")
        p.append(f'<polygon points="{" ".join(pts)}" fill="none" stroke="{cs["grid_color"] if cs["grid"] else "rgba(0,0,0,0.06)"}" stroke-width="0.5"/>')
    # Axes + labels
    for i in range(n):
        a = math.radians(-90 + i * angle_step)
        ex = cx + r * math.cos(a); ey = cy + r * math.sin(a)
        p.append(f'<line x1="{cx}" y1="{cy}" x2="{ex:.0f}" y2="{ey:.0f}" stroke="{cs["grid_color"] if cs["grid"] else "rgba(0,0,0,0.06)"}" stroke-width="0.5"/>')
        lx = cx + (r + 20) * math.cos(a); ly = cy + (r + 20) * math.sin(a)
        p.append(f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle" dominant-baseline="central" fill="{cs["axis_color"]}" font-size="13">{labels[i]}</text>')
    # Data polygon
    data_pts = []
    for i in range(n):
        a = math.radians(-90 + i * angle_step)
        vr = values[i] / mx * r
        data_pts.append(f"{cx + vr * math.cos(a):.0f},{cy + vr * math.sin(a):.0f}")
    p.append(f'<polygon points="{" ".join(data_pts)}" fill="{cs["radar_fill"]}" stroke="{cs["radar_stroke"]}" stroke-width="2"/>')
    # Data dots
    for i in range(n):
        a = math.radians(-90 + i * angle_step)
        vr = values[i] / mx * r
        dx = cx + vr * math.cos(a); dy = cy + vr * math.sin(a)
        p.append(f'<circle cx="{dx:.0f}" cy="{dy:.0f}" r="4" fill="{cs["radar_stroke"]}"/>')
    return _wrap("\n".join(p), w, h)


# ── Sparkline ──

def chart_spark(data, style_id="default", w=200, h=40):
    cs = _cs(style_id)
    values = data["values"]; n = len(values)
    if n < 2: return ""
    lo, hi = min(values), max(values); rng = max(hi - lo, 1)
    pts = " ".join(f"{i/(n-1)*w:.0f},{h-(v-lo)/rng*(h-4)-2:.0f}" for i, v in enumerate(values))
    return f'<svg viewBox="0 0 {w} {h}" style="width:{w}px;height:{h}px"><polyline points="{pts}" fill="none" stroke="{cs["line_stroke"]}" stroke-width="1.5" stroke-linejoin="round"/></svg>'


# ── CLI 测试 ──

if __name__ == "__main__":
    out_dir = "/tmp/chart_test"
    import os; os.makedirs(out_dir, exist_ok=True)

    bar_data = {"labels": [str(y) for y in range(2015,2026)], "values": [1160,1251,1257,1269,1393,1770,1799,1800,1940,2386,2850], "unit": "$"}
    pie_data = {"labels": ["债券","股票","现金","另类","房地产"], "values": [40,25,15,12,8]}
    scatter_data = {"points": [[i*0.5, 50+i*3+(-1)**i*10] for i in range(20)], "x_label":"风险", "y_label":"收益", "y_unit":"%"}
    bubble_data = {"bubbles": [[1,80,30,"A"],[2,60,50,"B"],[3,90,20,"C"],[4,70,40,"D"],[5,85,35,"E"]], "x_label":"流动性", "y_label":"收益"}
    radar_data = {"labels": ["收益性","安全性","流动性","分散化","成本","透明度"], "values": [0.85,0.7,0.6,0.9,0.5,0.8], "max": 1.0}

    for sid in ["03", "04"]:
        charts = [
            ("bar", chart_bar(bar_data, sid)),
            ("line", chart_line(bar_data, sid)),
            ("pie", chart_pie(pie_data, sid)),
            ("doughnut", chart_doughnut(pie_data, sid)),
            ("scatter", chart_scatter(scatter_data, sid)),
            ("bubble", chart_bubble(bubble_data, sid)),
            ("radar", chart_radar(radar_data, sid)),
        ]
        for name, svg in charts:
            path = os.path.join(out_dir, f"{sid}_{name}.svg")
            with open(path, 'w') as f: f.write(svg)
            print(f"  {sid} {name}: {len(svg)} bytes")
    print(f"Done! → {out_dir}")
