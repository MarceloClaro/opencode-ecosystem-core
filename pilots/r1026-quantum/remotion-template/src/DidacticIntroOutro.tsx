import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  Video,
} from "remotion";

const INK = "#FFFFFF";
const MUTED = "#B9B4C7";
const PURPLE = "#8B5CF6";
const FONT = "DejaVu Sans, sans-serif";
const CARD_BG = "#151020";

type RowProps = {
  index: number;
  text: string;
  enter: number;
  vertical: boolean;
};

const Row: React.FC<RowProps> = ({ index, text, enter, vertical }) => (
  <div
    style={{
      display: "flex",
      alignItems: "flex-start",
      gap: vertical ? 20 : 18,
      opacity: 0.26 + 0.74 * enter,
      transform: `translateY(${(1 - enter) * 24}px)`,
      marginBottom: vertical ? 34 : 28,
    }}
  >
    <div
      style={{
        width: vertical ? 48 : 44,
        height: vertical ? 48 : 44,
        borderRadius: "50%",
        border: `2px solid rgba(139,92,246,${0.35 + 0.65 * enter})`,
        color: `rgba(139,92,246,${0.4 + 0.6 * enter})`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: vertical ? 22 : 20,
        fontWeight: 700,
        flexShrink: 0,
      }}
    >
      {index}
    </div>
    <div
      style={{
        fontSize: vertical ? 32 : 30,
        lineHeight: 1.32,
        color: INK,
        paddingTop: 4,
      }}
    >
      {text}
    </div>
  </div>
);

type Step = {
  title: string;
  detail: string;
};

/**
 * Linha do tempo vertical para 9:16. Ocupa a metade inferior com os três
 * pontos do roadmap; cada passo acende quando a narração o menciona.
 * A linha e os passos futuros ficam visíveis em baixa opacidade.
 */
const Timeline: React.FC<{
  steps: Step[];
  delays: number[];
  top: number;
}> = ({ steps, delays, top }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const stepHeight = 340;

  return (
    <div
      style={{
        position: "absolute",
        left: 60,
        top,
        width: 960,
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
        NESTE VÍDEO
      </div>
      <div
        style={{
          position: "absolute",
          left: 27,
          top: 68,
          width: 3,
          height: stepHeight * (steps.length - 1),
          backgroundColor: "rgba(139,92,246,0.28)",
        }}
      />
      {steps.map((step, index) => {
        const enter = spring({
          frame: Math.max(0, frame - delays[index]),
          fps,
          config: { damping: 200 },
        });
        const active = enter > 0.35;
        return (
          <div
            key={step.title}
            style={{
              position: "absolute",
              top: 40 + index * stepHeight,
              left: 0,
              width: 960,
              display: "flex",
              alignItems: "flex-start",
              gap: 30,
              opacity: 0.26 + 0.74 * enter,
              transform: `translateY(${(1 - enter) * 20}px)`,
            }}
          >
            <div
              style={{
                width: 56,
                height: 56,
                borderRadius: "50%",
                border: `2px solid rgba(139,92,246,${active ? 1 : 0.4})`,
                backgroundColor: active
                  ? "rgba(139,92,246,0.16)"
                  : "rgba(139,92,246,0.02)",
                color: active ? PURPLE : "rgba(185,180,199,0.7)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 24,
                fontWeight: 700,
                flexShrink: 0,
                zIndex: 1,
              }}
            >
              {index + 1}
            </div>
            <div style={{ paddingTop: 2 }}>
              <div
                style={{
                  fontSize: 34,
                  fontWeight: 700,
                  color: INK,
                  lineHeight: 1.15,
                }}
              >
                {step.title}
              </div>
              <div
                style={{
                  fontSize: 22,
                  color: MUTED,
                  marginTop: 10,
                  lineHeight: 1.35,
                }}
              >
                {step.detail}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

/**
 * Cartão da apresentadora. Quando `video` é fornecido, usa o MP4 com a boca
 * sincronizada e o fundo do cartão já composto. Sem vídeo, mantém o retrato
 * estático recortado como fallback.
 */
const PresenterCard: React.FC<{ vertical: boolean; video?: string }> = ({
  vertical,
  video,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const progress = frame / Math.max(1, durationInFrames - 1);
  const scale = video
    ? interpolate(progress, [0, 1], [1.0, 1.04], {
        extrapolateRight: "clamp",
      })
    : interpolate(progress, [0, 1], [1.015, 1.08], {
        extrapolateRight: "clamp",
      });
  const driftX = video ? Math.sin(progress * Math.PI * 2) * 3 : 0;
  const driftY = video ? interpolate(progress, [0, 1], [2, -2]) : 0;
  const width = vertical ? 360 : 520;
  const height = vertical ? 514 : 743;

  return (
    <>
      <div
        style={{
          position: "absolute",
          right: vertical ? 40 : 78,
          top: vertical ? 78 : 112,
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
          top: vertical ? 96 : 130,
          width,
          height,
          borderRadius: vertical ? 24 : 28,
          overflow: "hidden",
          border: "1px solid rgba(139,92,246,0.45)",
          boxShadow: "0 30px 90px rgba(0,0,0,0.55)",
          background:
            "radial-gradient(circle at 50% 40%, #2B2145 0%, #171022 55%, #0B0B0F 100%)",
        }}
      >
        {video ? (
          <Video
            src={staticFile(video)}
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
        ) : (
          <>
            <div
              style={{
                position: "absolute",
                inset: 0,
                background:
                  "radial-gradient(circle at 52% 26%, rgba(139,92,246,0.40), rgba(139,92,246,0) 55%)",
              }}
            />
            <div
              style={{
                position: "absolute",
                left: "5%",
                bottom: "-12%",
                width: "90%",
                height: "45%",
                background:
                  "radial-gradient(ellipse at 50% 50%, rgba(139,92,246,0.26), rgba(139,92,246,0) 70%)",
                filter: "blur(26px)",
              }}
            />
            <Img
              src={staticFile("presenter-cutout.png")}
              style={{
                position: "absolute",
                inset: 0,
                width: "100%",
                height: "100%",
                objectFit: "contain",
                transform: `scale(${scale})`,
                filter: "saturate(0.95) contrast(1.04) brightness(1.02)",
              }}
            />
            <div
              style={{
                position: "absolute",
                inset: 0,
                background:
                  "linear-gradient(180deg, rgba(11,11,15,0) 58%, rgba(11,11,15,0.82) 100%)",
              }}
            />
          </>
        )}
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

export const DidacticIntro: React.FC<{ vertical: boolean }> = ({ vertical }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const title = spring({ frame, fps, config: { damping: 200 } });
  const rows = [
    "100+ qubits: o que mudou",
    "Por que os chips menores saíram",
    "O limite da simulação clássica",
  ];
  const steps: Step[] = [
    { title: "100+ qubits", detail: "o que mudou na escala" },
    { title: "Chips menores", detail: "por que saíram de linha" },
    { title: "Simulação clássica", detail: "o limite que permanece" },
  ];
  const delays = [45, 135, 345];

  return (
    <Shell>
      <Audio src={staticFile("intro-clone.wav")} />
      <PresenterCard vertical={vertical} video="presenter-intro-card.mp4" />
      <div
        style={{
          position: "absolute",
          left: vertical ? 60 : 100,
          top: vertical ? 110 : 180,
          width: vertical ? 560 : 1100,
          opacity: title,
          transform: `translateY(${(1 - title) * 30}px)`,
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
            fontSize: vertical ? 52 : 64,
            fontWeight: 700,
            lineHeight: 1.06,
            marginTop: 16,
            color: INK,
          }}
        >
          Circuitos quânticos
          <br />
          em larga escala
        </div>
        <div
          style={{
            fontSize: vertical ? 24 : 26,
            color: MUTED,
            marginTop: 16,
          }}
        >
          Um recorte didático para entender a mudança
        </div>
        <div
          style={{
            width: 90,
            height: 6,
            backgroundColor: PURPLE,
            marginTop: 22,
          }}
        />
      </div>
      {vertical ? (
        <Timeline steps={steps} delays={delays} top={670} />
      ) : (
        <div
          style={{
            position: "absolute",
            left: 100,
            top: 520,
            width: 1100,
          }}
        >
          <div
            style={{
              fontSize: 15,
              fontWeight: 700,
              letterSpacing: 2.4,
              color: PURPLE,
              marginBottom: 22,
            }}
          >
            NESTE VÍDEO
          </div>
          {rows.map((text, index) => (
            <Row
              key={text}
              index={index + 1}
              text={text}
              enter={spring({
                frame: Math.max(0, frame - delays[index]),
                fps,
                config: { damping: 200 },
              })}
              vertical={false}
            />
          ))}
        </div>
      )}
      <div
        style={{
          position: "absolute",
          left: vertical ? 60 : 100,
          bottom: vertical ? 64 : 72,
          fontSize: vertical ? 17 : 18,
          letterSpacing: 1.8,
          color: MUTED,
          opacity: 0.62,
        }}
      >
        FONTE: QISKIT • VOZ SINTÉTICA
      </div>
    </Shell>
  );
};

export const DidacticOutro: React.FC<{ vertical: boolean }> = ({ vertical }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const title = spring({ frame, fps, config: { damping: 200 } });
  const rows = [
    "100+ qubits amplamente disponíveis",
    "Chips menores desativados",
    "Simulação clássica ainda é um limite",
  ];
  const steps: Step[] = [
    { title: "100+ qubits", detail: "amplamente disponíveis" },
    { title: "Chips menores", detail: "desativados" },
    { title: "Simulação clássica", detail: "ainda é um limite" },
  ];
  const delays = [0, 75, 150];

  return (
    <Shell>
      <Audio src={staticFile("outro-clone.wav")} />
      <PresenterCard vertical={vertical} video="presenter-outro-card.mp4" />
      <div
        style={{
          position: "absolute",
          left: vertical ? 60 : 100,
          top: vertical ? 110 : 170,
          width: vertical ? 560 : 1100,
          opacity: title,
          transform: `translateY(${(1 - title) * 24}px)`,
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
          RECAPITULANDO
        </div>
        <div
          style={{
            fontSize: vertical ? 58 : 68,
            fontWeight: 700,
            marginTop: 14,
            color: INK,
          }}
        >
          Em resumo
        </div>
        <div
          style={{
            width: 90,
            height: 6,
            backgroundColor: PURPLE,
            marginTop: 22,
          }}
        />
      </div>
      {vertical ? (
        <Timeline steps={steps} delays={delays} top={670} />
      ) : (
        <div
          style={{
            position: "absolute",
            left: 100,
            top: 420,
            width: 1100,
          }}
        >
          {rows.map((text, index) => (
            <Row
              key={text}
              index={index + 1}
              text={text}
              enter={spring({
                frame: Math.max(0, frame - delays[index]),
                fps,
                config: { damping: 200 },
              })}
              vertical={false}
            />
          ))}
        </div>
      )}
      <div
        style={{
          position: "absolute",
          left: vertical ? 60 : 100,
          bottom: vertical ? 64 : 72,
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
