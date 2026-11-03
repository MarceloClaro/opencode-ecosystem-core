# UX Local — Panoramica AI (execução real em navegador isolado)

- **Data:** 2026-10-15
- **Execução:** `ecosystem_browser` (Playwright MCP 0.0.83, Chromium), ambiente real, 8,85 s
- **Alvo:** cópia local servida em `http://127.0.0.1:8791/index.html` (docroot `/tmp/opencode/rx-site`)
- **Origem autorizada:** `http://127.0.0.1:8791` (a app **não** fez nenhuma chamada externa)
- **Evidência:** `.opencode/browser/evidence/6850e1d3bc05ebbc15a155adcf9bd272e045b1b3d6e65b90ba1d30e6f32e70a9.json`
  (26.091 B, incluindo árvore de acessibilidade de 13.756 chars e log de console)
- **Nível de alegação:** observação de UI/UX local. Não é teste E2E do produto hospedado
  (backend ausente → a maioria dos fluxos fica em estado vazio/desabilitado).

## 1. Resultado da execução

| Item | Valor |
|---|---|
| Título | `Panoramica AI — Visualizador` |
| Ações concluídas | `navigate`, `read`, `snapshot`, `console_messages`, `close` |
| Erros de console | **9** (todos `404` de assets/endpoints ausentes localmente) |
| Sessão encerrada | sim (`browser_close_confirmed: true`) |

## 2. Mapa de navegação (5 rotas)

`/` Análise · `/review` Revisão · `/validacao` Validação · `/cadastro` Cadastro ·
`/docs` API / JSON · além de `/desejos` (Caixinha de desejos) e `/admin/api/*`.

## 3. Tela principal (Análise) — inventário de UX

**Estado inicial (empty states explícitos):** `status` "Selecione uma imagem de até
10 MiB." + botão "Fazer treinamento"; dropzone "Radiografia original"; 5 cards de
resultado com placeholders ("aparecem após a análise"):
Numeração FDI e quadrantes · Segmentação dentária · Anotações adicionais ·
Seios maxilares e canal mandibular · Dente a dente — original e marcado.

**Painel "Comandos" (complementary):**
- `Radiografia PNG/JPEG` (file), `Modelos` → `Pipeline completo` | `Somente Kaggle / Dental31`
- checkbox `Diagnosticar scores das 31 classes`
- spinbuttons: `Score mínimo 0.25` · `Score mínimo FDI 0.40` · `Score mínimo de canal e seio 0.10` · `Resolução do modelo 640`
- checkbox `Informações adicionais e anatomia` (**disabled**) · `Chave da API` (Somente Premium)
- `Analisar imagem` (ativo) · `Imprimir laudo` (**disabled**) + dica "Prévia A4: uma folha por imagem grande e até quatro dentes por folha"

**Edição (todas `disabled` sem análise):** quadrantes · caixas/FDI · achados DENTEX ·
máscaras · anotações adicionais · anatomia · `Salvar revisão no backend`.

**Legenda de classes:** Dente/número FDI · Impactado · Cárie · Lesão periapical ·
Cárie profunda · Informação adicional/Dental31 · Seio maxilar · Canal mandibular.

**Barra de estado / avisos (notável):**
> "Não foi possível verificar o modelo adicional. Recarregue a página."
> "Numeração por quadrante, de 1 a 8 do centro para fora. Dentes ausentes e achados
> exigem revisão clínica. **Os scores não são probabilidades de doença.**"

→ a própria UI embute **anti-overclaim** (revisão clínica + scores ≠ probabilidade),
alinhado às regras R110 do Core.

## 4. Elementos de engajamento/produto (abaixo da dobra)

- **Colaboradores** (6 cards): nome, especialidade, contador "**0** radiografias corrigidas", Instagram/LinkedIn por card.
- **Administradores**: Ronnei Borges Peres — "0 adultos · 0 crianças".
- **Próximo ciclo de inteligência**: `progressbar` 0/300, "300 radiografias completas",
  "300 restantes", 0%, etapas `01 Revisão especializada · 02 Curadoria do banco · 03 Novo treinamento da IA`.
  → modelo de **crowdsourcing de rotulagem** (300 revisões destravam o próximo treino).
- **Caixinha de desejos** → `/desejos`: feature-request board onde a comunidade apoia ideias.
- **Footer:** Panoramica AI · Open Source · Feito no Brasil 🇧🇷.

## 5. Sistema de design (a partir de `navigation.css` + classes)

- **Tema:** dark (`color-scheme: dark`), accent **teal** `#2dd4bf`/`#5eead4`.
- **Tokens observados:** fundo `#0a1119` (topbar translúcido `rgb(10 17 25/.97)`),
  borda `#29384a`, texto `#f8fafc`, mudo `#9fb1c5`, superfícies `#101a27`/`#172538`,
  ativo `#17343a`, perigo `#f87171`/`#fecaca`; **8 custom properties `--color:*`** inline.
- **Layout:** topbar fixa 64px, `backdrop-filter: blur(16px)`, container `min(1544px, 100% - 40px)`, nav com scroll horizontal (`scrollbar-color`).
- **Tipografia:** `system-ui`; pesos 650 (controles) e 760 (marca); `PA` mark 32px, radius 7px, glow.
- **Componentização:** Web Component `<panoramica-nav>`; CSS majoritariamente inline no HTML (só `navigation.css` é externo); nomenclatura kebab/BEM-ish (`reviewer-card`, `figure-action danger", `wishlist-dialog-shell`).
- **Responsivo:** breakpoint único `720px` (oculta texto da marca e o usuário, nav vira scroll).
- **Acessibilidade (boa):** roles `banner/navigation/main/complementary/region/contentinfo`;
  `aria-current="page"`; `aria-hidden` em decorativos; `progressbar` rotulada;
  `status` como região viva; `disabled` correto; `alt`/labels descritivos
  ("Abrir Instagram de X em nova aba"); `:focus-visible` estilizado.

## 6. Superfície real de backend revelada pelos 404

`/health`, `/reviewer-ranking`, `/reviewer-profiles`, `/administrator-statistics`,
`/training-progress`, `/admin/api/session` — mais assets `og-image.png`,
`training-video.mp4`, `favicon.ico`.

**Leitura:** a app é um cliente de um backend com *ranking/perfis de revisores* e
*estatísticas de administrador*; o contador "radiografias corrigidas" e a barra
`/300` são alimentados por `/training-progress`.

## 7. Guarda de rede

`network_guard` negou pedidos de fundo do Chromium (`accounts.google.com`,
`update.googleapis.com`, `www.google.com`). **Nenhuma chamada de terceiros
partiu da aplicação** — a única origem permitida foi a local.

## 8. Limitações

- Rodou com backend ausente: fluxos de análise, revisão e salvamento **não** foram exercitados.
- Cópia parcial (faltam vídeo, fotos de colaboradores, favicon) → 404 cosméticos.
- UX do produto hospedado pode divergir (versão do deploy remoto).
- Sem medição de performance (LCP/CLS) nem teste cross-browser.
