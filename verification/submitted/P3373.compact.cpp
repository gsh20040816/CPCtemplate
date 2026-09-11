#include <cassert>
#include <vector>
using namespace std;

struct AffineSegTree
{
    using ll = long long;

    struct Node
    {
        ll sum = 0, mul = 1, add = 0;
    };

    int n, mod;
    vector<Node> t;

    AffineSegTree(const vector<ll> &a, int mod) : n(a.size()), mod(mod), t(4 * n + 4)
    {
        assert(n > 0 && mod > 0);
        build(1, 1, n, a);
    }

    ll norm(ll x) const
    {
        x %= mod;
        if (x < 0)
            x += mod;
        return x;
    }

    void pull(int p)
    {
        t[p].sum = (t[p * 2].sum + t[p * 2 + 1].sum) % mod;
    }

    void build(int p, int l, int r, const vector<ll> &a)
    {
        t[p] = Node{};
        if (l == r)
        {
            t[p].sum = norm(a[l - 1]);
            return;
        }
        int m = (l + r) / 2;
        build(p * 2, l, m, a);
        build(p * 2 + 1, m + 1, r, a);
        pull(p);
    }

    // New transform follows the old pending transform: x -> x*a+b.
    void apply(int p, int len, ll a, ll b)
    {
        t[p].sum = (t[p].sum * a % mod + len * b % mod) % mod;
        t[p].mul = t[p].mul * a % mod;
        t[p].add = (t[p].add * a % mod + b) % mod;
    }

    void push(int p, int l, int r)
    {
        if (t[p].mul == 1 && t[p].add == 0)
            return;
        int m = (l + r) / 2;
        apply(p * 2, m - l + 1, t[p].mul, t[p].add);
        apply(p * 2 + 1, r - m, t[p].mul, t[p].add);
        t[p].mul = 1;
        t[p].add = 0;
    }

    void update(int l, int r, ll a, ll b)
    {
        assert(1 <= l && l <= r && r <= n);
        update(1, 1, n, l, r, norm(a), norm(b));
    }

    void update(int p, int l, int r, int ql, int qr, ll a, ll b)
    {
        if (ql <= l && r <= qr)
        {
            apply(p, r - l + 1, a, b);
            return;
        }
        push(p, l, r);
        int m = (l + r) / 2;
        if (ql <= m)
            update(p * 2, l, m, ql, qr, a, b);
        if (qr > m)
            update(p * 2 + 1, m + 1, r, ql, qr, a, b);
        pull(p);
    }

    ll query(int l, int r)
    {
        assert(1 <= l && l <= r && r <= n);
        return query(1, 1, n, l, r);
    }

    ll query(int p, int l, int r, int ql, int qr)
    {
        if (ql <= l && r <= qr)
            return t[p].sum;
        push(p, l, r);
        int m = (l + r) / 2;
        ll answer = 0;
        if (ql <= m)
            answer += query(p * 2, l, m, ql, qr);
        if (qr > m)
            answer += query(p * 2 + 1, m + 1, r, ql, qr);
        return answer % mod;
    }
};

#include <iostream>

int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, q, mod;
    std::cin >> n >> q >> mod;
    std::vector<long long> a(n);
    for (auto &x : a)
        std::cin >> x;
    AffineSegTree tree(a, mod);
    while (q--)
    {
        int op, l, r;
        std::cin >> op >> l >> r;
        if (op == 3)
            std::cout << tree.query(l, r) << '\n';
        else
        {
            long long k;
            std::cin >> k;
            if (op == 1)
                tree.update(l, r, k, 0);
            else
                tree.update(l, r, 1, k);
        }
    }
}
