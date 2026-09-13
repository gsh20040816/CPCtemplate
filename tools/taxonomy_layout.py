"""Render source-linked fragments in pinned OI Wiki navigation order."""
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
TAX = json.loads((ROOT/'docs/oi-taxonomy.json').read_text())['templates']
LEVELS = ['chapter', 'section', 'subsection', 'subsubsection']

def escape(text):
    chars = {'&': r'\&', '%': r'\%', '_': r'\_', '#': r'\#', '$': r'\$', '{': r'\{', '}': r'\}', '^': r'\textasciicircum{}', '\\': r'\textbackslash{}'}
    return ''.join(chars.get(c, c) for c in text)

def render(entries, omnibus=False):
    result = []
    previous = []
    root = None
    ordered = sorted(enumerate(entries), key=lambda p:(TAX[p[1]['symbol']]['order'],p[0]))
    for _, row in ordered:
        item = TAX[row['symbol']]
        path = item['hierarchy']
        if path[0] != root:
            if omnibus and root == '计算几何':
                result.append(r'\input{geometry-notes.tex}')
            if omnibus:
                result.append(r'\part{'+escape(path[0])+'}')
            previous = []
            root = path[0]
        branch = path[1:]
        assert len(branch) < len(LEVELS), path
        common = 0
        while common < min(len(previous), len(branch)) and previous[common] == branch[common]:
            common += 1
        fragment = re.sub(r'\\section\{', lambda m:'\\'+LEVELS[len(branch)]+'{', row['latex'], count=1)
        # Reserve space before the new taxonomy headings, so a fragment's own
        # Needspace/newpage cannot strand those headings on the preceding page.
        prefix = re.match(r'(?:(?:\\Needspace\{[0-9]+pt\}|\\newpage)\s*)+', fragment)
        if prefix:
            if r'\newpage' in prefix[0]:
                result.append(r'\newpage')
            need = re.search(r'\\Needspace\{([0-9]+)pt\}', prefix[0])
            if need:
                space = min(680, int(need[1]) + 35 * (len(branch)-common))
                result.append(r'\Needspace{'+str(space)+'pt}')
            fragment = fragment[prefix.end():]
        elif common < len(branch):
            result.append(r'\Needspace{180pt}')
        for depth in range(common, len(branch)):
            result.append('\\'+LEVELS[depth]+'{'+escape(branch[depth])+'}')
        if item['relation'] == 'related':
            result.append(r'\noindent 相关应用：'+escape(item['note']))
        result.append(fragment)
        previous = branch
    if omnibus and root == '计算几何':
        result.append(r'\input{geometry-notes.tex}')
    return '\n\n'.join(result)
