#include "../../src/compact/bivariate_inverse.hpp"
int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, h, w;
    cin >> n >> m >> h >> w;
    BivariateInverse::Matrix a(h, vector<BivariateInverse::Z>(w));
    for (auto &row : a)
        for (auto &x : row)
        {
            long long value;
            cin >> value;
            x = value;
        }
    if (a.empty() || a[0].empty() || a[0][0].v == 0)
    {
        cout << -1 << '\n';
        return 0;
    }
    auto b = BivariateInverse::inverse(a, n, m);
    for (const auto &row : b)
    {
        for (auto x : row)
            cout << x.v << ' ';
        cout << '\n';
    }
}
