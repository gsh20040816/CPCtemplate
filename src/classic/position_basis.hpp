#pragma once
#include <algorithm>
#include <cassert>
using namespace std;

struct Position_Basis
{
    using U = unsigned long long;
    U base[64];
    int pos[64];

    Position_Basis()
    {
        Init();
    }

    void Init()
    {
        fill(base, base + 64, 0);
        fill(pos, pos + 64, -1);
    }

    void Insert(U x, int at)
    {
        assert(at >= 0);
        for ( int i = 63; i >= 0; i-- )
            if ( x >> i & 1 )
            {
                if ( !base[i] )
                {
                    base[i] = x;
                    pos[i] = at;
                    return;
                }
                if ( at > pos[i] )
                {
                    swap(base[i], x);
                    swap(pos[i], at);
                }
                x ^= base[i];
            }
    }

    bool Contains(U x, long long lower = 0) const
    {
        assert(lower >= 0);
        for ( int i = 63; i >= 0; i-- )
            if ( (x >> i & 1) && pos[i] >= lower )
                x ^= base[i];
        return x == 0;
    }

    U Query(long long lower = 0, U x = 0) const
    {
        assert(lower >= 0);
        for ( int i = 63; i >= 0; i-- )
            if ( pos[i] >= lower )
                x = max(x, x ^ base[i]);
        return x;
    }

    int Rank(long long lower = 0) const
    {
        assert(lower >= 0);
        int answer = 0;
        for ( int i = 0; i < 64; i++ )
            answer += pos[i] >= lower;
        return answer;
    }
};
