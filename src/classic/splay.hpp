#pragma once
#include <cassert>
#include <optional>
#include <vector>
using namespace std;

template <int N> struct Ordered_Splay
{
    using ll = long long;

    struct Node
    {
        int ch[2]{}, fa = 0, cnt = 0, siz = 0;
        ll val = 0;
    };

    Node tree[N + 1];
    int tot = 0;
    int root = 0;

    void Init()
    {
        root = 0;
        tot = 0;
        tree[0] = Node{};
    }

    int Size() const
    {
        return tree[root].siz;
    }

    void Push_Up(int x)
    {
        tree[x].siz = tree[tree[x].ch[0]].siz + tree[x].cnt + tree[tree[x].ch[1]].siz;
    }

    int New_Node(ll value, int parent)
    {
        assert(tot < N);
        int x = ++tot;
        tree[x] = {{0, 0}, parent, 1, 1, value};
        return x;
    }

    void Rotate(int x)
    {
        int y = tree[x].fa, z = tree[y].fa;
        int k = tree[y].ch[1] == x;
        int w = tree[x].ch[k ^ 1];
        if ( z )
            tree[z].ch[tree[z].ch[1] == y] = x;
        else
            root = x;
        tree[x].fa = z;
        tree[y].ch[k] = w;
        if ( w )
            tree[w].fa = y;
        tree[x].ch[k ^ 1] = y;
        tree[y].fa = x;
        Push_Up(y);
        Push_Up(x);
    }

    void Splay(int x)
    {
        while ( tree[x].fa )
        {
            int y = tree[x].fa, z = tree[y].fa;
            if ( z )
            {
                bool same = (tree[y].ch[1] == x) == (tree[z].ch[1] == y);
                Rotate(same ? y : x);
            }
            Rotate(x);
        }
    }

    // Splay the last visited node even when the value does not exist.
    int Find(ll value)
    {
        int x = root, last = 0;
        while ( x && tree[x].val != value )
        {
            last = x;
            x = tree[x].ch[value > tree[x].val];
        }
        if ( x )
            Splay(x);
        else if ( last )
            Splay(last);
        return x;
    }

    void Insert(ll value)
    {
        int x = root, parent = 0;
        while ( x && tree[x].val != value )
        {
            parent = x;
            x = tree[x].ch[value > tree[x].val];
        }
        if ( x )
        {
            ++tree[x].cnt;
            Push_Up(x);
        }
        else
        {
            x = New_Node(value, parent);
            if ( parent )
                tree[parent].ch[value > tree[parent].val] = x;
            else
                root = x;
        }
        Splay(x);
    }

    bool Erase(ll value)
    {
        int x = Find(value);
        if ( !x )
            return false;
        if ( tree[x].cnt > 1 )
        {
            --tree[x].cnt;
            Push_Up(x);
            return true;
        }
        int l = tree[x].ch[0], r = tree[x].ch[1];
        if ( l )
            tree[l].fa = 0;
        if ( r )
            tree[r].fa = 0;
        if ( !l )
        {
            root = r;
            return true;
        }
        root = l;
        x = l;
        while ( tree[x].ch[1] )
            x = tree[x].ch[1];
        Splay(x);
        tree[x].ch[1] = r;
        if ( r )
            tree[r].fa = x;
        Push_Up(x);
        return true;
    }

    int Rank(ll value)
    {
        int x = root, last = 0, ans = 1;
        while ( x )
        {
            last = x;
            if ( value <= tree[x].val )
                x = tree[x].ch[0];
            else
            {
                ans += tree[tree[x].ch[0]].siz + tree[x].cnt;
                x = tree[x].ch[1];
            }
        }
        if ( last )
            Splay(last);
        return ans;
    }

    ll Kth(int k)
    {
        assert(1 <= k && k <= Size());
        int x = root;
        while ( true )
        {
            int left = tree[tree[x].ch[0]].siz;
            if ( k <= left )
                x = tree[x].ch[0];
            else if ( k <= left + tree[x].cnt )
            {
                Splay(x);
                return tree[x].val;
            }
            else
            {
                k -= left + tree[x].cnt;
                x = tree[x].ch[1];
            }
        }
    }

    optional<ll> Predecessor(ll value)
    {
        int x = root, last = 0, answer = 0;
        while ( x )
        {
            last = x;
            if ( tree[x].val < value )
            {
                answer = x;
                x = tree[x].ch[1];
            }
            else
                x = tree[x].ch[0];
        }
        if ( last )
            Splay(last);
        if ( !answer )
            return nullopt;
        Splay(answer);
        return tree[answer].val;
    }

    optional<ll> Successor(ll value)
    {
        int x = root, last = 0, answer = 0;
        while ( x )
        {
            last = x;
            if ( tree[x].val > value )
            {
                answer = x;
                x = tree[x].ch[0];
            }
            else
                x = tree[x].ch[1];
        }
        if ( last )
            Splay(last);
        if ( !answer )
            return nullopt;
        Splay(answer);
        return tree[answer].val;
    }
};
