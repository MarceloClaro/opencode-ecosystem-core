import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const base: React.CSSProperties = {
  backgroundColor: "#0B0B0F",
  color: "white",
  fontFamily: "DejaVu Sans, sans-serif",
};

const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const entrance = spring({ frame, fps, config: { damping: 200 } });
  const line = interpolate(frame, [8, 45], [0, 520], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const subtitle = interpolate(frame, [32, 58], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill
      style={{
        ...base,
        background: "radial-gradient(circle at 18% 22%, #1b1233, #0B0B0F 62%)",
      }}
    >
      <div
        style={{
          position: "absolute",
          left: 120,
          top: 300,
          opacity: entrance,
          transform: `translateY(${(1 - entrance) * 30}px)`,
        }}
      >
        <div style={{ width: line, height: 6, background: "#8B5CF6", marginBottom: 28 }} />
        <div style={{ fontSize: 64, fontWeight: 700, letterSpacing: -1, lineHeight: 1.1 }}>
          Circuitos quânticos
          <br />
          em larga escala
        </div>
        <div style={{ fontSize: 28, opacity: 0.78 * subtitle, marginTop: 22 }}>
          Qiskit • 100+ qubits • estudo técnico
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          left: 120,
          bottom: 100,
          fontSize: 20,
          letterSpacing: 3,
          opacity: 0.5,
        }}
      >
        OPENCODE ECOSYSTEM CORE
      </div>
    </AbsoluteFill>
  );
};

const Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const entrance = spring({ frame, fps, config: { damping: 200 } });
  const line = interpolate(frame, [6, 40], [0, 420], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill
      style={{
        ...base,
        background: "radial-gradient(circle at 82% 78%, #1b1233, #0B0B0F 62%)",
      }}
    >
      <div
        style={{
          position: "absolute",
          left: 120,
          top: 330,
          opacity: entrance,
          transform: `translateY(${(1 - entrance) * 24}px)`,
        }}
      >
        <div style={{ width: line, height: 6, background: "#8B5CF6", marginBottom: 26 }} />
        <div style={{ fontSize: 56, fontWeight: 700 }}>Fonte: Qiskit</div>
        <div style={{ fontSize: 28, opacity: 0.8, marginTop: 18 }}>
          Voz sintética • legenda PT-BR
        </div>
        <div style={{ fontSize: 22, opacity: 0.6, marginTop: 10 }}>
          Estudo técnico • verificar licença e consentimento antes de publicar
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          left: 120,
          bottom: 100,
          fontSize: 20,
          letterSpacing: 3,
          opacity: 0.5,
        }}
      >
        OPENCODE ECOSYSTEM CORE
      </div>
    </AbsoluteFill>
  );
};

export { Intro, Outro };
