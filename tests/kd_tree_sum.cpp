#include "../src/compact/kd_tree_sum.hpp"
#include <cassert>
#include <climits>
#include <iostream>
#include <map>
#include <random>
using ll = long long;
using Point = array<ll, 2>;

ll brute(const map<Point, ll> &a, ll x1, ll y1, ll x2, ll y2)
{
    ll sum = 0;
    for (auto [p, v] : a)
        if (x1 <= p[0] && p[0] <= x2 && y1 <= p[1] && p[1] <= y2) sum += v;
    return sum;
}

vector<Point> audit(KDTreeSum<ll> &s, int p, int axis, const map<Point, ll> &values)
{
    if (!p) return {};
    auto left = audit(s, s.a[p].child[0], axis ^ 1, values);
    auto right = audit(s, s.a[p].child[1], axis ^ 1, values);
    auto before = [&](Point x, Point y)
    {
        return x[axis] < y[axis] || (x[axis] == y[axis] && x[axis ^ 1] < y[axis ^ 1]);
    };
    for (auto x : left) assert(before(x, s.a[p].point));
    for (auto x : right) assert(before(s.a[p].point, x));
    assert(4LL * max(left.size(), right.size()) <= 3LL * s.a[p].size);
    left.insert(left.end(), right.begin(), right.end());
    left.push_back(s.a[p].point);
    assert(left.size() == size_t(s.a[p].size));
    ll sum = 0;
    Point lo = left[0], hi = lo;
    for (auto x : left)
    {
        sum += values.at(x);
        for (int d = 0; d < 2; d++)
        {
            lo[d] = min(lo[d], x[d]);
            hi[d] = max(hi[d], x[d]);
        }
    }
    assert(s.a[p].value == values.at(s.a[p].point));
    assert(s.a[p].sum == sum && s.a[p].low == lo && s.a[p].high == hi);
    return left;
}

int main()
{
    mt19937_64 rng(4148129);
    for (int test = 0; test < 200; test++)
    {
        KDTreeSum<ll> s;
        map<Point, ll> values;
        assert(s.query(LLONG_MIN, LLONG_MIN, LLONG_MAX, LLONG_MAX) == 0);
        for (int i = 0; i < 800; i++)
        {
            Point p = {ll(rng() % 61) - 30, ll(rng() % 61) - 30};
            ll delta = ll(rng() % 101) - 50;
            s.add(p[0], p[1], delta);
            values[p] += delta;
            ll x1 = ll(rng() % 71) - 35, x2 = ll(rng() % 71) - 35;
            ll y1 = ll(rng() % 71) - 35, y2 = ll(rng() % 71) - 35;
            if (i % 5)
            {
                if (x1 > x2) swap(x1, x2);
                if (y1 > y2) swap(y1, y2);
            }
            assert(s.query(x1, y1, x2, y2) == brute(values, x1, y1, x2, y2));
            assert(s.query(p[0], p[1], p[0], p[1]) == values[p]);
            if (i % 100 == 0) audit(s, s.root, 0, values);
        }
        audit(s, s.root, 0, values);
        assert(s.a.size() == values.size() + 1);
    }
    KDTreeSum<ll> edge;
    map<Point, ll> values;
    for (ll x : {LLONG_MIN, -1LL, 0LL, LLONG_MAX})
        for (ll y : {LLONG_MIN, -1LL, 0LL, LLONG_MAX})
        {
            edge.add(x, y, 1000000000000LL);
            values[{x, y}] = 1000000000000LL;
        }
    for (auto [p, v] : values)
        for (auto [q, w] : values)
            assert(edge.query(p[0], p[1], q[0], q[1]) ==
                   brute(values, p[0], p[1], q[0], q[1]));
    audit(edge, edge.root, 0, values);
    KDTreeSum<> grid(200000);
    for (int x = 0; x < 400; x++)
        for (int y = 0; y < 500; y++) grid.add(x, y, 1);
    assert(grid.a.size() == 200001 && grid.a.capacity() == 200001);
    assert(sizeof(KDTreeSum<>::Node) == 56);
    assert(grid.query(INT_MIN, INT_MIN, INT_MAX, INT_MAX) == 200000);
    for (int x = 0; x < 400; x++) assert(grid.query(x, 0, x, 499) == 500);
    for (int y = 0; y < 500; y++) assert(grid.query(0, y, 399, y) == 400);
    for (int i = 0; i < 200000; i++) grid.add(-1, -1, i % 2 ? -1 : 1);
    assert(grid.query(-1, -1, -1, -1) == 0);
    assert(grid.a.size() == 200002);
    cout << "KDTreeSum: 160000 map-oracle updates, invariant audits, signed64 "
            "extremes, 200000 grid, duplicates PASS\n";
}
