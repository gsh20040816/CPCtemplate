#include "../src/compact/string.hpp"
#include <cassert>

void check(const string &input)
{
    SuffixAutomaton sam;
    string s;
    assert(sam.distinct() == 0 && sam.counts() == vector<long long>{0});
    for (char ch : input)
    {
        sam.extend(ch - 'a');
        s += ch;
        map<string, set<int>> ends;
        for (int l = 0; l < (int)s.size(); l++)
            for (int r = l; r < (int)s.size(); r++)
                ends[s.substr(l, r - l + 1)].insert(r);
        assert(sam.distinct() == (long long)ends.size());
        auto counts = sam.counts();
        assert(counts == sam.counts());
        assert(counts[0] == (int)s.size());
        vector<set<int>> state_ends(sam.a.size());
        vector<vector<int>> lengths(sam.a.size());
        for (auto &[word, positions] : ends)
        {
            int u = 0;
            for (char c : word)
            {
                u = sam.a[u].go[c - 'a'];
                assert(u > 0 && u < (int)sam.a.size());
            }
            if (state_ends[u].empty()) state_ends[u] = positions;
            assert(state_ends[u] == positions);
            assert(counts[u] == (long long)positions.size());
            lengths[u].push_back(word.size());
            for (int c = 0; c < 26; c++)
                assert(bool(sam.a[u].go[c]) == ends.contains(word + char('a' + c)));
        }
        for (int c = 0; c < 26; c++)
            assert(bool(sam.a[0].go[c]) == ends.contains(string(1, char('a' + c))));
        set<set<int>> different;
        long long seeds = 0;
        for (int u = 1; u < (int)sam.a.size(); u++)
        {
            auto &v = sam.a[u];
            assert(!state_ends[u].empty() && different.insert(state_ends[u]).second);
            assert(v.link >= 0 && v.link < (int)sam.a.size());
            sort(lengths[u].begin(), lengths[u].end());
            vector<int> expected(v.len - sam.a[v.link].len);
            iota(expected.begin(), expected.end(), sam.a[v.link].len + 1);
            assert(lengths[u] == expected);
            assert(v.occ == 0 || v.occ == 1);
            seeds += v.occ;
            for (int to : v.go)
                if (to) assert(sam.a[to].len > v.len);
        }
        assert(seeds == (int)s.size());
        assert(sam.a[sam.last].len == (int)s.size());
    }
    sam = SuffixAutomaton();
    assert(sam.last == 0 && sam.a.size() == 1 && sam.counts() == vector<long long>{0});
}

int main()
{
    for (int n = 0, ways = 1; n <= 7; n++, ways *= 3)
        for (int mask = 0; mask < ways; mask++)
        {
            int code = mask;
            string s(n, 'a');
            for (char &c : s)
            {
                c += code % 3;
                code /= 3;
            }
            check(s);
        }
    check("abcdefghijklmnopqrstuvwxyz");
    check("abbbabbbbababbbbb");
    const int n = 1000000;
    SuffixAutomaton sam;
    for (int i = 0; i < n; i++) sam.extend(0);
    auto count = sam.counts();
    assert(sam.distinct() == n);
    for (int u = 1; u < (int)sam.a.size(); u++)
        assert(count[u] == n - sam.a[u].len + 1);
    cout << "SAM: 3280 ternary strings with every prefix, independent endpos classes, "
            "length intervals, raw seeds, repeated counts/append/reset and "
            "million-character frequencies PASS\n";
}
