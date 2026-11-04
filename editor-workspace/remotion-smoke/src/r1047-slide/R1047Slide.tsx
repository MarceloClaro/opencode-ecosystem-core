import React from 'react';
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
} from 'remotion';

const BG = '#F5F3FF';
const INK = '#161616';
const MUTED = '#525252';
const PURPLE = '#6929C4';
const ACCENT = '#8B5CF6';
const CARD = '#FFFFFF';
const BORDER = '#D0D0D8';
const CALLOUT = '#F0EAFB';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const fadeUp = (frame: number, start: number, duration = 18) => {
  const progress = interpolate(frame, [start, start + duration], [0, 1], {
    ...clamp,
    easing: Easing.out(Easing.cubic),
  });
  return {
    opacity: progress,
    transform: `translateY(${(1 - progress) * 18}px)`,
  };
};

const SceneBadge = ({label}: {label: string}) => (
  <div
    style={{
      position: 'absolute',
      right: 36,
      top: 30,
      color: PURPLE,
      fontSize: 15,
      fontWeight: 700,
      letterSpacing: 1.2,
    }}
  >
    {label}
  </div>
);

const Card = ({
  title,
  subtitle,
  accent,
  style,
  children,
}: {
  title: string;
  subtitle: string;
  accent: string;
  style?: React.CSSProperties;
  children?: React.ReactNode;
}) => (
  <div
    style={{
      background: CARD,
      border: `2px solid ${BORDER}`,
      borderRadius: 14,
      padding: '22px 24px',
      minHeight: 168,
      boxSizing: 'border-box',
      ...style,
    }}
  >
    <div style={{fontSize: 28, fontWeight: 800, color: INK}}>{title}</div>
    <div style={{fontSize: 19, color: MUTED, marginTop: 6}}>{subtitle}</div>
    <div
      style={{
        marginTop: 26,
        height: 8,
        width: 120,
        background: accent,
        borderRadius: 8,
      }}
    />
    {children ?? (
      <div style={{marginTop: 22, fontSize: 14, color: MUTED}}>
        processador
      </div>
    )}
  </div>
);

const ChipGrid = ({count, color}: {count: number; color: string}) => (
  <div
    style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(7, 16px)',
      gap: 4,
      marginTop: 18,
    }}
  >
    {Array.from({length: count}).map((_, index) => (
      <div
        key={index}
        style={{
          width: 16,
          height: 16,
          borderRadius: 3,
          border: `1px solid ${color}`,
          background: '#E8E8F2',
        }}
      />
    ))}
  </div>
);

const SceneOne = ({frame}: {frame: number}) => {
  const count = Math.min(100, Math.max(0, Math.round(
    interpolate(frame, [20, 110], [0, 100], clamp),
  )));
  return (
    <div style={{position: 'absolute', left: 36, top: 178, width: 863}}>
      <div style={{...fadeUp(frame, 0), color: PURPLE, fontSize: 16, fontWeight: 800, letterSpacing: 1}}>
        CENA 01 · CONTEXTO
      </div>
      <div style={{...fadeUp(frame, 4), color: INK, fontSize: 36, fontWeight: 800, marginTop: 8}}>
        Acesso ampliado
      </div>
      <div style={{...fadeUp(frame, 8), color: MUTED, fontSize: 20, marginTop: 8}}>
        Processadores quânticos com mais de cem qubits.
      </div>
      <div style={{display: 'flex', gap: 20, marginTop: 28}}>
        <div style={{...fadeUp(frame, 24), flex: 1}}>
          <div style={{fontSize: 96, lineHeight: 1, fontWeight: 900, color: PURPLE}}>
            {count}+
          </div>
          <div style={{fontSize: 20, color: MUTED, marginTop: 4}}>qubits disponíveis</div>
        </div>
        <div style={{...fadeUp(frame, 34), flex: 1}}>
          <Card title="Eagle" subtitle="127 qubits" accent={ACCENT} />
          <div style={{marginTop: 12, fontSize: 13, color: MUTED}}>
            maior capacidade acessível
          </div>
        </div>
        <div style={{...fadeUp(frame, 42), flex: 1}}>
          <Card title="Heron" subtitle="133 qubits × p" accent={ACCENT} />
          <div style={{marginTop: 12, fontSize: 13, color: MUTED}}>
            arquitetura modular
          </div>
        </div>
      </div>
    </div>
  );
};

const SceneTwo = ({frame}: {frame: number}) => {
  const fadeSmall = interpolate(frame, [160, 215], [1, 0.38], clamp);
  return (
    <div style={{position: 'absolute', left: 36, top: 178, width: 863}}>
      <div style={{...fadeUp(frame, 150), color: PURPLE, fontSize: 16, fontWeight: 800, letterSpacing: 1}}>
        CENA 02 · MUDANÇA
      </div>
      <div style={{...fadeUp(frame, 154), color: INK, fontSize: 36, fontWeight: 800, marginTop: 8}}>
        Menos chips pequenos
      </div>
      <div style={{...fadeUp(frame, 158), color: MUTED, fontSize: 20, marginTop: 8}}>
        Os menores saíram de linha para abrir espaço aos maiores.
      </div>
      <div style={{display: 'flex', gap: 16, marginTop: 30}}>
        <div style={{...fadeUp(frame, 164), flex: 1, opacity: fadeSmall}}>
          <Card title="Antes" subtitle="chips menores" accent="#9CA3AF">
            <ChipGrid count={28} color="#9CA3AF" />
          </Card>
        </div>
        <div style={{...fadeUp(frame, 190), flex: 1}}>
          <Card title="Agora" subtitle="100+ qubits" accent={ACCENT}>
            <ChipGrid count={77} color={ACCENT} />
          </Card>
        </div>
      </div>
      <div style={{...fadeUp(frame, 220), marginTop: 26, display: 'flex', alignItems: 'center', gap: 14}}>
        <div style={{width: 52, height: 52, borderRadius: 26, background: PURPLE, color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 28, fontWeight: 800}}>
          →
        </div>
        <div style={{fontSize: 19, color: INK, fontWeight: 700}}>
          prioridade para capacidade e disponibilidade
        </div>
      </div>
    </div>
  );
};

const SceneThree = ({frame}: {frame: number}) => (
  <div style={{position: 'absolute', left: 36, top: 178, width: 863}}>
    <div style={{...fadeUp(frame, 286), color: PURPLE, fontSize: 16, fontWeight: 800, letterSpacing: 1}}>
      CENA 03 · POR QUÊ
    </div>
    <div style={{...fadeUp(frame, 290), color: INK, fontSize: 36, fontWeight: 800, marginTop: 8}}>
      O limite da simulação
    </div>
    <div style={{...fadeUp(frame, 294), color: MUTED, fontSize: 20, marginTop: 8}}>
      Alguns tamanhos ainda são simuláveis classicamente.
    </div>
    <div style={{...fadeUp(frame, 310), marginTop: 26, background: CALLOUT, border: `2px solid ${ACCENT}`, borderRadius: 14, padding: '24px 26px'}}>
      <div style={{fontSize: 23, fontWeight: 800, color: PURPLE}}>O que muda com 100+ qubits?</div>
      <div style={{fontSize: 19, lineHeight: 1.45, color: INK, marginTop: 12}}>
        Os chips maiores ampliam o alcance da computação quântica. Eles permitem
        atacar problemas que a simulação clássica não alcança — sem transformar
        predição em medição.
      </div>
      <div style={{display: 'flex', gap: 12, marginTop: 18}}>
        <div style={{flex: 1, background: 'white', borderRadius: 10, padding: '12px 14px', fontSize: 16, color: MUTED}}>
          <strong style={{color: INK}}>Simulação clássica</strong><br />útil, mas limitada
        </div>
        <div style={{flex: 1, background: 'white', borderRadius: 10, padding: '12px 14px', fontSize: 16, color: MUTED}}>
          <strong style={{color: INK}}>Computação quântica</strong><br />outro regime de escala
        </div>
      </div>
    </div>
    <div style={{...fadeUp(frame, 350), marginTop: 18, fontSize: 16, color: PURPLE, fontWeight: 800}}>
      Menos chips pequenos  →  mais capacidade de 100+ qubits
    </div>
  </div>
);

export const R1047Slide = () => {
  const frame = useCurrentFrame();
  const scene = frame < 156 ? 1 : frame < 288 ? 2 : 3;
  const progress = interpolate(frame, [0, 599], [0, 100], clamp);
  return (
    <AbsoluteFill style={{background: BG, fontFamily: 'DejaVu Sans, Arial, sans-serif', color: INK}}>
      <div style={{position: 'absolute', left: 36, top: 30, color: PURPLE, fontSize: 16, fontWeight: 800, letterSpacing: 1.4}}>
        QISKIT  •  FUNDAMENTOS
      </div>
      <SceneBadge label={`0${scene}/03`} />
      <div style={{position: 'absolute', left: 36, top: 58, color: INK, fontSize: 37, fontWeight: 900}}>
        Computação quântica na prática
      </div>
      <div style={{position: 'absolute', left: 36, top: 108, color: MUTED, fontSize: 21}}>
        Por que a IBM prioriza chips de 100+ qubits?
      </div>
      <div style={{position: 'absolute', left: 36, top: 144, width: 863, height: 4, background: '#DDD6FE', borderRadius: 4}}>
        <div style={{width: `${progress}%`, height: 4, background: ACCENT, borderRadius: 4}} />
      </div>
      {scene === 1 && <SceneOne frame={frame} />}
      {scene === 2 && <SceneTwo frame={frame} />}
      {scene === 3 && <SceneThree frame={frame} />}
      <div style={{position: 'absolute', left: 36, bottom: 22, color: MUTED, fontSize: 14}}>
        Fonte: Qiskit  •  adaptação didática em PT-BR
      </div>
    </AbsoluteFill>
  );
};
