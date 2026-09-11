#include "../src/classic/graph.hpp"
#include "../src/compact/graph.hpp"
#include <iostream>
int main() {
  std::mt19937 rng(20260918);
  for (int it = 0; it < 1000; it++) {
    int n = 1 + rng() % 9, m = rng() % 20;
    Lowlink g(n);
    Low_Link G(n);
    std::vector<std::pair<int, int>> e;
    for (int j = 0; j < m; j++) {
      int u = 1 + rng() % n, v = 1 + rng() % n;
      e.push_back({u, v});
      g.add(u, v);
      G.Insert(u, v);
    }
    auto components = [&](int vertex, int edge) {
      std::vector<int> vis(n + 1);
      int cnt = 0;
      for (int s = 1; s <= n; s++)
        if (s != vertex && !vis[s]) {
          cnt++;
          std::vector<int> q{s};
          vis[s] = 1;
          for (int k = 0; k < (int)q.size(); k++) {
            int u = q[k];
            for (int id = 0; id < m; id++)
              if (id != edge) {
                auto [a, b] = e[id];
                if (b == u)
                  std::swap(a, b);
                if (a == u && b != vertex && !vis[b]) {
                  vis[b] = 1;
                  q.push_back(b);
                }
              }
          }
        }
      return cnt;
    };
    int base = components(-1, -1);
    g.run();
    G.Run();
    for (int u = 1; u <= n; u++) {
      bool want = components(u, -1) > base;
      assert(g.cut[u] == want && G.cut[u] == want);
    }
    for (int id = 0; id < m; id++) {
      bool want = components(-1, id) > base;
      assert(g.bridge[id] == want && G.bridge[id] == want);
    }
  }
  std::cout << "multigraph lowlink removal oracle PASS\n";
}
