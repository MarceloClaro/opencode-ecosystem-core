import {Composition} from 'remotion';
import {Smoke} from './Smoke';

export const RemotionRoot = () => (
  <Composition
    id="Smoke"
    component={Smoke}
    durationInFrames={50}
    fps={25}
    width={1280}
    height={720}
  />
);
