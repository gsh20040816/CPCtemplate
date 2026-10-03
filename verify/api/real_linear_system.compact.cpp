#include "../../src/compact/gauss_real.hpp"
#include <iomanip>
#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int m, n;
    long double eps;
    cin >> m >> n >> eps;
    GaussReal::Matrix a(m, vector<long double>(n + 1));
    for (auto &row : a)
        for (auto &x : row) cin >> x;
    auto r = GaussReal::solve(a, n, eps);
    cout << r.consistent << ' ' << r.rank << '\n';
    if (!r.consistent) return 0;
    cout << setprecision(20);
    for (auto x : r.particular) cout << x << ' ';
    cout << '\n' << r.kernel.size() << '\n';
    for (const auto &v : r.kernel)
    {
        for (auto x : v) cout << x << ' ';
        cout << '\n';
    }
}
