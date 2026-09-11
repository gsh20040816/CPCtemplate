#pragma once
#include <algorithm>
#include <cassert>
using namespace std;

struct PositionBasis
{
    using U = unsigned long long;
    U a[64];
    int pos[64];

    PositionBasis()
    {
        init();
    }

    void init()
    {
        fill(a, a + 64, 0);
        fill(pos, pos + 64, -1);
    }

    void insert(U x, int at)
    {
        assert(at >= 0);
        for (int i = 63; i >= 0; i--)
            if (x >> i & 1)
            {
                if (!a[i])
                {
                    a[i] = x;
                    pos[i] = at;
                    return;
                }
                if (at > pos[i])
                {
                    swap(a[i], x);
                    swap(pos[i], at);
                }
                x ^= a[i];
            }
    }

    bool contains(U x, long long lower = 0) const
    {
        assert(lower >= 0);
        for (int i = 63; i >= 0; i--)
            if ((x >> i & 1) && pos[i] >= lower)
                x ^= a[i];
        return x == 0;
    }

    U query(long long lower = 0, U x = 0) const
    {
        assert(lower >= 0);
        for (int i = 63; i >= 0; i--)
            if (pos[i] >= lower)
                x = max(x, x ^ a[i]);
        return x;
    }

    int rank(long long lower = 0) const
    {
        assert(lower >= 0);
        int answer = 0;
        for (int i = 0; i < 64; i++)
            answer += pos[i] >= lower;
        return answer;
    }
};
