#include "../src/compact/lazy_segtree.hpp"

struct S
{
    int sum, len;
};

// A tag is an arbitrary function {0,1}->{0,1}; includes identity, flip and both
// assignments.
using F = array<int, 2>;
long long calls;

S op(S a, S b)
{
    ++calls;
    return {a.sum + b.sum, a.len + b.len};
}

S e()
{
    return {0, 0};
}

S mapping(F f, S s)
{
    return {(s.len - s.sum) * f[0] + s.sum * f[1], s.len};
}

F composition(F f, F g)
{
    return {f[g[0]], f[g[1]]};
}

F id()
{
    return {0, 1};
}

using tree = lazy_segtree<S, F, op, e, mapping, composition, id>;

void check(tree &s, const vector<int> &a)
{
    int n = a.size();
    for (int k = 0; k < n; k++)
    {
        int nxt = k, pre = k;
        while (nxt < n && !a[nxt]) ++nxt;
        while (pre >= 0 && !a[pre]) --pre;
        assert(s.max_right(k, [](S x) { return x.sum == 0; }) == nxt);
        assert(s.min_left(k + 1, [](S x) { return x.sum == 0; }) - 1 == pre);
        assert(s.get(k).sum == a[k]);
    }
    assert(s.all().sum == accumulate(a.begin(), a.end(), 0));
}

int main()
{
    mt19937 rng(82661);
    // Exhaust all compositions on tiny bit strings, and preserve pending tags
    // by applying both operations before any read.
    vector<F> fs{{0, 1}, {1, 0}, {0, 0}, {1, 1}};
    for (int n = 1; n <= 5; n++)
        for (int mask = 0; mask < (1 << n); mask++)
            for (F f : fs)
                for (F g : fs)
                    for (int l = 0; l <= n; l++)
                        for (int r = l; r <= n; r++)
                        {
                            vector<int> a(n);
                            vector<S> init(n);
                            for (int i = 0; i < n; i++)
                                init[i] = {a[i] = mask >> i & 1, 1};
                            tree s(init);
                            s.apply(0, n, f);
                            s.apply(l, r, g);
                            for (int &x : a) x = f[x];
                            for (int i = l; i < r; i++) a[i] = g[a[i]];
                            check(s, a);
                        }
    for (int n : {7, 63, 128, 257})
    {
        tree s(vector<S>(n, {0, 1}));
        vector<int> a(n);
        for (int t = 0; t < 3000; t++)
        {
            int l = rng() % n, r = l + 1 + rng() % (n - l);
            F f = fs[rng() % fs.size()];
            s.apply(l, r, f);
            for (int i = l; i < r; i++) a[i] = f[a[i]];
            if (t % 5 == 0) check(s, a);
        }
    }
    // Instrument op calls: a search must not degrade to scanning all leaves.
    int n = 500000, height = 19;
    tree s(vector<S>(n, {0, 1}));
    for (int t = 0; t < 2000; t++)
    {
        int k = rng() % n;
        s.apply(0, n, {0, 0});
        s.apply(k, k + 1, {1, 1});
        calls = 0;
        assert(s.max_right(0, [](S x) { return x.sum == 0; }) == k);
        assert(calls <= 8 * height);
        calls = 0;
        assert(s.min_left(n, [](S x) { return x.sum == 0; }) == k + 1);
        assert(calls <= 8 * height);
    }
    cout << "Lazy binary searches: exhaustive flip/assignment composition, "
            "range-update predecessor/successor and logarithmic op-count bound PASS\n";
}
