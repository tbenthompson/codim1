import numpy as np
from codim1.fast_lib import single_integral, ConstantBasis, InteriorPoint
from codim1.core.quad_strategy import single_integral_wrapper

def interior_pt(mesh, pt_normal, kernel,
        basis_grabber = lambda e: e.soln,
        integrator = InteriorPoint,
        bounce = False, bounce_threshold = 0.05):
    """
    Calculate the influence at an interior point from a boundary condition
    """
    # if bounce:
    kernel.set_interior_data(pt_normal[0], pt_normal[1])
    i = integrator()
    for e_k in mesh:
        map = e_k.mapping.eval
        basis = basis_grabber(e_k)
        quad_info = e_k.qs.get_interior_quadrature(e_k, pt_normal[0])
        i.process_element(map, kernel, basis, quad_info);
    return np.array(i.result)
