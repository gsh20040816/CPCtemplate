"""Independent finite-language minimization; do not conflate it with endpos classes."""
import json
from pathlib import Path

def compare(words):
    nodes=[{}]
    final=[False]
    for word in words:
        for start in range(len(word)+1):
            p=0
            for c in word[start:]:
                if c not in nodes[p]:
                    nodes[p][c]=len(nodes)
                    nodes.append({})
                    final.append(False)
                p=nodes[p][c]
            final[p]=True
    classes={}
    state=[0]*len(nodes)
    for p in range(len(nodes)-1,-1,-1):
        key=(final[p],tuple(sorted((c,state[q]) for c,q in nodes[p].items())))
        if key not in classes: classes[key]=len(classes)
        state[p]=classes[key]
    ends={}
    for i,s in enumerate(words):
        for l in range(len(s)):
            for r in range(l,len(s)):
                ends.setdefault(s[l:r+1],set()).add((i,r))
    return dict(words=words,distinct=len(ends),endpos_states=1+len({frozenset(v) for v in ends.values()}),minimal_partial_suffix_dfa_states=len(classes))
rows=[compare(['ab','b']),compare(['ab']),compare(['a','a'])]
assert rows[0]['endpos_states']==4 and rows[0]['minimal_partial_suffix_dfa_states']==3
assert rows[1]['endpos_states']==rows[1]['minimal_partial_suffix_dfa_states']==3
assert rows[2]['endpos_states']==rows[2]['minimal_partial_suffix_dfa_states']==2
report=dict(scope='Independent exact suffix-language trie minimization vs document-position endpos equivalence. A rejecting sink is omitted, as in partial automata. No claim about the online P6139 checker.',cases=rows)
root=Path(__file__).resolve().parents[1]
(root/'verification/general-sam-semantics.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Suffix-language minimal DFA and endpos-state distinction reproduced PASS')
