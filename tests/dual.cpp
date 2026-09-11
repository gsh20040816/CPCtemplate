#include <bits/stdc++.h>
#include <cassert>
namespace compact {
#include "../src/compact/flow.hpp"
#include "../src/compact/geometry_extra.hpp"
#include "../src/compact/graph_advanced.hpp"
#include "../src/compact/optimization.hpp"
} // namespace compact
namespace classic {
#include "../src/classic/flow.hpp"
#include "../src/classic/geometry_extra.hpp"
#include "../src/classic/graph_advanced.hpp"
#include "../src/classic/min_cost_flow.hpp"
#include "../src/classic/optimization.hpp"
} // namespace classic
int main() {
  std::mt19937 rng(20260917);
  for (int it = 0; it < 500; it++) {
    int n = 2 + rng() % 15;
    std::vector<long long> x(n);
    for (auto &v : x)
      v = int(rng() % 101) - 50;
    compact::LiChao a(x);
    classic::Li_Chao_Tree b(x);
    compact::PersistentKth p(x);
    classic::Persistent_Kth q(x);
    for (int i = 0; i < n; i++) {
      long long k = int(rng() % 101) - 50, c = int(rng() % 101) - 50;
      a.add({k, c, i});
      b.Insert({k, c, i});
      for (auto v : x)
        assert(a.query(v) == b.Query(v));
    }
    for (int j = 0; j < 20; j++) {
      int l = 1 + rng() % n, r = 1 + rng() % n;
      if (l > r)
        std::swap(l, r);
      int k = 1 + rng() % (r - l + 1);
      assert(p.kth(l, r, k) == q.Kth(l, r, k));
    }
    std::vector<compact::IntegerGeometry::Point> u;
    std::vector<classic::Integer_Geometry::Point> v;
    for (int i = 0; i < n; i++) {
      int X = int(rng() % 100) - 50, Y = int(rng() % 100) - 50;
      u.push_back({X, Y});
      v.push_back({X, Y});
    }
    assert(compact::GeometryExtra::closest_pair(u) ==
           classic::Geometry_Extra::Closest_Pair(v));
    compact::BoundedCirculation f(3);
    classic::Bounded_Circulation<3, 6> F;
    F.Init(3);
    for (int j = 0; j < 6; j++) {
      int s = 1 + rng() % 3, t = 1 + rng() % 3, L = rng() % 3,
          R = L + rng() % 3;
      f.add(s, t, L, R);
      F.Insert(s, t, L, R);
    }
    assert(f.solve() == F.Solve());
    compact::MinCostFlow mf(4);
    classic::Min_Cost_Flow MF(4);
    for (int j = 0; j < 8; j++) {
      int s = 1 + rng() % 3, t = s + 1 + rng() % (4 - s), cap = rng() % 4,
          cost = int(rng() % 20) - 10;
      mf.add(s, t, cap, cost);
      MF.Insert(s, t, cap, cost);
    }
    assert(mf.flow(1, 4) == MF.Flow(1, 4));
    std::vector<std::vector<long long>> cost(3, std::vector<long long>(4));
    for (auto &r : cost)
      for (auto &z : r)
        z = int(rng() % 100) - 50;
    assert(compact::Hungarian::solve(cost).first ==
           classic::Kuhn_Munkres::Solve(cost).first);
    std::vector<compact::Arborescence::Edge> e;
    std::vector<classic::Directed_MST::Edge> E;
    for (int j = 0; j < 10; j++) {
      int s = rng() % 4, t = rng() % 4, w = int(rng() % 20) - 10;
      e.push_back({s, t, w});
      E.push_back({s, t, w});
    }
    assert(compact::Arborescence::solve(4, 0, e) ==
           classic::Directed_MST::Solve(4, 0, E));
    std::vector<std::vector<__int128>> w(4, std::vector<__int128>(4));
    for (int i = 0; i < 4; i++)
      for (int j = 0; j < i; j++)
        w[i][j] = w[j][i] = rng() % 20;
    assert(compact::StoerWagner::solve(w).first ==
           classic::Global_Min_Cut::Solve(w).first);
  }
  std::cout << "dual geometry, flow, optimization, graph-advanced PASS\n";
}
