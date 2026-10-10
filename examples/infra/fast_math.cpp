#include <bits/stdc++.h>
using namespace std;

__attribute__((noinline))
double expression(double x, double y) {
    return (x + y) - x;
}

int main() {
    double x;
    double y;
    cin >> x >> y;
    cout << setprecision(17) << expression(x, y) << '\n';
}
