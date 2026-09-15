#include "../../src/compact/dag_path_determinant.hpp"

int main()
{
    using Z = ModInt<998244353>;
    int n, m, k;
    cin >> n >> m >> k;
    vector<vector<pair<int, Z>>> g(n);
    for (int i = 0; i < m; i++)
    {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        g[u].push_back({v, Z(w)});
    }
    vector<int> sources(k), sinks(k);
    for (int &u : sources) cin >> u;
    for (int &u : sinks) cin >> u;
    auto ans = dag_path_determinant<998244353>(g, sources, sinks);
    if (!ans)
        cout << "CYCLE\n";
    else
        cout << ans->v << '\n';
}
