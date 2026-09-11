#include "../src/compact/geometry_extra.hpp"
#include "../src/compact/flow.hpp"
#include <iostream>
int main() {
  std::mt19937 rng(20260916);
  using G = IntegerGeometry;
  using E = GeometryExtra;
  for (int it = 0; it < 1000; it++) {
    std::vector<G::Point> a, b;
    for (int i = 0, n = 2 + rng() % 30; i < n; i++)
      a.push_back({int(rng() % 41) - 20, int(rng() % 41) - 20});
    for (int i = 0, n = 1 + rng() % 30; i < n; i++)
      b.push_back({int(rng() % 41) - 20, int(rng() % 41) - 20});
    __int128 best = __int128(1) << 120;
    for (int i = 0; i < (int)a.size(); i++)
      for (int j = 0; j < i; j++)
        best = std::min(best, G::dist2(a[i], a[j]));
    assert(*E::closest_pair(a) == best);
    auto h = G::hull(a), k = G::hull(b);
    std::vector<G::Point> sum;
    for (auto u : a)
      for (auto v : b)
        sum.push_back({u.x + v.x, u.y + v.y});
    auto want = G::hull(sum), got = E::minkowski(h, k);
    std::sort(want.begin(), want.end());
    std::sort(got.begin(), got.end());
    assert(want == got);
  }
  for (int it = 0; it < 300; it++) {
    int n = 3, m = 1 + rng() % 6;
    BoundedCirculation g(n);
    std::vector<std::array<int, 4>> es;
    for (int i = 0; i < m; i++) {
      int u = 1 + rng() % n, v = 1 + rng() % n, lo = rng() % 2,
          hi = lo + rng() % 3;
      es.push_back({u, v, lo, hi});
      g.add(u, v, lo, hi);
    }
    std::vector<int> b(n + 1);
    bool ok = false;
    std::function<void(int)> dfs = [&](int i) {
      if (i == m) {
        ok |= std::all_of(b.begin(), b.end(), [](int x) { return x == 0; });
        return;
      }
      auto [u, v, l, r] = es[i];
      for (int x = l; x <= r; x++) {
        b[u] -= x;
        b[v] += x;
        dfs(i + 1);
        b[u] += x;
        b[v] -= x;
      }
    };
    dfs(0);
    assert(g.solve() == ok);
    if (ok) {
      std::fill(b.begin(), b.end(), 0);
      for (int i = 0; i < m; i++) {
        auto [u, v, l, r] = es[i];
        auto f = g.used(i);
        assert(l <= f && f <= r);
        b[u] -= f;
        b[v] += f;
      }
      for (int x : b)
        assert(x == 0);
    }
  }
  std::cout << "closest pair, Minkowski, bounded circulation PASS\n";
}
