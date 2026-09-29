#include "../src/compact/string.hpp"
#include <cassert>

void check(const string &s)
{
    auto [odd, even] = manacher(s);
    int n = s.size();
    assert(odd.size() == n && even.size() == n);
    long long total = 0, expected = 0;
    for (int i = 0; i < n; i++) total += odd[i] + even[i];
    // Enumerate substrings and reverse-compare; do not duplicate the mirror recurrence.
    for (int l = 0; l < n; l++)
        for (int r = l; r < n; r++)
        {
            bool palindrome =
                equal(s.begin() + l, s.begin() + r + 1, s.rbegin() + n - r - 1);
            int len = r - l + 1;
            bool reported = len % 2 ? odd[(l + r) / 2] >= (len + 1) / 2
                                    : even[(l + r + 1) / 2] >= len / 2;
            assert(palindrome == reported);
            expected += palindrome;
        }
    assert(total == expected);
}

int main()
{
    string alphabet = string("a#$") + char(0) + char(255);
    int ways = 1;
    for (int n = 0; n <= 6; n++)
    {
        for (int mask = 0; mask < ways; mask++)
        {
            int code = mask;
            string s(n, ' ');
            for (char &c : s)
            {
                c = alphabet[code % 5];
                code /= 5;
            }
            check(s);
        }
        ways *= 5;
    }
    mt19937 rng(47721);
    for (int test = 0; test < 2000; test++)
    {
        string s(rng() % 60, ' ');
        for (char &c : s) c = char(rng() % 256);
        check(s);
    }
    const int n = 1000000;
    auto [odd, even] = manacher(string(n, 'x'));
    for (int i = 0; i < n; i++)
    {
        assert(odd[i] == min(i + 1, n - i));
        assert(even[i] == min(i, n - i));
    }
    cout << "Manacher: 19531 sentinel/zero/high-byte strings, 2000 arbitrary-byte "
            "strings, every substring predicate/count and million-character radius "
            "closed forms PASS\n";
}
