#include <bits/stdc++.h>
#include <cassert>
using namespace std;
#include "../src/compact/good_number_sum.hpp"
long long checks = 0;
void check(bool ok)
{
    if (!ok)
        throw runtime_error("mismatch " + to_string(checks));
    checks++;
}
long long number(const string &s, int l, int r)
{
    long long result = 0;
    for (int i = l; i < r; i++)
        result = result * 10 + s[i] - '0';
    return result;
}
void verify(const string &s, const string &x, bool exists)
{
    for (unsigned long long mod : {1ULL, 7ULL, (1ULL << 61) - 1})
    {
        auto [l, k, r] = good_number_sum(s, x, mod);
        check((l != -1) == exists);
        if (l != -1)
        {
            check(0 <= l && l < k && k < r && r <= (int)s.size());
            check(number(s, l, k) + number(s, k, r) == stoll(x));
        }
    }
}
int main()
{
    vector<string> targets;
    for (int x = 1; x < 1000; x++)
    {
        string s = to_string(x);
        if (s.find_first_not_of("1234") == string::npos)
            targets.push_back(s);
    }
    for (int n = 0; n <= 7; n++)
        for (int mask = 0; mask < (1 << n); mask++)
        {
            string s(n, '1');
            for (int i = 0; i < n; i++)
                s[i] += (mask >> i) & 1;
            set<long long> sums;
            for (int l = 0; l < n; l++)
                for (int k = l + 1; k < n; k++)
                    for (int r = k + 1; r <= n; r++)
                        sums.insert(number(s, l, k) + number(s, k, r));
            for (const auto &x : targets)
                verify(s, x, sums.count(stoll(x)));
        }
    mt19937 rng(1598);
    for (int trial = 0; trial < 2000; trial++)
    {
        int n = 2 + rng() % 15;
        string s(n, '1');
        for (char &c : s)
            c += rng() % 9;
        set<long long> sums;
        for (int l = 0; l < n; l++)
            for (int k = l + 1; k < n; k++)
                for (int r = k + 1; r <= n; r++)
                    sums.insert(number(s, l, k) + number(s, k, r));
        int chosen = rng() % sums.size();
        string x = to_string(*next(sums.begin(), chosen));
        if (x.find('0') == string::npos)
            verify(s, x, true);
        x = to_string(1 + rng() % 999999);
        if (x.find('0') == string::npos)
            verify(s, x, sums.count(stoll(x)));
    }
    verify("999124554", "99", true);
    cout << checks << " exhaustive existence and forced-collision checks PASS\n";
}
