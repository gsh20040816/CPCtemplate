#include <bits/stdc++.h>
using namespace std;

// BEGIN EightPuzzle
struct EightPuzzle
{
    vector<int> parent;
    vector<char> step;

    int rank(const array<int, 9> &a) const
    {
        int id = 0;
        for (int i = 0; i < 9; i++)
        {
            int smaller = 0;
            for (int j = i + 1; j < 9; j++) smaller += a[j] < a[i];
            id = id * (9 - i) + smaller;
        }
        return id;
    }

    EightPuzzle() : parent(362880, -1), step(362880)
    {
        array<int, 9> goal = {1, 2, 3, 4, 5, 6, 7, 8, 0};
        int root = rank(goal);
        parent[root] = root;
        queue<array<int, 9>> q;
        q.push(goal);
        int dr[] = {-1, 1, 0, 0};
        int dc[] = {0, 0, -1, 1};
        string inverse = "durl";
        while (!q.empty())
        {
            auto a = q.front();
            q.pop();
            int id = rank(a);
            int zero = find(a.begin(), a.end(), 0) - a.begin();
            for (int d = 0; d < 4; d++)
            {
                int r = zero / 3 + dr[d];
                int c = zero % 3 + dc[d];
                if (r < 0 || r >= 3 || c < 0 || c >= 3) continue;
                auto b = a;
                swap(b[zero], b[r * 3 + c]);
                int next = rank(b);
                if (parent[next] != -1) continue;
                parent[next] = id;
                step[next] = inverse[d];
                q.push(b);
            }
        }
    }

    pair<bool, string> solve(const array<int, 9> &a) const
    {
        int id = rank(a);
        if (parent[id] == -1) return {false, ""};
        string path;
        while (parent[id] != id)
        {
            path += step[id];
            id = parent[id];
        }
        return {true, path};
    }
};
// END EightPuzzle


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
