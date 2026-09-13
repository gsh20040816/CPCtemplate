#!/usr/bin/env python3
"""Check every external PDF jump against target named destinations and page labels."""
import json
import re
from pathlib import Path
from pypdf import PdfReader
root=Path(__file__).resolve().parents[1]
reader=PdfReader(root/'output/pdf/infra.pdf')
rows=json.loads((root/'docs/infra-links.json').read_text())
observed=[]
for page in reader.pages:
    for item in page.get('/Annots',[]):
        annotation=item.get_object()
        action=annotation.get('/A')
        if action: action=action.get_object()
        if not action or action.get('/S')!='/GoToR':continue
        file=action.get('/F')
        if isinstance(file,dict):file=file.get('/F')
        observed.append((str(file),str(action.get('/D'))))
checked=[]
for row in rows:
    aux=(root/('build/pdf/volume-'+row['volume']+'.aux')).read_text()
    match=re.search(r'\\newlabel\{compact-'+re.escape(row['symbol'])+r'\}\{\{[^}]*\}\{(\d+)\}\{.*?\}\{([^}]+)\}',aux)
    assert match,row
    number,dest=int(match[1]),match[2]
    assert (row['file'],dest) in observed,(row,observed)
    target=PdfReader(root/'output/pdf'/row['file'])
    assert dest in target.named_destinations,(row,dest)
    physical=target.get_destination_page_number(target.named_destinations[dest])
    assert target.page_labels[physical]==str(number),(row,number,physical)
    checked.append(dict(**row,printed_page=number,physical_page=physical+1,destination=dest))
(root/'verification/infra-links.json').write_text(json.dumps(checked,ensure_ascii=False,indent=2)+'\n')
print('Infra:',len(checked),'external PDF jumps resolve to named destinations and correct printed page labels')
