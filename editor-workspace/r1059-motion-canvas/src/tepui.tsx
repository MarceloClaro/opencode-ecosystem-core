import {Circle, Line, Node, makeScene2D} from '@motion-canvas/2d';
import {all, createRef, easeInOutCubic, easeOutBack, easeOutCubic, linear, waitFor} from '@motion-canvas/core';

// Ilustração vetorial original em planos 2D. Não é modelo 3D do relevo.
export default makeScene2D(function* (view) {
  const mountain = createRef<Node>();
  const clouds = createRef<Node>();
  const pulse = createRef<Circle>();
  const guides = [createRef<Line>(), createRef<Line>(), createRef<Line>()];

  view.add(
    <Node ref={mountain} y={90} scale={0.35} opacity={0}>
      {/* base rochosa */}
      <Line points={[[-240, 170], [225, 170], [165, 215], [-185, 215]]}
        closed fill={'#071b25cc'} />
      {/* face frontal: paredão com estrias verticais */}
      <Line points={[[-205, -25], [205, -25], [235, 155], [-235, 155]]}
        closed fill={'#8a6647'} stroke={'#332c25'} lineWidth={3} />
      {/* estratos sedimentares horizontais */}
      {[[10, 0.42], [44, 0.5], [78, 0.38], [112, 0.48], [144, 0.34]].map(([y, a], i) => (
        <Line key={`stratum-${i}`}
          points={[[-211 + i * 3, y + (i % 2 ? 2 : -2)], [-40, y - 3], [96, y + 2], [213 + i * 2, y - 4]]}
          stroke={i % 2 ? '#6b4d35' : '#a57f57'} lineWidth={i % 2 ? 2 : 3} opacity={a} />
      ))}
      {/* fissuras curtas, sem formar grade */}
      {[[-138, -18], [-34, -10], [96, -16]].map(([x, y], i) => (
        <Line key={`fissure-${i}`}
          points={[[x, y], [x + (i % 2 ? 9 : -7), y + 34], [x + (i % 2 ? -2 : 6), y + 62]]}
          stroke={'#5b3f2c'} lineWidth={2} opacity={0.5} />
      ))}
      {/* manchas de alteração na rocha */}
      {[[-96, 58, 46, 22], [42, 102, 62, 18], [158, 46, 38, 16]].map(([x, y, w, h], i) => (
        <Circle key={`patch-${i}`} x={x} y={y} width={w} height={h} fill={'#6d4f37'} opacity={0.22} />
      ))}
      {/* blocos de talus na base */}
      {[-210, -168, -110, 60, 132, 196].map((x, i) => (
        <Line key={`talus-${i}`} points={[[x, 150], [x + 22, 150], [x + 12, 176]]}
          closed fill={'#6f5138'} stroke={'#332c25'} lineWidth={1.5} />
      ))}
      {/* lateral direita em perspectiva */}
      <Line points={[[205, -25], [150, -110], [178, 62], [235, 155]]}
        closed fill={'#6a513d'} stroke={'#332c25'} lineWidth={2} />
      {/* platô */}
      <Line points={[[-160, -110], [150, -110], [205, -25], [-205, -25]]}
        closed fill={'#b28d60'} stroke={'#3a3129'} lineWidth={3} />
      <Line points={[[-160, -110], [150, -110]]} stroke={'#d8b483'} lineWidth={3} />
      {[-118, -62, -8, 46, 96].map((x, i) => (
        <Circle key={`moss-${i}`} x={x} y={-82 + (i % 2) * 16} width={34 + i * 3}
          height={11 + (i % 3) * 3} fill={'#6e9a68'} />
      ))}
      {/* nuvens na base, não sobre a parede */}
      <Node ref={clouds} x={-10} y={150} opacity={0}>
        {Array.from({length: 12}, (_, i) => (
          <Circle key={`cloud-${i}`} x={-230 + i * 42} y={Math.sin(i * 2.1) * 9}
            width={48 + (i % 3) * 12} height={30 + (i % 4) * 8}
            fill={i % 2 ? '#fffffff0' : '#e4f0ecf0'} />
        ))}
      </Node>
    </Node>,
  );

  // Conectores didáticos às etiquetas de país; não são fronteiras oficiais.
  const starts: [number, number][] = [[-150, -70], [150, -60], [-165, 55]];
  const ends: [number, number][] = [[0, -238], [236, 62], [-236, 78]];
  ends.forEach((end, i) => view.add(
    <Line ref={guides[i]} points={[starts[i], end]}
      stroke={['#ffd34e', '#73d5ef', '#87e0b1'][i]} lineWidth={3}
      lineDash={[8, 7]} end={0} opacity={0.85} />,
  ));
  view.add(<Circle ref={pulse} x={0} y={-66} size={14} stroke={'#ffe394'} lineWidth={3} opacity={0} />);

  // 0–1,2 s: a mesa cresce no centro.
  yield* all(
    mountain().opacity(1, 0.35),
    mountain().scale(1, 0.8, easeOutBack),
    mountain().y(0, 0.8, easeOutCubic),
  );
  // 1,2–6 s: nuvens deslizam na base.
  yield* all(
    clouds().opacity(1, 0.5),
    clouds().x(18, 5.2, linear),
  );
  // 6–7 s: conectores até as etiquetas dos três países.
  yield* all(...guides.map((ref) => ref().end(1, 0.8, easeOutCubic)));
  yield* waitFor(0.4);
  // 7,2–10 s: pulso no topo.
  for (let i = 0; i < 3; i++) {
    pulse().size(14);
    pulse().opacity(0.95);
    yield* all(pulse().size(96, 0.9, easeOutCubic), pulse().opacity(0, 0.9));
  }
  yield* waitFor(0.1);
});
