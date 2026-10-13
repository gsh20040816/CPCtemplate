#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_i128/main.cpp"

static string show(i64 x)
{
    ostringstream os;
    os << x;
    return os.str();
}

int main(int argc, char **argv)
{
    string mode = argc > 1 ? argv[1] : "ok";
    if (mode == "min") {
        i64 x = ((i64)1) << 127;
        cout << x;
        return 0;
    }
    i64 a, b;
    cin >> a >> b;
    cout << show(a) << ' ' << show(b) << ' ' << (long long)my128::abs(a) << '\n';
}
