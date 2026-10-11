#include "../../src/compact/hlpp.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, s, t;
    cin >> n >> m >> s >> t;
    HLPP g(n);
    vector<int> ids;
    for (int i = 0; i < m; i++)
    {
        int u, v;
        long long cap;
        cin >> u >> v >> cap;
        ids.push_back(g.add(u, v, cap));
    }
    cout << g.flow(s, t) << '\n';
    for (int id : ids) cout << g.used(id) << '\n';
    auto cut = g.min_cut();
    for (int u = 1; u <= n; u++) cout << cut[u];
    cout << '\n';
}
