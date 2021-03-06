import numpy as np
import scipy.interpolate as spi
import scipy.special
from codim1.fast_lib import PolyBasis, CoeffBasis
from quadracheer import gaussxw, lobatto_quad, map_pts_wts
from codim1.core.tools import local_interpolate

def get_equispaced_nodes(element_deg):
    """
    A small wrapper around linspace to make sure the right thing
    happens when element_deg = 0
    """
    if element_deg == 0:
        nodes = np.array([0.5])
    else:
        nodes = np.linspace(0.0, 1.0, element_deg + 1)
    return nodes

def basis_from_degree(element_deg):
    """
    Create an equispaced nodal basis.
    """
    nodes = get_equispaced_nodes(element_deg)
    return basis_from_nodes(nodes)

def basis_from_nodes(nodes):
    """
    Create a interpolated polynomial basis from arbitrary nodes.
    """
    n_fncs = len(nodes)
    fncs = np.empty((n_fncs, n_fncs))
    derivs = np.empty((n_fncs, n_fncs))
    for (i, n) in enumerate(nodes):
        w = np.zeros_like(nodes)
        w[i] = 1.0
        # scipy.interpolate.lagrange has trouble above 20 nodes, but that
        # shouldn't be an issue for this code
        poly = spi.lagrange(nodes, w)
        fncs[i, :] = poly.c
        derivs[i, 0] = 0.0
        derivs[i, 1:] = poly.deriv().c
    point_sources = []
    point_sources.append([0.0, 1.0, 1.0])
    point_sources.append([1.0, 1.0, 1.0])
    point_source_dependency = [0, n_fncs - 1]
    return PolyBasis(fncs, derivs, point_sources,
                     point_source_dependency, nodes)

def gll_basis(degree):
    """ A basis from the Gauss-Lobatto-Lagrange nodes """
    x, w = lobatto_quad(degree + 1)
    nodes, w = map_pts_wts(x, w, 0, 1)
    return basis_from_nodes(nodes)

def apply_coeffs(elements, solution_coeffs, name):
    """
    Applies a solution basis to each element. This assumes that a standard
    basis is already defined on the element.
    """
    for e in elements:
        values = solution_coeffs[e.dofs]
        e.__dict__[name] = CoeffBasis(e.basis, values)

def basis_from_func(under_basis, f, element):
    coeffs = local_interpolate(f, element.mapping, under_basis)
    return CoeffBasis(under_basis, coeffs)
