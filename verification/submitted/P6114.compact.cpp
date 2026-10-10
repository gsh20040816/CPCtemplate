#include <bits/stdc++.h>
#include <cassert>
using namespace std;
vector<int> lyndon(const string &s)
{
    assert(s.size() <= INT_MAX);
    int n = s.size();
    vector<int> ends;
    ends.reserve(n);
    int i = 0;
    while (i < n)
    {
        int j = i + 1, k = i;
        while (j < n && (unsigned char)s[k] <= (unsigned char)s[j])
        {
            if (s[k] == s[j])
                k++;
            else
                k = i;
            j++;
        }
        int len = j - k;
        while (i <= k)
        {
            i += len;
            ends.push_back(i);
        }
    }
    return ends;
}

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s;
    cin >> s;
    int ans = 0;
    for (int r : lyndon(s))
        ans ^= r;
    cout << ans << '\n';
}
