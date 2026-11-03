import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from "remotion";

// CPU-oriented 2D component. No CSS animation, timers, WebGL or external assets.
// This explains the dubbing pipeline; it is NOT inserted into drama episodes.
const smooth = (x: number) => {
  const u = Math.min(1, Math.max(0, x));
  return u * u * (3 - 2 * u);
};

export const ContinuousProcess: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const progress = frame / Math.max(1, durationInFrames - 1);
  const labels = ["Áudio original", "Falas + locutores", "Vozes em PT-BR", "Mixagem + legendas"];
  const x = [150, 470, 790, 1110];
  const segment = Math.min(2, Math.floor(progress * 3));
  const local = smooth(progress * 3 - segment);
  const cursor = x[segment] + (x[segment + 1] - x[segment]) * local;
  return <AbsoluteFill style={{background: "#0b0b14", color: "#fff", fontFamily: "DejaVu Sans, sans-serif", justifyContent: "center"}}>
    <svg viewBox="0 0 1280 720" width="100%" height="100%" role="img" aria-label="Fluxo de dublagem: áudio, locutores, vozes em português, mixagem e legendas">
      <text x="80" y="110" fill="#fff" fontSize="38" fontWeight="bold">Uma timeline, do diálogo à legenda</text>
      <text x="80" y="158" fill="#b9b4c7" fontSize="24">Demonstração do processo — não é uma medição de desempenho</text>
      <path d="M150 350 H1110" stroke="#302341" strokeWidth="6" fill="none" />
      <path d={`M150 350 H${cursor}`} stroke="#a78bfa" strokeWidth="6" fill="none" />
      {labels.map((label, i) => {
        const active = smooth((progress * 3 - i + 0.12) / 0.12);
        return <g key={label}>
          <circle cx={x[i]} cy={350} r={38} fill={active > 0 ? "#7148ae" : "#211a2c"} stroke="#a78bfa" strokeWidth="2" />
          <text x={x[i]} y={360} textAnchor="middle" fill="#fff" fontSize="28">{i + 1}</text>
          <text x={x[i]} y={435} textAnchor="middle" fill="#fff" fontSize="22">{label}</text>
        </g>;
      })}
      <circle cx={cursor} cy={350} r={9} fill="#f5edff" />
      <text x="80" y="610" fill="#b9b4c7" fontSize="22">O mesmo objeto percorre as etapas; o movimento depende do frame.</text>
    </svg>
  </AbsoluteFill>;
};
