#include "../../src/compact/plug_cycle.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    vector<string> a(n);
    for (auto &row : a) cin >> row;
    __int128 answer = grid_cycle<__int128>(a);
    string out;
    do
    {
        out += char('0' + answer % 10);
        answer /= 10;
    } while (answer);
    reverse(out.begin(), out.end());
    cout << out << '\n';
}
