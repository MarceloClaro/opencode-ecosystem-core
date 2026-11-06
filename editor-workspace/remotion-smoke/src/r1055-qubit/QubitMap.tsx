import React from 'react';
import {
  Easing,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {SCENES} from './timeline';

const MAP_W = 4096;
const MAP_H = 1354;
const LAT_MAX = 64;
const LAT_MIN = -55;
const INK = '#F7F5FF';
const MUTED = '#B9B1CE';
const DIM = '#8F86A8';
const LIME = '#A3E635';
const CYAN = '#22D3EE';
const PURPLE = '#A78BFA';
const PINK = '#F472B6';
const GOLD = '#FBBF24';
const BG = '#070D16';
const PANEL = 'rgba(7, 13, 22, 0.86)';
const BORDER = 'rgba(167, 139, 250, 0.32)';
const FONT = 'DejaVu Sans, Arial, sans-serif';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const mapX = (lon: number) => ((lon + 180) / 360) * MAP_W;
const mapY = (lat: number) => ((LAT_MAX - lat) / (LAT_MAX - LAT_MIN)) * MAP_H;

type Marker = {
  id: string;
  name: string;
  sub: string;
  lon: number;
  lat: number;
  color: string;
  dx: number;
  dy: number;
  align?: 'left' | 'right';
};

const MARKERS: Marker[] = [
  {id: 'cph', name: 'Copenhague', sub: 'Bohr · 1920s', lon: 12.57, lat: 55.68, color: CYAN, dx: 18, dy: -38},
  {id: 'vie', name: 'Viena', sub: 'Schrödinger · Zeilinger', lon: 16.37, lat: 48.21, color: PINK, dx: 18, dy: 20},
  {id: 'lej', name: 'Leipzig', sub: 'Heisenberg', lon: 12.37, lat: 51.34, color: PURPLE, dx: -18, dy: 20, align: 'right'},
  {id: 'par', name: 'Paris', sub: 'Aspect', lon: 2.35, lat: 48.86, color: GOLD, dx: -18, dy: 20, align: 'right'},
  {id: 'pas', name: 'Caltech', sub: 'Feynman · 1982', lon: -118.14, lat: 34.15, color: LIME, dx: 18, dy: -38},
  {id: 'ber', name: 'Berkeley', sub: 'Clauser', lon: -122.27, lat: 37.87, color: GOLD, dx: -18, dy: -30, align: 'right'},
  {id: 'ohi', name: 'Ohio', sub: 'Schumacher · 1995', lon: -82.0, lat: 40.0, color: LIME, dx: 18, dy: 20},
];

const NOBEL = new Set(['par', 'ber', 'vie']);

const MILESTONES = [
  {year: '1920s', label: 'Copenhague · Viena · Leipzig'},
  {year: '1982', label: 'Feynman · Caltech'},
  {year: '1995', label: 'Schumacher · Ohio'},
  {year: '2022', label: 'Nobel · Aspect · Clauser · Zeilinger'},
];

type Camera = {p: number; scale: number; lon: number; lat: number};

const buildCamera = (
  vertical: boolean,
  pEurope: number,
  pFeynman: number,
  pSchumacher: number,
  pNobel: number,
): Camera[] => {
  const europe = vertical ? 2.9 : 2.7;
  const usa = vertical ? 2.2 : 2.45;
  const world = vertical ? 0.62 : 1.05;
  return [
    {p: 0.0, scale: vertical ? 1.05 : 1.15, lon: vertical ? -30 : -20, lat: 35},
    {p: Math.max(0.06, pEurope - 0.04), scale: europe, lon: 8, lat: 51},
    {p: pEurope + 0.10, scale: europe, lon: 8, lat: 51},
    {p: Math.max(pEurope + 0.11, pFeynman - 0.01), scale: usa, lon: vertical ? -102 : -100, lat: 37},
    {p: pSchumacher + 0.08, scale: usa, lon: vertical ? -102 : -100, lat: 37},
    {
      p: Math.max(pSchumacher + 0.09, pNobel - 0.03),
      scale: world,
      lon: vertical ? -52 : -50,
      lat: 40,
    },
    {p: 1.0, scale: world, lon: vertical ? -52 : -50, lat: 40},
  ];
};

const cameraValue = (
  p: number,
  camera: Camera[],
  key: 'scale' | 'lon' | 'lat',
) => {
  const points = camera.map((item) => item.p);
  const values = camera.map((item) => item[key]);
  return interpolate(p, points, values, {
    ...clamp,
    easing: Easing.inOut(Easing.cubic),
  });
};

const Pulse = ({
  x,
  y,
  color,
  cue,
  frame,
  fps,
  size = 11,
  nobel = false,
}: {
  x: number;
  y: number;
  color: string;
  cue: number;
  frame: number;
  fps: number;
  size?: number;
  nobel?: boolean;
}) => {
  if (frame < cue) return null;
  const appear = spring({frame: frame - cue, fps, config: {damping: 13, stiffness: 140}});
  const age = Math.max(0, frame - cue);
  const cycle = 1.7 * fps;
  const phase = (age % cycle) / cycle;
  const ringScale = 0.9 + phase * 2.4;
  const ringOpacity = (1 - phase) * 0.7 * appear;
  const goldPhase = ((age + cycle / 2) % cycle) / cycle;
  return (
    <>
      <div
        style={{
          position: 'absolute',
          left: x - size / 2,
          top: y - size / 2,
          width: size,
          height: size,
          borderRadius: '50%',
          background: color,
          boxShadow: `0 0 20px ${color}, 0 0 46px ${color}66`,
          transform: `scale(${appear})`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: x - size / 2,
          top: y - size / 2,
          width: size,
          height: size,
          borderRadius: '50%',
          border: `2px solid ${color}`,
          opacity: ringOpacity,
          transform: `scale(${ringScale})`,
        }}
      />
      {nobel && (
        <div
          style={{
            position: 'absolute',
            left: x - size / 2,
            top: y - size / 2,
            width: size,
            height: size,
            borderRadius: '50%',
            border: `2px solid ${GOLD}`,
            opacity: (1 - goldPhase) * 0.55 * appear,
            transform: `scale(${0.9 + goldPhase * 3.2})`,
          }}
        />
      )}
    </>
  );
};

const MarkerLabel = ({
  marker,
  x,
  y,
  opacity,
}: {
  marker: Marker;
  x: number;
  y: number;
  opacity: number;
}) => {
  if (opacity <= 0.02) return null;
  const right = marker.align === 'right';
  return (
    <div
      style={{
        position: 'absolute',
        left: x + marker.dx,
        top: y + marker.dy,
        transform: `translate(${right ? '-100%' : '0'}, -50%)`,
        opacity,
        padding: '7px 11px',
        borderRadius: 10,
        background: 'rgba(7, 13, 22, 0.78)',
        borderLeft: `3px solid ${marker.color}`,
        boxShadow: '0 8px 24px rgba(0,0,0,0.35)',
        textAlign: right ? 'right' : 'left',
        whiteSpace: 'nowrap',
      }}
    >
      <div style={{color: INK, fontSize: 18, fontWeight: 800, lineHeight: 1.1}}>{marker.name}</div>
      <div style={{color: MUTED, fontSize: 13, marginTop: 2}}>{marker.sub}</div>
    </div>
  );
};

const ClusterLabel = ({
  x,
  y,
  title,
  sub,
  opacity,
  align = 'left',
}: {
  x: number;
  y: number;
  title: string;
  sub: string;
  opacity: number;
  align?: 'left' | 'right';
}) => {
  if (opacity <= 0.02) return null;
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        transform: `translate(${align === 'right' ? '-100%' : '0'}, -50%)`,
        opacity,
        padding: '8px 12px',
        borderRadius: 10,
        background: 'rgba(7, 13, 22, 0.76)',
        border: `1px solid ${BORDER}`,
        whiteSpace: 'nowrap',
      }}
    >
      <div style={{color: LIME, fontSize: 13, fontWeight: 800, letterSpacing: 1.5}}>{title}</div>
      <div style={{color: MUTED, fontSize: 13, marginTop: 2}}>{sub}</div>
    </div>
  );
};

const NobelLabel = ({
  x,
  y,
  name,
  opacity,
  align = 'left',
}: {
  x: number;
  y: number;
  name: string;
  opacity: number;
  align?: 'left' | 'right';
}) => {
  if (opacity <= 0.02) return null;
  return (
    <div
      style={{
        position: 'absolute',
        left: x + (align === 'right' ? -14 : 14),
        top: y + 30,
        transform: `translate(${align === 'right' ? '-100%' : '0'}, 0)`,
        opacity,
        padding: '3px 8px',
        borderRadius: 7,
        background: 'rgba(7, 13, 22, 0.84)',
        border: `1px solid ${GOLD}66`,
        color: GOLD,
        fontSize: 13,
        fontWeight: 800,
        whiteSpace: 'nowrap',
      }}
    >
      {name}
    </div>
  );
};

const Timeline = ({
  vertical,
  active,
}: {
  vertical: boolean;
  active: number;
}) => {
  const frame = useCurrentFrame();
  const left = vertical ? 54 : 980;
  const top = vertical ? 1470 : 138;
  const width = vertical ? 972 : 820;
  const columns = MILESTONES.length;
  const pulse = 0.5 + 0.5 * Math.sin(frame / 8);
  return (
    <div style={{position: 'absolute', left, top, width}}>
      <div style={{position: 'relative', height: 2, background: 'rgba(247,245,255,0.18)', marginBottom: 16}}>
        {MILESTONES.map((item, index) => {
          const x = ((index + 0.5) / columns) * 100;
          const on = index <= active;
          return (
            <div
              key={item.year}
              style={{
                position: 'absolute',
                left: `${x}%`,
                top: -4,
                width: 10,
                height: 10,
                borderRadius: 5,
                background: on ? LIME : 'rgba(247,245,255,0.25)',
                boxShadow: index === active ? `0 0 ${10 + 8 * pulse}px ${LIME}` : 'none',
                transform: 'translateX(-50%)',
              }}
            />
          );
        })}
      </div>
      <div style={{display: 'flex'}}>
        {MILESTONES.map((item, index) => {
          const on = index === active;
          return (
            <div key={item.year} style={{width: `${100 / columns}%`, paddingRight: 10}}>
              <div style={{color: on ? LIME : DIM, fontSize: 15, fontWeight: 800, letterSpacing: 1}}>
                {item.year}
              </div>
              <div style={{color: on ? INK : MUTED, fontSize: vertical ? 13 : 12, lineHeight: 1.35, marginTop: 2}}>
                {item.label}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export const MapCanvas = ({vertical = false}: {vertical?: boolean}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const scene = SCENES.find((item) => item.id === '06');
  if (!scene) return null;

  const W = vertical ? 1080 : 1920;
  const H = vertical ? 1920 : 1080;
  const duration = Math.max(1, scene.endFrame - scene.startFrame);
  const p = Math.min(1, Math.max(0, (frame - scene.startFrame) / duration));
  const caption = (index: number) =>
    scene.captions[Math.min(index, scene.captions.length - 1)];

  const cueEurope = caption(1).startFrame;
  const cueFeynman = caption(2).startFrame;
  const cueSchumacher = caption(3).startFrame;
  const cueNobel = caption(4).startFrame;

  const pEurope = (cueEurope - scene.startFrame) / duration;
  const pFeynman = (cueFeynman - scene.startFrame) / duration;
  const pSchumacher = (cueSchumacher - scene.startFrame) / duration;
  const pNobel = (cueNobel - scene.startFrame) / duration;
  const camera = buildCamera(vertical, pEurope, pFeynman, pSchumacher, pNobel);
  const active = frame >= cueNobel ? 3 : frame >= cueSchumacher ? 2 : frame >= cueFeynman ? 1 : 0;
  const scale = cameraValue(p, camera, 'scale');
  const lon = cameraValue(p, camera, 'lon');
  const lat = cameraValue(p, camera, 'lat');
  const focusX = mapX(lon);
  const focusY = mapY(lat);

  const band = vertical
    ? interpolate(p, [0.64, 0.72], [0, 1], clamp)
    : 0;
  const focusLeft = W / 2 - focusX * scale;
  const focusTop = H / 2 - focusY * scale;
  const bandLeft = W / 2 - mapX(-52) * scale;
  const bandTop = vertical ? 350 : (H - MAP_H * scale) / 2;
  const left = focusLeft * (1 - band) + bandLeft * band;
  const top = focusTop * (1 - band) + bandTop * band;
  const screen = (lonValue: number, latValue: number) => ({
    x: left + mapX(lonValue) * scale,
    y: top + mapY(latValue) * scale,
  });

  const zoomLabels = interpolate(scale, [1.5, 1.95], [0, 1], clamp);
  const nobel = interpolate(p, [0.735, 0.79], [0, 1], clamp);
  const clusterOpacity = (1 - zoomLabels) * (1 - nobel);
  const closing = interpolate(p, [0.88, 0.94], [0, 1], clamp);
  const titleOpacity = vertical ? 1 : 1 - interpolate(p, [0.84, 0.90], [0, 1], clamp);

  const lead = Math.round(0.12 * fps);
  const markerCue = (id: string) => {
    if (id === 'cph') return cueEurope - lead;
    if (id === 'vie') return cueEurope - lead + 0.55 * fps;
    if (id === 'lej') return cueEurope - lead + 1.1 * fps;
    if (id === 'pas') return cueFeynman - lead;
    if (id === 'ohi') return cueSchumacher - lead;
    return cueNobel - lead;
  };

  return (
    <div style={{position: 'absolute', inset: 0, overflow: 'hidden', background: BG, fontFamily: FONT}}>
      <Img
        src={staticFile('r1055-world-map.png')}
        style={{
          position: 'absolute',
          left,
          top,
          width: MAP_W * scale,
          height: MAP_H * scale,
          maxWidth: 'none',
          filter: 'brightness(1.22) contrast(1.06) saturate(0.95)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'radial-gradient(ellipse at 50% 44%, rgba(7,13,22,0) 32%, rgba(4,8,14,0.72) 100%)',
          pointerEvents: 'none',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          width: vertical ? 1080 : 960,
          height: vertical ? 360 : 330,
          background: 'linear-gradient(180deg, rgba(7,13,22,0.96), rgba(7,13,22,0))',
          pointerEvents: 'none',
        }}
      />

      <div
        style={{
          position: 'absolute',
          left: vertical ? 54 : 120,
          top: vertical ? 145 : 118,
          width: vertical ? 972 : 820,
          opacity: titleOpacity,
        }}
      >
        <div style={{color: LIME, fontSize: 17, fontWeight: 800, letterSpacing: 3}}>06 · ORIGEM</div>
        <div
          style={{
            color: INK,
            fontSize: vertical ? 58 : 64,
            fontWeight: 900,
            lineHeight: 1.02,
            letterSpacing: -1.5,
            marginTop: 8,
          }}
        >
          Uma ideia sem fronteira
        </div>
        <div style={{color: MUTED, fontSize: vertical ? 20 : 22, lineHeight: 1.4, marginTop: 10}}>
          De Copenhague a Pasadena, o qubit é uma construção coletiva.
        </div>
        <div style={{color: DIM, fontSize: 13, marginTop: 8}}>
          Base cartográfica: Natural Earth (domínio público)
        </div>
      </div>

      <Timeline vertical={vertical} active={active} />

      {MARKERS.map((marker) => {
        const cue = markerCue(marker.id);
        if (frame < cue) return null;
        const point = screen(marker.lon, marker.lat);
        const onScreen =
          point.x > -120 && point.x < W + 120 && point.y > -120 && point.y < H + 120;
        if (!onScreen) return null;
        const appear = spring({frame: frame - cue, fps, config: {damping: 13, stiffness: 140}});
        const nobelCue = marker.id === 'par'
          ? cueNobel - lead
          : marker.id === 'ber'
            ? cueNobel - lead + 0.45 * fps
            : marker.id === 'vie'
              ? cueNobel - lead + 0.9 * fps
              : null;
        const isNobel = nobelCue !== null && frame >= nobelCue;
        return (
          <React.Fragment key={marker.id}>
            <Pulse
              x={point.x}
              y={point.y}
              color={isNobel ? GOLD : marker.color}
              cue={isNobel ? (nobelCue as number) : cue}
              frame={frame}
              fps={fps}
              nobel={isNobel}
            />
            <MarkerLabel
              marker={marker}
              x={point.x}
              y={point.y}
              opacity={appear * zoomLabels * (isNobel ? 1 : 1 - nobel)}
            />
          </React.Fragment>
        );
      })}

      {nobel > 0.3 &&
        MARKERS.filter((marker) => NOBEL.has(marker.id)).map((marker) => {
          const cue = marker.id === 'par'
            ? cueNobel - lead
            : marker.id === 'ber'
              ? cueNobel - lead + 0.45 * fps
              : cueNobel - lead + 0.9 * fps;
          if (frame < cue) return null;
          const point = screen(marker.lon, marker.lat);
          return (
            <NobelLabel
              key={`nobel-${marker.id}`}
              x={point.x}
              y={point.y}
              name={marker.name}
              opacity={nobel}
              align={marker.id === 'ber' ? 'left' : 'right'}
            />
          );
        })}

      {(() => {
        const europe = screen(9, 52);
        const usa = screen(-100, 38);
        return (
          <>
            <ClusterLabel
              x={europe.x + 14}
              y={europe.y - 10}
              title="EUROPA · 1920s"
              sub="Bohr · Schrödinger · Heisenberg"
              opacity={clusterOpacity}
            />
            <ClusterLabel
              x={usa.x - 14}
              y={usa.y + 6}
              title="EUA · 1982–1995"
              sub="Feynman · Schumacher · Clauser"
              opacity={clusterOpacity}
              align="right"
            />
          </>
        );
      })()}

      {nobel > 0 && (
        <div
          style={{
            position: 'absolute',
            left: vertical ? 54 : 120,
            top: vertical ? 380 : 740,
            opacity: nobel * (1 - closing),
            display: 'flex',
            alignItems: 'center',
            gap: 14,
            padding: '10px 18px',
            borderRadius: 999,
            background: 'rgba(7,13,22,0.84)',
            border: `1px solid ${GOLD}66`,
          }}
        >
          <div style={{width: 10, height: 10, borderRadius: 5, background: GOLD, boxShadow: `0 0 18px ${GOLD}`}} />
          <div style={{color: GOLD, fontSize: 15, fontWeight: 800, letterSpacing: 2}}>NOBEL 2022</div>
          <div style={{color: MUTED, fontSize: 15}}>Aspect · Clauser · Zeilinger</div>
        </div>
      )}

      {closing > 0 && (
        <div
          style={{
            position: 'absolute',
            left: vertical ? 54 : 600,
            top: vertical ? 1210 : 330,
            width: vertical ? 972 : 720,
            opacity: closing,
            transform: `translateY(${(1 - closing) * 20}px)`,
            padding: '24px 28px',
            borderRadius: 24,
            background: PANEL,
            border: `1px solid ${BORDER}`,
            boxShadow: '0 20px 60px rgba(0,0,0,0.4)',
          }}
        >
          <div style={{color: LIME, fontSize: 17, fontWeight: 800, letterSpacing: 3}}>SÍNTESE</div>
          <div
            style={{
              color: INK,
              fontSize: vertical ? 54 : 62,
              fontWeight: 900,
              lineHeight: 1.04,
              letterSpacing: -1.5,
              marginTop: 8,
            }}
          >
            Qubit é uma porta,
            <br />
            <span style={{color: LIME}}>não mágica.</span>
          </div>
        </div>
      )}

      <div
        style={{
          position: 'absolute',
          left: vertical ? 54 : 72,
          bottom: vertical ? 58 : 60,
          color: DIM,
          fontSize: 12,
        }}
      >
        Mapa: Natural Earth · domínio público
      </div>
    </div>
  );
};
