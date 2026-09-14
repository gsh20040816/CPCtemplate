#include "../src/compact/general_sam.hpp"
#include <algorithm>
#include <iostream>
#include <map>
#include <random>
#include <set>
using namespace std;

void check(const vector<string> &words)
{
    GeneralSAM g;
    map<string, set<pair<int, int>>> ends;
    for (int id = 0; id < (int)words.size(); id++)
    {
        g.add(words[id]);
        for (int l = 0; l < (int)words[id].size(); l++)
            for (int r = l; r < (int)words[id].size(); r++)
                ends[words[id].substr(l, r - l + 1)].insert({id, r});
    }
    g.build();
    assert(g.distinct() == (long long)ends.size());
    set<set<pair<int, int>>> classes;
    map<int, set<pair<int, int>>> state_ends;
    for (auto &[s, locations] : ends)
    {
        classes.insert(locations);
        int p = 0;
        for (char c : s)
        {
            p = g.a[p].go[c - 'a'];
            assert(p);
        }
        if (state_ends.count(p)) assert(state_ends[p] == locations);
        state_ends[p] = locations;
        assert(g.a[g.a[p].link].len < (int)s.size());
        assert((int)s.size() <= g.a[p].len);
    }
    assert(classes.size() + 1 == g.a.size());
    assert(state_ends.size() + 1 == g.a.size());
    for (int p = 1; p < (int)g.a.size(); p++)
    {
        assert(0 <= g.a[p].link && g.a[p].link < (int)g.a.size());
        assert(g.a[g.a[p].link].len < g.a[p].len);
        for (int q : g.a[p].go)
            if (q) assert(g.a[q].len > g.a[p].len);
    }
    // Enumerate all accepted paths: no substring crossing document boundaries.
    set<string> language;
    auto dfs = [&](auto &&self, int p, string s) -> void
    {
        if (!s.empty()) language.insert(s);
        for (int c = 0; c < 26; c++)
            if (g.a[p].go[c]) self(self, g.a[p].go[c], s + char('a' + c));
    };
    dfs(dfs, 0, "");
    assert(language.size() == ends.size());
    for (auto &s : language) assert(ends.count(s));
    auto before = g.a.size();
    g.build();
    assert(g.a.size() == before && g.distinct() == (long long)ends.size());
}

int main()
{
    vector<string> small{""};
    for (int len = 1; len <= 3; len++)
        for (int mask = 0; mask < (1 << len); mask++)
        {
            string s(len, 'a');
            for (int i = 0; i < len; i++) s[i] += mask >> i & 1;
            small.push_back(s);
        }
    for (auto &a : small)
        for (auto &b : small)
            for (auto &c : small) check({a, b, c});
    mt19937 rng(6139);
    for (int trial = 0; trial < 2000; trial++)
    {
        vector<string> words(rng() % 7);
        for (auto &s : words)
        {
            s.resize(rng() % 9);
            for (char &c : s) c = 'a' + rng() % 4;
        }
        check(words);
        reverse(words.begin(), words.end());
        check(words);
    }
    GeneralSAM chain;
    chain.add(string(1000000, 'a'));
    chain.build();
    assert(chain.distinct() == 1000000 && chain.a.size() == 1000001);
    GeneralSAM repeated;
    for (int i = 0; i < 400000; i++) repeated.add("ab");
    repeated.build();
    assert(repeated.distinct() == 3 && repeated.a.size() == 3);
    cout << "GeneralSAM: 3375 exhaustive triples, 2000 random sets and reversed order, "
            "independent substring/endpos classes and accepted paths; "
            "million-character chain and 400000 duplicate strings PASS\n";
}
