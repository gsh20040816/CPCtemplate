#include "../../src/compact/maximum_closure.hpp"
#include <sstream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int m, n;
    cin >> m >> n;
    vector<long long> w(m + n);
    vector<pair<int, int>> dep;
    string line;
    getline(cin, line);
    for (int i = 1; i <= m; i++)
    {
        getline(cin, line);
        istringstream in(line);
        in >> w[i - 1];
        int j;
        while (in >> j) dep.push_back({i, m + j});
    }
    for (int j = 0; j < n; j++)
    {
        long long cost;
        cin >> cost;
        w[m + j] = -cost;
    }
    auto [best, selected] = maximum_closure(w, dep);
    for (int u : selected)
        if (u <= m) cout << u << ' ';
    cout << '\n';
    for (int u : selected)
        if (u > m) cout << u - m << ' ';
    cout << '\n' << best << '\n';
}
