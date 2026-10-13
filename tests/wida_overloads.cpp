#include <bits/stdc++.h>
#include <cassert>
using namespace std;
#include "fixtures/wida_misc2/02 - 常用库函数重载.cpp"

static i64 tri_root(i64 n)
{
    return get(n);
}

int main(int argc, char **argv)
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string mode = argc > 1 ? argv[1] : "cases";
    if (mode == "get0")
    {
        cout << get(0) << '\n';
        return 0;
    }
    if (mode == "logi")
    {
        cout << logi(1, 2) << '\n';
        return 0;
    }
    if (mode == "ceil-overflow")
    {
        cout << ceilDiv(LLONG_MAX, 2) << '\n';
        return 0;
    }
    if (mode == "sqrt-overflow")
    {
        cout << sqrt(LLONG_MAX) << '\n';
        return 0;
    }
    for (i64 n : {i64(0), i64(1), i64(2), i64(8), i64(9), i64(10), i64(1) << 53, (i64(1) << 53) - 1})
        cout << n << ' ' << sqrt(n) << '\n';
    for (i64 n : {1, 2, 3, 10, 11})
        cout << "T " << n << ' ' << tri_root(n) << '\n';
    cout << "C " << ceilDiv(5, 3) << ' ' << ceilDiv(-5, 3) << ' ' << ceilDiv(-6, 3)
         << ' ' << ceilDiv(-5, -3) << '\n';
    cout << "F " << floorDiv(5, 3) << ' ' << floorDiv(-5, 3) << ' ' << floorDiv(-6, 3)
         << ' ' << floorDiv(-5, -3) << '\n';
    i64 x = 3;
    chmax(x, (i64)3);
    chmax(x, (i64)4);
    chmax(x, (i64)1);
    cout << "M " << x << '\n';
    cout << "G " << (long long)gcd((i128)15, (i128)10) << ' '
         << (long long)gcd((i128)-15, (i128)10) << '\n';
    cout << "L " << logi(2, 1) << ' ' << logi(2, 2) << ' ' << logi(2, 3) << ' ' << logi(10, 1000)
         << ' ' << llog(2, 8) << ' ' << llog(8, 2) << '\n';
}
