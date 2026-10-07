#include "../src/compact/online_sam.hpp"
#include "../src/compact/general_sam.hpp"
#include "../src/compact/sam_queries.hpp"
#include <algorithm>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <stdexcept>

long long checks = 0, cases = 0;
void require(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("oracle");
}

template <class S>
void verify(const S &sam, const vector<string> &words)
{
    map<string, set<pair<int, int>>> ends;
    for (int id = 0; id < (int)words.size(); id++)
        for (int l = 0; l < (int)words[id].size(); l++)
            for (int r = l; r < (int)words[id].size(); r++)
                ends[words[id].substr(l, r - l + 1)].insert({id, r});
    set<set<pair<int, int>>> classes;
    map<int, set<pair<int, int>>> state_ends;
    vector<string> longest(sam.a.size());
    long long total = 0;
    for (int u = 1; u < (int)sam.a.size(); u++)
    {
        require(sam.a[u].link >= 0 && sam.a[u].link < (int)sam.a.size());
        require(sam.a[sam.a[u].link].len < sam.a[u].len);
        total += sam.a[u].len - sam.a[sam.a[u].link].len;
    }
    require(total == (long long)ends.size());
    for (auto &[s, locations] : ends)
    {
        classes.insert(locations);
        int p = 0;
        for (char c : s) p = sam.a[p].go[c - 'a'];
        require(p != 0);
        if (state_ends.count(p)) require(state_ends[p] == locations);
        state_ends[p] = locations;
        require(sam.a[sam.a[p].link].len < (int)s.size());
        require((int)s.size() <= sam.a[p].len);
        if (s.size() > longest[p].size()) longest[p] = s;
    }
    require(classes.size() + 1 == sam.a.size());
    require(state_ends.size() + 1 == sam.a.size());
    set<string> accepted;
    auto dfs = [&](auto &&self, int p, string s) -> void
    {
        if (p) accepted.insert(s);
        for (int c = 0; c < 26; c++)
            if (int q = sam.a[p].go[c])
            {
                require(sam.a[q].len > sam.a[p].len);
                self(self, q, s + char('a' + c));
            }
    };
    dfs(dfs, 0, "");
    require(accepted.size() == ends.size());
    for (auto &s : accepted) require(ends.count(s));
    SAMLex index(sam);
    int k = 0;
    for (auto &s : accepted) require(index.kth(++k) == optional<string>(s));
    require(!index.kth(k + 1));
    for (auto &s : words) require(sam_lcs(sam, s) == make_pair(0, (int)s.size()));
    cases++;
}

void operations(const vector<pair<int, int>> &ops)
{
    OnlineSAM online;
    GeneralSAM batch;
    vector<string> words(1);
    vector<int> state(1), trie(1);
    for (auto [p, c] : ops)
    {
        vector<int> old;
        for (auto &v : online.a) old.push_back(v.len);
        auto size = online.a.size();
        words.push_back(words[p] + char('a' + c));
        state.push_back(online.extend(state[p], c));
        trie.push_back(batch.add(trie[p], c));
        require(online.a.size() <= size + 2);
        for (int i = 0; i < (int)old.size(); i++) require(online.a[i].len == old[i]);
        verify(online, words);
        set<string> all;
        for (auto &s : words)
            for (int l = 0; l < (int)s.size(); l++)
                for (int r = l + 1; r <= (int)s.size(); r++) all.insert(s.substr(l, r - l));
        require(online.total == (long long)all.size());
        for (int i = 0; i < (int)words.size(); i++)
        {
            int q = 0;
            for (char ch : words[i]) q = online.a[q].go[ch - 'a'];
            require(q == state[i]);
            require(online.a[q].len == (int)words[i].size());
        }
    }
    batch.build();
    verify(batch, words);
    for (int i = 0; i < (int)words.size(); i++)
    {
        int q = 0;
        for (char ch : words[i]) q = batch.a[q].go[ch - 'a'];
        require(q == trie[i]);
    }
    require(batch.distinct() == online.total);
    GeneralSAM from_words;
    for (auto &s : words) from_words.add(s);
    from_words.build();
    verify(from_words, words);
    auto copy = online;
    copy.extend(0, 25);
    require(online.a[0].go[25] == 0);
}

int main()
{
    try
    {
        vector<pair<int, int>> ops;
        auto dfs = [&](auto &&self, int n) -> void
        {
            if ((int)ops.size() == n)
            {
                operations(ops);
                return;
            }
            for (int p = 0; p <= (int)ops.size(); p++)
                for (int c = 0; c < 2; c++)
                {
                    ops.push_back({p, c});
                    self(self, n);
                    ops.pop_back();
                }
        };
        for (int n = 0; n <= 5; n++) dfs(dfs, n);
        mt19937 rng(61390);
        for (int run = 0; run < 500; run++)
        {
            ops.clear();
            for (int i = 0; i < 18; i++) ops.push_back({rng() % (i + 1), rng() % 5});
            operations(ops);
        }
        // After an initial document, choose every state, including internal clones.
        for (string s : {"abcbc", "banana", "abbbb", "abcabac"})
        {
            OnlineSAM base;
            int p = 0;
            for (char c : s) p = base.extend(p, c - 'a');
            vector<string> longest(base.a.size());
            for (int i = 0; i < (int)s.size(); i++)
                for (int j = i + 1; j <= (int)s.size(); j++)
                {
                    int u = 0;
                    for (int k = i; k < j; k++) u = base.a[u].go[s[k] - 'a'];
                    if (j - i > (int)longest[u].size()) longest[u] = s.substr(i, j - i);
                }
            for (int u = 0; u < (int)base.a.size(); u++)
                for (int c = 0; c < 4; c++)
                {
                    auto sam = base;
                    int v = sam.extend(u, c);
                    string t = longest[u] + char('a' + c);
                    require(sam.a[v].len == (int)t.size());
                    verify(sam, {s, t});
                }
        }
        int n = 250000;
        OnlineSAM chain;
        GeneralSAM trie;
        int p = 0, q = 0;
        for (int i = 0; i < n; i++)
        {
            p = chain.extend(p, i == 0 ? 0 : 1);
            q = trie.add(q, i == 0 ? 0 : 1);
        }
        trie.build();
        require(chain.total == 2LL * n - 1);
        require(trie.distinct() == chain.total);
        require(chain.a.size() == 2ULL * n - 1);
        require(trie.a.size() == chain.a.size());
        cases++;
        cout << "PASS " << cases << " cases " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
