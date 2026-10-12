#include "../../src/compact/montgomery_modint.hpp"
int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    using Z = Montgomery<998244353>;
    int q;
    cin >> q;
    while (q--)
    {
        long long a, b;
        uint64_t k;
        cin >> a >> b >> k;
        Z x(a), y(b);
        auto inv = y.try_inv();
        cout << (x + y).get() << ' ' << (x - y).get() << ' ';
        cout << (x * y).get() << ' ' << x.pow(k).get() << ' ';
        cout << (inv ? (long long)inv->get() : -1) << '\n';
    }
}
