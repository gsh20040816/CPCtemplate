#include <iostream>
using namespace std;

#pragma GCC push_options
#ifdef BEFORE_HEADER
#pragma GCC optimize("Ofast")
#endif
#include "pragma_header.hpp"
#ifndef BEFORE_HEADER
#pragma GCC optimize("Ofast")
#endif
__attribute__((noinline))
double later_expression(double x, double y) {
    return (x + y) - x;
}
#pragma GCC pop_options

__attribute__((noinline))
double restored_expression(double x, double y) {
    return (x + y) - x;
}

int main() {
    double x;
    double y;
    cin >> x >> y;
    cout << header_expression(x, y) << ' ';
    cout << later_expression(x, y) << ' ';
    cout << restored_expression(x, y) << '\n';
}
