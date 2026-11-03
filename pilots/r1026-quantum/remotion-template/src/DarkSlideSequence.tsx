import React from "react";
import {
  AbsoluteFill,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const BG = "#0F0B18";
const INK = "#FFFFFF";
const MUTED = "#B9B4C7";
const PURPLE = "#8B5CF6";
const ACCENT = "#8B5CF6";
const CARD = "#171022";
const BORDER = "rgba(139,92,246,0.35)";
const CALLOUT = "#1B1233";
const FONT = "DejaVu Sans, sans-serif";

const gridStyle: React.CSSProperties = {
  backgroundColor: "#1B1233",
  border: "2px solid #8B5CF6",
  backgroundImage:
    "linear-gradient(#3A2A5A 1px, transparent 1px), linear-gradient(90deg, #3A2A5A 1px, transparent 1px)",
  backgroundSize: "14px 14px",
};

const ChipEagle: React.FC<{ size?: number }> = ({ size = 140 }) => (
  <div
    style={{
      ...gridStyle,
      width: size,
      height: size * 0.72,
      borderRadius: 6,
      transform: "rotate(45deg)",
    }}
  />
);

const ChipHeron: React.FC<{ scale?: number }> = ({ scale = 1 }) => (
  <div style={{ display: "flex", alignItems: "flex-end", transform: `scale(${scale})` }}>
    <div style={{ ...gridStyle, width: 52, height: 52, borderRadius: 4 }} />
    <div style={{ ...gridStyle, width: 52, height: 52, borderRadius: 4, marginBottom: 26 }} />
    <div style={{ ...gridStyle, width: 52, height: 52, borderRadius: 4, marginBottom: 52 }} />
  </div>
);

const Header: React.FC<{ progress: number; scene: string }> = ({ progress, scene }) => (
  <>
    <div
      style={{
        position: "absolute",
        left: 36,
        top: 28,
        fontSize: 15,
        fontWeight: 700,
        letterSpacing: 1,
        color: PURPLE,
        fontFamily: FONT,
      }}
    >
      QISKIT • FUNDAMENTOS
    </div>
    <div
      style={{
        position: "absolute",
        right: 36,
        top: 28,
        fontSize: 15,
        color: MUTED,
        fontFamily: FONT,
      }}
    >
      {scene} / 03
    </div>
    <div
      style={{
        position: "absolute",
        left: 36,
        top: 52,
        width: 863,
        height: 5,
        borderRadius: 3,
        backgroundColor: "#2A1A4A",
      }}
    >
      <div
        style={{
          width: `${progress}%`,
          height: "100%",
          borderRadius: 3,
          backgroundColor: ACCENT,
        }}
      />
    </div>
  </>
);

const Footer: React.FC = () => (
  <>
    <div style={{ position: "absolute", left: 36, top: 744, width: 863, height: 1, backgroundColor: "#2A1A4A" }} />
    <div style={{ position: "absolute", left: 36, top: 764, fontSize: 14, color: MUTED, fontFamily: FONT }}>
      Fonte: Qiskit • adaptação didática
    </div>
  </>
);

const Scene1: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 200 } });
  const exit = interpolate(frame, [duration - 12, duration], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scale = interpolate(enter, [0, 1], [0.9, 1]);
  const pulse = 1 + 0.018 * Math.sin(frame / 7);

  return (
    <div style={{ position: "absolute", inset: 0, opacity: enter * exit, fontFamily: FONT }}>
      <div style={{ position: "absolute", left: 36, top: 86, fontSize: 15, fontWeight: 700, color: PURPLE }}>
        CENA 1 • CONTEXTO
      </div>
      <div style={{ position: "absolute", left: 36, top: 112, fontSize: 40, fontWeight: 700, lineHeight: 1.05, color: INK }}>
        Computação quântica
        <br />
        na prática
      </div>
      <div style={{ position: "absolute", left: 36, top: 212, width: 500, fontSize: 21, color: MUTED }}>
        Processadores IBM com mais de 100 qubits
      </div>
      <div style={{ position: "absolute", left: 36, top: 280, width: 500, fontSize: 22, lineHeight: 1.35, color: INK }}>
        Nos últimos meses, a IBM tornou os processadores de 100+ qubits amplamente disponíveis.
      </div>
      <div
        style={{
          position: "absolute",
          right: 48,
          top: 232,
          fontSize: 120,
          fontWeight: 700,
          color: PURPLE,
          transform: `scale(${scale * pulse})`,
          transformOrigin: "right top",
          filter: "drop-shadow(0 0 16px rgba(105,41,196,0.25))",
        }}
      >
        100+
      </div>
      <div style={{ position: "absolute", right: 58, top: 366, fontSize: 28, color: MUTED }}>
        qubits
      </div>
      <div style={{ position: "absolute", right: 96, top: 420, transform: `scale(${scale})` }}>
        <ChipEagle size={150} />
      </div>
      <div style={{ position: "absolute", left: 36, top: 620, fontSize: 18, fontWeight: 700, color: PURPLE }}>
        Antes: menos qubits  →  Hoje: 100+ qubits
      </div>
      <Footer />
    </div>
  );
};

const Scene2: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const exit = interpolate(frame, [duration - 12, duration], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const card1 = spring({ frame: Math.max(0, frame - 12), fps, config: { damping: 200 } });
  const card2 = spring({ frame: Math.max(0, frame - 28), fps, config: { damping: 200 } });
  const line = interpolate(frame, [20, 55], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const card = (x: number, title: string, subtitle: string, icon: React.ReactNode, enter: number) => (
    <div
      style={{
        position: "absolute",
        left: x,
        top: 190,
        width: 415,
        height: 300,
        borderRadius: 12,
        backgroundColor: CARD,
        border: `2px solid ${BORDER}`,
        opacity: enter * exit,
        transform: `translateY(${(1 - enter) * 28}px)`,
        fontFamily: FONT,
      }}
    >
      <div style={{ position: "absolute", left: 24, top: 22, fontSize: 30, fontWeight: 700, color: INK }}>{title}</div>
      <div style={{ position: "absolute", left: 24, top: 64, fontSize: 21, color: MUTED }}>{subtitle}</div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 130, display: "flex", justifyContent: "center" }}>{icon}</div>
      <div style={{ position: "absolute", left: 24, bottom: 18, fontSize: 14, color: MUTED }}>processador</div>
    </div>
  );

  return (
    <div style={{ position: "absolute", inset: 0, opacity: exit, fontFamily: FONT }}>
      <div style={{ position: "absolute", left: 36, top: 86, fontSize: 15, fontWeight: 700, color: PURPLE }}>
        CENA 2 • MUDANÇA
      </div>
      <div style={{ position: "absolute", left: 36, top: 112, fontSize: 36, fontWeight: 700, color: INK }}>
        Por que os chips menores saíram de linha?
      </div>
      {card(36, "Eagle", "127 qubits", <ChipEagle size={120} />, card1)}
      {card(484, "Heron", "133 qubits × p", <ChipHeron scale={1.15} />, card2)}
      <div style={{ position: "absolute", left: 36, top: 522, width: 863, height: 4, backgroundColor: "#2A1A4A" }}>
        <div style={{ width: `${line}%`, height: "100%", backgroundColor: ACCENT }} />
      </div>
      <div
        style={{
          position: "absolute",
          left: `${line}%`,
          top: 518,
          width: 12,
          height: 12,
          borderRadius: "50%",
          backgroundColor: ACCENT,
          boxShadow: "0 0 12px rgba(139,92,246,0.9)",
          transform: "translateX(-50%)",
        }}
      />
      <div style={{ position: "absolute", left: 36, top: 540, fontSize: 16, color: MUTED }}>menos qubits</div>
      <div style={{ position: "absolute", right: 36, top: 540, fontSize: 16, color: PURPLE, fontWeight: 700 }}>100+ qubits</div>
      <div style={{ position: "absolute", left: 36, top: 588, width: 863, fontSize: 21, lineHeight: 1.3, color: INK }}>
        Os processadores menores foram desativados para abrir espaço aos maiores.
      </div>
      <div style={{ position: "absolute", left: 36, top: 660, fontSize: 18, fontWeight: 700, color: PURPLE }}>
        Mais capacidade, novos problemas.
      </div>
      <Footer />
    </div>
  );
};

const Scene3: React.FC<{ duration: number }> = ({ duration }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const exit = interpolate(frame, [duration - 12, duration], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const enter = spring({ frame, fps, config: { damping: 200 } });
  const bar = interpolate(frame, [10, 55], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const box = (x: number, title: string, text: string, icon: React.ReactNode, delay: number) => {
    const local = spring({ frame: Math.max(0, frame - delay), fps, config: { damping: 200 } });
    return (
      <div
        style={{
          position: "absolute",
          left: x,
          top: 270,
          width: 415,
          height: 230,
          borderRadius: 12,
          backgroundColor: CARD,
          border: `2px solid ${BORDER}`,
          opacity: local * exit,
          transform: `translateY(${(1 - local) * 24}px)`,
          fontFamily: FONT,
        }}
      >
        <div style={{ position: "absolute", left: 22, top: 18, fontSize: 23, fontWeight: 700, color: INK }}>{title}</div>
        <div style={{ position: "absolute", left: 22, top: 54, width: 250, fontSize: 17, lineHeight: 1.3, color: MUTED }}>{text}</div>
        <div style={{ position: "absolute", right: 18, bottom: 18 }}>{icon}</div>
      </div>
    );
  };

  return (
    <div style={{ position: "absolute", inset: 0, opacity: enter * exit, fontFamily: FONT }}>
      <div style={{ position: "absolute", left: 36, top: 86, fontSize: 15, fontWeight: 700, color: PURPLE }}>
        CENA 3 • POR QUÊ
      </div>
      <div style={{ position: "absolute", left: 36, top: 112, fontSize: 36, fontWeight: 700, color: INK }}>
        Alguns tamanhos ainda são simuláveis
      </div>
      <div style={{ position: "absolute", left: 36, top: 178, width: 863, height: 8, borderRadius: 4, backgroundColor: "#2A1A4A" }}>
        <div style={{ width: `${bar}%`, height: "100%", borderRadius: 4, background: "linear-gradient(90deg, #8B5CF6, #6929C4)" }} />
      </div>
      <div
        style={{
          position: "absolute",
          left: `${bar}%`,
          top: 174,
          width: 14,
          height: 14,
          borderRadius: "50%",
          backgroundColor: PURPLE,
          boxShadow: "0 0 12px rgba(105,41,196,0.8)",
          transform: "translateX(-50%)",
        }}
      />
      <div style={{ position: "absolute", left: 36, top: 194, fontSize: 15, color: MUTED }}>simulação clássica</div>
      <div style={{ position: "absolute", right: 36, top: 194, fontSize: 15, color: PURPLE, fontWeight: 700 }}>100+ qubits</div>
      <div style={{ position: "absolute", left: 36, top: 218, fontSize: 14, color: MUTED }}>
        depende do problema e do método de simulação
      </div>
      {box(36, "Simulação clássica", "alguns tamanhos ainda cabem", <ChipEagle size={86} />, 18)}
      {box(484, "Problemas reais", "100+ qubits abrem novos problemas", <ChipHeron scale={0.72} />, 32)}
      <div
        style={{
          position: "absolute",
          left: 36,
          top: 530,
          width: 863,
          height: 180,
          borderRadius: 12,
          backgroundColor: CALLOUT,
          border: `2px solid ${ACCENT}`,
          opacity: enter * exit,
        }}
      >
        <div style={{ position: "absolute", left: 22, top: 18, fontSize: 22, fontWeight: 700, color: PURPLE }}>
          Por que a mudança?
        </div>
        <div style={{ position: "absolute", left: 22, top: 52, width: 810, fontSize: 18, lineHeight: 1.35, color: INK }}>
          Chips maiores abrem espaço para problemas que a simulação não alcança. É por isso que os processadores menores saíram de linha.
        </div>
      </div>
      <Footer />
    </div>
  );
};

export const DarkSlideSequence: React.FC = () => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, 600], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scene = frame < 170 ? "01" : frame < 379 ? "02" : "03";
  return (
    <AbsoluteFill style={{ backgroundColor: BG, fontFamily: FONT }}>
      <Header progress={progress} scene={scene} />
      <Sequence from={0} durationInFrames={164}>
        <Scene1 duration={164} />
      </Sequence>
      <Sequence from={170} durationInFrames={197}>
        <Scene2 duration={197} />
      </Sequence>
      <Sequence from={379} durationInFrames={221}>
        <Scene3 duration={221} />
      </Sequence>
    </AbsoluteFill>
  );
};
