#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build
if [[ -z "${CXX:-}" ]]; then
    if command -v g++-16 >/dev/null 2>&1; then CXX=g++-16; else CXX=g++; fi
fi
flags=(-std=c++20 -O2 -Wall -Wextra)
if [[ -d /opt/homebrew/include/boost ]]; then flags+=(-I/opt/homebrew/include); fi
if [[ "${SANITIZE:-0}" == 1 ]]; then flags+=(-O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer); fi
"$CXX" "${flags[@]}" tests/property.cpp -o build/property
build/property

"$CXX" "${flags[@]}" tests/classic.cpp -o build/classic
build/classic

"$CXX" "${flags[@]}" tests/algebra.cpp -o build/algebra
build/algebra
"$CXX" "${flags[@]}" tests/optimization.cpp -o build/optimization
build/optimization
"$CXX" "${flags[@]}" tests/graph_advanced.cpp -o build/graph_advanced
build/graph_advanced
"$CXX" "${flags[@]}" tests/geometry_extra.cpp -o build/geometry_extra
build/geometry_extra
"$CXX" "${flags[@]}" tests/dual.cpp -o build/dual
build/dual
"$CXX" "${flags[@]}" tests/lowlink.cpp -o build/lowlink
build/lowlink
"$CXX" "${flags[@]}" tests/boundaries.cpp -o build/boundaries
build/boundaries
"$CXX" "${flags[@]}" tests/trees.cpp -o build/trees
build/trees

"$CXX" "${flags[@]}" tests/gcd_sequence.cpp -o build/gcd_sequence
build/gcd_sequence

"$CXX" "${flags[@]}" tests/blossom.cpp -o build/blossom
build/blossom

"$CXX" "${flags[@]}" tests/recurrence.cpp -o build/recurrence
build/recurrence

"$CXX" "${flags[@]}" tests/tarjan.cpp -o build/tarjan
build/tarjan

"$CXX" "${flags[@]}" -pthread tests/biconnected.cpp -o build/biconnected
build/biconnected

"$CXX" "${flags[@]}" tests/palindromic_tree.cpp -o build/palindromic_tree
build/palindromic_tree

"$CXX" "${flags[@]}" -pthread tests/centroid.cpp -o build/centroid
build/centroid

"$CXX" "${flags[@]}" -pthread tests/dsu_on_tree.cpp -o build/dsu_on_tree
build/dsu_on_tree

"$CXX" "${flags[@]}" tests/affine_segment_tree.cpp -o build/affine_segment_tree
build/affine_segment_tree

"$CXX" "${flags[@]}" -pthread tests/virtual_tree.cpp -o build/virtual_tree
build/virtual_tree

python3 tests/virtual_tree_application.py

"$CXX" "${flags[@]}" tests/persistent_array.cpp -o build/persistent_array
build/persistent_array

"$CXX" "${flags[@]}" tests/circle_precision.cpp -o build/circle_precision
build/circle_precision

"$CXX" "${flags[@]}" -pthread tests/hld.cpp -o build/hld
build/hld

"$CXX" "${flags[@]}" -pthread tests/hopcroft_karp.cpp -o build/hopcroft_karp
build/hopcroft_karp

"$CXX" "${flags[@]}" tests/graph_contracts.cpp -o build/graph_contracts
build/graph_contracts

"$CXX" "${flags[@]}" tests/weighted_matching.cpp -o build/weighted_matching
build/weighted_matching

"$CXX" "${flags[@]}" tests/exlucas.cpp -o build/exlucas
build/exlucas

"$CXX" "${flags[@]}" tests/interpolation.cpp -o build/interpolation
build/interpolation

"$CXX" "${flags[@]}" tests/discrete_log.cpp -o build/discrete_log
build/discrete_log

"$CXX" "${flags[@]}" -pthread tests/tree_path_kth.cpp -o build/tree_path_kth
build/tree_path_kth

"$CXX" "${flags[@]}" tests/dynamic_kth.cpp -o build/dynamic_kth
build/dynamic_kth

"$CXX" "${flags[@]}" tests/persistent_distinct.cpp -o build/persistent_distinct
build/persistent_distinct

"$CXX" "${flags[@]}" tests/modular_sqrt.cpp -o build/modular_sqrt
build/modular_sqrt

"$CXX" "${flags[@]}" -pthread tests/maximum_closure.cpp -o build/maximum_closure
build/maximum_closure

"$CXX" "${flags[@]}" tests/support_hull.cpp -o build/support_hull
build/support_hull

"$CXX" "${flags[@]}" tests/suffix_array.cpp -o build/suffix_array
build/suffix_array

"$CXX" "${flags[@]}" tests/suffix_lcp.cpp -o build/suffix_lcp
build/suffix_lcp

"$CXX" "${flags[@]}" tests/xor_basis.cpp -o build/xor_basis
build/xor_basis

"$CXX" "${flags[@]}" tests/position_basis.cpp -o build/position_basis
build/position_basis

"$CXX" "${flags[@]}" tests/basis_intersection.cpp -o build/basis_intersection
build/basis_intersection

"$CXX" "${flags[@]}" -pthread tests/xor_walk.cpp -o build/xor_walk
build/xor_walk

"$CXX" "${flags[@]}" -pthread tests/vertex_removal.cpp -o build/vertex_removal
build/vertex_removal

"$CXX" "${flags[@]}" -pthread tests/edge_components.cpp -o build/edge_components
build/edge_components

"$CXX" "${flags[@]}" -pthread tests/bridge_augmentation.cpp -o build/bridge_augmentation
build/bridge_augmentation

"$CXX" "${flags[@]}" -pthread tests/offline_lca.cpp -o build/offline_lca
build/offline_lca

"$CXX" "${flags[@]}" -pthread tests/euler_lca.cpp -o build/euler_lca
build/euler_lca

"$CXX" "${flags[@]}" -pthread tests/lifting_lca.cpp -o build/lifting_lca
build/lifting_lca

"$CXX" "${flags[@]}" tests/path_intersection.cpp -o build/path_intersection
build/path_intersection

"$CXX" "${flags[@]}" -pthread tests/directed_euler.cpp -o build/directed_euler
build/directed_euler

"$CXX" "${flags[@]}" -pthread tests/undirected_euler.cpp -o build/undirected_euler
build/undirected_euler

"$CXX" "${flags[@]}" -pthread tests/word_chain.cpp -o build/word_chain
build/word_chain

"$CXX" "${flags[@]}" -pthread tests/mixed_euler.cpp -o build/mixed_euler
build/mixed_euler

"$CXX" "${flags[@]}" -pthread tests/odd_cycle_vertices.cpp -o build/odd_cycle_vertices
build/odd_cycle_vertices

"$CXX" "${flags[@]}" -pthread tests/lex_two_sat.cpp -o build/lex_two_sat
build/lex_two_sat

"$CXX" "${flags[@]}" tests/crt.cpp -o build/crt
build/crt

python3 tests/widget_factory_application.py

"$CXX" "${flags[@]}" tests/garner.cpp -o build/garner
build/garner

"$CXX" "${flags[@]}" tests/lucas.cpp -o build/lucas
build/lucas

"$CXX" "${flags[@]}" tests/primitive_root.cpp -o build/primitive-root
build/primitive-root

"$CXX" "${flags[@]}" tests/carmichael.cpp -o build/carmichael
build/carmichael

"$CXX" "${flags[@]}" tests/binomial.cpp -o build/binomial
build/binomial

"$CXX" "${flags[@]}" tests/batch_inverse.cpp -o build/batch-inverse
build/batch-inverse

"$CXX" "${flags[@]}" tests/inverse_table.cpp -o build/inverse-table
build/inverse-table

"$CXX" "${flags[@]}" tests/segmented_sieve.cpp -o build/segmented_sieve
build/segmented_sieve
python3 tests/prime_distance_application.py

"$CXX" "${flags[@]}" tests/linear_equation.cpp -o build/linear_equation
build/linear_equation
python3 tests/linear_equation_application.py

"$CXX" "${flags[@]}" tests/linear_congruence.cpp -o build/linear_congruence
build/linear_congruence
python3 tests/frog_meeting_application.py

"$CXX" "${flags[@]}" tests/crt_system.cpp -o build/crt_system
build/crt_system

"$CXX" "${flags[@]}" tests/linear_sieve.cpp -o build/linear_sieve
build/linear_sieve

"$CXX" "${flags[@]}" tests/primality_factorization.cpp -o build/primality_factorization
build/primality_factorization

python3 tests/factorization_application.py

"$CXX" "${flags[@]}" tests/euler_phi.cpp -o build/euler_phi
build/euler_phi

"$CXX" "${flags[@]}" tests/coprime_pairs.cpp -o build/coprime_pairs
build/coprime_pairs
python3 tests/coprime_pairs_application.py

"$CXX" "${flags[@]}" tests/phi_inversion.cpp -o build/phi_inversion
build/phi_inversion

"$CXX" "${flags[@]}" tests/dujiao.cpp -o build/dujiao
build/dujiao

"$CXX" "${flags[@]}" tests/partitions.cpp -o build/partitions
build/partitions

"$CXX" "${flags[@]}" tests/divisor_sum.cpp -o build/divisor_sum
build/divisor_sum
python3 tests/divisor_sum_application.py

"$CXX" "${flags[@]}" tests/floor_sum.cpp -o build/floor_sum
build/floor_sum

"$CXX" "${flags[@]}" tests/floor_moments.cpp -o build/floor_moments
build/floor_moments
python3 tests/floor_moments_application.py

"$CXX" "${flags[@]}" tests/floor_moments_large.cpp -o build/floor_moments_large
build/floor_moments_large

"$CXX" "${flags[@]}" tests/arborescence.cpp -o build/arborescence
build/arborescence

"$CXX" "${flags[@]}" tests/global_min_cut.cpp -o build/global_min_cut
build/global_min_cut

"$CXX" "${flags[@]}" tests/gomory_hu.cpp -o build/gomory_hu
build/gomory_hu

"$CXX" "${flags[@]}" tests/cut_tree_queries.cpp -o build/cut_tree_queries
build/cut_tree_queries

python3 tests/gomory_hu_application.py

"$CXX" "${flags[@]}" tests/halfplanes.cpp -o build/halfplanes
build/halfplanes

"$CXX" "${flags[@]}" tests/geometry_extra_audit.cpp -o build/geometry_extra_audit
build/geometry_extra_audit

"$CXX" "${flags[@]}" tests/geometry_3d.cpp -o build/geometry_3d
build/geometry_3d

"$CXX" "${flags[@]}" tests/closest_pair.cpp -o build/closest_pair
build/closest_pair
python3 tests/closest_pair_application.py

"$CXX" "${flags[@]}" tests/circle_tangents.cpp -o build/circle_tangents
build/circle_tangents

"$CXX" "${flags[@]}" tests/enclosing_circle.cpp -o build/enclosing_circle
build/enclosing_circle
python3 tests/enclosing_circle_application.py
