#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_hlpp/main.cpp"

static long long ek(int n, const vector<tuple<int, int, int>> &edges, int s, int t)
{
    vector<vector<int>> g(n + 1);
    struct E { int to, rev, cap; };
    vector<E> e;
    auto add = [&](int u, int v, int c) {
        g[u].push_back((int)e.size());
        e.push_back({v, (int)e.size() + 1, c});
        g[v].push_back((int)e.size());
        e.push_back({u, (int)e.size() - 1, 0});
    };
    for (auto [u, v, c] : edges) add(u, v, c);
    long long flow = 0;
    while (true) {
        vector<int> pre(n + 1, -1);
        queue<int> q;
        q.push(s);
        pre[s] = -2;
        while (!q.empty()) {
            int u = q.front();
            q.pop();
            for (int id : g[u]) if (e[id].cap && pre[e[id].to] == -1) {
                pre[e[id].to] = id;
                q.push(e[id].to);
            }
        }
        if (pre[t] == -1) break;
        int aug = INT_MAX;
        for (int v = t; v != s; v = e[e[pre[v]].rev].to) aug = min(aug, e[pre[v]].cap);
        for (int v = t; v != s; v = e[e[pre[v]].rev].to) {
            e[pre[v]].cap -= aug;
            e[e[pre[v]].rev].cap += aug;
        }
        flow += aug;
    }
    return flow;
}

int main()
{
    vector<tuple<int, vector<tuple<int, int, int>>, int, int>> graphs = {
        {2, {{1, 2, 5}}, 1, 2},
        {2, {}, 1, 2},
        {4, {{1, 2, 10}, {1, 3, 10}, {2, 3, 1}, {2, 4, 10}, {3, 4, 10}}, 1, 4},
        {3, {{1, 2, 3}, {1, 2, 4}, {2, 3, 6}}, 1, 3},
    };
    mt19937 rng(7);
    for (int n = 2; n <= 6; n++) {
        vector<tuple<int, int, int>> edges;
        for (int i = 0; i < 8; i++) edges.push_back({int(rng() % n) + 1, int(rng() % n) + 1, int(rng() % 10)});
        graphs.push_back({n, edges, 1, n});
    }
    for (auto [n, edges, s, t] : graphs) {
        PushRelabel<long long> g(n);
        for (auto [u, v, c] : edges) g.addedge(u, v, c);
        long long got = g.work(s, t);
        long long expect = ek(n, edges, s, t);
        if (got != expect) {
            cout << "bad " << got << ' ' << expect << '\n';
            return 1;
        }
    }
    cout << "ok\n";
}
