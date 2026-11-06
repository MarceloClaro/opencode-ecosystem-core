// Gerado por pilots/r1055-qubit/build_remotion_timeline.py
export const FPS = 30;
export const TOTAL_FRAMES = 3292;
export type Caption = {
  startFrame: number;
  endFrame: number;
  text: string;
};
export type Scene = {
  id: string;
  title: string;
  subtitle: string;
  startFrame: number;
  endFrame: number;
  captions: Caption[];
};

export const SCENES: Scene[] = [
  {
    id: "01",
    title: "O que é um qubit?",
    subtitle: "Sabe o que é um qubit? Não é um bit menor. É outra unidade de informação. Pensa numa moeda girando: enquanto gira, ela não é cara nem coroa. Ela é as duas possibilidades. Só quando para, você vê um resultado.",
    startFrame: 12, endFrame: 565,
    captions: [
      {startFrame: 12, endFrame: 75, text: "Sabe o que é um qubit?"},
      {startFrame: 84, endFrame: 146, text: "Não é um bit menor."},
      {startFrame: 152, endFrame: 227, text: "É outra unidade de informação."},
      {startFrame: 238, endFrame: 377, text: "Pensa numa moeda girando: enquanto gira, ela não é cara nem coroa."},
      {startFrame: 388, endFrame: 465, text: "Ela é as duas possibilidades."},
      {startFrame: 474, endFrame: 565, text: "Só quando para, você vê um resultado."},
    ],
  },
  {
    id: "02",
    title: "Superposição",
    subtitle: "Na física, isso é superposição: α|0⟩ + β|1⟩. O quadrado de cada amplitude dá a probabilidade de medir 0 ou 1. Antes de medir, ele evolui como uma onda.",
    startFrame: 578, endFrame: 986,
    captions: [
      {startFrame: 578, endFrame: 729, text: "Na física, isso é superposição: α|0⟩ + β|1⟩."},
      {startFrame: 738, endFrame: 877, text: "O quadrado de cada amplitude dá a probabilidade de medir 0 ou 1."},
      {startFrame: 886, endFrame: 986, text: "Antes de medir, ele evolui como uma onda."},
    ],
  },
  {
    id: "03",
    title: "Medição",
    subtitle: "Agora vem a parte que confunde. O que acontece quando você mede? A onda colapsa: você vê 0 ou 1. Na esfera de Bloch, as portas quânticas são rotações.",
    startFrame: 1000, endFrame: 1410,
    captions: [
      {startFrame: 1000, endFrame: 1078, text: "Agora vem a parte que confunde."},
      {startFrame: 1086, endFrame: 1167, text: "O que acontece quando você mede?"},
      {startFrame: 1175, endFrame: 1280, text: "A onda colapsa: você vê 0 ou 1."},
      {startFrame: 1292, endFrame: 1410, text: "Na esfera de Bloch, as portas quânticas são rotações."},
    ],
  },
  {
    id: "04",
    title: "Emaranhamento",
    subtitle: "Dois qubits podem ser emaranhados. O estado de Bell correlaciona resultados que nenhuma teoria clássica local explica. Aspect, Clauser e Zeilinger testaram — e o Nobel de 2022 reconheceu.",
    startFrame: 1423, endFrame: 1863,
    captions: [
      {startFrame: 1423, endFrame: 1511, text: "Dois qubits podem ser emaranhados."},
      {startFrame: 1520, endFrame: 1679, text: "O estado de Bell correlaciona resultados que nenhuma teoria clássica local explica."},
      {startFrame: 1690, endFrame: 1863, text: "Aspect, Clauser e Zeilinger testaram — e o Nobel de 2022 reconheceu."},
    ],
  },
  {
    id: "05",
    title: "Interferência e limite",
    subtitle: "O ganho não é testar tudo ao mesmo tempo. É interferência: amplificar os caminhos certos e cancelar os errados. O inimigo é a decoerência: por isso, um qubit lógico exige muitos qubits físicos.",
    startFrame: 1876, endFrame: 2294,
    captions: [
      {startFrame: 1876, endFrame: 1968, text: "O ganho não é testar tudo ao mesmo tempo."},
      {startFrame: 1975, endFrame: 2115, text: "É interferência: amplificar os caminhos certos e cancelar os errados."},
      {startFrame: 2126, endFrame: 2294, text: "O inimigo é a decoerência: por isso, um qubit lógico exige muitos qubits físicos."},
    ],
  },
  {
    id: "06",
    title: "Origem",
    subtitle: "Essa ideia não nasceu num só lugar. Copenhague, Viena e Leipzig. Feynman propôs computar com ela, na Califórnia, em 1982. Schumacher batizou o qubit em Ohio, em 1995. E o Nobel de 2022 veio de Paris, Berkeley e Viena.",
    startFrame: 2308, endFrame: 2960,
    captions: [
      {startFrame: 2308, endFrame: 2394, text: "Essa ideia não nasceu num só lugar."},
      {startFrame: 2403, endFrame: 2486, text: "Copenhague, Viena e Leipzig."},
      {startFrame: 2497, endFrame: 2656, text: "Feynman propôs computar com ela, na Califórnia, em 1982."},
      {startFrame: 2666, endFrame: 2811, text: "Schumacher batizou o qubit em Ohio, em 1995."},
      {startFrame: 2822, endFrame: 2960, text: "E o Nobel de 2022 veio de Paris, Berkeley e Viena."},
    ],
  },
  {
    id: "07",
    title: "Autor",
    subtitle: "Muito obrigado por assistir. Projeto de Marcelo Claro Laranjeira. O QR code leva ao GitHub.",
    startFrame: 2974, endFrame: 3292,
    captions: [
      {startFrame: 2974, endFrame: 3047, text: "Muito obrigado por assistir."},
      {startFrame: 3056, endFrame: 3226, text: "Projeto de Marcelo Claro Laranjeira. O QR code leva ao GitHub."},
    ],
  },
];
