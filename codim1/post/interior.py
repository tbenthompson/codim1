from codim1.fast_lib import InteriorPoint, ConstantBasis, ZeroBasis
from codim1.assembly.shared import _choose_basis
from codim1.assembly.which_kernels import _make_which_kernels
import numpy as np

one = ConstantBasis([1.0, 1.0])
def sgbem_interior(mesh, pt, normal, kernel_set, soln_basis, int_type):
    i = InteriorPoint()
    which_kernels = _make_which_kernels(kernel_set)
    for e_l in mesh:
        # Handle the boundary condition first
        _interior_element(i, pt, normal, int_type,
                          e_l, which_kernels, soln_basis, "bc")
        _interior_element(i, pt, normal, int_type,
                          e_l, which_kernels, soln_basis, "soln")
    return np.array(i.result)

def _interior_element(integrator, pt, normal, int_type,
                      e_l, which_kernels, soln_basis, bc_or_soln):
    if bc_or_soln == "bc":
        init_e_l_basis = e_l.bc.basis
        e_l_type = e_l.bc.type
    else:
        init_e_l_basis = e_l.__dict__[soln_basis]
        e_l_type = which_kernels[e_l.bc.type]["opposite"]

    if type(init_e_l_basis) is ZeroBasis:
        return

    kernel, factor = which_kernels[int_type][e_l_type]["interior"]
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
    quad_info = e_l.qs.get_point_source_quadrature(
                    kernel.singularity_type, pt, e_l)
    integrator.process_element(e_l.mapping.eval,
                                 kernel,
                                 e_l_basis,
                                 quad_info,
                                 factor)
