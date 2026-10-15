"""Issue 28: every template prints its problem/function and core idea before the contract and code."""
from pathlib import Path
import json
import re
root = Path(__file__).resolve().parents[1]
catalog = [r[1] for r in json.loads((root / 'docs/catalog.json').read_text())]
intros = json.loads((root / 'docs/template-intros.json').read_text())
assert list(intros) == catalog, 'template-intros.json must follow catalog order and cover every template'
volume_ids = [v['id'] for v in json.loads((root / 'docs/volumes.json').read_text())]
volumes = [root / 'docs/generated.tex'] + [root / f'docs/volume-{v}.tex' for v in volume_ids]
checked = 0
for path in volumes:
    text = path.read_text()
    for symbol in catalog:
        m = re.search(r'\\label\{compact-' + re.escape(symbol) + r'\}', text)
        if not m:
            continue
        nxt = re.search(r'\\(?:chapter|section|subsection)\{', text[m.end():])
        body = text[m.end():m.end() + (nxt.start() if nxt else len(text))]
        label = '问题描述' if intros[symbol]['kind'] == 'problem' else '功能'
        first = body.index('\\textbf{' + label + '：}')
        idea = body.index('\\textbf{核心思路：}')
        contract = body.index('\\textbf{接口契约：}')
        code = body.index('\\lstinputlisting')
        assert first < idea < contract, (path.name, symbol)
        assert idea < code, (path.name, symbol)
        if symbol != 'Mo':  # Mo keeps its long contract after the scheduler code.
            assert contract < code, (path.name, symbol)
        checked += 1
assert checked >= 2 * len(catalog), checked
print(f'Template intros: {len(catalog)} templates, {checked} printed sections with problem/idea before code PASS')
