#include "../src/compact/support_hull.hpp"
#include "../src/classic/support_hull.hpp"
#include "../src/compact/maximum_closure.hpp"
#include "../src/classic/maximum_closure.hpp"
#include <random>
#include <iostream>
using P = pair<long long, long long>;
using I = __int128_t;

I turn(P a, P b, P c)
{
    return (I(b.first) - a.first) * (I(c.second) - a.second)
         - (I(b.second) - a.second) * (I(c.first) - a.first);
}

vector<P> expected(vector<P> points)
{
    sort(points.begin(), points.end());
    vector<P> h;
    for (P p : points)
    {
        if (!h.empty() && h.back().first == p.first)
            continue;
        while (h.size() >= 2 && turn(h[h.size()-2], h.back(), p) <= 0)
            h.pop_back();
        h.push_back(p);
    }
    return h;
}

template<class Oracle>
void compare(const vector<P> &points, Oracle &&oracle)
{
    auto want = expected(points);
    P a = want.front(), b = want.back();
    auto f = [&](long long x, long long y)
    {
        P p = oracle(x, y);
        return SupportHull::Point{p.first, p.second};
    };
    auto g = [&](long long x, long long y)
    {
        P p = oracle(x, y);
        return Support_Hull::Point{p.first, p.second};
    };
    auto h = SupportHull::build({a.first,a.second}, {b.first,b.second}, f);
    auto k = Support_Hull::Build({a.first,a.second}, {b.first,b.second}, g);
    assert(h.size() == want.size() && k.size() == want.size());
    for (int i = 0; i < int(want.size()); i++)
    {
        assert(P(h[i].x, h[i].y) == want[i]);
        assert(P(k[i].x, k[i].y) == want[i]);
    }
}

void check(vector<P> points)
{
    for (int mode = 0; mode < 3; mode++)
    {
        auto oracle = [&](long long x, long long y)
        {
            I best = -(I(1) << 126);
            vector<P> tied;
            for (P p : points)
            {
                I value = I(x) * p.first + I(y) * p.second;
                if (value > best)
                {
                    best = value;
                    tied.clear();
                }
                if (value == best)
                    tied.push_back(p);
            }
            sort(tied.begin(), tied.end());
            return tied[mode == 0 ? 0 : mode == 1 ? tied.size()-1 : tied.size()/2];
        };
        compare(points, oracle);
    }
}

void closure_check(int n, int m, const vector<pair<int,int>> &edges)
{
    vector<P> points;
    for (int mask = 0; mask < (1 << n); mask++)
    {
        int neighbors = 0;
        for (auto [u,v] : edges)
            if (mask >> (u-1) & 1)
                neighbors |= 1 << (v-n-1);
        points.emplace_back(__builtin_popcount(unsigned(mask)),
                            __builtin_popcount(unsigned(neighbors)));
    }
    for (int style = 0; style < 2; style++)
    {
        auto oracle = [&](long long a, long long b)
        {
            assert(a >= 0 && b < 0);
            vector<long long> w(n, a);
            w.resize(n+m, b);
            static Network_Flow<20, 120> graph;
            auto result = style ? Maximum_Closure(w,edges,graph)
                                : maximum_closure(w,edges);
            P p{0,0};
            for (int u : result.second)
            {
                if (u <= n)
                    p.first++;
                else
                    p.second++;
            }
            assert(I(a)*p.first + I(b)*p.second == result.first);
            return p;
        };
        compare(points, oracle);
    }
}

int main()
{
    for (int mask = 1; mask < 512; mask++)
    {
        vector<P> p;
        for (int i = 0; i < 9; i++)
            if (mask >> i & 1)
                p.emplace_back(i/3-1,i%3-1);
        check(p);
    }
    mt19937 rng(712367);
    for (int trial = 0; trial < 3000; trial++)
    {
        vector<P> p;
        for (int i = 0, n = 1 + rng()%80; i < n; i++)
            p.emplace_back(int(rng()%31)-15,int(rng()%31)-15);
        check(p);
    }
    const long long B = 1000000000000000000LL;
    check({{-B,B},{0,-B},{B,B},{-B,-B},{B,-B},{0,0}});
    check({{-B,B},{0,-B},{B,B}});
    vector<P> parabola;
    for (int x = -200; x <= 200; x++)
        parabola.emplace_back(x, x*x);
    check(parabola);
    for (int mask = 0; mask < 512; mask++)
    {
        vector<pair<int,int>> edges;
        for (int i = 0; i < 9; i++)
            if (mask >> i & 1)
                edges.emplace_back(i/3+1,i%3+4);
        closure_check(3,3,edges);
    }
    for (int trial = 0; trial < 500; trial++)
    {
        int n = 1 + rng()%7, m = 1 + rng()%7;
        vector<pair<int,int>> edges;
        for (int u = 1; u <= n; u++)
            for (int v = 1; v <= m; v++)
                if (rng()%3 == 0)
                    edges.emplace_back(u,n+v);
        closure_check(n,m,edges);
    }
    cout << "Support hull dual exact cloud oracle, ties, int64 bounds and maximum closure composition PASS\n";
}
