#include "../src/compact/lyndon.hpp"

#define CHECK(x) do { if (!(x)) abort(); } while (false)

int compare(const string &s, int a, int b, int c, int d)
{
    while (a < b && c < d)
    {
        int x = (unsigned char)s[a++];
        int y = (unsigned char)s[c++];
        if (x != y) return x < y ? -1 : 1;
    }
    return (a < b) - (c < d);
}

vector<int> brute(const string &s)
{
    int n = s.size();
    vector<vector<bool>> good(n, vector<bool>(n + 1, true));
    for (int l = 0; l < n; l++)
    {
        for (int r = l + 1; r <= n; r++)
        {
            for (int k = l + 1; k < r; k++)
                good[l][r] = good[l][r] && compare(s, l, r, k, r) < 0;
        }
    }
    int count = 0;
    vector<int> path, ans;
    auto dfs = [&](auto &&self, int l, int prev) -> void
    {
        if (l == n)
        {
            count++;
            ans = path;
            return;
        }
        for (int r = l + 1; r <= n; r++)
        {
            if (!good[l][r]) continue;
            if (l && compare(s, prev, l, l, r) < 0) continue;
            path.push_back(r);
            self(self, r, l);
            path.pop_back();
        }
    };
    dfs(dfs, 0, 0);
    CHECK(count == 1);
    return ans;
}

int main()
{
    int exhaustive = 0;
    for (int n = 0, total = 1; n <= 9; n++, total *= 3)
    {
        for (int mask = 0; mask < total; mask++)
        {
            string s(n, '\0');
            int x = mask;
            for (char &c : s)
            {
                c = (char)(x % 3 * 127);
                x /= 3;
            }
            CHECK(lyndon(s) == brute(s));
            exhaustive++;
        }
    }
    mt19937 rng(6114);
    for (int trial = 0; trial < 3000; trial++)
    {
        string s(rng() % 25, '\0');
        for (char &c : s)
            c = (char)(rng() % (trial % 2 ? 256 : 4));
        string before = s;
        CHECK(lyndon(s) == brute(s));
        CHECK(s == before);
    }
    int n = 5000001;
    string s(n, 'a');
    auto ends = lyndon(s);
    CHECK((int)ends.size() == n);
    for (int i = 0; i < n; i++)
        CHECK(ends[i] == i + 1);
    s.back() = 'b';
    CHECK(lyndon(s) == vector<int>{n});
    for (int i = 1; i < n; i += 2)
        s[i] = 'b';
    s.back() = 'a';
    ends = lyndon(s);
    CHECK((int)ends.size() == n / 2 + 1);
    for (int i = 0; i < n / 2; i++)
        CHECK(ends[i] == 2 * i + 2);
    CHECK(ends.back() == n);
    cout << "PASS " << exhaustive << " exhaustive, 3000 random, 3 length-5000001 cases\n";
}
