#include <bits/stdc++.h>
#include "../../src/compact/wavelet_matrix.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<long long> a(n);
    for (auto &x : a) cin >> x;
    WaveletMatrix wm(a);
    while (q--)
    {
        int l, r, k;
        cin >> l >> r >> k;
        cout << wm.kth(l, r, k) << '\n';
    }
}
