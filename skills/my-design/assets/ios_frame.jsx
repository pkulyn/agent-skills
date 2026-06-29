/**
 * IOSFrame — iPhone 15 Pro 设备框组件
 *
 * 用法（inline Babel）：
 *   <IOSFrame theme="dark">
 *     <div style={{...}}>你的内容</div>
 *   </IOSFrame>
 *
 * Props:
 *   theme   — 'light' | 'dark'，默认 'dark'
 *   scale   — 缩放比例，默认 1
 *   children — ReactNode 内部内容
 *
 * 逻辑尺寸：393×852pt（iPhone 15 Pro）
 * 禁止手写 Dynamic Island / status bar / Home Indicator — 必须用此组件
 */

function IOSFrame(props) {
  var theme = props.theme || 'dark';
  var scale = props.scale || 1;
  var children = props.children;

  // iPhone 15 Pro 逻辑尺寸
  var W = 393;
  var H = 852;
  var cornerRadius = 55;
  var framePadding = 12;  // 设备框边框厚度
  var outerW = W + framePadding * 2;
  var outerH = H + framePadding * 2;

  // Dynamic Island
  var diW = 126;
  var diH = 37;
  var diTop = 12;
  var diRadius = 20;

  // Home Indicator
  var hiW = 134;
  var hiH = 5;
  var hiBottom = 8;
  var hiRadius = 3;

  // 颜色
  var isDark = theme === 'dark';
  var frameBorder = isDark ? '#2a2a2e' : '#c8c8cc';
  var frameBg = isDark ? '#1c1c1e' : '#e8e8ec';
  var diBg = '#000000';
  var hiBg = isDark ? 'rgba(255,255,255,0.25)' : 'rgba(0,0,0,0.2)';
  var outerBg = isDark ? '#0a0a0a' : '#f0f0f2';

  // 内容区域（减去安全区）
  var safeTop = diTop + diH + 8;  // Dynamic Island 下方
  var safeBottom = hiBottom + hiH + 4; // Home Indicator 上方

  return React.createElement('div', {
    style: {
      display: 'inline-block',
      transform: 'scale(' + scale + ')',
      transformOrigin: 'top left',
      background: outerBg,
      borderRadius: (cornerRadius + framePadding) + 'px',
      padding: framePadding + 'px',
      border: '1px solid ' + frameBorder,
      boxShadow: isDark
        ? '0 20px 60px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.05) inset'
        : '0 20px 60px rgba(0,0,0,0.15), 0 0 0 1px rgba(0,0,0,0.05) inset',
      position: 'relative',
      overflow: 'hidden'
    }
  },
    // 内部手机屏幕容器
    React.createElement('div', {
      style: {
        width: W + 'px',
        height: H + 'px',
        borderRadius: cornerRadius + 'px',
        overflow: 'hidden',
        position: 'relative',
        background: frameBg
      }
    },
      // Dynamic Island
      React.createElement('div', {
        style: {
          position: 'absolute',
          top: diTop + 'px',
          left: '50%',
          transform: 'translateX(-50%)',
          width: diW + 'px',
          height: diH + 'px',
          background: diBg,
          borderRadius: diRadius + 'px',
          zIndex: 100,
          pointerEvents: 'none'
        }
      }),

      // 内容区域
      React.createElement('div', {
        style: {
          position: 'absolute',
          top: 0, left: 0, right: 0, bottom: 0,
          paddingTop: safeTop + 'px',
          paddingBottom: safeBottom + 'px',
          overflow: 'hidden',
          WebkitOverflowScrolling: 'touch'
        }
      }, children),

      // Home Indicator
      React.createElement('div', {
        style: {
          position: 'absolute',
          bottom: hiBottom + 'px',
          left: '50%',
          transform: 'translateX(-50%)',
          width: hiW + 'px',
          height: hiH + 'px',
          background: hiBg,
          borderRadius: hiRadius + 'px',
          zIndex: 100,
          pointerEvents: 'none'
        }
      })
    )
  );
}
