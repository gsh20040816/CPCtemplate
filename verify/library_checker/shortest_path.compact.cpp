#include "../../src/compact/pbds_heap.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, s, t;
    cin >> n >> m >> s >> t;
    vector<vector<pair<int, int>>> g(n);
    for (int i = 0; i < m; i++)
    {
        int u, v, w;
        cin >> u >> v >> w;
        g[u].push_back({v, w});
    }
    using P = pair<long long, int>;
    pheap<P, greater<P>> q;
    vector<decltype(q)::point_iterator> h(n);
    const long long inf = LLONG_MAX;
    vector<long long> d(n, inf);
    vector<int> pre(n, -1);
    vector<bool> in(n);
    d[s] = 0;
    h[s] = q.push({0, s});
    in[s] = true;
    while (!q.empty())
    {
        auto [du, u] = q.top();
        q.pop();
        in[u] = false;
        for (auto [v, w] : g[u])
        {
            if (du + w >= d[v]) continue;
            d[v] = du + w;
            pre[v] = u;
            if (in[v])
                q.modify(h[v], {d[v], v});
            else
            {
                h[v] = q.push({d[v], v});
                in[v] = true;
            }
        }
    }
    if (d[t] == inf)
    {
        cout << -1 << '\n';
        return 0;
    }
    vector<pair<int, int>> path;
    for (int v = t; v != s; v = pre[v]) path.push_back({pre[v], v});
    reverse(path.begin(), path.end());
    cout << d[t] << ' ' << path.size() << '\n';
    for (auto [u, v] : path) cout << u << ' ' << v << '\n';
}
