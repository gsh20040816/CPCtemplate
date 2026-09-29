#include "../src/compact/palindromic_tree.hpp"
#include <algorithm>
#include <iostream>
#include <map>
#include <string>

bool palindrome(const std::string &s)
{
    return std::equal(s.begin(), s.end(), s.rbegin());
}

void check(const std::string &input)
{
    PalindromicTree a;
    std::string s;
    for (char ch : input)
    {
        s += ch;
        int x = a.add(ch);
        std::map<std::string, long long> expected;
        int longest = 0, suffixes = 0;
        long long total = 0;
        for (int l = 0; l < (int)s.size(); l++)
        {
            for (int r = l; r < (int)s.size(); r++)
            {
                auto word = s.substr(l, r - l + 1);
                if (!palindrome(word)) continue;
                expected[word]++;
                total++;
                if (r + 1 == (int)s.size())
                {
                    suffixes++;
                    longest = std::max(longest, r - l + 1);
                }
            }
        }
        assert(a.t[x].len == longest);
        assert(a.t[x].suffixes == suffixes);
        assert(a.total == total);
        assert(a.distinct() == (int)expected.size());
        {
            auto count = a.occurrences();
            assert(count == a.occurrences());
            std::map<std::string, long long> actual;
            for (int u = 2; u < (int)count.size(); u++)
            {
                int len = a.t[u].len;
                int end = a.t[u].end;
                std::string word = s.substr(end - len + 1, len);
                assert(!actual.count(word));
                actual[word] = count[u];
                int fail = a.t[u].fail;
                int fail_len = a.t[fail].len;
                int proper = 0;
                for (int k = 1; k < len; k++)
                    if (palindrome(word.substr(len - k))) proper = k;
                assert(fail_len == proper);
                assert(fail < u);
            }
            assert(actual == expected);
        }
    }
    a = PalindromicTree();
    assert(a.distinct() == 0);
    assert(a.total == 0);
    assert(a.occurrences() == std::vector<long long>(2));
}

int main()
{
    int ways = 1;
    for (int n = 0; n <= 8; n++)
    {
        for (int mask = 0; mask < ways; mask++)
        {
            int code = mask;
            std::string s(n, 'a');
            for (char &c : s)
            {
                c += code % 3;
                code /= 3;
            }
            check(s);
        }
        ways *= 3;
    }
    const int n = 500000;
    PalindromicTree a;
    for (int i = 1; i <= n; i++)
    {
        a.add('z');
        assert(a.t[a.last].len == i);
        assert(a.total == 1LL * i * (i + 1) / 2);
    }
    auto ca = a.occurrences();
    for (int u = 2; u < (int)ca.size(); u++)
    {
        assert(ca[u] == n - a.t[u].len + 1);
    }
    std::cout << "PAM vector: all ternary strings through length 8, independent "
                 "substrings, links, suffix counts, repeated occurrences, later "
                 "append/reset and 500000 letters PASS\n";
}
