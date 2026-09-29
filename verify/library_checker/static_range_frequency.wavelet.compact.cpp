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
        int l, r;
        long long x;
        cin >> l >> r >> x;
        cout << wm.freq(l, r, x) << '\n';
    }
}
