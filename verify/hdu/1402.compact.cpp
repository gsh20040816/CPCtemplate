#include "../../src/compact/convolution_fft.hpp"
#include <iostream>
#include <string>

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s, t;
    while (cin >> s >> t)
    {
        bool negative = (s[0] == '-') != (t[0] == '-');
        int x = s[0] == '+' || s[0] == '-';
        int y = t[0] == '+' || t[0] == '-';
        vector<int> a(s.size() - x), b(t.size() - y);
        for (int i = x; i < int(s.size()); i++) a[s.size() - 1 - i] = s[i] - '0';
        for (int i = y; i < int(t.size()); i++) b[t.size() - 1 - i] = t[i] - '0';
        auto c = convolution_fft(a, b);
        c.push_back(0);
        for (int i = 0; i + 1 < int(c.size()); i++)
        {
            c[i + 1] += c[i] / 10;
            c[i] %= 10;
        }
        while (c.size() > 1 && c.back() == 0) c.pop_back();
        if (negative && c.back() != 0) cout << '-';
        for (int i = int(c.size()) - 1; i >= 0; i--) cout << c[i];
        cout << '\n';
    }
}
