#include "../src/compact/fps_functions.hpp"
#include "../src/compact/polynomial.hpp"
#include <iostream>
using F = FpsFunctions;
using Z = F::Z;
using V = F::Poly;
const long long p = 998244353;
long long power(long long a, long long e)
{
    long long r = 1;
    for (; e; e >>= 1, a = a * a % p) if (e & 1) r = r * a % p;
    return r;
}
void same(const V &a, const vector<long long> &b)
{
    assert(a.size() == b.size());
    for (int i = 0; i < (int)a.size(); i++) assert(a[i].v == b[i]);
}
int main()
{
    mt19937 rng(216099);
    for (int it = 0; it < 300; it++)
    {
        int n = 1 + rng() % 65, len = 1 + rng() % 100;
        V a(len);
        for (auto &x : a) x = rng() % p;
        a[0] = 1 + rng() % (p - 1);
        auto at = [&](int i) -> long long { return i < len ? a[i].v : 0; };
        vector<long long> inv(n);
        inv[0] = power(at(0), p - 2);
        for (int k = 1; k < n; k++)
        {
            long long sum = 0;
            for (int i = 1; i <= k; i++) sum = (sum + at(i) * inv[k-i]) % p;
            inv[k] = (p-sum) * inv[0] % p;
        }
        same(FpsInverse::inverse(a,n),inv);
        a[0] = 1;
        vector<long long> log(n);
        // a' = a * (log a)': independent triangular coefficient recurrence.
        for (int k = 1; k < n; k++)
        {
            long long sum = 0;
            for (int i = 1; i < k; i++) sum = (sum + i * log[i] % p * at(k-i)) % p;
            log[k] = (k * at(k) % p + p - sum) % p * power(k,p-2) % p;
        }
        same(F::log(a,n),log);
        a[0] = 0;
        vector<long long> exp(n);
        exp[0] = 1;
        // b' = a' * b for b = exp(a), without using log or Newton iteration.
        for (int k = 1; k < n; k++)
        {
            long long sum = 0;
            for (int i = 1; i <= k; i++) sum = (sum + i * at(i) % p * exp[k-i]) % p;
            exp[k] = sum * power(k,p-2) % p;
        }
        same(F::exp(a,n),exp);
        auto d = F::derivative(a), integral = F::integral(a);
        assert(d.size() == a.size()-1 && integral.size() == a.size()+1 && integral[0].v == 0);
        for (int i = 0; i < len; i++)
        {
            assert(integral[i+1].v == at(i)*power(i+1,p-2)%p);
            if (i) assert(d[i-1].v == at(i)*i%p);
        }
    }
    assert(F::derivative({}).empty());
    same(F::integral({}),{0});
    same(F::exp({},5),{1,0,0,0,0});
    int n = 131072;
    same(FpsInverse::inverse({1,p-1},n),vector<long long>(n,1));
    vector<long long> want(n);
    for (int i = 1; i < n; i++) want[i] = p-power(i,p-2);
    same(F::log({1,p-1},n),want);
    long long fac = 1;
    for (int i = 1; i < n; i++) fac = fac*i%p;
    want[n-1] = power(fac,p-2);
    for (int i = n-1; i > 0; i--) want[i-1] = want[i]*i%p;
    same(F::exp({0,1},n),want);
    // Old API returns any supplied prefix value before extrapolating from k terms.
    same(Polynomial::multiply({1,2},{3,4}),{3,10,8});
    assert(Polynomial::recurrence({2,7,99},{3},2).v == 99);
    assert(Polynomial::recurrence({2,7,99},{3},3).v == 54);
    assert(Polynomial::recurrence({12},{},0).v == 12);
    assert(Polynomial::recurrence({12},{},1).v == 0);
    auto c = Polynomial::berlekamp_massey({0,1,1,2,3,5,8,13});
    same(c,{1,1});
    assert(Polynomial::recurrence({0,1},c,20).v == 6765);
    cout << "Separated FPS: independent triangular coefficient recurrences, calculus, 131072-term analytic series and compatibility prefixes PASS\n";
}
