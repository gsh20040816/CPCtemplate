#include "../src/compact/dag_path_determinant.hpp"
using Z = ModInt<998244353>;
using Graph = vector<vector<pair<int, Z>>>;

void check(const Graph &g, const vector<int> &s, const vector<int> &t)
{
    int k = s.size();
    vector<vector<vector<pair<unsigned, Z>>>> paths(
        k, vector<vector<pair<unsigned, Z>>>(k));
    for (int i = 0; i < k; i++)
        for (int j = 0; j < k; j++)
        {
            auto dfs = [&](auto &&self, int u, unsigned mask, Z weight) -> void
            {
                mask |= 1U << u;
                if (u == t[j]) paths[i][j].push_back({mask, weight});
                for (auto [v, w] : g[u]) self(self, v, mask, weight * w);
            };
            dfs(dfs, s[i], 0, 1);
        }
    vector<int> p(k);
    iota(p.begin(), p.end(), 0);
    Z expected = 0;
    do
    {
        int sign = 1;
        for (int i = 0; i < k; i++)
            for (int j = 0; j < i; j++)
                if (p[j] > p[i]) sign = -sign;
        auto choose = [&](auto &&self, int i, unsigned used, Z value) -> void
        {
            if (i == k)
            {
                expected = expected + value * sign;
                return;
            }
            for (auto [mask, w] : paths[i][p[i]])
                if (!(used & mask)) self(self, i + 1, used | mask, value * w);
        };
        choose(choose, 0, 0, 1);
    } while (next_permutation(p.begin(), p.end()));
    auto result = dag_path_determinant<998244353>(g, s, t);
    assert(result && result->v == expected.v);
}

int main()
{
    check({}, {}, {});
    check(Graph(1), {0}, {0});
    Graph crossing(4);
    crossing[0].push_back({3, 1});
    crossing[1].push_back({2, 1});
    check(crossing, {0, 1}, {2, 3});
    assert(dag_path_determinant<998244353>(crossing, {0, 1}, {2, 3})->v == 998244352);
    mt19937 rng(314);
    for (int z = 0; z < 3000; z++)
    {
        int n = 1 + rng() % 7, k = rng() % (min(n, 3) + 1);
        vector<int> order(n), sources(n), sinks(n);
        iota(order.begin(), order.end(), 0);
        shuffle(order.begin(), order.end(), rng);
        sources = sinks = order;
        shuffle(sources.begin(), sources.end(), rng);
        shuffle(sinks.begin(), sinks.end(), rng);
        sources.resize(k);
        sinks.resize(k);
        Graph g(n);
        for (int i = 0; i < n; i++)
            for (int j = i + 1; j < n; j++)
                for (int copies = rng() % 3; copies--;)
                    if (rng() % 2)
                        g[order[i]].push_back({order[j], Z(int(rng() % 7) - 3)});
        check(g, sources, sinks);
    }
    Graph cycle(3);
    cycle[0].push_back({0, 1});
    assert(!dag_path_determinant<998244353>(cycle, {1}, {2}));
    cycle[0] = {{1, 1}};
    cycle[1] = {{2, 1}};
    cycle[2] = {{0, 1}};
    assert(!dag_path_determinant<998244353>(cycle, {}, {}));
    int n = 100000;
    Graph chain(n);
    for (int i = 1; i < n; i++) chain[i - 1].push_back({i, 1});
    assert(dag_path_determinant<998244353>(chain, {0}, {n - 1})->v == 1);
    cout << "LGV: 3000 independent disjoint path-family enumerations, signed "
            "permutations, zero-length paths, overlap, parallel/negative/zero edges; "
            "disconnected cycles and 100000-vertex DAG PASS\n";
}
