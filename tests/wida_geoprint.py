"""Audit the plane-primitive snippets from the WIDA geometry printout."""
import hashlib, json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-geo.md').read_bytes()
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '29b9fa7f47c21422e31cce8f3dbb5ee857764150'
text = blob.decode().replace('\r\n', '\n')
fences = []
pos = 0
while True:
    a = text.find('```', pos)
    if a < 0:
        break
    b = text.find('\n', a)
    c = text.find('```', b + 1)
    fences.append(text[b + 1:c])
    pos = c + 3
out = root / 'build/wida-geoprint'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
head = '#include <bits/stdc++.h>\nusing namespace std;\n'
# 0 read, 1 preset, 2 point, 3 cross, 4 dot, 5 dis, 6 manhattan, 7 unit, 8 rot90,
# 9 deg, 10 cosine, 11 angle, 12 rot, 13 rot point, 14 online, 15 left, 16 side,
# 17 intersection, 18 parallel, 19 pointToLine, 20 dis only, 21 segment including ends
parts = fences[1:22]
alias = 'using Pt = Point<ld>; using Lt = Line<ld>; using Pd = Point<ld>; using Ld = Line<ld>;\n'
# The second pointOnSegment has the same signature and calls itself.
segment = fences[22].split('template<class T> bool pointOnSegment', 2)
segment_ok = 'template<class T> bool pointOnSegment' + segment[1]
body = ''.join(parts[:3]) + alias + ''.join(parts[3:]) + segment_ok + r'''
int main() {
    stringstream in("1.25 3");
    cin.rdbuf(in.rdbuf());
    if (read() != 12500 || read() != 30000) return 1;
    if (!equal(fgcd(6.0L, 9.0L), 3.0L) || sign(0.0L) != 0 || sign(-2.0L) != -1) return 1;
    Point<ld> o(0, 0), e(1, 0), n(0, 1), p(3, 4);
    if (!equal(cross(e, n), 1.0L) || !equal(dot(e, n), 0.0L)) return 1;
    if (!equal(dis(o, p), 5.0L) || !equal(dis1(o, p), 7.0L)) return 1;
    auto u = standardize(p);
    if (!equal(u.x, 0.6L) || !equal(u.y, 0.8L)) return 1;
    auto cw = o + rotate(o, e);
    if (!equal(cw.x, 0.0L) || !equal(cw.y, -1.0L)) return 1;
    if (!equal(toDeg(PI), 180.0L)) return 1;
    if (!equal(angle(3.0L, 4.0L, 5.0L), PI / 2)) return 1;
    if (!equal(angle(e, n), PI / 2)) return 1;
    auto ccw = rotate(e, PI / 2);
    if (!equal(ccw.x, 0.0L) || !equal(ccw.y, 1.0L)) return 1;
    auto around = rotate(e, o, PI / 2);
    if (!equal(around.x, 0.0L) || !equal(around.y, -1.0L)) return 1;
    if (!onLine(Point<ld>(2, 0), e, o) || onLine(n, e, o)) return 1;
    if (!pointOnLineLeft<ld>(n, Line<ld>(o, e)) || pointOnLineLeft<ld>(Point<ld>(0, -1), Line<ld>(o, e))) return 1;
    Line<ld> x(o, e), y(o, n);
    auto hit = lineIntersection(x, y);
    if (!equal(hit.x, 0.0L) || !equal(hit.y, 0.0L)) return 1;
    if (!lineParallel<ld>(x, Line<ld>(Point<ld>(0, 1), Point<ld>(1, 1))) || lineParallel<ld>(x, y)) return 1;
    if (!lineVertical<ld>(x, y)) return 1;
    if (!equal(disPointToLine<ld>(n, x), 1.0L)) return 1;
    if (!pointOnSegment<ld>(e, x) || pointOnSegment<ld>(n, x)) return 1;
    cout << "ok\n";
}
'''

def run(name, code, flags):
    path = out / (name + '.cpp')
    path.write_text(head + code)
    exe = out / name
    compiled = subprocess.run([CXX, '-std=c++20', *flags, str(path), '-o', str(exe)], text=True, capture_output=True)
    if compiled.returncode != 0:
        compiled.stdout = ''
        return compiled
    return subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30)

prefix = ''.join(parts[:3]) + alias + ''.join(parts[3:]) + segment_ok
extra = ''.join(fences[i] for i in (23, 24, 28, 29, 30, 33))
area = next(f for f in fences if 'abs(cross(b, c, a))' in f)
more = prefix + extra + area + r'''
int main() {
    Line<ld> x(Point<ld>(0, 0), Point<ld>(1, 0));
    auto foot = project(Point<ld>(0, 1), x);
    if (!equal(foot.x, 0.0L) || !equal(foot.y, 0.0L)) return 1;
    auto near = pointToSegment(Point<ld>(2, 1), x);
    if (!equal(near.first.x, 1.0L) || !equal(near.first.y, 0.0L) || !equal(near.second, sqrt(2.0L))) return 1;
    auto right = getPoint(Point<ld>(0, 0), 1, 0);
    auto up = getPoint(Point<ld>(0, 0), 1, PI / 2);
    if (!equal(right.x, 1.0L) || !equal(up.y, 1.0L)) return 1;
    auto hit = lineCircleCross(x, Point<ld>(0, 0), 1);
    if (get<0>(hit) != 2) return 1;
    if (!equal(area(Point<ld>(0, 0), Point<ld>(4, 0), Point<ld>(0, 3)), 6.0L)) return 1;
    if (!equal(circleIntersectionArea(Point<ld>(0, 0), 1, Point<ld>(0, 0), 1), PI)) return 1;
    if (!equal(circleIntersectionArea(Point<ld>(0, 0), 1, Point<ld>(3, 0), 1), 0.0L)) return 1;
    auto touch = pointToCircle(Point<ld>(2, 0), Point<ld>(0, 0), 1);
    if (!equal(touch.first.x, 1.0L) || !equal(touch.second, 1.0L)) return 1;
    cout << "ok\n";
}
'''
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    got = run('prim-' + mode, body, flags)
    assert got.returncode == 0 and got.stdout == 'ok\n', (got.returncode, got.stdout, got.stderr[-600:])
    nxt = run('more-' + mode, more, flags)
    assert nxt.returncode == 0 and nxt.stdout == 'ok\n', (nxt.returncode, nxt.stdout, nxt.stderr[-700:])
    print(mode, 'PASS')
both = ''.join(parts[:3]) + alias + ''.join(parts[3:]) + fences[22] + 'int main(){return 0;}\n'
assert run('segment', both, ['-O2']).returncode != 0
poly = next(f for f in fences if 'ans += cross(P[i], P[(i + 1) % n])' in f)
grid = next(f for f in fences if 'onPolygonGrid' in f)
quad = next(f for f in fences if 'return cross(b, c, a)' in f)
poly_code = prefix + poly + grid + r'''
int main() {
    vector<Point<ld>> s = {{0, 0}, {1, 0}, {1, 1}, {0, 1}};
    if (!equal(area(s), 1.0L)) return 1;
    vector<Point<int>> g = {{0, 0}, {2, 0}, {2, 2}, {0, 2}};
    if (onPolygonGrid(g) != 8 || inPolygonGrid(g) != 1) return 1;
    cout << "ok\n";
}
'''
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    got = run('poly-' + mode, poly_code, flags)
    assert got.returncode == 0 and got.stdout == 'ok\n', (got.returncode, got.stdout, got.stderr[-400:])
assert run('cross', prefix + fences[26] + 'int main(){return 0;}\n', ['-O2']).returncode != 0
assert run('areaex', prefix + quad + 'int main(){return 0;}\n', ['-O2']).returncode != 0
circle3 = next(f for f in fences if 'getCircle' in f)
assert run('circle3', prefix + circle3 + 'int main(){ getCircle(Point<ld>(), Point<ld>(1,0), Point<ld>(0,1)); }\n', ['-O2']).returncode != 0
print('bounds PASS')
