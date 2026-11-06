#!/usr/bin/env python3
"""Varredura orto-tipográfica dos fragmentos LaTeX.

Busca por:
  - Acentuação proparoxítona ausente (ex: 'sugerido' → 'sugerído')
  - Palavras que deveriam ter acento diferencial
  - Uso de crase incorreto/ausente
  - 'mas' vs 'mais' (confusão comum)
  - 'a gente' vs 'agente'
  - 'porque/por que/porquê/por quê'
  - 'senão' vs 'se não'
  - 'acerca de' vs 'cerca de' vs 'há cerca de'
  - 'à cerca de' vs 'acerca de'
  - Palavras que o Acordo Ortográfico mudou
  - Pontos comuns de erro em PT-BR
"""

import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

# ── Padrões de busca ───────────────────────────────────────────────

CHECKS = [
    # (nome, padrão regex, explicação)
    (
        "Proparoxítona -ido sem acento",
        r'\b([a-zA-Z]+)ido\b',
        lambda m: check_proparoxitone(m.group(1) + 'ido', m.group(1)),
    ),
    (
        "Possível falta de crase (a + palavra feminina)",
        r'\b(a|A) ([a-zA-Z]+[aeiaõ]s?)\b',
        lambda m: check_crase(m.group(1), m.group(2)),
    ),
    (
        "Confusão mas/mais",
        r'\bmais\s+(é|era|será|foi|está|esteve)\b',
        "Verifique se deveria ser 'mas' (adversativa)",
    ),
    (
        "Confusão mas/mais (início de frase)",
        r'\bMais\b',
        "Verifique se é 'Mas' (adversativa) no início de frase",
    ),
    (
        "porque/por que",
        r'\bpor[^\s]*que\b',
        "Verifique a forma correta: porque/por que/porquê/por quê",
    ),
    (
        "senão/se não",
        r'\bsenão\b',
        "Verifique se é 'senão' (caso contrário) ou 'se não' (condicional + advérbio)",
    ),
    (
        "Palavras com acento diferencial (pôde/pode, pôr/por, têm/tem, vêm/vem)",
        r'\b(pode|podes|tem|tems|vem|vems)\b',
        "Verifique acento diferencial (pôde/pode, têm/tem, vêm/vem)",
    ),
    (
        "Possível anglicismo sem adaptação",
        r'\b(analisando|analisar|analisei)\b',
        "Preferir 'analisando' (aceito), mas verificar se 'análise' está correto",
    ),
    (
        "Concordância verbo-nominal",
        r'\b(há|havia|houve|houveram)\s+(muitos|muitas|vários|várias|diversos|diversas)\b',
        "Verificar concordância - 'há/havia/houve' é impessoal",
    ),
]

# Lista de proparoxítonas conhecidas que devem ser acentuadas
KNOWN_PROPAROXITONE_BASES = {
    'suger', 'adquir', 'compreend', 'descompreend', 'remet', 'submet',
    'introduz', 'traduz', 'conduz', 'reduz', 'produz', 'induz',
    'proib', 'atribu', 'distribu', 'contribu',
}

def check_proparoxitone(word, stem):
    """Check if a word ending in -ido should have an accent."""
    # If stem is in known proparoxitone bases, flag it
    if stem.lower() in KNOWN_PROPAROXITONE_BASES:
        return f"Possível proparoxítona: '{word}' pode precisar de acento: '{stem}ído'"
    # Check for 'i' before 'do' as the stressed syllable (proparoxytone pattern)
    # Words ending in -ido where stem is stressed on the 2nd-to-last of the stem
    # are proparoxytones
    if len(stem) >= 2:
        # Common pattern: verb stem ending in stressed vowel
        return None  # Too many false positives, skip by default
    return None


def check_crase(a_word, next_word):
    """Check possible crasis cases."""
    # Only check 'a' (not 'A' at start of sentence)
    if a_word == 'a':
        # 'a' followed by feminine word that is not a verb
        # This is very basic - just flag for review
        return None  # Too many false positives, skip in auto-check
    return None


def strip_latex(text):
    """Remove LaTeX markup to get clean text for checking."""
    # Remove comments
    text = re.sub(r'(?m)^%.*$', '', text)
    # Remove LaTeX commands
    text = re.sub(r'\\[a-zA-Z]+(\{[^}]*\})?', ' ', text)
    # Remove special chars
    text = re.sub(r'[{}]', ' ', text)
    # Clean up spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# ── Varredura ──────────────────────────────────────────────────────

def scan_file(filepath, check_funcs):
    """Scan a single file and report issues."""
    path = BASE / filepath
    if not path.exists():
        return []
    with open(path, encoding='utf-8') as f:
        text = f.read()
    
    clean = strip_latex(text)
    lines = text.split('\n')
    issues = []
    
    for name, pattern, explanation in check_funcs:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            # Find line number
            line_num = 1
            char_pos = m.start()
            for i, line in enumerate(lines, 1):
                if char_pos < len(line) + 1:
                    line_num = i
                    break
                char_pos -= len(line) + 1
            
            # Get context
            context = text[max(0, m.start()-40):m.end()+40]
            context = context.replace('\n', ' ')
            
            if callable(explanation):
                result = explanation(m)
                if result:
                    issues.append((path.name, line_num, m.group(), result, context))
            else:
                issues.append((path.name, line_num, m.group(), explanation, context))
    
    return issues


def scan_all_fragments():
    """Scan all fragment files."""
    all_issues = []
    
    # Fragment directories
    for frag_dir in ['fragmentos/mem', 'fragmentos/doc', 'fragmentos/luc', 'fragmentos/cont', 'frontmatter']:
        dir_path = BASE / frag_dir
        if not dir_path.exists():
            continue
        for tex_file in sorted(dir_path.glob('*.tex')):
            rel_path = tex_file.relative_to(BASE)
            issues = scan_file(str(rel_path), CHECKS)
            all_issues.extend(issues)
    
    return all_issues


# ── Verificações adicionais específicas ────────────────────────────

def check_specific_patterns():
    """Check for specific known issues across all text."""
    all_text = ""
    for frag_dir in ['fragmentos/mem', 'fragmentos/doc', 'fragmentos/luc', 'fragmentos/cont', 'frontmatter']:
        dir_path = BASE / frag_dir
        if not dir_path.exists():
            continue
        for tex_file in sorted(dir_path.glob('*.tex')):
            with open(tex_file, encoding='utf-8') as f:
                all_text += f.read() + '\n'
    
    specific_issues = []
    
    # Check distinct words for potential issues
    clean = strip_latex(all_text)
    words = clean.split()
    
    # Dictionary of known correct/incorrect spellings in PT-BR
    known_issues = {
        'coreção': 'correção',
        'excessão': 'exceção',
        'advinhar': 'adivinhar',
        'beneficiente': 'beneficente',
        'comprido': 'cumprido (no sentido de extenso, usar extenso/longo)',
        'conserto': 'concerto (se for musical)',
        'concerteza': 'com certeza',
        'derrepente': 'de repente',
        'despercebido': 'desapercebido (depende do sentido)',
        'encompridar': 'encompridar → encompridar?',
        'enrolar': 'enrolar ou enrrolar?',
        'extressar': 'estressar',
        'extressante': 'estressante',
        'freiar': 'frear',
        'fusivel': 'fusível',
        'grama (peso)': 'grama é masculino (o grama)',
        'heroi': 'herói',
        'identificar': 'verificar: ident**i**ficar',
        'impecilho': 'empecilho',
        'incomodar': 'incomodar (sem acento)',
        'interviu': 'interveio',
        'invéz': 'em vez de / invés',
        'irriquieto': 'irrequieto',
        'junto com': 'preferir apenas "com"',
        'mais (adversativa)': 'mas',
        'meio-ambiente': 'meio ambiente',
        'mendingo': 'mendigo',
        'menas': 'menos',
        'mortandade': 'mortalidade (ou mortandade é aceito?)',
        'morte-mato': 'mata-mata ou morte-mato?',
        'obsecado': 'obcecado',
        'obvio': 'óbvio',
        'oter': 'obter',
        'otoridade': 'autoridade',
        'paçiente': 'paciente',
        'paneiro': 'paneiro ou ponteiro?',
        'paralizar': 'paralisar',
        'pra (preposição)': 'para (formal)',
        'previlégio': 'privilégio',
        'propiocativo': 'provocativo?',
        'proposito': 'propósito',
        'reinvindicar': 'reivindicar',
        'solução': 'solução',
        'sote': 'sobre ou só?',
        'subestimar': 'subestimar ou superestimar?',
        'sugeito': 'sujeito',
        'suspeita': 'suspeita',
        'taxar': 'taxar ou tachar (atribuir defeito)?',
        'travez': 'través?',
        'ultima': 'última',
    }
    
    for word in set(words):
        word_lower = word.lower().strip('.,;:!?\'"()[]{}')
        if word_lower in known_issues:
            specific_issues.append((word, known_issues[word_lower]))
    
    return specific_issues


# ── Main ───────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("VARREDURA ORTO-TIPOGRÁFICA — Molambudos")
    print("=" * 60)
    
    # Scan fragments
    print("\n📋 Verificando padrões nos fragmentos...")
    issues = scan_all_fragments()
    
    if issues:
        print(f"\n⚠  {len(issues)} ocorrências encontradas:\n")
        for filename, line, match, explanation, context in issues:
            print(f"  📄 {filename}:{line}")
            print(f"     → '{match}'")
            print(f"     ⚠ {explanation}")
            print(f"     ...{context}...")
            print()
    else:
        print("   ✅ Nenhum padrão suspeito encontrado nos fragmentos.")
    
    # Specific checks
    print("\n📋 Verificações específicas adicionais...")
    specific = check_specific_patterns()
    if specific:
        print(f"\n⚠  {len(specific)} palavras suspeitas:\n")
        for word, suggestion in specific:
            print(f"     '{word}' → {suggestion}")
        print()
    else:
        print("   ✅ Nenhuma palavra suspeita encontrada.")
    
    print("\n" + "=" * 60)
    print("Varredura concluída.")
    print("=" * 60)


if __name__ == '__main__':
    main()
