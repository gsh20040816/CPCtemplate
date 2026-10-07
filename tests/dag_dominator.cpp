#include "../src/compact/dag_dominator.hpp"

long long cases = 0;

void require(bool ok)
{
    if (!ok)
        throw runtime_error("DAG dominator verification failed");
}

vector<int> reachable(const DagDominator &d, int root, int removed)
{
    vector<int> seen(d.n + 1);
    queue<int> q;
    if (root != removed)
    {
        seen[root] = 1;
        q.push(root);
    }
    while (!q.empty())
    {
        int u = q.front();
        q.pop();
        for (int v : d.g[u])
            if (v != removed && !seen[v])
            {
                seen[v] = 1;
                q.push(v);
            }
    }
    return seen;
}

bool acyclic(const DagDominator &d)
{
    vector<vector<int>> reach(d.n + 1, vector<int>(d.n + 1));
    for (int u = 1; u <= d.n; u++)
        for (int v : d.g[u])
            reach[u][v] = 1;
    for (int k = 1; k <= d.n; k++)
        for (int u = 1; u <= d.n; u++)
            for (int v = 1; v <= d.n; v++)
                reach[u][v] |= reach[u][k] && reach[k][v];
    for (int u = 1; u <= d.n; u++)
        if (reach[u][u])
            return false;
    return true;
}

void check(DagDominator &d)
{
    auto graph = d.g;
    bool dag = acyclic(d);
    for (int root = 1; root <= d.n; root++)
    {
        cases++;
        require(d.build(root) == dag);
        require(d.g == graph);
        if (!dag)
        {
            require(d.idom.empty() && d.dep.empty() && d.up.empty() && d.order.empty());
            continue;
        }
        auto seen = reachable(d, root, 0);
        vector<vector<int>> dom(d.n + 1, vector<int>(d.n + 1));
        for (int u = 1; u <= d.n; u++)
        {
            auto without = reachable(d, root, u);
            for (int v = 1; v <= d.n; v++)
                dom[u][v] = seen[v] && !without[v];
        }
        vector<int> rank(d.n + 1), size(d.n + 1);
        require(d.order.size() == (size_t)d.n);
        for (int i = 0; i < d.n; i++)
        {
            int u = d.order[i];
            require(1 <= u && u <= d.n && !rank[u]);
            rank[u] = i + 1;
        }
        for (int u = 1; u <= d.n; u++)
            for (int v : d.g[u])
                require(rank[u] < rank[v]);
        for (int u = 1; u <= d.n; u++)
        {
            if (!seen[u])
            {
                require(d.idom[u] == 0 && d.dep[u] == 0);
                continue;
            }
            require(d.idom[root] == root && d.dep[root] == 1);
            int count = 0;
            for (int p = 1; p <= d.n; p++)
                count += dom[p][u];
            require(count == d.dep[u]);
            if (u != root)
            {
                int p = d.idom[u];
                require(1 <= p && p <= d.n && p != u && dom[p][u]);
                for (int v = 1; v <= d.n; v++)
                    if (v != u && dom[v][u])
                        require(dom[v][p]);
            }
            require(d.lca(0, u) == u && d.lca(u, 0) == u);
            for (int v = 1; v <= d.n; v++)
                if (seen[v])
                {
                    int w = d.lca(u, v);
                    require(1 <= w && w <= d.n && dom[w][u] && dom[w][v]);
                    for (int p = 1; p <= d.n; p++)
                        if (dom[p][u] && dom[p][v])
                            require(dom[p][w]);
                }
        }
        require(d.lca(0, 0) == 0);
        for (int i = d.n - 1; i >= 0; i--)
        {
            int u = d.order[i];
            if (!seen[u])
                continue;
            size[u]++;
            if (u != root)
                size[d.idom[u]] += size[u];
        }
        for (int u = 1; u <= d.n; u++)
            require(size[u] == accumulate(dom[u].begin(), dom[u].end(), 0));
    }
    if (dag)
    {
        d.add(d.n, d.n);
        require(!d.build(1));
        require(d.idom.empty() && d.dep.empty() && d.up.empty() && d.order.empty());
    }
}

int main()
{
    mt19937 rng(20261009);
    for (int n = 1; n <= 6; n++)
    {
        vector<int> p(n);
        iota(p.begin(), p.end(), 1);
        shuffle(p.begin(), p.end(), rng);
        vector<pair<int, int>> edges;
        for (int i = 0; i < n; i++)
            for (int j = i + 1; j < n; j++)
                edges.push_back({p[i], p[j]});
        for (int mask = 0; mask < (1 << edges.size()); mask++)
        {
            DagDominator d(n);
            for (int i = 0; i < (int)edges.size(); i++)
                if (mask >> i & 1)
                    d.add(edges[i].first, edges[i].second);
            check(d);
        }
    }
    for (int trial = 0; trial < 800; trial++)
    {
        int n = 1 + rng() % 20;
        DagDominator d(n);
        vector<int> p(n);
        iota(p.begin(), p.end(), 1);
        shuffle(p.begin(), p.end(), rng);
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                if ((trial % 3 == 0 || i < j) && rng() % 4 == 0)
                {
                    d.add(p[i], p[j]);
                    if (rng() % 3 == 0)
                        d.add(p[i], p[j]);
                }
        check(d);
    }
    int n = 200000;
    DagDominator chain(n);
    for (int i = 2; i <= n; i++)
        chain.add(i, i - 1);
    require(chain.build(n));
    for (int i = 1; i <= n; i++)
    {
        require(chain.idom[i] == min(i + 1, n));
        require(chain.dep[i] == n - i + 1);
        int j = rng() % n + 1;
        require(chain.lca(i, j) == max(i, j));
    }
    require(chain.build(n / 2));
    for (int i = n / 2 + 1; i <= n; i++)
        require(chain.idom[i] == 0 && chain.dep[i] == 0);
    chain.add(1, n);
    require(!chain.build(n));
    require(chain.idom.empty() && chain.order.empty());
    cout << cases << '\n';
}
