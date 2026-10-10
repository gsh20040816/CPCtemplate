#include <iostream>
#include <limits>
#include <type_traits>
using namespace std;

int main() {
    cout << __cplusplus << '\n';
#ifdef __STRICT_ANSI__
    cout << 1 << '\n';
#else
    cout << 0 << '\n';
#endif
    cout << sizeof(__int128) << '\n';
    cout << is_integral_v<__int128> << '\n';
    cout << numeric_limits<__int128>::digits << '\n';
}
