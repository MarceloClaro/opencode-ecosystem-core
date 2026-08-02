#!/usr/bin/env python3
"""Quick fix: converte block-style lists no frontmatter para inline-style.

O parser _parse_skills_block do catalog_loader tem bugs com listas
no formato:
  tags:
  - item1
  - item2

Este script converte para:
  tags: [item1, item2]
"""

import re, os, sys
from pathlib import Path

CATALOG_DIR = Path("agents/catalog")

def fix_block_lists(filepath: Path, dry_run: bool = True) -> bool:
    """Converte block-style lists para inline-style no frontmatter YAML."""
    content = filepath.read_text(encoding="utf-8")
    
    # Find frontmatter
    match = re.match(r"^(---\s*\n)(.*?)(\n---)", content, re.DOTALL)
    if not match:
        return False
    
    start, yaml_text, end = match.group(1), match.group(2), match.group(3)
    
    # Find all block-style list patterns within the YAML
    # Pattern: key:\n  - item1\n  - item2
    # Must handle indentation properly
    
    # Process line by line to find and replace block lists
    lines = yaml_text.split('\n')
    new_lines = []
    i = 0
    modified = False
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line has key: followed by a block list
        stripped = line.strip()
        if ':' in stripped and not stripped.startswith('- '):
            key_part = stripped.split(':')[0].strip()
            # Valid key: no spaces, no special chars
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_-]*$', key_part):
                value_part = stripped[len(key_part)+1:].strip()
                if not value_part and i + 1 < len(lines):
                    # Check if next line starts a block list
                    base_indent = len(line) - len(line.lstrip())
                    list_indent = base_indent + 2  # typical indent for list items
                    
                    # Collect block list items
                    items = []
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j]
                        if not next_line.strip():
                            j += 1
                            continue
                        next_indent = len(next_line) - len(next_line.lstrip())
                        if next_indent >= base_indent + 1 and next_line.lstrip().startswith('- '):
                            item = next_line.lstrip('- ').strip()
                            items.append(item)
                            j += 1
                        else:
                            break
                    
                    if items:
                        # Replace block list with inline
                        inline = f"{' ' * base_indent}{key_part}: [{', '.join(items)}]"
                        new_lines.append(inline)
                        i = j
                        modified = True
                        continue
        
        new_lines.append(line)
        i += 1
    
    if not modified:
        return False
    
    new_yaml = '\n'.join(new_lines)
    new_content = start + new_yaml + end
    
    # Also fix the trailing body
    body = content[match.end():]
    new_content += body
    
    if not dry_run:
        filepath.write_text(new_content, encoding="utf-8")
    
    return True


def main():
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    agents = sorted(CATALOG_DIR.glob("*.md"))
    
    fixed = 0
    for agent_path in agents:
        if fix_block_lists(agent_path, dry_run=dry_run):
            fixed += 1
            verb = "FIXED" if not dry_run else "WOULD_FIX"
            print(f"  {verb}: {agent_path.name}")
    
    print(f"\n{fixed} agentes {'fixados' if not dry_run else 'para fixar'}")


if __name__ == "__main__":
    main()
