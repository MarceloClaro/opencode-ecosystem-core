import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {SCENES} from './timeline';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

export type CameraOptions = {
  zoomFrom?: number;
  zoomTo?: number;
  focusAt?: number;
  focusZoom?: number;
  panX?: number;
  panY?: number;
  shakeAt?: number;
  shakeAmount?: number;
};

export const useSceneCamera = (index: number, options: CameraOptions = {}) => {
  const frame = useCurrentFrame();
  const scene = SCENES[index];
  const start = scene.startFrame;
  const end = scene.endFrame;
  const zoomFrom = options.zoomFrom ?? 1;
  const zoomTo = options.zoomTo ?? 1.04;
  const base = interpolate(frame, [start, end], [zoomFrom, zoomTo], {
    ...clamp,
    easing: Easing.inOut(Easing.cubic),
  });
  const focusAt = options.focusAt;
  const focusZoom = options.focusZoom ?? zoomTo;
  let scale = base;
  if (focusAt !== undefined) {
    const push = interpolate(frame, [focusAt - 12, focusAt + 20, end], [0, 1, 0.45], {
      ...clamp,
      easing: Easing.inOut(Easing.cubic),
    });
    scale = base + (focusZoom - base) * push;
  }
  const panX = interpolate(frame, [start, end], [0, options.panX ?? 0], {
    ...clamp,
    easing: Easing.inOut(Easing.cubic),
  });
  const panY = interpolate(frame, [start, end], [0, options.panY ?? 0], {
    ...clamp,
    easing: Easing.inOut(Easing.cubic),
  });
  const shakeAt = options.shakeAt;
  const shakeAmount = options.shakeAmount ?? 0;
  const decay = shakeAt !== undefined && frame >= shakeAt
    ? Math.exp(-(frame - shakeAt) / 7)
    : 0;
  const shakeX = Math.sin((frame - (shakeAt ?? 0)) * 1.9) * shakeAmount * decay;
  const shakeY = Math.cos((frame - (shakeAt ?? 0)) * 2.3) * shakeAmount * 0.55 * decay;
  const breathe = Math.sin(frame * 0.035) * 1.1;
  return {
    scale,
    x: panX + shakeX,
    y: panY + shakeY + breathe,
    shake: decay,
  };
};

export const SceneCamera = ({
  index,
  options,
  children,
  style,
}: {
  index: number;
  options?: CameraOptions;
  children: React.ReactNode;
  style?: React.CSSProperties;
}) => {
  const camera = useSceneCamera(index, options);
  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        transform: `translate3d(${camera.x}px, ${camera.y}px, 0) scale(${camera.scale})`,
        transformOrigin: 'center',
        willChange: 'transform',
        ...style,
      }}
    >
      {children}
    </div>
  );
};

export const TravelingPulse = ({
  width,
  height,
  phase,
  color,
  count = 3,
  radius = 5,
}: {
  width: number;
  height: number;
  phase: number;
  color: string;
  count?: number;
  radius?: number;
}) => {
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{position: 'absolute', inset: 0}}>
      {Array.from({length: count}).map((_, index) => {
        const t = ((phase * 0.22 + index / count) % 1 + 1) % 1;
        const x = 20 + (width - 40) * t;
        const y = height / 2 + Math.sin(t * Math.PI * 2) * height * 0.12;
        return (
          <circle
            key={index}
            cx={x}
            cy={y}
            r={radius}
            fill={color}
            opacity={0.25 + 0.55 * (1 - Math.abs(t - 0.5) * 2)}
          />
        );
      })}
    </svg>
  );
};
