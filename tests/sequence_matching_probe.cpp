#include "../src/compact/order_match.hpp"
#include "../src/compact/string.hpp"
#include <climits>
#include <iostream>
#include <random>
#include <stdexcept>

long long checks = 0, cases = 0;
void require(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("oracle");
}

vector<int> direct(const vector<long long> &s, const vector<long long> &t)
{
    vector<int> ans;
    for (int i = 0; i + (int)t.size() <= (int)s.size(); i++)
    {
        bool ok = true;
        for (int j = 0; j < (int)t.size(); j++)
            for (int k = 0; k < j; k++)
                if ((s[i + j] < s[i + k]) != (t[j] < t[k]) ||
                    (s[i + j] == s[i + k]) != (t[j] == t[k]))
                    ok = false;
        if (ok) ans.push_back(i);
    }
    return ans;
}

void match(const vector<long long> &s, const vector<long long> &t)
{
    auto a = s, b = t;
    require(order_match(s, t) == direct(s, t));
    require(a == s && b == t);
    cases++;
}

template <class S>
void palindrome(const S &s)
{
    int n = s.size();
    vector<int> odd(n), even(n);
    // Enumerate substrings and compare mirrored pairs, without radius reuse.
    for (int l = 0; l < n; l++)
        for (int r = l; r < n; r++)
        {
            bool ok = true;
            for (int i = l; i <= r; i++)
                if (s[i] != s[l + r - i]) ok = false;
            if (ok)
            {
                int len = r - l + 1;
                if (len % 2) odd[(l + r) / 2] = max(odd[(l + r) / 2], len / 2 + 1);
                else even[(l + r + 1) / 2] = max(even[(l + r + 1) / 2], len / 2);
            }
        }
    auto before = s;
    auto got = manacher(s);
    require(got.first == odd && got.second == even);
    require(s == before);
    cases++;
}

vector<vector<long long>> sequences(int maxn)
{
    vector<vector<long long>> all;
    for (int n = 0, lim = 1; n <= maxn; n++, lim *= 3)
        for (int mask = 0; mask < lim; mask++)
        {
            vector<long long> a(n);
            int x = mask;
            for (auto &v : a)
            {
                v = x % 3 - 1;
                x /= 3;
            }
            all.push_back(a);
        }
    return all;
}

int main()
{
    try
    {
        auto small = sequences(4);
        for (auto &s : sequences(6))
            for (auto &t : small)
                if (!t.empty()) match(s, t);
        for (auto &s : sequences(8))
        {
            palindrome(s);
            palindrome(vector<int>(s.begin(), s.end()));
            string bytes;
            for (auto x : s) bytes += char(x == -1 ? 0 : x == 0 ? 128 : 255);
            palindrome(bytes);
        }
        mt19937_64 rng(6080);
        vector<long long> alphabet{LLONG_MIN, LLONG_MAX, -1, 0, 1, 256, 1LL << 40};
        for (int run = 0; run < 3000; run++)
        {
            vector<long long> s(rng() % 35), t(1 + rng() % 18);
            for (auto &x : s) x = alphabet[rng() % alphabet.size()];
            for (auto &x : t) x = alphabet[rng() % alphabet.size()];
            if (run % 3 == 0 && s.size() >= t.size())
                copy_n(s.begin() + rng() % (s.size() - t.size() + 1), t.size(), t.begin());
            match(s, t);
            palindrome(s);
        }
        int n = 1000000, m = 25000;
        vector<long long> s(n), t(m);
        vector<int> want(n - m + 1);
        iota(want.begin(), want.end(), 0);
        for (int mode = 0; mode < 3; mode++)
        {
            for (int i = 0; i < n; i++) s[i] = mode == 0 ? LLONG_MIN : mode == 1 ? i : -i;
            for (int i = 0; i < m; i++) t[i] = mode == 0 ? LLONG_MAX : mode == 1 ? i + 10LL : -i - 20LL;
            require(order_match(s, t) == want);
            cases++;
        }
        fill(s.begin(), s.end(), LLONG_MIN);
        auto [odd, even] = manacher(s);
        for (int i = 0; i < n; i++)
        {
            require(odd[i] == min(i + 1, n - i));
            require(even[i] == min(i, n - i));
        }
        for (int i = 0; i < n; i++) s[i] = i;
        auto a = manacher(s);
        for (int i = 0; i < n; i++) require(a.first[i] == 1 && a.second[i] == 0);
        for (int i = 0; i < n; i++) s[i] = i % 2 ? LLONG_MIN : LLONG_MAX;
        auto b = manacher(s);
        for (int i = 0; i < n; i++)
            require(b.first[i] == min(i + 1, n - i) && b.second[i] == 0);
        cases += 3;
        cout << "PASS " << cases << " cases " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
