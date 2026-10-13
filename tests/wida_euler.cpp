#include <bits/stdc++.h>
using namespace std;

static vector<int> trial(int n)
{
    vector<int> p;
    for (int i = 2; i <= n; i++) {
        bool ok = true;
        for (int j = 2; j * j <= i; j++) if (i % j == 0) ok = false;
        if (ok) p.push_back(i);
    }
    return p;
}

int main()
{
#include "fixtures/wida_euler/main.cpp"
    euler_Prime(1);
    cout << prime.size() << '\n';
    prime.clear();
    euler_Prime(30);
    auto expect = trial(30);
    cout << (prime == expect) << '\n';
    euler_Prime(10);
    cout << prime.size() << '\n';
}
