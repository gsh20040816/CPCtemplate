// Independent P5487 fixture: s[n] = sum_{t=1}^k t^n over a prime field.
// Distinct nonzero roots and unit weights make the k-by-k Hankel matrix
// V*V^T nonsingular. Thus the unique minimal polynomial is product(X-t).
#include <bits/stdc++.h>
#include <cassert>
using namespace std;
const int mod = 998244353;

int power(long long a, unsigned long long n)
{
    long long answer = 1;
    while (n)
    {
        if (n & 1) answer = answer * a % mod;
        a = a * a % mod;
        n >>= 1;
    }
    return answer;
}

int main(int argc, char **argv)
{
    assert(argc == 5);
    int k = stoi(argv[1]);
    unsigned long long m = stoull(argv[2]);
    assert(1 <= k && k <= 5000 && m > (unsigned)(2 * k));
    ofstream input(argv[3]), answer(argv[4]);
    input << 2 * k << ' ' << m << '\n';
    vector<int> powers(k, 1);
    for (int i = 0; i < 2 * k; i++)
    {
        long long value = 0;
        for (int t = 1; t <= k; t++)
        {
            value += powers[t - 1];
            powers[t - 1] = 1LL * powers[t - 1] * t % mod;
        }
        input << value % mod << (i + 1 == 2 * k ? '\n' : ' ');
    }
    vector<int> p{1};
    for (int t = 1; t <= k; t++)
    {
        vector<int> q(p.size() + 1);
        for (int j = 0; j < (int)p.size(); j++)
        {
            q[j] = (q[j] + 1LL * (mod - t) * p[j]) % mod;
            q[j + 1] = (q[j + 1] + p[j]) % mod;
        }
        p = move(q);
    }
    for (int j = 1; j <= k; j++)
        answer << (p[k - j] ? mod - p[k - j] : 0) << (j == k ? '\n' : ' ');
    long long nth = 0;
    for (int t = 1; t <= k; t++) nth += power(t, m);
    answer << nth % mod << '\n';
}
