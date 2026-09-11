#include <cassert>
#include <optional>
#include <random>
#include <vector>
using namespace std;

template <int N> struct Ordered_Treap
{
    using ll = long long;

    struct Node
    {
        int l = 0, r = 0, siz = 0;
        ll val = 0;
        unsigned long long pri = 0;
    };

    Node tree[N + 1];
    int tot = 0;
    mt19937_64 rng;
    int root = 0;

    void Init(unsigned long long seed = 712367821)
    {
        root = 0;
        tot = 0;
        tree[0] = Node{};
        rng.seed(seed);
    }

    void Push_Up(int p)
    {
        tree[p].siz = tree[tree[p].l].siz + tree[tree[p].r].siz + 1;
    }

    int New_Node(ll x)
    {
        assert(tot < N);
        int p = ++tot;
        tree[p] = {0, 0, 1, x, rng()};
        return p;
    }

    // left: val < x, or val <= x when equal is true. No x-1 overflow.
    void Split(int p, ll x, int &l, int &r, bool equal = false)
    {
        if ( !p )
        {
            l = 0;
            r = 0;
            return;
        }
        if ( tree[p].val < x || (equal && tree[p].val == x) )
        {
            l = p;
            Split(tree[p].r, x, tree[p].r, r, equal);
        }
        else
        {
            r = p;
            Split(tree[p].l, x, l, tree[p].l, equal);
        }
        Push_Up(p);
    }

    int Merge(int l, int r)
    {
        if ( !l || !r )
            return l ? l : r;
        if ( tree[l].pri > tree[r].pri )
        {
            tree[l].r = Merge(tree[l].r, r);
            Push_Up(l);
            return l;
        }
        tree[r].l = Merge(l, tree[r].l);
        Push_Up(r);
        return r;
    }

    void Insert(ll x)
    {
        int p = New_Node(x), l, r;
        Split(root, x, l, r);
        root = Merge(Merge(l, p), r);
    }

    bool Erase(ll x)
    {
        int l, mid, r;
        Split(root, x, l, mid);
        Split(mid, x, mid, r, true);
        bool found = mid != 0;
        if ( mid )
            mid = Merge(tree[mid].l, tree[mid].r);
        root = Merge(l, Merge(mid, r));
        return found;
    }

    int Size() const
    {
        return tree[root].siz;
    }

    int Count_Less(ll x, bool equal = false) const
    {
        int p = root, ans = 0;
        while ( p )
        {
            if ( tree[p].val < x || (equal && tree[p].val == x) )
            {
                ans += tree[tree[p].l].siz + 1;
                p = tree[p].r;
            }
            else
                p = tree[p].l;
        }
        return ans;
    }

    int Rank(ll x) const
    {
        return Count_Less(x) + 1;
    }

    ll Kth(int k) const
    {
        assert(1 <= k && k <= Size());
        int p = root;
        while ( true )
        {
            int left = tree[tree[p].l].siz;
            if ( k == left + 1 )
                return tree[p].val;
            if ( k <= left )
                p = tree[p].l;
            else
            {
                k -= left + 1;
                p = tree[p].r;
            }
        }
    }

    optional<ll> Predecessor(ll x) const
    {
        int k = Count_Less(x);
        if ( !k )
            return nullopt;
        return Kth(k);
    }

    optional<ll> Successor(ll x) const
    {
        int k = Count_Less(x, true);
        if ( k == Size() )
            return nullopt;
        return Kth(k + 1);
    }
};

template <int N> struct Sequence_Treap
{
    using ll = long long;

    struct Node
    {
        int l = 0, r = 0, siz = 0;
        ll val = 0, sum = 0, tag = 0;
        unsigned long long pri = 0;
        bool rev = false;
    };

    Node tree[N + 1];
    int tot = 0;
    mt19937_64 rng;
    int root = 0;

    void Init(unsigned long long seed = 712367821)
    {
        root = 0;
        tot = 0;
        tree[0] = Node{};
        rng.seed(seed);
    }

    int Size() const
    {
        return tree[root].siz;
    }

    void Push_Up(int p)
    {
        tree[p].siz = tree[tree[p].l].siz + tree[tree[p].r].siz + 1;
        tree[p].sum = tree[tree[p].l].sum + tree[p].val + tree[tree[p].r].sum;
    }

    void Apply_Add(int p, ll x)
    {
        if ( !p )
            return;
        tree[p].val += x;
        tree[p].sum += x * tree[p].siz;
        tree[p].tag += x;
    }

    void Apply_Reverse(int p)
    {
        if ( !p )
            return;
        swap(tree[p].l, tree[p].r);
        tree[p].rev = !tree[p].rev;
    }

    void Push_Down(int p)
    {
        if ( tree[p].rev )
        {
            Apply_Reverse(tree[p].l);
            Apply_Reverse(tree[p].r);
            tree[p].rev = false;
        }
        if ( tree[p].tag )
        {
            Apply_Add(tree[p].l, tree[p].tag);
            Apply_Add(tree[p].r, tree[p].tag);
            tree[p].tag = 0;
        }
    }

    // Split into the first k elements and the rest.
    void Split(int p, int k, int &l, int &r)
    {
        if ( !p )
        {
            l = 0;
            r = 0;
            return;
        }
        Push_Down(p);
        int left = tree[tree[p].l].siz;
        if ( k > left )
        {
            l = p;
            Split(tree[p].r, k - left - 1, tree[p].r, r);
        }
        else
        {
            r = p;
            Split(tree[p].l, k, l, tree[p].l);
        }
        Push_Up(p);
    }

    int Merge(int l, int r)
    {
        if ( !l || !r )
            return l ? l : r;
        if ( tree[l].pri > tree[r].pri )
        {
            Push_Down(l);
            tree[l].r = Merge(tree[l].r, r);
            Push_Up(l);
            return l;
        }
        Push_Down(r);
        tree[r].l = Merge(l, tree[r].l);
        Push_Up(r);
        return r;
    }

    // Insert after the first k elements, 0 <= k <= size().
    void Insert(int k, ll value)
    {
        assert(0 <= k && k <= Size());
        assert(tot < N);
        int p = ++tot, l, r;
        tree[p] = {0, 0, 1, value, value, 0, rng(), false};
        Split(root, k, l, r);
        root = Merge(Merge(l, p), r);
    }

    // All range operations use 1-based inclusive intervals.
    void Erase(int l, int r)
    {
        assert(1 <= l && l <= r && r <= Size());
        int x, y, z;
        Split(root, r, y, z);
        Split(y, l - 1, x, y);
        root = Merge(x, z);
    }

    void Reverse(int l, int r)
    {
        assert(1 <= l && l <= r && r <= Size());
        int x, y, z;
        Split(root, r, y, z);
        Split(y, l - 1, x, y);
        Apply_Reverse(y);
        root = Merge(Merge(x, y), z);
    }

    void Add(int l, int r, ll value)
    {
        assert(1 <= l && l <= r && r <= Size());
        int x, y, z;
        Split(root, r, y, z);
        Split(y, l - 1, x, y);
        Apply_Add(y, value);
        root = Merge(Merge(x, y), z);
    }

    ll Query(int l, int r)
    {
        assert(1 <= l && l <= r && r <= Size());
        int x, y, z;
        Split(root, r, y, z);
        Split(y, l - 1, x, y);
        ll ans = tree[y].sum;
        root = Merge(Merge(x, y), z);
        return ans;
    }

    void Collect(int p, vector<ll> &out)
    {
        if ( !p )
            return;
        Push_Down(p);
        Collect(tree[p].l, out);
        out.push_back(tree[p].val);
        Collect(tree[p].r, out);
    }

    vector<ll> Values()
    {
        vector<ll> answer;
        Collect(root, answer);
        return answer;
    }
};

#include <cstdio>
Ordered_Treap<100005> Tree;

int main()
{
    int n;
    scanf("%d", &n);
    Tree.Init();
    while ( n-- )
    {
        int op;
        long long x;
        scanf("%d%lld", &op, &x);
        if ( op == 1 )
            Tree.Insert(x);
        else if ( op == 2 )
            Tree.Erase(x);
        else if ( op == 3 )
            printf("%d\n", Tree.Rank(x));
        else if ( op == 4 )
            printf("%lld\n", Tree.Kth(x));
        else if ( op == 5 )
            printf("%lld\n", *Tree.Predecessor(x));
        else
            printf("%lld\n", *Tree.Successor(x));
    }
    return 0;
}
