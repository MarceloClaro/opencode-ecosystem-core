import {Composition, registerRoot} from 'remotion';
import {R1047Stage} from './R1047Stage';

const Root = () => (
  <Composition
    id="R1047Stage"
    component={R1047Stage}
    durationInFrames={600}
    fps={30}
    width={1920}
    height={1080}
  />
);

registerRoot(Root);
