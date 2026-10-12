#include "../../src/compact/ntt_2d.hpp"
int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, h, w;
    cin >> n >> m >> h >> w;
    using F = Ntt2D<>;
    F::Matrix a(n, vector<F::Z>(m)), b(h, vector<F::Z>(w));
    for (auto *matrix : {&a, &b})
        for (auto &row : *matrix)
            for (auto &x : row)
            {
                long long value;
                cin >> value;
                x = value;
            }
    auto c = F::multiply(a, b);
    cout << c.size() << ' ' << (c.empty() ? 0 : c[0].size()) << '\n';
    for (const auto &row : c)
    {
        for (auto x : row)
            cout << x.v << ' ';
        cout << '\n';
    }
}
