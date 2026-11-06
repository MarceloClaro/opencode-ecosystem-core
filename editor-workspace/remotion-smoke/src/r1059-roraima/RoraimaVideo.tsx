import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';

const W = 720;
const H = 1280;
const MAP_W = 1440;
const MAP_H = 2560;
const BBOX = {west: -84, south: -57, east: -30, north: 29};

// WGS84 → pixels da imagem equirretangular baixada (EPSG:4326, eixo lon/lat).
const px = (lon: number, lat: number): [number, number] => [
  ((lon - BBOX.west) * MAP_W) / (BBOX.east - BBOX.west),
  ((BBOX.north - lat) * MAP_H) / (BBOX.north - BBOX.south),
];

const RORAIMA = px(-60.7625, 5.1433);
const TRIPOINT = px(-60.735, 5.202);

const PLATEAU: Array<[number, number]> = [
  [-60.8, 5.19],
  [-60.745, 5.215],
  [-60.695, 5.17],
  [-60.705, 5.105],
  [-60.775, 5.09],
  [-60.815, 5.14],
].map(([lon, lat]) => px(lon, lat));

const COLORS = {
  ink: '#f7f4ea',
  dim: '#a8bccb',
  gold: '#ffd34e',
  teal: '#73d5ef',
  green: '#87e0b1',
  deep: '#06151f',
};

const ease = (frame: number, start: number, duration: number) =>
  interpolate(frame, [start, start + duration], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

const CountryChip: React.FC<{
  x: number;
  y: number;
  name: string;
  code: string;
  colors: [string, string, string];
  opacity: number;
  delay: number;
  frame: number;
}> = ({x, y, name, code, colors, opacity, delay, frame}) => {
  const show = ease(frame, delay, 14) * opacity;
  const lift = (1 - ease(frame, delay, 14)) * 16;
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        transform: `translate(-50%, -50%) translateY(${lift}px)`,
        opacity: show,
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        padding: '9px 13px 9px 10px',
        background: 'rgba(4,18,27,0.86)',
        border: '1px solid rgba(255,255,255,0.24)',
        borderRadius: 10,
        boxShadow: '0 10px 28px rgba(0,0,0,0.35)',
        backdropFilter: 'blur(4px)',
      }}
    >
      <div style={{display: 'flex', flexDirection: 'column', width: 8, height: 40, borderRadius: 3, overflow: 'hidden'}}>
        {colors.map((color) => (
          <div key={color} style={{flex: 1, background: color}} />
        ))}
      </div>
      <div>
        <div style={{color: COLORS.dim, fontSize: 12, fontWeight: 800, letterSpacing: 1.4}}>{code}</div>
        <div style={{color: COLORS.ink, fontSize: 22, fontWeight: 900, lineHeight: 1.1}}>{name}</div>
      </div>
    </div>
  );
};

const Caption: React.FC<{children: React.ReactNode; frame: number; start: number; end: number}> = ({
  children,
  frame,
  start,
  end,
}) => {
  const opacity = Math.min(ease(frame, start, 10), 1 - ease(frame, end - 10, 10));
  const rise = (1 - ease(frame, start, 12)) * 18;
  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        bottom: 158,
        display: 'flex',
        justifyContent: 'center',
        opacity,
        transform: `translateY(${rise}px)`,
        padding: '0 34px',
      }}
    >
      <div
        style={{
          background: COLORS.gold,
          color: '#171208',
          fontSize: 30,
          fontWeight: 900,
          lineHeight: 1.25,
          padding: '12px 18px',
          borderRadius: 6,
          boxShadow: '0 12px 30px rgba(0,0,0,0.45)',
          textAlign: 'center',
        }}
      >
        {children}
      </div>
    </div>
  );
};

export const RoraimaVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const zoom = interpolate(frame, [0, 299], [3.0, 4.0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const left = W / 2 - RORAIMA[0] * zoom;
  const top = H / 2 - RORAIMA[1] * zoom;

  const ring = 24 + Math.sin(frame / 7) * 5;
  const highlight = ease(frame, 45, 20);
  const titleIn = 1;
  const chips = ease(frame, 200, 20);

  return (
    <AbsoluteFill style={{backgroundColor: COLORS.deep, fontFamily: 'Inter, Roboto, sans-serif'}}>
      {/* Mapa base: imagem equirretangular, recortada por transformação calculada. */}
      <AbsoluteFill style={{overflow: 'hidden'}}>
        <Img
          src={staticFile('r1059-terrain.jpg')}
          style={{
            position: 'absolute',
            left,
            top,
            width: MAP_W * zoom,
            height: MAP_H * zoom,
            maxWidth: 'none',
            filter: 'saturate(1.05) contrast(1.04) brightness(0.72)',
          }}
        />
      </AbsoluteFill>

      {/* Grade e vinheta para leitura do texto. */}
      <AbsoluteFill
        style={{
          background:
            'radial-gradient(ellipse at 50% 46%, rgba(3,16,24,0) 28%, rgba(3,16,24,0.55) 78%), linear-gradient(180deg, rgba(3,16,24,0.78) 0%, rgba(3,16,24,0.12) 30%, rgba(3,16,24,0.28) 62%, rgba(3,16,24,0.86) 100%)',
        }}
      />

      {/* Destaque do platô e ponto do marco triplo. */}
      <svg
        viewBox={`0 0 ${MAP_W} ${MAP_H}`}
        style={{
          position: 'absolute',
          left,
          top,
          width: MAP_W * zoom,
          height: MAP_H * zoom,
          opacity: highlight,
          overflow: 'visible',
        }}
      >
        <polygon
          points={PLATEAU.map(([x, y]) => `${x},${y}`).join(' ')}
          fill="rgba(255,211,78,0.18)"
          stroke={COLORS.gold}
          strokeWidth={1.6}
          vectorEffect="non-scaling-stroke"
        />
        <circle cx={RORAIMA[0]} cy={RORAIMA[1]} r={ring} fill="none" stroke={COLORS.gold} strokeWidth={1.4} vectorEffect="non-scaling-stroke" />
        <circle cx={RORAIMA[0]} cy={RORAIMA[1]} r={4} fill={COLORS.gold} />
        <circle cx={TRIPOINT[0]} cy={TRIPOINT[1]} r={2.2} fill={COLORS.ink} stroke={COLORS.deep} strokeWidth={0.8} vectorEffect="non-scaling-stroke" />
      </svg>

      {/* Movimento gerado no Motion Canvas e exportado como PNG RGBA. */}
      <AbsoluteFill>
        <Img
          src={staticFile(`r1059-tepui/${String(Math.min(frame, 299)).padStart(6, '0')}.png`)}
          style={{width: '100%', height: '100%'}}
        />
      </AbsoluteFill>

      {/* Cabeçalho editorial. */}
      <div
        style={{
          position: 'absolute',
          top: 74,
          left: 46,
          right: 46,
          opacity: titleIn,
          transform: `translateY(${(1 - titleIn) * -14}px)`,
        }}
      >
        <div style={{display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12}}>
          <div style={{width: 34, height: 3, background: COLORS.gold}} />
          <div style={{color: COLORS.gold, fontSize: 15, fontWeight: 900, letterSpacing: 2.2}}>
            AMÉRICA DO SUL · TRÍPLICE FRONTEIRA
          </div>
        </div>
        <div style={{color: COLORS.ink, fontSize: 62, fontWeight: 900, lineHeight: 0.95, letterSpacing: -1.2}}>
          MONTE
          <br />
          RORAIMA
        </div>
        <div style={{color: COLORS.teal, fontSize: 24, fontWeight: 700, marginTop: 12}}>
          a ilha no céu de três países
        </div>
      </div>

      <div
        style={{
          position: 'absolute',
          top: 78,
          right: 42,
          padding: '7px 10px',
          border: '1px solid rgba(255,211,78,0.55)',
          borderRadius: 5,
          color: COLORS.gold,
          fontSize: 11,
          fontWeight: 900,
          letterSpacing: 1.6,
          background: 'rgba(4,18,27,0.55)',
        }}
      >
        ESTUDO R1059
      </div>

      <CountryChip x={360} y={330} name="Venezuela" code="VEN" colors={['#ffce00', '#0033a0', '#cf142b']} opacity={chips} delay={204} frame={frame} />
      <CountryChip x={75} y={820} name="Brasil" code="BRA" colors={['#009c3b', '#ffdf00', '#002776']} opacity={chips} delay={212} frame={frame} />
      <CountryChip x={645} y={820} name="Guiana" code="GUY" colors={['#009e49', '#fcd116', '#ce1126']} opacity={chips} delay={220} frame={frame} />

      <Caption frame={frame} start={10} end={116}>
        Uma mesa de pedra com quase 2 bilhões de anos.
      </Caption>
      <Caption frame={frame} start={118} end={206}>
        Três países dividem o topo dela.
      </Caption>
      <Caption frame={frame} start={208} end={330}>
        Monte Roraima · Brasil, Venezuela e Guiana.
      </Caption>

      <div
        style={{
          position: 'absolute',
          left: 34,
          right: 34,
          bottom: 58,
          color: COLORS.dim,
          fontSize: 12.5,
          lineHeight: 1.45,
          textAlign: 'center',
        }}
      >
        Mapa: EOX::Maps Terrain · OSM, Natural Earth, NASA e outros
        <br />
        Ilustração: Motion Canvas · Estudo R1059, não o vídeo original.
      </div>

      <Audio src={staticFile('r1059-narration.wav')} />
    </AbsoluteFill>
  );
};
