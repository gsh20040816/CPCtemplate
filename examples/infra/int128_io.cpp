#include <bits/stdc++.h>
using namespace std;
using i128 = __int128;
using u128 = unsigned __int128;

// Invalid or out-of-range token: return false, leave x unchanged.
bool parse128(const string& s, i128& x) {
    if (s.empty()) {
        return false;
    }
    bool neg = s[0] == '-';
    size_t pos = neg || s[0] == '+';
    if (pos == s.size()) {
        return false;
    }
    u128 limit = (u128(1) << 127) - !neg;
    u128 value = 0;
    for (; pos < s.size(); pos++) {
        if (s[pos] < '0' || s[pos] > '9') {
            return false;
        }
        unsigned digit = s[pos] - '0';
        if (value > (limit - digit) / 10) {
            return false;
        }
        value = value * 10 + digit;
    }
    x = neg && value ? -i128(value - 1) - 1 : i128(value);
    return true;
}

string str128(i128 x) {
    bool neg = x < 0;
    u128 value = neg ? u128(0) - u128(x) : u128(x);
    string s;
    do {
        s.push_back('0' + value % 10);
        value /= 10;
    } while (value);
    if (neg) {
        s.push_back('-');
    }
    reverse(s.begin(), s.end());
    return s;
}

int main() {
    string s;
    while (cin >> s) {
        i128 x = 0;
        if (parse128(s, x)) {
            cout << str128(x) << '\n';
        } else {
            cout << "invalid\n";
        }
    }
}
