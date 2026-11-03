# QC técnico

`scripts/video_qa.py` mede o que é observável. Use `--expect-frames` e
`--expect-fps` para contrato. Um `pass` significa que os predicados técnicos
passaram, não que o vídeo está bom. Um `fail` deve bloquear a entrega até
diagnóstico.
