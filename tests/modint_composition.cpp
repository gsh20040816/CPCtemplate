#include "../src/compact/data_structure.hpp"
#include "../src/compact/number_theory.hpp"

// Independent integer residues; inverses use extended Euclid, not Fermat.
long long norm(__int128 x, int p) {
  x %= p;
  if (x < 0)
    x += p;
  return (long long)x;
}

long long inverse(long long a, int p) {
  long long b = p, x = 1, y = 0;
  while (b) {
    long long q = a / b;
    tie(a, b) = pair{b, a - q * b};
    tie(x, y) = pair{y, x - q * y};
  }
  assert(a == 1);
  return norm(x, p);
}

template <int p> void check() {
  using Z = ModInt<p>;
  mt19937_64 rng(p);
  vector<long long> edge{0,         1,        -1, p - 1, p, -(long long)p,
                         LLONG_MIN, LLONG_MAX};
  for (int it = 0; it < 20000; it++) {
    long long a = it < (int)edge.size() ? edge[it] : (long long)rng();
    long long b =
        it < (int)edge.size() ? edge[edge.size() - 1 - it] : (long long)rng();
    long long x = norm(a, p), y = norm(b, p);
    Z z = a;
    assert(z.v == x);
    assert(&(z += Z(b)) == &z);
    assert(z.v == norm(x + y, p));
    z = a;
    assert(&(z -= Z(b)) == &z);
    assert(z.v == norm(x - y, p));
    z = a;
    assert(&(z *= Z(b)) == &z);
    assert(z.v == norm((__int128)x * y, p));
    if (y) {
      z = a;
      assert(&(z /= Z(b)) == &z);
      assert(z.v == norm((__int128)x * inverse(y, p), p));
    }
    z = a;
    z += z;
    assert(z.v == norm(2 * x, p));
    z = a;
    z -= z;
    assert(z.v == 0);
    z = a;
    z *= z;
    assert(z.v == norm((__int128)x * x, p));
    if (x) {
      z = a;
      z /= z;
      assert(z.v == 1);
    }
    z = a;
    (z += Z(b)) *= Z(b);
    assert(z.v == norm((__int128)(x + y) * y, p));
  }
  Fenwick<Z> empty(0);
  assert(empty.sum(0).v == 0);
  for (int n : {1, 2, 31, 64, 129}) {
    Fenwick<Z> f(n);
    vector<long long> a(n + 1);
    for (int it = 0; it < 3000; it++) {
      int at = 1 + rng() % n;
      long long delta = (long long)rng();
      f.add(at, Z(delta));
      a[at] = norm((__int128)a[at] + delta, p);
      int l = 1 + rng() % n, r = 1 + rng() % n;
      if (l > r)
        swap(l, r);
      long long sum = 0;
      for (int i = l; i <= r; i++)
        sum = norm(sum + a[i], p);
      assert(f.query(l, r).v == sum);
      sum = 0;
      for (int i = 1; i <= n; i++)
        sum = norm(sum + a[i], p);
      assert(f.sum(n).v == sum);
    }
  }
}

int main() {
  check<2>();
  check<998244353>();
  check<2147483647>();
  cout << "ModInt compound assignments, aliasing, Euclid inverse and Fenwick "
          "integer-residue oracle PASS\n";
}
