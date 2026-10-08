#include "../src/compact/plane3.hpp"
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

namespace original
{
#include "fixtures/real_space_sources/kuangbin.cpp"
}

using G = RealSpace;
using P = G::Point;
using R = G::R;

void need(bool ok)
{
    if (!ok) throw runtime_error("real-space check failed");
}

bool near(R a, R b, R eps = 2e-10L)
{
    return isfinite(a) && isfinite(b) && abs(a - b) <= eps * max({R(1), abs(a), abs(b)});
}

bool near(P a, P b, R eps = 2e-10L)
{
    return near(a.x, b.x, eps) && near(a.y, b.y, eps) && near(a.z, b.z, eps);
}

original::Point3 old(P a)
{
    return {(double)a.x, (double)a.y, (double)a.z};
}

P fresh(original::Point3 a)
{
    return {a.x, a.y, a.z};
}

int main()
{
    R pi = acos(R(-1));
    // Disclosed defects of the unmodified source, not accepted new behavior.
    original::Line3 raw({0, 0, 0}, {2, 0, 0});
    need(!raw.pointonseg({1, 0, 0}));
    original::Plane fx(1, 0, 0, -1), fy(0, 1, 0, -2);
    original::Line3 bad;
    need(fx.crossplane(fy, bad) == 1 && !near(bad.s.y, R(2)));
    original::Plane nx(2, 0, 0, 0), ny(0, 2, 0, 0);
    need(near(nx.angleplane(ny), pi / 8));
    need(!isfinite(nx.angleplane(nx)));
    original::Point3 a(0, 0, 0), b(0.75e-8, -1, 0), c(1.5e-8, -2, 0);
    need(c < b && b < a && !(c < a));
    original::Line3 zero({0, 0, 0}, {0, 0, 0});
    need(!isfinite(zero.dispointtoline({1, 0, 0})));

    vector<P> order{{0, 0, 0}, {0.75e-8L, -1, 0}, {1.5e-8L, -2, 0}};
    need(order[0] < order[1] && order[1] < order[2] && order[0] < order[2]);
    mt19937 rng(7302026);
    auto point = [&]() -> P
    {
        return {R(int(rng() % 21) - 10), R(int(rng() % 21) - 10), R(int(rng() % 21) - 10)};
    };
    int count = 0;
    for (int i = 0; i < 5000; i++)
    {
        P a = point(), b = point(), q = point();
        P d = b - a;
        if (G::norm(d) == 0) continue;
        count++;
        auto l = Line3::through(a, b);
        original::Line3 source(old(a), old(b));
        need(near(l.projection(q), fresh(source.lineprog(old(q)))));
        need(near(l.distance(q), source.dispointtoline(old(q))));
        need(near(l.segment_distance(q), source.dispointtoseg(old(q))));
        R rad = R(int(rng() % 601) - 300) / 100;
        need(near(l.rotate(q, rad), fresh(source.rotate(old(q), double(rad)))));
        need(near(l.rotate(l.rotate(q, rad), -rad), q));
        need(near(l.projection(l.rotate(q, rad)), l.projection(q)));
        need(near(l.distance(l.rotate(q, rad)), l.distance(q)));
        need(l.on_segment(a) && l.on_segment(b) && l.on_segment((a + b) / 2));
        need(!l.on_segment(a - d));
        P n = G::cross(d, q - a);
        if (G::norm(n) == 0) continue;
        auto f = Plane3::through(a, b, q);
        auto same = Plane3(a, n * -7);
        need(near(G::norm(f.n), 1));
        need(near(f.signed_distance(b), 0));
        need(near(f.signed_distance(q), 0));
        Line3 unused({91, 92, 93}, {94, 95, 96});
        need(f.intersect(same, unused) == -1);
        need(unused.p.x == 91 && unused.d.z == 96);
        P r = point(), hit{91, 92, 93};
        auto foot = f.projection(r);
        need(near(f.signed_distance(foot), 0));
        need(near(G::cross(r - foot, f.n), P{}));
        original::Plane sf(old(a), old(b), old(q));
        need(near(foot, fresh(sf.pointtoplane(old(r)))));
        need(f.intersect(l, hit) == -1 && hit.x == 91);
        need(f.intersect(Line3(r, f.n), hit) == 1 && near(hit, foot));
        original::Point3 sh;
        need(sf.crossline(original::Line3(old(r), old(r + f.n)), sh) == 1);
        need(near(hit, fresh(sh)));
        need(near(same.signed_distance(r), -f.signed_distance(r)));
    }
    for (R scale : {1e-100L, 1e-20L, R(1), 1e20L, 1e100L})
    {
        Plane3 f = Plane3::equation({scale, 0, 0}, 3 * scale);
        P q;
        need(f.intersect(Line3({0, 2, 4}, {scale, 0, 0}), q) == 1);
        need(near(q, P{3, 2, 4}));
        need(near(G::angle({scale, 0, 0}, {-scale, 0, 0}), pi));
        need(near(G::angle({scale, 0, 0}, {0, scale, 0}), pi / 2));
    }
    auto f = Plane3::equation({1, 0, 0}, 0);
    P q{91, 92, 93};
    need(f.intersect(Line3({0, 1, 2}, {}), q) == 1 && near(q, P{0, 1, 2}));
    need(f.intersect(Line3({1, 1, 2}, {}), q) == 0 && q.x == 0);
    need(near(Line3({1, 2, 3}, {}).projection({8, 9, 10}), P{1, 2, 3}));
    need(near(Line3({1, 2, 3}, {}).segment_distance({1, 2, 5}), 2));
    need(f.intersect(Line3({1, 0, 0}, {1e-13L, 1, 0}), q) == 0);
    need(f.intersect(Line3({0, 0, 0}, {1e-13L, 1, 0}), q) == -1);
    need(f.intersect(Line3({1, 0, 0}, {1e-9L, 1, 0}), q) == 1);
    need(near(q.x, 0) && near(q.y, -1e9L));
    need(f.intersect(Line3({1, 0, 0}, {1e-13L, 1, 0}), q, 0, 0) == 1);
    need(near(q.y, -1e13L));
    Line3 line;
    need(f.intersect(Plane3::equation({1, 1e-13L, 0}, 1), line) == 0);
    need(f.intersect(Plane3::equation({1, 1e-13L, 0}, 0), line) == -1);
    need(f.intersect(Plane3::equation({1, 1e-9L, 0}, 1), line) == 1);
    need(near(line.p.x, 0) && near(line.p.y, 1e9L));
    need(near(G::angle({1, 0, 0}, {1, 1e-14L, 0}), 1e-14L, 1e-25L));
    need(Line3({0, 0, 0}, {2, 0, 0}).on_segment({1, 0.5e-10L, 0}));
    need(!Line3({0, 0, 0}, {2, 0, 0}).on_segment({1, 2e-10L, 0}));
    cout << count << " nondegenerate source comparisons; boundary and defect checks PASS\n";
    return 0;
}
