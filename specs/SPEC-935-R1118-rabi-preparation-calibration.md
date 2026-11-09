# SPEC-935-R1118 — Calibração Rabi da preparação de q1

**Status:** implementação local
**Data:** 2026-11-09
**Depende de:** R1115/R1117 (tomografia), R1116 (scorecard)

## 1. Contexto

A tomografia R1117 mostrou que `prep |1>` = 1 − r1, ou seja, a fidelidade de
preparação de |1> e o erro de leitura são a mesma contagem Z. Não é possível
separar erro coerente de preparação de erro de leitura apenas com os 12
circuitos da tomografia.

A calibração proposta mede uma oscilação Rabi completa em q1:

- 8 ângulos de rotação, de π/4 a 2π;
- 2 eixos, `rx` e `ry`;
- 4096 shots por ponto;
- 16 jobs no total.

O modelo `p1(θ) = r0 + A·sin²((θ+ε)/2)` estima simultaneamente:

- `r0`: erro de leitura 0→1;
- `A = 1 − r0 − r1`: contraste de leitura;
- `r1`: erro de leitura 1→0;
- `ε`: desvio coerente do ângulo de π.

## 2. Requisitos

- **R1.** Plano com 8 ângulos × 2 eixos, parametrizado por qubit.
- **R2.** Simulação ideal: `p1 = sin²(θ/2)`.
- **R3.** Ajuste linearizado `c0 + c1 cos θ + c2 sin θ`, com erros padrão.
- **R4.** Reportar `r0`, `r1`, `A`, `ε`, `θ* = π − ε` e ganho vs π.
- **R5.** Marcar `identified = False` quando o contraste for inviável ou
  `r0 + r1 ≥ 1`.
- **R6.** Comparar `rx` e `ry`; preferir um eixo só quando a diferença de |ε|
  superar 2 erros padrão combinados.
- **R7.** TDD antes de hardware; simulação antes de submissão; `confirm=True`
  e `allow_hardware=True`.
- **R8.** Nenhuma chave em arquivo/log; usar conta cacheada quando disponível.
- **R9.** Não declarar melhora sem run de validação em ângulo corrigido.
- **R10.** Limites explícitos: decaimento/depuração podem enviesar o contraste.

## 3. Modelo

Para cada eixo:

```
p1(θ) = r0 + A · sin²((θ + ε)/2)
      = c0 + c1 cos θ + c2 sin θ
c0 = r0 + A/2
c1 = −(A/2) cos ε
c2 = (A/2) sin ε
A = 2√(c1² + c2²)
ε = atan2(c2, −c1)
r0 = c0 − A/2
r1 = 1 − r0 − A
θ* = π − ε
ganho vs π = A · sin²(ε/2)
```

## 4. Critérios de aceitação

- 16 circuitos no plano, 8 por eixo;
- simulação ideal passa;
- ajuste sintético recupera `ε` dentro de 0,02 rad e `r0/r1` dentro de 0,01
  com 200 mil shots;
- `identified=False` para contraste inviável;
- script bloqueia sem confirmação;
- resultado em JSON com counts, task_ids, fit e limites;
- nenhum overclaim.

## 5. Resultado do run em q1 (Baihua, 16 jobs)

| Eixo | ε (rad) | SE ε | r0 | r1 | Contraste | χ²/dof |
|---|---:|---:|---:|---:|---:|---:|
| rx | −0,0006 | 0,0091 | 0,0156 | 0,0695 | 0,9149 | 1,54 |
| ry | +0,0012 | 0,0129 | 0,0126 | 0,0786 | 0,9088 | 3,13 |

- Eixo preferido: **none** (diferença de |ε| abaixo de 2σ).
- Ganho estimado vs π: ~1e−7 (desprezível).
- Nenhum desvio coerente acima de 2σ foi detectado.
- O erro dominante é de leitura; não há justificativa para corrigir o ângulo.
- `r1` do Rabi (0,0695–0,0786) é próximo do `r1` da tomografia (0,0837),
  com diferença compatível com modelo/drift; não é prova de inconsistência.

## 6. Não objetivos

- Provar que `rx` ou `ry` é melhor em geral.
- Declarar ganho sem validação.
- Separar decaimento de erro coerente.
- Executar hardware sem confirmação.
