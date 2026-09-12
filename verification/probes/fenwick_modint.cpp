// Expected compile failure until the compound-assignment compatibility gap is fixed.
#include "../../src/compact/data_structure.hpp"
#include "../../src/compact/number_theory.hpp"
int main()
{
    Fenwick<ModInt<998244353>> f(3);
    f.add(1, 2);
    return f.sum(3).v;
}
