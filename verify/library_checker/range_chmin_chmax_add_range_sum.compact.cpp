// https://judge.yosupo.jp/problem/range_chmin_chmax_add_range_sum
#include "../../src/compact/segment_beats.hpp"
#include <iostream>

// BEGIN USAGE
int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<long long> a(n);
    for (auto &x : a) cin >> x;
    SegmentBeats t(a);
    while (q--)
    {
        int type, l, r;
        cin >> type >> l >> r;
        if (type == 3)
        {
            cout << t.sum(l, r) << '\n';
            continue;
        }
        long long x;
        cin >> x;
        if (type == 0) t.chmin(l, r, x);
        else if (type == 1) t.chmax(l, r, x);
        else t.add(l, r, x);
    }
}
// END USAGE
