# -*- coding: utf-8 -*-
from pathlib import Path
d = Path(r'C:\Users\marce\.config\opencode\artigo-mit-ia')
f1 = d / '01-introducao-referencial.md'
content = f1.read_text('utf-8', errors='replace')
print("File 1 length:", len(content))
print("First 100 chars:", content[:100])
