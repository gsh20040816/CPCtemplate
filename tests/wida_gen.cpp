#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_gen/main.cpp"

int main(int argc, char **argv)
{
    string mode = argc > 1 ? argv[1] : "tree";
    if (mode == "range") {
        cout << r(3, 3) << ' ' << r(0, 0) << '\n';
        return 0;
    }
    int n = atoi(argv[2]);
    int m = argc > 3 ? atoi(argv[3]) : -1;
    graph(n, -1, m);
}
