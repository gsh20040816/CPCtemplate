#include "../../src/compact/big_integer.hpp"

int main()
{
    vector<BigInteger> f(101);
    f[0] = 1;
    for (int i = 1; i <= 100; i++)
        f[i] = (f[i - 1] * BigInteger(4 * i - 2)).divmod(i + 1).first;
    int n;
    while (cin >> n && n != -1)
        cout << f[n].str() << '\n';
}
