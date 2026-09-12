#pragma once
#include <cassert>
#include <bits/stdc++.h>
using namespace std;

// BEGIN prefix_function
inline vector<int> prefix_function(const string &s)
{
    int n = (int)s.size();
    vector<int> p(n);
    for (int i = 1; i < n; i++)
    {
        int j = p[i - 1];
        while (j && s[i] != s[j]) j = p[j - 1];
        p[i] = j + (s[i] == s[j]);
    }
    return p;
}

// END prefix_function

// BEGIN kmp_match
inline vector<int> kmp_match(const string &s, const string &t)
{
    assert(!t.empty());
    auto p = prefix_function(t);
    vector<int> ans;
    for (int i = 0, j = 0; i < (int)s.size(); i++)
    {
        while (j && s[i] != t[j]) j = p[j - 1];
        j += (s[i] == t[j]);
        if (j == (int)t.size())
        {
            ans.push_back(i - j + 1);
            j = p[j - 1];
        }
    }
    return ans;
}

// END kmp_match

// BEGIN z_function
inline vector<int> z_function(const string &s)
{
    int n = (int)s.size();
    vector<int> a(n);
    if (n) a[0] = n;
    for (int i = 1, l = 0, r = 0; i < n; i++)
    {
        if (i < r) a[i] = min(r - i, a[i - l]);
        while (i + a[i] < n && s[a[i]] == s[i + a[i]]) ++a[i];
        if (i + a[i] > r)
        {
            l = i;
            r = i + a[i];
        }
    }
    return a;
}

// END z_function

// BEGIN manacher
// odd[i] includes the center; even[i] is centered before i.
inline pair<vector<int>, vector<int>> manacher(const string &s)
{
    int n = (int)s.size();
    vector<int> odd(n), even(n);
    for (int i = 0, l = 0, r = -1; i < n; i++)
    {
        int k = i > r ? 1 : min(odd[l + r - i], r - i + 1);
        while (i - k >= 0 && i + k < n && s[i - k] == s[i + k]) ++k;
        odd[i] = k--;
        if (i + k > r)
        {
            l = i - k;
            r = i + k;
        }
    }
    for (int i = 0, l = 0, r = -1; i < n; i++)
    {
        int k = i > r ? 0 : min(even[l + r - i + 1], r - i + 1);
        while (i - k - 1 >= 0 && i + k < n && s[i - k - 1] == s[i + k]) ++k;
        even[i] = k--;
        if (i + k > r)
        {
            l = i - k - 1;
            r = i + k;
        }
    }
    return {odd, even};
}

// END manacher

// BEGIN minimum_rotation
inline int minimum_rotation(const string &s)
{
    int n = (int)s.size(), i = 0, j = 1, k = 0;
    if (!n) return 0;
    while (i < n && j < n && k < n)
    {
        unsigned char a = s[(i + k) % n], b = s[(j + k) % n];
        if (a == b)
        {
            ++k;
            continue;
        }
        if (a > b)
        {
            i += k + 1;
            if (i == j) ++i;
        }
        else
        {
            j += k + 1;
            if (i == j) ++j;
        }
        k = 0;
    }
    return min(i, j);
}

// END minimum_rotation

struct AhoCorasick
{
    struct Node
    {
        array<int, 26> go{};
        int fail = 0;
    };

    vector<Node> a{Node{}};
    vector<int> order;
    bool built = false;

    int add(const string &s)
    {
        assert(!built && !s.empty());
        int u = 0;
        for (char ch : s)
        {
            int c = ch - 'a';
            assert(0 <= c && c < 26);
            if (!a[u].go[c])
            {
                int v = (int)a.size();
                a[u].go[c] = v;
                a.push_back(Node{});
            }
            u = a[u].go[c];
        }
        return u;
    }

    void build()
    {
        assert(!built);
        built = true;
        queue<int> q;
        for (int v : a[0].go)
            if (v) q.push(v);
        while (!q.empty())
        {
            int u = q.front();
            q.pop();
            order.push_back(u);
            for (int c = 0; c < 26; c++)
            {
                int v = a[u].go[c];
                if (v)
                {
                    a[v].fail = a[a[u].fail].go[c];
                    q.push(v);
                }
                else
                    a[u].go[c] = a[a[u].fail].go[c];
            }
        }
    }

    vector<long long> count(const string &s) const
    {
        assert(built);
        vector<long long> ans(a.size());
        int u = 0;
        for (char ch : s)
        {
            u = a[u].go[ch - 'a'];
            ++ans[u];
        }
        for (int i = (int)order.size() - 1; i >= 0; i--)
            ans[a[order[i]].fail] += ans[order[i]];
        return ans;
    }
};

struct SuffixArray
{
    vector<int> sa, rk, lcp;

    SuffixArray(const string &s)
    {
        vector<int> a;
        a.reserve(s.size());
        for (unsigned char c : s) a.push_back(c);
        init(a, 256);
    }

    SuffixArray(const vector<int> &s, int alphabet) { init(s, alphabet); }

    void init(const vector<int> &s, int alphabet)
    {
        assert(s.size() < INT_MAX);
        assert(1 <= alphabet && alphabet < INT_MAX);
        int n = (int)s.size();
        sa.resize(n);
        rk.resize(n);
        lcp.assign(n, 0);
        if (!n) return;
        vector<int> order(n), old(n), cnt(max(n + 1, alphabet + 1));
        int m = alphabet;
        for (int i = 0; i < n; i++)
        {
            assert(0 <= s[i] && s[i] < alphabet);
            rk[i] = s[i] + 1;
            cnt[rk[i]]++;
        }
        for (int i = 1; i <= m; i++) cnt[i] += cnt[i - 1];
        for (int i = n - 1; i >= 0; i--) sa[--cnt[rk[i]]] = i;
        for (int k = 1; k < n; k *= 2)
        {
            int p = 0;
            for (int i = n - k; i < n; i++) order[p++] = i;
            for (int i : sa)
                if (i >= k) order[p++] = i - k;
            fill(cnt.begin(), cnt.begin() + m + 1, 0);
            for (int x : rk) cnt[x]++;
            for (int i = 1; i <= m; i++) cnt[i] += cnt[i - 1];
            for (int i = n - 1; i >= 0; i--) sa[--cnt[rk[order[i]]]] = order[i];
            old.swap(rk);
            auto second = [&](int i)
            {
                return i < n - k ? old[i + k] : 0;
            };
            m = 1;
            rk[sa[0]] = m;
            for (int i = 1; i < n; i++)
            {
                int a = sa[i - 1], b = sa[i];
                if (old[a] != old[b] || second(a) != second(b)) m++;
                rk[b] = m;
            }
            if (m == n) break;
        }
        for (int i = 0; i < n; i++) rk[sa[i]] = i;
        for (int i = 0, k = 0; i < n; i++)
        {
            if (!rk[i])
            {
                k = 0;
                continue;
            }
            int j = sa[rk[i] - 1];
            while (k < n - i && k < n - j && s[i + k] == s[j + k]) ++k;
            lcp[rk[i]] = k;
            if (k) --k;
        }
    }
};

struct SuffixAutomaton
{
    struct Node
    {
        array<int, 26> go{};
        int link = -1, len = 0;
        long long occ = 0;
    };

    vector<Node> a{Node{}};
    int last = 0;

    void extend(int c)
    {
        assert(0 <= c && c < 26);
        int cur = (int)a.size();
        a.push_back(Node{});
        a[cur].len = a[last].len + 1;
        a[cur].occ = 1;
        int p = last;
        while (p != -1 && !a[p].go[c])
        {
            a[p].go[c] = cur;
            p = a[p].link;
        }
        if (p == -1)
            a[cur].link = 0;
        else
        {
            int q = a[p].go[c];
            if (a[p].len + 1 == a[q].len)
                a[cur].link = q;
            else
            {
                int clone = (int)a.size();
                Node copy = a[q];
                a.push_back(copy);
                a[clone].len = a[p].len + 1;
                a[clone].occ = 0;
                while (p != -1 && a[p].go[c] == q)
                {
                    a[p].go[c] = clone;
                    p = a[p].link;
                }
                a[q].link = a[cur].link = clone;
            }
        }
        last = cur;
    }

    vector<long long> counts() const
    {
        vector<int> bucket(a[last].len + 1), order(a.size());
        vector<long long> ans(a.size());
        for (auto &v : a) ++bucket[v.len];
        partial_sum(bucket.begin(), bucket.end(), bucket.begin());
        for (int i = 0; i < (int)a.size(); i++)
        {
            order[--bucket[a[i].len]] = i;
            ans[i] = a[i].occ;
        }
        for (int i = (int)order.size() - 1; i > 0; i--)
            ans[a[order[i]].link] += ans[order[i]];
        return ans;
    }

    long long distinct() const
    {
        long long ans = 0;
        for (int i = 1; i < (int)a.size(); i++) ans += a[i].len - a[a[i].link].len;
        return ans;
    }
};
