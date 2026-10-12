#include "../src/compact/static_mod64.hpp"
#include <boost/multiprecision/cpp_int.hpp>
using B = boost::multiprecision::cpp_int;
using U = uint64_t;
long long checks = 0;
void require(bool ok)
{
    if (!ok)
        throw runtime_error("StaticMod64 mismatch at " + to_string(checks));
    checks++;
}
U power(B a, U n, U p)
{
    B r = 1 % p;
    while (n)
    {
        if (n & 1)
            r = r * a % p;
        a = a * a % p;
        n >>= 1;
    }
    return r.convert_to<U>();
}
template <U P> void check(U a, U b, bool big)
{
    using Z = StaticMod64<P>;
    Z x(a), y(b);
    B aa = a, bb = b, pp = P;
    require(x.v == a && y.v == b);
    require((x + y).v == ((aa + bb) % pp).convert_to<U>());
    require((x - y).v == ((aa + pp - bb) % pp).convert_to<U>());
    require((x * y).v == (aa * bb % pp).convert_to<U>());
    require((-x).v == ((pp - aa) % pp).convert_to<U>());
    require((x == y) == (a == b));
    Z t = x;
    t += t;
    require(t.v == (2 * aa % pp).convert_to<U>());
    t = x;
    t -= t;
    require(t.v == 0);
    t = x;
    t *= t;
    require(t.v == (aa * aa % pp).convert_to<U>());
    auto inv = y.try_inv();
    require(bool(inv) == (gcd(b,P) == 1));
    if (inv)
    {
        require(bb * inv->v % pp == 1 % P);
        require((x / y * y).v == a);
        t = y;
        t /= t;
        require(t.v == 1 % P);
    }
    if (big)
        require(x.pow(UINT64_MAX).v == power(aa, UINT64_MAX, P));
}
template <U P> void small()
{
    for (U a = 0; a < P; a++)
        for (U b = 0; b < P; b++)
            check<P>(a,b,false);
    if constexpr (P > 1)
        small<P-1>();
}
template <U P> void large()
{
    using Z = StaticMod64<P>;
    mt19937_64 rng(P);
    require(Z().v == 0);
    for (long long x : {LLONG_MIN,LLONG_MIN + 1,-1LL,0LL,1LL,LLONG_MAX})
        require(Z(x).v == ((B(x)%P+P)%P).convert_to<U>());
    for (U x : {U(0),U(1),P-1,P,UINT64_MAX})
        require(Z(x).v == x % P);
    vector<U> edge{0,1%P,P/2,P-1};
    for (U a : edge)
    {
        for (U b : edge)
            check<P>(a,b,true);
        for (U k : {U(0),U(1),P-1,U(1)<<63,UINT64_MAX})
            require(Z(a).pow(k).v == power(B(a),k,P));
    }
    for (int i = 0; i < 10000; i++)
        check<P>(rng()%P,rng()%P,i<100);
}
int main()
{
    small<40>();
    large<1>();
    large<2>();
    large<998244353>();
    large<4294967296ULL>();
    large<1000000000000000003ULL>();
    large<9223372036854775783ULL>();
    large<9223372036854775808ULL>();
    large<18446744073709551557ULL>();
    large<18446744073709551614ULL>();
    large<18446744073709551615ULL>();
    cout << checks << " Boost integer and unit-inverse certificate checks PASS\n";
}
