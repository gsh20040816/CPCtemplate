#include "../src/compact/ac_shortest.hpp"
#include <iostream>

int main()
{
    AhoCorasick ac;
    int she = ac.add("she"), he = ac.add("he"), e = ac.add("e");
    assert(ac.add("he") == he);
    ac.build();
    auto before = ac.count("sheshe");
    auto all = ac_shortest(ac, {{she, 3}, {he, 2}, {e, 1}, {he, 2}});
    assert(all[she] == 1 && all[he] == 1 && all[e] == 1);
    auto subset = ac_shortest(ac, {{she, 3}, {he, 2}});
    assert(subset[she] == 2 && subset[he] == 2 && subset[e] == INT_MAX);
    auto only = ac_shortest(ac, {{she, 3}});
    assert(only[she] == 3 && only[he] == INT_MAX);
    auto none = ac_shortest(ac, {});
    for (int x : none) assert(x == INT_MAX);
    assert(ac.count("sheshe") == before);
    assert(before[she] == 2 && before[he] == 2 && before[e] == 2);
    assert(ac_shortest(ac, {{she, 3}, {he, 2}}) == subset);
    std::cout << "AC shortest suffix: independent subsets, duplicate registrations, "
                 "repeated queries and count preservation PASS\n";
}
