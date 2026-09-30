"""Compare narrowly scoped historical inverse bodies; never claim whole-source AC."""
from pathlib import Path
import hashlib
import json
import re
import sys
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from usage_examples import records

def tokens(s):
    parts = re.findall(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[A-Za-z_]\w*|\d+|\S', s, re.S)
    return [p for p in parts if not p.startswith(('//', '/*'))]

rows = {r['id']:r for r in records()}
reports = []
for ident, pid, symbol in [('example-196','P3811','inverse_table'), ('example-197','P5431','batch_inverse')]:
    row = rows[ident]
    archive = root / ('verification/submitted/' + pid + '.compact.cpp')
    old = archive.read_text()
    core = (root / ('src/compact/' + symbol + '.hpp')).read_text()
    def section(s):
        return s.split('// BEGIN ' + symbol + '\n')[1].split('// END ' + symbol)[0]
    a, b = tokens(section(old)), tokens(section(core))
    assert a[0] == 'inline'
    a = a[1:]
    remap = False
    if symbol == 'batch_inverse':
        # Historical member calls changed when the general number-theory namespace split.
        at = next(i for i in range(len(a)-3) if a[i:i+4] == ['NumberTheory', ':', ':', 'inverse'])
        a[at:at+4] = ['mod_inverse']
        remap = True
    assert a == b, 'Core differs beyond documented inline/adapter mapping'
    main_old = old[old.index('int main()'):]
    main_new = row['program'][row['program'].index('int main()'):]
    assert tokens(main_old) == tokens(main_new)
    helper_match = None
    if row.get('utility_functions'):
        helper_old = old[old.index('int read()'):old.index('int main()')]
        helper_new = row['program'][row['program'].index('int read()'):row['program'].index('int main()')]
        helper_match = tokens(helper_old) == tokens(helper_new)
        assert helper_match
    reports.append(dict(usage=ident,archive=str(archive.relative_to(root)),archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),current_program_sha256=row['program_sha256'],whole_program_byte_match=old == row['program'],main_token_match=True,reader_token_match=helper_match,core_tokens_match_after_removing_inline=True,dependency_call_remapped=remap,scope='Only named algorithm body, reader and main; headers/dependencies differ. This is not current exact-source online AC, dependency equivalence proof or a speed ranking.'))
(root / 'verification/inverse-archive-scope.json').write_text(json.dumps(reports,indent=2)+'\n')
print('P3811/P5431 scoped historical core, reader and main comparisons PASS; whole-program mismatch retained')
