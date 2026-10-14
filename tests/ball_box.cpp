#include "../src/compact/partitions.hpp"
#include "../src/compact/stirling.hpp"
#include <iostream>
#include <map>
#include <set>

// Independent oracles for the eight balls-into-boxes cases and the bounded-part partition tables.
using Z = ModInt<998244353>;
const int P = 998244353;

// partitions of s into parts no larger than cap, by direct recursion over the largest part
long long brute_parts(int s, int cap)
{
    if (s == 0) return 1;
    long long total = 0;
    for (int first = min(s, cap); first >= 1; first--) total += brute_parts(s - first, first);
    return total;
}

// same count reduced modulo mod with 64-bit sums, independent of the template's loop order
long long brute_mod(int n, int m, long long mod)
{
    vector<vector<long long>> dp(n + 1, vector<long long>(m + 1));
    for (int k = 0; k <= m; k++) dp[0][k] = 1 % mod;
    for (int s = 1; s <= n; s++)
        for (int k = 1; k <= m; k++)
            dp[s][k] = (dp[s][k - 1] + (s >= k ? dp[s - k][k] : 0)) % mod;
    return m ? dp[n][m] : (n == 0 ? 1 % mod : 0);
}

// enumerate all m^n placements and count classes under the chosen equivalence
array<long long, 8> brute_cases(int n, int m)
{
    array<set<vector<int>>, 8> seen;
    long long total = 1;
    for (int i = 0; i < n; i++) total *= m;
    for (long long code = 0; code < total; code++)
    {
        vector<int> f(n);
        long long c = code;
        for (int i = 0; i < n; i++) f[i] = c % m, c /= m;
        vector<int> cnt(m);
        for (int x : f) cnt[x]++;
        bool full = count(cnt.begin(), cnt.end(), 0) == 0;
        // labelled balls, unlabelled boxes: relabel boxes by first use
        vector<int> canon(n), id(m, -1);
        int next = 0;
        for (int i = 0; i < n; i++)
        {
            if (id[f[i]] < 0) id[f[i]] = next++;
            canon[i] = id[f[i]];
        }
        vector<int> sorted_cnt = cnt;
        sort(sorted_cnt.rbegin(), sorted_cnt.rend());
        // 0..3: distinct balls; 4..7: identical balls. Even index allows empty boxes.
        seen[0].insert(f);
        if (full) seen[1].insert(f);
        seen[2].insert(canon);
        if (full) seen[3].insert(canon);
        seen[4].insert(cnt);
        if (full) seen[5].insert(cnt);
        seen[6].insert(sorted_cnt);
        if (full) seen[7].insert(sorted_cnt);
    }
    array<long long, 8> r;
    for (int k = 0; k < 8; k++) r[k] = (long long)seen[k].size();
    return r;
}

array<long long, 8> formula_cases(int n, int m)
{
    Binomial<P> c(n + m + 1);
    auto S = stirling_second_row<P>(n, max(m, 0));
    auto f = parts_at_most(n, m, P);
    Z fact = 1;
    for (int i = 1; i <= m; i++) fact = fact * Z(i);
    Z bell = 0;
    for (int k = 0; k <= m; k++) bell = bell + S[k];
    long long exact = n >= m ? f[n - m] : 0;
    if (m == 0) exact = n == 0;
    return {Z(m).pow(n).v,               // distinct balls, distinct boxes, empty allowed
            (fact * S[m]).v,             // ... no empty box
            bell.v,                      // distinct balls, identical boxes, empty allowed
            S[m].v,                      // ... no empty box
            m ? c.choose(n + m - 1, m - 1).v : (long long)(n == 0),
            m ? c.choose(n - 1, m - 1).v : (long long)(n == 0),
            f[n],                        // identical balls and boxes, at most m parts
            exact};                      // exactly m parts = at most m parts of n-m
}

int main()
{
    long long checks = 0;
    for (int n = 0; n <= 60; n++)
        for (int m = 0; m <= 62; m++)
        {
            auto f = parts_at_most(n, m, P);
            auto g = parts_at_most_fps(n, m);
            assert((int)f.size() == n + 1 && (int)g.size() == n + 1);
            for (int s = 0; s <= n; s++)
            {
                assert(f[s] == brute_parts(s, m) % P);
                assert(g[s].v == f[s]);
                checks++;
            }
        }
    // small modulus and mod = 1
    for (int m : {0, 1, 3, 9})
    {
        auto f = parts_at_most(40, m, 7), one = parts_at_most(40, m, 1);
        for (int s = 0; s <= 40; s++) assert(f[s] == brute_parts(s, m) % 7 && one[s] == 0);
    }
    // moduli near INT_MAX: sums of two residues must not overflow int
    for (int mod : {INT_MAX, INT_MAX - 1, 1 << 30})
        for (int m : {5, 40, 200})
        {
            auto f = parts_at_most(200, m, mod);
            for (int s = 0; s <= 200; s++) assert(f[s] == (long long)(brute_mod(s, m, mod)));
        }
    // large table against the O(nm) recurrence
    for (int m : {1, 2, 17, 300, 3000, 5000})
    {
        auto f = parts_at_most(3000, m, P);
        auto g = parts_at_most_fps(3000, m);
        for (int s = 0; s <= 3000; s++) assert(g[s].v == f[s]);
    }
    for (int n = 0; n <= 7; n++)
        for (int m = 0; m <= 5; m++)
        {
            auto brute = brute_cases(n, m), want = formula_cases(n, m);
            for (int k = 0; k < 8; k++)
            {
                if (brute[k] != want[k])
                {
                    cerr << "case " << k << " n=" << n << " m=" << m << ' ' << brute[k] << ' ' << want[k] << '\n';
                    return 1;
                }
                checks++;
            }
        }
    cout << "Balls and boxes: eight cases n<=7,m<=5 by enumeration, bounded-part tables vs brute partitions "
            "(n<=60), FPS vs recurrence up to 3000 PASS (" << checks << " checks)\n";
}
