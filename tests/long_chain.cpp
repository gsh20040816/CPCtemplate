#include "../src/compact/long_chain.hpp"

#define CHECK(x) do { if (!(x)) { cerr << "line " << __LINE__ << '\n'; abort(); } } while (0)

void check(LongChain &t, int root)
{
    t.build(root);
    vector<int> p(t.n + 1, -1), d(t.n + 1), order{root};
    p[root] = 0;
    d[root] = 1;
    for (int i = 0; i < (int)order.size(); i++)
    {
        int u = order[i];
        for (int v : t.g[u])
        {
            if (p[v] != -1) continue;
            p[v] = u;
            d[v] = d[u] + 1;
            order.push_back(v);
        }
    }
    CHECK((int)order.size() == t.n);
    int total = 0;
    vector<int> height(t.n + 1, 1);
    for (int i = t.n - 1; i > 0; i--)
        height[p[order[i]]] = max(height[p[order[i]]], height[order[i]] + 1);
    for (int u = 1; u <= t.n; u++)
    {
        CHECK(t.dep[u] == d[u]);
        CHECK(t.len[u] == height[u]);
        int v = u;
        for (int k = 0; k <= t.n + 1; k++)
        {
            CHECK(t.kth(u, k) == v);
            if (v) v = p[v];
        }
        CHECK(t.kth(u, INT_MAX) == 0);
        if (t.top[u] == u)
        {
            CHECK((int)t.down[u].size() == height[u]);
            CHECK(t.up[u].size() == t.down[u].size());
            total += t.down[u].size();
            v = u;
            for (int i = 0; i < height[u]; i++)
            {
                CHECK(t.up[u][i] == v);
                if (v) v = p[v];
                int x = t.down[u][i];
                CHECK(t.top[x] == u);
                CHECK(i == 0 ? x == u : p[x] == t.down[u][i - 1]);
            }
        }
        else CHECK(t.up[u].empty() && t.down[u].empty());
    }
    CHECK(total == t.n);
}

int main(int argc, char **argv)
{
    if (argc > 1)
    {
        int n = 500000;
        for (int shape = 0; shape < 3; shape++)
        {
            LongChain t(n);
            for (int u = 2; u <= n; u++)
                t.add(u, shape == 0 ? u - 1 : shape == 1 ? 1 : u / 2);
            t.build();
            for (int u = 1; u <= n; u++)
            {
                CHECK(t.kth(u, 0) == u);
                CHECK(t.kth(u, t.dep[u] - 1) == 1);
                CHECK(t.kth(u, t.dep[u]) == 0);
                for (int k = 1; k < t.dep[u]; k *= 2)
                {
                    CHECK(t.kth(u, k) == (shape == 0 ? u - k : shape == 1 ? 1 : u >> k));
                }
            }
            if (shape == 0)
            {
                t.build(n);
                for (int u = 1; u <= n; u++)
                {
                    CHECK(t.kth(u, n - u) == n);
                    CHECK(t.kth(u, (n - u) / 2) == u + (n - u) / 2);
                    CHECK(t.kth(u, n - u + 1) == 0);
                }
            }
        }
        cout << "500000-node chain/reroot/star/heap PASS\n";
        return 0;
    }
    int count = 0;
    for (int n = 1; n <= 6; n++)
    {
        int sequences = 1;
        for (int i = 0; i < n - 2; i++) sequences *= n;
        for (int mask = 0; mask < sequences; mask++)
        {
            LongChain t(n);
            vector<int> code(max(0, n - 2)), degree(n + 1, 1);
            int x = mask;
            for (int &v : code)
            {
                v = x % n + 1;
                x /= n;
                degree[v]++;
            }
            for (int v : code)
            {
                int u = 1;
                while (degree[u] != 1) u++;
                t.add(u, v);
                degree[u]--;
                degree[v]--;
            }
            vector<int> leaves;
            for (int u = 1; u <= n; u++)
                if (degree[u] == 1) leaves.push_back(u);
            if (n > 1) t.add(leaves[0], leaves[1]);
            for (int root = 1; root <= n; root++) check(t, root);
            count++;
        }
    }
    mt19937 rng(5903);
    for (int trial = 0; trial < 3000; trial++)
    {
        int n = rng() % 100 + 1;
        vector<int> label(n);
        iota(label.begin(), label.end(), 1);
        shuffle(label.begin(), label.end(), rng);
        LongChain t(n);
        for (int u = 1; u < n; u++) t.add(label[u], label[rng() % u]);
        check(t, label[0]);
        LongChain copy = t;
        check(copy, label.back());
        CHECK(t.dep[label[0]] == 1);
        check(t, label[rng() % n]);
    }
    LongChain broom(100);
    for (int u = 2; u <= 20; u++) broom.add(u - 1, u);
    broom.add(1, 21);
    for (int u = 22; u <= 100; u++) broom.add(21, u);
    check(broom, 1);
    CHECK(broom.son[1] == 2);
    cout << count << " labelled trees/all roots; 3000 shuffled trees/copy/reroot; broom PASS\n";
}
