#pragma once
#include <cassert>
#include <climits>
#include <cstdint>
#include <optional>
#include <stdexcept>
#include <vector>
using namespace std;

struct PersistentXorTrie
{
    using U = uint64_t;
    struct Node
    {
        int ch[2] = {}, cnt = 0;
    };
    int bits, cap;
    vector<Node> t{Node{}};
    vector<int> root{0};

    PersistentXorTrie(int bits, int cap) : bits(bits), cap(cap)
    {
        if (bits < 1 || bits > 64 || cap < 0)
            throw invalid_argument("PersistentXorTrie domain");
        if (cap > (INT_MAX - 1) / (bits + 1))
            throw length_error("PersistentXorTrie capacity");
        reserve();
    }

    void reserve()
    {
        t.reserve(1 + size_t(cap) * (bits + 1));
        root.reserve(size_t(cap) + 1);
    }

    int size() const { return (int)root.size() - 1; }

    bool append(U x)
    {
        if (size() == cap || (bits < 64 && (x >> bits))) return false;
        reserve(); // A copied vector need not preserve its original capacity.
        int old = root.back(), p = t.size();
        Node copy = t[old];
        t.push_back(copy);
        root.push_back(p);
        t[p].cnt++;
        for (int d = bits - 1; d >= 0; d--)
        {
            int b = x >> d & 1, q = t.size();
            old = t[old].ch[b];
            copy = t[old];
            t.push_back(copy);
            t[p].ch[b] = q;
            p = q;
            t[p].cnt++;
        }
        return true;
    }

    optional<U> max_xor(int l, int r, U x) const
    {
        assert(0 <= l && l <= r && r <= size());
        if (l == r) return nullopt;
        int a = root[l], b = root[r];
        U y = 0;
        for (int d = bits - 1; d >= 0; d--)
        {
            int k = (x >> d & 1) ^ 1;
            if (t[t[b].ch[k]].cnt == t[t[a].ch[k]].cnt) k ^= 1;
            y |= U(k) << d;
            a = t[a].ch[k];
            b = t[b].ch[k];
        }
        return x ^ y;
    }
};
