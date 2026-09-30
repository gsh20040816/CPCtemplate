"""Verify named copy-reference destinations in final PDF files, not just TeX."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
from pypdf import PdfReader
root = Path(__file__).resolve().parents[1]
reports = []
for row in json.loads((root / 'verification/pdf-volumes.json').read_text()):
    file = root / row['file']
    stem = file.stem
    name = 'main' if stem == 'xcpc-template' else ('infra' if stem == 'infra' else stem.replace('xcpc-', 'volume-'))
    source = (root / ('docs/' + name + '.tex')).read_text()
    if name == 'main':
        source += (root / 'docs/generated.tex').read_text()
    labels = {}
    aux = (root / ('build/pdf/' + name + '.aux')).read_text()
    for label, number, page, dest in re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{([^}]*)\}\{.*?\}\{([^}]+)\}\{\}\}', aux):
        labels[label] = dict(section=number, printed_page=page, destination=dest)
    refs = Counter(re.findall(r'\\hyperref\[(compact-[^\]]+)\]', source))
    reader = PdfReader(file)
    links = Counter()
    source_pages = {}
    for index, page in enumerate(reader.pages):
        for annotation in page.get('/Annots', []):
            obj = annotation.get_object()
            action = obj.get('/A', {})
            if action.get('/S') == '/GoTo':
                dest = str(action['/D'])
                links[dest] += 1
                source_pages.setdefault(dest, set()).add(index+1)
    checks = []
    for label, count in sorted(refs.items()):
        assert label in labels, (name, label)
        info = labels[label]
        dest = info['destination']
        assert dest in reader.named_destinations, (name, label, dest)
        actual = reader.get_destination_page_number(reader.named_destinations[dest])+1
        expected = int(info['printed_page']) + row['offset']
        assert actual == expected, (name,label,actual,expected)
        # Each dependency is printed as name, page and section, all linked.
        assert links[dest] >= 3*count, (name,label,links[dest],count)
        checks.append(dict(label=label,section=info['section'],printed_page=int(info['printed_page']),physical_page=actual,reference_groups=count,pdf_links=links[dest],source_physical_pages=sorted(source_pages[dest])))
    reports.append(dict(file=row['file'],sha256=hashlib.sha256(file.read_bytes()).hexdigest(),dependency_reference_groups=sum(refs.values()),checks=checks))
(root / 'verification/dependency-pdf-links.json').write_text(json.dumps(reports,indent=2)+'\n')
print('Final PDF dependency links:',sum(r['dependency_reference_groups'] for r in reports),'name/page/section groups resolve to actual local destinations')
