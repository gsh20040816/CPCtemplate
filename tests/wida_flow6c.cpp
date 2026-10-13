#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_flow6c/main.cpp"
#include "../src/compact/flow.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int cases;
    cin >> cases;
    while (cases--)
    {
        int n, m, s, t, pre;
        cin >> n >> m >> s >> t >> pre;
        MaxFlow<long long> g(n);
        vector<tuple<int, int, long long>> edges(m);
        for (auto &[u, v, c] : edges)
            cin >> u >> v >> c;
        int before = 0;
        if (pre)
        {
            auto cut = g.minCut();
            before = 1;
            for (bool x : cut)
                before &= x;
        }
        for (auto [u, v, c] : edges)
            g.addEdge(u, v, c);
        long long got = g.flow(s, t);
        auto cut = g.minCut();
        long long library = -1;
        if (s != t)
        {
            Dinic d(n);
            for (auto [u, v, c] : edges)
                if (u != v)
                    d.add(u + 1, v + 1, c);
            library = d.flow(s + 1, t + 1);
        }
        cout << got << ' ' << library << ' ' << before;
        for (bool x : cut)
            cout << ' ' << x;
        auto restored = g.edges();
        cout << ' ' << restored.size();
        for (auto e : restored)
            cout << ' ' << e.from << ' ' << e.to << ' ' << e.cap << ' ' << e.flow;
        cout << '\n';
    }
}
