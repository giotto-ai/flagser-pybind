#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <stdio.h>

#include <flagser/src/flagser.cpp>
#include <iostream>
#include <string>

namespace py = pybind11;

#ifdef USE_COEFFICIENTS
PYBIND11_MODULE(flagser_coeff_pybind, m) {
#else
PYBIND11_MODULE(flagser_pybind, m) {
#endif

  /* `persistence_computer_t<T>` class requires to know if the computation is
   * in memory or not. Because, `persistence_computer_t<T>` contains the method
   * to retrieve the different results of the homology computation.
   * This class allows to store results from the computation independently if
   * it was in memory or not.
   * This duplicates the code in `persistence_computer_t`.
   */
  class PersistenceValues {
   public:
    PersistenceValues();
    PersistenceValues(index_t eu, std::vector<size_t> bn,
                      std::vector<std::vector<std::pair<value_t, value_t>>> bd,
                      std::vector<size_t> cc)
        : euler_characteristic(eu),
          betti_numbers(bn),
          birth_deaths_by_dim(bd),
          cell_count(cc) {}
    index_t get_euler_characteristic() { return euler_characteristic; }

    std::vector<size_t> get_betti_numbers() { return betti_numbers; }

    size_t get_betti_numbers(size_t dimension) {
      return betti_numbers[dimension];
    }

    std::vector<std::vector<std::pair<value_t, value_t>>>
    get_persistence_diagram() {
      return birth_deaths_by_dim;
    }

    std::vector<std::pair<value_t, value_t>> get_persistence_diagram(
        size_t dimension) {
      return birth_deaths_by_dim[dimension];
    }

    std::vector<size_t> get_cell_count() { return cell_count; }

    size_t get_cell_count(size_t dimension) { return cell_count[dimension]; }

   private:
    index_t euler_characteristic = 0;
    std::vector<size_t> betti_numbers;
    std::vector<std::vector<std::pair<value_t, value_t>>> birth_deaths_by_dim;
    std::vector<size_t> cell_count;
  };

  m.doc() = "Python interface for flagser";

  m.attr("AVAILABLE_FILTRATIONS") = custom_filtration_computer;

  py::class_<PersistenceValues>(m, "PersistenceValues", py::module_local())
      .def("get_euler_characteristic",
           &PersistenceValues::get_euler_characteristic)
      .def("get_betti_numbers",
           py::overload_cast<>(&PersistenceValues::get_betti_numbers))
      .def("get_betti_numbers",
           py::overload_cast<size_t>(&PersistenceValues::get_betti_numbers))
      .def("get_cell_count",
           py::overload_cast<>(&PersistenceValues::get_cell_count))
      .def("get_cell_count",
           py::overload_cast<size_t>(&PersistenceValues::get_cell_count))
      .def("get_persistence_diagram",
           py::overload_cast<>(&PersistenceValues::get_persistence_diagram))
      .def("get_persistence_diagram",
           py::overload_cast<size_t>(
               &PersistenceValues::get_persistence_diagram));

  m.def("compute_homology", [](std::vector<value_t>& vertices,
                               std::vector<std::vector<value_t>>& edges,
                               unsigned short min_dim, short max_dim,
                               bool directed, coefficient_t modulus,
                               signed int approximation, std::string filtration,
                               bool in_memory) {
    flagser_parameters params;

    // Save std::cout status
    auto cout_buff = std::cout.rdbuf();

    // Minimum dimension parameter
    params.min_dimension = min_dim;

    // Maximum dimension parameter
    unsigned short effective_max_dim = max_dim;
    if (max_dim < 0) {
      effective_max_dim = std::numeric_limits<unsigned short>::max();
    }
    params.max_dimension = effective_max_dim;

    // Filtration argument
    params.filtration_algorithm.reset(get_filtration_computer(filtration));

    // Modulus/Coefficient parameter
    params.modulus = modulus;

    // If approximation is negative it falls back to type::numeric_limits
    params.approximate_computation = approximation ? true : false;
    params.max_entries =
        params.approximate_computation > 0 ? approximation : params.max_entries;

    // Directed parameter
    params.directed = directed;

    // Output file is not used
    params.output_name = std::string("to_delete.flag");
    // Calls Trivial output, disable the generation of an output file
    params.output_format = std::string("none");

    // Enable in memory computation for directed flags
    // Threading memory for performances
    params.input_format = in_memory;

    // Building the filtered directed graph
    auto graph = filtered_directed_graph_t(vertices, params.directed);

    HAS_EDGE_FILTRATION has_edge_filtration =
        HAS_EDGE_FILTRATION::TOO_EARLY_TO_DECIDE;

    // If we have at least one edge
    if (edges.size() && has_edge_filtration == HAS_EDGE_FILTRATION::MAYBE) {
      // If the edge has three components, the last is the filtration
      // value
      has_edge_filtration = edges[0].size() == 2 ? HAS_EDGE_FILTRATION::NO
                                                 : HAS_EDGE_FILTRATION::YES;
    }

    for (auto& edge : edges) {
      if (has_edge_filtration == NO) {
        graph.add_edge(edge[0], edge[1]);
      } else {
        if (edge[2] < std::max(vertices[edge[0]], vertices[edge[1]])) {
          std::string err_msg =
              "The data contains an edge "
              "filtration that contradicts the vertex "
              "filtration, the edge (" +
              std::to_string(edge[0]) + ", " + std::to_string(edge[1]) +
              ") has filtration value " + std::to_string(edge[2]) +
              ", which is lower than min(" + std::to_string(vertices[edge[0]]) +
              ", " + std::to_string(vertices[edge[1]]) +
              "), the filtrations of its edges.";
          throw std::runtime_error(err_msg);
        }
        graph.add_filtered_edge((vertex_index_t)edge[0],
                                (vertex_index_t)edge[1], edge[2]);
      }
    }

    // Disable cout
    std::cout.rdbuf(nullptr);

    // Will contain Homology results
    std::vector<PersistenceValues> vec_pv;

    // Running flagser's compute_homology routine
    if (params.in_memory) {
      auto subgraph_persistence_computer =
          compute_homology<directed_flag_complex_in_memory_computer::
                               directed_flag_complex_in_memory_computer_t>(
              graph, params);
      /* FIXME: right now, the loop needs to be duplicated because in order
       * right now, it's not possible to create a vector of optional's
       */
      for (auto& sub : subgraph_persistence_computer)
        vec_pv.emplace_back(PersistenceValues(
            sub.get_euler_characteristic(), sub.get_betti_numbers(),
            sub.get_persistence_diagram(), sub.get_cell_count()));

    } else {
      auto subgraph_persistence_computer = compute_homology<
          directed_flag_complex_computer::directed_flag_complex_computer_t>(
          graph, params);
      /* FIXME: Remove when supported the duplicated loop */
      for (auto& sub : subgraph_persistence_computer)
        vec_pv.emplace_back(PersistenceValues(
            sub.get_euler_characteristic(), sub.get_betti_numbers(),
            sub.get_persistence_diagram(), sub.get_cell_count()));
    }

    // Re-enable again cout
    std::cout.rdbuf(cout_buff);

    return vec_pv;
  });
}
