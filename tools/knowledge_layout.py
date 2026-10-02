"""Place explicitly mapped knowledge sections in the pinned navigation."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def classified_fragments():
    mapping = json.loads((ROOT / 'docs/knowledge-taxonomy.json').read_text())
    navigation = json.loads((ROOT / 'docs/oi-taxonomy.json').read_text())
    assert mapping['reference_commit'] == navigation['reference_commit']
    assert mapping['reference_source_sha256'] == navigation['source_sha256']
    assert len(mapping['entries']) == len({entry['label'] for entry in mapping['entries']})
    nav = {item['path']: item for item in navigation['navigation']}
    fragments = {}
    for source in dict.fromkeys(entry['source'] for entry in mapping['entries']):
        content = (ROOT / source).read_text()
        for section in re.split(r'(?=\\section\{)', content)[1:]:
            labels = re.findall(r'\\label\{(knowledge-[^}]+)\}', section)
            assert len(labels) == 1, (source, labels)
            assert labels[0] not in fragments, labels[0]
            fragments[labels[0]] = (source, section)
    assert set(fragments) == {entry['label'] for entry in mapping['entries']}
    rows = []
    for entry in mapping['entries']:
        source, fragment = fragments[entry['label']]
        assert source == entry['source']
        page_break = entry.get('page_break_before', False)
        assert isinstance(page_break, bool), (entry['label'], 'invalid page break')
        if page_break:
            fragment = '\\newpage\n' + fragment
        item = dict(nav[entry['path']], relation='direct', note=entry['note'])
        rows.append(dict(symbol=entry['label'], latex=fragment, code='',
                         taxonomy=item, knowledge=True))
    return rows


def legacy_knowledge():
    """Keep unmapped legacy text explicit, without duplicating mapped sources."""
    text = (ROOT / 'docs/mathematics.tex').read_text()
    mapping = json.loads((ROOT / 'docs/knowledge-taxonomy.json').read_text())
    for source in dict.fromkeys(entry['source'] for entry in mapping['entries']):
        directive = r'\input{' + Path(source).name + '}'
        assert text.count(directive) == 1, source
        text = text.replace(directive, '')
    return text
