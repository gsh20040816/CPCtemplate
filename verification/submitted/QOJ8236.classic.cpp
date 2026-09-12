#include <cstdio>
#include <string>
#include <algorithm>
#include <cassert>
#include <climits>
#include <vector>
using namespace std;

// BEGIN Release_Bfs
template <class Neighbors>
vector<int> Release_Bfs(const vector<int> &open, int source, Neighbors neighbors)
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
    while ( head < int(queue.size()) || waiting )
    {
        int limit = head < int(queue.size()) ? dist[queue[head]] : INT_MAX;
        while ( time <= last && time <= limit && pending[time].empty() )
            time++;
        int u;
        if ( time <= last && time <= limit )
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
                      if ( dist[v] != -1 )
                          return;
                      dist[v] = max(dist[u] + 1, open[v]);
                      if ( dist[v] == dist[u] + 1 )
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

// END Release_Bfs


int main()
{
    int n, m, k;
    scanf("%d%d%d", &n, &m, &k);
    vector<int> open(n * m);
    int source = 0;
    for ( int i = 0; i < k; i++ )
    {
        int x, y;
        scanf("%d%d", &x, &y);
        int u = (x - 1) * m + y - 1;
        if ( i == 0 )
            source = u;
        else
            open[u] = k - i;
    }
    vector<string> grid(n);
    vector<char> row(m + 1);
    for ( auto &s : grid )
    {
        scanf("%s", row.data());
        s = row.data();
    }
    auto dist = Release_Bfs(open,
                            source,
                            [&](int u, auto visit)
                            {
                                int x = u / m, y = u % m;
                                const int dx[] = {-1, 1, 0, 0};
                                const int dy[] = {0, 0, -1, 1};
                                for ( int i = 0; i < 4; i++ )
                                {
                                    int a = x + dx[i], b = y + dy[i];
                                    if ( a >= 0 && a < n && b >= 0 && b < m &&
                                         grid[a][b] == '.' )
                                        visit(a * m + b);
                                }
                            });
    unsigned long long answer = 0;
    for ( int d : dist )
        if ( d >= 0 )
            answer += 1ULL * d * d;
    printf("%llu\n", answer);
}
