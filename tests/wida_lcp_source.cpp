#include <bits/stdc++.h>
using namespace std;
#define main unused_original_main
#include "fixtures/wida_lcp/main.cpp"
#undef main

static void init_root()
{
    fill(nxt[0], nxt[0] + 26, 1);
    len[0] = -1;
}

static void build(const vector<string> &S)
{
    init_root();
    int N = (int)S.size();
    for (int i = 0; i < N; i++)
    {
        int p = 1;
        for (auto c : S[i])
        {
            p = extend(p, c - 'a');
            if (f[p] != -1)
            {
                if (f[p] == 0)
                    f[p] = i + 1;
                else if (f[p] != i + 1)
                    f[p] = -1;
            }
        }
    }
    for (int i = 1; i <= tot; i++)
        adj[lnk[i]].push_back(i);
}

static void dump(const vector<string> &S)
{
    build(S);
    cout << tot << '\n';
    for (int i = 0; i <= tot; i++)
    {
        cout << len[i] << ' ' << lnk[i] << ' ' << f[i];
        for (int c = 0; c < 26; c++)
            cout << ' ' << nxt[i][c];
        cout << ' ' << adj[i].size();
        for (int v : adj[i])
            cout << ' ' << v;
        cout << '\n';
    }
}

int main(int argc, char **argv)
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string mode = argc > 1 ? argv[1] : "main";
    if (mode == "main")
    {
        unused_original_main();
        return 0;
    }
    int N;
    cin >> N;
    vector<string> S(N);
    for (int i = 0; i < N; i++)
        cin >> S[i];
    dump(S);
}
