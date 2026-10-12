#include <bits/stdc++.h>
using namespace std;

// BEGIN integer_io
bool read_ll(long long &x)
{
    int c = getchar();
    while (c != EOF && isspace(c))
        c = getchar();
    if (c == EOF)
        return false;
    bool neg = c == '-';
    if (c == '-' || c == '+')
        c = getchar();
    if (c < '0' || c > '9')
        return false;
    unsigned long long v = 0;
    unsigned long long lim = (1ULL << 63) - !neg;
    while (c >= '0' && c <= '9')
    {
        int d = c - '0';
        if (v > (lim - d) / 10)
            return false;
        v = v * 10 + d;
        c = getchar();
    }
    if (c != EOF && !isspace(c))
        return false;
    x = neg && v ? -static_cast<long long>(v - 1) - 1 : static_cast<long long>(v);
    return true;
}

void write_ll(long long x)
{
    auto v = x < 0 ? 0ULL - (unsigned long long)x : (unsigned long long)x;
    string s;
    do
    {
        s.push_back('0' + v % 10);
        v /= 10;
    } while (v);
    if (x < 0)
        putchar('-');
    for (int i = int(s.size()) - 1; i >= 0; i--)
        putchar(s[i]);
}
// END integer_io

int main()
{
    long long x;
    while (read_ll(x))
    {
        write_ll(x);
        putchar('\n');
    }
}
