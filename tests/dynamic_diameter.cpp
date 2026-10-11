#include "../src/compact/dynamic_diameter.hpp"

void check(const DynamicDiameter &tree)
{
    long long answer = 0;
    for (int root = 1; root <= tree.n; root++)
    {
        auto dfs = [&](auto &&self, int u, int parent, long long d) -> void
        {
            answer = max(answer, d);
            for (auto [v, id] : tree.g[u])
                if (v != parent) self(self, v, u, d + tree.edges[id].w);
        };
        dfs(dfs, root, 0, 0);
    }
    if (answer != tree.diameter()) abort();
}

int main()
{
    mt19937 rng(20261011);
    int exhaustive = 0;
    for (int n = 1; n <= 5; n++)
    {
        int codes = 1;
        for (int i = 0; i < n - 2; i++) codes *= n;
        for (int code = 0; code < codes; code++)
        {
            vector<int> degree(n + 1, 1), sequence;
            int cur = code;
            for (int i = 0; i < n - 2; i++)
            {
                int u = cur % n + 1;
                cur /= n;
                sequence.push_back(u);
                degree[u]++;
            }
            vector<pair<int, int>> es;
            for (int u : sequence)
            {
                int v = 1;
                while (degree[v] != 1) v++;
                es.push_back({u, v});
                degree[u]--;
                degree[v]--;
            }
            if (n > 1)
            {
                vector<int> leaves;
                for (int u = 1; u <= n; u++)
                    if (degree[u] == 1) leaves.push_back(u);
                es.push_back({leaves[0], leaves[1]});
            }
            int weights = 1;
            for (int i = 1; i < n; i++) weights *= 3;
            for (int mask = 0; mask < weights; mask++)
            {
                DynamicDiameter tree(n);
                int z = mask;
                for (auto [u, v] : es)
                {
                    tree.add(u, v, z % 3);
                    z /= 3;
                }
                for (int root = 1; root <= n; root++)
                {
                    tree.build(root);
                    check(tree);
                }
                for (int id = 0; id < n - 1; id++)
                {
                    tree.update(id, 4);
                    check(tree);
                    tree.update(id, 0);
                    check(tree);
                }
                exhaustive++;
            }
        }
    }
    for (int test = 0; test < 1500; test++)
    {
        int n = rng() % 45 + 1;
        DynamicDiameter tree(n);
        vector<int> p(n);
        iota(p.begin(), p.end(), 1);
        shuffle(p.begin(), p.end(), rng);
        for (int i = 1; i < n; i++) tree.add(p[i], p[rng() % i], rng() % 100);
        tree.build(rng() % n + 1);
        check(tree);
        for (int q = 0; q < 80 && n > 1; q++)
        {
            tree.update(rng() % (n - 1), rng() % 100);
            check(tree);
            if (q % 19 == 0)
            {
                auto copy = tree;
                copy.build(rng() % n + 1);
                check(copy);
                copy.update(rng() % (n - 1), 0);
                check(copy);
                check(tree);
            }
        }
    }
    DynamicDiameter large(3);
    large.add(1, 2, LLONG_MAX / 8);
    large.add(2, 3, LLONG_MAX / 8);
    large.build(2);
    check(large);
    large.update(0, 0);
    check(large);
    large.update(1, LLONG_MAX / 4);
    check(large);
    cout << "PASS: " << exhaustive << " weighted labeled trees, 1500 random update sequences, all-pairs oracle, roots/copies/rebuilds/64-bit\n";
}
