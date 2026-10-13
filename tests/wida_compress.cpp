#include <bits/stdc++.h>
#include <cassert>
using namespace std;
#include "fixtures/wida_compress/main.cpp"

int main(int argc, char **argv)
{
    string mode = argc > 1 ? argv[1] : "ok";
    if (mode == "bad") {
        Compress c;
        c.add(1);
        c.init();
        cout << c.Get(2) << '\n';
        return 0;
    }
    Compress c;
    c.add(1, 3, 1, 5);
    c.init();
    cout << c.size() << ' ' << c[1] << ' ' << c[3] << ' ' << c[5] << ' ' << c[2] << ' ' << c[4] << '\n';
    cout << c.Get(c[1]) << ' ' << c.Get(c[5]) << '\n';
    cout << c.count(1) << ' ' << c.count(2) << ' ' << c.count(numeric_limits<int>::max()) << '\n';
    c.shift = 1;
    cout << c[1] << '\n';
    ostringstream shown, diverted;
    auto *old = cout.rdbuf(diverted.rdbuf());
    shown << c;
    cout.rdbuf(old);
    cout << diverted.str() << '\n' << shown.str() << '\n';
}
