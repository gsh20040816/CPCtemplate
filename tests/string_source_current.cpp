#include "../src/compact/string.hpp"
int main()
{
    int cases;
    cin >> cases;
    while (cases--)
    {
        int n, limit;
        cin >> n >> limit;
        vector<int> a(n);
        for (int &x : a)
            cin >> x;
        SuffixArray suffix(a, n + 1);
        vector<int> remain(n + 1);
        for (int i = n - 1; i >= 0; i--)
        {
            if (a[i] <= limit)
                remain[i] = remain[i + 1] + 1;
        }
        auto height = suffix.lcp;
        for (int k = 1; k < n; k++)
            height[k] = min({height[k], remain[suffix.sa[k - 1]], remain[suffix.sa[k]]});
        for (int i = 0; i < n; i++)
            cout << suffix.sa[i] << ' ' << suffix.rk[i] << ' ' << height[i] << ' ';
        cout << '\n';
    }
}
