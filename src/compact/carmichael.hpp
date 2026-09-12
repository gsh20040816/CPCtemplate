#pragma once
#include <cassert>
#include <numeric>
using namespace std;

// BEGIN carmichael
inline int carmichael(int n)
{
    assert(n >= 1);
    long long answer = 1;
    for (int p = 2; p <= n / p; p++)
        if (n % p == 0)
        {
            int power = 1;
            while (n % p == 0)
            {
                n /= p;
                power *= p;
            }
            int value = power / p * (p - 1);
            if (p == 2 && power >= 8) value /= 2;
            answer = answer / gcd(answer, (long long)value) * value;
        }
    if (n > 1) answer = answer / gcd(answer, (long long)(n - 1)) * (n - 1);
    return answer;
}

// END carmichael
