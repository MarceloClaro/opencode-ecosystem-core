# Template Remotion — intro/outro

Template mínimo para motion graphics de um estúdio técnico. Renderiza uma
abertura e um encerramento de 3 s em 1920×1080/30 fps.

## Uso

```bash
npm install
npm run render:intro   # out/intro.mp4
npm run render:outro   # out/outro.mp4
```

Depois, na pasta do piloto:

```bash
../render-studio.sh out/intro.mp4 ../pilot-16x9-lipsync.mp4 out/outro.mp4 \
  ../pilot-16x9-studio.mp4
```

## Licença

Remotion usa a **Remotion License**, não uma licença OSI. Pessoa física, ONG e
empresa com até 3 funcionários têm uso gratuito; acima disso, licença comercial.
Este template não copia código do Remotion.

## Limites

O template é uma base de estudo. Ajuste tipografia, cores e textos à identidade
do projeto; valide a prévia antes de renderizar e preserve o master.
