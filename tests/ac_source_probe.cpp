#include <algorithm>
#include <iostream>
#include <map>
#include <random>
#include <stdexcept>
#include "../src/compact/string.hpp"
using namespace std;

long long cases = 0, checks = 0;
void require(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("oracle");
}

void check(const vector<string> &patterns, const vector<string> &texts)
{
    AhoCorasick ac;
    vector<int> ends;
    for (auto &s : patterns) ends.push_back(ac.add(s));
    map<string, int> node{{"", 0}};
    for (auto &s : patterns)
    {
        int u = 0;
        for (int i = 0; i < (int)s.size(); i++)
        {
            u = ac.a[u].go[s[i] - 'a'];
            node[s.substr(0, i + 1)] = u;
        }
    }
    require(node.size() == ac.a.size());
    ac.build();
    vector<int> rank(ac.a.size());
    for (int i = 0; i < (int)ac.order.size(); i++) rank[ac.order[i]] = i + 1;
    require(ac.order.size() + 1 == ac.a.size());
    for (auto &[s, u] : node)
    {
        if (u)
        {
            int fail = 0;
            for (int i = 1; i < (int)s.size(); i++)
                if (node.count(s.substr(i)))
                {
                    fail = node.at(s.substr(i));
                    break;
                }
            require(ac.a[u].fail == fail);
            require(rank[fail] < rank[u]);
        }
        for (char c = 'a'; c <= 'z'; c++)
        {
            string t = s + c;
            int want = 0;
            for (int i = 0; i < (int)t.size(); i++)
                if (node.count(t.substr(i)))
                {
                    want = node.at(t.substr(i));
                    break;
                }
            require(ac.a[u].go[c - 'a'] == want);
        }
    }
    auto before = ac.a;
    for (auto &text : texts)
    {
        cases++;
        auto cnt = ac.count(text);
        require(cnt[0] == (long long)text.size());
        for (auto &[s, u] : node)
        {
            if (!u) continue;
            long long want = 0;
            for (int i = 0; i + (int)s.size() <= (int)text.size(); i++)
                want += text.compare(i, s.size(), s) == 0;
            require(cnt[u] == want);
        }
        int got = 0, want = 0;
        for (int i = 0; i < (int)patterns.size(); i++)
        {
            got += cnt[ends[i]] > 0;
            want += text.find(patterns[i]) != string::npos;
        }
        require(got == want);
        require(ac.count(text) == cnt);
        AhoCorasick copy = ac;
        require(copy.count(text) == cnt);
    }
    for (int i = 0; i < (int)ac.a.size(); i++)
        require(ac.a[i].go == before[i].go && ac.a[i].fail == before[i].fail);
    ac = AhoCorasick();
    require(ac.a.size() == 1 && ac.order.empty() && !ac.built);
    int u = ac.add("z");
    ac.build();
    require(ac.count("zz")[u] == 2);
}

int main()
{
    try
    {
        vector<string> pool, texts{""};
        for (int len = 1; len <= 5; len++)
            for (int mask = 0; mask < (1 << len); mask++)
            {
                string s(len, 'a');
                for (int i = 0; i < len; i++) s[i] += mask >> i & 1;
                texts.push_back(s);
                if (len <= 3) pool.push_back(s);
            }
        check({}, texts);
        for (auto &a : pool)
        {
            check({a}, texts);
            for (auto &b : pool)
            {
                check({a, b}, texts);
                for (auto &c : pool) check({a, b, c}, {"", "ababba", "babbab", "cccc"});
            }
        }
        mt19937 rng(3808);
        for (int run = 0; run < 500; run++)
        {
            vector<string> ps(rng() % 20), ts(5);
            for (auto &s : ps)
            {
                s.resize(1 + rng() % 12);
                for (char &c : s) c = 'a' + rng() % (run % 2 ? 3 : 26);
            }
            for (auto &s : ts)
            {
                s.resize(rng() % 100);
                for (char &c : s) c = 'a' + rng() % (run % 2 ? 4 : 26);
            }
            check(ps, ts);
        }
        int n = 1000000;
        AhoCorasick ac;
        int u = ac.add(string(n, 'a'));
        ac.build();
        auto cnt = ac.count(string(n, 'a'));
        for (int i = 1; i <= n; i++) require(cnt[i] == n - i + 1);
        require(cnt[u] == 1);
        cases++;
        cout << "PASS " << cases << " cases " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
