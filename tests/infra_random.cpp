#include "../examples/infra/random_tools.hpp"

int main() {
    for (int seed = 0; seed < 1000; seed++) {
        rng.seed(seed);
        int n = seed % 31;
        auto p = permutation(n);
        auto sorted = p;
        sort(sorted.begin(), sorted.end());
        for (int i = 0; i < n; i++) {
            assert(sorted[i] == i);
        }
        auto values = distinct_values(n, n / 2);
        set<int> unique(values.begin(), values.end());
        assert(unique.size() == values.size());
        assert(values.size() == (size_t)n / 2);
        for (int x : values) {
            assert(0 <= x && x < n);
        }
        auto s = random_string(n, "az0");
        assert(s.size() == (size_t)n);
        assert(s.find_first_not_of("az0") == string::npos);
        auto tree = random_tree(n);
        assert(tree.size() == (size_t)max(0, n - 1));
        vector<vector<int>> adj(n);
        for (auto [u, v] : tree) {
            assert(0 <= u && u < n && 0 <= v && v < n && u != v);
            adj[u].push_back(v);
            adj[v].push_back(u);
        }
        vector<bool> seen(n);
        auto dfs = [&](auto&& self, int u) -> void {
            seen[u] = true;
            for (int v : adj[u]) {
                if (!seen[v]) {
                    self(self, v);
                }
            }
        };
        if (n > 0) {
            dfs(dfs, 0);
        }
        assert(count(seen.begin(), seen.end(), true) == n);
        int capacity = n * (n - 1) / 2;
        for (int m : {0, capacity / 2, capacity}) {
            auto edges = random_graph(n, m);
            set<pair<int, int>> distinct(edges.begin(), edges.end());
            assert(edges.size() == (size_t)m && distinct.size() == edges.size());
            for (auto [u, v] : edges) {
                assert(0 <= u && u < v && v < n);
            }
        }
        for (int i = 0; i < 100; i++) {
            auto x = random_int(-10, 10);
            auto y = random_real(-1, 1);
            assert(-10 <= x && x <= 10);
            assert(-1 <= y && y < 1);
        }
        assert(random_int(LLONG_MIN, LLONG_MIN) == LLONG_MIN);
        assert(random_int(LLONG_MAX, LLONG_MAX) == LLONG_MAX);
        (void)random_int(LLONG_MIN, LLONG_MAX);
        rng.seed(seed);
        auto a = random_tree(n);
        rng.seed(seed);
        assert(a == random_tree(n));
    }
    cout << "1000 seeds: permutation, unique values, strings, trees, graphs, ranges PASS\n";
}
