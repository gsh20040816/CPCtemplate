"""AOJ F/G full drivers against an 80-digit angular oracle (mpmath).
CPC_SANITIZE=1 selects ASan/UBSan. No online verdict is inferred.
"""
from compiler_config import CXX
from pathlib import Path
import hashlib
from functools import cmp_to_key
import json
import os
import random
import subprocess
import mpmath as mp

mp.mp.dps = 80
root = Path(__file__).resolve().parents[1]
mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
flags = ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
executables = {}
for letter in 'FG':
    executables[letter] = root / f'build/tangent-{letter}-{mode}'
    subprocess.run([CXX,'-std=c++20',*flags,str(root/f'verify/aoj/CGL_7_{letter}.compact.cpp'),'-o',str(executables[letter])],check=True)
counts = dict.fromkeys('FG',0)
worst = dict.fromkeys('FG',mp.mpf(0))

def ordered(points):
    # A tolerance appears only in this high-precision independent oracle.
    # Exact distinct x values differ by >1e-40 on the tested integer domain,
    # while the 80-digit construction error is far below 1e-50.
    def compare(a, b):
        i = 1 if abs(a[0]-b[0]) < mp.mpf('1e-50') else 0
        return int(a[i]>b[i])-int(a[i]<b[i])
    return sorted(points,key=cmp_to_key(compare))

def validate(output, points):
    lines = output.splitlines()
    assert len(lines) == len(points)
    error = mp.mpf(0)
    for line,expected in zip(lines,points):
        actual = list(map(mp.mpf,line.split()))
        assert len(actual)==2 and all(mp.isfinite(v) for v in actual)
        error=max(error,*(abs(x-y) for x,y in zip(actual,expected)))
    assert error < mp.mpf('1e-5'),(output,points,error)
    return error

def run(letter,data,points):
    result=subprocess.run([str(executables[letter])],input=data,text=True,capture_output=True,check=True,timeout=30)
    assert not result.stderr,result.stderr
    worst[letter]=max(worst[letter],validate(result.stdout,ordered(points)))
    counts[letter]+=1

def point_case(p,o,r):
    x,y=p[0]-o[0],p[1]-o[1]
    q=x*x+y*y
    assert q>r*r
    angle=mp.atan2(y,x)
    delta=mp.acos(r/mp.sqrt(q))
    points=[(o[0]+r*mp.cos(angle+sign*delta),o[1]+r*mp.sin(angle+sign*delta)) for sign in [-1,1]]
    run('F',f'{p[0]} {p[1]}\n{o[0]} {o[1]} {r}\n',points)

def circles(a,r,b,s):
    x,y=b[0]-a[0],b[1]-a[1]
    q=x*x+y*y
    assert q!=0 or r!=s
    points=[]
    if q:
        angle=mp.atan2(y,x)
        for side in [-1,1]:
            g=r-side*s
            if q<g*g:
                continue
            delta=mp.acos(g/mp.sqrt(q))
            for sign in [-1,1]:
                points.append((a[0]+r*mp.cos(angle+sign*delta),a[1]+r*mp.sin(angle+sign*delta)))
                if q==g*g:
                    break
    run('G',f'{a[0]} {a[1]} {r}\n{b[0]} {b[1]} {s}\n',points)

for p,o,r in [((0,0),(2,2),2),((-3,0),(2,2),2),((1000,1),(0,0),1000),
              ((-1000,-1000),(1000,1000),1),((1000,0),(0,0),999),((0,1000),(0,0),999)]:
    point_case(p,o,r)
for a,r,b,s in [((1,1),1,(6,2),2),((1,2),1,(4,2),2),((1,2),1,(3,2),2),
                 ((0,0),1,(1,0),2),((0,0),1,(0,0),2),((0,0),3,(5,5),4),
                 ((-1000,-1000),1000,(1000,1000),1000),
                 ((0,0),500,(999,1),499),((0,0),1000,(1,1),999)]:
    circles(a,r,b,s)
for scale in [1,2,3,10,100,200]:
    for xsign in [-1,1]:
        for ysign in [-1,1]:
            a,b=(0,0),(5*scale*xsign,5*scale*ysign)
            circles(a,3*scale,b,4*scale)
            circles(b,4*scale,a,3*scale)
# Small exhaustive integer center offsets and positive radii cover all 0..4
# common-tangent counts, including exact inner/outer tangencies.
for x in range(-3,4):
    for y in range(-3,4):
        for r in range(1,4):
            for s in range(1,4):
                if x or y or r!=s:
                    circles((0,0),r,(x,y),s)
rng=random.Random(29701)
coord=lambda:rng.randrange(-1000,1001)
for _ in range(500):
    a,b=(coord(),coord()),(coord(),coord())
    r,s=rng.randrange(1,1001),rng.randrange(1,1001)
    if a!=b or r!=s:
        circles(a,r,b,s)
    p=(coord(),coord())
    if (p[0]-a[0])**2+(p[1]-a[1])**2>r*r:
        point_case(p,a,r)
negative=[('1.8 2.4\n1.8 -2.4\n',[(mp.mpf('1.8'),mp.mpf('-2.4')),(mp.mpf('1.8'),mp.mpf('2.4'))]),
          ('nan 0\n',[(0,0)]),('inf 0\n',[(0,0)]),('0 0\n',[]),
          ('1.00002 0\n',[(1,0)]),('',[(0,0)])]
for output,points in negative:
    try:
        validate(output,points)
    except (AssertionError,ValueError):
        pass
    else:
        raise AssertionError('Invalid output accepted')
paths=[Path(__file__).resolve(),*[root/f'verify/aoj/CGL_7_{letter}.compact.cpp' for letter in 'FG'],
       *[root/f'src/compact/{name}.hpp' for name in ['circle_tangents','integer_tangents','integer_plane','real_plane']]]
proof=dict(mode=mode,cases=counts,maximum_absolute_errors={k:str(v) for k,v in worst.items()},negative_controls=len(negative),
           oracle='80-digit angular coordinates; exact integer count and algebraic separation for reference tie handling',
           sha256={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},scope='Local complete AOJ F/G drivers, no online AC')
(root/f'verification/tangent-applications-{mode}.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof,indent=2))
