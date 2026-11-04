import {Composition, registerRoot} from 'remotion';
import {QubitVertical} from './QubitVertical';
import {TOTAL_FRAMES} from './timeline';

const Root = () => (
  <Composition
    id="QubitVertical"
    component={QubitVertical}
    durationInFrames={TOTAL_FRAMES}
    fps={30}
    width={1080}
    height={1920}
  />
);

registerRoot(Root);
