#pragma once
#include <cassert>
#include <optional>
#include <vector>
using namespace std;

struct OrderedSplay
{
    using ll = long long;

    struct Node
    {
        int ch[2]{}, fa = 0, cnt = 0, siz = 0;
        ll val = 0;
    };

    vector<Node> a{Node{}};
    int root = 0;

    int size() const { return a[root].siz; }

    void pull(int x) { a[x].siz = a[a[x].ch[0]].siz + a[x].cnt + a[a[x].ch[1]].siz; }

    int node(ll value, int parent)
    {
        int x = a.size();
        a.push_back({{0, 0}, parent, 1, 1, value});
        return x;
    }

    void rotate(int x)
    {
        int y = a[x].fa, z = a[y].fa;
        int k = a[y].ch[1] == x;
        int w = a[x].ch[k ^ 1];
        if (z)
            a[z].ch[a[z].ch[1] == y] = x;
        else
            root = x;
        a[x].fa = z;
        a[y].ch[k] = w;
        if (w) a[w].fa = y;
        a[x].ch[k ^ 1] = y;
        a[y].fa = x;
        pull(y);
        pull(x);
    }

    void splay(int x)
    {
        while (a[x].fa)
        {
            int y = a[x].fa, z = a[y].fa;
            if (z)
            {
                bool same = (a[y].ch[1] == x) == (a[z].ch[1] == y);
                rotate(same ? y : x);
            }
            rotate(x);
        }
    }

    // Splay the last visited node even when the value does not exist.
    int find(ll value)
    {
        int x = root, last = 0;
        while (x && a[x].val != value)
        {
            last = x;
            x = a[x].ch[value > a[x].val];
        }
        if (x)
            splay(x);
        else if (last)
            splay(last);
        return x;
    }

    void insert(ll value)
    {
        int x = root, parent = 0;
        while (x && a[x].val != value)
        {
            parent = x;
            x = a[x].ch[value > a[x].val];
        }
        if (x)
        {
            ++a[x].cnt;
            pull(x);
        }
        else
        {
            x = node(value, parent);
            if (parent)
                a[parent].ch[value > a[parent].val] = x;
            else
                root = x;
        }
        splay(x);
    }

    bool erase(ll value)
    {
        int x = find(value);
        if (!x) return false;
        if (a[x].cnt > 1)
        {
            --a[x].cnt;
            pull(x);
            return true;
        }
        int l = a[x].ch[0], r = a[x].ch[1];
        if (l) a[l].fa = 0;
        if (r) a[r].fa = 0;
        if (!l)
        {
            root = r;
            return true;
        }
        root = l;
        x = l;
        while (a[x].ch[1]) x = a[x].ch[1];
        splay(x);
        a[x].ch[1] = r;
        if (r) a[r].fa = x;
        pull(x);
        return true;
    }

    int rank(ll value)
    {
        int x = root, last = 0, ans = 1;
        while (x)
        {
            last = x;
            if (value <= a[x].val)
                x = a[x].ch[0];
            else
            {
                ans += a[a[x].ch[0]].siz + a[x].cnt;
                x = a[x].ch[1];
            }
        }
        if (last) splay(last);
        return ans;
    }

    ll kth(int k)
    {
        assert(1 <= k && k <= size());
        int x = root;
        while (true)
        {
            int left = a[a[x].ch[0]].siz;
            if (k <= left)
                x = a[x].ch[0];
            else if (k <= left + a[x].cnt)
            {
                splay(x);
                return a[x].val;
            }
            else
            {
                k -= left + a[x].cnt;
                x = a[x].ch[1];
            }
        }
    }

    optional<ll> prev(ll value)
    {
        int x = root, last = 0, answer = 0;
        while (x)
        {
            last = x;
            if (a[x].val < value)
            {
                answer = x;
                x = a[x].ch[1];
            }
            else
                x = a[x].ch[0];
        }
        if (last) splay(last);
        if (!answer) return nullopt;
        splay(answer);
        return a[answer].val;
    }

    optional<ll> next(ll value)
    {
        int x = root, last = 0, answer = 0;
        while (x)
        {
            last = x;
            if (a[x].val > value)
            {
                answer = x;
                x = a[x].ch[0];
            }
            else
                x = a[x].ch[1];
        }
        if (last) splay(last);
        if (!answer) return nullopt;
        splay(answer);
        return a[answer].val;
    }
};
