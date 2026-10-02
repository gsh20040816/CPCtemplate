#!/usr/bin/env python3
"""Check the exact sole handbook listing against independent binary-string/matrix oracles."""
import hashlib
from itertools import product
import re
from state_recurrence_knowledge import ROOT, expand, nth, options, run_bound, sequence


def prepare_snippet(out):
    tex=ROOT/'docs/knowledge-state-recurrence.tex'
    snippets=re.findall(r'\\begin\{lstlisting\}\n(.*?)\\end\{lstlisting\}',tex.read_text(),re.S)
    assert len(snippets)==1,'Expected exactly one unmodified mathematical usage listing'
    deps=set()
    program=expand('#include "recurrence.hpp"',ROOT/'src/compact',deps)
    program += '#include <iostream>\nint main(){unsigned long long N;while(std::cin>>N){\n'+snippets[0]+'\nstd::cout<<answer<<"\\n";}}\n'
    a=[[1,0,1],[1,1,0],[0,1,0]];v=[1,0,0];u=[1,1,1];p=998244353
    indices=list(range(13))+[21,64,10**18,2**64-1]
    want=[nth(a,v,u,n,p) for n in indices]
    brute=[sum('101' not in ''.join(bits) for bits in product('01',repeat=n)) for n in range(13)]
    assert want[:13]==brute==sequence(a,v,u,13)
    fixture=out/'indices.txt';fixture.write_text('\n'.join(map(str,indices))+'\n')
    evidence=dict(indices=indices,expected=want,binary_strings_enumerated=8191,
                  snippet_sha256=hashlib.sha256(snippets[0].encode()).hexdigest(),
                  extraction='Sole lstlisting copied unchanged; wrapper only supplies unsigned long long N and prints answer')
    return program,fixture,'\n'.join(map(str,want))+'\n',evidence


def main():
    run_bound(options('state-recurrence-snippet'),prepare_snippet)


if __name__=='__main__':
    main()
