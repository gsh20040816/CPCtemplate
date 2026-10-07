#pragma once
#include <algorithm>
#include <array>
#include <cassert>
#include <climits>
#include <numeric>
#include <vector>
using namespace std;

struct Chain3D
{
    using Point = array<long long, 3>;

    struct State
    {
        int len = 0, ways = 0, end = -1;
    };

    vector<int> len, ways, parent;
    int length = 0, count = 0, last = -1;

    Chain3D(const vector<Point> &p, int mod, bool strict = true)
    {
        assert(mod > 0 && p.size() <= INT_MAX / 2);
        int n = p.size();
        count = 1 % mod;
        len.assign(n, 1);
        ways.assign(n, 1 % mod);
        parent.assign(n, -1);
        if (!n) return;
        vector<int> order(n), z(n), cut{0};
        vector<long long> values;
        iota(order.begin(), order.end(), 0);
        sort(order.begin(), order.end(), [&](int x, int y)
        {
            if (p[x] != p[y]) return p[x] < p[y];
            return x < y;
        });
        for (int i = 1; i < n; i++)
        {
            if (!strict || p[order[i]][0] != p[order[i - 1]][0]) cut.push_back(i);
        }
        cut.push_back(n);
        for (auto q : p) values.push_back(q[2]);
        sort(values.begin(), values.end());
        values.erase(unique(values.begin(), values.end()), values.end());
        for (int i = 0; i < n; i++)
        {
            z[i] = lower_bound(values.begin(), values.end(), p[i][2]) - values.begin() + 1;
        }
        vector<State> bit(values.size() + 1);
        auto join = [&](State x, State y)
        {
            if (x.len != y.len) return x.len > y.len ? x : y;
            x.ways = ((long long)x.ways + y.ways) % mod;
            x.end = min(x.end, y.end);
            return x;
        };
        auto cdq = [&](auto &&self, int l, int r) -> void
        {
            if (r - l <= 1) return;
            int mid = l + (r - l) / 2;
            self(self, l, mid);
            {
                vector<int> a(order.begin() + cut[l], order.begin() + cut[mid]);
                vector<int> b(order.begin() + cut[mid], order.begin() + cut[r]);
                auto by_y = [&](int x, int y)
                {
                    return p[x][1] < p[y][1];
                };
                sort(a.begin(), a.end(), by_y);
                sort(b.begin(), b.end(), by_y);
                int i = 0;
                for (int v : b)
                {
                    while (i < (int)a.size())
                    {
                        int u = a[i];
                        if (strict ? p[u][1] >= p[v][1] : p[u][1] > p[v][1]) break;
                        i++;
                        for (int t = z[u]; t < (int)bit.size(); t += t & -t)
                        {
                            bit[t] = join(bit[t], {len[u], ways[u], u});
                        }
                    }
                    State best;
                    for (int t = z[v] - strict; t > 0; t -= t & -t)
                    {
                        best = join(best, bit[t]);
                    }
                    if (!best.len) continue;
                    if (best.len + 1 > len[v])
                    {
                        len[v] = best.len + 1;
                        ways[v] = best.ways;
                        parent[v] = best.end;
                    }
                    else if (best.len + 1 == len[v])
                    {
                        ways[v] = ((long long)ways[v] + best.ways) % mod;
                        parent[v] = min(parent[v], best.end);
                    }
                }
                for (int j = 0; j < i; j++)
                {
                    for (int t = z[a[j]]; t < (int)bit.size(); t += t & -t) bit[t] = State{};
                }
            }
            self(self, mid, r);
        };
        cdq(cdq, 0, cut.size() - 1);
        State best;
        for (int i = 0; i < n; i++) best = join(best, {len[i], ways[i], i});
        length = best.len;
        count = best.ways;
        last = best.end;
    }

    vector<int> path() const
    {
        vector<int> ans;
        for (int u = last; u != -1; u = parent[u]) ans.push_back(u);
        reverse(ans.begin(), ans.end());
        return ans;
    }
};
