#include "../../src/compact/kruskal_tree.hpp"
#include "../../src/compact/graph.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t;
    cin >> t;
    while (t--)
    {
        int n, m;
        cin >> n >> m;
        KruskalTree tr(n);
        Dijkstra g(n);
        for (int i = 0; i < m; i++)
        {
            int u, v;
            long long l, a;
            cin >> u >> v >> l >> a;
            g.add(u, v, l);
            g.add(v, u, l);
            tr.add(u - 1, v - 1, a);
        }
        g.run(1);
        tr.build(true);
        vector<long long> best(tr.ch.size());
        for (int u = 0; u < n; u++) best[u] = g.dis[u + 1];
        for (int u = n; u < (int)tr.ch.size(); u++)
        {
            auto [l, r] = tr.ch[u];
            best[u] = min(best[l], best[r]);
        }
        int q, k;
        long long s, last = 0;
        cin >> q >> k >> s;
        while (q--)
        {
            long long v, p;
            cin >> v >> p;
            v = (v + k * last - 1) % n;
            p = (p + k * last) % (s + 1);
            last = best[tr.component(v, p, true)];
            cout << last << '\n';
        }
    }
}
