#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_misc2/01 - int128 库函数自定义.cpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    cout << (i128)0 << '|' << (i128)1234567890123456789LL << '|' << (i128)-12 << "|\n";
    cout << (long long)toi128("00123") << '|' << (long long)toi128("") << '|' << (long long)toi128("-12") << "|\n";
    i128 cap = (i128)1E16;
    i128 over = (cap + 1) * (cap + 1);
    cout << cap << '|' << sqrti128(0) << '|' << sqrti128(1) << '|' << sqrti128(2)
         << '|' << sqrti128(cap * cap) << '|' << sqrti128(over) << '|' << sqrti128(-5) << "|\n";
    cout << (long long)gcd((i128)0, (i128)0) << '|' << (long long)gcd((i128)15, (i128)10) << '|'
         << (long long)gcd((i128)-15, (i128)10) << "|\n";
}
