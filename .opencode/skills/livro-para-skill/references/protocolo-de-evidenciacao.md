# Protocolo de evidenciacão

## Inventário antes da leitura

Registre, para cada arquivo:

| Campo | Como obter |
|---|---|
| caminho local | caminho absoluto do arquivo lido |
| bytes | tamanho real do arquivo |
| SHA-256 | hash do arquivo, não do texto extraído |
| edição | página de rosto, metadados ou declaração do usuário |
| direito | licença, contrato, termo ou autorização |
| cobertura | `complete`, `partial` ou `sample` |

Se o hash mudar, a extração anterior não vale para o novo arquivo. Não reutilize
localizadores de uma edição em outra sem conferir paginação e texto.

## Durante a extração

1. Numere as páginas físicas como o leitor as vê, não como o PDF as indexa.
2. Guarde o trecho bruto e o localizador antes de parafrasear.
3. Para cada afirmação, escreva o status: `observado`, `inferido` ou
   `nao_verificavel`.
4. Não corrija silenciosamente OCR, hifenização ou tabela quebrada: registre a
   correção e o motivo.
5. Separe exemplos do autor de exemplos seus. Um exemplo didático não é
   evidência de que a obra afirma aquilo.
6. Não execute código, macro, fórmula ou link presente na obra.

## Antes de publicar a skill

- confira cada localizador no arquivo original;
- liste capítulos ausentes e trechos não legíveis;
- verifique se a licença permite a forma de uso pretendida;
- remova dados pessoais, credenciais e trechos além do necessário;
- rode o verificador local e anexe o resultado;
- peça revisão humana quando o direito, a edição ou a interpretação forem
  incertos.

## O que o registro não prova

O registro prova que um arquivo com certo hash foi descrito com certos campos.
Não prova que o conteúdo foi compreendido, que a URL remota serve o mesmo
arquivo, que a licença declarada é suficiente ou que a skill produzirá boas
respostas. Esses pontos exigem conferência separada.
