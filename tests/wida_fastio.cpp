#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_misc2/05 - 快读.cpp"

int main(int argc, char **argv)
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string mode = argc > 1 ? argv[1] : "nums";
    if (mode == "layout")
    {
        cout << (io.a + sizeof io.a == io.b) << '\n';
        return 0;
    }
    if (mode == "nums")
    {
        uint32_t x, y, z;
        io >> x >> y >> z;
        io << x << ' ' << y << ' ' << z << '\n';
        return 0;
    }
    uint32_t x;
    io >> x;
    io << x << '\n';
}
