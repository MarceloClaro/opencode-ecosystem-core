# Política de segurança

## Relatar uma vulnerabilidade

Para uma vulnerabilidade potencial, use o formulário de [Security Advisories](https://github.com/MarceloClaro/opencode-ecosystem-core/security/advisories/new) deste repositório no GitHub. Não abra issue pública, não publique prova de conceito explorável e não inclua tokens, chaves, dados pessoais ou artefatos sensíveis.

Descreva, quando possível:

1. a revisão Git afetada;
2. o componente e o ambiente de execução;
3. passos mínimos para reproduzir o comportamento;
4. impacto observado e limites conhecidos;
5. mitigação temporária já testada, se houver.

Se o recurso não estiver disponível para sua conta, solicite ao mantenedor do
repositório a abertura de um canal privado antes de divulgar detalhes técnicos.

## Escopo e tratamento

Os relatos serão avaliados conforme reprodutibilidade, impacto, evidências e
condições do ambiente. Um relato recebido ou uma correção incorporada não
representa certificação externa do sistema, de dependências de terceiros ou de
ambientes de instalação.

Não realize testes destrutivos, indisponibilização de serviços, acesso a dados
de terceiros ou tentativa de contornar controles sem autorização explícita.

## Boas práticas para usuários

- confira versão, commit e hash publicados antes de executar instaladores;
- execute scripts a partir de checkout local revisado;
- mantenha credenciais fora do repositório e de logs;
- se uma credencial puder ter sido exposta, revogue-a ou rotacione-a
  imediatamente no provedor, substitua-a no ambiente ou cofre de segredos e
  não a reutilize;
- use ambientes isolados para dependências Python;
- revise saídas de modelos e ferramentas antes de empregá-las em domínios
  sensíveis.

Consulte [installer/README.md](installer/README.md),
[installer/windows/README.md](installer/windows/README.md) e
[CORRIGENDUM.md](CORRIGENDUM.md) para limites adicionais.
