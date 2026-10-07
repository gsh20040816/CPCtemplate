#pragma once
#include <array>
#include <cassert>
#include <vector>
using namespace std;

struct OnlineSAM
{
    struct Node
    {
        array<int, 26> go{};
        int link = -1, len = 0;
    };

    vector<Node> a{Node{}};
    long long total = 0;

    // Append c to the longest string represented by state p.
    int extend(int p, int c)
    {
        assert(0 <= p && p < (int)a.size() && 0 <= c && c < 26);
        if (int q = a[p].go[c])
        {
            if (a[q].len == a[p].len + 1) return q;
            int clone = a.size();
            Node copy = a[q];
            copy.len = a[p].len + 1;
            a.push_back(copy);
            a[q].link = clone;
            while (p != -1 && a[p].go[c] == q)
            {
                a[p].go[c] = clone;
                p = a[p].link;
            }
            return clone;
        }
        int cur = a.size();
        Node node;
        node.len = a[p].len + 1;
        a.push_back(node);
        while (p != -1 && !a[p].go[c])
        {
            a[p].go[c] = cur;
            p = a[p].link;
        }
        int parent = p == -1 ? 0 : extend(p, c);
        a[cur].link = parent;
        total += a[cur].len - a[parent].len;
        return cur;
    }
};
