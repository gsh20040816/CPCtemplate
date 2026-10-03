#include "../src/compact/manhattan_mst.hpp"

string decimal(__int128 x)
{
    bool negative = x < 0;
    __uint128_t v = negative ? __uint128_t(-(x + 1)) + 1 : x;
    string s;
    do
    {
        s += char('0' + v % 10);
        v /= 10;
    } while (v);
    if (negative) s += '-';
    reverse(s.begin(), s.end());
    return s;
}

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int cases;
    cin >> cases;
    while (cases--)
    {
        int n;
        cin >> n;
        vector<ManhattanMST::Point> p(n);
        for (auto &[x, y] : p) cin >> x >> y;
        auto before = p;
        auto r = ManhattanMST::solve(p);
        vector<ManhattanMST::Edge> e;
        bool repeat = true;
        if (n <= 8)
        {
            e = ManhattanMST::candidates(p);
            auto again = ManhattanMST::solve(p);
            repeat = r.weight == again.weight && r.edges == again.edges;
        }
        cout << n << ' ' << decimal(r.weight) << ' ' << r.edges.size() << ' '
             << e.size() << ' ' << (p == before) << ' ' << repeat << '\n';
        for (auto [u, v] : r.edges) cout << u << ' ' << v << '\n';
        for (auto [w, u, v] : e) cout << decimal(w) << ' ' << u << ' ' << v << '\n';
    }
}
