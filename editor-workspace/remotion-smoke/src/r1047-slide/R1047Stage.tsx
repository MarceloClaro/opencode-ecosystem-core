import React from 'react';
import {
  AbsoluteFill,
  OffthreadVideo,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import {SceneOne, SceneThree, SceneTwo, Step} from './R1047Slide';

const BG = '#0B0912';
const INK = '#F7F5FF';
const MUTED = '#B9B1CE';
const PURPLE = '#A78BFA';
const LIME = '#A3E635';
const BORDER = 'rgba(167, 139, 250, 0.34)';
const SPRING = {damping: 15.35, stiffness: 115, mass: 1};

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const sceneWindow = (frame: number, start: number, end: number) => {
  if (frame < start - 12 || frame > end + 12) return {opacity: 0, blur: 6};
  const opacity = interpolate(
    frame,
    [start - 12, start + 8, end - 8, end + 12],
    [0, 1, 1, 0],
    clamp,
  );
  const edge = Math.min(
    Math.abs(frame - (start - 6)),
    Math.abs(frame - (end + 6)),
  );
  const blur = interpolate(edge, [0, 10], [4, 0], clamp);
  return {opacity, blur};
};

const Grain = () => (
  <div
    style={{
      position: 'absolute',
      inset: 0,
      opacity: 0.055,
      pointerEvents: 'none',
      mixBlendMode: 'overlay',
      backgroundImage:
        "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.9'/%3E%3C/svg%3E\")",
      backgroundSize: '160px 160px',
    }}
  />
);

const Vignette = () => (
  <div
    style={{
      position: 'absolute',
      inset: 0,
      pointerEvents: 'none',
      background:
        'radial-gradient(ellipse at center, transparent 38%, rgba(0,0,0,0.50) 100%)',
    }}
  />
);

const PresenterCard = ({frame}: {frame: number}) => {
  const enter = Math.min(1, Math.max(0, spring({
    frame,
    fps: 30,
    config: {damping: 17, stiffness: 80, mass: 1.1},
  })));
  const tilt = interpolate(frame, [0, 599], [-2.4, 1.2], clamp);
  const angle = (frame * 0.55) % 360;
  return (
    <div
      style={{
        position: 'absolute',
        left: 1312,
        top: 224,
        width: 536,
        padding: 3,
        borderRadius: 32,
        background: `conic-gradient(from ${angle}deg, rgba(167,139,250,0.95), rgba(163,230,53,0.38), rgba(139,92,246,0.18), rgba(167,139,250,0.95))`,
        boxShadow: '0 28px 90px rgba(91, 33, 182, 0.42)',
        opacity: enter,
        transform: `translateX(${(1 - enter) * 80}px) perspective(1200px) rotateY(${tilt}deg)`,
        transformOrigin: 'right center',
      }}
    >
      <div
        style={{
          position: 'relative',
          width: 530,
          height: 660,
          borderRadius: 29,
          overflow: 'hidden',
          background: '#120D1D',
        }}
      >
        <OffthreadVideo
          src={staticFile('r1047-presenter-card.mp4')}
          muted
          style={{width: '100%', height: '100%', objectFit: 'cover'}}
        />
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            bottom: 0,
            padding: '44px 20px 16px',
            background: 'linear-gradient(transparent, rgba(5,4,10,0.92))',
            color: INK,
            fontSize: 14,
            fontWeight: 800,
            letterSpacing: 1,
          }}
        >
          APRESENTADORA  •  VOZ SINTÉTICA
        </div>
        <div
          style={{
            position: 'absolute',
            left: 16,
            top: 16,
            width: 9,
            height: 9,
            borderRadius: 5,
            background: LIME,
            boxShadow: '0 0 14px rgba(163,230,53,0.9)',
          }}
        />
      </div>
    </div>
  );
};

export const R1047Stage = () => {
  const frame = useCurrentFrame();
  const scene = frame < 156 ? 1 : frame < 288 ? 2 : 3;
  const progress = interpolate(frame, [0, 599], [0, 100], clamp);
  const drift = interpolate(frame, [0, 599], [0, -90], clamp);
  const titleRaw = spring({frame, fps: 30, config: SPRING});
  const titleIn = Math.min(1, Math.max(0, titleRaw));
  const titleShine = interpolate(frame, [0, 599], [0, 220], clamp);
  const window = sceneWindow(
    frame,
    scene === 1 ? 0 : scene === 2 ? 150 : 282,
    scene === 1 ? 156 : scene === 2 ? 288 : 600,
  );
  return (
    <AbsoluteFill
      style={{
        background: BG,
        color: INK,
        fontFamily: 'DejaVu Sans, Arial, sans-serif',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          position: 'absolute', width: 760, height: 760, borderRadius: 380,
          left: -260, top: -300, background: 'rgba(139,92,246,0.26)',
          filter: 'blur(100px)', transform: `translate(${drift}px, ${-drift / 2}px)`,
        }}
      />
      <div
        style={{
          position: 'absolute', width: 620, height: 620, borderRadius: 310,
          right: -220, bottom: -260, background: 'rgba(163,230,53,0.13)',
          filter: 'blur(110px)', transform: `translate(${-drift}px, ${drift / 3}px)`,
        }}
      />
      <div
        style={{
          position: 'absolute', inset: 0, opacity: 0.16,
          backgroundImage:
            'linear-gradient(rgba(167,139,250,0.16) 1px, transparent 1px), linear-gradient(90deg, rgba(167,139,250,0.16) 1px, transparent 1px)',
          backgroundSize: '56px 56px',
          transform: `translateY(${drift / 4}px)`,
        }}
      />
      <Vignette />
      <Grain />

      <div style={{position: 'absolute', left: 76, top: 50, color: PURPLE, fontSize: 15, fontWeight: 900, letterSpacing: 2}}>
        QISKIT  •  FUNDAMENTOS
      </div>
      <div
        style={{
          position: 'absolute', left: 76, top: 88, fontSize: 58, fontWeight: 900,
          letterSpacing: -1.2, opacity: titleIn, color: INK,
          transform: `translateY(${(1 - titleIn) * 24}px)`,
          textShadow: '0 0 34px rgba(167,139,250,0.28)',
        }}
      >
        Do acesso ao <span style={{color: LIME}}>limite</span>
        <span style={{display: 'inline-block', width: 78, height: 8, marginLeft: 18, borderRadius: 8, background: `linear-gradient(90deg, ${LIME}, rgba(163,230,53,0))`, opacity: 0.5 + titleShine / 440, verticalAlign: 'middle'}} />
      </div>
      <div style={{position: 'absolute', left: 76, top: 160, color: MUTED, fontSize: 23}}>
        Como os chips de 100+ qubits mudam a escala
      </div>
      <div style={{position: 'absolute', left: 76, top: 216, width: 1160, display: 'flex', gap: 14}}>
        <Step index="1" label="Acesso" active={scene === 1} done={scene > 1} />
        <Step index="2" label="Mudança" active={scene === 2} done={scene > 2} />
        <Step index="3" label="Limite" active={scene === 3} done={false} />
      </div>
      <div style={{position: 'absolute', left: 76, top: 258, width: 1160, height: 3, background: 'rgba(255,255,255,0.08)', borderRadius: 3}}>
        <div style={{width: `${progress}%`, height: 3, background: LIME, borderRadius: 3}} />
      </div>

      <div
        style={{
          position: 'absolute', left: 76, top: 300, width: 1160, height: 690,
          opacity: window.opacity, filter: `blur(${window.blur}px)`,
        }}
      >
        {scene === 1 && <SceneOne frame={frame} />}
        {scene === 2 && <SceneTwo frame={frame} />}
        {scene === 3 && <SceneThree frame={frame} />}
      </div>

      <PresenterCard frame={frame} />

      <div style={{position: 'absolute', left: 76, bottom: 30, color: MUTED, fontSize: 14}}>
        Fonte: Qiskit  •  adaptação didática em PT-BR  •  lip sync e voz sintética
      </div>
      <div style={{position: 'absolute', right: 76, bottom: 30, color: BORDER, fontSize: 13}}>
        R1047  •  cena didática
      </div>
    </AbsoluteFill>
  );
};
