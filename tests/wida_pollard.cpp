#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_pollard/main.cpp"

static bool trial_prime(int n)
{
    if (n <= 1) return false;
    for (int i = 2; 1LL * i * i <= n; i++) if (n % i == 0) return false;
    return true;
}

static vector<int> trial_fac(int n)
{
    vector<int> ans;
    for (int i = 2; 1LL * i * i <= n; i++) while (n % i == 0) {
        ans.push_back(i);
        n /= i;
    }
    if (n > 1) ans.push_back(n);
    return ans;
}

int main(int argc, char **argv)
{
    string mode = argc > 1 ? argv[1] : "small";
    if (mode == "big") {
        cout << MR(1000000007) << '\n';
        return 0;
    }
    for (int n = 1; n <= 20000; n++) if (MR(n) != trial_prime(n)) {
        cout << "prime " << n << '\n';
        return 1;
    }
    for (int n = 1; n <= 4000; n++) if (fac(n) != trial_fac(n)) {
        cout << "fac " << n << '\n';
        return 1;
    }
    cout << "ok\n";
}
