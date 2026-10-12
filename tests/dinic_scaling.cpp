// The runner supplies unchanged Dinic and the version enabled from its comments.
using ll = long long;
using i128 = __int128_t;
long long checks = 0;

void require(bool ok)
{
    if (!ok)
        throw runtime_error("oracle mismatch");
    checks++;
}

template<class Flow>
ll oracle(const Flow &g, int s, int t)
{
    i128 ans = i128(1) << 120;
    for (int mask = 0; mask < (1 << g.n); mask++)
    {
        if (!(mask >> (s - 1) & 1) || (mask >> (t - 1) & 1))
            continue;
        i128 cap = 0;
        for (int id = 0; id < (int)g.e.size(); id += 2)
        {
            auto a = g.e[id];
            if ((mask >> (a.from - 1) & 1) && !(mask >> (a.to - 1) & 1))
                cap += a.initial;
        }
        ans = min(ans, cap);
    }
    require(ans <= LLONG_MAX);
    return (ll)ans;
}

template<class Flow>
void certificate(Flow &g, int s, int t, ll value, bool full)
{
    vector<i128> balance(g.n + 1);
    for (int id = 0; id < (int)g.e.size(); id += 2)
    {
        auto [u, v, cap, f] = g.get_edge(id);
        require(0 <= f && f <= cap);
        require(g.e[id].cap == cap - f && g.e[id ^ 1].cap == f);
        balance[u] -= f;
        balance[v] += f;
    }
    for (int u = 1; u <= g.n; u++)
        require(balance[u] == (u == s ? -i128(value) : u == t ? i128(value) : 0));
    if (!full)
        return;
    vector<int> side(g.n + 1);
    for (int u : g.cut(s))
        side[u] = 1;
    require(side[s] && !side[t]);
    i128 cap = 0;
    for (int id = 0; id < (int)g.e.size(); id += 2)
        if (side[g.e[id].from] && !side[g.e[id].to])
            cap += g.e[id].initial;
    require(cap == value);
}

template<class Flow>
void exercise(int n, const vector<tuple<int, int, ll>> &edges, mt19937_64 &rng)
{
    Flow g(n);
    for (auto [u, v, cap] : edges)
        g.add(u, v, cap);
    ll best = oracle(g, 1, n);
    ll total = 0;
    for (ll limit : {0LL, best / 3, 1LL, best / 2, LLONG_MAX})
    {
        ll got = g.flow(1, n, limit);
        require(got == min(limit, best - total));
        total += got;
        certificate(g, 1, n, total, total == best);
    }
    require(g.flow(1, n) == 0);
    // Preserve each edge's existing flow while increasing capacities.
    for (int id = 0; id < (int)g.e.size(); id += 2)
        g.change_edge(id, g.e[id].initial + rng() % 11, g.used(id));
    g.add(1, n, 17);
    ll grown = oracle(g, 1, n);
    require(g.flow(1, n) == grown - total);
    certificate(g, 1, n, grown, true);
    // Reset all edges together, including shrinking to zero, before changing s/t.
    for (int id = 0; id < (int)g.e.size(); id += 2)
        g.change_edge(id, rng() % 19, 0);
    ll reversed = oracle(g, n, 1);
    require(g.flow(n, 1) == reversed);
    certificate(g, n, 1, reversed, true);
}

template<class Flow>
void boundaries()
{
    Flow empty(3);
    require(empty.flow(1, 3) == 0);
    empty.add(1, 3, 0);
    require(empty.flow(1, 3) == 0);
    certificate(empty, 1, 3, 0, true);
    Flow big(3);
    big.add(1, 2, LLONG_MAX);
    big.add(2, 3, LLONG_MAX);
    require(big.flow(1, 3, 1) == 1);
    certificate(big, 1, 3, 1, false);
    require(big.flow(1, 3, LLONG_MAX - 2) == LLONG_MAX - 2);
    require(big.flow(1, 3) == 1);
    require(big.flow(1, 3) == 0);
    certificate(big, 1, 3, LLONG_MAX, true);
    // The second path requires cancelling the first path through a reverse edge.
    Flow reroute(6);
    reroute.add(1, 2, 1);
    reroute.add(2, 3, 1);
    reroute.add(3, 6, 1);
    require(reroute.flow(1, 6) == 1);
    reroute.add(1, 4, 1);
    reroute.add(4, 3, 1);
    reroute.add(2, 5, 1);
    reroute.add(5, 6, 1);
    require(reroute.flow(1, 6) == 1);
    certificate(reroute, 1, 6, 2, true);
}

int main()
{
    try
    {
        mt19937_64 rng(20261012);
        for (int it = 0; it < 4000; it++)
        {
            int n = 2 + rng() % 7;
            vector<tuple<int, int, ll>> edges;
            int m = rng() % 65;
            for (int j = 0; j < m; j++)
            {
                int u = 1 + rng() % n;
                int v = 1 + rng() % n;
                ll cap = rng() % 31;
                if (it % 4 == 0)
                    cap = (1LL << (rng() % 56)) + rng() % 8;
                edges.emplace_back(u, v, cap);
            }
            auto seed = rng();
            mt19937_64 a(seed), b(seed);
            exercise<Dinic>(n, edges, a);
            exercise<ScalingDinic>(n, edges, b);
        }
        boundaries<Dinic>();
        boundaries<ScalingDinic>();
        ScalingDinic threshold(3);
        threshold.add(1, 2, 7);
        threshold.add(2, 3, 7);
        require(!threshold.bfs(1, 3, 8));
        require(threshold.bfs(1, 3, 4));
        fill(threshold.cur.begin(), threshold.cur.end(), 0);
        require(threshold.dfs(1, 3, 3, 4) == 3);
        require(threshold.bfs(1, 3, 4));
        fill(threshold.cur.begin(), threshold.cur.end(), 0);
        require(threshold.dfs(1, 3, 4, 4) == 4);
        certificate(threshold, 1, 3, 7, true);
        ScalingDinic recursive_threshold(4);
        recursive_threshold.add(1, 2, 8);
        recursive_threshold.add(2, 3, 1);
        recursive_threshold.add(3, 4, 8);
        require(recursive_threshold.bfs(1, 4));
        fill(recursive_threshold.cur.begin(), recursive_threshold.cur.end(), 0);
        require(recursive_threshold.dfs(1, 4, 8, 4) == 0);
        cout << "PASS " << checks << " cut/flow/residual certificates; 4000 graphs; 64-bit and continuation boundaries\n";
    }
    catch (const exception &e)
    {
        cerr << e.what() << '\n';
        return 1;
    }
}
