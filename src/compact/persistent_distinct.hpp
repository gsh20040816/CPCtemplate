#pragma once
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

struct PersistentDistinct
{
    struct Node
    {
        int l = 0, r = 0, sum = 0;
    };

    int n;
    vector<Node> t{Node{}};
    vector<int> root;

    PersistentDistinct(const vector<long long> &a) : n(a.size()), root(n + 1)
    {
        assert(n > 0);
        int height = 1;
        while ((1LL << (height - 1)) < n) height++;
        t.reserve(size_t(n) * height + 1);
        vector<long long> vals = a;
        sort(vals.begin(), vals.end());
        vals.erase(unique(vals.begin(), vals.end()), vals.end());
        vector<int> last(vals.size());
        for (int i = 1; i <= n; i++)
        {
            int x = lower_bound(vals.begin(), vals.end(), a[i - 1]) - vals.begin();
            root[i] = insert(root[i - 1], 0, n - 1, last[x]);
            last[x] = i;
        }
    }

    int insert(int old, int l, int r, int x)
    {
        int p = t.size();
        Node copy = t[old];
        t.push_back(copy);
        t[p].sum++;
        if (l < r)
        {
            int m = (l + r) / 2;
            if (x <= m)
            {
                int child = insert(t[old].l, l, m, x);
                t[p].l = child;
            }
            else
            {
                int child = insert(t[old].r, m + 1, r, x);
                t[p].r = child;
            }
        }
        return p;
    }

    int query(int l, int r) const
    {
        assert(1 <= l && l <= r && r <= n);
        int u = root[l - 1], v = root[r];
        int L = 0, R = n - 1, answer = 0;
        while (L < R)
        {
            int m = (L + R) / 2;
            if (l - 1 <= m)
            {
                u = t[u].l;
                v = t[v].l;
                R = m;
            }
            else
            {
                answer += t[t[v].l].sum - t[t[u].l].sum;
                u = t[u].r;
                v = t[v].r;
                L = m + 1;
            }
        }
        return answer + t[v].sum - t[u].sum;
    }
};
