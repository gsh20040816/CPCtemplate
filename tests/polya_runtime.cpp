// Local performance experiment; not an additional contest template.
#include <bits/stdc++.h>
#include "../src/compact/polya.hpp"
using namespace std;

vector<int> sieve()
{
    vector<int> p;
    vector<bool> composite(31624);
    for (int i = 2; i <= 31623; i++)
    {
        if (composite[i]) continue;
        p.push_back(i);
        for (int j = i * i; j <= 31623; j += i) composite[j] = true;
    }
    return p;
}

long long evaluate(int n, const vector<int> &primes, int mode)
{
    if (mode == 0) return necklace_colorings(n, n, 1000000007);
    vector<pair<int, int>> factors;
    int x = n;
    for (int p : primes)
    {
        if (p > x / p) break;
        if (x % p != 0) continue;
        int k = 0;
        while (x % p == 0)
        {
            x /= p;
            k++;
        }
        factors.push_back({p, k});
    }
    if (x > 1) factors.push_back({x, 1});
    BurnsideAverage avg(n, 1000000007);
    long long sum = 0;
    auto power = [](long long a, int k)
    {
        long long v = 1;
        while (k)
        {
            if (k & 1) v = v * a % 1000000007;
            a = a * a % 1000000007;
            k >>= 1;
        }
        return v;
    };
    auto add = [&](int d, int phi)
    {
        if (mode == 3) sum = (sum + power(n, n / d) * phi) % 1000000007;
        else avg.add(avg.power(n, n / d), phi);
    };
    if (mode == 1)
    {
        auto divisor = [&](int d)
        {
            int phi = d;
            for (auto [p, k] : factors)
            {
                if (d % p == 0) phi = phi / p * (p - 1);
            }
            add(d, phi);
        };
        for (int d = 1; d <= n / d; d++)
        {
            if (n % d) continue;
            divisor(d);
            if (d != n / d) divisor(n / d);
        }
    }
    else
    {
        auto dfs = [&](auto &&self, int i, int d, int phi) -> void
        {
            if (i == int(factors.size()))
            {
                add(d, phi);
                return;
            }
            self(self, i + 1, d, phi);
            auto [p, k] = factors[i];
            for (int e = 1; e <= k; e++)
            {
                d *= p;
                phi *= e == 1 ? p - 1 : p;
                self(self, i + 1, d, phi);
            }
        };
        dfs(dfs, 0, 1, 1);
    }
    if (mode == 3) return sum * power(n, 1000000005) % 1000000007;
    return avg.result();
}

int main(int argc, char **argv)
{
    int mode = stoi(argv[1]);
    vector<int> input;
    int n;
    while (cin >> n) input.push_back(n);
    auto start = chrono::steady_clock::now();
    auto primes = mode ? sieve() : vector<int>{};
    vector<long long> answers;
    for (int x : input) answers.push_back(evaluate(x, primes, mode));
    auto finish = chrono::steady_clock::now();
    cerr << chrono::duration<double, milli>(finish - start).count() << '\n';
    for (auto x : answers) cout << x << '\n';
}
