# 图表组件库

> 输入 data + style_id → 输出风格化 SVG。7种图表 + sparkline。

## API

```python
from charts import chart_bar, chart_line, chart_pie, chart_doughnut, chart_scatter, chart_bubble, chart_radar, chart_spark
```

## 数据格式

```python
# 柱状图/折线图
{"labels": ["2015","2016",...], "values": [1160,1251,...], "unit": "$"}

# 饼图/环形图
{"labels": ["债券","股票","现金","另类","房地产"], "values": [40,25,15,12,8]}

# 散点图
{"points": [[x1,y1],[x2,y2],...], "x_label":"风险", "y_label":"收益", "y_unit":"%"}

# 气泡图
{"bubbles": [[x,y,r,"标签"],...], "x_label":"流动性", "y_label":"收益"}

# 雷达图
{"labels": ["收益性","安全性",...], "values": [0.85,0.7,...], "max": 1.0}

# Sparkline
{"values": [1160,1251,...]}
```

## 风格差异

| 图表 | 03 数据叙事 | 04 Rams |
|------|------------|---------|
| 柱状图 | 蓝+网格+趋势虚线+标注 | 橙+无网格+极简 |
| 折线图 | 粗线+数据点+区间阴影 | 细线+无点+无阴影 |
| 饼图 | 蓝色渐变6阶 | 橙色渐变6阶 |
| 环形图 | 蓝色+中心总计 | 橙色+中心总计 |
| 散点图 | 蓝点+网格 | 橙点+无网格 |
| 气泡图 | 蓝半透明+描边 | 橙半透明+描边 |
| 雷达图 | 蓝填充+网格环 | 橙填充+无网格 |
