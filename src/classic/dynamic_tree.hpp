#pragma once
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

template <int N> struct Link_Cut_Tree
{
    using U = unsigned long long;

    struct Node
    {
        int ch[2]{}, fa = 0;
        U val = 0, sum = 0;
        bool rev = false;
    };

    Node tree[N + 1];
    int st[N + 1];

    void Init(int n)
    {
        assert(0 <= n && n <= N);
        fill(tree, tree + n + 1, Node{});
    }

    bool Is_Root(int x) const
    {
        int f = tree[x].fa;
        return tree[f].ch[0] != x && tree[f].ch[1] != x;
    }

    void Push_Up(int x)
    {
        tree[x].sum = tree[tree[x].ch[0]].sum ^ tree[x].val ^ tree[tree[x].ch[1]].sum;
    }

    void Reverse(int x)
    {
        if ( !x )
            return;
        swap(tree[x].ch[0], tree[x].ch[1]);
        tree[x].rev = !tree[x].rev;
    }

    void Push_Down(int x)
    {
        if ( !tree[x].rev )
            return;
        Reverse(tree[x].ch[0]);
        Reverse(tree[x].ch[1]);
        tree[x].rev = false;
    }

    void Rotate(int x)
    {
        int y = tree[x].fa, z = tree[y].fa;
        int k = tree[y].ch[1] == x;
        int w = tree[x].ch[k ^ 1];
        if ( !Is_Root(y) )
            tree[z].ch[tree[z].ch[1] == y] = x;
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
        int top = 0, y = x;
        st[top++] = y;
        while ( !Is_Root(y) )
        {
            y = tree[y].fa;
            st[top++] = y;
        }
        while ( top )
            Push_Down(st[--top]);
        while ( !Is_Root(x) )
        {
            int y = tree[x].fa, z = tree[y].fa;
            if ( !Is_Root(y) )
            {
                bool same = (tree[y].ch[1] == x) == (tree[z].ch[1] == y);
                Rotate(same ? y : x);
            }
            Rotate(x);
        }
    }

    void Access(int x)
    {
        int last = 0;
        for ( int y = x; y; y = tree[y].fa )
        {
            Splay(y);
            // The old right child's fa remains y: it becomes a path-parent.
            tree[y].ch[1] = last;
            if ( last )
                tree[last].fa = y;
            Push_Up(y);
            last = y;
        }
        Splay(x);
    }

    void Make_Root(int x)
    {
        Access(x);
        Reverse(x);
    }

    int Find_Root(int x)
    {
        Access(x);
        Push_Down(x);
        while ( tree[x].ch[0] )
        {
            x = tree[x].ch[0];
            Push_Down(x);
        }
        Splay(x);
        return x;
    }

    bool Connected(int x, int y)
    {
        return x == y || Find_Root(x) == Find_Root(y);
    }

    bool Link(int x, int y)
    {
        Make_Root(x);
        if ( Find_Root(y) == x )
            return false;
        tree[x].fa = y;
        return true;
    }

    bool Cut(int x, int y)
    {
        Make_Root(x);
        Access(y);
        if ( tree[y].ch[0] != x || tree[x].ch[1] )
            return false;
        tree[y].ch[0] = 0;
        tree[x].fa = 0;
        Push_Up(y);
        return true;
    }

    void Set(int x, U value)
    {
        Access(x);
        tree[x].val = value;
        Push_Up(x);
    }

    // x and y must be connected. This is a path aggregate, not a subtree sum.
    U Query(int x, int y)
    {
        Make_Root(x);
        Access(y);
        return tree[y].sum;
    }
};
