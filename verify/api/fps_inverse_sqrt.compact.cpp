#include "../../src/compact/fps_sqrt.hpp"
int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int tests;
    cin >> tests;
    while (tests--)
    {
        int n;
        cin >> n;
        FpsSqrt::Poly a(n);
        for (auto &x : a)
        {
            long long value;
            cin >> value;
            x = value;
        }
        auto root = FpsSqrt::sqrt(a, n);
        if (!root || (*root)[0].v == 0)
        {
            cout << -1 << '\n';
            continue;
        }
        auto inverse = FpsInverse::inverse(*root, n);
        for (int i = 0; i < n; i++)
            cout << inverse[i].v << " \n"[i + 1 == n];
    }
}
