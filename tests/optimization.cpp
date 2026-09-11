#include "../src/compact/optimization.hpp"
#include <iostream>
int main() {
  std::mt19937 rng(20260914);
  for (int it = 0; it < 500; it++) {
    int n = 1 + rng() % 30;
    std::vector<long long> a(n);
    for (auto &x : a)
      x = int(rng() % 100) - 50;
    PersistentKth p(a);
    LiChao l(a);
    std::vector<LiChao::Line> lines;
    for (int i = 0; i < n; i++) {
      lines.push_back({int(rng() % 100) - 50, int(rng() % 100) - 50, i});
      l.add(lines.back());
      for (auto x : a) {
        std::pair<__int128, int> want{__int128(1) << 120, -1};
        for (auto line : lines)
          want = std::min(want, std::pair{line.value(x), line.id});
        assert(l.query(x) == want);
      }
    }
    for (int j = 0; j < 30; j++) {
      int L = rng() % n, R = rng() % n;
      if (L > R)
        std::swap(L, R);
      std::vector<long long> b(a.begin() + L, a.begin() + R + 1);
      std::sort(b.begin(), b.end());
      int k = 1 + rng() % b.size();
      assert(p.kth(L + 1, R + 1, k) == b[k - 1]);
    }
    int m = 1 + rng() % 5;
    MaxPlusMatrix mat(m);
    for (auto &row : mat.a)
      for (auto &x : row)
        if (rng() % 3)
          x = int(rng() % 20) - 10;
    int steps = rng() % 8;
    auto got = mat.power(steps);
    std::vector<__int128> d(m, MaxPlusMatrix::neg);
    d[0] = 0;
    for (int t = 0; t < steps; t++) {
      std::vector<__int128> nd(m, MaxPlusMatrix::neg);
      for (int u = 0; u < m; u++)
        for (int v = 0; v < m; v++)
          if (d[u] != MaxPlusMatrix::neg && mat.a[u][v] != MaxPlusMatrix::neg)
            nd[v] = std::max(nd[v], d[u] + mat.a[u][v]);
      d = nd;
    }
    for (int i = 0; i < m; i++)
      assert(got.a[0][i] == d[i]);
  }
  std::cout << "Li Chao, persistent kth, max-plus PASS\n";
}
