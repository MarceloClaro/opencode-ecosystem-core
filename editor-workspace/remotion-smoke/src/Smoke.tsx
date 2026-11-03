import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';

export const Smoke = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 25], [0, 1], {
    extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill
      style={{
        background: '#101820',
        color: '#f2f2f2',
        fontFamily: 'sans-serif',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <h1 style={{opacity, fontSize: 72}}>Editor universal</h1>
    </AbsoluteFill>
  );
};
