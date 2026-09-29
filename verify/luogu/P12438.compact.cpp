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
    cout << s.water() << '\n';
    while (q--)
    {
        int l, r;
        cin >> l >> r;
        s.add(l - 1, r, 1);
        cout << s.water() << '\n';
    }
}
