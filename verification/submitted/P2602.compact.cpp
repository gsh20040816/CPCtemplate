#include <bits/stdc++.h>
using namespace std;

array<__int128, 10> digit_count(long long n)
{
    struct State
    {
        __int128 ways = 0;
        array<__int128, 10> count{};
    };
    if (n <= 0) return {};
    string s = to_string(n);
    vector<array<State, 2>> memo(s.size());
    vector<array<bool, 2>> seen(s.size());
    auto dfs = [&](auto &&self, int pos, bool tight, bool started) -> State
    {
        if (pos == (int)s.size())
        {
            State result;
            result.ways = started;
            return result;
        }
        if (!tight && seen[pos][started]) return memo[pos][started];
        State result;
        int limit = tight ? s[pos] - '0' : 9;
        for (int d = 0; d <= limit; d++)
        {
            bool next = started || d != 0;
            State child = self(self, pos + 1, tight && d == limit, next);
            result.ways += child.ways;
            for (int x = 0; x < 10; x++)
                result.count[x] += child.count[x];
            if (next) result.count[d] += child.ways;
        }
        if (!tight)
        {
            seen[pos][started] = true;
            memo[pos][started] = result;
        }
        return result;
    };
    return dfs(dfs, 0, true, false).count;
}


int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    long long a, b;
    cin >> a >> b;
    auto left = digit_count(a - 1);
    auto right = digit_count(b);
    for (int d = 0; d < 10; d++)
        cout << (long long)(right[d] - left[d]) << " \n"[d == 9];
}
