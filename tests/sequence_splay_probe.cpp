#include <bits/stdc++.h>
#include "../src/compact/sequence_splay.hpp"
using namespace std;

long long checks = 0, cases = 0;

void require(bool ok)
{
    checks++;
    if (!ok)
    {
        cout << "ORACLE_REJECT\n";
        exit(0);
    }
}

int audit(SequenceSplay &t, int x, int p, vector<int> &seen)
{
    if (!x) return 0;
    require(0 < x && x < (int)t.a.size() && !seen[x]);
    seen[x] = 1;
    require(t.a[x].fa == p);
    t.push(x);
    int l = audit(t, t.a[x].ch[0], x, seen);
    int r = audit(t, t.a[x].ch[1], x, seen);
    require(t.a[x].siz == l + r + 1);
    return l + r + 1;
}

void verify(SequenceSplay &t, const vector<int> &v)
{
    // Audit a copy so the original still retains its lazy reversals.
    auto copy = t;
    vector<int> seen(copy.a.size());
    require(audit(copy, copy.root, 0, seen) == t.n + 2);
    require(copy.order() == v);
    for (int k = (int)v.size() - 1; k >= 0; k--)
    {
        require(t.pos(v[k]) == k);
        require(t.at(k) == v[k]);
    }
    require(t.order() == v);
}

int main(int argc, char **)
{
    SequenceSplay empty(0);
    empty.reverse(0, 0);
    verify(empty, {});
    cases++;
    for (int n = 1; n <= 7; n++)
    {
        vector<int> v(n);
        iota(v.begin(), v.end(), 0);
        do
        {
            SequenceSplay base(n);
            vector<int> cur(n);
            iota(cur.begin(), cur.end(), 0);
            for (int i = 0; i < n; i++)
            {
                int p = find(cur.begin(), cur.end(), v[i]) - cur.begin();
                base.reverse(i, p + 1);
                reverse(cur.begin() + i, cur.begin() + p + 1);
            }
            require(cur == v);
            for (int l = 0; l <= n; l++)
                for (int r = l; r <= n; r++)
                {
                    auto t = base;
                    auto want = v;
                    t.reverse(l, r);
                    reverse(want.begin() + l, want.begin() + r);
                    verify(t, want);
                    // The copy must not modify the original object's tags.
                    auto fresh = base;
                    require(fresh.order() == v);
                    cases++;
                }
        } while (next_permutation(v.begin(), v.end()));
    }
    mt19937 rng(3165);
    for (int test = 0; test < 150; test++)
    {
        int n = 1 + rng() % 150;
        SequenceSplay t(n);
        vector<int> v(n);
        iota(v.begin(), v.end(), 0);
        for (int step = 0; step < 1000; step++)
        {
            int op = rng() % 4;
            if (op < 2)
            {
                int l = rng() % (n + 1), r = rng() % (n + 1);
                if (l > r) swap(l, r);
                t.reverse(l, r);
                reverse(v.begin() + l, v.begin() + r);
            }
            else if (op == 2)
            {
                int id = rng() % n;
                require(t.pos(id) == find(v.begin(), v.end(), id) - v.begin());
            }
            else
            {
                int k = rng() % n;
                require(t.at(k) == v[k]);
            }
            if (step % 79 == 0) verify(t, v);
        }
        verify(t, v);
        cases++;
    }
    cout << "SMALL " << cases << " cases " << checks << " checks\n";
    if (argc > 1) return 0;
    int n = 100000;
    SequenceSplay t(n);
    for (int k = 0; k < n; k++) require(t.at(k) == k);
    // Sequential accesses create a deep tree; traversal remains recursive.
    auto initial = t.order();
    for (int k = 0; k < n; k++) require(initial[k] == k);
    int offset = 0;
    for (int step = 0; step < n; step++)
    {
        t.reverse(1, n);
        t.reverse(0, n);
        offset = (offset + 1) % n;
        int id = (int)((long long)step * 7919 % n);
        require(t.pos(id) == (id - offset + n) % n);
        int k = (int)((long long)step * 104729 % n);
        require(t.at(k) == (k + offset) % n);
    }
    for (int step = 0; step < n; step++)
    {
        t.reverse(0, n);
        int k = step % n;
        require(t.at(k) == (step % 2 == 0 ? n - 1 - k : k));
        require(t.pos(k) == (step % 2 == 0 ? n - 1 - k : k));
    }
    initial = t.order();
    for (int k = 0; k < n; k++) require(initial[k] == k);
    cout << "PASS " << cases << " cases " << checks << " checks\n";
}
