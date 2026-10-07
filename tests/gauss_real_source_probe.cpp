#include "../src/compact/gauss_real.hpp"
#include <iomanip>
#include <iostream>

namespace Original
{
#include "fixtures/gauss_real_sources/kuangbin.inc"
}
#undef eps

int main()
{
    cout << setprecision(24);
    int m, n;
    while (cin >> m >> n)
    {
        Original::equ = m;
        Original::var = n;
        fill(begin(Original::x), end(Original::x), 0);
        GaussReal::Matrix b(m, vector<long double>(n + 1));
        for (int i = 0; i < m; i++)
        {
            for (int j = 0; j <= n; j++)
                cin >> b[i][j];
            for (int j = 0; j < n; j++)
                Original::a[i][j] = b[i][j];
            Original::x[i] = b[i][n];
        }
        int status = Original::Gauss();
        cout << status;
        for (int i = 0; i < n; i++)
            cout << ' ' << Original::x[i];
        auto ans = GaussReal::solve(b, n, 1e-12L);
        cout << ' ' << ans.consistent << ' ' << ans.rank << ' ' << ans.kernel.size();
        for (auto v : ans.particular)
            cout << ' ' << v;
        for (auto &v : ans.kernel)
            for (auto x : v)
                cout << ' ' << x;
        cout << '\n';
    }
    return 0;
}
