#include "../../src/compact/big_integer.hpp"

int main()
{
    string s, t;
    cin >> s >> t;
    BigInteger a(s), b(t);
    cout << (a - b).str() << '\n';
}
