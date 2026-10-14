#!/usr/bin/env python3
"""Render the full knowledge notes (derivations, counterexamples, verification scope) as Markdown.

Issue 21: the printed sections keep formulas, conditions and complexity only; the full text
stays in docs/knowledge-full/*.tex and is published here for reading.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def braced(text, start):
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if not depth:
                return i
    return len(text) - 1


def command(text, name, render):
    out, i = [], 0
    while True:
        j = text.find('\\' + name + '{', i)
        if j < 0:
            return ''.join(out) + text[i:]
        k = braced(text, j + len(name) + 1)
        args = [text[j + len(name) + 2:k]]
        if name == 'href' and k + 1 < len(text) and text[k + 1] == '{':
            m = braced(text, k + 1)
            args.append(text[k + 2:m])
            k = m
        out.append(text[i:j] + render(*args))
        i = k + 1


def convert(tex):
    s = re.sub(r'(?m)^%.*\n', '', tex)
    s = re.sub(r'第~?\\pageref\{[^}]*\}~?页', '', s)
    s = re.sub(r'\\(?:page)?ref\{[^}]*\}', '', s)
    s = re.sub(r'\\(?:label|index)\{[^}]*\}', '', s)
    s = re.sub(r'\\(?:newpage|noindent|medskip|smallskip|bigskip)\b', '', s)
    s = re.sub(r'\\Needspace\{[^}]*\}', '', s)
    for level, mark in [('subsubsection', '#####'), ('subsection', '####'), ('section', '###'), ('chapter', '###')]:
        s = command(s, level, lambda t, m=mark: m + ' ' + t.strip())
    s = command(s, 'paragraph', lambda t: '**' + t.strip() + '**')
    s = command(s, 'texttt', lambda t: '`' + t.replace('\\_', '_').replace('\\%', '%').replace('\\#', '#') + '`')
    s = command(s, 'textbf', lambda t: '**' + t + '**')
    s = command(s, 'emph', lambda t: '*' + t + '*')
    s = command(s, 'href', lambda u, t: '[' + t + '](' + u + ')')
    s = command(s, 'url', lambda u: '<' + u + '>')
    s = command(s, 'nolinkurl', lambda u: '`' + u + '`')
    s = re.sub(r'\\begin\{(?:itemize|enumerate)\}|\\end\{(?:itemize|enumerate)\}', '', s)
    s = re.sub(r'(?m)^\s*\\item\s*', '- ', s)
    s = s.replace('~', ' ').replace('\\_', '_').replace('\\%', '%').replace('\\&', '&').replace('\\#', '#')
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip() + '\n'


def main():
    parts = ['# 知识节完整说明', '',
             'issue #21 起，PDF 中的知识节只保留公式、适用条件和复杂度。推导、例子、误用反例与本地验证范围保留在 '
             '[docs/knowledge-full](knowledge-full/) 的原始 TeX 中，本文件由 `tools/knowledge_markdown.py` 从中生成。'
             '页码引用在此省略；验证记录仍以 verification/ 下的原始报告为准。', '']
    for path in sorted((ROOT / 'docs/knowledge-full').glob('*.tex')):
        parts.append('## ' + path.stem)
        parts.append('')
        parts.append(convert(path.read_text()))
    (ROOT / 'docs/KNOWLEDGE-DETAILS.md').write_text('\n'.join(parts))
    print('Rendered', len(parts), 'knowledge detail blocks')


if __name__ == '__main__':
    main()
