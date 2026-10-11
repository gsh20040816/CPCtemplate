#include "../src/compact/tutte.hpp"

int power(int a, int b)
{
    int result = 1;
    while (b-- > 0) result = (long long)result * a % 998244353;
    return result;
}

int main()
{
    const int n = 21;
    for (int shape = 0; shape < 3; shape++)
    {
        vector<unsigned> g(n);
        for (int u = 0; u < n; u++)
            for (int v = u + 1; v < n; v++)
                if (shape == 0 || v == u + 1 || (shape == 2 && u == 0 && v == n - 1))
                {
                    g[u] |= 1U << v;
                    g[v] |= 1U << u;
                }
        for (auto [x, y] : vector<pair<int,int>>{{2,2},{1,1},{876543210,123456789}})
        {
            auto start = chrono::steady_clock::now();
            int got = tutte(g,x,y);
            int expected = -1;
            if (x == 2 && y == 2)
            {
                int m = shape == 0 ? n * (n - 1) / 2 : n - 1 + (shape == 2);
                expected = power(2,m);
            }
            if (x == 1 && y == 1) expected = shape == 0 ? power(n,n-2) : (shape == 1 ? 1 : n);
            if (shape == 1) expected = power(x,n-1);
            if (shape == 2)
            {
                expected = y;
                for (int i = 1; i < n; i++) expected = (expected + power(x,i)) % 998244353;
            }
            if (expected != -1 && got != expected) abort();
            double time = chrono::duration<double>(chrono::steady_clock::now()-start).count();
            cout << "shape=" << shape << " x=" << x << " y=" << y << " value=" << got << " checked=" << (expected != -1) << " seconds=" << time << endl;
        }
    }
}
