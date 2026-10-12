#pragma once
#include "ntt_2d.hpp"
#include "fps_inverse.hpp"

struct BivariateInverse : Ntt2D<998244353>
{
    static Matrix inverse(const Matrix &a, int n, int m)
    {
        assert(n > 0 && m > 0 && m <= max_size);
        assert(!a.empty() && !a[0].empty() && a[0][0].v != 0);
        auto row = a[0];
        if ((int)row.size() > m)
            row.resize(m);
        Matrix b{FpsInverse::inverse(row, m)};
        if (n == 1)
            return b;
        assert(n <= max_size && 2LL * m - 1 <= max_size);
        int width = 1;
        while (width < 2LL * m - 1)
            width *= 2;
        while ((int)b.size() < n)
        {
            int k = b.size(), height = 2 * k;
            int next = min(n, height);
            Matrix f(height, vector<Z>(width));
            for (int i = 0; i < min(next, (int)a.size()); i++)
                for (int j = 0; j < min(m, (int)a[i].size()); j++)
                    f[i][j] = a[i][j];
            Matrix g = b;
            g.resize(height);
            for (auto &v : g)
                v.resize(width);
            transform(f);
            transform(g);
            for (int i = 0; i < height; i++)
                for (int j = 0; j < width; j++)
                    f[i][j] *= g[i][j];
            transform(f, true);
            // Keep only the high x-half, reduced modulo y^m.
            for (int i = 0; i < height; i++)
                fill(f[i].begin() + (i < k ? 0 : m), f[i].end(), Z(0));
            transform(f);
            for (int i = 0; i < height; i++)
                for (int j = 0; j < width; j++)
                    f[i][j] *= g[i][j];
            transform(f, true);
            b.resize(next);
            for (int i = k; i < next; i++)
            {
                b[i].resize(m);
                for (int j = 0; j < m; j++)
                    b[i][j] = Z(0) - f[i][j];
            }
        }
        return b;
    }
};
