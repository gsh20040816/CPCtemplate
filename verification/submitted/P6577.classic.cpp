#include <algorithm>
#include <cassert>
#include <optional>
#include <vector>
using namespace std;

template <int N, int M> struct Weighted_Matching
{
    using I = __int128_t;
    static constexpr I inf = I(1) << 120;
    int n, m;
    I w[N + 1][M + 1];
    int l[N + 1], r[M + 1];

    void Init(int left_size, int right_size)
    {
        assert(0 <= left_size && left_size <= N);
        assert(0 <= right_size && right_size <= M);
        n = left_size;
        m = right_size;
        for ( int i = 0; i <= n; i++ )
            fill(w[i], w[i] + m + 1, -inf);
        fill(l, l + n + 1, 0);
        fill(r, r + m + 1, 0);
    }

    void Insert(int x, int y, long long weight)
    {
        assert(1 <= x && x <= n && 1 <= y && y <= m);
        w[x][y] = max(w[x][y], I(weight));
    }

    optional<I> Solve(bool allow_unmatched = false)
    {
        fill(l, l + n + 1, 0);
        fill(r, r + m + 1, 0);
        if ( !allow_unmatched && n > m )
            return nullopt;
        int cols = m + (allow_unmatched ? n : 0);
        vector<I> u(n + 1), v(cols + 1);
        vector<int> p(cols + 1), way(cols + 1);
        for ( int i = 1; i <= n; i++ )
        {
            p[0] = i;
            int j0 = 0;
            vector<I> dis(cols + 1, inf);
            vector<bool> used(cols + 1);
            do
            {
                used[j0] = true;
                int x = p[j0], j1 = 0;
                I delta = inf;
                for ( int j = 1; j <= cols; j++ )
                {
                    if ( used[j] )
                        continue;
                    I weight = j <= m ? w[x][j] : 0;
                    if ( weight != -inf )
                    {
                        I cur = -weight - u[x] - v[j];
                        if ( cur < dis[j] )
                        {
                            dis[j] = cur;
                            way[j] = j0;
                        }
                    }
                    if ( dis[j] < delta )
                    {
                        delta = dis[j];
                        j1 = j;
                    }
                }
                if ( delta == inf )
                    return nullopt;
                for ( int j = 0; j <= cols; j++ )
                {
                    if ( used[j] )
                    {
                        u[p[j]] += delta;
                        v[j] -= delta;
                    }
                    else if ( dis[j] != inf )
                        dis[j] -= delta;
                }
                j0 = j1;
            } while ( p[j0] );
            do
            {
                int j1 = way[j0];
                p[j0] = p[j1];
                j0 = j1;
            } while ( j0 );
        }
        I answer = 0;
        for ( int j = 1; j <= m; j++ )
        {
            if ( !p[j] )
                continue;
            l[p[j]] = j;
            r[j] = p[j];
            answer += w[p[j]][j];
        }
        return answer;
    }
};

#include <cstdio>

Weighted_Matching<500, 500> graph;

int main()
{
    int n, m;
    scanf("%d%d", &n, &m);
    graph.Init(n, n);
    while ( m-- )
    {
        int x, y;
        long long w;
        scanf("%d%d%lld", &x, &y, &w);
        graph.Insert(x, y, w);
    }
    auto answer = graph.Solve();
    assert(answer);
    printf("%lld\n", (long long)*answer);
    for ( int j = 1; j <= n; j++ )
        printf("%d%c", graph.r[j], j == n ? '\n' : ' ');
}
