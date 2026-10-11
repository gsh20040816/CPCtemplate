#include "../src/compact/steiner_tree.hpp"

void check(const SteinerTree &s, vector<int> terminals)
{
    long long want = terminals.empty() ? 0 : SteinerTree::inf;
    for (int mask = 0; mask < (1 << s.edges.size()); mask++)
    {
        vector<int> p(s.n);
        iota(p.begin(), p.end(), 0);
        auto find = [&](auto &&self, int u) -> int
        {
            return p[u] == u ? u : p[u] = self(self, p[u]);
        };
        long long cost = 0;
        for (int id = 0; id < (int)s.edges.size(); id++)
        {
            if (!(mask >> id & 1)) continue;
            auto e = s.edges[id];
            p[find(find, e.u)] = find(find, e.v);
            cost += e.w;
        }
        bool ok = true;
        for (int v : terminals)
            if (find(find, v) != find(find, terminals[0])) ok = false;
        if (ok) want = min(want, cost);
    }
    if (want == SteinerTree::inf) want = -1;
    auto result = s.solve(terminals);
    if (result.cost != want) abort();
    vector<int> p(s.n);
    iota(p.begin(), p.end(), 0);
    auto find = [&](auto &&self, int u) -> int
    {
        return p[u] == u ? u : p[u] = self(self, p[u]);
    };
    vector<bool> used(s.edges.size());
    long long sum = 0;
    for (int id : result.edges)
    {
        if (id < 0 || id >= (int)s.edges.size() || used[id]) abort();
        used[id] = true;
        auto e = s.edges[id];
        sum += e.w;
        p[find(find, e.u)] = find(find, e.v);
    }
    if (want == -1)
    {
        if (!result.edges.empty()) abort();
        return;
    }
    if (sum != want) abort();
    for (int v : terminals)
        if (find(find, v) != find(find, terminals[0])) abort();
}

int main()
{
    mt19937 rng(6192);
    int cases = 0;
    for (int n = 1; n <= 4; n++)
    {
        vector<pair<int, int>> pairs;
        for (int u = 0; u < n; u++)
            for (int v = u + 1; v < n; v++) pairs.push_back({u, v});
        for (int mask = 0; mask < (1 << pairs.size()); mask++)
        {
            SteinerTree s(n);
            for (int i = 0; i < (int)pairs.size(); i++)
                if (mask >> i & 1) s.add(pairs[i].first, pairs[i].second, i % 3);
            for (int t = 0; t < (1 << n); t++)
            {
                vector<int> terminals;
                for (int v = 0; v < n; v++)
                    if (t >> v & 1) terminals.push_back(v);
                check(s, terminals);
                cases++;
            }
        }
    }
    for (int test = 0; test < 1000; test++)
    {
        int n = 1 + rng() % 8;
        SteinerTree s(n);
        int m = rng() % 13;
        for (int i = 0; i < m; i++)
            s.add(rng() % n, rng() % n, rng() % 9);
        vector<int> terminals;
        int k = rng() % 9;
        for (int i = 0; i < k; i++) terminals.push_back(rng() % n);
        check(s, terminals);
        cases++;
    }
    SteinerTree large_weight(3);
    large_weight.add(0, 1, SteinerTree::inf / 3);
    large_weight.add(1, 2, SteinerTree::inf / 3);
    check(large_weight, {0, 2, 0});
    cout << cases + 1 << " independent edge-subset and witness cases PASS\n";
}
