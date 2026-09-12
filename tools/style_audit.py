#!/usr/bin/env python3
from pathlib import Path
import re,json,hashlib,subprocess,argparse
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--base',default='873990f')
args=parser.parse_args()
files=sorted(list((root/'src/compact').glob('*.hpp'))+list((root/'verify').rglob('*.compact.cpp')))
# Preserve strings/chars; ignore whitespace and comments. Longest-match C++ punctuation.
pat=re.compile(r'''\s+|//[^\n]*|/\*[\s\S]*?\*/|(?:u8|u|U|L)?"(?:\\[\s\S]|[^"\\])*"|(?:u8|u|U|L)?'(?:\\[\s\S]|[^'\\])*'|[A-Za-z_]\w*|(?:\d[\w.']*)|(?:<=>|>>=|<<=|->\*|\.\.\.|::|->|\.\*|\+\+|--|<<|>>|<=|>=|==|!=|&&|\|\||\+=|-=|\*=|/=|%=|&=|\^=|\|=|##)|[^\s]''')
def tokens(s):
 assert not re.search(r'\b(?:u8|u|U|L)?R"',s), 'Raw string requires explicit lexer support'
 return [x for x in pat.findall(s) if not x.isspace() and not x.startswith(('//','/*'))]
rows=[]
for p in files:
 old=subprocess.check_output(['git','show',args.base+':'+str(p.relative_to(root))],cwd=root,text=True)
 new=p.read_text()
 assert tokens(old)==tokens(new),str(p)
 rows.append(dict(path=str(p.relative_to(root)),before_sha256=hashlib.sha256(old.encode()).hexdigest(),after_sha256=hashlib.sha256(new.encode()).hexdigest(),before_lines=len(old.splitlines()),after_lines=len(new.splitlines()),tokens_equal=True))
result=dict(issue='https://github.com/gsh20040816/CPCtemplate/issues/2',baseline_commit=args.base,method='C++ lexical comparison preserving literals, dropping comments/whitespace; raw strings rejected. No algorithm or public names changed in this pass.',files=rows)
(root/'verification/issue2-format-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('Token-equal:',len(rows),'files; lines:',sum(r['before_lines'] for r in rows),'->',sum(r['after_lines'] for r in rows))
