#include "../src/compact/exkmp.hpp"
#include <iostream>
#include <random>
#include <stdexcept>
using namespace std;
long long checks = 0, cases = 0;

void require(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("oracle");
}

int lcp(const string &a, int i, const string &b)
{
    int j = 0;
    while (i + j < (int)a.size() && j < (int)b.size() && a[i + j] == b[j])
        j++;
    return j;
}

void one(const string &s)
{
    cases++;
    int n = s.size();
    auto p = prefix_function(s);
    auto z = z_function(s);
    auto [odd, even] = manacher(s);
    require(p.size() == s.size() && z.size() == s.size());
    require(odd.size() == s.size() && even.size() == s.size());
    for (int i = 0; i < n; i++)
    {
        int border = 0;
        for (int k = 0; k <= i; k++)
            if (s.substr(0, k) == s.substr(i + 1 - k, k)) border = k;
        require(p[i] == border);
        require(z[i] == lcp(s, i, s));
    }
    long long total = 0, got = 0;
    for (int x : odd) got += x;
    for (int x : even) got += x;
    for (int l = 0; l < n; l++)
        for (int r = l; r < n; r++)
        {
            string a = s.substr(l, r - l + 1), b = a;
            reverse(b.begin(), b.end());
            bool pal = a == b;
            int len = r - l + 1;
            bool reported = len % 2 ? odd[(l + r) / 2] >= (len + 1) / 2
                                    : even[(l + r + 1) / 2] >= len / 2;
            require(pal == reported);
            total += pal;
        }
    require(total == got);
    if (n)
    {
        int period = n, repeat = n;
        for (int k = 1; k <= n; k++)
        {
            bool ok = true;
            for (int i = k; i < n; i++) ok &= s[i] == s[i - k];
            if (ok) period = min(period, k);
            if (ok && n % k == 0) repeat = min(repeat, k);
        }
        int step = n - p.back();
        require(period == step);
        require(repeat == (n % step == 0 ? step : n));
    }
}

void two(const string &s, const string &t)
{
    cases++;
    string a = s, b = t;
    auto [z, p] = exkmp(s, t);
    require(s == a && t == b);
    require(z.size() == t.size() && p.size() == s.size());
    for (int i = 0; i < (int)t.size(); i++) require(z[i] == lcp(t, i, t));
    vector<int> match;
    for (int i = 0; i < (int)s.size(); i++)
    {
        int want = lcp(s, i, t);
        require(p[i] == want);
        if (!t.empty() && want == (int)t.size()) match.push_back(i);
    }
    if (!t.empty()) require(kmp_match(s, t) == match);
}

int main()
{
    try
    {
        string chars = string("a") + char(0) + char(255);
        vector<string> small;
        int ways = 1;
        for (int n = 0; n <= 7; n++)
        {
            for (int mask = 0; mask < ways; mask++)
            {
                string s(n, ' ');
                int x = mask;
                for (char &c : s)
                {
                    c = chars[x % 3];
                    x /= 3;
                }
                one(s);
                if (n <= 4) small.push_back(s);
            }
            ways *= 3;
        }
        for (const auto &s : small)
            for (const auto &t : small) two(s, t);
        mt19937 gen(5410);
        for (int test = 0; test < 1500; test++)
        {
            string s(gen() % 70, ' '), t(gen() % 60, ' ');
            for (char &c : s) c = char(gen() % 256);
            for (char &c : t) c = char(gen() % 256);
            one(s);
            two(s, t);
        }
        string all;
        for (int i = 0; i < 256; i++) all += char(i);
        two(all + all, all);
        two(all, all + all);
        const int n = 1000000;
        for (int m : {0, 1, n / 2, n, n + 1})
        {
            cases++;
            auto [z, p] = exkmp(string(n, 'a'), string(m, 'a'));
            for (int i = 0; i < m; i++) require(z[i] == m - i);
            for (int i = 0; i < n; i++) require(p[i] == min(m, n - i));
        }
        cout << "PASS " << cases << " cases " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
