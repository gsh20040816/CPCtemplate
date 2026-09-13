#include "../src/compact/hash_table.hpp"
#include "../src/compact/ordered_set.hpp"
#include "../src/compact/rope.hpp"
int main()
{
    rp<int> a;
    a.push_back(3);
    a.insert(0, 7);
    rp<int> b = a;
    b.replace(1, 9);
    b.erase(0, 1);
    auto c = a.substr(0, 1);
    int x = a[1];
    assert(a.size() == 2 && a[0] == 7 && x == 3);
    assert(b.size() == 1 && b[0] == 9);
    assert(c.size() == 1 && c[0] == 7);
    ost<pair<int,int>> tree;
    tree.insert({3,1});
    tree.insert({3,2});
    assert(tree.order_of_key({3,0}) == 0);
    assert(tree.order_of_key({3,INT_MAX}) == 2);
    assert(tree.find_by_order(1)->second == 2);
    gp_map<int,int> gp;
    cc_map<int,int> cc;
    gp[7] = cc[7] = 9;
    assert(gp.find(7)->second == cc.find(7)->second);
    cout << "GNU handbook examples: rope version isolation, PBDS duplicate ranks and gp/cc composition PASS\n";
}
