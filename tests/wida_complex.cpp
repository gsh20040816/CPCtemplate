#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_complex/main.cpp"

int main()
{
    cout << setprecision(20);
    Point a(3, 4), b(1, 0), c(0, 1);
    cout << dot(a, b) << ' ' << cross(b, c) << ' ' << cross(b, b) << ' ' << length(a) << ' ' << dist(a, Point(0, 0)) << '\n';
    Point o(0, 0), h(4, 0), p(1, 1), q(1, 3);
    cout << get(o, h, p, q) << '\n';
    Point r(0, 2), s(2, 2);
    cout << get(o, h, r, s) << '\n';
}
