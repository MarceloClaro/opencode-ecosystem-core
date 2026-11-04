import React from 'react';
import {
  AbsoluteFill,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import {MAP, SCENES, SKILLS} from './timeline';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const BG = '#07111f';
const PANEL = '#0d1b2b';
const PANEL_2 = '#102338';
const INK = '#f8fafc';
const MUTED = '#a8b8cc';
const DIM = '#71859c';
const TEAL = '#2dd4bf';
const GOLD = '#f4b942';
const PURPLE = '#8b5cf6';
const GREEN = '#34d399';
const ROSE = '#fb7185';
const BORDER = 'rgba(148,163,184,0.22)';
const FONT = "'DejaVu Sans', 'Segoe UI', sans-serif";

const pct = (n: number) => `${n}%`;
const ease = (frame: number, start: number, duration = 18) =>
  interpolate(frame, [start, start + duration], [0, 1], {...clamp});

const Background: React.FC<{frame: number}> = ({frame}) => {
  const drift = Math.sin(frame * 0.008) * 16;
  return (
    <AbsoluteFill style={{background: `radial-gradient(1200px 700px at 15% 5%, #12314a 0%, ${BG} 55%, #040a12 100%)`, fontFamily: FONT}}>
      <AbsoluteFill style={{
        backgroundImage: 'linear-gradient(rgba(45,212,191,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(45,212,191,0.035) 1px, transparent 1px)',
        backgroundSize: '80px 80px',
        transform: `translate(${drift}px, ${drift * 0.4}px)`,
      }} />
      <div style={{position: 'absolute', width: 700, height: 700, borderRadius: 350, background: 'rgba(139,92,246,0.12)', filter: 'blur(90px)', left: -220, top: -240}} />
      <div style={{position: 'absolute', width: 600, height: 600, borderRadius: 300, background: 'rgba(45,212,191,0.10)', filter: 'blur(100px)', right: -220, bottom: -220}} />
    </AbsoluteFill>
  );
};

const Kicker: React.FC<{children: React.ReactNode; color?: string}> = ({children, color = TEAL}) => (
  <div style={{color, fontSize: 18, fontWeight: 800, letterSpacing: 4, textTransform: 'uppercase'}}>{children}</div>
);

const Title: React.FC<{children: React.ReactNode; size?: number}> = ({children, size = 64}) => (
  <div style={{color: INK, fontSize: size, lineHeight: 1.05, fontWeight: 900, letterSpacing: -1.2, marginTop: 12}}>{children}</div>
);

const LogoCard: React.FC<{width?: number; style?: React.CSSProperties}> = ({width = 520, style}) => (
  <div style={{display: 'inline-block', background: '#f7f5ef', borderRadius: 18, padding: 14, boxShadow: '0 24px 70px rgba(0,0,0,0.35)', ...style}}>
    <Img src={staticFile('r1058-airam-logo.png')} style={{width, display: 'block', borderRadius: 10}} />
  </div>
);

const Chip: React.FC<{children: React.ReactNode; color?: string; dark?: boolean}> = ({children, color = TEAL, dark = false}) => (
  <div style={{
    display: 'inline-flex', alignItems: 'center', gap: 8, padding: '9px 14px', borderRadius: 999,
    background: dark ? 'rgba(255,255,255,0.06)' : `${color}20`, border: `1px solid ${color}55`,
    color: dark ? INK : color, fontSize: 19, fontWeight: 700,
  }}>{children}</div>
);

const Metric: React.FC<{value: string; label: string; color?: string; size?: number}> = ({value, label, color = TEAL, size = 74}) => (
  <div>
    <div style={{fontSize: size, lineHeight: 1, fontWeight: 900, color}}>{value}</div>
    <div style={{fontSize: 17, color: MUTED, marginTop: 8, lineHeight: 1.3}}>{label}</div>
  </div>
);

const Bar: React.FC<{value: number; color: string; delay?: number; frame: number; label: string}> = ({value, color, delay = 0, frame, label}) => {
  const grow = ease(frame, delay, 26);
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 14, marginTop: 16}}>
      <div style={{width: 54, color: MUTED, fontSize: 17, fontWeight: 700}}>{label}</div>
      <div style={{height: 12, flex: 1, borderRadius: 8, background: 'rgba(255,255,255,0.08)', overflow: 'hidden'}}>
        <div style={{height: '100%', width: `${value * grow}%`, background: color, borderRadius: 8, boxShadow: `0 0 18px ${color}66`}} />
      </div>
      <div style={{width: 58, textAlign: 'right', color: INK, fontSize: 19, fontWeight: 800}}>{pct(Math.round(value * grow))}</div>
    </div>
  );
};

const Panel: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <div style={{background: PANEL, border: `1px solid ${BORDER}`, borderRadius: 22, padding: 28, boxShadow: '0 18px 50px rgba(0,0,0,0.22)', ...style}}>{children}</div>
);

const SceneHeader: React.FC<{index: number; kicker?: string}> = ({index, kicker}) => {
  const scene = SCENES[index];
  return (
    <div style={{position: 'absolute', left: 110, top: 86, width: 1550}}>
      <Kicker>{kicker ?? scene.kicker}</Kicker>
      <Title>{scene.title}</Title>
    </div>
  );
};

const CaptionBar: React.FC<{frame: number}> = ({frame}) => {
  let text = '';
  for (const scene of SCENES) {
    for (const caption of scene.captions) {
      if (frame >= caption.startFrame && frame < caption.endFrame) text = caption.text;
    }
  }
  if (!text) return null;
  return (
    <div style={{position: 'absolute', left: 110, right: 110, bottom: 34, zIndex: 50}}>
      <div style={{
        background: 'rgba(4,10,18,0.88)', borderLeft: `5px solid ${TEAL}`, borderRadius: 12,
        padding: '18px 24px', boxShadow: '0 16px 40px rgba(0,0,0,0.35)',
        color: INK, fontSize: 27, lineHeight: 1.35, fontWeight: 600, maxWidth: 1680,
      }}>{text}</div>
    </div>
  );
};

const Watermark: React.FC = () => (
  <div style={{position: 'absolute', right: 110, top: 36, display: 'flex', alignItems: 'center', gap: 12, opacity: 0.95, background: 'rgba(4,10,18,0.55)', padding: '8px 12px', borderRadius: 8}}>
    <div style={{width: 9, height: 9, borderRadius: 9, background: GOLD}} />
    <div style={{color: MUTED, fontSize: 15, fontWeight: 800, letterSpacing: 2}}>ESCOLA DE CIDADANIA AIRAM VERAS</div>
  </div>
);

const Scene: React.FC<{index: number; children: React.ReactNode}> = ({index, children}) => {
  const scene = SCENES[index];
  return (
    <Sequence from={scene.startFrame} durationInFrames={scene.endFrame - scene.startFrame} name={scene.title}>
      <AbsoluteFill>{children}</AbsoluteFill>
    </Sequence>
  );
};

// 01 — Abertura
const Opening: React.FC = () => {
  const frame = useCurrentFrame();
  const logo = ease(frame, 0, 24);
  const title = ease(frame, 18, 24);
  const sub = ease(frame, 38, 22);
  return (
    <AbsoluteFill>
      <Background frame={frame} />
      <div style={{position: 'absolute', left: 110, top: 130, width: 900, transform: `translateY(${(1 - logo) * 24}px)`, opacity: logo}}>
        <LogoCard width={540} />
      </div>
      <div style={{position: 'absolute', left: 110, top: 470, width: 1050, opacity: title, transform: `translateY(${(1 - title) * 26}px)`}}>
        <Kicker color={GOLD}>PLANO DE AÇÃO PEDAGÓGICA</Kicker>
        <div style={{color: INK, fontSize: 86, lineHeight: 0.98, fontWeight: 900, letterSpacing: -2, marginTop: 12}}>
          SPAECE<br/><span style={{color: TEAL}}>NOVEMBRO 2026</span>
        </div>
      </div>
      <div style={{position: 'absolute', left: 110, top: 760, width: 980, opacity: sub, transform: `translateY(${(1 - sub) * 20}px)`}}>
        <div style={{color: INK, fontSize: 38, fontWeight: 800}}>5º ano A e B · Língua Portuguesa e Matemática</div>
        <div style={{color: MUTED, fontSize: 23, marginTop: 12}}>Recompor habilidades, acompanhar evidências, ajustar o ensino.</div>
      </div>
      <div style={{position: 'absolute', right: 110, top: 600, display: 'flex', flexDirection: 'column', gap: 18, opacity: sub}}>
        <Chip color={TEAL}>55 estudantes</Chip>
        <Chip color={GOLD}>2 turmas</Chip>
        <Chip color={GREEN}>LP + Matemática</Chip>
      </div>
      <CaptionBar frame={frame + SCENES[0].startFrame} />
    </AbsoluteFill>
  );
};

// 02 — Mapa
type MapLayerProps = {
  src: string;
  scale: number;
  opacity: number;
  marker: readonly [number, number];
  pulse: number;
  label: string;
  color?: string;
};

const MapLayer: React.FC<MapLayerProps> = ({src, scale, opacity, marker, pulse, label, color = TEAL}) => {
  const x = marker[0] * 100;
  const y = marker[1] * 100;
  const ring = 22 + pulse * 16;
  return (
    <div style={{position: 'absolute', inset: 0, opacity, overflow: 'hidden'}}>
      <div style={{position: 'absolute', inset: 0, transform: `scale(${scale})`, transformOrigin: `${x}% ${y}%`}}>
        <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', display: 'block'}} />
        <div style={{position: 'absolute', left: `${x}%`, top: `${y}%`, transform: `translate(-50%, -50%) scale(${1 / Math.max(1, scale)})`, zIndex: 8}}>
          <div style={{width: ring * 2, height: ring * 2, borderRadius: ring * 2, border: `2px solid ${color}`, opacity: 0.35, position: 'absolute', left: -ring, top: -ring, transform: `scale(${1 + pulse * 0.3})`}} />
          <div style={{width: 22, height: 22, borderRadius: 22, background: color, border: '4px solid #fff', boxShadow: `0 0 24px ${color}`, position: 'absolute', left: -11, top: -11}} />
          <div style={{position: 'absolute', left: 18, top: -12, whiteSpace: 'nowrap', background: 'rgba(4,10,18,0.92)', color: '#fff', padding: '8px 12px', borderRadius: 8, fontSize: 18, fontWeight: 800, border: `1px solid ${color}77`}}>{label}</div>
        </div>
      </div>
    </div>
  );
};

const MapScene: React.FC = () => {
  const frame = useCurrentFrame();
  const worldScale = interpolate(frame, [0, 80], [1, 3], clamp);
  const worldOpacity = interpolate(frame, [0, 55, 80], [1, 1, 0], clamp);
  const stateScale = interpolate(frame, [55, 175], [1.35, 2.6], clamp);
  const stateOpacity = interpolate(frame, [55, 80, 145, 175], [0, 1, 1, 0], clamp);
  const cityScale = interpolate(frame, [145, 245], [1.25, 2.2], clamp);
  const cityOpacity = interpolate(frame, [145, 170, 225, 245], [0, 1, 1, 0], clamp);
  const streetScale = interpolate(frame, [225, 300], [1.1, 1], clamp);
  const streetOpacity = interpolate(frame, [225, 250], [0, 1], clamp);
  const pulse = (Math.sin(frame * 0.18) + 1) / 2;
  const panel = ease(frame, 0, 20);
  return (
    <AbsoluteFill>
      <Background frame={frame} />
      <MapLayer src="r1058-world-map.png" scale={worldScale} opacity={worldOpacity} marker={MAP.world.marker} pulse={pulse} label="Crateús · Brasil" color={PURPLE} />
      <MapLayer src="r1058-map-ceara.png" scale={stateScale} opacity={stateOpacity} marker={MAP.state.marker} pulse={pulse} label="Crateús · CE" />
      <MapLayer src="r1058-map-city.png" scale={cityScale} opacity={cityOpacity} marker={MAP.city.marker} pulse={pulse} label="Crateús · urbano" color={GOLD} />
      <MapLayer src="r1058-map-street.png" scale={streetScale} opacity={streetOpacity} marker={MAP.street.marker} pulse={pulse} label="Escola · Maratoan" />
      <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(90deg, rgba(7,17,31,0.96) 0%, rgba(7,17,31,0.78) 28%, rgba(7,17,31,0.18) 55%, rgba(7,17,31,0.05) 100%)'}} />
      <div style={{position: 'absolute', left: 110, top: 150, width: 700, opacity: panel, transform: `translateX(${(1 - panel) * -24}px)`}}>
        <Kicker>TERRITÓRIO EDUCATIVO</Kicker>
        <Title size={62}>Onde o plano<br/>acontece</Title>
        <div style={{marginTop: 26, display: 'flex', flexDirection: 'column', gap: 12}}>
          <Chip color={TEAL}>Maratoan · Crateús/CE</Chip>
          <Chip color={GOLD}>Sertão do Ceará</Chip>
          <Chip color={GREEN}>55 estudantes · 5º A e B</Chip>
        </div>
        <div style={{marginTop: 30, color: MUTED, fontSize: 21, lineHeight: 1.5, maxWidth: 620}}>
          O mapa localiza a escola no território. O ponto pulsa na sede do município e no bairro;
          a leitura é pedagógica, não um mapa de resultados.
        </div>
      </div>
      <div style={{position: 'absolute', right: 110, top: 100, color: MUTED, fontSize: 15, textAlign: 'right'}}>
        Mundo → Brasil → Ceará → Crateús → Maratoan
      </div>
      <div style={{position: 'absolute', left: 110, bottom: 140, color: DIM, fontSize: 14}}>
        © OpenStreetMap contributors · ODbL 1.0 · limites IBGE
      </div>
      <CaptionBar frame={frame + SCENES[1].startFrame} />
    </AbsoluteFill>
  );
};

// 03 — Diagnóstico
const Diagnosis: React.FC = () => {
  const frame = useCurrentFrame();
  const p1 = ease(frame, 0, 20);
  const p2 = ease(frame, 50, 20);
  const p3 = ease(frame, 100, 24);
  return (
    <AbsoluteFill>
      <Background frame={frame} />
      <SceneHeader index={2} kicker="LINHA DE BASE • 11/08/2026" />
      <div style={{position: 'absolute', left: 110, top: 260, width: 820, opacity: p1, transform: `translateY(${(1 - p1) * 20}px)`}}>
        <Panel>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start'}}>
            <div>
              <Kicker color={TEAL}>LÍNGUA PORTUGUESA</Kicker>
              <div style={{color: MUTED, fontSize: 19, marginTop: 8}}>Nível adequado</div>
            </div>
            <Metric value="70%" label="escola" color={TEAL} size={82} />
          </div>
          <Bar frame={frame} delay={10} label="5º A" value={78} color={TEAL} />
          <Bar frame={frame} delay={26} label="5º B" value={63} color={GOLD} />
          <div style={{marginTop: 16, color: DIM, fontSize: 15}}>22% intermediário · 7% defasagem no consolidado</div>
        </Panel>
      </div>
      <div style={{position: 'absolute', left: 970, top: 260, width: 820, opacity: p2, transform: `translateY(${(1 - p2) * 20}px)`}}>
        <Panel>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start'}}>
            <div>
              <Kicker color={GOLD}>MATEMÁTICA</Kicker>
              <div style={{color: MUTED, fontSize: 19, marginTop: 8}}>Nível adequado</div>
            </div>
            <Metric value="62%" label="escola" color={GOLD} size={82} />
          </div>
          <Bar frame={frame} delay={60} label="5º A" value={59} color={GOLD} />
          <Bar frame={frame} delay={76} label="5º B" value={65} color={TEAL} />
          <div style={{marginTop: 16, color: DIM, fontSize: 15}}>30% intermediário · 8% defasagem no consolidado</div>
        </Panel>
      </div>
      <div style={{position: 'absolute', left: 110, top: 680, width: 1680, opacity: p3, transform: `translateY(${(1 - p3) * 16}px)`}}>
        <Panel style={{display: 'flex', alignItems: 'center', gap: 36, padding: '20px 30px'}}>
          <Kicker color={GREEN}>FLUÊNCIA LEITORA</Kicker>
          <div style={{display: 'flex', gap: 34, alignItems: 'baseline'}}>
            <div><span style={{fontSize: 42, fontWeight: 900, color: TEAL}}>43</span> <span style={{color: MUTED, fontSize: 18}}>fluentes</span></div>
            <div><span style={{fontSize: 42, fontWeight: 900, color: GOLD}}>5</span> <span style={{color: MUTED, fontSize: 18}}>iniciantes</span></div>
            <div><span style={{fontSize: 42, fontWeight: 900, color: ROSE}}>2</span> <span style={{color: MUTED, fontSize: 18}}>pré-leitores</span></div>
          </div>
          <div style={{color: MUTED, fontSize: 18, marginLeft: 'auto'}}>50 avaliados · 5 resultados do 5º B a recuperar</div>
        </Panel>
      </div>
      <div style={{position: 'absolute', right: 110, top: 180, color: DIM, fontSize: 15}}>linha de base histórica — não é resultado de novembro</div>
      <CaptionBar frame={frame + SCENES[2].startFrame} />
    </AbsoluteFill>
  );
};

// 04 — Habilidades
const SkillChip: React.FC<{children: React.ReactNode; color: string; delay: number; frame: number}> = ({children, color, delay, frame}) => {
  const show = ease(frame, delay, 14);
  return <div style={{opacity: show, transform: `translateY(${(1 - show) * 10}px)`}}><Chip color={color}>{children}</Chip></div>;
};

const OVERVIEW: Record<string, {a: Array<[string, string]>; b: Array<[string, string]>; chips: string[]; note: string}> = {
  LP: {
    a: [['H18/H19', '26%'], ['H12', '41%'], ['H05', '52%'], ['H11', '56%']],
    b: [['H05', '22%'], ['H18', '26%'], ['H19', '30%'], ['H12', '37%'], ['H20', '44%']],
    chips: ['Inferência', 'Assunto global', 'Sentido e pontuação', 'Conflito narrativo', 'Gênero e coesão', 'Referenciação'],
    note: 'LP: inferência, assunto global, sentido, pontuação, conflito, gênero e referenciação.',
  },
  MAT: {
    a: [['H18', '33%'], ['H12', '37%'], ['H01/H14', '41%'], ['H08/H11', '48%']],
    b: [['H12', '23%'], ['H14', '33%'], ['H11', '42%'], ['H01/H18', '46%']],
    chips: ['Multiplicação/divisão', 'Frações', 'Localização', 'Planificação/polígonos', 'Área', 'Medidas e gráficos'],
    note: 'MAT: multiplicação/divisão, frações, geometria/área, medidas e gráficos.',
  },
};

const Overview: React.FC<{component: 'LP' | 'MAT'; index: number}> = ({component, index}) => {
  const frame = useCurrentFrame();
  const data = OVERVIEW[component];
  const accent = component === 'LP' ? TEAL : GOLD;
  return (
    <AbsoluteFill>
      <Background frame={frame} />
      <SceneHeader index={index} />
      <div style={{position: 'absolute', left: 110, top: 270, width: 1680, display: 'flex', gap: 24}}>
        {(['a', 'b'] as const).map((key, col) => {
          const show = ease(frame, col * 8, 18);
          return (
            <Panel key={key} style={{flex: 1, minHeight: 470, opacity: show, transform: `translateY(${(1 - show) * 18}px)`}}>
              <Kicker color={accent}>{key === 'a' ? '5º ANO A' : '5º ANO B'}</Kicker>
              <div style={{display: 'flex', flexWrap: 'wrap', gap: 9, marginTop: 16}}>
                {data.chips.map((chip, i) => <SkillChip key={chip} color={accent} delay={col * 8 + i * 3} frame={frame}>{chip}</SkillChip>)}
              </div>
              <div style={{marginTop: 20, borderTop: `1px solid ${BORDER}`, paddingTop: 14}}>
                <div style={{color: MUTED, fontSize: 14, fontWeight: 800, letterSpacing: 2}}>MENORES ACERTOS</div>
                <div style={{display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 10}}>
                  {data[key].map(([code, value]) => (
                    <div key={code} style={{background: 'rgba(255,255,255,0.05)', border: `1px solid ${accent}44`, borderRadius: 10, padding: '8px 10px', color: INK, fontSize: 17, fontWeight: 800}}>
                      {code} <span style={{color: accent}}>{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </Panel>
          );
        })}
      </div>
      <div style={{position: 'absolute', left: 110, top: 780, width: 1680, opacity: ease(frame, 90, 20)}}>
        <div style={{background: 'rgba(251,113,133,0.09)', border: '1px solid rgba(251,113,133,0.32)', borderRadius: 14, padding: '13px 18px', color: '#fecdd3', fontSize: 18}}>
          {data.note} H01–H20 são marcadores do arquivo CAEd; não são descritores oficiais do SPAECE sem dicionário de equivalência.
        </div>
      </div>
      <CaptionBar frame={frame + SCENES[index].startFrame} />
    </AbsoluteFill>
  );
};

const MiniVisual: React.FC<{kind: string; frame: number}> = ({kind, frame}) => {
  if (kind === 'fraction') {
    const fill = ease(frame, 35, 20);
    return <div style={{display: 'flex', gap: 6, marginTop: 12}}>{[0, 1, 2, 3].map((i) => <div key={i} style={{height: 54, flex: 1, borderRadius: 8, border: `2px solid ${GOLD}`, background: i < 3 ? `rgba(244,185,66,${0.15 + 0.55 * fill})` : 'rgba(255,255,255,0.03)'}} />)}</div>;
  }
  if (kind === 'area') {
    const show = ease(frame, 35, 20);
    return <div style={{display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 4, width: 300, marginTop: 12}}>{Array.from({length: 24}).map((_, i) => <div key={i} style={{height: 32, borderRadius: 4, border: `1px solid ${TEAL}66`, background: `rgba(45,212,191,${0.05 + 0.22 * show * (i / 24)})`}} />)}</div>;
  }
  if (kind === 'groups') {
    return <div style={{display: 'flex', gap: 8, marginTop: 12}}>{[0, 1, 2, 3].map((i) => <div key={i} style={{width: 64, height: 64, borderRadius: 10, background: 'rgba(244,185,66,0.12)', border: `1px solid ${GOLD}66`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: GOLD, fontSize: 24, fontWeight: 900}}>12</div>)}</div>;
  }
  if (kind === 'measure') {
    return <div style={{display: 'flex', alignItems: 'center', gap: 12, marginTop: 18, flexWrap: 'wrap'}}><div style={{color: GOLD, fontSize: 26, fontWeight: 900}}>2,5 kg × 4</div><div style={{color: DIM}}>→</div><div style={{color: TEAL, fontSize: 26, fontWeight: 900}}>10 kg</div><div style={{color: DIM}}>→</div><div style={{color: INK, fontSize: 22, fontWeight: 900}}>10.000 g</div></div>;
  }
  if (kind === 'graph') {
    const grow = ease(frame, 35, 20);
    return <div style={{display: 'flex', alignItems: 'flex-end', gap: 18, height: 150, marginTop: 12}}><div style={{textAlign: 'center'}}><div style={{height: 110 * grow, width: 64, background: TEAL, borderRadius: 8}} /><div style={{color: MUTED, fontSize: 14, marginTop: 6}}>5º A 78%</div></div><div style={{textAlign: 'center'}}><div style={{height: 88 * grow, width: 64, background: GOLD, borderRadius: 8}} /><div style={{color: MUTED, fontSize: 14, marginTop: 6}}>5º B 63%</div></div></div>;
  }
  return <div style={{display: 'flex', gap: 10, marginTop: 16}}>{['Localizar', 'Interpretar', 'Justificar'].map((s, i) => <div key={s} style={{flex: 1, padding: '12px 8px', borderRadius: 10, border: `1px solid ${TEAL}44`, background: 'rgba(45,212,191,0.06)', color: TEAL, fontSize: 16, fontWeight: 800, textAlign: 'center'}}>{i + 1}. {s}</div>)}</div>;
};

const SkillScene: React.FC<{skill: any; index: number}> = ({skill, index}) => {
  const frame = useCurrentFrame();
  const zoom = 1 + 0.025 * Math.sin(frame / 38);
  const shift = Math.sin(frame / 52) * 7;
  const step = Math.min(2, Math.floor(frame / 48));
  const accent = skill.component === 'LP' ? TEAL : GOLD;
  return (
    <AbsoluteFill>
      <Background frame={frame} />
      <div style={{position: 'absolute', inset: 0, transform: `scale(${zoom}) translateX(${shift}px)`, transformOrigin: 'center'}}>
        <SceneHeader index={index} />
        <div style={{position: 'absolute', left: 110, top: 260, width: 690}}>
          <Panel style={{minHeight: 500}}>
            <Kicker color={accent}>{skill.classes}</Kicker>
            <div style={{color: MUTED, fontSize: 17, marginTop: 10}}>Marcadores de menor acerto</div>
            <div style={{color: INK, fontSize: 26, fontWeight: 900, marginTop: 4}}>{skill.markers}</div>
            <div style={{color: MUTED, fontSize: 19, lineHeight: 1.5, marginTop: 18}}>{skill.why}</div>
            <div style={{marginTop: 18, borderTop: `1px solid ${BORDER}`, paddingTop: 12}}>
              <div style={{color: accent, fontSize: 14, fontWeight: 900, letterSpacing: 2}}>APOIO VISUAL</div>
              <MiniVisual kind={skill.visual} frame={frame} />
            </div>
          </Panel>
        </div>
        <div style={{position: 'absolute', left: 840, top: 260, width: 970}}>
          <Panel style={{minHeight: 190}}>
            <Kicker color={GOLD}>PERGUNTA</Kicker>
            <div style={{color: INK, fontSize: 24, lineHeight: 1.4, marginTop: 10}}>{skill.question}</div>
          </Panel>
          <Panel style={{marginTop: 16, minHeight: 230}}>
            <Kicker color={accent}>COMO RESPONDER</Kicker>
            <div style={{display: 'flex', flexDirection: 'column', gap: 8, marginTop: 10}}>
              {skill.steps.map((text: string, i: number) => (
                <div key={text} style={{display: 'flex', gap: 10, alignItems: 'center', padding: '9px 10px', borderRadius: 9, background: i === step ? `${accent}18` : 'rgba(255,255,255,0.03)', border: `1px solid ${i === step ? accent : 'rgba(255,255,255,0.08)'}`}}>
                  <div style={{width: 24, height: 24, borderRadius: 24, background: i === step ? accent : 'rgba(255,255,255,0.08)', color: i === step ? BG : MUTED, fontSize: 13, fontWeight: 900, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{i + 1}</div>
                  <div style={{color: INK, fontSize: 17, lineHeight: 1.3}}>{text}</div>
                </div>
              ))}
            </div>
          </Panel>
          <div style={{marginTop: 14, background: 'rgba(45,212,191,0.07)', border: '1px solid rgba(45,212,191,0.25)', borderRadius: 12, padding: '11px 14px'}}>
            <span style={{color: TEAL, fontSize: 13, fontWeight: 900, letterSpacing: 2}}>RESPOSTA ESPERADA </span>
            <span style={{color: INK, fontSize: 17}}>{skill.answer}</span>
          </div>
        </div>
      </div>
      <CaptionBar frame={frame + SCENES[index].startFrame} />
    </AbsoluteFill>
  );
};

// 05 — Por que
const Why: React.FC = () => {
  const frame = useCurrentFrame();
  const cards = [
    {title: 'Menor acerto', body: 'A evidência mostra onde a turma precisa de mais apoio.', color: TEAL},
    {title: 'Sustentam outras', body: 'Inferência, frações e medidas aparecem em várias situações.', color: GOLD},
    {title: 'Exigem justificativa', body: 'Localizar pista, explicar e escolher — não chutar.', color: PURPLE},
  ];
  return (
    <AbsoluteFill>
      <Background frame={frame} />
      <SceneHeader index={4} kicker="DA EVIDÊNCIA À AULA" />
      <div style={{position: 'absolute', left: 110, top: 300, width: 1680, display: 'flex', gap: 24}}>
        {cards.map((card, i) => {
          const show = ease(frame, i * 22, 18);
          return (
            <Panel key={card.title} style={{flex: 1, minHeight: 280, opacity: show, transform: `translateY(${(1 - show) * 24}px)`}}>
              <div style={{width: 54, height: 54, borderRadius: 16, background: `${card.color}22`, border: `1px solid ${card.color}66`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: card.color, fontSize: 26, fontWeight: 900}}>{i + 1}</div>
              <div style={{color: INK, fontSize: 30, fontWeight: 900, marginTop: 20}}>{card.title}</div>
              <div style={{color: MUTED, fontSize: 20, lineHeight: 1.5, marginTop: 10}}>{card.body}</div>
            </Panel>
          );
        })}
      </div>
      <div style={{position: 'absolute', left: 110, top: 680, width: 1680, opacity: ease(frame, 110, 22)}}>
        <div style={{borderLeft: `6px solid ${GOLD}`, paddingLeft: 26}}>
          <div style={{color: INK, fontSize: 44, fontWeight: 900, lineHeight: 1.15}}>Recomposição, não treino de prova.</div>
          <div style={{color: MUTED, fontSize: 21, marginTop: 10}}>Representação concreta → prática guiada → explicação do erro → nova evidência.</div>
        </div>
      </div>
      <CaptionBar frame={frame + SCENES[4].startFrame} />
    </AbsoluteFill>
  );
};

// 06 — Cronograma
const WeekCard: React.FC<{week: string; dates: string; focus: string; check: string; color: string; show: number}> = ({week, dates, focus, check, color, show}) => (
  <div style={{flex: 1, opacity: show, transform: `translateY(${(1 - show) * 18}px)`}}>
    <div style={{background: PANEL, border: `1px solid ${color}55`, borderRadius: 18, padding: 18, minHeight: 300, display: 'flex', flexDirection: 'column'}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <div style={{color: color, fontSize: 17, fontWeight: 900, letterSpacing: 1}}>{week}</div>
        <div style={{width: 10, height: 10, borderRadius: 10, background: color, boxShadow: `0 0 14px ${color}`}} />
      </div>
      <div style={{color: INK, fontSize: 23, fontWeight: 900, marginTop: 8}}>{dates}</div>
      <div style={{color: MUTED, fontSize: 17, lineHeight: 1.4, marginTop: 12, flex: 1}}>{focus}</div>
      <div style={{color: color, fontSize: 15, fontWeight: 800, borderTop: `1px solid ${BORDER}`, paddingTop: 10}}>{check}</div>
    </div>
  </div>
);

const Schedule: React.FC = () => {
  const frame = useCurrentFrame();
  const weeks = [
    {week: 'SEMANA 1', dates: '03–06/11', focus: 'Diagnóstico, operações e inferência', check: 'Miniavaliação 06/11', color: TEAL},
    {week: 'SEMANA 2', dates: '09–13/11', focus: 'Gêneros, frações e geometria', check: 'Simulado parcial 13/11', color: GOLD},
    {week: 'SEMANA 3', dates: '16–19/11', focus: 'Textos multimodais, medidas e gráficos', check: 'Revisão 19/11', color: PURPLE},
    {week: 'SEMANA 4', dates: '23–27/11', focus: 'Simulado, clínica de erros e oficinas', check: 'Contraprova 27/11', color: ROSE},
    {week: 'SEMANA 5', dates: '30/11', focus: 'Revisão final, logística e acolhimento', check: 'SPAECE 01/12/2026', color: GREEN},
  ];
  const daily = ease(frame, 300, 24);
  return (
    <AbsoluteFill>
      <Background frame={frame} />
      <SceneHeader index={3} kicker="PREPARAÇÃO ATÉ 30/11 • PROVA 01/12/2026" />
      <div style={{position: 'absolute', left: 110, top: 210, width: 1700, opacity: ease(frame, 0, 18)}}>
        <div style={{display: 'inline-flex', alignItems: 'center', gap: 14, background: 'rgba(244,185,66,0.12)', border: `1px solid ${GOLD}66`, borderRadius: 12, padding: '11px 18px'}}>
          <div style={{color: GOLD, fontSize: 16, fontWeight: 900, letterSpacing: 2}}>SPAECE 2026</div>
          <div style={{color: INK, fontSize: 22, fontWeight: 900}}>01/12/2026 · terça-feira · Língua Portuguesa e Matemática</div>
        </div>
      </div>
      <div style={{position: 'absolute', left: 110, top: 285, width: 1700, display: 'flex', gap: 14}}>
        {weeks.map((w, i) => <WeekCard key={w.week} {...w} show={ease(frame, i * 120, 20)} />)}
      </div>
      <div style={{position: 'absolute', left: 110, top: 595, width: 1700, opacity: daily}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8}}>
          <Kicker color={TEAL}>ROTINA SEMANAL FIXA</Kicker>
          <div style={{color: MUTED, fontSize: 15}}>integra o plano de ação e a preparação para 01/12</div>
        </div>
        <div style={{display: 'flex', gap: 10}}>
          {[
            {day: 'SEGUNDA', items: ['Leitura e interpretação', 'Produção textual'], color: TEAL},
            {day: 'TERÇA', items: ['Matemática: operações, problemas e geometria', 'Resolução de problemas'], color: GOLD},
            {day: 'QUARTA', items: ['Leitura e interpretação', 'Produção textual'], color: TEAL},
            {day: 'QUINTA', items: ['Simulados e correções', 'Revisão das dificuldades'], color: PURPLE},
            {day: 'SEXTA', items: ['Vídeos de apoio', 'Torta na Cara · Tabuada · Bingo'], color: ROSE},
          ].map((d) => (
            <div key={d.day} style={{flex: 1, background: PANEL, border: `1px solid ${d.color}55`, borderRadius: 13, padding: '11px 12px', minHeight: 130}}>
              <div style={{color: d.color, fontSize: 14, fontWeight: 900, letterSpacing: 1}}>{d.day}</div>
              {d.items.map((item) => <div key={item} style={{color: INK, fontSize: 14, lineHeight: 1.35, marginTop: 6}}>• {item}</div>)}
            </div>
          ))}
        </div>
      </div>
      <div style={{position: 'absolute', left: 110, top: 755, width: 1700, color: DIM, fontSize: 15}}>
        Lema: Juntos pelo avanço da aprendizagem! · 02/11 e 20/11 feriados; 15/11 domingo.
      </div>
      <CaptionBar frame={frame + SCENES[3].startFrame} />
    </AbsoluteFill>
  );
};

// 07 — LP
const LPExample: React.FC = () => {
  const frame = useCurrentFrame();
  const a = ease(frame, 0, 20);
  const b = ease(frame, 60, 20);
  const c = ease(frame, 200, 20);
  return (
    <AbsoluteFill>
      <Background frame={frame} />
      <SceneHeader index={6} kicker="INFERÊNCIA E PONTUAÇÃO" />
      <div style={{position: 'absolute', left: 110, top: 270, width: 780, opacity: a, transform: `translateY(${(1 - a) * 18}px)`}}>
        <Panel style={{minHeight: 430}}>
          <Kicker color={TEAL}>LEIA O TRECHO</Kicker>
          <div style={{color: INK, fontSize: 30, lineHeight: 1.5, marginTop: 20}}>
            “No início, Ana achava o parque um terreno vazio. <span style={{color: TEAL, fontWeight: 900}}>Depois do mutirão</span>, passou a cuidar das plantas e a convidar os colegas.”
          </div>
          <div style={{marginTop: 24, color: MUTED, fontSize: 18}}>Pista: a mudança aparece no contraste entre “no início” e “depois”.</div>
          <div style={{marginTop: 20, background: 'rgba(45,212,191,0.08)', border: '1px solid rgba(45,212,191,0.25)', borderRadius: 12, padding: 16}}>
            <div style={{color: TEAL, fontSize: 14, fontWeight: 900, letterSpacing: 2}}>RESPOSTA ESPERADA</div>
            <div style={{color: INK, fontSize: 18, lineHeight: 1.45, marginTop: 6}}>“Depois do mutirão, passou a cuidar das plantas...” mostra a mudança; a justificativa deve citar essa pista, não apenas opinar.</div>
          </div>
        </Panel>
      </div>
      <div style={{position: 'absolute', left: 930, top: 270, width: 860, opacity: b, transform: `translateY(${(1 - b) * 18}px)`}}>
        <Panel style={{minHeight: 200}}>
          <Kicker color={GOLD}>PERGUNTA 1</Kicker>
          <div style={{color: INK, fontSize: 28, lineHeight: 1.4, marginTop: 12}}>Qual trecho mostra que a opinião de Ana mudou? Explique com uma pista do texto.</div>
        </Panel>
        <Panel style={{marginTop: 18, minHeight: 210}}>
          <Kicker color={PURPLE}>PERGUNTA 2 • PONTUAÇÃO</Kicker>
          <div style={{color: INK, fontSize: 24, lineHeight: 1.55, marginTop: 12}}>
            “Ana não queria ir.”<br/>
            “Ana, não queria ir.”<br/>
            <span style={{color: MUTED, fontSize: 20}}>Como a vírgula muda o sentido?</span>
          </div>
        </Panel>
      </div>
      <div style={{position: 'absolute', left: 110, top: 760, width: 1680, opacity: c, transform: `translateY(${(1 - c) * 16}px)`}}>
        <div style={{borderLeft: `6px solid ${GOLD}`, paddingLeft: 22}}>
          <div style={{color: GOLD, fontSize: 15, fontWeight: 900, letterSpacing: 2}}>POR QUE TRABALHAR</div>
          <div style={{color: INK, fontSize: 26, marginTop: 6}}>Inferência e pontuação estão entre os menores acertos: exigem localizar pista, justificar e perceber efeitos de sentido — não chute.</div>
        </div>
      </div>
      <CaptionBar frame={frame + SCENES[6].startFrame} />
    </AbsoluteFill>
  );
};

// 08 — Matemática
const FractionBar: React.FC<{frame: number}> = ({frame}) => {
  const fill = ease(frame, 80, 24);
  return (
    <div style={{display: 'flex', gap: 6, marginTop: 18}}>
      {[0, 1, 2, 3].map((i) => (
        <div key={i} style={{height: 56, flex: 1, borderRadius: 8, border: `2px solid ${GOLD}`, background: i < 3 ? `rgba(244,185,66,${0.15 + 0.55 * fill})` : 'rgba(255,255,255,0.03)'}} />
      ))}
    </div>
  );
};

const AreaGrid: React.FC<{frame: number}> = ({frame}) => {
  const show = ease(frame, 130, 24);
  return (
    <div style={{display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 4, width: 300, marginTop: 14}}>
      {Array.from({length: 24}).map((_, i) => (
        <div key={i} style={{height: 36, borderRadius: 4, border: `1px solid ${TEAL}66`, background: `rgba(45,212,191,${0.05 + 0.25 * show * (i / 24)})`}} />
      ))}
    </div>
  );
};

const MathExample: React.FC = () => {
  const frame = useCurrentFrame();
  const a = ease(frame, 0, 20);
  const b = ease(frame, 55, 20);
  const c = ease(frame, 80, 20);
  const why = ease(frame, 120, 20);
  return (
    <AbsoluteFill>
      <Background frame={frame} />
      <SceneHeader index={7} kicker="MULTIPLICAÇÃO, FRAÇÃO E ÁREA" />
      <div style={{position: 'absolute', left: 110, top: 270, width: 520, opacity: a, transform: `translateY(${(1 - a) * 16}px)`}}>
        <Panel style={{minHeight: 360}}>
          <Kicker color={GOLD}>1 · MULTIPLICAÇÃO</Kicker>
          <div style={{color: INK, fontSize: 26, lineHeight: 1.4, marginTop: 12}}>4 caixas com 12 cadernos em cada uma.</div>
          <div style={{display: 'flex', gap: 10, marginTop: 20}}>
            {[0, 1, 2, 3].map((i) => <div key={i} style={{width: 72, height: 72, borderRadius: 12, background: 'rgba(244,185,66,0.12)', border: `1px solid ${GOLD}66`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: GOLD, fontSize: 28, fontWeight: 900}}>12</div>)}
          </div>
          <div style={{color: TEAL, fontSize: 22, fontWeight: 800, marginTop: 20}}>4 × 12 = 48 cadernos</div>
          <div style={{color: MUTED, fontSize: 19, marginTop: 6}}>48 ÷ 4 turmas = 12 por turma</div>
        </Panel>
      </div>
      <div style={{position: 'absolute', left: 670, top: 270, width: 560, opacity: b, transform: `translateY(${(1 - b) * 16}px)`}}>
        <Panel style={{minHeight: 360}}>
          <Kicker color={GOLD}>2 · FRAÇÃO</Kicker>
          <div style={{color: INK, fontSize: 26, lineHeight: 1.4, marginTop: 12}}>Uma barra em 4 partes iguais. Pintaram 3.</div>
          <FractionBar frame={frame} />
          <div style={{color: TEAL, fontSize: 30, fontWeight: 900, marginTop: 18}}>3/4</div>
          <div style={{color: MUTED, fontSize: 18, marginTop: 6}}>Três de quatro partes iguais.</div>
        </Panel>
      </div>
      <div style={{position: 'absolute', left: 1270, top: 270, width: 520, opacity: c, transform: `translateY(${(1 - c) * 16}px)`}}>
        <Panel style={{minHeight: 360}}>
          <Kicker color={TEAL}>3 · ÁREA</Kicker>
          <div style={{color: INK, fontSize: 26, lineHeight: 1.4, marginTop: 12}}>Retângulo de 6 linhas por 4 colunas.</div>
          <AreaGrid frame={frame} />
          <div style={{color: TEAL, fontSize: 26, fontWeight: 900, marginTop: 14}}>6 × 4 = 24 quadradinhos</div>
        </Panel>
      </div>
      <div style={{position: 'absolute', left: 110, top: 760, width: 1680, opacity: why}}>
        <div style={{borderLeft: `6px solid ${TEAL}`, paddingLeft: 22}}>
          <div style={{color: TEAL, fontSize: 15, fontWeight: 900, letterSpacing: 2}}>POR QUE TRABALHAR</div>
          <div style={{color: INK, fontSize: 26, marginTop: 6}}>Multiplicação, fração e área são prioridades e pedem representação concreta, cálculo e explicação do raciocínio.</div>
        </div>
      </div>
      <CaptionBar frame={frame + SCENES[7].startFrame} />
    </AbsoluteFill>
  );
};

// 09 — Intervenções
const Interventions: React.FC = () => {
  const frame = useCurrentFrame();
  const roles = [
    {title: 'Professoras regentes', body: 'Executam os blocos, registram erros, apoios e respostas.', color: TEAL},
    {title: 'Coordenação', body: 'Acompanha miniavaliações, apoia itens e revisa grupos.', color: GOLD},
    {title: 'Gestão', body: 'Garante tempo, materiais, presença e calendário.', color: PURPLE},
  ];
  return (
    <AbsoluteFill>
      <Background frame={frame} />
      <SceneHeader index={17} kicker="RESPONSÁVEIS • MONITORAMENTO" />
      <div style={{position: 'absolute', left: 110, top: 270, width: 1680, display: 'flex', gap: 20}}>
        {roles.map((r, i) => {
          const show = ease(frame, i * 24, 18);
          return <Panel key={r.title} style={{flex: 1, minHeight: 220, opacity: show, transform: `translateY(${(1 - show) * 16}px)`}}>
            <div style={{color: r.color, fontSize: 16, fontWeight: 900, letterSpacing: 1}}>0{i + 1}</div>
            <div style={{color: INK, fontSize: 27, fontWeight: 900, marginTop: 10}}>{r.title}</div>
            <div style={{color: MUTED, fontSize: 19, lineHeight: 1.45, marginTop: 10}}>{r.body}</div>
          </Panel>;
        })}
      </div>
      <div style={{position: 'absolute', left: 110, top: 530, width: 900, opacity: ease(frame, 60, 20)}}>
        <Panel>
          <Kicker color={GREEN}>GRUPOS DE INTERVENÇÃO</Kicker>
          <div style={{display: 'flex', gap: 12, flexWrap: 'wrap', marginTop: 16}}>
            <Chip color={ROSE}>C1 intensivo</Chip>
            <Chip color={GOLD}>C2 focal</Chip>
            <Chip color={TEAL}>C3 consolidação</Chip>
            <Chip color={PURPLE}>C4 aprofundamento</Chip>
          </div>
          <div style={{color: MUTED, fontSize: 18, marginTop: 14}}>Sem ranking público; código interno e devolutiva individual.</div>
        </Panel>
      </div>
      <div style={{position: 'absolute', left: 1040, top: 530, width: 750, opacity: ease(frame, 100, 20)}}>
        <Panel>
          <Kicker color={GOLD}>METAS PROPOSTAS</Kicker>
          <div style={{display: 'flex', gap: 34, marginTop: 12}}>
            <Metric value="80%" label="Língua Portuguesa" color={TEAL} size={58} />
            <Metric value="75%" label="Matemática" color={GOLD} size={58} />
          </div>
          <div style={{color: ROSE, fontSize: 17, marginTop: 12}}>Meta não é resultado garantido.</div>
        </Panel>
      </div>
      <div style={{position: 'absolute', left: 110, top: 730, width: 1680, opacity: ease(frame, 120, 20)}}>
        <div style={{background: 'rgba(45,212,191,0.07)', border: '1px solid rgba(45,212,191,0.25)', borderRadius: 14, padding: '14px 20px', display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap'}}>
          <div style={{color: TEAL, fontSize: 14, fontWeight: 900, letterSpacing: 2}}>MONITORAMENTO</div>
          {['Diário', '06/11', '13/11', '19/11', '23/11', '27/11', '30/11'].map((d) => <div key={d} style={{color: d === 'Diário' ? TEAL : INK, fontSize: 16, fontWeight: 800, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 999, padding: '7px 11px'}}>{d}</div>)}
        </div>
      </div>
      <CaptionBar frame={frame + SCENES[17].startFrame} />
    </AbsoluteFill>
  );
};

// 10 — Fechamento
const Closing: React.FC = () => {
  const frame = useCurrentFrame();
  const show = ease(frame, 0, 22);
  return (
    <AbsoluteFill>
      <Background frame={frame} />
      <div style={{position: 'absolute', left: 110, top: 170, opacity: show, transform: `translateY(${(1 - show) * 20}px)`}}>
        <LogoCard width={560} />
      </div>
      <div style={{position: 'absolute', left: 110, top: 520, width: 1200, opacity: ease(frame, 30, 22)}}>
        <Kicker color={GOLD}>SPAECE • NOVEMBRO 2026</Kicker>
        <div style={{color: INK, fontSize: 54, fontWeight: 900, lineHeight: 1.1, marginTop: 12}}>Dados para decidir,<br/><span style={{color: TEAL}}>não para ranquear.</span></div>
        <div style={{color: MUTED, fontSize: 24, marginTop: 18}}>Escola de Cidadania Airam Veras · Crateús/CE</div>
        <div style={{display: 'flex', gap: 12, marginTop: 22}}>
          <Chip color={TEAL}>Educar</Chip>
          <Chip color={GOLD}>Formar</Chip>
          <Chip color={GREEN}>Transformar</Chip>
        </div>
      </div>
      <div style={{position: 'absolute', left: 110, bottom: 150, color: DIM, fontSize: 15}}>Dados agregados; sem exposição de estudantes.</div>
      <CaptionBar frame={frame + SCENES[9].startFrame} />
    </AbsoluteFill>
  );
};

// 11 — Agradecimento e autor
const Author: React.FC = () => {
  const frame = useCurrentFrame();
  const photo = ease(frame, 0, 22);
  const qr = ease(frame, 30, 22);
  const text = ease(frame, 15, 22);
  return (
    <AbsoluteFill>
      <Background frame={frame} />
      <div style={{position: 'absolute', left: 110, top: 78, width: 1600}}>
        <Kicker color={GOLD}>AGRADECIMENTO</Kicker>
        <div style={{color: INK, fontSize: 60, fontWeight: 900, marginTop: 8}}>Muito obrigado por assistir.</div>
      </div>
      <div style={{position: 'absolute', left: 110, top: 235, width: 380, opacity: photo, transform: `translateY(${(1 - photo) * 20}px)`}}>
        <div style={{width: 330, height: 330, borderRadius: 165, padding: 7, background: `linear-gradient(135deg, ${TEAL}, ${GOLD})`, boxShadow: '0 22px 60px rgba(0,0,0,0.4)'}}>
          <Img src={staticFile('r1058-author.png')} style={{width: '100%', height: '100%', objectFit: 'cover', borderRadius: 158, display: 'block', border: '5px solid #07111f'}} />
        </div>
      </div>
      <div style={{position: 'absolute', left: 500, top: 250, width: 880, opacity: text, transform: `translateY(${(1 - text) * 18}px)`}}>
        <div style={{color: INK, fontSize: 44, fontWeight: 900, lineHeight: 1.1}}>MARCELO CLARO<br/>LARANJEIRA</div>
        <div style={{color: TEAL, fontSize: 20, fontWeight: 800, marginTop: 14}}>Professor · Pedagogo · Mestrado em Ciência da Educação</div>
        <div style={{color: MUTED, fontSize: 19, lineHeight: 1.5, marginTop: 10}}>Tecnologia, inteligência artificial e computação quântica na educação básica.</div>
        <div style={{marginTop: 22, display: 'flex', flexDirection: 'column', gap: 8, color: MUTED, fontSize: 17}}>
          <div><span style={{color: GOLD, fontWeight: 900}}>GitHub</span> · github.com/MarceloClaro</div>
          <div><span style={{color: GOLD, fontWeight: 900}}>ORCID</span> · 0000-0001-8996-2887</div>
          <div><span style={{color: GOLD, fontWeight: 900}}>Instagram</span> · @marceloclaro.geomaker</div>
          <div><span style={{color: GOLD, fontWeight: 900}}>Links</span> · bit.ly/geomaker</div>
        </div>
      </div>
      <div style={{position: 'absolute', right: 110, top: 250, width: 300, opacity: qr, transform: `translateY(${(1 - qr) * 18}px)`}}>
        <div style={{background: '#f7f5ef', borderRadius: 20, padding: 18, boxShadow: '0 24px 60px rgba(0,0,0,0.35)'}}>
          <Img src={staticFile('r1058-github-qr.png')} style={{width: '100%', display: 'block', borderRadius: 8}} />
          <div style={{color: '#14532d', fontSize: 15, fontWeight: 900, textAlign: 'center', marginTop: 10}}>Aponte a câmera para o GitHub</div>
        </div>
      </div>
      <div style={{position: 'absolute', left: 500, top: 600, width: 860, opacity: ease(frame, 55, 20)}}>
        <div style={{borderLeft: `4px solid ${GOLD}`, paddingLeft: 18, color: MUTED, fontSize: 20, lineHeight: 1.45}}>
          Obrigado, professoras, coordenação e gestão.
        </div>
      </div>
      <div style={{position: 'absolute', left: 110, bottom: 145, display: 'flex', alignItems: 'center', gap: 18, opacity: ease(frame, 85, 20)}}>
        <div style={{background: '#f7f5ef', borderRadius: 10, padding: 7}}><Img src={staticFile('r1058-airam-logo.png')} style={{width: 230, display: 'block'}} /></div>
        <div style={{color: MUTED, fontSize: 17}}>Escola de Cidadania Airam Veras · Crateús/CE<br/><span style={{color: DIM, fontSize: 14}}>Dados agregados; sem exposição de estudantes.</span></div>
      </div>
      <CaptionBar frame={frame + SCENES[18].startFrame} />
    </AbsoluteFill>
  );
};

export const AiramVideo: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: BG, fontFamily: FONT}}>
      <Background frame={frame} />
      <Scene index={0}><Opening /></Scene>
      <Scene index={1}><MapScene /></Scene>
      <Scene index={2}><Diagnosis /></Scene>
      <Scene index={3}><Schedule /></Scene>
      <Scene index={4}><Overview component="LP" index={4} /></Scene>
      {SKILLS.filter((skill) => skill.component === 'LP').map((skill, i) => (
        <Scene key={skill.id} index={5 + i}><SkillScene skill={skill} index={5 + i} /></Scene>
      ))}
      <Scene index={11}><Overview component="MAT" index={11} /></Scene>
      {SKILLS.filter((skill) => skill.component === 'MAT').map((skill, i) => (
        <Scene key={skill.id} index={12 + i}><SkillScene skill={skill} index={12 + i} /></Scene>
      ))}
      <Scene index={17}><Interventions /></Scene>
      <Scene index={18}><Author /></Scene>
      <Watermark />
    </AbsoluteFill>
  );
};
