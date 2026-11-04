import {Composition, registerRoot} from 'remotion';
import {QubitExplainer} from './QubitExplainer';
import {TOTAL_FRAMES} from './timeline';

const Root = () => (
  <Composition
    id="QubitExplainer"
    component={QubitExplainer}
    durationInFrames={TOTAL_FRAMES}
    fps={30}
    width={1920}
    height={1080}
  />
);

registerRoot(Root);
