import {Composition, registerRoot} from 'remotion';
import {AiramVideo} from './AiramVideo';
import {TOTAL_FRAMES} from './timeline';

const Root = () => (
  <Composition
    id="AiramVerasVideo"
    component={AiramVideo}
    durationInFrames={TOTAL_FRAMES}
    fps={30}
    width={1920}
    height={1080}
  />
);

registerRoot(Root);
