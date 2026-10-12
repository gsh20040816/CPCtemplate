#define main exhaustive_main
#include "weighted_blossom.cpp"
#undef main

int main()
{
    mt19937_64 rng(98712661);
    for (int type = 0; type < 8; type++)
    {
        WeightedBlossom g(400);
        for (int u = 1; u <= 400; u++)
            for (int v = u + 1; v <= 400; v++)
            {
                if (type == 0 && (u - 1) / 5 != (v - 1) / 5) continue;
                if (type == 1 && rng() % 40) continue;
                if (type == 2 && rng() % 4) continue;
                long long w = rng() % 500000000 + 1;
                if (type == 3) w = 7;
                if (type == 4) w = 0;
                if (type == 5) w = -w;
                if (type == 6) w = LLONG_MAX - w;
                if (type == 7) w = LLONG_MIN + w;
                g.add_edge(u, v, w);
            }
        verify(g, false);
        verify(g, true);
    }
    cout << checks << " large primal/dual certificate checks PASS\n";
    return 0;
}
