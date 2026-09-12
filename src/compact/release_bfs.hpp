#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <vector>
using namespace std;

// BEGIN release_bfs
template <class Neighbors>
vector<int> release_bfs(const vector<int> &open, int source, Neighbors neighbors)
{
    int n = open.size();
    assert(0 <= source && source < n);
    int last = *max_element(open.begin(), open.end());
    assert(last >= 0 && last < INT_MAX - n);
    vector<vector<int>> pending(last + 1);
    vector<int> dist(n, -1), queue;
    queue.reserve(n);
    dist[source] = open[source];
    queue.push_back(source);
    int head = 0, time = 0, waiting = 0;
    while (head < int(queue.size()) || waiting)
    {
        int limit = head < int(queue.size()) ? dist[queue[head]] : INT_MAX;
        while (time <= last && time <= limit && pending[time].empty()) time++;
        int u;
        if (time <= last && time <= limit)
        {
            u = pending[time].back();
            pending[time].pop_back();
            waiting--;
        }
        else
            u = queue[head++];
        neighbors(u,
                  [&](int v)
                  {
                      if (dist[v] != -1) return;
                      dist[v] = max(dist[u] + 1, open[v]);
                      if (dist[v] == dist[u] + 1)
                          queue.push_back(v);
                      else
                      {
                          pending[open[v]].push_back(v);
                          waiting++;
                      }
                  });
    }
    return dist;
}

// END release_bfs
