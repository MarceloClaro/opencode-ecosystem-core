import React from 'react';
import {AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {SCENES, TOTAL_FRAMES} from './timeline';
import {MapCanvas} from './QubitMap';
import {SceneCamera} from './cinematic';
import {Background, BlochSphere, splitSubtitle, wavePath} from './QubitExplainer';

const W = 1080;
const H = 1920;
const INK = '#F7F5FF';
const MUTED = '#B9B1CE';
const DIM = '#8F86A8';
const PURPLE = '#A78BFA';
const LIME = '#A3E635';
const CYAN = '#22D3EE';
const PINK = '#F472B6';
const PANEL = 'rgba(23, 17, 38, 0.94)';
const BORDER = 'rgba(167, 139, 250, 0.30)';
const FONT = 'DejaVu Sans, Arial, sans-serif';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const enter = (frame: number, start: number, fps: number, damping = 18) =>
  spring({frame: Math.max(0, frame - start), fps, config: {damping, stiffness: 95, mass: 1}});

const fade = (frame: number, start: number, end: number, hold = false) => {
  if (frame < start - 10 || frame > end + 10) return 0;
  if (hold) return interpolate(frame, [start - 10, start + 8], [0, 1], clamp);
  return interpolate(frame, [start - 10, start + 8, end - 8, end + 10], [0, 1, 1, 0], clamp);
};

const Header = () => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, TOTAL_FRAMES], [0, 100], clamp);
  return (
    <>
      <div style={{position: 'absolute', left: 54, top: 44, color: LIME, fontSize: 18, fontWeight: 900, letterSpacing: 4}}>
        QUBIT
      </div>
      <div style={{position: 'absolute', left: 176, top: 46, color: DIM, fontSize: 14, letterSpacing: 2}}>
        R1055 · 9:16
      </div>
      <div style={{position: 'absolute', right: 54, top: 46, color: MUTED, fontSize: 14}}>
        {Math.round(progress)}%
      </div>
      <div style={{position: 'absolute', left: 54, right: 54, top: 86, height: 4, borderRadius: 2, background: 'rgba(255,255,255,0.10)'}}>
        <div style={{width: `${progress}%`, height: 4, borderRadius: 2, background: LIME}} />
      </div>
    </>
  );
};

const Footer = () => (
  <>
    <div style={{position: 'absolute', left: 54, bottom: 34, color: DIM, fontSize: 13}}>
      Voz neural Edge · mapa Natural Earth
    </div>
    <div style={{position: 'absolute', right: 54, bottom: 34, color: BORDER, fontSize: 12}}>
      OpenCode Ecosystem Core
    </div>
  </>
);

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
        left: 50,
        right: 50,
        bottom: 118,
        padding: '18px 26px',
        borderRadius: 16,
        background: 'rgba(8, 7, 15, 0.82)',
        border: `1px solid ${BORDER}`,
        textAlign: 'center',
        color: INK,
        fontSize: 32,
        lineHeight: 1.34,
        whiteSpace: 'pre-line',
        fontFamily: FONT,
      }}
    >
      {splitSubtitle(caption.text, 50)}
    </div>
  );
};

const SceneWrap = ({index, children, hold = false}: {index: number; children: React.ReactNode; hold?: boolean}) => {
  const frame = useCurrentFrame();
  const scene = SCENES[index];
  const opacity = fade(frame, scene.startFrame, scene.endFrame, hold);
  if (opacity <= 0) return null;
  const local = frame - scene.startFrame;
  const rise = interpolate(local, [0, 22], [24, 0], clamp);
  return <div style={{position: 'absolute', inset: 0, opacity, transform: `translateY(${rise}px)`}}>{children}</div>;
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
      <div style={{color: MUTED, fontSize: 17, marginTop: 10}}>moeda girando</div>
    </div>
  );
};

const Label = ({text, color = LIME}: {text: string; color?: string}) => (
  <div style={{color, fontSize: 17, fontWeight: 800, letterSpacing: 3, marginBottom: 10}}>{text}</div>
);

const Title = ({children, size = 68}: {children: React.ReactNode; size?: number}) => (
  <div style={{color: INK, fontSize: size, lineHeight: 1.04, fontWeight: 900, letterSpacing: -1.5}}>{children}</div>
);

const Body = ({children, size = 27, color = MUTED}: {children: React.ReactNode; size?: number; color?: string}) => (
  <div style={{color, fontSize: size, lineHeight: 1.45, marginTop: 16}}>{children}</div>
);

const Pill = ({text, color = MUTED}: {text: string; color?: string}) => (
  <div style={{padding: '8px 14px', borderRadius: 999, border: `1px solid ${BORDER}`, color, fontSize: 17, display: 'inline-block', marginRight: 8, marginTop: 10}}>
    {text}
  </div>
);

const VScene01 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const grow = enter(frame, SCENES[0].startFrame, fps);
  const value = Math.floor(frame / 14) % 2;
  return (
    <SceneWrap index={0}>
      <SceneCamera index={0} options={{zoomTo: 1.03, panY: 4}}>
      <div style={{position: 'absolute', left: 54, top: 140, width: 972, opacity: grow}}>
        <Label text="A UNIDADE DA INFORMAÇÃO QUÂNTICA" />
        <Title size={82}>
          O que é um <span style={{color: LIME}}>qubit</span>?
        </Title>
        <Body size={29}>Não é um bit menor. É uma unidade de informação que obedece a outra lógica.</Body>
      </div>
      <div style={{position: 'absolute', left: 90, top: 520, width: 900, display: 'flex', alignItems: 'center', gap: 36, opacity: grow}}>
        <div style={{textAlign: 'center'}}>
          <div style={{width: 150, height: 150, borderRadius: 20, border: `2px solid ${PURPLE}`, background: 'rgba(167,139,250,0.10)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: INK, fontSize: 96, fontWeight: 900}}>
            {value}
          </div>
          <div style={{color: MUTED, fontSize: 18, marginTop: 10}}>bit clássico</div>
        </div>
        <div style={{color: DIM, fontSize: 34}}>→</div>
        <div style={{textAlign: 'center'}}>
          <BlochSphere size={270} angle={0.85} phase={frame * 0.025} glow={0.65} label="" />
          <div style={{color: MUTED, fontSize: 18, marginTop: 2}}>qubit · muito mais que 0 ou 1</div>
        </div>
      </div>
      <div style={{position: 'absolute', left: 54, top: 1000, width: 972, opacity: grow}}>
        <Body size={22} color={DIM}>superposição · medição · emaranhamento · interferência</Body>
      </div>
      <div style={{position: 'absolute', left: 54, top: 1100, width: 972, display: 'flex', alignItems: 'center', gap: 28, opacity: enter(frame, 240, fps)}}>
        <SpinningCoin size={210} frame={frame} />
        <div style={{flex: 1}}>
          <div style={{color: LIME, fontSize: 17, fontWeight: 800, letterSpacing: 2}}>ANALOGIA</div>
          <Body size={22}>Enquanto gira, a moeda não é cara nem coroa: é as duas possibilidades. Só ao parar você vê um resultado.</Body>
        </div>
      </div>
      </SceneCamera>
    </SceneWrap>
  );
};

const VScene02 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - SCENES[1].startFrame;
  const alpha = 0.5 + 0.28 * Math.sin(local * 0.035);
  const beta = 1 - alpha;
  const grow = enter(frame, SCENES[1].startFrame, fps, 16);
  return (
    <SceneWrap index={1}>
      <SceneCamera index={1} options={{zoomTo: 1.045, panY: -4}}>
      <div style={{position: 'absolute', left: 54, top: 140, width: 972, opacity: grow}}>
        <Label text="02 · SUPERPOSIÇÃO" />
        <Title size={56}>Uma onda de possibilidades</Title>
        <div style={{color: INK, fontSize: 42, fontWeight: 800, marginTop: 22}}>|ψ⟩ = α|0⟩ + β|1⟩</div>
      </div>
      <div style={{position: 'absolute', left: 340, top: 360, opacity: grow}}>
        <BlochSphere size={400} angle={0.9 + 0.06 * Math.sin(local * 0.02)} phase={local * 0.04} glow={0.85} label="estado puro" />
      </div>
      <div style={{position: 'absolute', left: 54, top: 790, width: 972, opacity: grow}}>
        {[
          {label: '|α|² · medir 0', value: alpha, color: PURPLE},
          {label: '|β|² · medir 1', value: beta, color: CYAN},
        ].map((row) => (
          <div key={row.label} style={{display: 'flex', alignItems: 'center', gap: 14, marginTop: 14}}>
            <div style={{width: 180, color: MUTED, fontSize: 18}}>{row.label}</div>
            <div style={{flex: 1, height: 18, borderRadius: 9, background: 'rgba(255,255,255,0.08)'}}>
              <div style={{width: `${row.value * 100}%`, height: 18, borderRadius: 9, background: row.color}} />
            </div>
            <div style={{width: 60, color: INK, fontSize: 18, textAlign: 'right'}}>{(row.value * 100).toFixed(0)}%</div>
          </div>
        ))}
        <Body size={22} color={DIM}>|α|² + |β|² = 1 · a norma se conserva</Body>
        <div style={{marginTop: 22, padding: 18, borderRadius: 16, border: `1px solid ${BORDER}`, background: PANEL}}>
          <Body size={21} color={MUTED}>Antes de medir, o qubit evolui como onda. A medição devolve um resultado clássico, não uma cópia da superposição.</Body>
        </div>
      </div>
      </SceneCamera>
    </SceneWrap>
  );
};

const VScene03 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - SCENES[2].startFrame;
  const duration = SCENES[2].endFrame - SCENES[2].startFrame;
  const collapse = interpolate(local, [duration * 0.45, duration * 0.65], [0, 1], clamp);
  const amplitude = 70 * (1 - collapse);
  const flash = interpolate(local, [duration * 0.60, duration * 0.66, duration * 0.75], [0, 1, 0], clamp);
  const grow = enter(frame, SCENES[2].startFrame, fps, 16);
  return (
    <SceneWrap index={2}>
      <SceneCamera index={2} options={{zoomTo: 1.03, focusAt: SCENES[2].captions[2]?.startFrame, focusZoom: 1.07, shakeAt: SCENES[2].captions[2]?.startFrame, shakeAmount: 5}}>
      <div style={{position: 'absolute', left: 54, top: 140, width: 972, opacity: grow}}>
        <Label text="03 · MEDIÇÃO" />
        <Title size={56}>A onda vira um resultado</Title>
      </div>
      <div style={{position: 'absolute', left: 54, top: 350, width: 972, height: 330, borderRadius: 24, background: PANEL, border: `1px solid ${BORDER}`, padding: 20, opacity: grow}}>
        <div style={{color: MUTED, fontSize: 17, letterSpacing: 2}}>EVOLUÇÃO DA ONDA</div>
        <svg width={930} height={240} viewBox="0 0 930 240">
          <line x1={0} y1={120} x2={930} y2={120} stroke="rgba(255,255,255,0.14)" strokeWidth={1} />
          <path d={wavePath(930, 240, amplitude, local * 0.04)} fill="none" stroke={PURPLE} strokeWidth={4} strokeLinecap="round" />
        </svg>
        <div style={{display: 'flex', justifyContent: 'space-between', color: DIM, fontSize: 16}}>
          <span>ψ(x)</span>
          <span>evolução unitária</span>
        </div>
      </div>
      <div style={{position: 'absolute', left: 54, top: 720, width: 972, borderRadius: 24, background: PANEL, border: `1px solid ${LIME}55`, padding: 22, opacity: grow}}>
        <div style={{color: MUTED, fontSize: 17, letterSpacing: 2}}>DEPOIS DA MEDIÇÃO</div>
        <div style={{display: 'flex', alignItems: 'center', gap: 20, marginTop: 16}}>
          <div style={{width: 100, height: 100, borderRadius: 18, border: `2px solid ${LIME}`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: LIME, fontSize: 40, fontWeight: 900}}>M</div>
          <Body size={21} color={MUTED}>A medição seleciona 0 ou 1 com probabilidade |α|² ou |β|².</Body>
        </div>
        <div style={{display: 'flex', gap: 14, marginTop: 20}}>
          {['0', '1'].map((label, index) => (
            <div key={label} style={{flex: 1, padding: '14px 0', borderRadius: 14, border: `2px solid ${(index === 0 ? collapse > 0.65 : collapse <= 0.65) ? (index === 0 ? PURPLE : CYAN) : 'rgba(255,255,255,0.10)'}`, textAlign: 'center', color: INK, fontSize: 40, fontWeight: 900}}>
              {label}
            </div>
          ))}
        </div>
      </div>
      <div style={{position: 'absolute', left: 54, top: 1035, width: 972, display: 'flex', alignItems: 'center', gap: 26, opacity: grow}}>
        <BlochSphere size={280} angle={0.85} phase={local * 0.035} glow={0.7} label="porta = rotação" />
        <div style={{flex: 1}}>
          <div style={{color: LIME, fontSize: 17, fontWeight: 800, letterSpacing: 2}}>ESFERA DE BLOCH</div>
          <Body size={21}>Cada porta quântica gira o vetor de estado. A medição projeta esse vetor em 0 ou 1.</Body>
        </div>
      </div>
      <div style={{position: 'absolute', left: 54, top: 1350, width: 972, opacity: grow}}>
        <Body size={20} color={DIM}>colapso: um resultado clássico, não uma cópia da superposição</Body>
      </div>
      <div style={{position: 'absolute', inset: 0, background: 'rgba(163,230,53,0.10)', opacity: flash, pointerEvents: 'none'}} />
      </SceneCamera>
    </SceneWrap>
  );
};

const VScene04 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - SCENES[3].startFrame;
  const grow = enter(frame, SCENES[3].startFrame, fps, 16);
  const pulse = 0.5 + 0.5 * Math.sin(local * 0.08);
  return (
    <SceneWrap index={3}>
      <SceneCamera index={3} options={{zoomTo: 1.04, focusAt: SCENES[3].captions[1]?.startFrame, focusZoom: 1.055, panY: 4}}>
      <div style={{position: 'absolute', left: 54, top: 140, width: 972, opacity: grow}}>
        <Label text="04 · EMARANHAMENTO" color={PINK} />
        <Title size={56}>Duas partes, um só estado</Title>
        <div style={{color: INK, fontSize: 38, fontWeight: 800, marginTop: 18}}>(|00⟩ + |11⟩) / √2</div>
      </div>
      <div style={{position: 'absolute', left: 70, top: 370, width: 400, textAlign: 'center', opacity: grow}}>
        <BlochSphere size={280} mixed phase={local * 0.03} glow={0.6} color={PURPLE} label="qubit A · misto" />
      </div>
      <div style={{position: 'absolute', left: 610, top: 370, width: 400, textAlign: 'center', opacity: grow}}>
        <BlochSphere size={280} mixed phase={-local * 0.03} glow={0.6} color={CYAN} label="qubit B · misto" />
      </div>
      <div style={{position: 'absolute', left: 54, top: 710, width: 972, opacity: grow}}>
        <div style={{display: 'flex', justifyContent: 'center', gap: 14}}>
          <Pill text="0 ↔ 0" />
          <Pill text="1 ↔ 1" />
        </div>
        <Body size={21}>Correlações que nenhuma teoria clássica local reproduz.</Body>
        <div style={{marginTop: 20, display: 'flex', alignItems: 'center', gap: 16}}>
          <div style={{padding: '8px 16px', borderRadius: 999, background: LIME, color: '#0B0912', fontSize: 17, fontWeight: 900, letterSpacing: 2}}>NOBEL 2022</div>
          <div style={{color: MUTED, fontSize: 20}}>Aspect · Clauser · Zeilinger</div>
        </div>
      </div>
      <div style={{position: 'absolute', left: 54, top: 1180, width: 972, padding: '20px 24px', borderRadius: 18, background: PANEL, border: `1px solid ${PINK}44`, opacity: grow}}>
        <div style={{color: PINK, fontSize: 17, fontWeight: 800, letterSpacing: 2}}>O QUE O EMARANHAMENTO NÃO É</div>
        <Body size={21}>Não é um sinal mais rápido que a luz. A correlação só aparece quando os resultados são comparados.</Body>
      </div>
      </SceneCamera>
    </SceneWrap>
  );
};

const VScene05 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - SCENES[4].startFrame;
  const grow = enter(frame, SCENES[4].startFrame, fps, 16);
  const noise = interpolate(local, [0, 100, 240], [0, 0.3, 0.9], clamp);
  const interferenceCue = SCENES[4].captions[1]?.startFrame ?? SCENES[4].startFrame;
  const wavePhase = local * (frame >= interferenceCue ? 0.065 : 0.04);
  const cursorX = (local * 3.2) % 930;
  const cursorY = 120 + Math.sin((cursorX / 930) * Math.PI * 2 * 5 + wavePhase + Math.PI / 2) * 18;
  return (
    <SceneWrap index={4}>
      <SceneCamera index={4} options={{zoomTo: 1.04, focusAt: SCENES[4].captions[1]?.startFrame, focusZoom: 1.06, panY: -4}}>
      <div style={{position: 'absolute', left: 54, top: 140, width: 972, opacity: grow}}>
        <Label text="05 · INTERFERÊNCIA E LIMITE" color={CYAN} />
        <Title size={56}>O ganho não é força bruta</Title>
      </div>
      <div style={{position: 'absolute', left: 54, top: 340, width: 972, height: 330, borderRadius: 24, background: PANEL, border: `1px solid ${BORDER}`, padding: 20, opacity: grow}}>
        <div style={{color: MUTED, fontSize: 17, letterSpacing: 2}}>AMPLITUDES SE SOMAM</div>
        <svg width={930} height={240} viewBox="0 0 930 240">
          <defs>
            <filter id="r1055-wave-glow-v">
              <feGaussianBlur stdDeviation="5" />
            </filter>
          </defs>
          <line x1={0} y1={120} x2={930} y2={120} stroke="rgba(255,255,255,0.12)" strokeWidth={1} />
          <path d={wavePath(930, 240, 60, wavePhase)} fill="none" stroke={PURPLE} strokeWidth={3} opacity={0.8} />
          <path d={wavePath(930, 240, 60, wavePhase + Math.PI)} fill="none" stroke={CYAN} strokeWidth={3} opacity={0.8} />
          <path d={wavePath(930, 240, 18, wavePhase + Math.PI / 2)} fill="none" stroke={LIME} strokeWidth={5} filter="url(#r1055-wave-glow-v)" opacity={0.7} />
          <path d={wavePath(930, 240, 18, wavePhase + Math.PI / 2)} fill="none" stroke={LIME} strokeWidth={3} />
          <line x1={cursorX} y1={30} x2={cursorX} y2={210} stroke={LIME} strokeOpacity={0.14} strokeWidth={2} />
          <circle cx={cursorX} cy={cursorY} r={6} fill={LIME} filter="url(#r1055-wave-glow-v)" />
          <circle cx={cursorX} cy={cursorY} r={3.5} fill={INK} />
        </svg>
        <div style={{display: 'flex', gap: 20, color: MUTED, fontSize: 17}}>
          <span style={{color: PURPLE}}>caminho A</span>
          <span style={{color: CYAN}}>caminho B</span>
          <span style={{color: LIME}}>interferência</span>
        </div>
      </div>
      <div style={{position: 'absolute', left: 54, top: 710, width: 972, borderRadius: 24, background: PANEL, border: `1px solid ${PINK}55`, padding: 22, opacity: grow}}>
        <div style={{color: PINK, fontSize: 18, fontWeight: 800, letterSpacing: 2}}>O INIMIGO</div>
        <div style={{color: INK, fontSize: 40, fontWeight: 800, marginTop: 8}}>Decoerência</div>
        <div style={{height: 14, borderRadius: 7, background: 'rgba(255,255,255,0.08)', marginTop: 18}}>
          <div style={{width: `${noise * 100}%`, height: 14, borderRadius: 7, background: PINK, boxShadow: `0 0 ${18 * noise}px ${PINK}88`}} />
        </div>
        <Body size={21}>O ambiente “mede” o qubit e apaga a fase. Por isso um qubit lógico exige muitos físicos e correção de erro.</Body>
      </div>
      <div style={{position: 'absolute', left: 54, top: 1030, width: 972, padding: 18, borderRadius: 16, border: `1px solid ${LIME}55`, background: 'rgba(163,230,53,0.06)', opacity: grow}}>
        <div style={{color: LIME, fontSize: 25, fontWeight: 800}}>1 qubit lógico ≠ 1 qubit físico</div>
      </div>
      <div style={{position: 'absolute', left: 54, top: 1160, width: 972, padding: '20px 24px', borderRadius: 18, background: PANEL, border: `1px solid ${CYAN}44`, opacity: grow}}>
        <div style={{color: CYAN, fontSize: 17, fontWeight: 800, letterSpacing: 2}}>CORREÇÃO DE ERRO</div>
        <Body size={21}>Um qubit lógico é codificado em muitos físicos. O código detecta e corrige erros antes que a informação se perca.</Body>
      </div>
      </SceneCamera>
    </SceneWrap>
  );
};

const VScene06 = () => (
  <SceneWrap index={5} hold>
    <MapCanvas vertical />
  </SceneWrap>
);

const VScene07 = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const grow = enter(frame, SCENES[6].startFrame, fps, 20);
  return (
    <SceneWrap index={6} hold>
      <div style={{position: 'absolute', left: 54, top: 140, width: 972, textAlign: 'center', opacity: grow}}>
        <Img
          src={staticFile('r1055-author.png')}
          style={{
            width: 260,
            height: 260,
            borderRadius: 130,
            objectFit: 'cover',
            border: `4px solid ${LIME}`,
            boxShadow: '0 0 60px rgba(163,230,53,0.28)',
          }}
        />
        <div style={{color: LIME, fontSize: 17, fontWeight: 800, letterSpacing: 3, marginTop: 18}}>AUTOR</div>
        <div style={{color: INK, fontSize: 50, fontWeight: 900, lineHeight: 1.05, marginTop: 6}}>
          Marcelo Claro<br />Laranjeira
        </div>
        <div style={{color: MUTED, fontSize: 20, lineHeight: 1.45, marginTop: 12}}>
          Professor · Mochileiro · Pedagogo<br />
          Mestrado em Ciência da Educação<br />
          Entusiasta em Tecnologia
        </div>
        <div style={{color: INK, fontSize: 46, fontWeight: 900, lineHeight: 1.05, marginTop: 26}}>
          Obrigado por<br /><span style={{color: LIME}}>assistir.</span>
        </div>
        <div style={{color: MUTED, fontSize: 20, lineHeight: 1.45, marginTop: 10}}>
          IA e Computação Quântica para educação básica.
        </div>
      </div>
      <div style={{position: 'absolute', left: 154, top: 900, width: 772, textAlign: 'center', opacity: grow}}>
        <div style={{background: INK, padding: 14, borderRadius: 18, display: 'inline-block'}}>
          <Img
            src={staticFile('r1055-github-qr.png')}
            style={{width: 320, height: 320, display: 'block'}}
          />
        </div>
        <div style={{color: LIME, fontSize: 17, fontWeight: 800, letterSpacing: 2, marginTop: 16}}>GITHUB</div>
        <div style={{color: INK, fontSize: 25, fontWeight: 700, marginTop: 2}}>github.com/MarceloClaro</div>
        <div style={{color: MUTED, fontSize: 18, lineHeight: 1.6, marginTop: 12}}>
          ORCID: 0000-0001-8996-2887<br />
          Instagram: @marceloclaro.geomaker<br />
          bit.ly/geomaker
        </div>
        <div style={{color: DIM, fontSize: 15, marginTop: 12}}>Aponte a câmera para o QR code.</div>
      </div>
    </SceneWrap>
  );
};

export const QubitVertical = () => (
  <AbsoluteFill style={{width: W, height: H, background: '#0B0912', color: INK, fontFamily: FONT, overflow: 'hidden'}}>
    <Background />
    <VScene01 />
    <VScene02 />
    <VScene03 />
    <VScene04 />
    <VScene05 />
    <VScene06 />
    <VScene07 />
    <Subtitle />
    <Header />
    <Footer />
  </AbsoluteFill>
);
