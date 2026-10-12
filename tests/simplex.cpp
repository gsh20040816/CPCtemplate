#include "../src/compact/simplex.hpp"

int main()
{
    int cases;
    cin >> cases;
    while (cases--)
    {
        int n, m;
        cin >> n >> m;
        vector<long double> c(n), b(m);
        vector<vector<long double>> a(m, vector<long double>(n));
        for (auto &v : c) cin >> v;
        for (int i = 0; i < m; i++)
        {
            for (auto &v : a[i]) cin >> v;
            cin >> b[i];
        }
        Simplex lp(a, b, c);
        auto r = lp.solve();
        cout << r.status << ' ' << setprecision(20) << r.value;
        for (auto v : r.x) cout << ' ' << v;
        cout << '\n';
    }
}
