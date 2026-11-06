import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {RoraimaVideo} from './RoraimaVideo';

const Root: React.FC = () => (
  <Composition
    id="RoraimaStudy"
    component={RoraimaVideo}
    durationInFrames={300}
    fps={30}
    width={720}
    height={1280}
  />
);

registerRoot(Root);
