#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <random>
#include "../src/compact/persistent_xor_trie.hpp"

long long checks = 0;
void require(bool ok)
{
    checks++;
    if (!ok)
    {
        cout << "ORACLE_REJECT\n";
        exit(0);
    }
}

void compare(const PersistentXorTrie &trie, const vector<uint64_t> &a)
{
    require(trie.size() == (int)a.size());
    require(trie.t.size() == 1 + a.size() * (trie.bits + 1));
    require(trie.t[0].cnt == 0 && trie.t[0].ch[0] == 0 && trie.t[0].ch[1] == 0);
    for (int l = 0; l <= (int)a.size(); l++)
        for (int r = l; r <= (int)a.size(); r++)
            for (uint64_t x : {uint64_t(0), uint64_t(1), uint64_t(2), uint64_t(3),
                               uint64_t(4), uint64_t(7), uint64_t(1) << 63, UINT64_MAX})
            {
                optional<uint64_t> want;
                for (int i = l; i < r; i++)
                    want = max(want.value_or(0), x ^ a[i]);
                require(trie.max_xor(l, r, x) == want);
            }
}

int main()
{
    for (auto [bits, cap] : vector<pair<int, int>>{{0, 1}, {65, 1}, {1, -1}})
    {
        bool rejected = false;
        try { PersistentXorTrie t(bits, cap); }
        catch (const invalid_argument &) { rejected = true; }
        require(rejected);
    }
    bool rejected = false;
    try { PersistentXorTrie t(64, INT_MAX); }
    catch (const length_error &) { rejected = true; }
    require(rejected);
    for (int bits : {1, 24, 63, 64})
    {
        PersistentXorTrie empty(bits, 0);
        require(!empty.append(0));
        compare(empty, {});
        uint64_t high = uint64_t(1) << (bits - 1);
        vector<uint64_t> a{0, 1, high, high | 1, 0, high};
        if (bits == 64) a.push_back(UINT64_MAX);
        PersistentXorTrie trie(bits, a.size());
        vector<uint64_t> prefix;
        for (uint64_t x : a)
        {
            if (bits < 64)
            {
                size_t nodes = trie.t.size(), roots = trie.root.size();
                require(!trie.append(uint64_t(1) << bits));
                require(nodes == trie.t.size() && roots == trie.root.size());
                compare(trie, prefix);
            }
            require(trie.append(x));
            prefix.push_back(x);
            compare(trie, prefix);
        }
        require(!trie.append(0));
        compare(trie, a);
    }
    int words = 1;
    for (int n = 0; n <= 6; n++, words *= 3)
        for (int mask = 0; mask < words; mask++)
        {
            PersistentXorTrie trie(2, n + 2);
            vector<uint64_t> a;
            compare(trie, a);
            int code = mask;
            for (int i = 0; i < n; i++, code /= 3)
            {
                uint64_t x = code % 3 == 2 ? 3 : code % 3;
                require(trie.append(x));
                a.push_back(x);
                compare(trie, a);
            }
            auto copy = trie;
            auto b = a;
            require(copy.append(2));
            b.push_back(2);
            compare(copy, b);
            compare(trie, a);
            require(trie.append(0));
            a.push_back(0);
            compare(trie, a);
            compare(copy, b);
        }
    mt19937_64 rng(20261004);
    for (int run = 0; run < 200; run++)
    {
        int bits = 1 + rng() % 64;
        PersistentXorTrie trie(bits, 16);
        vector<uint64_t> a;
        for (int i = 0; i < 16; i++)
        {
            uint64_t x = rng();
            if (bits < 64) x &= (uint64_t(1) << bits) - 1;
            require(trie.append(x));
            a.push_back(x);
            compare(trie, a);
            for (int q = 0; q < 32; q++)
            {
                int l = rng() % (a.size() + 1), r = rng() % (a.size() + 1);
                if (l > r) swap(l, r);
                uint64_t x = rng();
                optional<uint64_t> want;
                for (int j = l; j < r; j++) want = max(want.value_or(0), x ^ a[j]);
                require(trie.max_xor(l, r, x) == want);
            }
        }
    }
    for (int family = 0; family < 2; family++)
    {
        int n = 600001;
        PersistentXorTrie trie(24, n);
        for (int i = 0; i < n; i++) require(trie.append(family ? i % 2 : 0));
        require(!trie.append(0));
        require(trie.t.size() == 1 + size_t(n) * 25);
        for (int i = 0; i < 10000; i++)
        {
            int l = rng() % n, r = l + 1 + rng() % (n - l);
            uint64_t x = rng(), want = x;
            if (family) want = r - l == 1 ? x ^ uint64_t(l % 2) : max(x, x ^ 1);
            require(trie.max_xor(l, r, x) == want);
        }
        cout << "large " << family << ' ' << sizeof(PersistentXorTrie::Node)
             << ' ' << trie.t.size() << ' ' << trie.root.size() << '\n';
    }
    cout << "PASS " << checks << '\n';
}
