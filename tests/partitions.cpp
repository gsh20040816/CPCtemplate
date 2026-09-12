#include "../src/compact/partitions.hpp"
#include "../src/classic/partitions.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <climits>
#include <iostream>
using boost::multiprecision::cpp_int;

int main()
{
    vector<cpp_int> exact(1001);
    exact[0] = 1;
    for (int part = 1; part <= 1000; part++)
        for (int s = part; s <= 1000; s++)
            exact[s] += exact[s-part];
    for (int mod : {1,2,6,97,1000000007,INT_MAX})
    {
        Partitions a(1000,mod);
        Integer_Partitions b(1000,mod);
        for (int n = 0; n <= 1000; n++)
        {
            int expected = (exact[n]%mod).convert_to<int>();
            assert(a.p[n] == expected && b.p[n] == expected);
            assert(a.limited(n,INT_MAX) == expected);
            assert(b.Limited(n,INT_MAX) == expected);
        }
        for (int k = 0; k <= 101; k++)
        {
            vector<int> dp(101);
            dp[0] = 1%mod;
            for (int part = 1; part <= 100; part++)
            {
                vector<int> next(101);
                for (int s = 0; s <= 100; s++)
                    for (int copies = 0; copies <= k && s+copies*part <= 100; copies++)
                    {
                        int t = s+copies*part;
                        next[t] = (next[t]+1LL*dp[s])%mod;
                    }
                dp = next;
            }
            for (int n = 0; n <= 100; n++)
            {
                assert(a.limited(n,k) == dp[n]);
                assert(b.Limited(n,k) == dp[n]);
            }
        }
    }
    Partitions a(100000,1000000007);
    Integer_Partitions b(100000,1000000007);
    assert(a.p == b.p);
    assert(a.limited(100000,0) == 0 && b.Limited(100000,0) == 0);
    assert(a.limited(100000,100000) == a.p[100000]);
    assert(b.Limited(100000,100000) == b.p[100000]);
    assert(Partitions(0,1).p[0] == 0);
    assert(Integer_Partitions(0,1).Limited(0,0) == 0);
    cout << "Partitions dual exact coin DP, bounded-multiplicity enumeration, composite moduli and n=100000 boundaries PASS\n";
}
