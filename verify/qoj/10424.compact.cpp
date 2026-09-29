#include "../../src/compact/unit_flow_edges.hpp"
using namespace std;

// BEGIN USAGE
bool blocks(const vector<int> &p,
            const vector<int> &s,
            vector<int> &id,
            vector<int> &cap)
{
    int n = p.size(), k = s.size(), last = -1, prev = -1;
    vector<int> pos(n + 1);
    for (int i = 0; i < n; i++) pos[p[i]] = i;
    id.assign(n + 1, -1);
    cap.clear();
    for (int i = 0; i <= k; i++)
    {
        if (i < k && s[i] == -1) continue;
        int at = i == k ? n : pos[s[i]];
        if (at <= last || at - last - 1 < i - prev - 1) return false;
        int g = cap.size();
        cap.push_back(i - prev - 1);
        for (int j = last + 1; j < at; j++) id[p[j]] = g;
        if (i < k)
        {
            id[s[i]] = cap.size();
            cap.push_back(1);
        }
        last = at;
        prev = i;
    }
    return true;
}

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int tests;
    cin >> tests;
    while (tests--)
    {
        int n, k;
        cin >> n;
        vector<int> p(n), q(n);
        for (int &x : p) cin >> x;
        for (int &x : q) cin >> x;
        cin >> k;
        vector<int> a(k), b(k), l, r, x, y;
        for (int &v : a) cin >> v;
        for (int &v : b) cin >> v;
        if (!blocks(p, a, l, x) || !blocks(q, b, r, y))
        {
            cout << "Inconsistent\n";
            continue;
        }
        int m = x.size(), source = m + y.size() + 1, sink = source + 1;
        Dinic g(sink);
        for (int i = 0; i < m; i++) g.add(source, i + 1, x[i]);
        for (int i = 0; i < (int)y.size(); i++) g.add(m + i + 1, sink, y[i]);
        vector<int> ids;
        for (int v = 1; v <= n; v++) ids.push_back(g.add(l[v] + 1, m + r[v] + 1, 1));
        if (g.flow(source, sink) != k)
        {
            cout << "Inconsistent\n";
            continue;
        }
        for (auto [possible, forced] : unit_flow_edges(g, ids))
            cout << (forced ? 'Y' : possible ? '?' : 'N');
        cout << '\n';
    }
}
