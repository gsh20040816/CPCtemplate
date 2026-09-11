#include "../src/compact/graph_advanced.hpp"
#include <iostream>
int main() {
  std::mt19937 rng(20260915);
  for (int it = 0; it < 500; it++) {
    int n = 1 + rng() % 5, m = n + rng() % 2;
    std::vector<std::vector<long long>> c(n, std::vector<long long>(m));
    for (auto &row : c)
      for (auto &x : row)
        x = int(rng() % 100) - 50;
    std::vector<int> p(m);
    std::iota(p.begin(), p.end(), 0);
    long long want = LLONG_MAX;
    do {
      long long sum = 0;
      for (int i = 0; i < n; i++)
        sum += c[i][p[i]];
      want = std::min(want, sum);
    } while (std::next_permutation(p.begin(), p.end()));
    auto [ans, match] = Hungarian::solve(c);
    assert(ans == want);
    std::set<int> s;
    long long sum = 0;
    for (int i = 0; i < n; i++) {
      s.insert(match[i]);
      sum += c[i][match[i]];
    }
    assert((int)s.size() == n && sum == want);
  }
  for (int it = 0; it < 300; it++) {
    int n = 2 + rng() % 5;
    std::vector<Arborescence::Edge> es;
    std::vector<std::vector<int>> incoming(n);
    for (int j = 0; j < 10; j++) {
      int u = rng() % n, v = rng() % n;
      es.push_back({u, v, int(rng() % 20) - 10});
      if (u != v)
        incoming[v].push_back(es.size() - 1);
    }
    __int128 best = __int128(1) << 120;
    std::vector<int> par(n, -1);
    std::function<void(int, __int128)> dfs = [&](int v, __int128 cost) {
      if (v == n) {
        for (int i = 1; i < n; i++) {
          int u = i, steps = 0;
          while (u != 0 && steps < n) {
            u = par[u];
            steps++;
          }
          if (u != 0)
            return;
        }
        best = std::min(best, cost);
        return;
      }
      for (int id : incoming[v]) {
        par[v] = es[id].u;
        dfs(v + 1, cost + es[id].w);
      }
    };
    dfs(1, 0);
    auto got = Arborescence::solve(n, 0, es);
    assert(got.has_value() == (best != (__int128(1) << 120)));
    if (got)
      assert(*got == best);
    std::vector<std::vector<__int128>> w(n, std::vector<__int128>(n));
    for (int i = 0; i < n; i++)
      for (int j = 0; j < i; j++)
        w[i][j] = w[j][i] = rng() % 20;
    best = __int128(1) << 120;
    for (int mask = 1; mask < (1 << n) - 1; mask++) {
      __int128 sum = 0;
      for (int i = 0; i < n; i++)
        for (int j = 0; j < i; j++)
          if ((mask >> i & 1) != (mask >> j & 1))
            sum += w[i][j];
      best = std::min(best, sum);
    }
    assert(StoerWagner::solve(w).first == best);
  }
  std::cout << "Hungarian, arborescence, Stoer-Wagner PASS\n";
}
