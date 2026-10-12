#include "../../src/compact/ntt_convolution.hpp"
int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    using N = NttConvolution<998244353>;
    N::Poly a(n), b(m);
    for (auto *p : {&a, &b})
    {
        for (auto &x : *p)
        {
            long long value;
            cin >> value;
            x = value;
        }
    }
    reverse(b.begin(), b.end());
    auto c = N::multiply(a, b);
    if (!c.empty())
        c.erase(c.begin(), c.begin() + m - 1);
    cout << c.size() << '\n';
    for (auto x : c)
        cout << x.v << ' ';
    cout << '\n';
}
