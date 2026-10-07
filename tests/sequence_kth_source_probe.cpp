// Included after the complete original source with its main renamed.
int main()
{
    for (int n : {16, 64, 256, 1024, 4096})
    {
        Splay::init();
        ScapeGoatTree::init();
        vector<int> v(n);
        iota(v.begin(), v.end(), 1);
        ScapeGoatTree::root = ScapeGoatTree::buildTree(v.data(), 0, n);
        auto root = ScapeGoatTree::root->root;
        int height = 0;
        for (auto p = root; p != Splay::null; p = p->ch[0])
            height++;
        if (height != n)
            return 1;
        query_visits = 0;
        for (int q = 0; q < 20; q++)
        {
            if (Splay::query(root, 0) != 0)
                return 2;
            if (root != ScapeGoatTree::root->root)
                return 3;
        }
        if (query_visits != 20LL * n)
            return 4;
        long long rank_visits = query_visits;
        query_visits = 0;
        for (int q = 0; q < 20; q++)
            if (ScapeGoatTree::query(1, n, 1) != 1)
                return 5;
        if (query_visits < 20LL * n)
            return 6;
        cout << n << ' ' << height << ' ' << rank_visits << ' ' << query_visits << '\n';
    }
}
