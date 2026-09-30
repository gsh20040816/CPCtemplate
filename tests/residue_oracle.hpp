#pragma once
#include <bits/stdc++.h>
using namespace std;

// Independent cycle enumeration, only for small test moduli.
vector<long long> generators(int mod)
{
    int phi = 0;
    for (int x = 1; x < mod; x++)
        if (gcd(x, mod) == 1) phi++;
    vector<long long> answer;
    for (int g = 1; g < mod; g++)
        if (gcd(g, mod) == 1)
        {
            int x = 1, length = 0;
            do
            {
                x = (long long)x * g % mod;
                length++;
            } while (x != 1);
            if (length == phi) answer.push_back(g);
        }
    return answer;
}
