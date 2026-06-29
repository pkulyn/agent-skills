/**
 * Animations — Stage + Sprite 时间轴动画组件
 *
 * 用法（inline Babel）：
 *   <Stage duration={3000} loop>
 *     <Sprite start={0} duration={1000} easing="easeOutExpo">
 *       {({ progress }) => (
 *         <div style={{ opacity: progress, transform: `translateY(${(1-progress)*40}px)` }}>
 *           Hello
 *         </div>
 *       )}
 *     </Sprite>
 *   </Stage>
 *
 * interpolate(time, [{time:0, value:0}, {time:1000, value:1}]) → number
 * Easing: easeInOutCubic, easeOutExpo, easeInOutQuart, easeOutBack, easeInQuad
 */

// ── Easing 库 ──
var Easing = {
  linear: function(t) { return t; },
  easeInQuad: function(t) { return t * t; },
  easeOutExpo: function(t) { return t === 1 ? 1 : 1 - Math.pow(2, -10 * t); },
  easeInOutCubic: function(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  },
  easeInOutQuart: function(t) {
    return t < 0.5 ? 8 * t * t * t * t : 1 - Math.pow(-2 * t + 2, 4) / 2;
  },
  easeOutBack: function(t) {
    var c1 = 1.70158;
    var c3 = c1 + 1;
    return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
  }
};

// ── interpolate 关键帧插值 ──
function interpolate(time, keyframes) {
  if (!keyframes || keyframes.length === 0) return 0;
  if (keyframes.length === 1) return keyframes[0].value;

  // 在边界外
  if (time <= keyframes[0].time) return keyframes[0].value;
  if (time >= keyframes[keyframes.length - 1].time) return keyframes[keyframes.length - 1].value;

  // 找到区间
  var i = 0;
  while (i < keyframes.length - 1 && keyframes[i + 1].time <= time) i++;

  var from = keyframes[i];
  var to = keyframes[i + 1];
  if (!to) return from.value;

  var segDuration = to.time - from.time;
  var segProgress = segDuration > 0 ? (time - from.time) / segDuration : 1;

  // 应用 easing（如果关键帧有 easing 属性）
  var easingName = to.easing || 'linear';
  var easingFn = Easing[easingName] || Easing.linear;
  var easedProgress = easingFn(segProgress);

  // 线性插值
  return from.value + (to.value - from.value) * easedProgress;
}

// ── useTime hook ──
function useTime() {
  var ctx = React.useContext(StageContext);
  return ctx ? ctx.time : 0;
}

// ── StageContext ──
var StageContext = React.createContext(null);

// ── Stage 组件 ──
function Stage(props) {
  var duration = props.duration || 2000;
  var loop = props.loop !== false; // 默认循环
  var children = props.children;
  var autoplay = props.autoplay !== false; // 默认自动播放

  var _state = React.useState(autoplay ? 'playing' : 'paused');
  var playState = _state[0];
  var setPlayState = _state[1];

  var _time = React.useState(0);
  var currentTime = _time[0];
  var setCurrentTime = _time[1];

  var rafRef = React.useRef(null);
  var lastTickRef = React.useRef(null);

  // 动画循环
  React.useEffect(function() {
    if (playState !== 'playing') {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      return;
    }

    lastTickRef.current = performance.now();

    function tick() {
      var now = performance.now();
      var delta = now - lastTickRef.current;
      lastTickRef.current = now;

      setCurrentTime(function(prev) {
        var next = prev + delta;
        if (next >= duration) {
          if (loop) {
            return next % duration;
          } else {
            setPlayState('paused');
            return duration;
          }
        }
        return next;
      });

      rafRef.current = requestAnimationFrame(tick);
    }

    rafRef.current = requestAnimationFrame(tick);
    return function() { if (rafRef.current) cancelAnimationFrame(rafRef.current); };
  }, [playState, duration, loop]);

  // 播放/暂停
  function togglePlay() {
    setPlayState(function(s) {
      if (s === 'playing') return 'paused';
      // 从头播放如果已结束
      if (currentTime >= duration) setCurrentTime(0);
      return 'playing';
    });
  }

  function reset() {
    setCurrentTime(0);
    if (playState === 'paused') setPlayState('playing');
  }

  // 格式化时间
  function fmtTime(ms) {
    var s = Math.floor(ms / 1000);
    var m = Math.floor(s / 60);
    var frac = Math.floor((ms % 1000) / 10);
    return (m > 0 ? m + ':' : '') + (s % 60).toString().padStart(m > 0 ? 2 : 1, '0') + '.' + frac.toString().padStart(2, '0');
  }

  var progress = duration > 0 ? currentTime / duration : 0;

  // 控制栏
  var controls = React.createElement('div', {
    style: {
      display: 'flex', alignItems: 'center', gap: 12,
      padding: '10px 16px',
      background: '#1a1a1a', borderRadius: 8,
      fontFamily: 'system-ui, sans-serif', fontSize: 13,
      color: '#ccc', userSelect: 'none'
    }
  },
    // 播放/暂停按钮
    React.createElement('button', {
      onClick: togglePlay,
      style: {
        background: 'none', border: 'none', color: '#fff',
        fontSize: 18, cursor: 'pointer', padding: '2px 6px',
        lineHeight: 1, minWidth: 28
      }
    }, playState === 'playing' ? '⏸' : '▶'),

    // 进度条
    React.createElement('div', {
      style: { flex: 1, position: 'relative', height: 6, background: '#333', borderRadius: 3, cursor: 'pointer' },
      onClick: function(e) {
        var rect = e.currentTarget.getBoundingClientRect();
        var ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        setCurrentTime(ratio * duration);
      }
    },
      React.createElement('div', {
        style: {
          position: 'absolute', left: 0, top: 0, bottom: 0,
          width: (progress * 100) + '%',
          background: '#4a90d9', borderRadius: 3,
          transition: 'width 0.05s linear'
        }
      }),
      // Scrubber 手柄
      React.createElement('div', {
        style: {
          position: 'absolute', top: '50%', left: (progress * 100) + '%',
          transform: 'translate(-50%, -50%)',
          width: 14, height: 14, borderRadius: '50%',
          background: '#fff', boxShadow: '0 1px 4px rgba(0,0,0,0.3)',
          cursor: 'grab'
        },
        // 拖拽 scrubber
        onMouseDown: function(e) {
          e.preventDefault();
          var bar = e.currentTarget.parentElement;
          function onMove(ev) {
            var rect = bar.getBoundingClientRect();
            var ratio = Math.max(0, Math.min(1, (ev.clientX - rect.left) / rect.width));
            setCurrentTime(ratio * duration);
          }
          function onUp() {
            document.removeEventListener('mousemove', onMove);
            document.removeEventListener('mouseup', onUp);
          }
          document.addEventListener('mousemove', onMove);
          document.addEventListener('mouseup', onUp);
        }
      })
    ),

    // 时间显示
    React.createElement('span', {
      style: { fontVariantNumeric: 'tabular-nums', minWidth: 100, textAlign: 'center', fontSize: 12, color: '#999' }
    }, fmtTime(currentTime) + ' / ' + fmtTime(duration)),

    // 循环开关
    React.createElement('button', {
      onClick: function() { /* toggle loop via parent — simplified: just visual */ },
      style: {
        background: loop ? 'rgba(74,144,217,0.2)' : 'none',
        border: loop ? '1px solid #4a90d9' : '1px solid #555',
        borderRadius: 4, color: loop ? '#4a90d9' : '#666',
        padding: '2px 8px', cursor: 'pointer', fontSize: 12
      }
    }, '↻ Loop'),

    // 重置按钮
    React.createElement('button', {
      onClick: reset,
      style: {
        background: 'none', border: '1px solid #555', borderRadius: 4,
        color: '#999', padding: '2px 8px', cursor: 'pointer', fontSize: 12
      }
    }, '↺')
  );

  // Context 提供当前时间
  var contextValue = React.useMemo(function() {
    return { time: currentTime, duration: duration };
  }, [currentTime, duration]);

  return React.createElement('div', {
    style: { display: 'flex', flexDirection: 'column', gap: 0 }
  },
    // 动画画布
    React.createElement('div', {
      style: { position: 'relative', overflow: 'hidden', minHeight: 200 }
    },
      React.createElement(StageContext.Provider, { value: contextValue }, children)
    ),
    // 控制栏
    controls
  );
}

// ── Sprite 组件 ──
function Sprite(props) {
  var start = props.start || 0;
  var duration = props.duration || 1000;
  var easingName = props.easing || 'easeInOutCubic';
  var children = props.children;

  var ctx = React.useContext(StageContext);
  var time = ctx ? ctx.time : 0;

  // 计算当前片段进度 [0, 1]
  var localTime = time - start;
  var rawProgress = duration > 0 ? localTime / duration : 0;
  var active = localTime >= 0 && localTime <= duration;

  // 应用缓动
  var easingFn = Easing[easingName] || Easing.linear;
  var progress = active ? easingFn(Math.max(0, Math.min(1, rawProgress))) : (localTime < 0 ? 0 : 1);

  // 如果不在片段范围内且还没开始，不渲染
  if (localTime < 0) {
    return null;
  }

  // 子元素可以是函数或 ReactNode
  if (typeof children === 'function') {
    return children({ progress: progress, time: localTime, active: active });
  }

  return React.createElement('div', {
    style: { opacity: active ? 1 : 0 }
  }, children);
}
