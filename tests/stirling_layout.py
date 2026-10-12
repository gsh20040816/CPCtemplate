from pathlib import Path
import re
labels=['knowledge-stirling-definitions','compact-stirling_first_row','usage-example-54','compact-stirling_first_column','usage-example-433','compact-stirling_second_row','usage-example-53','compact-stirling_second_column','usage-example-434','knowledge-stirling-inversion']
for f in ['docs/generated.tex','docs/volume-mathematics.tex']:
 s=Path(f).read_text();at=[s.index('\\label{'+x+'}') for x in labels]
 assert at==sorted(at),f
 assert s.count('{斯特林数与斯特林反演}')==1,f
 span=s[at[0]:at[-1]]
 assert not re.search(r'\\(?:chapter|section)\{',span),f
for f in ['docs/mathematics.tex','docs/mathematics-legacy.tex']:
 assert 'section{斯特林数的快速整行计算}' not in Path(f).read_text()
print('Stirling topic: definitions, four algorithms with adjacent usages, inversion; no duplicate legacy section PASS')
