import {Composition} from 'remotion';
import {Smoke} from './Smoke';
import {R1047Slide} from './r1047-slide/R1047Slide';

export const RemotionRoot = () => (
  <>
    <Composition
      id="Smoke"
      component={Smoke}
      durationInFrames={50}
      fps={25}
      width={1280}
      height={720}
    />
    <Composition
      id="R1047Slide"
      component={R1047Slide}
      durationInFrames={600}
      fps={30}
      width={935}
      height={864}
    />
  </>
);
