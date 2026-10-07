#include <algorithm>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <stdexcept>
#include "../src/compact/general_sam.hpp"
#include "../src/compact/online_sam.hpp"
#include "../src/compact/string.hpp"
#include "../src/compact/sam_queries.hpp"
#include "../src/compact/sam_documents.hpp"
using namespace std;

long long cases = 0, checks = 0;
void require(bool ok)
{
    checks++;
    if (!ok) throw runtime_error("oracle");
}

template<class S>
void check(const S &sam, const vector<string> &s)
{
    cases++;
    auto before = sam.a;
    SAMDocuments index(sam, s);
    map<string, set<int>> docs;
    for (int id = 0; id < (int)s.size(); id++)
        for (int l = 0; l < (int)s[id].size(); l++)
            for (int r = l + 1; r <= (int)s[id].size(); r++)
                docs[s[id].substr(l, r - l)].insert(id);
    vector<string> rep(sam.a.size());
    require(index.cnt[0] == (int)s.size());
    long long distinct = 0;
    vector<string> weighted;
    for (auto &[t, ids] : docs)
    {
        int p = 0;
        for (char c : t)
        {
            p = sam.a[p].go[c - 'a'];
            require(p > 0);
        }
        require(index.cnt[p] == (int)ids.size());
        if (t.size() > rep[p].size()) rep[p] = t;
        for (int id : ids) weighted.push_back(t);
    }
    for (int u = 1; u < (int)sam.a.size(); u++)
    {
        require((int)rep[u].size() == sam.a[u].len);
        require(index.cnt[u] <= index.cnt[sam.a[u].link]);
        distinct += sam.a[u].len - sam.a[sam.a[u].link].len;
    }
    require(distinct == (long long)docs.size());
    for (int k = 1; k <= (int)s.size() + 2; k++)
    {
        auto best = index.lengths(k);
        require(best[0] == 0);
        for (int u = 1; u < (int)sam.a.size(); u++)
        {
            int want = 0;
            for (int l = 0; l < (int)rep[u].size(); l++)
                if ((int)docs.at(rep[u].substr(l)).size() >= k)
                    want = max(want, (int)rep[u].size() - l);
            require(best[u] == want);
        }
        for (auto &t : s)
        {
            int p = 0;
            long long got = 0, want = 0;
            for (char c : t)
            {
                p = sam.a[p].go[c - 'a'];
                got += best[p];
            }
            for (int l = 0; l < (int)t.size(); l++)
                for (int r = l + 1; r <= (int)t.size(); r++)
                    want += (int)docs.at(t.substr(l, r - l)).size() >= k;
            require(got == want);
        }
    }
    auto large = index.lengths(2147483647);
    require(all_of(large.begin(), large.end(), [](int x) { return x == 0; }));
    sort(weighted.begin(), weighted.end());
    vector<long long> w(index.cnt.begin(), index.cnt.end());
    SAMLex lex(sam, w);
    require(lex.sum[0] == (long long)weighted.size());
    for (int i = 0; i < (int)weighted.size(); i++) require(lex.kth(i + 1) == weighted[i]);
    require(!lex.kth(weighted.size() + 1));
    auto copy = index;
    require(copy.cnt == index.cnt && copy.lengths(1) == index.lengths(1));
    require(before.size() == sam.a.size());
    for (int u = 0; u < (int)sam.a.size(); u++)
    {
        require(before[u].go == sam.a[u].go);
        require(before[u].link == sam.a[u].link && before[u].len == sam.a[u].len);
    }
}

void run(const vector<string> &s)
{
    GeneralSAM sam;
    OnlineSAM online;
    for (auto &t : s)
    {
        sam.add(t);
        int p = 0;
        for (char c : t) p = online.extend(p, c - 'a');
    }
    sam.build();
    check(sam, s);
    check(online, s);
    if (s.size() == 1)
    {
        SuffixAutomaton single;
        for (char c : s[0]) single.extend(c - 'a');
        check(single, s);
    }
}

void large_tests()
{
    int n = 100000;
    for (bool clone : {false, true})
    {
        string t(n, clone ? 'b' : 'a');
        if (clone) t[0] = 'a';
        vector<string> s{t, t, "", string(n / 2, clone ? 'b' : 'a')};
        GeneralSAM sam;
        for (auto &v : s) sam.add(v);
        sam.build();
        SAMDocuments index(sam, s);
        auto three = index.lengths(3), four = index.lengths(4), one = index.lengths(1);
        require(index.cnt[0] == 4);
        int p = 0;
        long long ans = 0;
        for (int i = 0; i < n; i++)
        {
            p = sam.a[p].go[t[i] - 'a'];
            require(one[p] == i + 1);
            require(three[p] == min(n / 2, i + (clone ? 0 : 1)));
            require(four[p] == 0);
            ans += one[p];
        }
        require(ans == 1LL * n * (n + 1) / 2);
        cases++;
    }
    vector<string> s(n, "ab");
    GeneralSAM sam;
    for (auto &t : s) sam.add(t);
    sam.build();
    SAMDocuments index(sam, s);
    for (int c : index.cnt) require(c == n);
    auto best = index.lengths(n);
    for (int u = 0; u < (int)sam.a.size(); u++) require(best[u] == sam.a[u].len);
    cases++;
}

int main()
{
    try
    {
        run({});
        vector<string> pool{""};
        for (int len = 1; len <= 3; len++)
            for (int mask = 0; mask < (1 << len); mask++)
            {
                string s(len, 'a');
                for (int i = 0; i < len; i++) s[i] += mask >> i & 1;
                pool.push_back(s);
            }
        for (auto &a : pool)
        {
            run({a});
            for (auto &b : pool)
            {
                run({a, b});
                for (auto &c : pool) run({a, b, c});
            }
        }
        mt19937 rng(204);
        for (int turn = 0; turn < 600; turn++)
        {
            vector<string> s(rng() % 7);
            for (auto &t : s)
            {
                t.resize(rng() % 13);
                for (char &c : t) c = 'a' + rng() % (turn % 2 ? 3 : 26);
            }
            run(s);
            reverse(s.begin(), s.end());
            run(s);
        }
        run({"abcbc", "banana", "abbbb", "abcabac", ""});
        large_tests();
        cout << "PASS " << cases << " cases " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
