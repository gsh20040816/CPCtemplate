#include "../src/compact/mod64.hpp"
#include "../src/compact/prime64.hpp"
#include "../src/compact/mod_inverse.hpp"
#include "../src/compact/crt_merge.hpp"
#include "../src/compact/floor_sum.hpp"
#include <boost/multiprecision/cpp_int.hpp>
using boost::multiprecision::cpp_int;
int main()
{
    mt19937_64 rng(56291);
    for (int it = 0; it < 3000; it++)
    {
        unsigned long long a = rng(), b = rng(), m = rng() | 1;
        assert(cpp_int(Mod64::mul(a,b,m)) == cpp_int(a)*b%m);
        assert(cpp_int(Mod64::power(a,b,m)) == boost::multiprecision::powm(cpp_int(a),cpp_int(b),cpp_int(m)));
    }
    assert(Mod64::power(ULLONG_MAX,0,1) == 0);
    for (unsigned n = 0; n < 30000; n++)
    {
        bool prime = n >= 2;
        for (unsigned d = 2; d*d <= n; d++) if (n%d == 0) prime = false;
        assert(Prime64::prime(n) == prime);
    }
    using I = __int128_t;
    vector<I> edge{0,1,2,LLONG_MAX,I(1)<<63};
    for (I a : edge) for (I b : edge)
    {
        I x,y,g = extended_gcd(a,b,x,y);
        assert(cpp_int(a)*cpp_int(x)+cpp_int(b)*cpp_int(y)==cpp_int(g));
        cpp_int u=a,v=b;
        while (v != 0) { cpp_int r=u%v; u=v; v=r; }
        assert(cpp_int(g)==u);
    }
    for (long long m = 1; m <= 70; m++) for (long long a = -100; a <= 100; a++)
    {
        long long want=-1;
        for (long long x=0; x<m; x++) if ((a*x%m+m)%m==1%m) want=x;
        assert(mod_inverse(a,m)==want);
    }
    for (long long m=1; m<=12; m++) for (long long n=1; n<=12; n++)
        for (long long a=0; a<m; a++) for (long long b=0; b<n; b++)
        {
            long long r=a,period=m,want=-1;
            for (long long x=0; x<lcm(m,n); x++) if (x%m==a && x%n==b) { want=x; break; }
            assert(crt_merge(r,period,b,n)==(want!=-1));
            if (want!=-1) assert(r==want && period==lcm(m,n));
        }
    for (int it=0; it<3000; it++)
    {
        long long n=rng()%40,m=1+rng()%30,a=(long long)(rng()%101)-50,b=(long long)(rng()%101)-50;
        long long want=0;
        for (int i=0; i<n; i++)
        {
            long long t=a*i+b,q=t/m;
            if (t%m<0) q--;
            want+=q;
        }
        assert(floor_sum(n,m,a,b)==want);
    }
    cout << "Separated number theory: cpp_int modular oracle, trial primes, Bezout certificates, exhaustive residues and signed floor sums PASS\n";
}
