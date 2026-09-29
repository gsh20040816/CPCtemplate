// Independent partition reference: small parts use coin DP; large parts
// are enumerated by their count, then convolved with small-part counts.
#include <bits/stdc++.h>
using namespace std;
int main()
{
    int n, mod;
    cin >> n >> mod;
    int b = sqrt(n);
    vector<int> small(n + 1), large(n + 1), previous(n + 1), current(n + 1);
    small[0] = large[0] = previous[0] = 1 % mod;
    for (int part = 1; part <= b; part++)
        for (int s = part; s <= n; s++)
            small[s] = (small[s] + 1LL * small[s - part]) % mod;
    for (int count = 1; count * (b + 1) <= n; count++)
    {
        fill(current.begin(), current.end(), 0);
        for (int s = count * (b + 1); s <= n; s++)
        {
            current[s] = (current[s - count] + 1LL * previous[s - b - 1]) % mod;
            large[s] = (large[s] + 1LL * current[s]) % mod;
        }
        swap(previous, current);
    }
    long long answer = 0;
    for (int s = 0; s <= n; s++) answer = (answer + 1LL * small[s] * large[n - s]) % mod;
    cout << answer << '\n';
}
