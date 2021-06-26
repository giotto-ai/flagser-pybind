"""Testing for the python bindings of the C++ flagser library."""

import os
import numpy as np
import pytest
from multiprocessing import Pool
from numpy.testing import assert_almost_equal

from pyflagser import load_unweighted_flag, load_weighted_flag, \
    flagser_unweighted, flagser_weighted


betti = {
    'a.flag': [1, 2, 0],
    'b.flag': [1, 0, 0],
    'c.flag': [1, 5],
    'd.flag': [1, 0, 1],
    'e.flag': [1, 0, 0, 0],
    'f.flag': [1, 0, 0],
    'd2.flag': [1, 1],
    'd3.flag': [1, 0, 2],
    'd3-allzero.flag': [1, 0, 2],
    'double-d3.flag': [1, 0, 5],
    'double-d3-allzero.flag': [1, 0, 5],
    'd4.flag': [1, 0, 0, 9],
    'd4-allzero.flag': [1, 0, 0, 9],
    'd5.flag': [1, 0, 0, 0, 44],
    'd7.flag': [1, 0, 0, 0, 0, 0, 1854],
    'medium-test-data.flag': [14237, 39477, 378, 0],
    'd10.flag': [1, 0, 0, 0, 0, 0, 0, 0, 0, 1334961],
}


cell_count = {
    'a.flag': [5, 7, 1],
    'b.flag': [4, 6, 3],
    'c.flag': [8, 12],
    'd.flag': [5, 9, 6],
    'e.flag': [5, 9, 7, 2],
    'f.flag': [3, 5, 3],
    'd2.flag': [2, 2],
    'd3.flag': [3, 6, 6],
    'd3-allzero.flag': [3, 6, 6],
    'double-d3.flag': [4, 10, 12],
    'double-d3-allzero.flag': [4, 10, 12],
    'd4.flag': [4, 12, 24, 24],
    'd4-allzero.flag': [4, 12, 24, 24],
    'd5.flag': [5, 20, 60, 120, 120],
    'd7.flag': [7, 42, 210, 840, 2520, 5040, 5040],
    'medium-test-data.flag': [31346, 68652, 12694, 250],
    'd10.flag': [10, 90, 720, 5040, 30240, 151200, 604800,
                 1814400, 3628800, 3628800],
}


# Filtrations are only tested for d5.flag, see conftest.py
filtrations_results = {
    'dimension':
    {
        'dgms': [
            np.array([[0., 1.],
                      [0., 1.],
                      [0., 1.],
                      [0., 1.],
                      [0., np.inf]]),
            np.array([[1., 2.],
                      [1., 2.],
                      [1., 2.],
                      [1., 2.],
                      [1., 2.],
                      [1., 2.]])]
    },
    'zero':
    {
        'dgms': [
            np.array([[0., np.inf]])]
    },
    'max':
    {
        'dgms': [
            np.array([[0.44, 1.00999999],
                      [0.36000001, 1.125],
                      [0.33000001, 1.14499998],
                      [0.88999999, 1.17999995],
                      [0.11,       np.inf]]),
            np.array([[1.29499996, 1.34000003],
                      [1.20000005, 1.65499997]])]
    },
    'max3':
    {
        'dgms': [
            np.array([[0.44, 1.00999999],
                      [0.36000001, 1.125],
                      [0.33000001, 1.14499998],
                      [0.88999999, 1.17999995],
                      [0.11,       np.inf]]),
            np.array([[1.29499996, 1.34000003],
                      [1.20000005, 1.65499997]])]
    },
    'max_plus_one':
    {
        'dgms': [
            np.array([[0.44, 1.00999999],
                      [0.36000001, 1.125],
                      [0.33000001, 1.14499998],
                      [0.88999999, 1.17999995],
                      [0.11,       np.inf]]),
            np.array([[1.76999998, 2.76999998],
                      [1.755, 2.75500011],
                      [1.65499997, 2.65499997],
                      [1.34000003, 2.34000015],
                      [1.29499996, 2.34000015],
                      [1.20000005, 2.65499997]])]
    },
    'product':
    {
        'dgms': [
            np.array([[0.44, 1.00999999],
                      [0.36000001, 1.125],
                      [0.33000001, 1.14499998],
                      [0.88999999, 1.17999995],
                      [0.11,       np.inf]]),
            np.array([[1.76999998, 2.04691648],
                      [1.755, 1.99411869],
                      [1.65499997, 1.97242892],
                      [1.34000003, 1.77884996],
                      [1.29499996, 2.08236003],
                      [1.20000005, 2.27397013]])]
    },
    'sum':
    {
        'dgms': [
            np.array([[0.44, 1.00999999],
                      [0.36000001, 1.125],
                      [0.33000001, 1.14499998],
                      [0.88999999, 1.17999995],
                      [0.11,       np.inf]]),
            np.array([[1.76999998, 3.92499995],
                      [1.755, 3.8900001],
                      [1.65499997, 3.84500003],
                      [1.34000003, 3.64499998],
                      [1.29499996, 3.83500004],
                      [1.20000005, 4.]])]
    },
    'pmean':
    {
        'dgms': [
            np.array([[0.44, 1.00999999],
                      [0.36000001, 1.125],
                      [0.33000001, 1.14499998],
                      [0.88999999, 1.17999995],
                      [0.11,       np.inf]]),
            np.array([[1.76999998, 2.54917502],
                      [1.755, 2.52713633],
                      [1.65499997, 2.41156578],
                      [1.34000003, 2.04345369],
                      [1.29499996, 2.07881474],
                      [1.20000005, 2.43602848]])]
    },
    'pmoment':
    {
        'dgms': [
            np.array([[0.44, 1.00999999],
                      [0.36000001, 1.125],
                      [0.33000001, 1.14499998],
                      [0.88999999, 1.17999995],
                      [0.11,       np.inf]]),
            np.array([[1.76999998, 1.9275918],
                      [1.755, 1.85709834],
                      [1.65499997, 1.7869581],
                      [1.34000003, 1.37369251],
                      [1.29499996, 1.39265192],
                      [1.20000005, 1.81259179]])]
    },
    'remove_edges':
    {
        'dgms': [
            np.array([[0.44, 1.00999999],
                      [0.36000001, 1.125],
                      [0.33000001, 1.14499998],
                      [0.88999999, 1.17999995],
                      [0.11,       np.inf]]),
            np.array([[1.29499996, 1.34000003],
                      [1.20000005, 1.65499997]])]
    },
    'vertex_degree':
    {
        'dgms': [
            np.array([[-4, np.inf]]),
            np.array([])]
    },
}


def are_matrices_equal(m1, m2):
    for i in range(min(len(m1), len(m2))):
        m1f = np.array(m1[i]).flatten()
        m2f = np.array(m2[i]).flatten()
        if not np.isclose(m1f, m2f).all():
            return False
    return True


def test_output(flag_file):
    adjacency_matrix = load_unweighted_flag(flag_file, fmt='coo')
    res = flagser_unweighted(adjacency_matrix)
    betti_exp = betti[os.path.split(flag_file)[1]]
    betti_res = res["betti"]
    assert_almost_equal(betti_res, betti_exp)

    cell_count_exp = cell_count[os.path.split(flag_file)[1]]
    cell_count_res = res["cell_count"]
    assert_almost_equal(cell_count_res, cell_count_exp)


def test_filtrations_d5(flag_file, filtration):
    """Test all filtrations available for dataset d5.flag, see conftest.py"""
    adjacency_matrix = load_weighted_flag(flag_file, fmt='coo')
    res = flagser_weighted(adjacency_matrix, max_dimension=1,
                           directed=False, filtration=filtration)
    for filt, tests in filtrations_results.items():
        if filtration == filt:
            tmp = res["dgms"]
            tmp2 = tests["dgms"]
            assert are_matrices_equal(tmp, tmp2), \
                "Diagrams {} \n and {} \n are not equal"\
                .format(tmp, tmp2)


def test_concurrent(flag_file_small):
    nb_workers = 3
    adjacency_matrix = load_weighted_flag(flag_file_small, fmt='coo')
    data_list = nb_workers * [adjacency_matrix]

    pool = Pool(processes=len(data_list))
    pool.map(flagser_unweighted, data_list)

    # close and join are needed by pytest-cov
    pool.close()
    pool.join()


@pytest.mark.timeout(30)
def test_higher_coefficients():
    """Regression test for issue #45"""
    x = np.random.random((5, 5))
    np.fill_diagonal(x, 0.)
    flagser_weighted(x, coeff=3)


def test_huge_graphs():
    """Regression test for issue #65"""
    from scipy.sparse import coo_matrix
    x = coo_matrix(([1], ([0], [1])), shape=(2**16, 2**16))
    flagser_unweighted(x)
