#include "../../src/compact/det_prime.hpp"

int main()
{
    using Z = ModInt<1000000007>;
    int n;
    cin >> n;
    int k = n - 1;
    vector<vector<pair<int, int>>> edges(k);
    for (auto &group : edges)
    {
        int m;
        cin >> m;
        while (m--)
        {
            int u, v;
            cin >> u >> v;
            group.push_back({u - 1, v - 1});
        }
    }
    vector<vector<Z>> lap(k, vector<Z>(k));
    Z ans = 0;
    int prev = 0;
    for (int mask = 1; mask < (1 << k); mask++)
    {
        int gray = mask ^ (mask >> 1);
        int bit = __builtin_ctz(unsigned(gray ^ prev));
        Z delta = (gray >> bit & 1) ? 1 : -1;
        for (auto [u, v] : edges[bit])
        {
            if (u < k)
                lap[u][u] = lap[u][u] + delta;
            if (v < k)
                lap[v][v] = lap[v][v] + delta;
            if (u < k && v < k)
            {
                lap[u][v] = lap[u][v] - delta;
                lap[v][u] = lap[v][u] - delta;
            }
        }
        Z ways = det_prime<1000000007>(lap);
        if ((k - __builtin_popcount(unsigned(gray))) & 1)
            ans = ans - ways;
        else
            ans = ans + ways;
        prev = gray;
    }
    cout << ans.v << '\n';
}
