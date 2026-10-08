#include <cstdio>
#include <algorithm>
#include <vector>
#include <iostream>
using namespace std;
const int max1 = 1e6;
bool Check(int n)
{
    int tmp = n, prime = 0;
    for (int i = 2; i * i <= tmp; i++)
    {
        if (!(tmp % i))
        {
            if (i == 2 || prime)
                return false;
            prime = i;
            while (!(tmp % i))
                tmp /= i;
        }
    }
    if (tmp == 2 || (tmp != 1 && prime))
        return false;
    return true;
}
int Get_Phi(int n)
{
    int tmp = n, ans = n;
    for (int i = 2; i * i <= tmp; i++)
    {
        if (!(tmp % i))
        {
            ans = ans / i * (i - 1);
            while (!(tmp % i))
                tmp /= i;
        }
    }
    if (tmp != 1)
        ans = ans / tmp * (tmp - 1);
    return ans;
}
int Quick_Power(int base, int p, int mod)
{
    int res = 1;
    while (p)
    {
        if (p & 1)
            res = 1LL * res * base % mod;
        p >>= 1;
        base = 1LL * base * base % mod;
    }
    return res;
}
void Work()
{
    int n, d;
    vector<int> ans;
    ans.clear();
    scanf("%d%d", &n, &d);
    if (n == 2)
        ans.push_back(1);
     else if (n == 4)
         ans.push_back(3);
     else
     {
         if (((n & 1) && Check(n)) || (!(n & 1) && Check(n >> 1)))
         {
             int phi = Get_Phi(n), tmp = phi;
             vector<int> prime;
             for (int i = 2; i * i <= tmp; i++)
             {
                 if (!(tmp % i))
                 {
                     prime.push_back(i);
                     while (!(tmp % i))
                         tmp /= i;
                 }
             }
             if (tmp != 1)
                 prime.push_back(tmp);
             for (int i = 1; i <= n; i++)
             {
                 if (__gcd(i, n) == 1)
                 {
                     bool flag = true;
                     for (auto p : prime)
                         if (Quick_Power(i, phi / p, n) == 1)
                         {
                             flag = false;
                             break;
                         }
                     if (flag)
                     {
                         ans.push_back(i);
                         break;
                     }
                 }
             }
             int power = ans.front(), now = 1;
             ans.clear();
            for (int i = 1; i <= phi; i++)
            {
                now = 1LL * now * power % n;
                if (__gcd(i, phi) == 1)
                    ans.push_back(now);
            }
            sort(ans.begin(), ans.end());
        }
    }
    printf("%lu\n", ans.size());
    for (unsigned int i = 0; i < ans.size(); i++)
        if (!((i + 1) % d))
             printf("%d ", ans[i]);
    printf("\n");
    return;
}
int main()
{
    int T;
    scanf("%d", &T);
    while (T--)
        Work();
    return 0;
}
