from pathlib import Path
import re
root = Path(__file__).resolve().parents[1]
# Issue 27: definitions -> layer conditions -> layer code/usage -> Knuth conditions -> Knuth code/usage.
labels = ['knowledge-quadrangle-definitions', 'knowledge-quadrangle-layer', 'compact-monotone_dp_layer', 'usage-example-363',
          'knowledge-quadrangle-knuth', 'compact-knuth_interval_dp', 'usage-example-461']
for f in ['docs/generated.tex', 'docs/volume-misc.tex']:
    s = (root / f).read_text()
    at = [s.index('\\label{' + x + '}') for x in labels]
    assert at == sorted(at), f
    assert s.count('{四边形不等式优化}') == 1, f
    assert not re.search(r'\\(?:chapter|section)\{', s[at[0]:at[-1]]), f
print('Quadrangle topic: definitions, layer and Knuth conditions each before their code and usage PASS')
