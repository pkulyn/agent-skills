/**
 * DesignCanvas — 并排变体展示组件
 *
 * 用法（inline Babel）：
 *   <DesignCanvas labels={['方案 A', '方案 B']}>
 *     <div style={...}>内容A</div>
 *     <div style={...}>内容B</div>
 *   </DesignCanvas>
 *
 * Props:
 *   labels     — string[] 变体标签，默认 ['A','B',...]
 *   children   — ReactNode[] 2-4 个变体内容
 *   tweaks     — { label, min, max, step, value, onChange }[] 可选参数面板
 *   gap        — 间距 px，默认 24
 *   theme      — 'light' | 'dark'，默认 'dark'
 */

function DesignCanvas(props) {
  var labels = props.labels || [];
  var children = React.Children.toArray(props.children);
  var tweaks = props.tweaks || [];
  var gap = props.gap || 24;
  var theme = props.theme || 'dark';

  var count = children.length;
  if (count < 2 || count > 4) {
    return React.createElement('div', {
      style: { color: '#f66', padding: 24 }
    }, 'DesignCanvas: 需要 2-4 个 children，当前 ' + count + ' 个');
  }

  // 默认标签
  var defaultLabels = ['Variant A', 'Variant B', 'Variant C', 'Variant D'];
  var finalLabels = labels.length === count ? labels : defaultLabels.slice(0, count);

  // 布局：3个以下横排，4个 2×2 网格
  var isGrid = count === 4;

  var bg = theme === 'dark' ? '#0d0d0d' : '#f5f5f5';
  var cardBg = theme === 'dark' ? '#1a1a1a' : '#fff';
  var borderColor = theme === 'dark' ? '#333' : '#ddd';
  var labelColor = theme === 'dark' ? '#aaa' : '#666';
  var textColor = theme === 'dark' ? '#eee' : '#222';

  // 容器样式
  var containerStyle = {
    display: 'flex',
    flexDirection: isGrid ? 'row' : 'row',
    flexWrap: isGrid ? 'wrap' : 'nowrap',
    gap: gap + 'px',
    padding: gap + 'px',
    background: bg,
    borderRadius: 12,
    minHeight: 0
  };

  // 单个卡片样式
  function cardStyle(isGridItem) {
    return {
      flex: isGrid ? '1 1 calc(50% - ' + (gap / 2) + 'px)' : '1 1 0%',
      minWidth: 0,
      background: cardBg,
      border: '1px solid ' + borderColor,
      borderRadius: 8,
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column'
    };
  }

  // 标签栏
  function labelBar(text) {
    return React.createElement('div', {
      style: {
        padding: '8px 16px',
        borderBottom: '1px solid ' + borderColor,
        fontSize: 12,
        fontWeight: 600,
        color: labelColor,
        textTransform: 'uppercase',
        letterSpacing: '0.5px',
        fontFamily: 'system-ui, sans-serif'
      }
    }, text);
  }

  // 内容区域
  function contentArea(child) {
    return React.createElement('div', {
      style: {
        flex: 1,
        padding: 16,
        overflow: 'auto',
        color: textColor
      }
    }, child);
  }

  // Tweaks 面板
  var tweaksPanel = null;
  if (tweaks.length > 0) {
    var tweakRows = tweaks.map(function(t, i) {
      return React.createElement('div', {
        key: i,
        style: { display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }
      },
        React.createElement('label', {
          style: { fontSize: 12, color: labelColor, width: 80, flexShrink: 0, fontFamily: 'system-ui' }
        }, t.label),
        React.createElement('input', {
          type: 'range',
          min: t.min, max: t.max, step: t.step, value: t.value,
          onChange: t.onChange,
          style: { flex: 1, accentColor: '#4a90d9' }
        }),
        React.createElement('span', {
          style: { fontSize: 12, color: textColor, width: 40, textAlign: 'right', fontFamily: 'monospace' }
        }, t.value)
      );
    });

    tweaksPanel = React.createElement('div', {
      style: {
        background: cardBg,
        border: '1px solid ' + borderColor,
        borderRadius: 8,
        padding: 16,
        marginBottom: gap
      }
    },
      React.createElement('div', {
        style: { fontSize: 12, fontWeight: 600, color: labelColor, marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.5px' }
      }, '⚡ Tweaks'),
      tweakRows
    );
  }

  // 卡片列表
  var cards = children.map(function(child, i) {
    return React.createElement('div', {
      key: i, style: cardStyle(isGrid)
    }, labelBar(finalLabels[i]), contentArea(child));
  });

  return React.createElement('div', {
    style: { fontFamily: 'system-ui, sans-serif' }
  },
    tweaksPanel,
    React.createElement('div', { style: containerStyle }, cards)
  );
}
