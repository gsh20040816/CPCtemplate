#include <bits/stdc++.h>
#include "../src/compact/tree_isomorphism.hpp"
using namespace std;

void need(bool ok)
{
    if (!ok) abort();
}

string canonical(const vector<vector<int>> &g, int u, int p)
{
    vector<string> children;
    for (int v : g[u])
    {
        if (v != p) children.push_back(canonical(g, v, u));
    }
    sort(children.begin(), children.end());
    string result = "(";
    for (auto s : children) result += s;
    return result + ")";
}

int main()
{
    TreeIsomorphism iso;
    map<string, int> forward;
    map<int, string> backward;
    map<string, pair<int, int>> unrooted;
    map<pair<int, int>, string> reverse;
    mt19937 rng(3575043);
    int tested = 0;
    auto check = [&](const vector<vector<int>> &g)
    {
        string best;
        for (int root = 0; root < int(g.size()); root++)
        {
            string key = canonical(g, root, -1);
            int code = iso.rooted(g, root);
            need(forward.emplace(key, code).first->second == code);
            need(backward.emplace(code, key).first->second == key);
            if (best.empty() || key < best) best = key;
        }
        auto code = iso.unrooted(g);
        need(unrooted.emplace(best, code).first->second == code);
        need(reverse.emplace(code, best).first->second == best);
        vector<int> permutation(g.size());
        iota(permutation.begin(), permutation.end(), 0);
        shuffle(permutation.begin(), permutation.end(), rng);
        vector<vector<int>> h(g.size());
        for (int u = 0; u < int(g.size()); u++)
        {
            for (int v : g[u]) h[permutation[u]].push_back(permutation[v]);
            shuffle(h[permutation[u]].begin(), h[permutation[u]].end(), rng);
        }
        need(iso.unrooted(h) == code);
        need(iso.rooted(h, permutation[0]) == iso.rooted(g, 0));
        tested++;
    };
    check(vector<vector<int>>(1));
    for (int n = 2; n <= 6; n++)
    {
        int total = 1;
        for (int i = 0; i < n - 2; i++) total *= n;
        for (int mask = 0; mask < total; mask++)
        {
            int value = mask;
            vector<int> degree(n, 1), sequence;
            for (int i = 0; i < n - 2; i++)
            {
                sequence.push_back(value % n);
                degree[value % n]++;
                value /= n;
            }
            vector<vector<int>> g(n);
            for (int v : sequence)
            {
                int u = find(degree.begin(), degree.end(), 1) - degree.begin();
                g[u].push_back(v);
                g[v].push_back(u);
                degree[u]--;
                degree[v]--;
            }
            int u = find(degree.begin(), degree.end(), 1) - degree.begin();
            degree[u]--;
            int v = find(degree.begin(), degree.end(), 1) - degree.begin();
            g[u].push_back(v);
            g[v].push_back(u);
            check(g);
        }
    }
    for (int test = 0; test < 1000; test++)
    {
        int n = 1 + rng() % 30;
        vector<vector<int>> g(n);
        for (int v = 1; v < n; v++)
        {
            int u = rng() % v;
            g[u].push_back(v);
            g[v].push_back(u);
        }
        check(g);
    }
    TreeIsomorphism large;
    int n = 100000;
    vector<vector<int>> chain(n), star(n);
    for (int v = 1; v < n; v++)
    {
        chain[v - 1].push_back(v);
        chain[v].push_back(v - 1);
        star[0].push_back(v);
        star[v].push_back(0);
    }
    need(large.rooted(chain, 0) == large.rooted(chain, n - 1));
    need(large.unrooted(chain) != large.unrooted(star));
    cout << "PASS " << tested << " trees, all roots and relabelings; 100000-node chain/star\n";
}
