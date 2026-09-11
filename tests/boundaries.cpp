#include "../src/classic/data_structure.hpp"
#include "../src/compact/data_structure.hpp"
#include "../src/compact/geometry.hpp"
#include "../src/compact/number_theory.hpp"
#include "../src/compact/string.hpp"
#include <iostream>
int main() {
  std::mt19937 rng(20260919);
  for (int it = 0; it < 500; it++) {
    RollbackDSU a(10);
    Rollback_DSU<10> b;
    b.Init(10);
    XorBasis x;
    Xor_Basis y;
    for (int j = 0; j < 50; j++) {
      int u = 1 + rng() % 10, v = 1 + rng() % 10;
      assert(a.merge(u, v) == b.Merge(u, v));
      if (rng() % 3 == 0) {
        int t = rng() % (a.snapshot() + 1);
        a.rollback(t);
        b.Rollback(t);
      }
      for (int k = 1; k <= 10; k++)
        for (int l = 1; l <= 10; l++)
          assert((a.find(k) == a.find(l)) == (b.Find(k) == b.Find(l)));
      auto z = (unsigned long long)rng() << 32 | rng();
      assert(x.insert(z) == y.Insert(z));
      assert(x.query() == y.Query());
    }
    std::string s;
    for (int j = 0, n = 1 + rng() % 20; j < n; j++)
      s += 'a' + rng() % 3;
    SuffixAutomaton sam;
    for (char c : s)
      sam.extend(c - 'a');
    auto count = sam.counts();
    assert(count == sam.counts());
    for (int i = 0; i < (int)s.size(); i++)
      for (int j = i; j < (int)s.size(); j++) {
        auto t = s.substr(i, j - i + 1);
        int state = 0;
        for (char c : t)
          state = sam.a[state].go[c - 'a'];
        int want = 0;
        for (int k = 0; k + (int)t.size() <= (int)s.size(); k++)
          want += s.substr(k, t.size()) == t;
        assert(count[state] == want);
      }
  }
  for (int it = 0; it < 500; it++) {
    std::string s;
    for (int i = 0, n = 1 + rng() % 30; i < n; i++)
      s += char(rng() % 256);
    std::string want = s;
    for (int i = 1; i < (int)s.size(); i++)
      want = std::min(want, s.substr(i) + s.substr(0, i));
    int k = StringAlgo::rotation(s);
    assert(s.substr(k) + s.substr(0, k) == want);
  }
  Binomial<101> c(100);
  std::vector<int> row{1};
  for (int n = 0; n <= 100; n++) {
    for (int k = -1; k <= n + 1; k++)
      assert(c.choose(n, k).v == (k < 0 || k > n ? 0 : row[k]));
    std::vector<int> next(n + 2);
    for (int k = 0; k <= n; k++) {
      next[k] = (next[k] + row[k]) % 101;
      next[k + 1] = (next[k + 1] + row[k]) % 101;
    }
    row = next;
  }
  using G = IntegerGeometry;
  std::vector<G::Point> polygon{{0, 0}, {4, 0}, {4, 1}, {1, 1}, {1, 4}, {0, 4}};
  assert(G::contains(polygon, {2, 2}) == 0);
  assert(G::contains(polygon, {1, 2}) == 1);
  assert(G::contains(polygon, {0, 0}) == 1);
  std::reverse(polygon.begin(), polygon.end());
  assert(G::contains(polygon, {2, 2}) == 0);
  assert(G::contains(polygon, {1, 2}) == 1);
  assert(NumberTheory::prime(18446744073709551557ULL));
  assert(!NumberTheory::prime(341550071728321ULL));
  assert(!NumberTheory::prime(3825123056546413051ULL));
  long long r = LLONG_MAX - 1, m = LLONG_MAX;
  assert(NumberTheory::crt(r, m, 0, 1) && r == LLONG_MAX - 1);
  std::cout
      << "rollback, basis, SAM counts, binomial, boundary regressions PASS\n";
}
