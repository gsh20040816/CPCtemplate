#include "../../src/compact/eight_puzzle.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    EightPuzzle solver;
    char ch;
    while (cin >> ch)
    {
        array<int, 9> a;
        a[0] = ch == 'x' ? 0 : ch - '0';
        for (int i = 1; i < 9; i++)
        {
            cin >> ch;
            a[i] = ch == 'x' ? 0 : ch - '0';
        }
        auto result = solver.solve(a);
        cout << (result.first ? result.second : "unsolvable") << '\n';
    }
}
