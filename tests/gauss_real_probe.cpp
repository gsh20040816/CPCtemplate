#include "../src/compact/gauss_real.hpp"
#include <iomanip>
#include <iostream>
#include <limits>
#include <string>

int main(int argc, char **argv)
{
    if (argc > 1)
    {
        string mode = argv[1];
        if (mode == "bad-eps") GaussReal::solve({}, 0, 0);
        if (mode == "bad-n") GaussReal::solve({}, INT_MAX, 0.01L);
        if (mode == "bad-shape") GaussReal::solve({{1}}, 1, 0.01L);
        if (mode == "nan")
            GaussReal::solve({{numeric_limits<long double>::quiet_NaN(), 1}},
                             1, 0.01L);
        return 0;
    }
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    cout << setprecision(numeric_limits<long double>::max_digits10);
    int cases;
    cin >> cases;
    while (cases--)
    {
        int m, n;
        long double eps;
        cin >> m >> n >> eps;
        GaussReal::Matrix a(m, vector<long double>(n + 1));
        for (auto &v : a)
            for (auto &x : v) cin >> x;
        auto old = a;
        auto r = GaussReal::solve(a, n, eps);
        assert(a == old);
        cout << r.consistent << ' ' << r.rank << ' ' << r.particular.size()
             << ' ' << r.kernel.size() << '\n';
        for (auto x : r.particular) cout << x << ' ';
        cout << '\n';
        for (const auto &v : r.kernel)
        {
            assert((int)v.size() == n);
            for (auto x : v) cout << x << ' ';
            cout << '\n';
        }
    }
}
