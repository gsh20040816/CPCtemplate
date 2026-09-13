#include <bits/stdc++.h>
#include <cassert>
namespace isolated
{
#include "../src/compact/number_theory.hpp"
#include "../src/compact/polynomial.hpp"
}
int main()
{
    assert(isolated::NumberTheory::floor_sum(3,2,-1,0) == -2);
    assert(isolated::floor_sum(3,2,-1,0) == -2);
    assert(isolated::NumberTheory::power(5,3,7) == 6);
    assert(isolated::NumberTheory::prime(1000000007));
    long long r=2,m=3;
    assert(isolated::NumberTheory::crt(r,m,3,5) && r==8 && m==15);
    assert(isolated::NumberTheory::inverse(3,7)==5);
    auto c = isolated::Polynomial::berlekamp_massey({0,1,1,2,3,5,8,13});
    assert(c.size() == 2 && c[0].v == 1 && c[1].v == 1);
    assert(isolated::Polynomial::recurrence({0,1},c,20).v == 6765);
    std::cout << "Isolated namespace number theory: legacy floor/BM/recurrence forwarding, arithmetic and CRT certificates PASS\n";
}
