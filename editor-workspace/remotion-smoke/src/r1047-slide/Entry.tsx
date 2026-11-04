import {Composition, registerRoot} from 'remotion';
import {R1047Slide} from './R1047Slide';

const Root = () => (
  <Composition
    id="R1047Slide"
    component={R1047Slide}
    durationInFrames={600}
    fps={30}
    width={935}
    height={864}
  />
);

registerRoot(Root);
