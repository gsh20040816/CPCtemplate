#include "../../src/compact/minimum_mean_cycle.hpp"

int main()
{
    int n, m;
    cin >> n >> m;
    vector<tuple<int, int, long long>> edges(m);
    for (auto &[u, v, w] : edges)
        cin >> u >> v >> w;
    auto ans = minimum_mean_cycle(n, edges);
    if (!ans)
    {
        cout << "NONE\n";
        return 0;
    }
    auto num = ans->first;
    if (num < 0)
    {
        cout << '-';
        num = -num;
    }
    string out;
    do
    {
        out += char('0' + num % 10);
        num /= 10;
    } while (num);
    reverse(out.begin(), out.end());
    cout << out << ' ' << ans->second << '\n';
}
