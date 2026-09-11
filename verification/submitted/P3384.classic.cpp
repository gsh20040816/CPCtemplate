#include <cassert>
#include <algorithm>
#include <vector>
using namespace std;

template <int N> struct Heavy_Light_Decomposition
{
    int n, timer = 0;
    vector<int> g[N + 1];
    int fa[N + 1], dep[N + 1], siz[N + 1], son[N + 1];
    int top[N + 1], dfn[N + 1], rk[N + 1];

    void Init(int vertices)
    {
        assert(0 < vertices && vertices <= N);
        n = vertices;
        for ( int u = 1; u <= n; u++ )
            g[u].clear();
    }

    void Insert(int u, int v)
    {
        g[u].push_back(v);
        g[v].push_back(u);
    }

    void Dfs1(int u, int p)
    {
        fa[u] = p;
        siz[u] = 1;
        son[u] = 0;
        for ( int v : g[u] )
        {
            if ( v == p )
                continue;
            dep[v] = dep[u] + 1;
            Dfs1(v, u);
            siz[u] += siz[v];
            if ( !son[u] || siz[v] > siz[son[u]] )
                son[u] = v;
        }
    }

    void Dfs2(int u, int t)
    {
        top[u] = t;
        dfn[u] = ++timer;
        rk[timer] = u;
        if ( son[u] )
            Dfs2(son[u], t);
        for ( int v : g[u] )
        {
            if ( v != fa[u] && v != son[u] )
                Dfs2(v, v);
        }
    }

    // Connected tree only. Recursive DFS; subtree interval is [dfn, dfn+siz-1].
    void Build(int root = 1)
    {
        assert(1 <= root && root <= n);
        timer = 0;
        dep[root] = 0;
        Dfs1(root, root);
        Dfs2(root, root);
        assert(timer == n);
    }

    int Lca(int u, int v) const
    {
        while ( top[u] != top[v] )
        {
            if ( dep[top[u]] < dep[top[v]] )
                swap(u, v);
            u = fa[top[u]];
        }
        return dep[u] < dep[v] ? u : v;
    }

    // Commutative operations only; edge=true excludes the LCA's position.
    template <class F> void Path(int u, int v, F work, bool edge = false) const
    {
        while ( top[u] != top[v] )
        {
            if ( dep[top[u]] < dep[top[v]] )
                swap(u, v);
            work(dfn[top[u]], dfn[u]);
            u = fa[top[u]];
        }
        if ( dep[u] > dep[v] )
            swap(u, v);
        if ( dfn[u] + edge <= dfn[v] )
            work(dfn[u] + edge, dfn[v]);
    }
};

#include <cassert>
#include <vector>
using namespace std;

template <int N> struct Affine_Segment_Tree
{
    using ll = long long;

    struct Node
    {
        ll sum = 0, mul = 1, add = 0;
    };

    int n, mod;
    Node t[4 * N + 4];

    void Init(const vector<ll> &a, int modulus)
    {
        n = a.size();
        mod = modulus;
        assert(0 < n && n <= N && mod > 0);
        Build(1, 1, n, a);
    }

    ll Norm(ll x) const
    {
        x %= mod;
        if ( x < 0 )
            x += mod;
        return x;
    }

    void Push_Up(int p)
    {
        t[p].sum = (t[p * 2].sum + t[p * 2 + 1].sum) % mod;
    }

    void Build(int p, int l, int r, const vector<ll> &a)
    {
        t[p] = Node{};
        if ( l == r )
        {
            t[p].sum = Norm(a[l - 1]);
            return;
        }
        int m = (l + r) / 2;
        Build(p * 2, l, m, a);
        Build(p * 2 + 1, m + 1, r, a);
        Push_Up(p);
    }

    // New transform follows the old pending transform: x -> x*a+b.
    void Apply(int p, int len, ll a, ll b)
    {
        t[p].sum = (t[p].sum * a % mod + len * b % mod) % mod;
        t[p].mul = t[p].mul * a % mod;
        t[p].add = (t[p].add * a % mod + b) % mod;
    }

    void Push_Down(int p, int l, int r)
    {
        if ( t[p].mul == 1 && t[p].add == 0 )
            return;
        int m = (l + r) / 2;
        Apply(p * 2, m - l + 1, t[p].mul, t[p].add);
        Apply(p * 2 + 1, r - m, t[p].mul, t[p].add);
        t[p].mul = 1;
        t[p].add = 0;
    }

    void Update(int l, int r, ll a, ll b)
    {
        assert(1 <= l && l <= r && r <= n);
        Update(1, 1, n, l, r, Norm(a), Norm(b));
    }

    void Update(int p, int l, int r, int ql, int qr, ll a, ll b)
    {
        if ( ql <= l && r <= qr )
        {
            Apply(p, r - l + 1, a, b);
            return;
        }
        Push_Down(p, l, r);
        int m = (l + r) / 2;
        if ( ql <= m )
            Update(p * 2, l, m, ql, qr, a, b);
        if ( qr > m )
            Update(p * 2 + 1, m + 1, r, ql, qr, a, b);
        Push_Up(p);
    }

    ll Query(int l, int r)
    {
        assert(1 <= l && l <= r && r <= n);
        return Query(1, 1, n, l, r);
    }

    ll Query(int p, int l, int r, int ql, int qr)
    {
        if ( ql <= l && r <= qr )
            return t[p].sum;
        Push_Down(p, l, r);
        int m = (l + r) / 2;
        ll answer = 0;
        if ( ql <= m )
            answer += Query(p * 2, l, m, ql, qr);
        if ( qr > m )
            answer += Query(p * 2 + 1, m + 1, r, ql, qr);
        return answer % mod;
    }
};

#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m, root, mod;
    std::cin >> n >> m >> root >> mod;
    std::vector<long long> values(n + 1);
    for ( int u = 1; u <= n; u++ )
        std::cin >> values[u];
    static Heavy_Light_Decomposition<100000> h;
    h.Init(n);
    for ( int i = 1; i < n; i++ )
    {
        int u, v;
        std::cin >> u >> v;
        h.Insert(u, v);
    }
    h.Build(root);
    std::vector<long long> ordered(n);
    for ( int u = 1; u <= n; u++ )
        ordered[h.dfn[u] - 1] = values[u];
    static Affine_Segment_Tree<100000> seg;
    seg.Init(ordered, mod);
    while ( m-- )
    {
        int op, u;
        std::cin >> op >> u;
        if ( op == 1 )
        {
            int v;
            long long x;
            std::cin >> v >> x;
            h.Path(u,
                   v,
                   [&](int l, int r)
                   {
                       seg.Update(l, r, 1, x);
                   });
        }
        else if ( op == 2 )
        {
            int v;
            std::cin >> v;
            long long answer = 0;
            h.Path(u,
                   v,
                   [&](int l, int r)
                   {
                       answer = (answer + seg.Query(l, r)) % mod;
                   });
            std::cout << answer << '\n';
        }
        else if ( op == 3 )
        {
            long long x;
            std::cin >> x;
            seg.Update(h.dfn[u], h.dfn[u] + h.siz[u] - 1, 1, x);
        }
        else
            std::cout << seg.Query(h.dfn[u], h.dfn[u] + h.siz[u] - 1) << '\n';
    }
}
