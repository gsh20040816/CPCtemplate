#include "../../src/compact/flow.hpp"

void print128(__int128 x)
{
    if (x < 0)
    {
        cout << '-';
        x = -x;
    }
    string s;
    do
    {
        s += char('0' + x % 10);
        x /= 10;
    } while (x);
    reverse(s.begin(), s.end());
    cout << s;
}

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, s, t;
    cin >> n >> m >> s >> t;
    MinCostFlow g(n);
    while (m--)
    {
        int u, v;
        long long cap, cost;
        cin >> u >> v >> cap >> cost;
        g.add(u, v, cap, cost);
    }
    auto curve = g.slope(s, t);
    auto [flow, cost] = curve.back();
    cout << flow << ' ';
    print128(cost);
    cout << '\n';
}
