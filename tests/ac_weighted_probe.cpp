#include "../src/compact/ac_weighted.hpp"
#include <iostream>
#include <random>
#include <stdexcept>
using P = vector<pair<string, long long>>;
long long checks = 0;
long long cases = 0;

void check(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("oracle mismatch");
}

long long brute(const P &p, const string &t)
{
    long long ans = 0;
    for (const auto &[s, w] : p)
    {
        for (int j = 0; j <= (int)t.size(); j++)
        {
            if (t.compare(j, s.size(), s) == 0) ans += w;
        }
    }
    return ans;
}

void audit(const P &p, const vector<string> &texts)
{
    cases++;
    ACWeighted ac(p);
    vector<string> word(ac.ac.a.size());
    for (const auto &[s, w] : p)
    {
        (void)w;
        int u = 0;
        for (int i = 0; i < (int)s.size(); i++)
        {
            u = ac.ac.a[u].go[s[i] - 'a'];
            word[u] = s.substr(0, i + 1);
        }
    }
    for (int u = 0; u < (int)word.size(); u++)
    {
        long long want = 0;
        for (const auto &[s, w] : p)
        {
            if (s.size() <= word[u].size() && word[u].compare(word[u].size() - s.size(), s.size(), s) == 0)
                want += w;
        }
        check(ac.sum[u] == want);
    }
    auto old = ac.sum;
    ACWeighted copy = ac;
    ac = ACWeighted({{"z", 123}});
    ACWeighted moved = move(copy);
    for (const string &s : texts)
    {
        check(moved.query(s) == brute(p, s));
        check(moved.query(s) == brute(p, s));
    }
    check(moved.sum == old);
}

int main()
{
    try
    {
        vector<string> words = {""};
        for (int n = 1; n <= 4; n++)
        {
            for (int mask = 0; mask < (1 << n); mask++)
            {
                string s(n, 'a');
                for (int j = 0; j < n; j++) s[j] += (mask >> j) & 1;
                words.push_back(s);
            }
        }
        audit({}, words);
        for (const string &a : words)
        {
            for (const string &b : words)
            {
                for (int w : {-3, 0, 5}) audit({{a, w}, {b, 2}, {a, -1}}, words);
            }
        }
        audit({{"", 4000000000LL}, {"a", -3000000000LL}, {"aa", 5000000000LL}}, words);
        mt19937 rng(710);
        for (int round = 0; round < 160; round++)
        {
            DynamicAC ac;
            P p;
            for (int step = 0; step < 140; step++)
            {
                string s = words[rng() % words.size()];
                long long w = (int)(rng() % 21) - 10;
                ac.add(s, w);
                p.push_back({s, w});
                cases++;
                size_t count = 0;
                for (int k = 0; k < (int)ac.block.size(); k++)
                {
                    check(ac.block[k].empty() || ac.block[k].size() == (size_t(1) << k));
                    count += ac.block[k].size();
                }
                check(count == p.size());
                for (int i = 0; i < 4; i++)
                {
                    string t = words[rng() % words.size()] + words[rng() % words.size()];
                    check(ac.query(t) == brute(p, t));
                }
            }
            DynamicAC copy = ac;
            ac = DynamicAC();
            for (const string &s : words)
            {
                check(ac.query(s) == 0);
                check(copy.query(s) == brute(p, s));
            }
        }
        DynamicAC large;
        for (int i = 0; i < 65537; i++) large.add("a", i % 2 ? -1000000000LL : 1000000000LL);
        check(large.query(string(100000, 'a')) == 100000000000000LL);
        ACWeighted chain({{string(300000, 'a'), 7}});
        check(chain.query(string(300005, 'a')) == 42);
        cout << "PASS " << cases << " cases " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
