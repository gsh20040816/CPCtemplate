#include <bits/stdc++.h>
using namespace std;

struct Closest_Pair
{
    using R = long double;

    struct Point
    {
        R x, y;
    };

    // Finite coordinates, |x|, |y| <= 1e100. Returns distance, not its square.
    static optional<R> Solve(vector<Point> p)
    {
        int n = p.size();
        if ( n < 2 )
            return nullopt;
        sort(p.begin(),
             p.end(),
             [](Point a, Point b)
             {
                 return tie(a.x, a.y) < tie(b.x, b.y);
             });
        for ( int i = 1; i < n; i++ )
            if ( p[i].x == p[i - 1].x && p[i].y == p[i - 1].y )
                return R(0);
        auto by_y = [](Point a, Point b)
        {
            return tie(a.y, a.x) < tie(b.y, b.x);
        };
        auto distance = [](Point a, Point b)
        {
            return hypotl(a.x - b.x, a.y - b.y);
        };
        vector<Point> tmp(n);
        function<R(int, int)> Dfs = [&](int l, int r) -> R
        {
            if ( r - l <= 3 )
            {
                R best = numeric_limits<R>::infinity();
                for ( int i = l; i < r; i++ )
                    for ( int j = l; j < i; j++ )
                        best = min(best, distance(p[i], p[j]));
                sort(p.begin() + l, p.begin() + r, by_y);
                return best;
            }
            int m = (l + r) / 2;
            R x = p[m].x;
            R best = min(Dfs(l, m), Dfs(m, r));
            merge(p.begin() + l,
                  p.begin() + m,
                  p.begin() + m,
                  p.begin() + r,
                  tmp.begin() + l,
                  by_y);
            copy(tmp.begin() + l, tmp.begin() + r, p.begin() + l);
            vector<Point> strip;
            for ( int i = l; i < r; i++ )
                if ( fabsl(p[i].x - x) <= best )
                {
                    for ( int j = (int)strip.size() - 1; j >= 0; j-- )
                    {
                        if ( p[i].y - strip[j].y > best )
                            break;
                        best = min(best, distance(p[i], strip[j]));
                    }
                    strip.push_back(p[i]);
                }
            return best;
        };
        return Dfs(0, n);
    }
};


int main()
{
    int n;
    scanf("%d", &n);
    vector<Closest_Pair::Point> p(n);
    for ( auto &v : p )
        scanf("%Lf%Lf", &v.x, &v.y);
    printf("%.4Lf\n", *Closest_Pair::Solve(p));
}
