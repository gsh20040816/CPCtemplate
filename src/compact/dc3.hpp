#pragma once
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

struct DC3
{
    vector<int> sa, rk, lcp;

    DC3(const string &s)
    {
        vector<int> a;
        for (unsigned char c : s)
            a.push_back(c);
        *this = DC3(a, 256);
    }

    DC3(const vector<int> &s, int alphabet)
    {
        assert(s.size() < INT_MAX - 3 && 1 <= alphabet && alphabet < INT_MAX - 3);
        int n = s.size();
        vector<int> a(n);
        for (int i = 0; i < n; i++)
        {
            assert(0 <= s[i] && s[i] < alphabet);
            a[i] = s[i] + 1;
        }
        sa = sort_suffixes(move(a), alphabet);
        rk.resize(n);
        lcp.assign(n, 0);
        for (int i = 0; i < n; i++)
            rk[sa[i]] = i;
        for (int i = 0, k = 0; i < n; i++)
        {
            if (!rk[i])
            {
                k = 0;
                continue;
            }
            int j = sa[rk[i] - 1];
            while (k < n - i && k < n - j && s[i + k] == s[j + k])
                k++;
            lcp[rk[i]] = k;
            if (k)
                k--;
        }
    }

private:
    static vector<int> sort_suffixes(vector<int> s, int alphabet)
    {
        int n = s.size();
        if (!n)
            return {};
        if (n == 1)
            return {0};
        s.resize(n + 3);
        int n0 = (n + 2) / 3;
        int extra = n % 3 == 1;
        vector<int> sample, zero;
        for (int i = 0; i < n + extra; i++)
            if (i % 3)
                sample.push_back(i);
        auto radix = [&](vector<int> &a, int shift)
        {
            vector<int> count(alphabet + 1), b(a.size());
            for (int i : a)
                count[s[i + shift]]++;
            for (int i = 1; i <= alphabet; i++)
                count[i] += count[i - 1];
            for (int i = (int)a.size() - 1; i >= 0; i--)
                b[--count[s[a[i] + shift]]] = a[i];
            a.swap(b);
        };
        for (int shift = 2; shift >= 0; shift--)
            radix(sample, shift);
        int names = 0;
        vector<int> reduced(sample.size()), order(sample.size());
        array<int, 3> last{-1, -1, -1};
        for (int i : sample)
        {
            array<int, 3> key{s[i], s[i + 1], s[i + 2]};
            if (key != last)
                names++;
            last = key;
            reduced[i / 3 + (i % 3 == 2 ? n0 : 0)] = names;
        }
        if (names < (int)sample.size())
            order = sort_suffixes(move(reduced), names);
        else
            for (int i = 0; i < (int)reduced.size(); i++)
                order[reduced[i] - 1] = i;
        vector<int> rank(n + 3);
        for (int k = 0; k < (int)order.size(); k++)
        {
            int i = order[k];
            int p = i < n0 ? 3 * i + 1 : 3 * (i - n0) + 2;
            sample[k] = p;
            rank[p] = k + 1;
            if (p % 3 == 1)
                zero.push_back(p - 1);
        }
        radix(zero, 0);
        vector<int> result;
        int a = extra, b = 0;
        while (a < (int)sample.size() && b < (int)zero.size())
        {
            int i = sample[a], j = zero[b];
            bool first;
            if (i % 3 == 1)
                first = pair{s[i], rank[i + 1]} < pair{s[j], rank[j + 1]};
            else
                first = tuple{s[i], s[i + 1], rank[i + 2]}
                      < tuple{s[j], s[j + 1], rank[j + 2]};
            if (first)
                result.push_back(sample[a++]);
            else
                result.push_back(zero[b++]);
        }
        while (a < (int)sample.size())
            result.push_back(sample[a++]);
        while (b < (int)zero.size())
            result.push_back(zero[b++]);
        return result;
    }
};
