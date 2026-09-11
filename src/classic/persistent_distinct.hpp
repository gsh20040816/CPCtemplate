#pragma once
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

template <int N, int NODES> struct Persistent_Distinct
{
    struct Node
    {
        int l = 0, r = 0, sum = 0;
    };

    int n, tot;
    Node t[NODES + 1];
    int root[N + 1];

    void Init(const vector<long long> &a)
    {
        n = a.size();
        assert(0 < n && n <= N);
        tot = 0;
        t[0] = Node{};
        root[0] = 0;
        vector<long long> vals = a;
        sort(vals.begin(), vals.end());
        vals.erase(unique(vals.begin(), vals.end()), vals.end());
        vector<int> last(vals.size());
        for ( int i = 1; i <= n; i++ )
        {
            int x = lower_bound(vals.begin(), vals.end(), a[i - 1]) - vals.begin();
            root[i] = Insert(root[i - 1], 0, n - 1, last[x]);
            last[x] = i;
        }
    }

    int Insert(int old, int l, int r, int x)
    {
        assert(tot < NODES);
        int p = ++tot;
        t[p] = t[old];
        t[p].sum++;
        if ( l < r )
        {
            int m = (l + r) / 2;
            if ( x <= m )
            {
                int child = Insert(t[old].l, l, m, x);
                t[p].l = child;
            }
            else
            {
                int child = Insert(t[old].r, m + 1, r, x);
                t[p].r = child;
            }
        }
        return p;
    }

    int Query(int l, int r) const
    {
        assert(1 <= l && l <= r && r <= n);
        int u = root[l - 1], v = root[r];
        int L = 0, R = n - 1, answer = 0;
        while ( L < R )
        {
            int m = (L + R) / 2;
            if ( l - 1 <= m )
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
