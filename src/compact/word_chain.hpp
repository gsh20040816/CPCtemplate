#pragma once
#include "directed_euler.hpp"
#include <numeric>
#include <optional>
#include <string>

// BEGIN word_chain
// Lowercase nonempty words. Returns original 0-based IDs; duplicates stay distinct.
inline optional<vector<int>> word_chain(const vector<string> &words)
{
    int n = words.size();
    vector<int> order(n);
    iota(order.begin(), order.end(), 0);
    for (const auto &word : words)
    {
        assert(!word.empty());
        for (char c : word)
            assert('a' <= c && c <= 'z');
    }
    sort(order.begin(),
         order.end(),
         [&](int a, int b)
         {
             if (words[a] != words[b])
                 return words[a] < words[b];
             return a < b;
         });
    DirectedEuler graph(26);
    for (int id : order)
        graph.add(words[id].front() - 'a' + 1, words[id].back() - 'a' + 1);
    // Preserve word order in each adjacency list; do not sort by destination.
    if (!graph.run(0, false))
        return nullopt;
    vector<int> result;
    for (int id : graph.edge_ids)
        result.push_back(order[id]);
    return result;
}

// END word_chain
