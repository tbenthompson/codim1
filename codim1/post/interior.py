from codim1.fast_lib import InteriorPoint, ConstantBasis, ZeroBasis
from codim1.assembly.shared import _choose_basis
from codim1.assembly.which_kernels import _make_which_kernels
import numpy as np

one = ConstantBasis([1.0, 1.0])
def interior(mesh, pt, normal, kernel_set, soln_basis, interior_type,
                   integrator = InteriorPoint, quad_strategy = None):
    i = integrator()
    which_kernels = _make_which_kernels(kernel_set)
    for e_l in mesh:
        # Handle the boundary condition first
        _interior_element(i, pt, normal, interior_type,
                          e_l, which_kernels, soln_basis, "bc", quad_strategy)
        _interior_element(i, pt, normal, interior_type,
                          e_l, which_kernels, soln_basis, "soln", quad_strategy)
    return np.array(i.result)

def interior_on_element(mesh, e, x_hat, normal,
                        kernel_set, soln_basis, interior_type,
                        integrator = InteriorPoint, quad_strategy = None):
    i = integrator()
    which_kernels = _make_which_kernels(kernel_set)
    pt = e.mapping.get_physical_point(x_hat)
    for e_l in mesh:
        if e is e_l:# in e_l.neighbors_left or e in e_l.neighbors_right:
            continue
        # Handle the boundary condition first
        _interior_element(i, pt, normal, interior_type,
                          e_l, which_kernels, soln_basis, "bc", quad_strategy)
        _interior_element(i, pt, normal, interior_type,
                          e_l, which_kernels, soln_basis, "soln", quad_strategy)

    # Process self and adjacent elements.
    # _interior_element(i, pt, normal, interior_type,
    #                   e, which_kernels, soln_basis, "bc", quad_strategy,
    #                   on_boundary = True, x_hat = x_hat)
    # _interior_element(i, pt, normal, interior_type,
    #                   e, which_kernels, soln_basis, "soln", quad_strategy,
    #                   on_boundary = True, x_hat = x_hat)
    res = np.array(i.result)
    print res
    return res

def _interior_element(integrator, pt, normal, interior_type,
                      e_l, which_kernels, soln_basis, bc_or_soln,
                      quad_strategy, on_boundary = False, x_hat = None):
    if bc_or_soln == "bc":
        init_e_l_basis = e_l.bc.basis
        e_l_type = e_l.bc.type
    else:
        init_e_l_basis = e_l.__dict__[soln_basis]
        e_l_type = which_kernels[e_l.bc.type]["opposite"]

    if type(init_e_l_basis) is ZeroBasis:
        return

    kernel, factor = which_kernels[interior_type][e_l_type]["interior"]
    if kernel is None:
        return
    assert(kernel.test_gradient == False)

    kernel.set_interior_data(pt, normal)

    e_l_basis, e_l_pt_srcs = _choose_basis(init_e_l_basis, kernel.soln_gradient)

    # Handle the integration of point sources
    for i, e_l_pt in enumerate(e_l_pt_srcs[0]):
        strength = [e_l_pt[1], e_l_pt[2]]
        ref_pt = e_l_pt[0]
        integrator.process_point_source(e_l.mapping.eval,
                                        kernel, ref_pt, strength, factor)

    if type(e_l_basis) is ZeroBasis:
        return

    # Handle the integration of basis functions
    if quad_strategy is None:
        quad_strategy = e_l.qs
    if on_boundary is False:
        quad_info = quad_strategy.get_point_source_quadrature(
                        kernel.singularity_type, pt, e_l)
    else:
        quad_info = quad_strategy.get_point_source_quadrature(
                        kernel.singularity_type, pt, e_l,
                        in_element = True, reference_loc = x_hat)
        print x_hat, np.array(quad_info.x)

    integrator.process_element(e_l.mapping.eval,
                                 kernel,
                                 e_l_basis,
                                 quad_info,
                                 factor)
