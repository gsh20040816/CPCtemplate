#include "../src/compact/string.hpp"
#include <map>
#include <random>
#include <stdexcept>
#include <iostream>

long long cases = 0, checks = 0;
void check(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("oracle");
}

void audit(const vector<vector<int>> &ps, const vector<vector<int>> &ts, int offset)
{
    AhoCorasick ac, low;
    vector<int> end;
    map<vector<int>, int> node{{{}, 0}};
    for (auto s : ps)
    {
        string text;
        for (int c : s) text += char('a' + c);
        int u = low.add(text);
        for (int &c : s) c += offset;
        check(ac.add(s, offset) == u);
        end.push_back(u);
        vector<int> prefix;
        u = 0;
        for (int c : s)
        {
            prefix.push_back(c - offset);
            u = ac.a[u].go[c - offset];
            node[prefix] = u;
        }
    }
    ac.build();
    low.build();
    check(node.size() == ac.a.size());
    for (const auto &[s, u] : node)
    {
        check(ac.a[u].len == (int)s.size());
        check(ac.a[u].go == low.a[u].go);
        check(ac.a[u].fail == low.a[u].fail);
        vector<int> suffix;
        int fail = 0;
        for (int i = (int)s.size() - 1; i >= 1; i--)
        {
            suffix.insert(suffix.begin(), s[i]);
            if (node.count(suffix)) fail = node.at(suffix);
        }
        check(ac.a[u].fail == fail);
        for (int c = 0; c < 26; c++)
        {
            auto t = s;
            t.push_back(c);
            int want = 0;
            for (int i = 0; i <= (int)t.size(); i++)
            {
                vector<int> sub(t.begin() + i, t.end());
                if (node.count(sub))
                {
                    want = node.at(sub);
                    break;
                }
            }
            check(ac.a[u].go[c] == want);
        }
    }
    AhoCorasick copy = ac;
    for (auto t : ts)
    {
        cases++;
        auto encoded = t;
        for (int &c : encoded) c += offset;
        auto cnt = ac.count(encoded, offset);
        check(cnt == copy.count(encoded, offset));
        for (const auto &[s, u] : node)
        {
            long long want = 0;
            for (int i = 0; i + (int)s.size() <= (int)t.size(); i++)
                want += equal(s.begin(), s.end(), t.begin() + i);
            check(cnt[u] == want);
        }
    }
    ac = AhoCorasick();
    check(ac.a[0].len == 0 && !ac.built);
    check(ac.add(vector<int>{}, offset) == 0);
    ac.build();
    check(ac.count(vector<int>{}, offset)[0] == 1);
}

int main()
{
    try
    {
        vector<vector<int>> words{{}};
        for (int n = 1; n <= 3; n++)
        {
            for (int mask = 0; mask < (1 << n); mask++)
            {
                vector<int> s(n);
                for (int j = 0; j < n; j++) s[j] = mask >> j & 1;
                words.push_back(s);
            }
        }
        for (int offset : {0, -17, INT_MIN, INT_MAX - 25})
        {
            audit({}, words, offset);
            for (const auto &a : words)
                for (const auto &b : words) audit({a, b, a}, words, offset);
        }
        mt19937 rng(265);
        for (int trial = 0; trial < 800; trial++)
        {
            vector<vector<int>> ps(rng() % 15), ts(5);
            for (auto &s : ps)
            {
                s.resize(rng() % 12);
                for (int &c : s) c = rng() % 26;
            }
            for (auto &s : ts)
            {
                s.resize(rng() % 60);
                for (int &c : s) c = rng() % 26;
            }
            audit(ps, ts, -1000000);
        }
        for (int offset : {'A', 'a', '0'})
        {
            AhoCorasick ac;
            string p(5, char(offset + 25));
            int u = ac.add(p, offset);
            check(ac.add(string{}, offset) == 0);
            ac.build();
            auto cnt = ac.count(string(8, char(offset + 25)), offset);
            check(cnt[u] == 4 && cnt[0] == 9);
            check(ac.a[u].len == 5);
        }
        AhoCorasick chain;
        int u = chain.add(vector<int>(1000000, INT_MIN), INT_MIN);
        chain.build();
        check(chain.a[u].len == 1000000);
        check(chain.count(vector<int>(1000000, INT_MIN), INT_MIN)[u] == 1);
        cout << "PASS " << cases << " cases " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
