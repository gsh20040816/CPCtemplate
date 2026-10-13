#include <bits/stdc++.h>
using namespace std;

static long long ek(int n, const vector<tuple<int, int, int>> &edges, int s, int t)
{
    struct E { int to, rev, cap; };
    vector<E> e;
    vector<vector<int>> g(n + 1);
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

int main(int argc, char **argv)
{
    string mode = argc > 1 ? argv[1] : "flow";
    if (mode == "flow") {
        vector<tuple<int, vector<tuple<int, int, int>>, int, int>> graphs = {
            {2, {{1, 2, 5}}, 1, 2},
            {2, {}, 1, 2},
            {4, {{1, 2, 10}, {1, 3, 10}, {2, 3, 1}, {2, 4, 10}, {3, 4, 10}}, 1, 4},
        };
        mt19937 rng(7);
        for (int n = 2; n <= 5; n++) {
            vector<tuple<int, int, int>> edges;
            for (int i = 0; i < 7; i++) edges.push_back({int(rng() % n) + 1, int(rng() % n) + 1, int(rng() % 9)});
            graphs.push_back({n, edges, 1, n});
        }
        for (auto [n, edges, s, t] : graphs) {
            Flow g(n);
            for (auto [u, v, c] : edges) g.add(u, v, c);
            long long got = g.work(s, t);
            g.reset();
            long long again = g.work(s, t);
            if (got != ek(n, edges, s, t) || again != got) return 1;
        }
        cout << "flow\n";
        return 0;
    }
    if (mode == "cut") {
        int n = 2, m = 1;
        vector<int> profit = {0, 10, 1};
        int S = n + m + 1, T = n + m + 2;
        Flow flow(T);
        for (int i = 1; i <= n; i++) flow.add(S, i, profit[i]);
        int x = 1, y = 2, w = 3, sum = w;
        flow.add(x, n + 1, (int)1E18);
        flow.add(y, n + 1, (int)1E18);
        flow.add(n + 1, T, w);
        int printed = sum - (int)flow.work(S, T);
        int best = 0;
        for (int mask = 0; mask < (1 << n); mask++) {
            int got = 0;
            bool used = false;
            for (int i = 1; i <= n; i++) if (mask & (1 << (i - 1))) {
                got += profit[i];
                if (i == x || i == y) used = true;
            }
            if (used) got -= w;
            best = max(best, got);
        }
        cout << printed << ' ' << best << ' ' << (int)1E18 << '\n';
        return 0;
    }
    MinCostFlow g(4);
    g.add(0, 1, 2, 1);
    g.add(0, 2, 1, 2);
    g.add(1, 3, 1, 3);
    g.add(2, 3, 2, 1);
    auto [flow, cost] = g.flow(0, 3);
    MinCostFlow neg(2);
    neg.add(0, 1, 1, -5);
    auto [nf, nc] = neg.flow(0, 1);
    cout << flow << ' ' << cost << ' ' << nf << ' ' << nc << '\n';
}
