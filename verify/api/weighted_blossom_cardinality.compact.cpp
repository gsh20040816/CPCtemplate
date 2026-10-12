#include "../../src/compact/weighted_blossom.hpp"

int main()
{
    auto print128 = [](__int128 x)
    {
        if (x < 0)
        {
            cout << '-';
            x = -x;
        }
        string s;
        do
        {
            s.push_back('0' + x % 10);
            x /= 10;
        } while (x);
        reverse(s.begin(), s.end());
        cout << s;
    };
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    WeightedBlossom g(n);
    while (m--)
    {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        g.add_edge(u, v, w);
    }
    auto result = g.solve(true);
    cout << result.pairs << ' ';
    print128(result.weight);
    cout << '\n';
    for (int u = 1; u <= n; u++) cout << result.mate[u] << ' ';
    cout << '\n';
    cout << (2 * result.pairs == n ? "PERFECT" : "NOT_PERFECT") << '\n';
}
