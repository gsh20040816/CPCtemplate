#include "../src/compact/chain_3d.hpp"
#include <iostream>
#include <random>
#include <cstdlib>
using P = Chain3D::Point;
long long checked = 0;

void require(bool ok)
{
    if (!ok)
    {
        cout << "ORACLE_REJECT\n";
        exit(0);
    }
}

bool before(const vector<P> &p, int u, int v, bool strict)
{
    if (strict)
    {
        return p[u][0] < p[v][0] && p[u][1] < p[v][1] && p[u][2] < p[v][2];
    }
    return (p[u] < p[v] || (p[u] == p[v] && u < v)) &&
           p[u][0] <= p[v][0] && p[u][1] <= p[v][1] && p[u][2] <= p[v][2];
}

void check(vector<P> p, int mod, bool strict, bool enumerate = false)
{
    auto original = p;
    Chain3D got(p, mod, strict);
    require(p == original);
    int n = p.size();
    vector<int> len(n, 1), ways(n, 1 % mod), parent(n, -1), order(n);
    iota(order.begin(), order.end(), 0);
    sort(order.begin(), order.end(), [&](int u, int v)
    {
        return make_pair(p[u], u) < make_pair(p[v], v);
    });
    for (int v : order)
    {
        for (int u : order)
        {
            if (!before(p, u, v, strict)) continue;
            if (len[u] + 1 > len[v])
            {
                len[v] = len[u] + 1;
                ways[v] = ways[u];
                parent[v] = u;
            }
            else if (len[u] + 1 == len[v])
            {
                ways[v] = ((long long)ways[v] + ways[u]) % mod;
                parent[v] = min(parent[v], u);
            }
        }
    }
    int length = n ? *max_element(len.begin(), len.end()) : 0;
    int count = n ? 0 : 1 % mod, last = -1;
    for (int i = 0; i < n; i++)
    {
        if (len[i] != length) continue;
        count = ((long long)count + ways[i]) % mod;
        if (last == -1) last = i;
    }
    require(got.len == len && got.ways == ways && got.parent == parent);
    require(got.length == length && got.count == count && got.last == last);
    vector<int> path;
    for (int u = last; u != -1; u = parent[u]) path.push_back(u);
    reverse(path.begin(), path.end());
    require(got.path() == path);
    if (enumerate && n)
    {
        vector<int> elen(n), eways(n);
        for (int mask = 1; mask < (1 << n); mask++)
        {
            int prev = -1, size = 0;
            bool valid = true;
            for (int v : order)
            {
                if (!(mask >> v & 1)) continue;
                if (prev != -1 && !before(p, prev, v, strict)) valid = false;
                prev = v;
                size++;
            }
            if (!valid) continue;
            if (size > elen[prev])
            {
                elen[prev] = size;
                eways[prev] = 0;
            }
            if (size == elen[prev]) eways[prev] = (eways[prev] + 1) % mod;
        }
        require(elen == len && eways == ways);
    }
    checked++;
}

int main()
{
    mt19937_64 rng(4742);
    vector<long long> pool{LLONG_MIN, -2, -1, 0, 1, 2, LLONG_MAX};
    vector<int> mods{1, 2, 3, 17, 1 << 30, INT_MAX};
    for (int n = 0; n <= 4; n++)
    {
        int total = 1 << (3 * n);
        for (int code = 0; code < total; code++)
        {
            vector<P> p(n);
            for (int i = 0; i < n; i++)
            {
                for (int d = 0; d < 3; d++) p[i][d] = code >> (3 * i + d) & 1;
            }
            for (bool strict : {false, true}) check(p, mods[code % mods.size()], strict, true);
        }
    }
    for (int test = 0; test < 3000; test++)
    {
        int n = rng() % 36;
        vector<P> p(n);
        for (auto &v : p)
        {
            for (auto &x : v) x = pool[rng() % pool.size()];
        }
        int mod = mods[test % mods.size()];
        for (bool strict : {false, true}) check(p, mod, strict, n <= 10);
        Chain3D base(p, mod, true);
        for (auto &v : p) rotate(v.begin(), v.begin() + 1, v.end());
        Chain3D rotated(p, mod, true);
        require(base.length == rotated.length && base.count == rotated.count);
        require(base.len == rotated.len && base.ways == rotated.ways && base.parent == rotated.parent);
        for (auto &v : p)
        {
            for (auto &x : v) x = lower_bound(pool.begin(), pool.end(), x) - pool.begin();
        }
        Chain3D remapped(p, mod, true);
        require(rotated.len == remapped.len && rotated.ways == remapped.ways);
        shuffle(p.begin(), p.end(), rng);
        Chain3D shuffled(p, mod, true);
        require(base.length == shuffled.length && base.count == shuffled.count);
    }
    for (bool strict : {false, true})
    {
        int n = 100000;
        vector<P> p(n);
        for (int i = 0; i < n; i++) p[i] = {i, i, i};
        Chain3D chain(p, 1, strict);
        require(chain.length == n && chain.count == 0 && (int)chain.path().size() == n);
        for (int i = 0; i < n; i++)
        {
            require(chain.len[i] == i + 1 && chain.ways[i] == 0 && chain.parent[i] == i - 1);
            p[i] = {i, n - i, i};
        }
        Chain3D anti(p, INT_MAX, strict);
        require(anti.length == 1 && anti.count == n && anti.path() == vector<int>{0});
        fill(p.begin(), p.end(), P{0, 0, 0});
        Chain3D equal(p, INT_MAX, strict);
        require(equal.length == (strict ? 1 : n) && equal.count == (strict ? n : 1));
        for (int i = 0; i < n; i++) p[i] = {i / 10, i / 10, i / 10};
        Chain3D layers(p, 1 << 30, strict);
        int ways = 1;
        for (int i = 0; i < n / 10; i++) ways = (long long)ways * 10 % (1 << 30);
        require(layers.length == (strict ? n / 10 : n) && layers.count == (strict ? ways : 1));
        auto path = layers.path();
        for (int i = 0; i < (int)path.size(); i++) require(path[i] == (strict ? i * 10 : i));
        // A huge equal-x group exercises uneven point counts across group splits.
        for (int i = 0; i < n; i++) p[i] = {i == n - 1 ? 1 : 0, i, i};
        Chain3D skew(p, INT_MAX, strict);
        require(skew.length == (strict ? 2 : n) && skew.count == (strict ? n - 1 : 1));
    }
    cout << "PASS " << checked << " independent small cases plus 100000-point analytic families\n";
}
