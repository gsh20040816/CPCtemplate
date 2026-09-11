#pragma once
#include "directed_euler.hpp"
#include <numeric>
#include <optional>
#include <string>

// BEGIN Word_Chain
// Lowercase nonempty words. Returns original 0-based IDs; duplicates stay distinct.
inline optional<vector<int>> Word_Chain(const vector<string> &words)
{
    int n = words.size();
    vector<int> order(n);
    iota(order.begin(), order.end(), 0);
    for ( const auto &word : words )
    {
        assert(!word.empty());
        for ( char c : word )
            assert('a' <= c && c <= 'z');
    }
    sort(order.begin(),
         order.end(),
         [&](int a, int b)
         {
             if ( words[a] != words[b] )
                 return words[a] < words[b];
             return a < b;
         });
    Directed_Euler<26> graph;
    graph.Init(26);
    for ( int id : order )
        graph.Insert(words[id].front() - 'a' + 1, words[id].back() - 'a' + 1);
    // Preserve word order in each adjacency list; do not sort by destination.
    if ( !graph.Run(0, false) )
        return nullopt;
    vector<int> result;
    for ( int id : graph.edge_ids )
        result.push_back(order[id]);
    return result;
}

// END Word_Chain
