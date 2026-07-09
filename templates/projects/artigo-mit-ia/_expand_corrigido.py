# -*- coding: utf-8 -*-
from pathlib import Path
d = Path(r'C:\Users\marce\.config\opencode\artigo-mit-ia')
f1 = d / "01-introducao-referencial.md"
content = f1.read_text('utf-8', errors='replace')
parts = content.split('---', 2)
body = parts[2]
body = body.replace('(Gill & Kharas, 2007)', '(Gill & Kharas, 2007)[^1]')
body = body.replace('(World Bank, 2024)', '(World Bank, 2024)[^2]', 1)
body = body.replace('(Brynjolfsson et al., 2023)', '(Brynjolfsson et al., 2023)[^3]')
body = body.replace('(Cazzaniga et al., 2024)', '(Cazzaniga et al., 2024)[^4]')
body = body.replace('(Bresnahan & Trajtenberg, 1995)', '(Bresnahan & Trajtenberg, 1995)[^5]')
body = body.replace('(Cerutti et al., 2025)', '(Cerutti et al., 2025)[^6]', 1)
body = body.replace('(Veloso, 2024)', '(Veloso, 2024)[^7]')
body = body.replace('(Imam & Temple, 2024)', '(Imam & Temple, 2024)[^8]')
if '## Notas' in body:
body = body.split('## Notas')[0]
body += '\n\n## Notas TSAC\n\n'
body += '[^1]: Gill & Kharas (2007). An East Asian Renaissance: Ideas for Economic Growth. Washington, DC: World Bank.\n\n'
body += '[^2]: World Bank (2024). World Development Report 2024: The Middle-Income Trap. https://www.worldbank.org/en/publication/wdr2024\n\n'
body += '[^3]: Brynjolfsson, E., Li, D., & Raymond, L. R. (2023). Generative AI at work. NBER WP 31161. https://doi.org/10.3386/w31161\n\n'
body += '[^4]: Cazzaniga, M. et al. (2024). Gen-AI: AI and the future of work. IMF SDN/2024/001.\n\n'
body += '[^5]: Bresnahan, T. F. & Trajtenberg, M. (1995). General purpose technologies. J. of Econometrics, 65(1). https://doi.org/10.1016/0304-4076(94)01598-T\n\n'
body += '[^6]: Cerutti, E. et al. (2025). AI and economic growth. IMF WP/25/76.\n\n'
body += '[^7]: Veloso, F. (2024). Como não escapar da armadilha da renda media. Portal FGV.\n\n'
body += '[^8]: Imam, P. A. & Temple, J. R. W. (2024). At the threshold. IMF WP/24/91.\n\n'
body += '[^9]: Paus, E. (2020). Innovation strategies matter. J. of Dev. Studies, 56(4). https://doi.org/10.1080/00220388.2019.1595600\n\n'
body += '[^10]: Glawe, L. & Wagner, H. (2020). MIT 2.0. CEAMeS DP 1/2020.\n\n'
body += '[^11]: Nair, J. M. (2026). Evolution of MIT research. SN Business & Economics, 6, 98. https://doi.org/10.1007/s43546-026-01104-w\n\n'
body += '[^12]: OECD (2025). Effects of generative AI on productivity. OECD Publishing.\n\n'
f1.write_text(parts[0] + '---' + parts[1] + '---' + body, encoding='utf-8')
print('File 1 TSAC done')
