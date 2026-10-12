#include <bits/stdc++.h>
#include <cassert>
using namespace std;
struct dsu
{
    vector<int> fa, sz;

    dsu(int n) : fa(n), sz(n, 1) { iota(fa.begin(), fa.end(), 0); }

    int find(int x)
    {
        while (x != fa[x]) x = fa[x] = fa[fa[x]];
        return x;
    }

    bool same(int x, int y) { return find(x) == find(y); }

    bool merge(int x, int y)
    {
        x = find(x), y = find(y);
        if (x == y) return false;
        sz[x] += sz[y], fa[y] = x;
        return true;
    }

    int size(int x) { return sz[find(x)]; }

    vector<vector<int>> groups()
    {
        vector<vector<int>> res(fa.size());
        for (int i = 0; i < int(fa.size()); i++) res[find(i)].push_back(i);
        res.erase(
            remove_if(res.begin(), res.end(), [&](const auto &v) { return v.empty(); }),
            res.end());
        return res;
    }
};

struct ManhattanMST
{
    using I = __int128;
    using Point = pair<long long, long long>;
    using Edge = tuple<I, int, int>;
    struct Result
    {
        I weight = 0;
        vector<pair<int, int>> edges;
    };

    static vector<Edge> candidates(const vector<Point> &points)
    {
        assert(points.size() <= INT_MAX);
        int n = int(points.size());
        vector<pair<I, I>> p(points.begin(), points.end());
        vector<int> id(n);
        iota(id.begin(), id.end(), 0);
        vector<Edge> e;
        e.reserve(size_t(n) * 4);
        for (int dir = 0; dir < 4; dir++)
        {
            sort(id.begin(), id.end(), [&](int i, int j)
            {
                return pair{p[i].first + p[i].second, i} <
                       pair{p[j].first + p[j].second, j};
            });
            map<I, int> sweep;
            for (int i : id)
            {
                auto it = sweep.lower_bound(-p[i].second);
                while (it != sweep.end())
                {
                    int j = it->second;
                    I dx = p[i].first - p[j].first;
                    I dy = p[i].second - p[j].second;
                    if (dx < dy) break;
                    e.emplace_back(dx + dy, i, j);
                    it = sweep.erase(it);
                }
                sweep[-p[i].second] = i;
            }
            for (auto &[x, y] : p)
                if (dir & 1) x = -x;
                else swap(x, y);
        }
        return e;
    }

    static Result solve(const vector<Point> &points)
    {
        auto e = candidates(points);
        int n = int(points.size());
        Result r;
        if (n < 2) return r;
        sort(e.begin(), e.end());
        dsu uf(n);
        for (auto [w, u, v] : e)
        {
            int a = uf.find(u), b = uf.find(v);
            if (a == b) continue;
            if (uf.size(a) < uf.size(b)) swap(a, b);
            uf.merge(a, b);
            r.weight += w;
            r.edges.emplace_back(u, v);
            if (r.edges.size() == points.size() - 1) break;
        }
        assert(r.edges.size() == points.size() - 1);
        return r;
    }
};
vector<int> manhattan_order(const vector<ManhattanMST::Point> &p)
{
    assert(p.size() <= INT_MAX);
    int n = int(p.size());
    if (n == 0)
        return {};
    auto t = ManhattanMST::solve(p);
    vector<vector<int>> g(n);
    for (auto [u, v] : t.edges)
    {
        g[u].push_back(v);
        g[v].push_back(u);
    }
    vector<int> ord;
    ord.reserve(n);
    auto dfs = [&](auto &&self, int u, int fa) -> void
    {
        ord.push_back(u);
        for (int v : g[u])
        {
            if (v != fa)
                self(self, v, u);
        }
    };
    dfs(dfs, 0, -1);
    return ord;
}
int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m)
    {
        vector<int> a(n);
        for (int &x : a)
            cin >> x;
        vector<ManhattanMST::Point> q(m);
        for (auto &[l, r] : q)
        {
            cin >> l >> r;
            l--;
        }
        vector<int> cnt(n + 1);
        vector<pair<long long, long long>> ans(m);
        long long sum = 0;
        auto add = [&](int i)
        {
            sum += cnt[a[i]];
            cnt[a[i]]++;
        };
        auto del = [&](int i)
        {
            cnt[a[i]]--;
            sum -= cnt[a[i]];
        };
        auto save = [&](int id, long long len)
        {
            long long den = len * (len - 1) / 2;
            if (sum == 0)
            {
                ans[id] = {0, 1};
                return;
            }
            long long d = gcd(sum, den);
            ans[id] = {sum / d, den / d};
        };
        int l = 0, r = 0;
        for (int id : manhattan_order(q))
        {
            auto [ql, qr] = q[id];
            while (l > ql)
                add(--l);
            while (r < qr)
                add(r++);
            while (l < ql)
                del(l++);
            while (r > qr)
                del(--r);
            save(id, r - l);
        }
        for (auto [num, den] : ans)
            cout << num << '/' << den << '\n';
    }
}
