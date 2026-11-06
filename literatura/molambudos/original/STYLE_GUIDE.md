# GUIA DE ESTILO — MOLAMBUDOS

## Paleta de Estimulação Sensorial Extrema

### Cores Base (Dark Mode Absoluto)

```
BG_PRINCIPAL:      #0a0a0a  (preto absoluto)
BG_SECUNDARIO:     #0f0f0f  (quase preto)
BG_TERCIARIO:      #1a0a0a  (preto com sangue)
BORDA:             #2a0a0a  (bordas sutis)

TEXTO_PRINCIPAL:   #f0d0c0  (pele pálida à luz de velas)
TEXTO_SECUNDARIO:  #8a4a3a  (sangue seco)
TEXTO_MUTED:       #3a1a1a  (quase invisível, como cicatriz)
```

### Paleta de Estimulação

```
SANGUE_VIVO:       #cc0a0a  (vermelho arterial — alerta máximo)
SANGUE_VENOSO:     #8a0a0a  (vermelho escuro — tensão)
FOGO:              #ff4a0a  (laranja — perigo iminente)
OLHO_AMARELO:      #ccaa0a  (amarelo pústula — contaminação)
BRILHO:            #ffcc44  (amarelo claro — o olho na escuridão)
```

### Por Tipo de Fragmento

| Tipo | Background | Cor do Título | Efeito Visual |
|---|---|---|---|
| **DOC** | `#0f0f0f` (cinza chumbo) | `#cc0a0a` (sangue) | Bordas finas, como papel queimado |
| **MEM** | `#0a0500` (sépia escuro) | `#ccaa0a` (olho) | Textura de terra rachada ao fundo |
| **CONT** | `#1a0000` (preto sangrento) | `#ff4a0a` (fogo) | Pulso sutil, sombra animada |
| **LUC** | `#05050a` (azul noturno) | `#8a4a3a` (sangue seco) | Névoa sutil, como arquivo empoeirado |

### Tipografia

```
TITULOS:    'Creepster', 'UnifrakturCook', serifa gótica
CORPO:      'Crimson Text', 'EB Garamond', serifa clássica
CONT (2ªp): 'Inconsolata', monoespaçada — voz da criatura
DOC:        'Courier Prime', monoespaçada — máquina de escrever
```

### Elementos Visuais

1. **Molambudos Pattern** — textura de terra rachada no fundo dos MEM
2. **Sangramento de tinta** — manchas de tinta nas bordas dos CONT
3. **Olho Amarelo** — ícone animado (pisca a cada 3s) nos CONT
4. **Número 1.260** — marca d'água em todas as páginas dos DOC
5. **Fileira de dentes** — separador entre fragmentos nos MEM
6. **Rasga Mortalha** — silhueta de coruja nos fragmentos de contaminação avançada

### Como Aplicar

```css
/* Exemplo de aplicação */
.fragment-CONT {
    background: #1a0000;
    border-left: 4px solid #ff4a0a;
    box-shadow: 0 0 30px rgba(204, 170, 10, 0.1);
    animation: pulse 4s ease-in-out infinite;
}
.fragment-MEM {
    background: #0a0500;
    border: 1px solid #2a0a0a;
}
.fragment-DOC {
    background: #0f0f0f;
    font-family: 'Courier Prime', monospace;
    border: 1px dashed #3a1a1a;
}
.fragment-LUC {
    background: #05050a;
    border-left: 4px solid #8a4a3a;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.85; }
}
```
