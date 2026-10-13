#include <bits/stdc++.h>
using namespace std;
#include "fixtures/wida_hash/main.cpp"

int main()
{
    myhash h;
    uint64_t a = h(1), b = h(1), c = h(2);
    cout << (a == b) << ' ' << (a == c) << '\n';
    unordered_map<int, int, myhash> mp;
    mp[-1] = 3;
    mp[0] = 4;
    mp[1] = 5;
    cout << mp[-1] << ' ' << mp[0] << ' ' << mp[1] << ' ' << mp.count(2) << '\n';
    mymap<pair<uint64_t, uint64_t>, int, myhash> dic;
    dic[{1, 2}] = 9;
    cout << dic[{1, 2}] << ' ' << dic[{2, 1}] << '\n';
    int uniq = 1;
    vector<size_t> seen;
    for (uint64_t i = 0; i < 1000; i++) seen.push_back(h(i));
    sort(seen.begin(), seen.end());
    uniq = (int)(unique(seen.begin(), seen.end()) - seen.begin());
    cout << uniq << '\n';
}
