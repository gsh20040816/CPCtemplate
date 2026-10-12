#include "../src/compact/eight_puzzle.hpp"
#include <cassert>

int main(int argc, char **argv)
{
    using U = unsigned long long;
    auto pack = [](const array<int, 9> &a)
    {
        U key = 0;
        for (int i = 0; i < 9; i++) key |= U(a[i]) << (4 * i);
        return key;
    };
    array<int, 9> goal = {1, 2, 3, 4, 5, 6, 7, 8, 0};
    U target = pack(goal);
    unordered_map<U, int> distance;
    queue<U> q;
    distance[target] = 0;
    q.push(target);
    vector<pair<int, int>> edges;
    for (int i = 0; i < 9; i++)
    {
        if (i % 3 < 2) edges.push_back({i, i + 1});
        if (i < 6) edges.push_back({i, i + 3});
    }
    while (!q.empty())
    {
        U state = q.front();
        q.pop();
        int depth = distance.at(state);
        for (auto [a, b] : edges)
        {
            U x = state >> (4 * a) & 15;
            U y = state >> (4 * b) & 15;
            if (x && y) continue;
            U next = state ^ ((x ^ y) << (4 * a)) ^ ((x ^ y) << (4 * b));
            if (distance.emplace(next, depth + 1).second) q.push(next);
        }
    }
    assert(distance.size() == 181440);
    EightPuzzle solver;
    vector<bool> seen(362880);
    vector<int> histogram(32);
    array<int, 9> a = {0, 1, 2, 3, 4, 5, 6, 7, 8};
    ofstream inputs, answers;
    if (argc == 3)
    {
        inputs.open(argv[1]);
        answers.open(argv[2]);
    }
    do
    {
        int id = solver.rank(a);
        assert(id >= 0 && id < 362880 && !seen[id]);
        seen[id] = true;
        auto found = distance.find(pack(a));
        int depth = found == distance.end() ? -1 : found->second;
        int inversions = 0;
        for (int i = 0; i < 9; i++)
            for (int j = i + 1; j < 9; j++)
                if (a[i] && a[j]) inversions += a[i] > a[j];
        auto [ok, path] = solver.solve(a);
        assert(ok == (depth >= 0));
        assert(ok == (inversions % 2 == 0));
        if (ok)
        {
            assert(int(path.size()) == depth && depth <= 31);
            histogram[depth]++;
            auto b = a;
            for (char move : path)
            {
                int z = find(b.begin(), b.end(), 0) - b.begin();
                int next = z;
                if (move == 'u' && z >= 3) next -= 3;
                else if (move == 'd' && z < 6) next += 3;
                else if (move == 'l' && z % 3) next--;
                else if (move == 'r' && z % 3 < 2) next++;
                else assert(false);
                swap(b[z], b[next]);
            }
            assert(b == goal);
        }
        else assert(path.empty());
        if (inputs)
        {
            for (int v : a) inputs << (v ? char('0' + v) : 'x') << ' ';
            inputs << '\n';
            answers << depth << '\n';
        }
    } while (next_permutation(a.begin(), a.end()));
    assert(histogram[0] == 1 && histogram[31] == 2);
    for (int x : histogram) cout << x << ' ';
    cout << '\n';
}
