# Química em nuvem — adaptação original

**Objetivo:** usar API proprietária de modelagem molecular com custo e termos
explícitos.

**Fluxo:** confirmar conta, termos e orçamento; classificar dado (público,
sensível, proprietário); enviar somente o mínimo autorizado; registrar job,
versão, parâmetros e hash; comparar com baseline local; revisar resultado.

**Gates:** API key nunca no repositório; não enviar dado confidencial sem
autorização; custo por job; predição não é síntese nem ensaio.

**Saída:** recibo do job, resultado, custo, validação e limites.
