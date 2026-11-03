import React from "react";
import {
  AbsoluteFill,
  Composition,
  OffthreadVideo,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Intro, Outro } from "./IntroOutro";
import { SlideSequence } from "./SlideSequence";
import { DarkSlideSequence } from "./DarkSlideSequence";
import { DidacticIntro, DidacticOutro } from "./DidacticIntroOutro";
import { DidacticMiddle } from "./DidacticMiddle";

const Pilot: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const entrance = spring({ frame, fps, config: { damping: 200 } });
  const progress = interpolate(frame, [0, durationInFrames], [0, 100], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <OffthreadVideo
        src={staticFile("source.mp4")}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(to top, rgba(0,0,0,0.78) 0%, rgba(0,0,0,0.15) 38%, transparent 60%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 64,
          bottom: 84,
          color: "white",
          fontFamily: "DejaVu Sans, sans-serif",
          transform: `translateY(${(1 - entrance) * 40}px)`,
          opacity: entrance,
        }}
      >
        <div style={{ fontSize: 48, fontWeight: 700, letterSpacing: -0.5 }}>
          Circuitos quânticos em larga escala
        </div>
        <div style={{ fontSize: 26, opacity: 0.86, marginTop: 10 }}>
          Qiskit • 100+ qubits • Remotion
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          height: 6,
          width: `${progress}%`,
          background: "#8b5cf6",
        }}
      />
    </AbsoluteFill>
  );
};

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="QuantumPilot"
      component={Pilot}
      durationInFrames={240}
      fps={30}
      width={1920}
      height={1080}
    />
    <Composition
      id="Intro"
      component={Intro}
      durationInFrames={90}
      fps={30}
      width={1920}
      height={1080}
    />
    <Composition
      id="Outro"
      component={Outro}
      durationInFrames={90}
      fps={30}
      width={1920}
      height={1080}
    />
    <Composition
      id="SlideSequence"
      component={SlideSequence}
      durationInFrames={600}
      fps={30}
      width={935}
      height={864}
    />
    <Composition
      id="DarkSlideSequence"
      component={DarkSlideSequence}
      durationInFrames={600}
      fps={30}
      width={935}
      height={864}
    />
    <Composition
      id="DidacticIntro16"
      component={DidacticIntro}
      durationInFrames={425}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ vertical: false }}
    />
    <Composition
      id="DidacticIntro9"
      component={DidacticIntro}
      durationInFrames={425}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{ vertical: true }}
    />
    <Composition
      id="DidacticOutro16"
      component={DidacticOutro}
      durationInFrames={294}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ vertical: false }}
    />
    <Composition
      id="DidacticOutro9"
      component={DidacticOutro}
      durationInFrames={294}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{ vertical: true }}
    />
    <Composition
      id="DidacticMiddle16"
      component={DidacticMiddle}
      durationInFrames={600}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ vertical: false }}
    />
    <Composition
      id="DidacticMiddle9"
      component={DidacticMiddle}
      durationInFrames={600}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{ vertical: true }}
    />
  </>
);
