#include "../src/classic/algebra.hpp"
#include "../src/classic/geometry.hpp"
#include "../src/classic/graph.hpp"
#include "../src/classic/min_cost_flow.hpp"
#include "../src/classic/polynomial.hpp"
#include "../src/classic/string.hpp"
#include "../src/classic/tree.hpp"
#include <iostream>
int main() {
  std::mt19937 rng(20260912);
  for (int it = 0; it < 500; it++) {
    int n = 2 + rng() % 7;
    Strong_Component g(n);
    Shortest_Path d(n);
    std::vector<std::vector<int>> reach(n + 1, std::vector<int>(n + 1));
    for (int i = 1; i <= n; i++)
      reach[i][i] = 1;
    for (int j = 0; j < 20; j++) {
      int u = 1 + rng() % n, v = 1 + rng() % n;
      g.Insert(u, v);
      d.Insert(u, v, 1);
      reach[u][v] = 1;
    }
    for (int k = 1; k <= n; k++)
      for (int i = 1; i <= n; i++)
        for (int j = 1; j <= n; j++)
          reach[i][j] |= reach[i][k] & reach[k][j];
    g.Run();
    d.Run(1);
    for (int i = 1; i <= n; i++) {
      assert((d.dis[i] != Shortest_Path::inf) == bool(reach[1][i]));
      for (int j = 1; j <= n; j++)
        assert((g.bel[i] == g.bel[j]) == bool(reach[i][j] && reach[j][i]));
    }
    std::string s;
    for (int i = 0; i < n; i++)
      s += 'a' + rng() % 3;
    Suffix_Array sa(s);
    Suffix_Automaton sam;
    for (char c : s)
      sam.Extend(c - 'a');
    std::set<std::string> sub;
    for (int i = 0; i < n; i++)
      for (int j = i; j < n; j++)
        sub.insert(s.substr(i, j - i + 1));
    assert(sam.Distinct() == (long long)sub.size());
    for (int i = 1; i < n; i++)
      assert(s.substr(sa.sa[i - 1]) < s.substr(sa.sa[i]));
    using G = Integer_Geometry;
    std::vector<G::Point> p;
    for (int i = 0; i < n; i++)
      p.push_back({int(rng() % 20), int(rng() % 20)});
    auto h = G::Convex_Hull(p);
    __int128 best = 0;
    for (auto a : p)
      for (auto b : p)
        best = std::max(best, G::Distance_Squared(a, b));
    assert(G::Diameter_Squared(h) == best);
    using P = Polynomial;
    P::Poly a(n);
    for (auto &x : a)
      x = rng();
    a[0] = 1;
    auto b = P::Exp(P::Log(a, n), n);
    for (int i = 0; i < n; i++)
      assert(a[i].v == b[i].v);
    Min_Cost_Flow f(2);
    int id = f.Insert(1, 2, n, -3);
    auto [v, c] = f.Flow(1, 2);
    assert(v == n && c == -3 * n && f.Used(id) == n);
  }
  for (int n = 1; n < 1000; n++) {
    bool p = n > 1;
    for (int j = 2; j * j <= n; j++)
      if (n % j == 0)
        p = false;
    assert(Number_Theory::Prime(n) == p);
  }
  std::cout << "classic modules PASS\n";
}
