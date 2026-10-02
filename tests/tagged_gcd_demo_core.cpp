#include "../src/compact/gcd_sequence.hpp"
#include <iostream>
#include <limits>
using namespace std;

int main()
{
    using U = GcdSequenceTreap::U;
    const U hi = numeric_limits<U>::max();
    GcdSequenceTreap tr;
    int builds = 0, rounds = 0, queries = 0;
    auto build = [&](const vector<pair<U, int>> &v) { tr.build(v); ++builds; };
    auto check = [&](int l, int r, int t, optional<U> want)
    {
        assert(tr.query(l, r, t) == want);
        ++queries;
    };
    build({{0, 0}, {hi, 1}, {6, 0}});
    tr.erase(2, 2);
    assert(tr.recycled.size() == 1);
    build({{hi, 1}}); // Replace a nonempty sequence with pending recycled slots.
    assert(tr.size() == 1 && tr.a.size() == 2 && tr.recycled.empty());
    check(1, 1, 0, nullopt);
    check(1, 1, 1, hi);
    build({});
    assert(tr.size() == 0 && tr.root == 0 && tr.a.size() == 1 && tr.recycled.empty());
    tr.insert(0, 0, 0);
    check(1, 1, 0, U(0));
    build({{12, 0}, {18, 1}});
    check(1, 2, 0, U(12));
    check(1, 2, 1, U(18));
    const int n = 257;
    build(vector<pair<U, int>>(n, {0, 0}));
    const auto slots = tr.a.size(), capacity = tr.a.capacity();
    for (int round = 0; round < 128; ++round)
    {
        tr.erase(1, n);
        assert(tr.size() == 0 && tr.recycled.size() == n);
        for (int i = 0; i < n; ++i) tr.insert(i, round % 2 ? hi : 0, round % 2);
        assert(tr.a.size() == slots && tr.a.capacity() == capacity && tr.recycled.empty());
        check(1, n, round % 2, round % 2 ? hi : U(0));
        check(1, n, (round % 2) ^ 1, nullopt);
        tr.erase(2, n - 1);
        for (int i = 0; i < n - 2; ++i) tr.insert(1, 6, 0);
        assert(tr.a.size() == slots && tr.a.capacity() == capacity);
        check(2, n - 1, 0, U(6));
        check(2, n - 1, 1, nullopt);
        ++rounds;
    }
    // Exact selected protocol envelope, followed by extra API-only checks.
    build(vector<pair<U, int>>(200000, {0, 0}));
    for (int i = 0; i < 100000; ++i) tr.insert(tr.size(), hi, 1);
    assert(tr.size() == 300000 && tr.a.size() == 300001);
    check(1, 300000, 0, U(0));
    check(1, 300000, 1, hi);
    check(200000, 200001, 0, U(0));
    check(200000, 200001, 1, hi);
    check(300000, 300000, 0, nullopt);
    check(300000, 300000, 1, hi);
    tr.erase(1, 300000);
    assert(tr.recycled.size() == 300000);
    build({});
    assert(tr.a.size() == 1 && tr.recycled.empty() && tr.size() == 0);
    cout << "PASS builds=" << builds << " recycling_rounds=" << rounds << " queries=" << queries << '\n';
}
