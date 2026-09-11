#pragma once
#include <algorithm>
#include <array>
#include <cassert>
#include <climits>
#include <cmath>
#include <functional>
#include <map>
#include <numeric>
#include <optional>
#include <queue>
#include <random>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <utility>
#include <vector>
using namespace std;

struct String_Algorithm
{
    static vector<int> Prefix(const string &s)
    {
        int n = (int)s.size();
        vector<int> p(n);
        for ( int i = 1; i < n; i++ )
        {
            int j = p[i - 1];
            while ( j && s[i] != s[j] )
                j = p[j - 1];
            p[i] = j + (s[i] == s[j]);
        }
        return p;
    }
    static vector<int> Match(const string &s, const string &t)
    {
        assert(!t.empty());
        auto p = Prefix(t);
        vector<int> ans;
        for ( int i = 0, j = 0; i < (int)s.size(); i++ )
        {
            while ( j && s[i] != t[j] )
                j = p[j - 1];
            j += (s[i] == t[j]);
            if ( j == (int)t.size() )
            {
                ans.push_back(i - j + 1);
                j = p[j - 1];
            }
        }
        return ans;
    }
    static vector<int> Z_Function(const string &s)
    {
        int n = (int)s.size();
        vector<int> a(n);
        if ( n )
            a[0] = n;
        for ( int i = 1, l = 0, r = 0; i < n; i++ )
        {
            if ( i < r )
                a[i] = min(r - i, a[i - l]);
            while ( i + a[i] < n && s[a[i]] == s[i + a[i]] )
                ++a[i];
            if ( i + a[i] > r )
            {
                l = i;
                r = i + a[i];
            }
        }
        return a;
    }
    // odd[i]: radius including center; even[i]: pairs centered before i.
    static pair<vector<int>, vector<int>> Manacher(const string &s)
    {
        int n = (int)s.size();
        vector<int> odd(n), even(n);
        for ( int i = 0, l = 0, r = -1; i < n; i++ )
        {
            int k = i > r ? 1 : min(odd[l + r - i], r - i + 1);
            while ( i - k >= 0 && i + k < n && s[i - k] == s[i + k] )
                ++k;
            odd[i] = k--;
            if ( i + k > r )
            {
                l = i - k;
                r = i + k;
            }
        }
        for ( int i = 0, l = 0, r = -1; i < n; i++ )
        {
            int k = i > r ? 0 : min(even[l + r - i + 1], r - i + 1);
            while ( i - k - 1 >= 0 && i + k < n && s[i - k - 1] == s[i + k] )
                ++k;
            even[i] = k--;
            if ( i + k > r )
            {
                l = i - k - 1;
                r = i + k;
            }
        }
        return {odd, even};
    }
    static int Rotation(const string &s)
    {
        int n = (int)s.size(), i = 0, j = 1, k = 0;
        if ( !n )
            return 0;
        while ( i < n && j < n && k < n )
        {
            unsigned char a = s[(i + k) % n], b = s[(j + k) % n];
            if ( a == b )
            {
                ++k;
                continue;
            }
            if ( a > b )
            {
                i += k + 1;
                if ( i == j )
                    ++i;
            }
            else
            {
                j += k + 1;
                if ( i == j )
                    ++j;
            }
            k = 0;
        }
        return min(i, j);
    }
};

struct AC_Automaton
{
    struct Node
    {
        array<int, 26> go{};
        int fail = 0;
    };
    vector<Node> a{Node{}};
    vector<int> order;
    bool built = false;
    int Insert(const string &s)
    {
        assert(!built && !s.empty());
        int u = 0;
        for ( char ch : s )
        {
            int c = ch - 'a';
            assert(0 <= c && c < 26);
            if ( !a[u].go[c] )
            {
                int v = (int)a.size();
                a[u].go[c] = v;
                a.push_back(Node{});
            }
            u = a[u].go[c];
        }
        return u;
    }
    void Build()
    {
        assert(!built);
        built = true;
        queue<int> q;
        for ( int v : a[0].go )
            if ( v )
                q.push(v);
        while ( !q.empty() )
        {
            int u = q.front();
            q.pop();
            order.push_back(u);
            for ( int c = 0; c < 26; c++ )
            {
                int v = a[u].go[c];
                if ( v )
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
        for ( char ch : s )
        {
            u = a[u].go[ch - 'a'];
            ++ans[u];
        }
        for ( int i = (int)order.size() - 1; i >= 0; i-- )
            ans[a[order[i]].fail] += ans[order[i]];
        return ans;
    }
};

struct Suffix_Array
{
    vector<int> sa, rk, lcp;
    Suffix_Array(const string &s)
    {
        int n = (int)s.size();
        sa.resize(n);
        rk.resize(n);
        lcp.assign(n, 0);
        for ( int i = 0; i < n; i++ )
        {
            sa[i] = i;
            rk[i] = (unsigned char)s[i];
        }
        vector<int> tmp(n);
        for ( int k = 1; k < n; k *= 2 )
        {
            auto key = [&](int i) { return pair{rk[i], i + k < n ? rk[i + k] : -1}; };
            sort(sa.begin(), sa.end(), [&](int i, int j) { return key(i) < key(j); });
            tmp[sa[0]] = 0;
            for ( int i = 1; i < n; i++ )
                tmp[sa[i]] = tmp[sa[i - 1]] + (key(sa[i]) != key(sa[i - 1]));
            rk = tmp;
            if ( rk[sa.back()] == n - 1 )
                break;
        }
        for ( int i = 0; i < n; i++ )
            rk[sa[i]] = i;
        for ( int i = 0, k = 0; i < n; i++ )
        {
            if ( !rk[i] )
            {
                k = 0;
                continue;
            }
            int j = sa[rk[i] - 1];
            while ( i + k < n && j + k < n && s[i + k] == s[j + k] )
                ++k;
            lcp[rk[i]] = k;
            if ( k )
                --k;
        }
    }
};

struct Suffix_Automaton
{
    struct Node
    {
        array<int, 26> go{};
        int link = -1, len = 0;
        long long occ = 0;
    };
    vector<Node> a{Node{}};
    int last = 0;
    void Extend(int c)
    {
        assert(0 <= c && c < 26);
        int cur = (int)a.size();
        a.push_back(Node{});
        a[cur].len = a[last].len + 1;
        a[cur].occ = 1;
        int p = last;
        while ( p != -1 && !a[p].go[c] )
        {
            a[p].go[c] = cur;
            p = a[p].link;
        }
        if ( p == -1 )
            a[cur].link = 0;
        else
        {
            int q = a[p].go[c];
            if ( a[p].len + 1 == a[q].len )
                a[cur].link = q;
            else
            {
                int clone = (int)a.size();
                Node copy = a[q];
                a.push_back(copy);
                a[clone].len = a[p].len + 1;
                a[clone].occ = 0;
                while ( p != -1 && a[p].go[c] == q )
                {
                    a[p].go[c] = clone;
                    p = a[p].link;
                }
                a[q].link = a[cur].link = clone;
            }
        }
        last = cur;
    }
    vector<long long> Counts() const
    {
        vector<int> bucket(a[last].len + 1), order(a.size());
        vector<long long> ans(a.size());
        for ( auto &v : a )
            ++bucket[v.len];
        partial_sum(bucket.begin(), bucket.end(), bucket.begin());
        for ( int i = 0; i < (int)a.size(); i++ )
        {
            order[--bucket[a[i].len]] = i;
            ans[i] = a[i].occ;
        }
        for ( int i = (int)order.size() - 1; i > 0; i-- )
            ans[a[order[i]].link] += ans[order[i]];
        return ans;
    }
    long long Distinct() const
    {
        long long ans = 0;
        for ( int i = 1; i < (int)a.size(); i++ )
            ans += a[i].len - a[a[i].link].len;
        return ans;
    }
};
