#include "../src/compact/algebra.hpp"
#include "../src/compact/polynomial.hpp"
#include <iostream>
int main() {
  using A = LinearAlgebra<101>;
  using Z = A::Z;
  std::mt19937 rng(20260913);
  for (int it = 0; it < 300; it++) {
    int n = 1 + rng() % 3, m = 1 + rng() % 4;
    A::Matrix a(m, std::vector<Z>(n + 1));
    for (auto &row : a)
      for (auto &x : row)
        x = rng() % 101;
    auto ans = A::solve(a, n);
    if (ans.consistent) {
      for (auto row : a) {
        Z got = 0;
        for (int j = 0; j < n; j++)
          got = got + row[j] * ans.particular[j];
        assert(got.v == row[n].v);
      }
      for (auto v : ans.kernel)
        for (auto row : a) {
          Z got = 0;
          for (int j = 0; j < n; j++)
            got = got + row[j] * v[j];
          assert(got.v == 0);
        }
      assert((int)ans.kernel.size() == n - ans.rank);
    }
    // Brute force over a small field for an independent consistency oracle.
    using B = LinearAlgebra<3>;
    B::Matrix b(m, std::vector<B::Z>(n + 1));
    for (auto &row : b)
      for (auto &x : row)
        x = rng() % 3;
    bool ok = false;
    int lim = 1;
    for (int j = 0; j < n; j++)
      lim *= 3;
    for (int mask = 0; mask < lim; mask++) {
      int t = mask;
      std::vector<int> x(n);
      for (auto &v : x) {
        v = t % 3;
        t /= 3;
      }
      bool good = true;
      for (auto row : b) {
        int got = 0;
        for (int j = 0; j < n; j++)
          got += row[j].v * x[j];
        good &= (got % 3 == row[n].v);
      }
      ok |= good;
    }
    assert(B::solve(b, n).consistent == ok);
    A::Matrix mat(n, std::vector<Z>(n));
    for (auto &row : mat)
      for (auto &x : row)
        x = rng();
    std::vector<int> p(n);
    std::iota(p.begin(), p.end(), 0);
    Z want = 0;
    do {
      Z prod = 1;
      int inv = 0;
      for (int i = 0; i < n; i++) {
        prod = prod * mat[i][p[i]];
        for (int j = 0; j < i; j++)
          inv += p[j] > p[i];
      }
      want = want + (inv % 2 ? Z(0) - prod : prod);
    } while (std::next_permutation(p.begin(), p.end()));
    assert(A::determinant(mat).v == want.v);
  }
  for (int m = 1; m <= 80; m++)
    for (int a = 0; a < m; a++)
      for (int b = 0; b < m; b++) {
        int x = 1 % m, want = -1;
        std::vector<int> seen(m);
        for (int i = 0; !seen[x]; i++) {
          if (x == b) {
            want = i;
            break;
          }
          seen[x] = 1;
          x = x * a % m;
        }
        assert(DiscreteLog::solve(a, b, m) == want);
      }
  LinearSieve s(20000);
  DuJiao d(100);
  long long mu = 0, phi = 0;
  for (int i = 1; i <= 20000; i++) {
    mu += s.mu[i];
    phi += s.phi[i];
    if (i % 19 == 0) {
      assert(d.mertens(i) == mu);
      assert(d.totient_sum(i) == phi);
    }
  }
  for (int n = 1; n <= 8; n++) {
    std::vector<std::pair<int, int>> es;
    for (int i = 0; i < n; i++)
      for (int j = i + 1; j < n; j++)
        es.push_back({i, j});
    assert(A::spanning_trees(n, es).v == (n == 1 ? 1 : Z(n).pow(n - 2).v));
  }
  using P = Polynomial;
  for (char op : std::string("^|&"))
    for (int it = 0; it < 50; it++) {
      int n = 1 << (rng() % 6);
      P::Poly a(n), b(n), want(n);
      for (auto &x : a)
        x = rng();
      for (auto &x : b)
        x = rng();
      for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
          int k = op == '^' ? (i ^ j) : op == '|' ? (i | j) : (i & j);
          want[k] = want[k] + a[i] * b[j];
        }
      P::fwt(a, op);
      P::fwt(b, op);
      for (int i = 0; i < n; i++)
        a[i] = a[i] * b[i];
      P::fwt(a, op, true);
      for (int i = 0; i < n; i++)
        assert(a[i].v == want[i].v);
    }
  std::cout << "algebra, discrete log, Du Jiao, FWT PASS\n";
}
