#pragma once
#include <algorithm>
#include <cassert>
#include <numeric>
#include <utility>
#include <vector>
using namespace std;

struct OfflineLCA
{
    int n;
    vector<vector<int>> g;
    vector<vector<pair<int, int>>> queries;
    vector<int> parent, size, ancestor, done, answer;

    OfflineLCA(int n)
        : n(n),
          g(n + 1),
          queries(n + 1),
          parent(n + 1),
          size(n + 1),
          ancestor(n + 1),
          done(n + 1)
    {
    }

    void add(int u, int v)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        g[u].push_back(v);
        g[v].push_back(u);
    }

    int add_query(int u, int v)
    {
        assert(1 <= u && u <= n && 1 <= v && v <= n);
        int id = answer.size();
        answer.push_back(0);
        queries[u].push_back({v, id});
        queries[v].push_back({u, id});
        return id;
    }

    int find(int u)
    {
        if (parent[u] != u)
            parent[u] = find(parent[u]);
        return parent[u];
    }

    void merge(int u, int v)
    {
        u = find(u);
        v = find(v);
        if (size[u] < size[v])
            swap(u, v);
        parent[v] = u;
        size[u] += size[v];
    }

    void dfs(int u, int p)
    {
        for (int v : g[u])
            if (v != p)
            {
                dfs(v, u);
                merge(u, v);
                ancestor[find(u)] = u;
            }
        done[u] = 1;
        for (auto [v, id] : queries[u])
            if (done[v])
                answer[id] = ancestor[find(v)];
    }

    // Input must be a nonempty tree. Query IDs are 0-based.
    void run(int root = 1)
    {
        assert(1 <= root && root <= n);
        iota(parent.begin(), parent.end(), 0);
        iota(ancestor.begin(), ancestor.end(), 0);
        fill(size.begin(), size.end(), 1);
        fill(done.begin(), done.end(), 0);
        fill(answer.begin(), answer.end(), 0);
        dfs(root, 0);
    }
};
