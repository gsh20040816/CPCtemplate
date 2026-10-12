#include "../../src/compact/manhattan_order.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m)
    {
        vector<int> a(n);
        for (int &x : a)
            cin >> x;
        vector<ManhattanMST::Point> q(m);
        for (auto &[l, r] : q)
        {
            cin >> l >> r;
            l--;
        }
        vector<int> cnt(n + 1);
        vector<pair<long long, long long>> ans(m);
        long long sum = 0;
        auto add = [&](int i)
        {
            sum += cnt[a[i]];
            cnt[a[i]]++;
        };
        auto del = [&](int i)
        {
            cnt[a[i]]--;
            sum -= cnt[a[i]];
        };
        auto save = [&](int id, long long len)
        {
            long long den = len * (len - 1) / 2;
            if (sum == 0)
            {
                ans[id] = {0, 1};
                return;
            }
            long long d = gcd(sum, den);
            ans[id] = {sum / d, den / d};
        };
        int l = 0, r = 0;
        for (int id : manhattan_order(q))
        {
            auto [ql, qr] = q[id];
            while (l > ql)
                add(--l);
            while (r < qr)
                add(r++);
            while (l < ql)
                del(l++);
            while (r > qr)
                del(--r);
            save(id, r - l);
        }
        for (auto [num, den] : ans)
            cout << num << '/' << den << '\n';
    }
}
