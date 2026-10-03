#include "../../src/compact/mod64.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int q;
    if (!(cin >> q) || q < 0 || q > 200000) return 1;
    while (q--)
    {
        unsigned long long a, b, m;
        if (!(cin >> a >> b >> m) || !m) return 1;
        cout << Mod64::mul(a, b, m) << ' ' << Mod64::power(a, b, m) << '\n';
    }
}
