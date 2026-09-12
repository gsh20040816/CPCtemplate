#include <cassert>
#include <vector>
using namespace std;

template <int N> struct Lucas_Theorem
{
    int mod;
    int fac[N + 1], ifac[N + 1];

    void Init(int p)
    {
        assert(2 <= p && p <= N);
        mod = p;
        fac[0] = 1;
        for ( int i = 1; i < p; i++ )
            fac[i] = 1LL * fac[i - 1] * i % p;
        long long a = fac[p - 1], r = 1;
        for ( int e = p - 2; e; e >>= 1 )
        {
            if ( e & 1 )
                r = r * a % p;
            a = a * a % p;
        }
        ifac[p - 1] = r;
        for ( int i = p - 1; i; i-- )
            ifac[i - 1] = 1LL * ifac[i] * i % p;
    }

    int Choose(unsigned long long n, unsigned long long k) const
    {
        if ( k > n )
            return 0;
        long long answer = 1;
        while ( n || k )
        {
            int a = n % mod, b = k % mod;
            if ( b > a )
                return 0;
            answer = answer * fac[a] % mod;
            answer = answer * ifac[b] % mod;
            answer = answer * ifac[a - b] % mod;
            n /= mod;
            k /= mod;
        }
        return answer;
    }
};

#include <iostream>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t;
    cin >> t;
    while ( t-- )
    {
        unsigned long long n, m;
        int p;
        cin >> n >> m >> p;
        static Lucas_Theorem<100000> solver;
        solver.Init(p);
        cout << solver.Choose(n + m, n) << '\n';
    }
    return 0;
}
