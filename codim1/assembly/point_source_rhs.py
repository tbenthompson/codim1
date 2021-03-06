import numpy as np
from codim1.fast_lib import single_integral, ConstantBasis

def point_source_rhs(mesh, str_loc_norm, kernel):
    """
    Creates RHS terms that consist of a point source. Depending on the
    kernel chosen, these point sources could be:
    1. point forces
    2. point displacements
    3. point displacement discontinuity gradients
    """
    total_dofs = mesh.total_dofs
    rhs = np.zeros(total_dofs)
    basis_grabber = lambda e: e.basis
    if kernel.test_gradient:
        basis_grabber = lambda e: e.basis.get_gradient_basis()
    for (str, loc, normal) in str_loc_norm:
        strength = ConstantBasis(np.array(str))
        kernel.set_interior_data(np.array(loc), np.array(normal))
        for e_k in mesh:
            quad_info = e_k.qs.get_point_source_quadrature(
                    kernel.singularity_type, loc, e_k)
            for i in range(e_k.basis.n_fncs):
                integral = single_integral(e_k.mapping.eval,
                                       kernel,
                                       basis_grabber(e_k),
                                       strength,
                                       quad_info,
                                       i, 0)
                for idx1 in range(2):
                    for idx2 in range(2):
                        rhs[e_k.dofs[idx1, i]] += integral[idx1][idx2]
    return rhs
