#include "../../src/compact/cartesian_tree.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<int> a(n);
    for (int &x : a) cin >> x;
    auto tree = cartesian_tree(a);
    long long left = 0;
    long long right = 0;
    for (int i = 0; i < n; i++)
    {
        left ^= 1LL * (i + 1) * (tree.left[i] + 2);
        right ^= 1LL * (i + 1) * (tree.right[i] + 2);
    }
    cout << left << ' ' << right << '\n';
}
