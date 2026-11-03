import React from "react";
import {
  AbsoluteFill,
  Audio,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  Video,
} from "remotion";

const INK = "#FFFFFF";
const MUTED = "#B9B4C7";
const PURPLE = "#8B5CF6";
const FONT = "DejaVu Sans, sans-serif";

const Shell: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const progress = frame / Math.max(1, durationInFrames - 1);

  return (
    <AbsoluteFill
      style={{
        background: "radial-gradient(circle at 18% 18%, #1B1233, #0B0B0F 62%)",
        fontFamily: FONT,
      }}
    >
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          height: 6,
          width: `${progress * 100}%`,
          backgroundColor: PURPLE,
        }}
      />
      {children}
    </AbsoluteFill>
  );
};

const PresenterCard: React.FC<{ vertical: boolean }> = ({ vertical }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const progress = frame / Math.max(1, durationInFrames - 1);
  const scale = interpolate(progress, [0, 1], [1.0, 1.03], {
    extrapolateRight: "clamp",
  });
  const driftX = Math.sin(progress * Math.PI * 2) * 3;
  const driftY = interpolate(progress, [0, 1], [2, -2]);
  const width = vertical ? 360 : 520;
  const height = vertical ? 514 : 743;

  return (
    <>
      <div
        style={{
          position: "absolute",
          right: vertical ? 40 : 78,
          top: vertical ? 78 : 132,
          width,
          height,
          borderRadius: 999,
          background:
            "radial-gradient(circle, rgba(139,92,246,0.30), rgba(139,92,246,0) 70%)",
          filter: "blur(46px)",
        }}
      />
      <div
        style={{
          position: "absolute",
          right: vertical ? 56 : 100,
          top: vertical ? 96 : 150,
          width,
          height,
          borderRadius: vertical ? 24 : 28,
          overflow: "hidden",
          border: "1px solid rgba(139,92,246,0.45)",
          boxShadow: "0 30px 90px rgba(0,0,0,0.55)",
          background: "#0B0B0F",
        }}
      >
        <Video
          src={staticFile("presenter-middle-card.mp4")}
          muted
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `translate(${driftX}px, ${driftY}px) scale(${scale})`,
          }}
        />
        <div
          style={{
            position: "absolute",
            left: vertical ? 14 : 18,
            bottom: vertical ? 14 : 16,
            padding: vertical ? "8px 11px" : "9px 13px",
            borderRadius: 12,
            background: "rgba(11,11,15,0.72)",
            border: "1px solid rgba(139,92,246,0.35)",
            display: "flex",
            flexDirection: "column",
            gap: 2,
          }}
        >
          <span
            style={{
              fontSize: vertical ? 11 : 12,
              fontWeight: 700,
              letterSpacing: 1.4,
              color: INK,
            }}
          >
            APRESENTADORA
          </span>
          <span
            style={{
              fontSize: vertical ? 10 : 11,
              letterSpacing: 1.2,
              color: MUTED,
            }}
          >
            VOZ SINTÉTICA
          </span>
        </div>
      </div>
    </>
  );
};

export const DidacticMiddle: React.FC<{ vertical: boolean }> = ({ vertical }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const progress = frame / Math.max(1, durationInFrames - 1);
  const title = interpolate(progress, [0, 0.08], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <Shell>
      <Audio src={staticFile("middle-clone.wav")} />
      <PresenterCard vertical={vertical} />
      {vertical ? (
        <>
          <div
            style={{
              position: "absolute",
              left: 60,
              top: 110,
              width: 560,
              opacity: title,
            }}
          >
            <div
              style={{
                fontSize: 15,
                fontWeight: 700,
                letterSpacing: 2.4,
                color: PURPLE,
              }}
            >
              QISKIT • FUNDAMENTOS
            </div>
            <div
              style={{
                fontSize: 48,
                fontWeight: 700,
                lineHeight: 1.06,
                marginTop: 14,
                color: INK,
              }}
            >
              Computação quântica
              <br />
              na prática
            </div>
            <div style={{ fontSize: 24, color: MUTED, marginTop: 14 }}>
              100+ qubits • dublado
            </div>
            <div
              style={{
                width: 90,
                height: 6,
                backgroundColor: PURPLE,
                marginTop: 20,
              }}
            />
          </div>
          <div
            style={{
              position: "absolute",
              left: 60,
              top: 650,
              width: 960,
              height: 887,
              borderRadius: 24,
              overflow: "hidden",
              border: "1px solid rgba(139,92,246,0.35)",
              boxShadow: "0 30px 90px rgba(0,0,0,0.5)",
              background: "#0F0B18",
            }}
          >
            <Video
              src={staticFile("slide-sequence-dark.mp4")}
              muted
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
              }}
            />
          </div>
        </>
      ) : (
        <div
          style={{
            position: "absolute",
            left: 70,
            top: 120,
            width: 980,
            height: 906,
            borderRadius: 24,
            overflow: "hidden",
            border: "1px solid rgba(139,92,246,0.35)",
            boxShadow: "0 30px 90px rgba(0,0,0,0.5)",
            background: "#0F0B18",
          }}
        >
          <Video
            src={staticFile("slide-sequence-dark.mp4")}
            muted
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
            }}
          />
        </div>
      )}
      <div
        style={{
          position: "absolute",
          left: vertical ? 60 : 70,
          bottom: vertical ? 64 : 36,
          fontSize: vertical ? 17 : 18,
          letterSpacing: 1.8,
          color: MUTED,
          opacity: 0.65,
        }}
      >
        Fonte: Qiskit • adaptação didática • voz sintética
      </div>
    </Shell>
  );
};
