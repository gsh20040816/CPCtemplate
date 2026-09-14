#pragma once
#include <array>
#include <cassert>
#include <queue>
#include <string>
#include <vector>
using namespace std;

struct GeneralSAM
{
    struct Node
    {
        array<int, 26> go{};
        int link = -1, len = 0;
    };

    vector<Node> a{Node{}};
    bool ready = false;

    void add(const string &s)
    {
        assert(!ready);
        int p = 0;
        for (char ch : s)
        {
            int c = ch - 'a';
            assert(0 <= c && c < 26);
            if (!a[p].go[c])
            {
                int v = a.size();
                a.push_back(Node{});
                a[p].go[c] = v;
            }
            p = a[p].go[c];
        }
    }

    void build()
    {
        if (ready) return;
        a.reserve(2 * a.size());
        queue<pair<int, int>> todo;
        for (int c = 0; c < 26; c++)
            if (a[0].go[c]) todo.push({0, c});
        while (!todo.empty())
        {
            auto [parent, c] = todo.front();
            todo.pop();
            int cur = a[parent].go[c], p = a[parent].link;
            a[cur].len = a[parent].len + 1;
            while (p != -1 && !a[p].go[c])
            {
                a[p].go[c] = cur;
                p = a[p].link;
            }
            if (p == -1)
                a[cur].link = 0;
            else
            {
                int q = a[p].go[c];
                if (a[p].len + 1 == a[q].len)
                    a[cur].link = q;
                else
                {
                    int clone = a.size();
                    Node copy = a[q];
                    copy.len = a[p].len + 1;
                    for (int &v : copy.go)
                        if (!a[v].len) v = 0;
                    a.push_back(copy);
                    while (p != -1 && a[p].go[c] == q)
                    {
                        a[p].go[c] = clone;
                        p = a[p].link;
                    }
                    a[q].link = a[cur].link = clone;
                }
            }
            for (int ch = 0; ch < 26; ch++)
                if (int v = a[cur].go[ch]; v && !a[v].len) todo.push({cur, ch});
        }
        ready = true;
    }

    long long distinct() const
    {
        assert(ready);
        long long ans = 0;
        for (int v = 1; v < (int)a.size(); v++) ans += a[v].len - a[a[v].link].len;
        return ans;
    }
};
