#include <bits/stdc++.h>
#include "../../src/compact/set_convolution.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    using C = SetConvolution<>;
    int k;
    cin >> k;
    int n = 1 << k, m = n;
    C::Poly a(n), b(m);
    for (auto &x : a) cin >> x.v;
    for (auto &x : b) cin >> x.v;
    auto c = C::multiply(move(a), move(b), '&');
    for (int i = 0; i < (int)c.size(); i++)
        cout << c[i].v << (i + 1 == (int)c.size() ? '\n' : ' ');
}
