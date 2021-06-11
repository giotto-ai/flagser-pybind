"""Implementation of input/output functions for .flag files."""

import warnings
import numpy as np
import scipy.sparse as sp

from ._utils import _extract_unweighted_graph, _extract_weighted_graph


def load_unweighted_flag(fname, fmt='csr', dtype=bool):
    """Load a ``.flag`` file and return the adjacency matrix of the
    directed/undirected unweighted graph it describes.

    Parameters
    ----------
    fname : file, str, or pathlib.Path, required
        Filename of extension ``.flag`` containing the information of a flag
        matrix.

    fmt : {'dense', 'dia', 'csr', 'csc', 'lil', ...}, optional, \
        default: ``'csr'``
        Matrix format of the result. By default, a CSR sparse matrix is
        returned. Keep in mind that some matrix formats do not track zero
        values.

    dtype : data-type, optional, default: ``bool``
        Data-type of the resulting array.

    Returns
    -------
    adjacency_matrix : matrix of shape (n_vertices, n_vertices) and format \
        `fmt`
        Adjacency matrix of a directed/undirected unweighted graph. It is
        understood as a boolean matrix. Off-diagonal, ``0`` or ``False`` values
        denote absent edges while non-``0`` or ``True`` values denote edges
        which are present. Diagonal values are ignored.

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
    with open(fname, 'r') as f:
        next(f)  # Skip 'dim0' header
        n_vertices = len(f.readline().strip().split(' '))
        adjacency_matrix = sp.csr_matrix((n_vertices, n_vertices), dtype=dtype)

        # Silence sparse warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', sp.SparseEfficiencyWarning)

            next(f)  # Skip 'dim1' header
            for line in f:
                edge = line.strip().split(' ')
                adjacency_matrix[int(edge[0]), int(edge[1])] = 1

    return adjacency_matrix.asformat(fmt)


def load_weighted_flag(fname, fmt='csr', dtype=float, infinity_value=None):
    """Load a ``.flag`` file and return the adjacency matrix of the
    directed/undirected weighted graph it describes.

    Parameters
    ----------
    fname : file, str, or pathlib.Path, required
        Filename of extension ``.flag`` containing the information of a flag
        matrix.

    fmt : {'dense', 'dia', 'csr', 'csc', 'lil', ...}, optional,
        default: ``'csr'``
        Matrix format of the result. By default, a CSR sparse matrix is
        returned. Keep in mind that some matrix formats do not track zero
        values.

    dtype : data-type, optional, default: ``float``
        Data-type of the resulting array.

    infinity_value : int or float or None, optional, default: ``None``
        Value to use to denote an absence of edge. It is only useful when `fmt`
        is `'dense'`. If ``None``, it is set to the maximum value allowed by
        `dtype`.

    Returns
    -------
    adjacency_matrix : matrix of shape (n_vertices, n_vertices) and format \
        `fmt`
        Matrix representation of a directed/undirected weighted graph. Diagonal
        elements are vertex weights.

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
    # Warn if dtype is bool
    if np.issubdtype(dtype, np.bool_):
        warnings.warn("dtype is a bool type, you may want to use "
                      " the load_unweighted_flag function instead.")

    # Handle default parameter
    if infinity_value is None:
        if fmt != 'dense':
            _infinity_value = None
        else:
            # Get the maximum value depending on adjacency_matrix.dtype
            if np.issubdtype(dtype, np.integer):
                _infinity_value = np.iinfo(dtype).max
            elif np.issubdtype(dtype, np.floating):
                _infinity_value = np.inf
            else:
                _infinity_value = 0
    else:
        if fmt != 'dense':
            warnings.warn("infinity_value has been specified with a fmt that "
                          "is not 'dense' and will be ignored.")
            _infinity_value = None
        else:
            _infinity_value = infinity_value

    with open(fname, 'r') as f:
        next(f)  # Skip 'dim0' header
        vertices = np.array(f.readline().strip().split(' '), dtype=dtype)

        if fmt == 'dense':
            adjacency_matrix = np.full((len(vertices), len(vertices)),
                                       _infinity_value, dtype=dtype)
            adjacency_matrix[np.diag_indices(len(vertices))] = vertices
        else:
            adjacency_matrix = sp.csr_matrix((len(vertices), len(vertices)),
                                             dtype=dtype)

        # Silence sparse warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', sp.SparseEfficiencyWarning)
            adjacency_matrix.setdiag(vertices)

            next(f)  # Skip 'dim1' header
            for line in f:
                edge = line.strip().split(' ')
                adjacency_matrix[int(edge[0]), int(edge[1])] = float(edge[2])

    return adjacency_matrix.asformat(fmt)


def save_unweighted_flag(fname, adjacency_matrix):
    """Save the adjacency matrix of a directed/undirected unweighted graph
    into a ``.flag`` file.

    Parameters
    ----------
    fname : file, str, or pathlib.Path, required
        Filename of extension ``.flag``.

    adjacency_matrix : 2d ndarray or scipy.sparse matrix, required
        Adjacency matrix of a directed/undirected unweighted graph. It is
        understood as a boolean matrix. Off-diagonal, ``0`` or ``False`` values
        denote absent edges while non-``0`` or ``True`` values denote edges
        which are present. Diagonal values are ignored.

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
    # Extract vertices and edges
    vertices, edges = _extract_unweighted_graph(adjacency_matrix)

    with open(fname, 'w') as f:
        np.savetxt(f, vertices.reshape((1, -1)), delimiter=' ', comments='',
                   header='dim 0', fmt='%i')
        np.savetxt(f, edges, comments='', header='dim 1', fmt='%i %i %i')


def save_weighted_flag(fname, adjacency_matrix, max_edge_weight=None):
    """Save the adjacency matrix of a directed/undirected weighted graph into
    a ``.flag`` file.

    Parameters
    ----------
    fname : file, str, or pathlib.Path, required
        Filename of extension ``.flag``.

    adjacency_matrix : 2d ndarray or scipy.sparse matrix, required
        Matrix representation of a directed/undirected weighted graph. Diagonal
        elements are vertex weights. The way zero values are handled depends on
        the format of the matrix. If the matrix is a dense ``numpy.ndarray``,
        zero values denote zero-weighted edges. If the matrix is a sparse
        ``scipy.sparse`` matrix, explicitly stored off-diagonal zeros and all
        diagonal zeros denote zero-weighted edges. Off-diagonal values that
        have not been explicitely stored are treated by ``scipy.sparse`` as
        zeros but will be understood as infinitely-valued edges, i.e., edges
        absent from the filtration.

    max_edge_weight : int or float or ``None``, optional, default: ``None``
        Maximum edge weight to be considered in the filtration. All edge
        weights greater than that value will be considered as
        infinitely-valued, i.e., absent from the filtration. If ``None``, all
        finite edge weights are considered.

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
    # Extract vertices and edges weights
    vertices, edges = _extract_weighted_graph(adjacency_matrix,
                                              max_edge_weight)

    with open(fname, 'w') as f:
        np.savetxt(f, vertices.reshape((1, -1)), delimiter=' ', comments='',
                   header='dim 0', fmt='%.18e')
        np.savetxt(f, edges, comments='', header='dim 1', fmt='%i %i %.18e')
