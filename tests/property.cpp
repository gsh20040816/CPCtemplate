#include "../src/classic/data_structure.hpp"
#include "../src/classic/flow.hpp"
#include "../src/classic/string.hpp"
#include "../src/compact/data_structure.hpp"
#include "../src/compact/flow.hpp"
#include "../src/compact/geometry.hpp"
#include "../src/compact/graph.hpp"
#include "../src/compact/number_theory.hpp"
#include "../src/compact/polynomial.hpp"
#include "../src/compact/string.hpp"
#include "../src/compact/tree.hpp"
#include <boost/multiprecision/cpp_int.hpp>
using boost::multiprecision::cpp_int;
mt19937 rng(20260911);
int rnd(int n) { return rng() % n; }
void structures() {
  for (int it = 0; it < 500; it++) {
    int n = 1 + rnd(50);
    Fenwick<> f(n);
    LazySeg s(n);
    dsu d(n + 1);
    Binary_Indexed_Tree<50> F;
    F.Init(n);
    Segment_Tree<50> S;
    S.Init(n);
    Disjoint_Set<50> D;
    D.Init(n);
    vector<long long> a(n + 1), b(n + 1);
    vector<int> c(n + 1);
    iota(c.begin(), c.end(), 0);
    for (int j = 0; j < 100; j++) {
      int l = 1 + rnd(n), r = 1 + rnd(n);
      if (l > r)
        swap(l, r);
      int v = rnd(30);
      a[l] += v;
      f.add(l, v);
      F.Insert(l, v);
      assert(f.query(l, r) ==
             accumulate(a.begin() + l, a.begin() + r + 1, 0LL));
      assert(F.Query(l, r) == f.query(l, r));
      long long total = f.sum(n);
      int k = 1 + rnd(total + 1), pos = 1;
      long long sum = 0;
      while (pos <= n && sum + a[pos] < k)
        sum += a[pos++];
      assert(f.kth(k) == pos && F.Kth(k) == pos);
      v -= 15;
      s.add(l, r, v);
      S.Insert(l, r, v);
      for (int x = l; x <= r; x++)
        b[x] += v;
      l = 1 + rnd(n);
      r = 1 + rnd(n);
      if (l > r)
        swap(l, r);
      auto want = accumulate(b.begin() + l, b.begin() + r + 1, 0LL);
      assert(s.query(l, r) == want && S.Query(l, r) == want);
      bool same = c[l] == c[r];
      assert(d.merge(l, r) == !same && D.Merge(l, r) == !same);
      int old = c[r], to = c[l];
      for (int &x : c)
        if (x == old)
          x = to;
      for (int x = 1; x <= n; x++)
        assert((d.find(x) == d.find(l)) == (c[x] == c[l]));
    }
  }
  RollbackDSU d(5);
  d.merge(1, 2);
  int t = d.snapshot();
  d.merge(2, 3);
  d.merge(4, 5);
  d.rollback(t);
  assert(d.find(1) == d.find(2) && d.find(1) != d.find(3) &&
         d.find(4) != d.find(5));
  for (int it = 0; it < 100; it++) {
    XorBasis b;
    vector<unsigned long long> vals{0};
    for (int i = 0; i < 10; i++) {
      auto x = (unsigned long long)rng();
      b.insert(x);
      int n = vals.size();
      for (int j = 0; j < n; j++)
        vals.push_back(vals[j] ^ x);
    }
    assert(b.query() == *max_element(vals.begin(), vals.end()));
  }
}
void flows() {
  for (int it = 0; it < 1500; it++) {
    int n = 2 + rnd(6), m = rnd(25);
    Dinic d(n);
    Network_Flow<8, 30> D;
    D.Init(n);
    vector<tuple<int, int, int>> es;
    for (int j = 0; j < m; j++) {
      int u = 1 + rnd(n), v = 1 + rnd(n), c = rnd(10);
      es.push_back({u, v, c});
      d.add(u, v, c);
      D.Add_Edge(u, v, c);
    }
    long long best = LLONG_MAX;
    for (int mask = 0; mask < (1 << n); mask++)
      if ((mask & 1) && !(mask >> (n - 1) & 1)) {
        long long sum = 0;
        for (auto [u, v, c] : es)
          if ((mask >> (u - 1) & 1) && !(mask >> (v - 1) & 1))
            sum += c;
        best = min(best, sum);
      }
    assert(d.flow(1, n) == best && D.Max_Flow(1, n) == best);
    assert(d.flow(1, n) == 0 && D.Max_Flow(1, n) == 0);
    vector<long long> balance(n + 1);
    for (int i = 0; i < m; i++) {
      auto [u, v, c] = es[i];
      auto f = d.used(2 * i);
      assert(0 <= f && f <= c);
      balance[u] -= f;
      balance[v] += f;
    }
    assert(balance[1] == -best && balance[n] == best);
    for (int u = 2; u < n; u++)
      assert(balance[u] == 0);
    auto cut = d.cut(1);
    vector<int> seen(n + 1);
    for (int u : cut)
      seen[u] = 1;
    long long sum = 0;
    for (auto [u, v, c] : es)
      if (seen[u] && !seen[v])
        sum += c;
    assert(sum == best);
  }
  // Independent enumeration of feasible integer edge flows on small DAGs.
  for (int it = 0; it < 300; it++) {
    int n = 4, m = 1 + rnd(6);
    MinCostFlow f(n);
    vector<array<int, 4>> es;
    for (int j = 0; j < m; j++) {
      int u = 1 + rnd(3), v = u + 1 + rnd(n - u), c = rnd(3), w = rnd(9) - 4;
      es.push_back({u, v, c, w});
      f.add(u, v, c, w);
    }
    int bestf = -1;
    long long bestc = LLONG_MAX;
    vector<int> bal(n + 1);
    function<void(int, long long)> dfs = [&](int i, long long cost) {
      if (i == m) {
        if (bal[2] || bal[3] || bal[1] + bal[4])
          return;
        int flow = bal[4];
        if (flow > bestf) {
          bestf = flow;
          bestc = cost;
        } else if (flow == bestf)
          bestc = min(bestc, cost);
        return;
      }
      auto [u, v, c, w] = es[i];
      for (int x = 0; x <= c; x++) {
        bal[u] -= x;
        bal[v] += x;
        dfs(i + 1, cost + 1LL * x * w);
        bal[u] += x;
        bal[v] -= x;
      }
    };
    dfs(0, 0);
    auto [got, cost] = f.flow(1, n);
    assert(got == bestf && cost == bestc);
  }
}
void graphs() {
  for (int it = 0; it < 500; it++) {
    int n = 2 + rnd(7);
    SCC s(n);
    Dijkstra d(n);
    vector<vector<long long>> a(n + 1, vector<long long>(n + 1, 1000000));
    for (int i = 1; i <= n; i++)
      a[i][i] = 0;
    for (int j = 0; j < 25; j++) {
      int u = 1 + rnd(n), v = 1 + rnd(n), w = rnd(20);
      s.add(u, v);
      d.add(u, v, w);
      a[u][v] = min(a[u][v], (long long)w);
    }
    for (int k = 1; k <= n; k++)
      for (int i = 1; i <= n; i++)
        for (int j = 1; j <= n; j++)
          a[i][j] = min(a[i][j], a[i][k] + a[k][j]);
    s.run();
    d.run(1);
    for (int i = 1; i <= n; i++) {
      assert(d.dis[i] == (a[1][i] < 1000000 ? a[1][i] : Dijkstra::inf));
      for (int j = 1; j <= n; j++)
        assert((s.bel[i] == s.bel[j]) ==
               (a[i][j] < 1000000 && a[j][i] < 1000000));
    }
    TwoSAT sat(n);
    vector<array<int, 4>> cs;
    for (int j = 0; j < 20; j++) {
      int x = 1 + rnd(n), y = 1 + rnd(n), b = rnd(2), c = rnd(2);
      sat.add(x, b, y, c);
      cs.push_back({x, b, y, c});
    }
    bool ok = false;
    for (int mask = 0; mask < (1 << n); mask++) {
      bool good = true;
      for (auto [x, b, y, c] : cs)
        good &= ((mask >> (x - 1) & 1) == b) || ((mask >> (y - 1) & 1) == c);
      ok |= good;
    }
    assert(sat.solve() == ok);
    if (ok)
      for (auto [x, b, y, c] : cs)
        assert(sat.ans[x] == b || sat.ans[y] == c);
    BipartiteMatching bm(n, n);
    vector<vector<int>> adj(n + 1);
    for (int j = 0; j < 20; j++) {
      int u = 1 + rnd(n), v = 1 + rnd(n);
      bm.add(u, v);
      adj[u].push_back(v);
    }
    function<int(int, int)> search = [&](int u, int mask) {
      if (u > n)
        return 0;
      int ans = search(u + 1, mask);
      for (int v : adj[u])
        if (!(mask >> (v - 1) & 1))
          ans = max(ans, 1 + search(u + 1, mask | (1 << (v - 1))));
      return ans;
    };
    assert(bm.solve() == search(1, 0));
    HLD h(n);
    vector<int> par(n + 1);
    par[1] = 1;
    for (int u = 2; u <= n; u++) {
      par[u] = 1 + rnd(u - 1);
      h.add(par[u], u);
    }
    h.build();
    for (int u = 1; u <= n; u++)
      for (int v = 1; v <= n; v++) {
        set<int> ancestors;
        int x = u;
        while (x != 1) {
          ancestors.insert(x);
          x = par[x];
        }
        ancestors.insert(1);
        x = v;
        while (!ancestors.count(x))
          x = par[x];
        assert(h.lca(u, v) == x);
        int length = 0;
        h.path(u, v, [&](int l, int r) { length += r - l + 1; });
        assert(length == h.dep[u] + h.dep[v] - 2 * h.dep[x] + 1);
      }
  }
}
void strings() {
  for (int it = 0; it < 1000; it++) {
    string s;
    int n = rnd(35);
    for (int i = 0; i < n; i++)
      s += 'a' + rnd(3);
    auto z = z_function(s);
    assert(z == Z_Function(s));
    auto p = prefix_function(s);
    assert(p == Prefix_Function(s));
    auto [odd, even] = manacher(s);
    assert(manacher(s) == Manacher(s));
    set<string> sub;
    SuffixAutomaton sam;
    for (char c : s)
      sam.extend(c - 'a');
    for (int i = 0; i < n; i++) {
      int k = 0;
      while (i + k < n && s[k] == s[i + k])
        k++;
      assert(z[i] == k);
      int want = 0;
      for (k = 1; k <= i; k++)
        if (s.substr(0, k) == s.substr(i - k + 1, k))
          want = k;
      assert(p[i] == want);
      k = 1;
      while (i - k >= 0 && i + k < n && s[i - k] == s[i + k])
        k++;
      assert(odd[i] == k);
      k = 0;
      while (i - k - 1 >= 0 && i + k < n && s[i - k - 1] == s[i + k])
        k++;
      assert(even[i] == k);
      for (int j = i; j < n; j++)
        sub.insert(s.substr(i, j - i + 1));
    }
    assert(sam.distinct() == (long long)sub.size());
    SuffixArray sa(s);
    vector<int> order(n);
    iota(order.begin(), order.end(), 0);
    sort(order.begin(), order.end(),
         [&](int a, int b) { return s.substr(a) < s.substr(b); });
    assert(sa.sa == order);
    for (int i = 1; i < n; i++) {
      int k = 0;
      while (order[i] + k < n && order[i - 1] + k < n &&
             s[order[i] + k] == s[order[i - 1] + k])
        k++;
      assert(sa.lcp[i] == k);
    }
    if (n) {
      string best = s;
      for (int k = 1; k < n; k++)
        best = min(best, s.substr(k) + s.substr(0, k));
      int k = minimum_rotation(s);
      assert(k == Minimum_Rotation(s));
      assert(s.substr(k) + s.substr(0, k) == best);
    }
    AhoCorasick ac;
    vector<string> ts;
    vector<int> ids;
    for (int j = 0; j < 5; j++) {
      string t;
      for (int k = 0, len = 1 + rnd(5); k < len; k++)
        t += 'a' + rnd(3);
      ts.push_back(t);
      ids.push_back(ac.add(t));
    }
    ac.build();
    auto cnt = ac.count(s);
    for (int j = 0; j < 5; j++) {
      vector<int> want;
      for (int i = 0; i + (int)ts[j].size() <= n; i++)
        if (s.substr(i, ts[j].size()) == ts[j])
          want.push_back(i);
      assert(kmp_match(s, ts[j]) == want);
      assert(Kmp_Match(s, ts[j]) == want);
      assert(cnt[ids[j]] == (long long)want.size());
    }
  }
}
void math_test() {
  LinearSieve s(10000);
  for (int n = 1; n <= 10000; n++) {
    bool p = n >= 2;
    for (int j = 2; j * j <= n; j++)
      if (n % j == 0)
        p = false;
    assert(NumberTheory::prime(n) == p);
    if (n <= 300) {
      int phi = 0;
      for (int j = 1; j <= n; j++)
        phi += gcd(j, n) == 1;
      assert(s.phi[n] == phi);
    }
  }
  PollardRho rho;
  for (int i = 0; i < 100; i++) {
    unsigned long long n = 1 + (unsigned long long)rng() * rng();
    auto a = rho.factor(n);
    __uint128_t prod = 1;
    for (auto p : a) {
      assert(NumberTheory::prime(p));
      prod *= p;
    }
    assert(prod == n);
  }
  for (int n = 0; n < 20; n++)
    for (int m = 1; m < 15; m++)
      for (int a = -15; a < 15; a++)
        for (int b = -15; b < 15; b++) {
          long long ans = 0;
          for (int i = 0; i < n; i++)
            ans += (long long)floor((long double)(a * i + b) / m);
          assert(NumberTheory::floor_sum(n, m, a, b) == ans);
        }
  for (int m = 1; m < 30; m++)
    for (int n = 1; n < 30; n++)
      for (int j = 0; j < 5; j++) {
        long long r = rnd(m), b = rnd(n), R = r, M = m, want = -1;
        for (int k = 0; k < lcm(m, n); k++)
          if (k % m == r && k % n == b) {
            want = k;
            break;
          }
        bool ok = NumberTheory::crt(R, M, b, n);
        assert(ok == (want != -1));
        if (ok)
          assert(R == want && M == lcm(m, n));
      }
  using P = Polynomial;
  for (int it = 0; it < 100; it++) {
    int n = 1 + rnd(50), m = 1 + rnd(50);
    P::Poly a(n), b(m), c(n + m - 1);
    for (auto &x : a)
      x = rng();
    for (auto &x : b)
      x = rng();
    for (int i = 0; i < n; i++)
      for (int j = 0; j < m; j++)
        c[i + j] = c[i + j] + a[i] * b[j];
    auto d = P::multiply(a, b);
    for (int i = 0; i < n + m - 1; i++)
      assert(c[i].v == d[i].v);
    a[0] = 1;
    auto inv = P::inverse(a, n);
    d = P::multiply(a, inv);
    assert(d[0].v == 1);
    for (int i = 1; i < n; i++)
      assert(d[i].v == 0);
    auto back = P::exp(P::log(a, n), n);
    for (int i = 0; i < n; i++)
      assert(back[i].v == a[i].v);
    P::Poly f{0, 1};
    for (int i = 2; i < 100; i++)
      f.push_back(f[i - 1] + f[i - 2]);
    auto rec = P::berlekamp_massey(f);
    for (int i = 0; i < 100; i++)
      assert(P::recurrence({0, 1}, rec, i).v == f[i].v);
  }
}
void geometry() {
  using G = IntegerGeometry;
  using Pt = G::Point;
  for (int it = 0; it < 1000; it++) {
    vector<Pt> p;
    for (int j = 0, n = rnd(20); j < n; j++)
      p.push_back({rnd(21) - 10, rnd(21) - 10});
    auto h = G::hull(p);
    __int128 best = 0;
    for (auto a : p)
      for (auto b : p)
        best = max(best, G::dist2(a, b));
    assert(G::diameter2(h) == best);
    for (auto a : p)
      assert(G::contains(h, a));
    for (int j = 0; j < 20; j++) {
      Pt a{rnd(25) - 12, rnd(25) - 12};
      assert(G::contains(h, a) == G::convex_contains(h, a));
    }
  }
  for (int it = 0; it < 1000; it++) {
    auto pt = []() {
      return Pt{(long long)rng() * 400 - 800000000000LL,
                (long long)rng() * 400 - 800000000000LL};
    };
    Pt a = pt(), b = pt(), c = pt();
    cpp_int x = (cpp_int(b.x) - a.x) * (cpp_int(c.y) - a.y) -
                (cpp_int(b.y) - a.y) * (cpp_int(c.x) - a.x);
    assert(G::sign(G::cross(a, b, c)) == ((x > 0) - (x < 0)));
  }
  assert(G::intersect({0, 0}, {0, 0}, {-1, 0}, {1, 0}));
  assert(!G::intersect({0, 0}, {0, 0}, {1, 0}, {2, 0}));
  RealGeometry g;
  using R = RealGeometry;
  R::Circle a{{0, 0}, 1}, b{{2, 0}, 1};
  assert(g.circles(a, b).kind == R::Kind::one);
  assert(g.circles(a, a).kind == R::Kind::infinite);
  assert(g.line_circle({-2, 1}, {2, 1}, a).kind == R::Kind::one);
  assert(fabsl(g.overlap(a, a) - acosl(-1.L)) < 1e-12L);
  for (int it = 0; it < 1000; it++) {
    long double d = (1 + rnd(1999)) / 1000.L;
    R::Circle b{{d, 0}, 1};
    auto r = g.circles(a, b);
    assert(r.kind == R::Kind::two);
    for (auto p : r.p) {
      assert(fabsl(R::norm(p - a.o) - 1) < 1e-10L);
      assert(fabsl(R::norm(p - b.o) - 1) < 1e-10L);
    }
  }
}
int main() {
  structures();
  cout << "structures PASS\n";
  flows();
  cout << "flows PASS\n";
  graphs();
  cout << "graphs PASS\n";
  strings();
  cout << "strings PASS\n";
  math_test();
  cout << "math PASS\n";
  geometry();
  cout << "geometry PASS\n";
}
