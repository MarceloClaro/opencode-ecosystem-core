# Consentimento e licenças — dublagem com voz clonada

## Declaração do operador

- Voz de referência: apresentadora do vídeo `sVRpKhCfKRI` (canal Qiskit).
- Em 02/11/2026, o operador declarou possuir **consentimento escrito** da voz
  de referência para a clonagem.
- O Core **não verificou** esse consentimento; ele é registrado como declaração
  do operador, não como prova documental.
- Uso pretendido: **piloto pessoal/estudo, não comercial**.

## Licenças dos modelos

| Componente | Licença | Observação |
|---|---|---|
| XTTS v2 (Coqui) | Coqui Public Model License (CPML) | uso não comercial; requer aceite |
| Wav2Lip | licença do repositório: pessoal/pesquisa/não comercial | não usar em produto comercial |
| Piper | MIT | voz sintética anterior, não clonada |
| Remotion | Remotion License | pessoa física; não é MIT |

## Limites de uso

- A voz clonada não deve ser apresentada como a pessoa real sem autorização.
- Em publicação, identifique a dublagem como sintética/clonada quando exigido.
- Não use o resultado para endossar produtos, declarações ou opiniões que a
  apresentadora não fez.
- O consentimento declarado cobre esta voz e este piloto; não se estende a
  outros vídeos, campanhas ou usos comerciais.
- O Core não faz parecer jurídico.

## Registro técnico

- Referência: `presenter-ref.wav`, 6,0 s, 24 kHz mono, extraída do início do
  clipe.
- Modelo de voz: XTTS v2, CPU.
- Lip sync: Wav2Lip, CPU, checkpoint `wav2lip_gan.pth`.
- Nenhum áudio ou peso é enviado a serviço externo nesta etapa.
