#!/usr/bin/env python3
"""
Test script to validate LaTeX structure of dissertation chapters.
"""

import os
import re
import sys
from pathlib import Path

# Set stdout encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def check_latex_structure(file_path):
    """Check LaTeX structure of a file."""
    issues = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for CJK characters
    cjk_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')
    cjk_matches = cjk_pattern.findall(content)
    if cjk_matches:
        issues.append(f"CJK characters found: {cjk_matches[:5]}")
    
    # Check for TODO comments
    todo_pattern = re.compile(r'%\s*TODO', re.IGNORECASE)
    todo_matches = todo_pattern.findall(content)
    if todo_matches:
        issues.append(f"TODO comments found: {len(todo_matches)}")
    
    # Check for \cite commands
    cite_pattern = re.compile(r'\\cite\{([^}]+)\}')
    cite_matches = cite_pattern.findall(content)
    
    # Check for \ref commands
    ref_pattern = re.compile(r'\\ref\{([^}]+)\}')
    ref_matches = ref_pattern.findall(content)
    
    # Check for \label commands
    label_pattern = re.compile(r'\\label\{([^}]+)\}')
    label_matches = label_pattern.findall(content)
    
    return {
        'file': os.path.basename(file_path),
        'size': len(content),
        'lines': content.count('\n') + 1,
        'cjk_issues': len(cjk_matches),
        'todo_count': len(todo_matches),
        'citations': cite_matches,
        'references': ref_matches,
        'labels': label_matches,
        'issues': issues
    }

def main():
    """Main function to test all chapter files."""
    base_path = Path(r'C:\Users\marce\Documents\OpenCode_Ecosystem\dissertacao-opencode\capitulos')
    
    chapter_files = [
        '01_introducao.tex',
        '02_aspectos_estrategicos.tex',
        '03_organizacao_trabalho.tex',
        '04_projecao_estudo.tex',
        '05_conclusao.tex',
        '06_referencias.tex'
    ]
    
    print("=" * 60)
    print("LaTeX Structure Validation Report")
    print("=" * 60)
    
    total_citations = 0
    total_references = 0
    total_labels = 0
    all_issues = []
    
    for chapter_file in chapter_files:
        file_path = base_path / chapter_file
        if file_path.exists():
            result = check_latex_structure(file_path)
            print(f"\nFile: {result['file']}:")
            print(f"   Size: {result['size']} bytes, {result['lines']} lines")
            print(f"   Citations: {len(result['citations'])}")
            print(f"   References: {len(result['references'])}")
            print(f"   Labels: {len(result['labels'])}")
            
            if result['citations']:
                print(f"   Cite commands: {', '.join(result['citations'][:3])}{'...' if len(result['citations']) > 3 else ''}")
            
            if result['references']:
                print(f"   Ref commands: {', '.join(result['references'][:3])}{'...' if len(result['references']) > 3 else ''}")
            
            if result['issues']:
                print(f"   Issues: {result['issues']}")
                all_issues.extend(result['issues'])
            
            total_citations += len(result['citations'])
            total_references += len(result['references'])
            total_labels += len(result['labels'])
        else:
            print(f"\nFile not found: {chapter_file}")
    
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"   Total chapters: {len(chapter_files)}")
    print(f"   Total citations: {total_citations}")
    print(f"   Total references: {total_references}")
    print(f"   Total labels: {total_labels}")
    print(f"   Total issues: {len(all_issues)}")
    print("=" * 60)
    
    if all_issues:
        print("\nIssues found:")
        for issue in all_issues:
            print(f"   - {issue}")
    else:
        print("\nNo issues found!")

if __name__ == '__main__':
    main()
