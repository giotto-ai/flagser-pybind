"""Implementation of the python API for the flagser C++ library."""

import numpy as np

from ._utils import _extract_static_weights, _extract_persistence_weights
from flagser_pybind import compute_homology, implemented_filtrations


def flagser_static(flag_matrix, min_dimension=0, max_dimension=np.inf,
                   directed=True, filtration="max", coeff=2,
                   approximation=None):
    """Compute homology of a directed/undirected unweighted flag complex.

    Important: the input graphs cannot contain self-loops, i.e. edges
    that start and end in the same vertex, therefore diagonal elements
    of the flag matrix store vertex weights.

    Parameters
    ----------
    flag_matrix : 2d ndarray or scipy.sparse matrix, required
        Matrix representation of a directed/undirected unweighted graph. It is
        understood as a boolean matrix. Diagonal elements are vertex weights
        with non-``0`` or ``True`` values corresponding to ``True`` values and
        ``0`` or ``False`` values corresponding to ``False`` values.
        Off-diagonal, ``0`` or ``False`` values denote edge absence while
        non-``0`` or ``True`` values denote edges presence.

    min_dimension : int, optional, default: ``0``
        Minimum homology dimension.

    max_dimension : int or np.inf, optional, default: ``np.inf``
        Maximum homology dimension.

    directed : bool, optional, default: ``True``
        If true, computes the directed flag complex. Otherwise, it computes
        the undirected flag complex.

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
        computation. A negative value computes highest possible precision. If
        ``None``, no approximation is used.

    Returns
    -------
    out : dict of list
        A dictionary holding the results of the flagser computation. Its
        key-value pairs are as follows:

        - ``'dgms'``: list of ndarray of shape ``(n_pairs, 2)``
          A list of persistence diagrams, one for each dimension greater
          than or equal than `min_dimension` and less than `max_dimension`.
          Each diagram is an ndarray of size (n_pairs, 2) with the first
          column representing the birth time and the second column
          representing the death time of each pair.
        - ``'cell_count'``: list of int
          Cell count per dimension greater than or equal than
          `min_dimension` and less than `max_dimension`.
        - ``'betti'``: list of int
          Betti number per dimension greater than or equal than
          `min_dimension` and less than `max_dimension`.
        - ``'euler'``: int
          Euler characteristic per dimension greater than or equal than
          `min_dimension` and less than `max_dimension`.

    Notes
    -----
    For more details, please refer to the `flagser documentation \
    <https://github.com/luetge/flagser/blob/master/docs/\
    documentation_flagser.pdf>`_.

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

    if filtration not in implemented_filtrations:
        raise ValueError("Filtration not recongnized. Available filtrations "
                         "are ", implemented_filtrations)

    # Extract vertices and edges weights
    vertices, edges = _extract_static_weights(flag_matrix)

    # Call flagser binding
    homology = compute_homology(vertices, edges, min_dimension, _max_dimension,
                                directed, coeff, _approximation, filtration)

    # Creating dictionary of return values
    out = dict()
    out['dgms'] = [np.asarray(homology[0].get_persistence_diagram()[i])
                   for i in range(len(homology[0].get_persistence_diagram()))]
    out['cell_count'] = homology[0].get_cell_count()
    out['betti'] = homology[0].get_betti_numbers()
    out['euler'] = homology[0].get_euler_characteristic()

    return out


def flagser_persistence(flag_matrix, max_edge_length=None, min_dimension=0,
                        max_dimension=np.inf, directed=True, filtration="max",
                        coeff=2, approximation=None):
    """Compute persistent homology of a directed/undirected
    weighted/unweighted flag complexes.

    Important: the input graphs cannot contain self-loops, i.e. edges
    that start and end in the same vertex, therefore diagonal elements
    of the flag matrix store vertex weights.

    Parameters
    ----------
    flag_matrix : 2d ndarray or scipy.sparse matrix, required
        Matrix representation of a directed/undirected weighted/unweighted
        graph. Diagonal elements are vertex weights. The way zero values are
        handled depends on the format of the matrix. If the matrix is a dense
        ``np.ndarray``, zero values denote zero-weighted edges. If the matrix
        is a sparse ``scipy.sparse`` matrix, explicitely stored off-diagonal
        zeros  and all diagonal zeros denote zero-weighted edges. Off-diagonal
        values that have not been explicitely stored are treated by
        ``scipy.sparse`` as zeros but will be understood as infinitely-valued
        edges, i.e., edges absent from the filtration.

    max_edge_length : int or float or ``None``, optional, default: ``None``
        Maximum edge length to be considered in the filtration. All edge
        weights greater than that value will be considered as
        infinitely-valued, i.e., absent from the filtration. Additionally,
        it sets the maximum death values of diagram points. If ``None``, it is
        set to the maximum value allowed by the `flag_matrix` dtype.

    min_dimension : int, optional, default: ``0``
        Minimum homology dimension.

    max_dimension : int or np.inf, optional, default: ``np.inf``
        Maximum homology dimension.

    directed : bool, optional, default: ``True``
        If true, computes the directed flag complex. Otherwise, it computes
        the undirected flag complex.

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
        computation. A negative value computes highest possible precision. If
        ``None``, no approximation is used.

    Returns
    -------
    out : dict of list
        A dictionary holding the results of the flagser computation. Its
        key-value pairs are as follows:

        - ``'dgms'``: list of ndarray of shape ``(n_pairs, 2)``
          A list of persistence diagrams, one for each dimension greater
          than or equal than `min_dimension` and less than `max_dimension`.
          Each diagram is an ndarray of size (n_pairs, 2) with the first
          column representing the birth time and the second column
          representing the death time of each pair.
        - ``'cell_count'``: list of int
          Cell count per dimension greater than or equal than
          `min_dimension` and less than `max_dimension`.
        - ``'betti'``: list of int
          Betti number per dimension greater than or equal than
          `min_dimension` and less than `max_dimension`.
        - ``'euler'``: int
          Euler characteristic per dimension greater than or equal than
          `min_dimension` and less than `max_dimension`.

    Notes
    -----
    For more details, please refer to the `flagser documentation \
    <https://github.com/luetge/flagser/blob/master/docs/\
    documentation_flagser.pdf>`_.

    """
    # Handle default parameters
    if max_edge_length is None:
        # Get the maximum value depending on flag_matrix.dtype
        if np.issubdtype(flag_matrix.dtype, np.integer):
            _max_edge_length = np.iinfo(flag_matrix.dtype).max
        elif np.issubdtype(flag_matrix.dtype, np.float):
            _max_edge_length = np.inf
        else:
            _max_edge_length = None
    else:
        _max_edge_length = max_edge_length

    if max_dimension == np.inf:
        _max_dimension = -1
    else:
        _max_dimension = max_dimension

    if approximation is None:
        _approximation = -1
    else:
        _approximation = approximation

    if filtration not in implemented_filtrations:
        raise ValueError("Filtration not recongnized. Available filtrations "
                         "are ", implemented_filtrations)

    # Extract vertices and edges weights
    vertices, edges = _extract_persistence_weights(flag_matrix,
                                                   _max_edge_length)

    # Call flagser binding
    homology = compute_homology(vertices, edges, min_dimension, _max_dimension,
                                directed, coeff, _approximation, filtration)

    # Create dictionary of return values
    out = dict()
    out['dgms'] = [np.nan_to_num(homology[0].get_persistence_diagram()[i],
                                 posinf=_max_edge_length)
                   for i in range(len(homology[0].get_persistence_diagram()))]
    out['cell_count'] = homology[0].get_cell_count()
    out['betti'] = homology[0].get_betti_numbers()
    out['euler'] = homology[0].get_euler_characteristic()

    return out
