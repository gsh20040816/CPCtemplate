#include "../../src/compact/static_rmq.hpp"
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<long long> a(n);
    for (auto &x : a) cin >> x;
    StaticRMQ<long long> mn(a);
    StaticRMQ<long long, greater<long long>> mx(a);
    while (q--)
    {
        int l, r;
        cin >> l >> r;
        cout << mn.query(l, r) << ' ' << mx.query(l, r) << '\n';
    }
}
