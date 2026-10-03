#include "../src/compact/tree.hpp"

long long trees = 0, checks = 0;

vector<int> route(int u, int v, const vector<int> &fa, const vector<int> &dep)
{
    vector<int> a, b;
    while (u != v)
    {
        if (dep[u] >= dep[v])
        {
            a.push_back(u);
            u = fa[u];
        }
        else
        {
            b.push_back(v);
            v = fa[v];
        }
    }
    a.push_back(u);
    a.insert(a.end(), b.rbegin(), b.rend());
    return a;
}

void check(HLD &h, int root, const vector<pair<int, int>> &queries)
{
    h.build(root);
    vector<int> fa(h.n + 1, -1), dep(h.n + 1);
    queue<int> q;
    q.push(root);
    fa[root] = root;
    while (!q.empty())
    {
        int u = q.front();
        q.pop();
        for (int v : h.g[u])
            if (fa[v] == -1)
            {
                fa[v] = u;
                dep[v] = dep[u] + 1;
                q.push(v);
            }
    }
    for (auto [u, v] : queries)
    {
        auto nodes = route(u, v, fa, dep);
        int ancestor = *min_element(nodes.begin(), nodes.end(), [&](int a, int b)
        {
            return dep[a] < dep[b];
        });
        for (bool edge : {false, true})
        {
            auto expected = nodes;
            if (edge) expected.erase(find(expected.begin(), expected.end(), ancestor));
            vector<int> actual;
            int segments = 0;
            h.path_ordered(u, v, [&](int l, int r, bool rev)
            {
                assert(1 <= l && l <= r && r <= h.n);
                segments++;
                if (rev)
                    for (int i = r; i >= l; --i) actual.push_back(h.rk[i]);
                else
                    for (int i = l; i <= r; ++i) actual.push_back(h.rk[i]);
            }, edge);
            assert(actual == expected);
            assert(segments <= 2 * int(bit_width(unsigned(h.n))) + 1);
            if (u == v) assert(segments == (edge ? 0 : 1));
            checks++;
        }
    }
}

int main()
{
    for (int n = 1; n <= 6; n++)
    {
        int count = 1;
        for (int i = 0; i < n - 2; i++) count *= n;
        for (int code = 0; code < count; code++)
        {
            HLD h(n);
            vector<int> seq, degree(n + 1, 1);
            int x = code;
            for (int i = 0; i < n - 2; i++)
            {
                int v = x % n + 1;
                x /= n;
                seq.push_back(v);
                degree[v]++;
            }
            for (int v : seq)
            {
                int leaf = 1;
                while (degree[leaf] != 1) leaf++;
                h.add(leaf, v);
                degree[leaf]--;
                degree[v]--;
            }
            if (n > 1)
            {
                vector<int> leaves;
                for (int i = 1; i <= n; i++)
                    if (degree[i] == 1) leaves.push_back(i);
                assert(leaves.size() == 2);
                h.add(leaves[0], leaves[1]);
            }
            vector<pair<int, int>> queries;
            for (int u = 1; u <= n; u++)
                for (int v = 1; v <= n; v++) queries.emplace_back(u, v);
            for (int root = 1; root <= n; root++) check(h, root, queries);
            for (auto &g : h.g) reverse(g.begin(), g.end());
            check(h, n, queries);
            trees++;
        }
    }
    mt19937 rng(231);
    for (int trial = 0; trial < 100; trial++)
    {
        int n = 10 + rng() % 71;
        HLD h(n);
        vector<int> p(n);
        iota(p.begin(), p.end(), 1);
        shuffle(p.begin(), p.end(), rng);
        for (int i = 1; i < n; i++) h.add(p[i], p[rng() % i]);
        vector<pair<int, int>> queries;
        for (int i = 0; i < 100; i++) queries.emplace_back(1 + rng() % n, 1 + rng() % n);
        for (int root : {1, n, p[0]}) check(h, root, queries);
        trees++;
    }
    {
        HLD h(15);
        for (int i = 2; i <= 15; i++) h.add(i / 2, i);
        vector<pair<int, int>> queries{{11,15},{11,12},{15,11}};
        for (int root : {1,15,1}) check(h, root, queries);
        trees++;
    }
    for (int kind = 0; kind < 3; kind++)
    {
        int n = 200000;
        HLD h(n);
        for (int v = 2; v <= n; v++) h.add(v, kind == 0 ? v - 1 : kind == 1 ? 1 : v / 2);
        vector<pair<int, int>> queries{{1,n},{n,1},{n,n},{1,1},{n/2,n},{n,n/2},{n/2,n/2+1}};
        if (kind == 2)
            for (int i = 0; i < 2000; i++) queries.emplace_back(1 + rng() % n, 1 + rng() % n);
        for (int root : {1, n, n/2}) check(h, root, queries);
        trees++;
    }
    cout << "Ordered HLD: " << trees << " trees, " << checks
         << " exact directed vertex/edge paths, rerooting and 200000-node chain/star/binary trees PASS\n";
}
