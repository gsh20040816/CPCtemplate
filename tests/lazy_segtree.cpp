#include "../src/compact/lazy_segtree.hpp"

using S = pair<long long, int>;
using F = pair<long long, long long>;

S op(S a, S b)
{
    return {a.first + b.first, a.second + b.second};
}

S e()
{
    return {0, 0};
}

S mapping(F f, S a)
{
    return {a.first * f.first + a.second * f.second, a.second};
}

F composition(F f, F g)
{
    return {f.first * g.first, f.first * g.second + f.second};
}

F id()
{
    return {1, 0};
}

string cat(string a, string b)
{
    return a + b;
}

string se()
{
    return "";
}

string smap(int f, string a)
{
    if (f >= 0)
        for (auto &c : a) c = char('a' + f);
    return a;
}

int comp(int f, int g)
{
    return f < 0 ? g : f;
}

int sid()
{
    return -1;
}

int main()
{
    mt19937 rng(51673);
    for (int n = 0; n <= 65; n++)
    {
        vector<S> initial(n, {1, 1});
        vector<long long> a(n, 1);
        lazy_segtree<S, F, op, e, mapping, composition, id> s(initial);
        for (int t = 0; t < 1000; t++)
        {
            int l = rng() % (n + 1), r = rng() % (n + 1);
            if (l > r) swap(l, r);
            F f{rng() % 2, rng() % 8};
            s.apply(l, r, f);
            for (int i = l; i < r; i++) a[i] = a[i] * f.first + f.second;
            if (n && t % 3 == 0)
            {
                int p = rng() % n;
                a[p] = rng() % 20;
                s.set(p, {a[p], 1});
                assert(s.get(p).first == a[p]);
            }
            long long sum = accumulate(a.begin() + l, a.begin() + r, 0LL);
            assert(s.prod(l, r) == S(sum, r - l));
            assert(s.all() == S(accumulate(a.begin(), a.end(), 0LL), n));
            int cap = rng() % 100;
            auto ok = [&](S x)
            {
                return x.first <= cap;
            };
            int rr = l, ll = r;
            sum = 0;
            while (rr < n && sum + a[rr] <= cap) sum += a[rr++];
            sum = 0;
            while (ll > 0 && sum + a[ll - 1] <= cap) sum += a[--ll];
            assert(s.max_right(l, ok) == rr);
            assert(s.min_left(r, ok) == ll);
        }
        vector<string> a2(n, "a");
        lazy_segtree<string, int, cat, se, smap, comp, sid> s2(a2);
        for (int t = 0; t < 100; t++)
        {
            int l = rng() % (n + 1), r = rng() % (n + 1), f = rng() % 3;
            if (l > r) swap(l, r);
            s2.apply(l, r, f);
            for (int i = l; i < r; i++) a2[i] = char('a' + f);
            auto ok = [](string x)
            {
                return x.find("ab") == string::npos;
            };
            for (int x = 0; x <= n; x++)
            {
                string a, b;
                int rr = x, ll = x;
                while (rr < n && ok(a + a2[rr])) a += a2[rr++];
                while (ll > 0 && ok(a2[ll - 1] + b)) b = a2[--ll] + b;
                assert(s2.max_right(x, ok) == rr);
                assert(s2.min_left(x, ok) == ll);
            }
            string result;
            for (int i = l; i < r; i++) result += a2[i];
            assert(s2.prod(l, r) == result);
        }
    }
    lazy_segtree<S, F, op, e, mapping, composition, id> large(
        vector<S>(500000, {1, 1}));
    large.apply(0, 500000, {2, 1});
    large.apply(0, 500000, {3, 4});
    assert(large.all().first == 6500000);
    assert(large.max_right(0, [](S x) { return x.first <= 13 * 12345; }) == 12345);
    assert(large.min_left(500000, [](S x) { return x.first <= 13 * 12345; }) ==
           500000 - 12345);
    cout << "Generic lazy segtree: affine vector oracle, assignment string order, both "
            "boundary scans and 500000 pending tags PASS\n";
}
