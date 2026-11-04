import React from 'react';
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {SCENES, TOTAL_FRAMES} from './timeline';
import {MapCanvas} from './QubitMap';
import {SceneCamera} from './cinematic';

const W = 1920;
const H = 1080;
const BG = '#0B0912';
const PANEL = 'rgba(23, 17, 38, 0.92)';
const INK = '#F7F5FF';
const MUTED = '#B9B1CE';
const DIM = '#8F86A8';
const PURPLE = '#A78BFA';
const LIME = '#A3E635';
const CYAN = '#22D3EE';
const PINK = '#F472B6';
const BORDER = 'rgba(167, 139, 250, 0.30)';
const FONT = 'DejaVu Sans, Arial, sans-serif';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const enter = (frame: number, start: number, fps: number, damping = 18) =>
  spring({frame: Math.max(0, frame - start), fps, config: {damping, stiffness: 95, mass: 1}});

const sceneOpacity = (frame: number, start: number, end: number, hold = false) => {
  if (frame < start - 12 || frame > end + 12) return 0;
  if (hold) {
    return interpolate(frame, [start - 12, start + 10], [0, 1], clamp);
  }
  return interpolate(
    frame,
    [start - 12, start + 10, end - 10, end + 12],
    [0, 1, 1, 0],
    clamp,
  );
};

export const Grain = () => (
  <div
    style={{
      position: 'absolute',
      inset: 0,
      opacity: 0.055,
      pointerEvents: 'none',
      mixBlendMode: 'overlay',
      backgroundImage:
        "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.9'/%3E%3C/svg%3E\")",
      backgroundSize: '180px 180px',
    }}
  />
);

export const Vignette = () => (
  <div
    style={{
      position: 'absolute',
      inset: 0,
      pointerEvents: 'none',
      background: 'radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.62) 100%)',
    }}
  />
);

export const Background = () => {
  const frame = useCurrentFrame();
  const drift = interpolate(frame, [0, TOTAL_FRAMES], [0, -120], clamp);
  return (
    <AbsoluteFill style={{background: BG, overflow: 'hidden'}}>
      <div
        style={{
          position: 'absolute',
          width: 950,
          height: 950,
          borderRadius: 475,
          left: -320,
          top: -380,
          background: 'rgba(124, 58, 237, 0.30)',
          filter: 'blur(120px)',
          transform: `translate(${drift}px, ${-drift / 2}px)`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          width: 760,
          height: 760,
          borderRadius: 380,
          right: -280,
          bottom: -360,
          background: 'rgba(163, 230, 53, 0.12)',
          filter: 'blur(130px)',
          transform: `translate(${-drift}px, ${drift / 3}px)`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          opacity: 0.14,
          backgroundImage:
            'linear-gradient(rgba(167,139,250,0.16) 1px, transparent 1px), linear-gradient(90deg, rgba(167,139,250,0.16) 1px, transparent 1px)',
          backgroundSize: '64px 64px',
          transform: `translateY(${drift / 4}px)`,
        }}
      />
      <Vignette />
      <Grain />
    </AbsoluteFill>
  );
};

const Header = () => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, TOTAL_FRAMES], [0, 100], clamp);
  const scene = SCENES.find((item) => frame >= item.startFrame && frame < item.endFrame);
  return (
    <>
      <div style={{position: 'absolute', left: 72, top: 42, display: 'flex', gap: 18, alignItems: 'center'}}>
        <span style={{color: LIME, fontSize: 18, fontWeight: 900, letterSpacing: 4}}>QUBIT</span>
        <span style={{color: DIM, fontSize: 15, letterSpacing: 2}}>R1055 · EXPLAINER</span>
      </div>
      <div style={{position: 'absolute', right: 72, top: 42, color: MUTED, fontSize: 16}}>
        {scene ? `${scene.id} / ${String(SCENES.length).padStart(2, '0')}` : `${String(SCENES.length).padStart(2, '0')} / ${String(SCENES.length).padStart(2, '0')}`}
      </div>
      <div style={{position: 'absolute', left: 72, right: 72, top: 82, height: 4, borderRadius: 2, background: 'rgba(255,255,255,0.10)'}}>
        <div style={{width: `${progress}%`, height: 4, borderRadius: 2, background: LIME}} />
      </div>
    </>
  );
};

const Footer = () => (
  <>
    <div style={{position: 'absolute', left: 72, bottom: 34, color: DIM, fontSize: 15}}>
      Visuals originais · mapa Natural Earth · voz neural Edge
    </div>
    <div style={{position: 'absolute', right: 72, bottom: 34, color: BORDER, fontSize: 14}}>
      OpenCode Ecosystem Core · R1055
    </div>
  </>
);

export const splitSubtitle = (text: string, max = 78) => {
  if (text.length <= max) return text;
  const words = text.split(' ');
  let line = '';
  const lines: string[] = [];
  for (const word of words) {
    const candidate = `${line} ${word}`.trim();
    if (line && candidate.length > max) {
      lines.push(line);
      line = word;
    } else {
      line = candidate;
    }
  }
  if (line) lines.push(line);
  return lines.join('\n');
};

const Subtitle = () => {
  const frame = useCurrentFrame();
  const scene = SCENES.find((item) => frame >= item.startFrame && frame < item.endFrame);
  if (!scene) return null;
  if (scene.id === '07') return null;
  const caption = scene.captions.find(
    (item) => frame >= item.startFrame && frame < item.endFrame,
  );
  if (!caption) return null;
  return (
    <div
      style={{
        position: 'absolute',
        left: 210,
        right: 210,
        bottom: 92,
        padding: '18px 34px',
        borderRadius: 18,
        background: 'rgba(8, 7, 15, 0.78)',
        border: `1px solid ${BORDER}`,
        textAlign: 'center',
        color: INK,
        fontSize: 32,
        lineHeight: 1.35,
        whiteSpace: 'pre-line',
        fontFamily: FONT,
        boxShadow: '0 12px 40px rgba(0,0,0,0.35)',
      }}
    >
      {splitSubtitle(caption.text, 82)}
    </div>
  );
};

const SceneShell = ({
  index,
  children,
  hold = false,
}: {
  index: number;
  children: React.ReactNode;
  hold?: boolean;
}) => {
  const frame = useCurrentFrame();
  const scene = SCENES[index];
  const opacity = sceneOpacity(frame, scene.startFrame, scene.endFrame, hold);
  if (opacity <= 0) return null;
  const local = frame - scene.startFrame;
  const rise = interpolate(local, [0, 24], [28, 0], clamp);
  return (
    <div style={{position: 'absolute', inset: 0, opacity, transform: `translateY(${rise}px)`}}>
      {children}
    </div>
  );
};

export const BlochSphere = ({
  size = 300,
  angle = 0.8,
  color = PURPLE,
  label = '|ψ⟩',
  mixed = false,
  phase = 0,
  glow = 0.55,
  collapsed = false,
}: {
  size?: number;
  angle?: number;
  color?: string;
  label?: string;
  mixed?: boolean;
  phase?: number;
  glow?: number;
  collapsed?: boolean;
}) => {
  const cx = size / 2;
  const cy = size / 2;
  const r = size * 0.37;
  const polar = collapsed ? 0.035 : angle;
  const x = cx + Math.sin(polar) * Math.cos(phase) * r * 0.92;
  const y = cy - Math.cos(polar) * r * 0.92;
  const depth = 0.62 + 0.38 * ((Math.sin(polar) * Math.sin(phase) + 1) / 2);
  const uid = `b-${label.replace(/[^a-zA-Z0-9]/g, '')}-${Math.round(size)}`;
  const latitudes = [-0.62, -0.31, 0, 0.31, 0.62];
  const longitudes = [0, Math.PI / 3, (2 * Math.PI) / 3];
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <defs>
        <radialGradient id={`${uid}-fill`} cx="35%" cy="30%" r="72%">
          <stop offset="0%" stopColor={color} stopOpacity={0.34} />
          <stop offset="55%" stopColor={color} stopOpacity={0.10} />
          <stop offset="100%" stopColor={color} stopOpacity={0.02} />
        </radialGradient>
        <radialGradient id={`${uid}-aura`} cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor={LIME} stopOpacity={0.22 * glow} />
          <stop offset="100%" stopColor={LIME} stopOpacity={0} />
        </radialGradient>
        <filter id={`${uid}-blur`}>
          <feGaussianBlur stdDeviation={Math.max(2, size * 0.018)} />
        </filter>
      </defs>
      <circle cx={cx} cy={cy} r={r * 1.12} fill={`url(#${uid}-aura)`} />
      <circle
        cx={cx}
        cy={cy}
        r={r}
        fill={`url(#${uid}-fill)`}
        stroke={color}
        strokeOpacity={0.72}
        strokeWidth={2}
      />
      {latitudes.map((k) => {
        const rr = r * Math.sqrt(Math.max(0, 1 - k * k));
        return (
          <ellipse
            key={`lat-${k}`}
            cx={cx}
            cy={cy + k * r}
            rx={rr}
            ry={Math.max(1.5, rr * 0.18)}
            fill="none"
            stroke={color}
            strokeOpacity={0.22}
            strokeWidth={1}
          />
        );
      })}
      {longitudes.map((rotation) => (
        <ellipse
          key={`lon-${rotation}`}
          cx={cx}
          cy={cy}
          rx={Math.max(2, Math.abs(Math.cos(rotation)) * r * 0.37 + 1.5)}
          ry={r}
          fill="none"
          stroke={color}
          strokeOpacity={0.24}
          strokeWidth={1.1}
        />
      ))}
      <ellipse cx={cx} cy={cy} rx={r} ry={r * 0.36} fill="none" stroke={color} strokeOpacity={0.52} strokeWidth={1.8} />
      {mixed ? (
        <>
          <circle cx={cx} cy={cy} r={r * 0.075} fill={LIME} opacity={0.95} />
          <circle
            cx={cx}
            cy={cy}
            r={r * (0.15 + 0.02 * Math.sin(phase * 1.7))}
            fill="none"
            stroke={LIME}
            strokeOpacity={0.35}
            strokeWidth={2}
            strokeDasharray="5 7"
          />
          <circle cx={cx} cy={cy} r={r * 0.25} fill="none" stroke={LIME} strokeOpacity={0.10} strokeWidth={3} />
        </>
      ) : (
        <>
          {[0.55, 0.7, 0.85].map((t, index) => (
            <line
              key={`trail-${t}`}
              x1={cx}
              y1={cy}
              x2={cx + (x - cx) * t}
              y2={cy + (y - cy) * t}
              stroke={LIME}
              strokeWidth={2}
              strokeOpacity={0.08 + index * 0.06}
              strokeLinecap="round"
            />
          ))}
          <line
            x1={cx}
            y1={cy}
            x2={x}
            y2={y}
            stroke={LIME}
            strokeWidth={4.5}
            strokeLinecap="round"
            opacity={depth}
          />
          <circle cx={x} cy={y} r={r * 0.034} fill={LIME} filter={`url(#${uid}-blur)`} opacity={0.75} />
          <circle cx={x} cy={y} r={r * 0.022} fill={LIME} />
          <circle cx={cx} cy={cy} r={4} fill={INK} />
        </>
      )}
      <text x={cx} y={cy + r + 34} textAnchor="middle" fill={MUTED} fontSize={18} fontFamily={FONT}>
        {label}
      </text>
    </svg>
  );
};

export const CorrelationBeam = ({
  width = 520,
  height = 90,
  phase = 0,
  pulse = 0.5,
  idPrefix = 'bell',
}: {
  width?: number;
  height?: number;
  phase?: number;
  pulse?: number;
  idPrefix?: string;
}) => {
  const gradient = `${idPrefix}-gradient`;
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{overflow: 'visible'}}>
      <defs>
        <linearGradient id={gradient} x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor={PURPLE} stopOpacity={0.25} />
          <stop offset="50%" stopColor={LIME} stopOpacity={0.9} />
          <stop offset="100%" stopColor={CYAN} stopOpacity={0.25} />
        </linearGradient>
        <filter id={`${idPrefix}-glow`}>
          <feGaussianBlur stdDeviation="4" />
        </filter>
      </defs>
      <line
        x1={20}
        y1={height / 2}
        x2={width - 20}
        y2={height / 2}
        stroke={LIME}
        strokeOpacity={0.10}
        strokeWidth={14}
      />
      <line
        x1={20}
        y1={height / 2}
        x2={width - 20}
        y2={height / 2}
        stroke={`url(#${gradient})`}
        strokeWidth={4}
        strokeDasharray="10 8"
        opacity={0.66 + 0.24 * pulse}
      />
      {[0, 1, 2].map((index) => {
        const t = ((phase * 0.02 + index / 3) % 1 + 1) % 1;
        const x = 20 + (width - 40) * t;
        const alpha = 0.45 + 0.55 * (1 - Math.abs(t - 0.5) * 2);
        return (
          <g key={index}>
            <circle cx={x} cy={height / 2} r={10 + 4 * pulse} fill={LIME} opacity={0.12 * alpha} />
            <circle cx={x} cy={height / 2} r={4.5 + 1.5 * pulse} fill={LIME} opacity={alpha} />
          </g>
        );
      })}
      <circle cx={20} cy={height / 2} r={8} fill={PURPLE} />
      <circle cx={width - 20} cy={height / 2} r={8} fill={CYAN} />
    </svg>
  );
};

const SpinningCoin = ({size = 200, frame}: {size?: number; frame: number}) => {
  const angle = frame * 0.1;
  const facing = Math.sin(angle) >= 0;
  const scaleX = Math.max(0.35, Math.abs(Math.cos(angle)));
  return (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
      <div
        style={{
          width: size,
          height: size,
          borderRadius: '50%',
          transform: `scaleX(${scaleX})`,
          background: 'radial-gradient(circle at 35% 30%, #FDE68A, #D97706 68%, #92400E)',
          border: '4px solid #FCD34D',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#3B1D00',
          fontSize: size * 0.2,
          fontWeight: 900,
          letterSpacing: -1,
          boxShadow: '0 0 46px rgba(252,211,77,0.24)',
        }}
      >
        {facing ? 'CARA' : 'COROA'}
      </div>
      <div style={{color: MUTED, fontSize: 18, marginTop: 12}}>moeda girando</div>
    </div>
  );
};

const BitFlip = () => {
  const frame = useCurrentFrame();
  const value = Math.floor(frame / 14) % 2;
  return (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 18}}>
      <div
        style={{
          width: 168,
          height: 168,
          borderRadius: 24,
          border: `2px solid ${PURPLE}`,
          background: 'rgba(167,139,250,0.10)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: INK,
          fontSize: 112,
          fontWeight: 900,
          boxShadow: '0 0 40px rgba(167,139,250,0.22)',
        }}
      >
        {value}
      </div>
      <div style={{color: MUTED, fontSize: 22}}>bit clássico</div>
    </div>
  );
};

const Scene01 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const title = enter(frame, SCENES[0].startFrame, fps);
  return (
    <SceneShell index={0}>
      <SceneCamera index={0} options={{zoomTo: 1.03, panX: 4}}>
      <div style={{position: 'absolute', left: 120, top: 220, width: 820}}>
        <div style={{color: LIME, fontSize: 20, fontWeight: 800, letterSpacing: 3, marginBottom: 18}}>
          A UNIDADE DA INFORMAÇÃO QUÂNTICA
        </div>
        <div style={{color: INK, fontSize: 108, lineHeight: 0.98, fontWeight: 900, letterSpacing: -3}}>
          O que é um <span style={{color: LIME}}>qubit</span>?
        </div>
        <div style={{color: MUTED, fontSize: 34, marginTop: 30, lineHeight: 1.4}}>
          Não é um bit menor. É uma unidade de informação que obedece a outra lógica.
        </div>
        <div style={{display: 'flex', gap: 18, marginTop: 40}}>
          <div style={{padding: '12px 22px', borderRadius: 999, border: `1px solid ${BORDER}`, color: PURPLE, fontSize: 20}}>
            superposição
          </div>
          <div style={{padding: '12px 22px', borderRadius: 999, border: `1px solid ${BORDER}`, color: CYAN, fontSize: 20}}>
            medição
          </div>
          <div style={{padding: '12px 22px', borderRadius: 999, border: `1px solid ${BORDER}`, color: PINK, fontSize: 20}}>
            emaranhamento
          </div>
        </div>
      </div>
      <div
        style={{
          position: 'absolute',
          right: 150,
          top: 250,
          display: 'flex',
          alignItems: 'center',
          gap: 60,
          opacity: title,
          transform: `translateY(${(1 - title) * 24}px)`,
        }}
      >
        <BitFlip />
        <div style={{color: DIM, fontSize: 40}}>→</div>
        <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
          <BlochSphere size={300} angle={0.85} phase={frame * 0.025} glow={0.65} label="" />
          <div style={{color: MUTED, fontSize: 22, marginTop: 2}}>qubit · muito mais que 0 ou 1</div>
        </div>
      </div>
      <div style={{position: 'absolute', right: 250, top: 640, opacity: enter(frame, 240, fps)}}>
        <SpinningCoin size={160} frame={frame} />
      </div>
      </SceneCamera>
    </SceneShell>
  );
};

const Scene02 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - SCENES[1].startFrame;
  const alpha = 0.5 + 0.28 * Math.sin(local * 0.035);
  const beta = 1 - alpha;
  const grow = enter(frame, SCENES[1].startFrame, fps, 16);
  return (
    <SceneShell index={1}>
      <SceneCamera index={1} options={{zoomTo: 1.06, panX: -8}}>
      <div style={{position: 'absolute', left: 110, top: 170}}>
        <div style={{color: LIME, fontSize: 18, fontWeight: 800, letterSpacing: 3}}>02 · SUPERPOSIÇÃO</div>
        <div style={{color: INK, fontSize: 64, fontWeight: 900, marginTop: 8}}>Uma onda de possibilidades</div>
      </div>
      <div
        style={{
          position: 'absolute',
          left: 110,
          top: 300,
          width: 520,
          height: 430,
          borderRadius: 28,
          background: PANEL,
          border: `1px solid ${BORDER}`,
          padding: 34,
          opacity: grow,
          transform: `translateY(${(1 - grow) * 24}px)`,
        }}
      >
        <div style={{color: MUTED, fontSize: 20, letterSpacing: 2}}>BIT CLÁSSICO</div>
        <div style={{display: 'flex', gap: 18, marginTop: 42}}>
          {[0, 1].map((value) => (
            <div
              key={value}
              style={{
                width: 180,
                height: 180,
                borderRadius: 22,
                border: `2px solid ${PURPLE}`,
                background: 'rgba(167,139,250,0.08)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: INK,
                fontSize: 96,
                fontWeight: 900,
              }}
            >
              {value}
            </div>
          ))}
        </div>
        <div style={{color: MUTED, fontSize: 24, marginTop: 34, lineHeight: 1.4}}>
          Um estado por vez. A leitura devolve exatamente o valor armazenado.
        </div>
      </div>
      <div
        style={{
          position: 'absolute',
          left: 690,
          top: 300,
          width: 1120,
          height: 430,
          borderRadius: 28,
          background: PANEL,
          border: `1px solid ${LIME}55`,
          padding: 30,
          display: 'flex',
          gap: 30,
          opacity: grow,
          transform: `translateY(${(1 - grow) * 24}px)`,
        }}
      >
        <div style={{width: 360, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
          <BlochSphere size={330} angle={1.08 + 0.06 * Math.sin(local * 0.02)} phase={local * 0.045} glow={0.9} label="estado puro" />
        </div>
        <div style={{flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
          <div style={{color: MUTED, fontSize: 20, letterSpacing: 2}}>QUBIT</div>
          <div style={{color: INK, fontSize: 46, fontWeight: 800, marginTop: 18}}>
            |ψ⟩ = α|0⟩ + β|1⟩
          </div>
          <div style={{color: MUTED, fontSize: 23, marginTop: 18, lineHeight: 1.45}}>
            α e β são amplitudes. O módulo ao quadrado dá a probabilidade de cada resultado.
          </div>
          <div style={{marginTop: 26}}>
            {[
              {label: '|α|² · medir 0', value: alpha, color: PURPLE},
              {label: '|β|² · medir 1', value: beta, color: CYAN},
            ].map((row) => (
              <div key={row.label} style={{display: 'flex', alignItems: 'center', gap: 16, marginTop: 12}}>
                <div style={{width: 170, color: MUTED, fontSize: 18}}>{row.label}</div>
                <div style={{flex: 1, height: 16, borderRadius: 8, background: 'rgba(255,255,255,0.08)'}}>
                  <div
                    style={{
                      width: `${row.value * 100}%`,
                      height: 16,
                      borderRadius: 8,
                      background: row.color,
                      boxShadow: `0 0 16px ${row.color}77`,
                    }}
                  />
                </div>
                <div style={{width: 66, color: INK, fontSize: 18, textAlign: 'right'}}>
                  {(row.value * 100).toFixed(0)}%
                </div>
              </div>
            ))}
          </div>
          <div style={{color: DIM, fontSize: 18, marginTop: 18}}>
            |α|² + |β|² = 1 · a norma se conserva
          </div>
        </div>
      </div>
      </SceneCamera>
    </SceneShell>
  );
};

export const wavePath = (width: number, height: number, amplitude: number, phase: number, cycles = 3) => {
  const points: string[] = [];
  for (let i = 0; i <= 120; i += 1) {
    const x = (i / 120) * width;
    const y = height / 2 + Math.sin((i / 120) * Math.PI * 2 * cycles + phase) * amplitude;
    points.push(`${i === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`);
  }
  return points.join(' ');
};

const Scene03 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - SCENES[2].startFrame;
  const duration = SCENES[2].endFrame - SCENES[2].startFrame;
  const collapse = interpolate(local, [duration * 0.45, duration * 0.65], [0, 1], clamp);
  const amplitude = 90 * (1 - collapse);
  const flash = interpolate(local, [duration * 0.60, duration * 0.66, duration * 0.75], [0, 1, 0], clamp);
  const grow = enter(frame, SCENES[2].startFrame, fps, 16);
  return (
    <SceneShell index={2}>
      <SceneCamera index={2} options={{zoomTo: 1.04, focusAt: SCENES[2].captions[2]?.startFrame, focusZoom: 1.09, shakeAt: SCENES[2].captions[2]?.startFrame, shakeAmount: 6}}>
      <div style={{position: 'absolute', left: 110, top: 170}}>
        <div style={{color: LIME, fontSize: 18, fontWeight: 800, letterSpacing: 3}}>03 · MEDIÇÃO</div>
        <div style={{color: INK, fontSize: 64, fontWeight: 900, marginTop: 8}}>A onda vira um resultado</div>
      </div>
      <div
        style={{
          position: 'absolute',
          left: 110,
          top: 290,
          width: 760,
          height: 400,
          borderRadius: 28,
          background: PANEL,
          border: `1px solid ${BORDER}`,
          padding: 30,
          opacity: grow,
          transform: `translateY(${(1 - grow) * 24}px)`,
        }}
      >
        <div style={{color: MUTED, fontSize: 20, letterSpacing: 2}}>EVOLUÇÃO DA ONDA</div>
        <svg width={700} height={260} viewBox="0 0 700 260">
          <line x1={0} y1={130} x2={700} y2={130} stroke="rgba(255,255,255,0.14)" strokeWidth={1} />
          <path
            d={wavePath(700, 260, amplitude, local * 0.04)}
            fill="none"
            stroke={PURPLE}
            strokeWidth={4}
            strokeLinecap="round"
          />
        </svg>
        <div style={{display: 'flex', justifyContent: 'space-between', color: DIM, fontSize: 18}}>
          <span>ψ(x)</span>
          <span>evolução unitária · portas quânticas</span>
        </div>
      </div>
      <div
        style={{
          position: 'absolute',
          left: 930,
          top: 290,
          width: 880,
          height: 410,
          borderRadius: 28,
          background: PANEL,
          border: `1px solid ${LIME}55`,
          padding: 30,
          opacity: grow,
          transform: `translateY(${(1 - grow) * 24}px)`,
          boxShadow: `0 0 ${80 * flash}px rgba(163,230,53,${0.35 * flash})`,
        }}
      >
        <div style={{color: MUTED, fontSize: 20, letterSpacing: 2}}>DEPOIS DA MEDIÇÃO</div>
        <div style={{display: 'flex', alignItems: 'center', gap: 26, marginTop: 26}}>
          <div
            style={{
              width: 120,
              height: 120,
              borderRadius: 22,
              border: `2px solid ${LIME}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: LIME,
              fontSize: 48,
              fontWeight: 900,
            }}
          >
            M
          </div>
          <div style={{color: MUTED, fontSize: 22, lineHeight: 1.4, flex: 1}}>
            A medição não revela um valor escondido: ela seleciona um resultado com probabilidade |α|² ou |β|².
          </div>
        </div>
        <div style={{display: 'flex', gap: 20, marginTop: 34}}>
          {[
            {label: '0', active: collapse > 0.65, color: PURPLE},
            {label: '1', active: collapse <= 0.65, color: CYAN},
          ].map((row) => (
            <div
              key={row.label}
              style={{
                flex: 1,
                padding: '22px 0',
                borderRadius: 18,
                border: `2px solid ${row.active ? row.color : 'rgba(255,255,255,0.10)'}`,
                background: row.active ? `${row.color}22` : 'transparent',
                textAlign: 'center',
                color: row.active ? INK : DIM,
                fontSize: 54,
                fontWeight: 900,
              }}
            >
              {row.label}
            </div>
          ))}
        </div>
        <div style={{color: DIM, fontSize: 18, marginTop: 22}}>
          colapso: um resultado clássico, não uma cópia da superposição
        </div>
      </div>
      <div style={{position: 'absolute', left: 110, top: 705, width: 960, display: 'flex', alignItems: 'center', gap: 22, opacity: enter(frame, SCENES[2].captions[3]?.startFrame ?? SCENES[2].startFrame, fps)}}>
        <BlochSphere size={145} angle={1.02} phase={local * 0.05} glow={0.75} label="" />
        <div style={{flex: 1}}>
          <div style={{color: LIME, fontSize: 17, fontWeight: 800, letterSpacing: 2}}>ESFERA DE BLOCH</div>
          <div style={{color: MUTED, fontSize: 19, lineHeight: 1.4, marginTop: 4}}>
            As portas quânticas são rotações. A medição projeta o vetor em 0 ou 1.
          </div>
        </div>
      </div>
      <div style={{position: 'absolute', inset: 0, background: 'rgba(163,230,53,0.10)', opacity: flash, pointerEvents: 'none'}} />
      </SceneCamera>
    </SceneShell>
  );
};

const Scene04 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - SCENES[3].startFrame;
  const grow = enter(frame, SCENES[3].startFrame, fps, 16);
  const pulse = 0.5 + 0.5 * Math.sin(local * 0.08);
  return (
    <SceneShell index={3}>
      <SceneCamera index={3} options={{zoomTo: 1.07, focusAt: SCENES[3].captions[1]?.startFrame, focusZoom: 1.08, panX: 8}}>
      <div style={{position: 'absolute', left: 110, top: 170}}>
        <div style={{color: PINK, fontSize: 18, fontWeight: 800, letterSpacing: 3}}>04 · EMARANHAMENTO</div>
        <div style={{color: INK, fontSize: 64, fontWeight: 900, marginTop: 8}}>Duas partes, um só estado</div>
      </div>
      <div
        style={{
          position: 'absolute',
          left: 110,
          top: 300,
          width: 1700,
          height: 470,
          borderRadius: 30,
          background: PANEL,
          border: `1px solid ${PINK}55`,
          padding: 30,
          opacity: grow,
          transform: `translateY(${(1 - grow) * 24}px)`,
        }}
      >
        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
          <div style={{width: 420, textAlign: 'center'}}>
            <BlochSphere size={300} mixed phase={local * 0.03} glow={0.55 + 0.35 * pulse} color={PURPLE} label="qubit A · misto" />
          </div>
          <div style={{flex: 1, textAlign: 'center'}}>
            <div style={{color: MUTED, fontSize: 20, letterSpacing: 2}}>ESTADO DE BELL</div>
            <div style={{color: INK, fontSize: 42, fontWeight: 800, marginTop: 8}}>
              (|00⟩ + |11⟩) / √2
            </div>
            <div style={{display: 'flex', justifyContent: 'center', marginTop: 8}}>
              <CorrelationBeam width={520} height={90} phase={local * 0.05} pulse={pulse} idPrefix="bell16" />
            </div>
            <div style={{display: 'flex', justifyContent: 'center', gap: 18, marginTop: 14}}>
              <div style={{padding: '10px 18px', borderRadius: 999, border: `1px solid ${BORDER}`, color: MUTED, fontSize: 18}}>0 ↔ 0</div>
              <div style={{padding: '10px 18px', borderRadius: 999, border: `1px solid ${BORDER}`, color: MUTED, fontSize: 18}}>1 ↔ 1</div>
            </div>
            <div style={{color: MUTED, fontSize: 21, marginTop: 20, lineHeight: 1.4}}>
              Correlações que nenhuma teoria clássica local reproduz.
            </div>
          </div>
          <div style={{width: 420, textAlign: 'center'}}>
            <BlochSphere size={300} mixed phase={-local * 0.03} glow={0.55 + 0.35 * pulse} color={CYAN} label="qubit B · misto" />
          </div>
        </div>
      </div>
      <div
        style={{
          position: 'absolute',
          left: 110,
          top: 800,
          display: 'flex',
          alignItems: 'center',
          gap: 24,
          opacity: grow,
        }}
      >
        <div style={{padding: '10px 20px', borderRadius: 999, background: LIME, color: BG, fontSize: 18, fontWeight: 900, letterSpacing: 2}}>
          NOBEL 2022
        </div>
        <div style={{color: MUTED, fontSize: 24}}>Aspect · Clauser · Zeilinger</div>
        <div style={{color: DIM, fontSize: 18}}>testes de Bell com fótons emaranhados</div>
      </div>
      </SceneCamera>
    </SceneShell>
  );
};

const Scene05 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - SCENES[4].startFrame;
  const grow = enter(frame, SCENES[4].startFrame, fps, 16);
  const noise = interpolate(local, [0, 100, 240], [0, 0.3, 0.9], clamp);
  const interferenceCue = SCENES[4].captions[1]?.startFrame ?? SCENES[4].startFrame;
  const wavePhase = local * (frame >= interferenceCue ? 0.065 : 0.04);
  const cursorX = (local * 3.6) % 1020;
  const cursorY = 165 + Math.sin((cursorX / 1020) * Math.PI * 2 * 5 + wavePhase + Math.PI / 2) * 20;
  return (
    <SceneShell index={4}>
      <SceneCamera index={4} options={{zoomTo: 1.07, focusAt: SCENES[4].captions[1]?.startFrame, focusZoom: 1.08, panX: -8}}>
      <div style={{position: 'absolute', left: 110, top: 170}}>
        <div style={{color: CYAN, fontSize: 18, fontWeight: 800, letterSpacing: 3}}>05 · INTERFERÊNCIA E LIMITE</div>
        <div style={{color: INK, fontSize: 64, fontWeight: 900, marginTop: 8}}>O ganho não é força bruta</div>
      </div>
      <div
        style={{
          position: 'absolute',
          left: 110,
          top: 300,
          width: 1080,
          height: 470,
          borderRadius: 28,
          background: PANEL,
          border: `1px solid ${BORDER}`,
          padding: 28,
          opacity: grow,
          transform: `translateY(${(1 - grow) * 24}px)`,
        }}
      >
        <div style={{color: MUTED, fontSize: 20, letterSpacing: 2}}>AMPLITUDES SE SOMAM</div>
        <svg width={1020} height={330} viewBox="0 0 1020 330">
          <defs>
            <filter id="r1055-wave-glow">
              <feGaussianBlur stdDeviation="5" />
            </filter>
          </defs>
          <line x1={0} y1={165} x2={1020} y2={165} stroke="rgba(255,255,255,0.12)" strokeWidth={1} />
          <path d={wavePath(1020, 330, 70, wavePhase)} fill="none" stroke={PURPLE} strokeWidth={3} opacity={0.8} />
          <path d={wavePath(1020, 330, 70, wavePhase + Math.PI)} fill="none" stroke={CYAN} strokeWidth={3} opacity={0.8} />
          <path d={wavePath(1020, 330, 20, wavePhase + Math.PI / 2)} fill="none" stroke={LIME} strokeWidth={5} filter="url(#r1055-wave-glow)" opacity={0.7} />
          <path d={wavePath(1020, 330, 20, wavePhase + Math.PI / 2)} fill="none" stroke={LIME} strokeWidth={3} />
          <line x1={cursorX} y1={40} x2={cursorX} y2={290} stroke={LIME} strokeOpacity={0.14} strokeWidth={2} />
          <circle cx={cursorX} cy={cursorY} r={7} fill={LIME} filter="url(#r1055-wave-glow)" />
          <circle cx={cursorX} cy={cursorY} r={4} fill={INK} />
        </svg>
        <div style={{display: 'flex', gap: 26, color: MUTED, fontSize: 19}}>
          <span style={{color: PURPLE}}>caminho A</span>
          <span style={{color: CYAN}}>caminho B</span>
          <span style={{color: LIME}}>resultado: interferência</span>
        </div>
      </div>
      <div
        style={{
          position: 'absolute',
          left: 1230,
          top: 300,
          width: 580,
          height: 470,
          borderRadius: 28,
          background: PANEL,
          border: `1px solid ${PINK}55`,
          padding: 30,
          opacity: grow,
          transform: `translateY(${(1 - grow) * 24}px)`,
        }}
      >
        <div style={{color: PINK, fontSize: 20, fontWeight: 800, letterSpacing: 2}}>O INIMIGO</div>
        <div style={{color: INK, fontSize: 40, fontWeight: 800, marginTop: 10}}>Decoerência</div>
        <div style={{height: 14, borderRadius: 7, background: 'rgba(255,255,255,0.08)', marginTop: 26}}>
          <div style={{width: `${noise * 100}%`, height: 14, borderRadius: 7, background: PINK, boxShadow: `0 0 ${18 * noise}px ${PINK}88`}} />
        </div>
        <div style={{color: MUTED, fontSize: 21, marginTop: 18, lineHeight: 1.45}}>
          O ambiente “mede” o qubit e apaga a fase. Por isso um qubit lógico exige muitos qubits físicos e correção de erro.
        </div>
        <div style={{marginTop: 30, padding: 20, borderRadius: 18, border: `1px solid ${LIME}55`, background: 'rgba(163,230,53,0.06)'}}>
          <div style={{color: LIME, fontSize: 26, fontWeight: 800}}>1 qubit lógico ≠ 1 qubit físico</div>
          <div style={{color: DIM, fontSize: 18, marginTop: 8}}>a correção de erro é parte do computador, não um detalhe</div>
        </div>
      </div>
      </SceneCamera>
    </SceneShell>
  );
};

const Scene06 = () => (
  <SceneShell index={5} hold>
    <MapCanvas />
  </SceneShell>
);

const Scene07 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const grow = enter(frame, SCENES[6].startFrame, fps, 20);
  return (
    <SceneShell index={6} hold>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 70,
          padding: '90px 120px',
        }}
      >
        <div style={{width: 430, textAlign: 'center', opacity: grow}}>
          <Img
            src={staticFile('r1055-author.png')}
            style={{
              width: 300,
              height: 300,
              borderRadius: 150,
              objectFit: 'cover',
              border: `4px solid ${LIME}`,
              boxShadow: '0 0 70px rgba(163,230,53,0.28)',
            }}
          />
          <div style={{color: LIME, fontSize: 18, fontWeight: 800, letterSpacing: 3, marginTop: 22}}>AUTOR</div>
          <div style={{color: INK, fontSize: 44, fontWeight: 900, lineHeight: 1.05, marginTop: 8}}>
            Marcelo Claro<br />Laranjeira
          </div>
          <div style={{color: MUTED, fontSize: 20, lineHeight: 1.45, marginTop: 14}}>
            Professor · Mochileiro · Pedagogo<br />
            Mestrado em Ciência da Educação<br />
            Entusiasta em Tecnologia
          </div>
        </div>
        <div style={{flex: 1, opacity: grow}}>
          <div style={{color: INK, fontSize: 64, fontWeight: 900, lineHeight: 1.05}}>
            Obrigado por<br /><span style={{color: LIME}}>assistir.</span>
          </div>
          <div style={{color: MUTED, fontSize: 24, lineHeight: 1.5, marginTop: 18}}>
            IA e Computação Quântica para educação básica.
          </div>
          <div style={{display: 'flex', gap: 34, alignItems: 'center', marginTop: 28}}>
            <div style={{background: INK, padding: 12, borderRadius: 16}}>
              <Img
                src={staticFile('r1055-github-qr.png')}
                style={{width: 250, height: 250, display: 'block'}}
              />
            </div>
            <div>
              <div style={{color: LIME, fontSize: 18, fontWeight: 800, letterSpacing: 2}}>GITHUB</div>
              <div style={{color: INK, fontSize: 26, fontWeight: 700, marginTop: 4}}>
                github.com/MarceloClaro
              </div>
              <div style={{color: MUTED, fontSize: 19, lineHeight: 1.6, marginTop: 12}}>
                ORCID: 0000-0001-8996-2887<br />
                Instagram: @marceloclaro.geomaker<br />
                bit.ly/geomaker
              </div>
            </div>
          </div>
          <div style={{color: DIM, fontSize: 16, marginTop: 18}}>
            Aponte a câmera para o QR code e acompanhe o projeto.
          </div>
        </div>
      </div>
    </SceneShell>
  );
};

export const QubitExplainer = () => {
  return (
    <AbsoluteFill style={{background: BG, color: INK, fontFamily: FONT, overflow: 'hidden'}}>
      <Background />
      <Scene01 />
      <Scene02 />
      <Scene03 />
      <Scene04 />
      <Scene05 />
      <Scene06 />
      <Scene07 />
      <Subtitle />
      <Header />
      <Footer />
    </AbsoluteFill>
  );
};
