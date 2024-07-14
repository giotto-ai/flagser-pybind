"""Implementation of the python API for the flagser C++ library."""

import numpy as np

from ._utils import _extract_unweighted_graph, _extract_weighted_graph
from .modules.flagser_pybind import compute_homology, AVAILABLE_FILTRATIONS
from .modules.flagser_coeff_pybind import compute_homology as \
    compute_homology_coeff


def flagser_unweighted(adjacency_matrix, min_dimension=0, max_dimension=np.inf,
                       directed=True, coeff=2, approximation=None,
                       in_memory=False):
    """Compute homology of a directed/undirected flag complex.

    From an adjacency_matrix construct all cells forming its associated flag
    complex and compute its homology.

    Parameters
    ----------
    adjacency_matrix : 2d ndarray or scipy.sparse matrix, required
        Adjacency matrix of a directed/undirected unweighted graph. It is
        understood as a boolean matrix. Off-diagonal, ``0`` or ``False`` values
        denote absent edges while non-``0`` or ``True`` values denote edges
        which are present. Diagonal values are ignored.

    min_dimension : int, optional, default: ``0``
        Minimum homology dimension to compute.

    max_dimension : int or np.inf, optional, default: ``np.inf``
        Maximum homology dimension to compute.

    directed : bool, optional, default: ``True``
        If ``True``, computes homology for the directed flag complex determined
        by `adjacency_matrix`. If ``False``, computes homology for the
        undirected flag complex obtained by considering all edges as
        undirected, and it is therefore sufficient (but not necessary)
        to pass an upper-triangular matrix.

    coeff : int, optional, default: ``2``
        Compute homology with coefficients in the prime field
        :math:`\\mathbb{F}_p = \\{ 0, \\ldots, p - 1 \\}` where
        :math:`p` equals `coeff`.

    approximation : int or None, optional, default: ``None``
        Skip all cells creating columns in the reduction matrix with more than
        this number of entries. Use this for hard problems; a good value is
        often ``100,000``. Increase for higher precision, decrease for faster
        computation. If ``None``, no approximation is made and all cells are
        used. For more details, please refer to [1]_.

    in_memory: bool, optional, default: ``False``
        If ``True``, speeds up computation at the cost of increased memory
        consumption, by enabling an efficient lookup in the data structure
        instead of relying on hashing for looking up simplex indices.

    Returns
    -------
    out : dict of list
        A dictionary with the following key-value pairs:

        - ``'betti'``: list of int
          Betti numbers, per dimension greater than or equal than
          `min_dimension` and less than `max_dimension`.
        - ``'cell_count'``: list of int
          Cell counts (number of simplices), per dimension greater than or
          equal to `min_dimension` and less than `max_dimension`.
        - ``'euler'``: int
          Euler characteristic.

    Notes
    -----
    The input graphs cannot contain self-loops, i.e. edges that start and end
    in the same vertex, therefore diagonal elements of the input adjacency
    matrix will be ignored.

    References
    ----------
    .. [1] D. Luetgehetmann, "Documentation of the C++ flagser library";
           `GitHub: luetge/flagser <https://github.com/luetge/flagser/blob/\
           master/docs/documentation_flagser.pdf>`_.

    """
    # Handle default parameters
    if max_dimension == np.inf:
        _max_dimension = -1
    else:
        _max_dimension = max_dimension

    if approximation is None:
        _approximation = -1
    else:
        _approximation = approximation

    # All edge filtrations are equivalent in the static case
    _filtration = 'max'

    # Extract vertices and edges
    vertices, edges = _extract_unweighted_graph(adjacency_matrix)

    # Select the homology computer based on coeff
    if coeff == 2:
        _compute_homology = compute_homology
    else:
        _compute_homology = compute_homology_coeff

    # Call flagser binding
    homology = _compute_homology(vertices, edges, min_dimension,
                                 _max_dimension, directed, coeff,
                                 _approximation, _filtration, in_memory)[0]

    # Creating dictionary of return values
    out = {
        'betti': homology.get_betti_numbers(),
        'cell_count': homology.get_cell_count(),
        'euler': homology.get_euler_characteristic()
    }
    return out


def flagser_weighted(adjacency_matrix, max_edge_weight=None, min_dimension=0,
                     max_dimension=np.inf, directed=True, filtration="max",
                     coeff=2, approximation=None, in_memory=False):
    """Compute persistent homology of a directed/undirected filtered flag
    complex.

    From an adjacency_matrix and a filtration algorithm construct a filtered
    flag complex as a sequence of its cells associated to their filtration
    values and compute its persistent homology.

    Parameters
    ----------
    adjacency_matrix : 2d ndarray or scipy.sparse matrix, required
        Matrix representation of a directed/undirected weighted graph. Diagonal
        elements are vertex weights. The way zero values are handled depends on
        the format of the matrix. If the matrix is a dense ``numpy.ndarray``,
        zero values denote zero-weighted edges. If the matrix is a sparse
        ``scipy.sparse`` matrix, explicitly stored off-diagonal zeros and all
        diagonal zeros denote zero-weighted edges. Off-diagonal values that
        have not been explicitly stored are treated by ``scipy.sparse`` as
        zeros but will be understood as infinitely-valued edges, i.e., edges
        absent from the filtration.

    max_edge_weight : int or float or ``None``, optional, default: ``None``
        Maximum edge weight to be considered in the filtration. All edge
        weights greater than that value will be considered as
        infinitely-valued, i.e., absent from the filtration. If ``None``, all
        finite edge weights are considered.

    min_dimension : int, optional, default: ``0``
        Minimum homology dimension to compute.

    max_dimension : int or np.inf, optional, default: ``np.inf``
        Maximum homology dimension to compute.

    directed : bool, optional, default: ``True``
        If ``True``, computes persistent homology for the directed filtered
        flag complex determined by `adjacency_matrix`. If ``False``, computes
        persistent homology for the undirected filtered flag complex obtained
        by considering all weighted edges as undirected, and if two directed
        edges corresponding to the same undirected edge are explicitly assigned
        different weights and neither exceeds `max_edge_weight`, only the one
        in the upper triangular part of the adjacency matrix is considered.
        Therefore:

        - if `max_edge_weight` is ``numpy.inf``, it is sufficient to pass a
          (dense or sparse) upper-triangular matrix;
        - if `max_edge_weight` is finite, it is recommended to pass either a
          symmetric dense matrix, or a sparse upper-triangular matrix.

    filtration : string, optional, default: ``'max'``
        Algorithm determining the filtration. Warning: if an edge filtration is
        specified, it is assumed that the resulting filtration is consistent,
        meaning that the filtration value of every simplex of dimension at
        least two should evaluate to a value that is at least the maximal value
        of the filtration values of its containing edges. For performance
        reasons, this is not checked automatically.  Possible values are:
        ['dimension', 'zero', 'max', 'max3', 'max_plus_one', 'product', 'sum',
        'pmean', 'pmoment', 'remove_edges', 'vertex_degree']

    coeff : int, optional, default: ``2``
        Compute homology with coefficients in the prime field
        :math:`\\mathbb{F}_p = \\{ 0, \\ldots, p - 1 \\}` where
        :math:`p` equals `coeff`.

    approximation : int or None, optional, default: ``None``
        Skip all cells creating columns in the reduction matrix with more than
        this number of entries. Use this for hard problems; a good value is
        often ``100,000``. Increase for higher precision, decrease for faster
        computation. If ``None``, no approximation is made and all cells are
        used. For more details, please refer to [1]_.

    in_memory: bool, optional, default: ``False``
        If ``True``, speeds up computation at the cost of increased memory
        consumption, by enabling an efficient lookup in the data structure
        instead of relying on hashing for looking up simplex indices.

    Returns
    -------
    out : dict of list
        A dictionary with the following key-value pairs:

        - ``'dgms'``: list of ndarray of shape ``(n_pairs, 2)``
          A list of persistence diagrams, one for each dimension greater
          than or equal than `min_dimension` and less than `max_dimension`.
          Each diagram is an ndarray of size (n_pairs, 2) with the first
          column representing the birth time and the second column
          representing the death time of each pair.
        - ``'betti'``: list of int
          Betti numbers at filtration value `max_edge_weight`, per dimension
          greater than or equal to `min_dimension` and less than
          `max_dimension`.
        - ``'cell_count'``: list of int
          Cell counts (number of simplices) at filtration value
          `max_edge_weight`, per dimension greater than or equal to
          `min_dimension` and less than `max_dimension`.
        - ``'euler'``: int
          Euler characteristic at filtration value `max_edge_weight`.

    Notes
    -----
    The input graphs cannot contain self-loops, i.e. edges that start and end
    in the same vertex, therefore diagonal elements of the input adjacency
    matrix store vertex weights.

    References
    ----------
    .. [1] D. Luetgehetmann, "Documentation of the C++ flagser library";
           `GitHub: luetge/flagser <https://github.com/luetge/flagser/blob/\
           master/docs/documentation_flagser.pdf>`_.

    """
    # Handle default parameters
    if max_dimension == np.inf:
        _max_dimension = -1
    else:
        _max_dimension = max_dimension

    if approximation is None:
        _approximation = -1
    else:
        _approximation = approximation

    if filtration not in AVAILABLE_FILTRATIONS:
        raise ValueError("Filtration not recognized. Available filtrations "
                         "are ", AVAILABLE_FILTRATIONS)

    # Extract vertices and edges weights
    vertices, edges = _extract_weighted_graph(adjacency_matrix,
                                              max_edge_weight)

    # Select the homology computer based on coeff
    if coeff == 2:
        _compute_homology = compute_homology
    else:
        _compute_homology = compute_homology_coeff

    # Call flagser binding
    homology = _compute_homology(vertices, edges, min_dimension,
                                 _max_dimension, directed, coeff,
                                 _approximation, filtration, in_memory)[0]

    # Create dictionary of return values
    out = {
        'dgms': [np.asarray(d).reshape((-1, 2))
                 for d in homology.get_persistence_diagram()],
        'betti': homology.get_betti_numbers(),
        'cell_count': homology.get_cell_count(),
        'euler': homology.get_euler_characteristic()
    }
    return out
