#include "../src/compact/string.hpp"
#include "../src/compact/general_sam.hpp"
#include "../src/compact/sam_queries.hpp"
#include <climits>
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

map<string, long long> substrings(const vector<string> &docs)
{
    map<string, long long> all;
    for (auto &s : docs)
        for (int i = 0; i < (int)s.size(); i++)
            for (int j = i + 1; j <= (int)s.size(); j++) all[s.substr(i, j - i)]++;
    return all;
}

template <class S>
vector<array<int, 28>> snapshot(const S &sam)
{
    vector<array<int, 28>> ans;
    for (auto &v : sam.a)
    {
        array<int, 28> row;
        copy(v.go.begin(), v.go.end(), row.begin());
        row[26] = v.link;
        row[27] = v.len;
        ans.push_back(row);
    }
    return ans;
}

template <class S>
void lcs(const S &sam, const map<string, long long> &all, const string &t)
{
    pair<int, int> want{0, 0};
    for (int i = 0; i < (int)t.size(); i++)
        for (int j = i + 1; j <= (int)t.size(); j++)
            if (j - i > want.second && all.count(t.substr(i, j - i))) want = {i, j - i};
    require(sam_lcs(sam, t) == want);
}

template <class S>
void ranks(const S &sam, const map<string, long long> &all,
           const vector<long long> &weight, const string &alphabet)
{
    auto before = snapshot(sam);
    SAMLex index(sam, weight);
    array<int, 26> rank{};
    for (int i = 0; i < 26; i++) rank[alphabet[i] - 'a'] = i;
    vector<pair<string, long long>> words;
    __int128 total = 0;
    for (auto &[s, count] : all)
    {
        int u = 0;
        for (char c : s) u = sam.a[u].go[c - 'a'];
        require(u != 0);
        long long w = weight.empty() ? 1 : weight[u];
        words.push_back({s, w});
        total += w;
    }
    sort(words.begin(), words.end(), [&](auto &x, auto &y)
    {
        auto &a = x.first;
        auto &b = y.first;
        for (int i = 0; i < (int)min(a.size(), b.size()); i++)
            if (a[i] != b[i]) return rank[a[i] - 'a'] < rank[b[i] - 'a'];
        return a.size() < b.size();
    });
    require(index.sum[0] == min(total, (__int128)LLONG_MAX));
    require(!index.kth(0, alphabet) && !index.kth(-1, alphabet));
    vector<long long> queries{1, LLONG_MAX, LLONG_MAX - 1};
    if (total < 2000)
        for (int k = 1; k <= total + 1; k++) queries.push_back(k);
    __int128 prefix = 0;
    for (auto &[s, w] : words)
    {
        if (prefix + 1 <= LLONG_MAX) queries.push_back((long long)(prefix + 1));
        prefix += w;
        if (prefix && prefix <= LLONG_MAX) queries.push_back((long long)prefix);
    }
    for (long long k : queries)
    {
        optional<string> want;
        __int128 rem = k;
        for (auto &[s, w] : words)
        {
            if (rem <= w)
            {
                want = s;
                break;
            }
            rem -= w;
        }
        require(index.kth(k, alphabet) == want);
    }
    require(snapshot(sam) == before);
    cases++;
}

vector<string> strings(int maxn)
{
    vector<string> all;
    for (int n = 0; n <= maxn; n++)
        for (int mask = 0; mask < (1 << n); mask++)
        {
            string s(n, 'a');
            for (int i = 0; i < n; i++) s[i] += (mask >> i) & 1;
            all.push_back(s);
        }
    return all;
}

int main()
{
    try
    {
        string alphabet = "abcdefghijklmnopqrstuvwxyz";
        mt19937 rng(3975);
        auto texts = strings(5);
        for (auto &s : strings(7))
        {
            SuffixAutomaton sam;
            for (char c : s) sam.extend(c - 'a');
            auto all = substrings({s});
            require(sam.distinct() == (long long)all.size());
            auto count = sam.counts();
            for (auto &[word, times] : all)
            {
                int u = 0;
                for (char c : word) u = sam.a[u].go[c - 'a'];
                require(count[u] == times);
            }
            ranks(sam, all, {}, alphabet);
            ranks(sam, all, count, alphabet);
            reverse(alphabet.begin(), alphabet.end());
            ranks(sam, all, {}, alphabet);
            for (auto &t : texts) lcs(sam, all, t);
            lcs(sam, all, "z" + s + "z" + s);
            require(count == sam.counts());
        }
        auto docs = strings(3);
        for (auto &s : docs)
            for (auto &t : docs)
            {
                GeneralSAM sam;
                sam.add(s);
                sam.add(t);
                sam.add(s);
                sam.build();
                auto all = substrings({s, t});
                ranks(sam, all, {}, alphabet);
                for (auto &q : texts) lcs(sam, all, q);
                lcs(sam, all, s + t);
            }
        for (int run = 0; run < 800; run++)
        {
            string s(rng() % 22, 'a'), t(rng() % 30, 'a');
            for (char &c : s) c += rng() % 5;
            for (char &c : t) c += rng() % 6;
            SuffixAutomaton sam;
            for (char c : s) sam.extend(c - 'a');
            auto all = substrings({s});
            shuffle(alphabet.begin(), alphabet.end(), rng);
            ranks(sam, all, sam.counts(), alphabet);
            lcs(sam, all, t);
            vector<long long> w(sam.a.size());
            for (auto &x : w) x = run % 2 ? rng() % 4 : LLONG_MAX - rng() % 3;
            ranks(sam, all, w, alphabet);
        }
        int n = 500000;
        SuffixAutomaton sam;
        for (int i = 0; i < n; i++) sam.extend(0);
        SAMLex unique(sam);
        require(unique.sum[0] == n);
        require(unique.kth(n) == optional<string>(string(n, 'a')));
        require(!unique.kth(n + 1));
        SAMLex repeated(sam, sam.counts());
        long long total = 1LL * n * (n + 1) / 2;
        require(repeated.sum[0] == total);
        for (long long k : {1LL, (long long)n, (long long)n + 1, 1000000000LL, total})
        {
            int len = 1;
            long long left = k;
            while (left > n - len + 1) left -= n - len++ + 1;
            require(repeated.kth(k) == optional<string>(string(len, 'a')));
        }
        require(sam_lcs(sam, "b" + string(250000, 'a')) == make_pair(1, 250000));
        require(sam_lcs(sam, string(250000, 'b')) == make_pair(0, 0));
        cases++;
        cout << "PASS " << cases << " cases " << checks << " checks\n";
    }
    catch (const runtime_error &)
    {
        cout << "ORACLE_REJECT\n";
    }
}
