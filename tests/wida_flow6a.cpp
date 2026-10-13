#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_flow6a/main.cpp"
#include "../src/compact/flow.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int cases;
    cin >> cases;
    while (cases--)
    {
        int n, m, s, t, kind;
        cin >> n >> m >> s >> t >> kind;
        vector<tuple<int, int, long long>> edges(m);
        for (auto &[u, v, c] : edges)
            cin >> u >> v >> c;
        long long original, library;
        if (kind == 0)
        {
            Flow<int> g(n);
            for (auto [u, v, c] : edges)
                g.addEdge(u, v, (int)c);
            original = g.maxFlow(s, t);
        }
        else
        {
            Flow<long long> g(n);
            for (auto [u, v, c] : edges)
                g.addEdge(u, v, c);
            original = g.maxFlow(s, t);
        }
        if (s == t)
            library = -1;
        else
        {
            Dinic g(n);
            for (auto [u, v, c] : edges)
                if (u != v)
                    g.add(u + 1, v + 1, c);
            library = g.flow(s + 1, t + 1);
        }
        cout << original << ' ' << library << '\n';
    }
}
