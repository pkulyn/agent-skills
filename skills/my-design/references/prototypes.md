# 交互原型专项参考

> 面向 Agent 使用。中文为主，技术术语保留英文。

---

## 1. 架构选型

### 默认：单文件 inline React

所有 JSX / data / styles 写进 `<script type="text/babel">`，双击 HTML 即可在浏览器打开。

**优点**：零构建、零依赖、一键交付、设计同学直接查看。

### 何时拆外部文件

| 条件 | 说明 |
|------|------|
| 单文件 > 1000 行 | 维护成本飙升，拆出 `data.js` / `styles.css` |
| 多 subagent 并行 | 不同屏由不同 agent 写，各自独立文件再合并 |

拆文件时，HTML 用 `<script src="data.js"></script>` 引入，仍保持零构建。

### 选型速查表

| 场景 | 架构 | 交付方式 |
|------|------|----------|
| 3–5 屏设计 review | 单文件 inline React | 一个 HTML |
| 6–10 屏 Flow Demo | 单文件 inline React（状态机） | 一个 HTML |
| 10+ 屏大型原型 | 拆文件 + 合并 | HTML + JS/CSS |
| 多人并行 | 按屏拆文件 | 各自交付后合并 |
| 需要真实图片 | 单文件 + 图片 URL | 一个 HTML（图片在线） |
| 需要离线演示 | 拆文件 + 图片 base64 | 打包 zip |

---

## 2. 交付形态：Overview 平铺 vs Flow Demo

**先问用户要哪种，不要默认挑一种。**

### Overview 平铺

- 所有屏并排静态展示
- 每屏一台独立 iPhone 设备框
- 用途：设计 review、走查、PPT 截图
- 交互：无（纯展示）
- 优点：一屏总览全流程，方便标注和对比

### Flow Demo

- 单台 iPhone 设备框
- 内嵌 AppPhone 状态管理器
- 用途：交互演示、可用性测试、stakeholder 汇报
- 交互：可点击跳转、TabBar 切换、返回
- 优点：体验接近真实产品

### 快速判断

| 需求 | 推荐 |
|------|------|
| "看全流程" / "放PPT" / "设计走查" | Overview 平铺 |
| "点一下试试" / "给老板演示" / "可用性测试" | Flow Demo |
| 不确定 | 问用户 |

---

## 3. 真图优先原则

### 默认行为：主动取真实图片

不等用户要求，默认去取真实图片。图片来源优先级：

1. **Wikimedia Commons** — 免费、高质、可直接 URL 引用
2. **Unsplash** — 免费、美观、`https://images.unsplash.com/photo-xxx?w=400`
3. **Pexels** — 免费、商业可用

### 真图诚实性测试

在决定是否加图时，做这个判断：

- **去掉图信息有损** → 必须加真图（如：旅游 App 的目的地照片、美食 App 的菜品图）
- **去掉图无影响** → 不要加（如：设置页面的装饰图、纯占位头像）

### 禁止事项

- ❌ SVG 手画人物 / 物品 / 场景（火柴人、简笔画城市等）
- ❌ 用 emoji 当图片替代品（🗺️ ≠ 真实地图截图）
- ❌ 纯色块 + 文字假装图片

### 实操模板

```jsx
// 取 Unsplash 图片的标准写法
const IMAGES = {
  destination: "https://images.unsplash.com/photo-1506929562872-bb421503ef21?w=400&h=300&fit=crop",
  food: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=300&fit=crop",
  avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop",
};
```

---

## 4. 设备框规范

### 核心规则：用组件，禁止手写

| 平台 | 组件 | 禁止手写 |
|------|------|----------|
| iOS | `assets/ios_frame.jsx` | Dynamic Island / Status Bar / Home Indicator |
| Android | `assets/android_frame.jsx` | 状态栏 / 导航栏 / 手势条 |
| macOS | `assets/macos_window.jsx` | 红绿灯 / 工具栏 |
| Browser | `assets/browser_window.jsx` | 地址栏 / Tab 栏 |

### 使用方式

```jsx
// 引入设备框组件
const { IPhoneFrame } = await import('./assets/ios_frame.jsx');

// 使用
<IPhoneFrame>
  {/* 你的页面内容 */}
</IPhoneFrame>
```

### 设备尺寸参考

| 设备 | 逻辑尺寸 (pt) | 渲染尺寸 (px @2x) |
|------|---------------|-------------------|
| iPhone 15 Pro | 393 × 852 | 786 × 1704 |
| iPhone 15 | 390 × 844 | 780 × 1688 |
| iPad Air | 820 × 1180 | 1640 × 2360 |
| Android avg | 360 × 800 | 720 × 1600 |

---

## 5. 交付前 Playwright 验证

### 3 项最小点击测试

| # | 测试项 | 目的 |
|---|--------|------|
| 1 | 进入详情 | 导航链路通畅 |
| 2 | 关键标注点 | 核心信息可见 |
| 3 | Tab 切换 | 状态切换正常 |

### 验证流程

```bash
# 1. 启动本地服务器
npx serve . -p 3456 &

# 2. 运行 Playwright 测试
npx playwright test --project=chromium

# 3. 检查 pageerror
# 测试脚本中必须包含：
# expect(page.errors).toHaveLength(0)
```

### 最小测试脚本模板

```javascript
const { test, expect } = require('@playwright/test');

test('原型基本可用', async ({ page }) => {
  await page.goto('http://localhost:3456/prototype.html');

  // 测试1：进入详情
  await page.click('[data-testid="card"]');
  await expect(page.locator('[data-testid="detail"]')).toBeVisible();

  // 测试2：关键标注点
  await expect(page.locator('[data-testid="key-label"]')).toBeVisible();

  // 测试3：Tab 切换
  await page.click('[data-testid="tab-explore"]');
  await expect(page.locator('[data-testid="explore-view"]')).toBeVisible();

  // 检查无 JS 错误
  expect(page.errors).toHaveLength(0);
});
```

**交付标准：3 项测试全过 + pageerror 为 0。**

---

## 6. App 原型品位锚点

| 维度 | 首选 ✅ | 避免 ❌ |
|------|---------|---------|
| 字体 | 衬线 display（如 Playfair Display）+ `-apple-system` body | 全场 SF Pro 或 Inter，毫无层次 |
| 色彩 | 有温度底色（如 #FAF7F2）+ 单个 accent（如 #E85D3A） | 多色聚类，彩虹调色板 |
| 信息密度·克制型 | 少容器少 border，留白即信息 | 无意义 icon + tag + dot 堆砌 |
| 信息密度·高密度型 | AI/数据产品 ≥ 3 处差异化信息层 | 只放一个按钮一个时钟 |
| 图标 | 线性 / 单色，只做表意 | 渐变 icon、3D icon、emoji 当 icon |
| 间距 | 8pt 网格，16/24/32 常用 | 随意间距，3px/7px/13px |
| 圆角 | 12–16pt（大卡片）/ 8pt（小卡片） | 全部 0 或全部 999px |
| 阴影 | 微妙 shadow-sm，或无阴影加 border | 大面积浓重阴影 |
| 动效 | 200–300ms ease-out，克制 | 弹簧弹跳 / 过长动画 |

### 字体搭配推荐

| 风格 | Display（标题） | Body（正文） |
|------|-----------------|-------------|
| 经典杂志 | Playfair Display | -apple-system |
| 现代极简 | DM Serif Display | -apple-system |
| 科技感 | Space Grotesk | -apple-system |
| 中文优先 | Noto Serif SC | -apple-system |

```html
<!-- Google Fonts 引入方式 -->
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">
```

---

## 7. iOS 原型骨架代码

### 7.1 Overview 平铺骨架

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>App Prototype - Overview</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #F0EDE8;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    padding: 60px 40px;
    min-height: 100vh;
  }
  .overview-title {
    font-family: 'Playfair Display', serif;
    font-size: 32px;
    color: #1A1A1A;
    margin-bottom: 12px;
  }
  .overview-subtitle {
    font-size: 14px;
    color: #888;
    margin-bottom: 48px;
  }
  .screens-container {
    display: flex;
    gap: 40px;
    overflow-x: auto;
    padding-bottom: 40px;
  }
  .screen-wrapper {
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
  }
  .screen-label {
    font-size: 13px;
    color: #666;
    font-weight: 500;
  }
  /* iPhone Frame */
  .iphone-frame {
    width: 280px;
    height: 607px;
    background: #1A1A1A;
    border-radius: 40px;
    padding: 12px;
    position: relative;
    box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  }
  .iphone-screen {
    width: 100%;
    height: 100%;
    background: #FFFFFF;
    border-radius: 30px;
    overflow: hidden;
    position: relative;
  }
  .dynamic-island {
    position: absolute;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    width: 80px;
    height: 24px;
    background: #1A1A1A;
    border-radius: 12px;
    z-index: 10;
  }
  .home-indicator {
    position: absolute;
    bottom: 8px;
    left: 50%;
    transform: translateX(-50%);
    width: 100px;
    height: 4px;
    background: #1A1A1A;
    border-radius: 2px;
    z-index: 10;
  }
</style>
</head>
<body>
<div id="root"></div>
<script type="text/babel">

const SCREENS = [
  { name: "首页", component: HomeScreen },
  { name: "发现", component: ExploreScreen },
  { name: "详情", component: DetailScreen },
  { name: "个人", component: ProfileScreen },
];

function IPhoneFrame({ children, label }) {
  return (
    <div className="screen-wrapper">
      <div className="iphone-frame">
        <div className="iphone-screen">
          <div className="dynamic-island" />
          {children}
          <div className="home-indicator" />
        </div>
      </div>
      <span className="screen-label">{label}</span>
    </div>
  );
}

function HomeScreen() {
  return (
    <div style={{ padding: '52px 20px 20px', height: '100%', background: '#FAF7F2' }}>
      <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 22, color: '#1A1A1A' }}>Good Morning</h2>
      <p style={{ fontSize: 13, color: '#999', marginTop: 4 }}>Let's find something nice</p>
      {/* 内容区域 */}
      <div style={{ marginTop: 24, display: 'flex', flexDirection: 'column', gap: 12 }}>
        {[1,2,3].map(i => (
          <div key={i} style={{
            height: 80, borderRadius: 12, background: '#FFF',
            boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
            padding: 16, display: 'flex', alignItems: 'center', gap: 12
          }}>
            <div style={{ width: 48, height: 48, borderRadius: 10, background: '#F0EDE8' }} />
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, color: '#1A1A1A' }}>Card Title {i}</div>
              <div style={{ fontSize: 12, color: '#999', marginTop: 2 }}>Subtitle text</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ExploreScreen() {
  return (
    <div style={{ padding: '52px 20px 20px', height: '100%', background: '#FAF7F2' }}>
      <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 22, color: '#1A1A1A' }}>Explore</h2>
      <div style={{ marginTop: 20, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
        {[1,2,3,4].map(i => (
          <div key={i} style={{
            height: 100, borderRadius: 12, background: '#E85D3A',
            opacity: 0.6 + i * 0.1
          }} />
        ))}
      </div>
    </div>
  );
}

function DetailScreen() {
  return (
    <div style={{ height: '100%', background: '#FFF' }}>
      <div style={{ height: 180, background: '#E85D3A', position: 'relative' }}>
        <div style={{ position: 'absolute', bottom: 16, left: 20, color: '#FFF' }}>
          <h3 style={{ fontFamily: "'Playfair Display', serif", fontSize: 20 }}>Detail View</h3>
        </div>
      </div>
      <div style={{ padding: 20 }}>
        <p style={{ fontSize: 14, color: '#666', lineHeight: 1.6 }}>
          Detail content goes here with meaningful information.
        </p>
      </div>
    </div>
  );
}

function ProfileScreen() {
  return (
    <div style={{ padding: '52px 20px 20px', height: '100%', background: '#FAF7F2', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <div style={{ width: 64, height: 64, borderRadius: 32, background: '#E85D3A', marginTop: 20 }} />
      <h3 style={{ fontFamily: "'Playfair Display', serif", fontSize: 18, marginTop: 12, color: '#1A1A1A' }}>User Name</h3>
      <p style={{ fontSize: 12, color: '#999', marginTop: 4 }}>user@email.com</p>
    </div>
  );
}

function App() {
  return (
    <>
      <h1 className="overview-title">App Name</h1>
      <p className="overview-subtitle">Overview — All Screens</p>
      <div className="screens-container">
        {SCREENS.map(({ name, component: Screen }) => (
          <IPhoneFrame key={name} label={name}>
            <Screen />
          </IPhoneFrame>
        ))}
      </div>
    </>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
</script>
</body>
</html>
```

### 7.2 Flow Demo 骨架（AppPhone 状态管理器）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>App Prototype - Flow Demo</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #F0EDE8;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
  }
  .iphone-frame {
    width: 320px;
    height: 693px;
    background: #1A1A1A;
    border-radius: 44px;
    padding: 12px;
    position: relative;
    box-shadow: 0 30px 80px rgba(0,0,0,0.2);
  }
  .iphone-screen {
    width: 100%;
    height: 100%;
    background: #FFFFFF;
    border-radius: 34px;
    overflow: hidden;
    position: relative;
  }
  .dynamic-island {
    position: absolute;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    width: 90px;
    height: 26px;
    background: #1A1A1A;
    border-radius: 13px;
    z-index: 10;
  }
  .home-indicator {
    position: absolute;
    bottom: 8px;
    left: 50%;
    transform: translateX(-50%);
    width: 110px;
    height: 4px;
    background: #1A1A1A;
    border-radius: 2px;
    z-index: 10;
  }
</style>
</head>
<body>
<div id="root"></div>
<script type="text/babel">
const { useState, useCallback, createContext, useContext } = React;

// ─── AppPhone 状态管理器 ───
const AppPhoneContext = createContext();

function useAppPhone() {
  return useContext(AppPhoneContext);
}

function AppPhoneProvider({ children, initialScreen = 'home' }) {
  const [screen, setScreen] = useState(initialScreen);
  const [params, setParams] = useState({});
  const [history, setHistory] = useState([]);

  const navigate = useCallback((nextScreen, nextParams = {}) => {
    setHistory(prev => [...prev, { screen, params }]);
    setScreen(nextScreen);
    setParams(nextParams);
  }, [screen, params]);

  const goBack = useCallback(() => {
    if (history.length === 0) return;
    const prev = history[history.length - 1];
    setHistory(h => h.slice(0, -1));
    setScreen(prev.screen);
    setParams(prev.params);
  }, [history]);

  return (
    <AppPhoneContext.Provider value={{ screen, params, navigate, goBack }}>
      {children}
    </AppPhoneContext.Provider>
  );
}

// ─── 页面组件 ───

function HomeScreen() {
  const { navigate } = useAppPhone();
  return (
    <div data-testid="home-view" style={{ padding: '52px 20px 80px', height: '100%', background: '#FAF7F2', overflowY: 'auto' }}>
      <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 24, color: '#1A1A1A' }}>Good Morning</h2>
      <p style={{ fontSize: 13, color: '#999', marginTop: 4 }}>Let's find something nice</p>
      <div style={{ marginTop: 24, display: 'flex', flexDirection: 'column', gap: 12 }}>
        {[1,2,3].map(i => (
          <div
            key={i}
            data-testid="card"
            onClick={() => navigate('detail', { id: i })}
            style={{
              height: 80, borderRadius: 12, background: '#FFF',
              boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
              padding: 16, display: 'flex', alignItems: 'center', gap: 12,
              cursor: 'pointer',
              transition: 'transform 0.15s ease',
            }}
          >
            <div style={{ width: 48, height: 48, borderRadius: 10, background: '#F0EDE8' }} />
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, color: '#1A1A1A' }}>Card Title {i}</div>
              <div style={{ fontSize: 12, color: '#999', marginTop: 2 }}>Tap to view detail</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function DetailScreen() {
  const { params, goBack } = useAppPhone();
  return (
    <div data-testid="detail" style={{ height: '100%', background: '#FFF', overflowY: 'auto' }}>
      <div style={{ height: 200, background: '#E85D3A', position: 'relative', display: 'flex', alignItems: 'flex-end', padding: 20 }}>
        <div onClick={goBack} style={{
          position: 'absolute', top: 52, left: 16,
          width: 32, height: 32, borderRadius: 16, background: 'rgba(255,255,255,0.3)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          cursor: 'pointer', color: '#FFF', fontSize: 16
        }}>←</div>
        <div style={{ color: '#FFF' }}>
          <h3 style={{ fontFamily: "'Playfair Display', serif", fontSize: 22 }}>Detail #{params.id}</h3>
          <p data-testid="key-label" style={{ fontSize: 13, marginTop: 4, opacity: 0.8 }}>Key information label</p>
        </div>
      </div>
      <div style={{ padding: 20 }}>
        <p style={{ fontSize: 14, color: '#666', lineHeight: 1.7 }}>
          This is the detail view for item {params.id}. Content area supports scrolling for longer text.
        </p>
      </div>
    </div>
  );
}

function ProfileScreen() {
  return (
    <div data-testid="profile-view" style={{ padding: '52px 20px 80px', height: '100%', background: '#FAF7F2', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <div style={{ width: 72, height: 72, borderRadius: 36, background: '#E85D3A', marginTop: 30 }} />
      <h3 style={{ fontFamily: "'Playfair Display', serif", fontSize: 20, marginTop: 16, color: '#1A1A1A' }}>User Name</h3>
      <p style={{ fontSize: 13, color: '#999', marginTop: 4 }}>user@email.com</p>
    </div>
  );
}

function ExploreScreen() {
  return (
    <div data-testid="explore-view" style={{ padding: '52px 20px 80px', height: '100%', background: '#FAF7F2', overflowY: 'auto' }}>
      <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 24, color: '#1A1A1A' }}>Explore</h2>
      <div style={{ marginTop: 20, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
        {[1,2,3,4].map(i => (
          <div key={i} style={{ height: 100, borderRadius: 12, background: `hsl(14, 80%, ${50 + i * 5}%)` }} />
        ))}
      </div>
    </div>
  );
}

// ─── TabBar ───

function TabBar() {
  const { screen, navigate } = useAppPhone();
  const tabs = [
    { id: 'home', label: '首页', icon: '🏠' },
    { id: 'explore', label: '发现', icon: '🧭' },
    { id: 'profile', label: '我的', icon: '👤' },
  ];
  // detail 不属于 tab，用 home 高亮
  const activeTab = tabs.find(t => t.id === screen) ? screen : 'home';

  return (
    <div style={{
      position: 'absolute', bottom: 20, left: 0, right: 0,
      display: 'flex', justifyContent: 'space-around',
      padding: '8px 0 4px',
      background: 'rgba(255,255,255,0.95)',
      backdropFilter: 'blur(20px)',
      borderTop: '0.5px solid rgba(0,0,0,0.08)',
      zIndex: 20,
    }}>
      {tabs.map(tab => (
        <div
          key={tab.id}
          data-testid={`tab-${tab.id}`}
          onClick={() => navigate(tab.id)}
          style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2,
            cursor: 'pointer', opacity: activeTab === tab.id ? 1 : 0.4,
            transition: 'opacity 0.2s',
          }}
        >
          <span style={{ fontSize: 20 }}>{tab.icon}</span>
          <span style={{ fontSize: 10, fontWeight: 500 }}>{tab.label}</span>
        </div>
      ))}
    </div>
  );
}

// ─── Screen Router ───

function ScreenRouter() {
  const { screen } = useAppPhone();
  const screens = {
    home: HomeScreen,
    explore: ExploreScreen,
    detail: DetailScreen,
    profile: ProfileScreen,
  };
  const Screen = screens[screen] || HomeScreen;
  return <Screen />;
}

// ─── App ───

function App() {
  return (
    <div className="iphone-frame">
      <div className="iphone-screen">
        <div className="dynamic-island" />
        <AppPhoneProvider initialScreen="home">
          <ScreenRouter />
          <TabBar />
        </AppPhoneProvider>
        <div className="home-indicator" />
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
</script>
</body>
</html>
```

### 7.3 TabBar 交互示例（独立片段）

可直接嵌入 Flow Demo 或单独使用：

```jsx
// ─── TabBar 组件（带动画） ───
function AnimatedTabBar({ tabs, activeId, onSwitch }) {
  return (
    <div style={{
      position: 'absolute', bottom: 20, left: 0, right: 0,
      display: 'flex', justifyContent: 'space-around',
      padding: '10px 0 4px',
      background: 'rgba(255,255,255,0.92)',
      backdropFilter: 'blur(20px)',
      WebkitBackdropFilter: 'blur(20px)',
      borderTop: '0.5px solid rgba(0,0,0,0.06)',
      zIndex: 20,
    }}>
      {tabs.map(tab => {
        const isActive = tab.id === activeId;
        return (
          <div
            key={tab.id}
            onClick={() => onSwitch(tab.id)}
            style={{
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3,
              cursor: 'pointer',
              transition: 'all 0.2s ease-out',
              transform: isActive ? 'scale(1.05)' : 'scale(1)',
            }}
          >
            {/* 图标容器 */}
            <div style={{
              width: 32, height: 32, borderRadius: 16,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: isActive ? '#E85D3A' : 'transparent',
              color: isActive ? '#FFF' : '#999',
              fontSize: 16,
              transition: 'all 0.2s ease-out',
            }}>
              {tab.icon}
            </div>
            {/* 标签文字 */}
            <span style={{
              fontSize: 10, fontWeight: isActive ? 600 : 400,
              color: isActive ? '#E85D3A' : '#999',
              transition: 'all 0.2s ease-out',
            }}>
              {tab.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}

// 使用方式
const TABS = [
  { id: 'home', label: '首页', icon: '🏠' },
  { id: 'explore', label: '发现', icon: '🧭' },
  { id: 'profile', label: '我的', icon: '👤' },
];

// 在父组件中
const [activeTab, setActiveTab] = useState('home');
// ...
<AnimatedTabBar tabs={TABS} activeId={activeTab} onSwitch={setActiveTab} />
```

---

## 附录：常见陷阱

| 陷阱 | 正确做法 |
|------|----------|
| 设备框内写死 px 尺寸 | 用 % / vh / calc 适配不同展示尺寸 |
| Overview 每屏都有 TabBar | Overview 去掉 TabBar，只在 Flow Demo 加 |
| Flow Demo 没有返回手势 | 至少提供 ← 按钮，最好加 swipe back |
| 所有页面用同一背景色 | 每个页面独立配色，暗示场景切换 |
| 图片用 placeholder 矩形 | 默认取真实图片，矩形只做最后 fallback |
| testid 只加在 div 上 | 关键交互元素都要加 `data-testid` |
