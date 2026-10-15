#!/usr/bin/env python3
"""Split bound copies at chapter boundaries without duplicating body/dependencies.

Each half gets a new cover and the original full table of contents. Printed
numbers remain unchanged; links to the other half become sibling-file links.
The complete category PDFs remain the canonical targets for Infra references.
"""
import hashlib
import json
import subprocess
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject, NameObject, TextStringObject

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf'
BUILD = ROOT / 'build/pdf'
# Named chapter destinations survive pagination changes; never cut a listing.
SPLITS = [('mathematics', '数学', 'chapter.5', '组合数学'),
          ('graphs', '图论', 'chapter.9', '2-SAT')]


def cover(key, title, half):
    stem = f'print-{key}-{half}'
    tex = BUILD / (stem + '.tex')
    tex.write_text(r'''\input{preamble.tex}
\begin{document}
\hypersetup{pageanchor=false}
\begin{titlepage}\centering\vspace*{35mm}
{\Huge\bfseries ''' + title + ('（上册）' if half == 'upper' else '（下册）') + r'''\par}\vspace{15mm}
{\LARGE Morning Flower and Evening Oath\par}
\vfill
\end{titlepage}
\end{document}
''')
    with (BUILD / (stem + '-build.log')).open('w') as log:
        subprocess.run(['latexmk', '-xelatex', '-interaction=nonstopmode',
                        '-halt-on-error', f'-outdir={BUILD}', str(tex)],
                       cwd=ROOT / 'docs', stdout=log, stderr=subprocess.STDOUT, check=True)
    warnings = [line for line in (BUILD / (stem + '.log')).read_text().splitlines()
                if any(word in line for word in ('Warning', 'Overfull', 'Underfull', 'Missing character'))]
    assert not warnings, (stem, warnings)
    result = PdfReader(BUILD / (stem + '.pdf'))
    assert len(result.pages) == 1
    return result


def make_half(reader, key, title, half, selected, other_file):
    writer = PdfWriter()
    writer.add_page(cover(key, title, half).pages[0])
    mapping = {source: target for target, source in enumerate(selected, 1)}
    for source in selected:
        writer.add_page(reader.pages[source], excluded_keys=['/Annots'])
    writer.set_page_label(0, 0, prefix='封面')
    labels = reader.page_labels
    for source, target in mapping.items():
        writer.set_page_label(target, target, prefix=labels[source])

    destinations = reader.named_destinations
    for name, dest in destinations.items():
        source = reader.get_destination_page_number(dest)
        if source in mapping:
            array = ArrayObject([writer.pages[mapping[source]].indirect_reference,
                                 *dest.dest_array[1:]])
            writer.add_named_destination_array(TextStringObject(name), array)

    # Copy annotations explicitly: do not let page cloning pull in unselected pages.
    for source, target in mapping.items():
        annotations = ArrayObject()
        for ref in reader.pages[source].get('/Annots', []):
            original = ref.get_object()
            annotation = DictionaryObject({k: v.clone(writer) for k, v in original.items()
                                           if k not in ('/P', '/A')})
            if '/A' in original:
                action = original['/A'].get_object()
                if action.get('/S') == '/GoTo':
                    name = str(action['/D'])
                    assert name in destinations, name
                    local = reader.get_destination_page_number(destinations[name]) in mapping
                    action = DictionaryObject({NameObject('/S'): NameObject('/GoTo' if local else '/GoToR'),
                                               NameObject('/D'): TextStringObject(name)})
                    if not local:
                        action[NameObject('/F')] = TextStringObject(other_file)
                annotation[NameObject('/A')] = action.clone(writer)
            annotations.append(writer._add_object(annotation))
        if annotations:
            writer.pages[target][NameObject('/Annots')] = annotations

    def outlines(items, parent=None):
        last_parent = parent
        for item in items:
            if isinstance(item, list):
                outlines(item, last_parent)
            else:
                page = reader.get_destination_page_number(item)
                last_parent = writer.add_outline_item(item.title, mapping[page], parent=parent) if page in mapping else parent
    outlines(reader.outline)
    writer.add_metadata({'/Title': title + ('（上册）' if half == 'upper' else '（下册）')})
    path = OUT / f'xcpc-{key}-{half}.pdf'
    writer.write(path)
    return path, mapping


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    reports = []
    for key, title, chapter, chapter_title in SPLITS:
        source = OUT / f'xcpc-{key}.pdf'
        reader = PdfReader(source)
        dest = reader.named_destinations
        assert chapter_title in str(dest[chapter].title) or any(
            chapter_title in line and '{' + chapter + '}' in line
            for line in (BUILD / f'volume-{key}.toc').read_text().splitlines())
        start = reader.get_destination_page_number(dest['page.1'])
        cut = reader.get_destination_page_number(dest[chapter])
        assert start < cut < len(reader.pages)
        front = list(range(1, start))
        upper_body, lower_body = list(range(start, cut)), list(range(cut, len(reader.pages)))
        assert upper_body + lower_body == list(range(start, len(reader.pages)))
        halves = []
        for half, body, other in [('upper', upper_body, 'lower'), ('lower', lower_body, 'upper')]:
            path, mapping = make_half(reader, key, title, half, front + body, f'xcpc-{key}-{other}.pdf')
            halves.append((path, mapping, body))
        outputs = {p.name: PdfReader(p) for p, _, _ in halves}
        output_destinations = {name: pdf.named_destinations for name, pdf in outputs.items()}
        output_labels = {name: pdf.page_labels for name, pdf in outputs.items()}
        source_labels = reader.page_labels
        for path, mapping, body in halves:
            output = outputs[path.name]
            assert len(output.pages) == 1 + len(mapping)
            for source_page, target in mapping.items():
                assert output.pages[target].get_contents().get_data() == reader.pages[source_page].get_contents().get_data()
                assert output_labels[path.name][target] == source_labels[source_page]
            remote = 0
            for page in output.pages:
                for ref in page.get('/Annots', []):
                    action = ref.get_object().get('/A')
                    if not action:
                        continue
                    action = action.get_object()
                    if action.get('/S') == '/GoTo':
                        assert str(action['/D']) in output_destinations[path.name]
                    elif action.get('/S') == '/GoToR':
                        sibling = outputs[str(action['/F'])]
                        name = str(action['/D'])
                        sibling_destinations = output_destinations[str(action['/F'])]
                        assert name in sibling_destinations
                        expected = reader.get_destination_page_number(dest[name])
                        actual = sibling.get_destination_page_number(sibling_destinations[name])
                        assert output_labels[str(action['/F'])][actual] == source_labels[expected]
                        remote += 1
            reports.append(dict(file=str(path.relative_to(ROOT)), pages=len(output.pages),
                                source=str(source.relative_to(ROOT)), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                body_first_page=reader.page_labels[body[0]], body_last_page=reader.page_labels[body[-1]],
                                source_body_physical_pages=[body[0] + 1, body[-1] + 1],
                                shared_toc_pages=len(front), sibling_links=remote,
                                body_streams_unchanged=True, duplicated_body_pages=0))
            print(f'{path.name}: {len(output.pages)} pages, original pages {reader.page_labels[body[0]]}-{reader.page_labels[body[-1]]}')
    (ROOT / 'verification/print-split-volumes.json').write_text(json.dumps(reports, ensure_ascii=False, indent=2) + '\n')
    print('PASS: chapter boundaries, exact body partition, unchanged content/page labels, local and sibling links')


if __name__ == '__main__':
    main()
