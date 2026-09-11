#!/usr/bin/env python3
"""Expand local includes once, retaining system includes; exact submitted source is reproducible."""
import argparse,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);a=p.parse_args();seen=set()
def expand(p):
 p=p.resolve()
 if p in seen:return ''
 seen.add(p);out=[]
 for s in p.read_text().splitlines():
  m=re.fullmatch(r'\s*#include "([^"]+)"\s*',s)
  if m:out.append(expand(p.parent/m[1]))
  elif s.strip()!='#pragma once':out.append(s)
 return '\n'.join(out)+'\n'
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(expand(a.input))
