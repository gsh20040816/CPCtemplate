#pragma once
#include "block_cut_forest.hpp"
#include "bridge_component_forest.hpp"

struct Biconnected : BiconnectedCore
{
    Biconnected(int n) : BiconnectedCore(n) {}

    vector<vector<int>> block_forest() const { return block_cut_forest(*this); }

    vector<vector<pair<int, int>>> bridge_forest() const
    {
        return bridge_component_forest(*this);
    }
};
