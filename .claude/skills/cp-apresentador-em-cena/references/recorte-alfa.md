# Recorte alfa verificável

Leia somente quando a composição precisar separar a pessoa do fundo.

## Verifique a capacidade real

Identifique uma ferramenta de segmentação ou chroma key realmente disponível e compatível com o material. Confira requisitos, licença do modelo, recursos computacionais e formato de saída antes de prometer a técnica. A presença de uma skill não prova que a ferramenta existe ou funciona nesse ambiente.

Comece com cerca de cinco segundos que incluam cabelo, mãos, movimento e eventual cruzamento de objetos. Use a mesma resolução de trabalho e o mesmo caminho de renderização planejados para a edição; um teste reduzido serve para viabilidade, mas precisa ser conferido no tamanho final antes de escalar.

## Julgue o contorno, não só o fundo removido

Observe o trecho sobre fundo claro e escuro, com a camada que passará atrás da pessoa. Confira em reprodução e nos frames críticos:

- Cabelo e dedos continuam presentes; ombros não encolhem ou desaparecem.
- Não surgem buracos no rosto ou corpo, duplicação de bordas ou fundo original preso ao contorno.
- O limite não pulsa nem deixa rastros quando a pessoa se move.
- O texto de trás desaparece na área ocupada pela pessoa e reaparece onde realmente há fundo.
- A suavidade da borda combina com a imagem, sem halo criado por feather excessivo ou alfa interpretado incorretamente.

Se a qualidade não passar, tente uma correção localizada justificada. Se persistir, descarte a saída para essa composição, identifique o limite e proponha moldura com fundo original ou nova gravação adequada. Não esconda o defeito com brilho, borrão forte ou máscara geométrica.

## Preserve e reutilize

Guarde origem, intervalo usado, FPS, dimensões e alinhamento do alfa. Reutilize a camada ao ajustar lettering ou posição. Confira se a ferramenta produziu vídeo com canal alfa, sequência RGBA ou vídeo de máscara; esses formatos não são intercambiáveis sem composição apropriada.

Mantenha uma versão da transparência em formato compatível e a entrega final já composta. Um MP4 H.264 comum não preserva esse canal. Verifique o arquivo decodificado, sem inferir transparência apenas pelo nome do codec ou pela aparência do player.
