#include "../../src/compact/closest_pair_i64.hpp"
using namespace std;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int tests;
    cin >> tests;
    while (tests--)
    {
        int n;
        cin >> n;
        vector<IntegerPlane::Point> p(n);
        for (auto &v : p) cin >> v.x >> v.y;
        pair<int, int> ids;
        closest_pair_i64(p, &ids);
        cout << ids.first << ' ' << ids.second << '\n';
    }
}
