#include <bits/stdc++.h>
#include "../../src/compact/monotone_stack_seg.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<long long> a(n);
    for (auto &x : a) cin >> x;
    MonotoneStackSeg s(a);
    while (q--)
    {
        int op, l, r;
        long long x;
        cin >> op >> l >> r >> x;
        if (op == 0)
            s.add(l, r, x);
        else
        {
            auto [cost, height] = s.scan(l, r, x, op == 2);
            cout << cost << ' ' << height << '\n';
        }
    }
}
