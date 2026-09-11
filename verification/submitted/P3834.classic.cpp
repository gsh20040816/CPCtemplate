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

struct Max_Plus_Matrix
{
    using I = __int128_t;
    static constexpr I neg = -(I(1) << 120);
    int n;
    vector<vector<I>> a;

    Max_Plus_Matrix(int n, bool identity = false) : n(n), a(n, vector<I>(n, neg))
    {
        if ( identity )
            for ( int i = 0; i < n; i++ )
                a[i][i] = 0;
    }

    Max_Plus_Matrix operator*(const Max_Plus_Matrix &b) const
    {
        assert(n == b.n);
        Max_Plus_Matrix c(n);
        for ( int i = 0; i < n; i++ )
            for ( int k = 0; k < n; k++ )
                if ( a[i][k] != neg )
                    for ( int j = 0; j < n; j++ )
                        if ( b.a[k][j] != neg )
                            c.a[i][j] = max(c.a[i][j], a[i][k] + b.a[k][j]);
        return c;
    }

    Max_Plus_Matrix Power(unsigned long long e) const
    {
        Max_Plus_Matrix b = *this, r(n, true);
        for ( ; e; e >>= 1, b = b * b )
            if ( e & 1 )
                r = r * b;
        return r;
    }
};

struct Li_Chao_Tree
{
    using ll = long long;
    using I = __int128_t;

    struct Line
    {
        ll k = 0, b = 0;
        int id = -1;

        I value(ll x) const
        {
            return I(k) * x + b;
        }
    };

    struct Node
    {
        Line line;
        int left = -1, right = -1;
    };

    vector<ll> xs;
    vector<Node> a{Node{}};

    Li_Chao_Tree(vector<ll> x) : xs(x)
    {
        sort(xs.begin(), xs.end());
        xs.erase(unique(xs.begin(), xs.end()), xs.end());
        assert(!xs.empty());
    }

    bool better(Line u, Line v, ll x) const
    {
        return v.id == -1 ||
               (u.id != -1 && pair{u.value(x), u.id} < pair{v.value(x), v.id});
    }

    void Insert(Line line)
    {
        assert(line.id >= 0);
        Insert(0, 0, (int)xs.size() - 1, line);
    }

    void Insert(int p, int l, int r, Line line)
    {
        int m = (l + r) / 2;
        if ( better(line, a[p].line, xs[m]) )
            swap(line, a[p].line);
        if ( l == r || line.id == -1 )
            return;
        bool left = better(line, a[p].line, xs[l]);
        bool right = better(line, a[p].line, xs[r]);
        if ( !left && !right )
            return;
        int next = left ? a[p].left : a[p].right;
        if ( next == -1 )
        {
            next = (int)a.size();
            a.push_back(Node{});
            if ( left )
                a[p].left = next;
            else
                a[p].right = next;
        }
        if ( left )
            Insert(next, l, m, line);
        else
            Insert(next, m + 1, r, line);
    }

    pair<I, int> Query(ll x) const
    {
        int idx = lower_bound(xs.begin(), xs.end(), x) - xs.begin();
        assert(idx < (int)xs.size() && xs[idx] == x);
        int p = 0, l = 0, r = (int)xs.size() - 1;
        Line best;
        while ( p != -1 )
        {
            if ( better(a[p].line, best, x) )
                best = a[p].line;
            if ( l == r )
                break;
            int m = (l + r) / 2;
            if ( idx <= m )
            {
                p = a[p].left;
                r = m;
            }
            else
            {
                p = a[p].right;
                l = m + 1;
            }
        }
        assert(best.id != -1);
        return {best.value(x), best.id};
    }
};

struct Persistent_Kth
{
    struct Node
    {
        int l = 0, r = 0, sum = 0;
    };

    vector<Node> t{Node{}};
    vector<int> root{0};
    vector<long long> vals;

    Persistent_Kth(const vector<long long> &a) : vals(a)
    {
        sort(vals.begin(), vals.end());
        vals.erase(unique(vals.begin(), vals.end()), vals.end());
        for ( long long x : a )
        {
            int p = lower_bound(vals.begin(), vals.end(), x) - vals.begin();
            root.push_back(Insert(root.back(), 0, (int)vals.size() - 1, p));
        }
    }

    int Insert(int old, int l, int r, int x)
    {
        int p = t.size();
        Node copy = t[old];
        t.push_back(copy);
        ++t[p].sum;
        if ( l < r )
        {
            int m = (l + r) / 2;
            if ( x <= m )
            {
                int v = Insert(t[old].l, l, m, x);
                t[p].l = v;
            }
            else
            {
                int v = Insert(t[old].r, m + 1, r, x);
                t[p].r = v;
            }
        }
        return p;
    }

    long long Kth(int l, int r, int k) const
    {
        assert(1 <= l && l <= r && r < (int)root.size() && 1 <= k && k <= r - l + 1);
        int u = root[l - 1], v = root[r], L = 0, R = (int)vals.size() - 1;
        while ( L < R )
        {
            int m = (L + R) / 2, c = t[t[v].l].sum - t[t[u].l].sum;
            if ( k <= c )
            {
                u = t[u].l;
                v = t[v].l;
                R = m;
            }
            else
            {
                k -= c;
                u = t[u].r;
                v = t[v].r;
                L = m + 1;
            }
        }
        return vals[L];
    }
};

#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    std::cin >> n >> m;
    std::vector<long long> a(n);
    for ( auto &x : a )
        std::cin >> x;
    Persistent_Kth tree(a);
    while ( m-- )
    {
        int l, r, k;
        std::cin >> l >> r >> k;
        std::cout << tree.Kth(l, r, k) << '\n';
    }
}
