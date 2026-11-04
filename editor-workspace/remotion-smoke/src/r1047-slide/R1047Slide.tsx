import React from 'react';
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
} from 'remotion';

const BG = '#0B0912';
const PANEL = 'rgba(20, 16, 32, 0.86)';
const CARD = 'rgba(29, 23, 44, 0.92)';
const INK = '#F7F5FF';
const MUTED = '#B9B1CE';
const PURPLE = '#A78BFA';
const ACCENT = '#8B5CF6';
const LIME = '#A3E635';
const BORDER = 'rgba(167, 139, 250, 0.34)';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const fadeUp = (frame: number, start: number, duration = 20) => {
  const progress = interpolate(frame, [start, start + duration], [0, 1], {
    ...clamp,
    easing: Easing.out(Easing.cubic),
  });
  return {
    opacity: progress,
    transform: `translateY(${(1 - progress) * 20}px)`,
  };
};

const SceneBadge = ({label}: {label: string}) => (
  <div
    style={{
      position: 'absolute',
      right: 34,
      top: 30,
      color: PURPLE,
      fontSize: 14,
      fontWeight: 800,
      letterSpacing: 1.6,
      border: `1px solid ${BORDER}`,
      borderRadius: 999,
      padding: '4px 10px',
      background: 'rgba(139, 92, 246, 0.12)',
    }}
  >
    {label}
  </div>
);

const Step = ({
  index,
  label,
  active,
  done,
}: {
  index: string;
  label: string;
  active: boolean;
  done: boolean;
}) => (
  <div style={{display: 'flex', alignItems: 'center', gap: 8, flex: 1}}>
    <div
      style={{
        width: 26,
        height: 26,
        borderRadius: 13,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: 12,
        fontWeight: 900,
        color: done || active ? BG : MUTED,
        background: done || active ? LIME : 'rgba(255,255,255,0.06)',
        border: `1px solid ${done || active ? LIME : BORDER}`,
      }}
    >
      {done ? '✓' : index}
    </div>
    <div
      style={{
        fontSize: 14,
        fontWeight: active ? 800 : 600,
        color: active ? INK : MUTED,
      }}
    >
      {label}
    </div>
  </div>
);

const Card = ({
  title,
  subtitle,
  accent,
  children,
  style,
}: {
  title: string;
  subtitle: string;
  accent: string;
  children?: React.ReactNode;
  style?: React.CSSProperties;
}) => (
  <div
    style={{
      background: CARD,
      border: `1px solid ${BORDER}`,
      borderRadius: 16,
      padding: '20px 22px',
      minHeight: 170,
      boxSizing: 'border-box',
      boxShadow: '0 18px 40px rgba(0,0,0,0.28)',
      ...style,
    }}
  >
    <div style={{fontSize: 27, fontWeight: 900, color: INK}}>{title}</div>
    <div style={{fontSize: 18, color: MUTED, marginTop: 4}}>{subtitle}</div>
    <div
      style={{
        marginTop: 18,
        height: 6,
        width: 100,
        background: accent,
        borderRadius: 6,
      }}
    />
    {children ?? (
      <div style={{marginTop: 22, fontSize: 13, color: MUTED}}>
        processador
      </div>
    )}
  </div>
);

const ChipGrid = ({count, color}: {count: number; color: string}) => (
  <div
    style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(7, 14px)',
      gap: 4,
      marginTop: 18,
    }}
  >
    {Array.from({length: count}).map((_, index) => (
      <div
        key={index}
        style={{
          width: 14,
          height: 14,
          borderRadius: 3,
          border: `1px solid ${color}`,
          background: 'rgba(139, 92, 246, 0.18)',
        }}
      />
    ))}
  </div>
);

const SceneOne = ({frame}: {frame: number}) => {
  const count = Math.min(100, Math.max(0, Math.round(
    interpolate(frame, [10, 105], [0, 100], clamp),
  )));
  return (
    <div style={{paddingTop: 8}}>
      <div style={{...fadeUp(frame, 0), color: LIME, fontSize: 14, fontWeight: 900, letterSpacing: 1.4}}>
        ATO 01 · ACESSO
      </div>
      <div style={{...fadeUp(frame, 4), color: INK, fontSize: 36, fontWeight: 900, marginTop: 6}}>
        A escala mudou
      </div>
      <div style={{...fadeUp(frame, 8), color: MUTED, fontSize: 19, marginTop: 6}}>
        Processadores quânticos com mais de cem qubits.
      </div>
      <div style={{display: 'flex', gap: 18, marginTop: 24}}>
        <div style={{...fadeUp(frame, 20), flex: 1.15}}>
          <div style={{fontSize: 104, lineHeight: 1, fontWeight: 900, color: LIME}}>
            {count}+
          </div>
          <div style={{fontSize: 19, color: MUTED, marginTop: 2}}>qubits disponíveis</div>
          <div style={{marginTop: 20, height: 4, background: 'rgba(163,230,53,0.18)', borderRadius: 4}}>
            <div style={{width: `${count}%`, height: 4, background: LIME, borderRadius: 4}} />
          </div>
        </div>
        <div style={{...fadeUp(frame, 30), flex: 1}}>
          <Card title="Eagle" subtitle="127 qubits" accent={ACCENT} />
        </div>
        <div style={{...fadeUp(frame, 40), flex: 1}}>
          <Card title="Heron" subtitle="133 qubits × p" accent={ACCENT} />
        </div>
      </div>
      <div style={{...fadeUp(frame, 52), marginTop: 20, display: 'flex', gap: 10}}>
        <div style={{fontSize: 13, color: MUTED, border: `1px solid ${BORDER}`, borderRadius: 999, padding: '6px 10px'}}>
          acesso ampliado
        </div>
        <div style={{fontSize: 13, color: MUTED, border: `1px solid ${BORDER}`, borderRadius: 999, padding: '6px 10px'}}>
          arquitetura modular
        </div>
      </div>
    </div>
  );
};

const SceneTwo = ({frame}: {frame: number}) => {
  const fadeSmall = interpolate(frame, [160, 220], [1, 0.42], clamp);
  return (
    <div style={{paddingTop: 8}}>
      <div style={{...fadeUp(frame, 0), color: LIME, fontSize: 14, fontWeight: 900, letterSpacing: 1.4}}>
        ATO 02 · MUDANÇA
      </div>
      <div style={{...fadeUp(frame, 4), color: INK, fontSize: 36, fontWeight: 900, marginTop: 6}}>
        Menos chips pequenos
      </div>
      <div style={{...fadeUp(frame, 8), color: MUTED, fontSize: 19, marginTop: 6}}>
        Os menores saíram de linha para abrir espaço aos maiores.
      </div>
      <div style={{display: 'flex', gap: 16, marginTop: 24}}>
        <div style={{...fadeUp(frame, 18), flex: 1, opacity: fadeSmall}}>
          <Card title="Antes" subtitle="chips menores" accent="#9CA3AF">
            <ChipGrid count={28} color="#9CA3AF" />
          </Card>
        </div>
        <div style={{...fadeUp(frame, 34), flex: 1}}>
          <Card title="Agora" subtitle="100+ qubits" accent={LIME}>
            <ChipGrid count={77} color={ACCENT} />
          </Card>
        </div>
      </div>
      <div style={{...fadeUp(frame, 52), marginTop: 22, display: 'flex', alignItems: 'center', gap: 12}}>
        <div style={{width: 44, height: 44, borderRadius: 22, background: LIME, color: BG, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, fontWeight: 900}}>
          →
        </div>
        <div style={{fontSize: 18, color: INK, fontWeight: 800}}>
          prioridade para capacidade e disponibilidade
        </div>
      </div>
    </div>
  );
};

const SceneThree = ({frame}: {frame: number}) => (
  <div style={{paddingTop: 8}}>
    <div style={{...fadeUp(frame, 0), color: LIME, fontSize: 14, fontWeight: 900, letterSpacing: 1.4}}>
      ATO 03 · LIMITE
    </div>
    <div style={{...fadeUp(frame, 4), color: INK, fontSize: 36, fontWeight: 900, marginTop: 6}}>
      O limite da simulação
    </div>
    <div style={{...fadeUp(frame, 8), color: MUTED, fontSize: 19, marginTop: 6}}>
      Alguns tamanhos ainda são simuláveis classicamente.
    </div>
    <div style={{...fadeUp(frame, 20), marginTop: 24, background: PANEL, border: `1px solid ${ACCENT}`, borderRadius: 16, padding: '22px 24px'}}>
      <div style={{fontSize: 22, fontWeight: 900, color: PURPLE}}>O que muda com 100+ qubits?</div>
      <div style={{fontSize: 18, lineHeight: 1.45, color: INK, marginTop: 10}}>
        Os chips maiores ampliam o alcance da computação quântica. Eles permitem
        atacar problemas que a simulação clássica não alcança — sem transformar
        predição em medição.
      </div>
      <div style={{display: 'flex', gap: 12, marginTop: 16}}>
        <div style={{flex: 1, background: 'rgba(255,255,255,0.05)', borderRadius: 10, padding: '12px 14px', fontSize: 15, color: MUTED}}>
          <strong style={{color: INK}}>Simulação clássica</strong><br />útil, mas limitada
        </div>
        <div style={{flex: 1, background: 'rgba(255,255,255,0.05)', borderRadius: 10, padding: '12px 14px', fontSize: 15, color: MUTED}}>
          <strong style={{color: INK}}>Computação quântica</strong><br />outro regime de escala
        </div>
      </div>
    </div>
    <div style={{...fadeUp(frame, 40), marginTop: 16, fontSize: 15, color: LIME, fontWeight: 800}}>
      Menos chips pequenos → mais capacidade de 100+ qubits
    </div>
  </div>
);

export const R1047Slide = () => {
  const frame = useCurrentFrame();
  const scene = frame < 156 ? 1 : frame < 288 ? 2 : 3;
  const progress = interpolate(frame, [0, 599], [0, 100], clamp);
  const drift = interpolate(frame, [0, 599], [0, -80], clamp);
  const sceneOpacity = (start: number, end: number) => {
    if (frame < start - 10 || frame > end + 10) return 0;
    return interpolate(frame, [start - 10, start + 8, end - 8, end + 10], [0, 1, 1, 0], clamp);
  };
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'DejaVu Sans, Arial, sans-serif', color: INK, overflow: 'hidden'}}>
      <div
        style={{
          position: 'absolute', width: 520, height: 520, borderRadius: 260,
          left: -180, top: -160, background: 'rgba(139,92,246,0.30)',
          filter: 'blur(80px)', transform: `translate(${drift}px, ${-drift / 2}px)`,
        }}
      />
      <div
        style={{
          position: 'absolute', width: 430, height: 430, borderRadius: 215,
          right: -150, bottom: -170, background: 'rgba(163,230,53,0.16)',
          filter: 'blur(90px)', transform: `translate(${-drift}px, ${drift / 3}px)`,
        }}
      />
      <div
        style={{
          position: 'absolute', inset: 0, opacity: 0.18,
          backgroundImage: 'linear-gradient(rgba(167,139,250,0.18) 1px, transparent 1px), linear-gradient(90deg, rgba(167,139,250,0.18) 1px, transparent 1px)',
          backgroundSize: '46px 46px',
          transform: `translateY(${drift / 4}px)`,
        }}
      />
      <div style={{position: 'absolute', left: 34, top: 30, color: PURPLE, fontSize: 14, fontWeight: 900, letterSpacing: 1.8}}>
        QISKIT  •  FUNDAMENTOS
      </div>
      <SceneBadge label={`0${scene}/03`} />
      <div style={{position: 'absolute', left: 34, top: 56, color: INK, fontSize: 41, fontWeight: 900, letterSpacing: -0.8}}>
        Do acesso ao limite
      </div>
      <div style={{position: 'absolute', left: 34, top: 106, color: MUTED, fontSize: 19}}>
        Como os chips de 100+ qubits mudam a escala
      </div>
      <div style={{position: 'absolute', left: 34, top: 148, width: 867, display: 'flex', gap: 12}}>
        <Step index="1" label="Acesso" active={scene === 1} done={scene > 1} />
        <Step index="2" label="Mudança" active={scene === 2} done={scene > 2} />
        <Step index="3" label="Limite" active={scene === 3} done={false} />
      </div>
      <div style={{position: 'absolute', left: 34, top: 190, width: 867, height: 3, background: 'rgba(255,255,255,0.08)', borderRadius: 3}}>
        <div style={{width: `${progress}%`, height: 3, background: LIME, borderRadius: 3}} />
      </div>
      <div style={{position: 'absolute', left: 34, right: 34, top: 222, bottom: 72}}>
        {scene === 1 && <div style={{opacity: sceneOpacity(0, 156)}}><SceneOne frame={frame} /></div>}
        {scene === 2 && <div style={{opacity: sceneOpacity(150, 288)}}><SceneTwo frame={frame} /></div>}
        {scene === 3 && <div style={{opacity: sceneOpacity(282, 600)}}><SceneThree frame={frame} /></div>}
      </div>
      <div style={{position: 'absolute', left: 34, bottom: 24, color: MUTED, fontSize: 13}}>
        Fonte: Qiskit  •  adaptação didática em PT-BR  •  voz sintética
      </div>
    </AbsoluteFill>
  );
};
