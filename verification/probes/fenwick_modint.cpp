// Regression for the previously recorded compound-assignment compile failure.
#include "../../src/compact/data_structure.hpp"
#include "../../src/compact/number_theory.hpp"
int main() {
  Fenwick<ModInt<998244353>> f(3);
  f.add(1, 2);
  assert(f.sum(3).v == 2);
  return 0;
}
