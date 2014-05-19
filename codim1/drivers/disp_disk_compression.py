import numpy as np
import matplotlib.pyplot as plt

import codim1.core.tools as tools
from codim1.core import *
from codim1.assembly import *
from codim1.fast_lib import *


def test_elastic_scaling():
    shear_modulus = 1.0
    poisson_ratio = 0.25
    n_elements = 30
    degree = 1
    quad_min = 4
    quad_max = 10
    quad_logr = 10
    quad_oneoverr = 10


    bf = BasisFunctions.from_degree(degree)
    mesh = circular_mesh(n_elements, 1.0)
    qs = QuadStrategy(mesh, quad_max, quad_max, quad_logr, quad_oneoverr)
    apply_to_elements(mesh, "basis", bf, non_gen = True)
    apply_to_elements(mesh, "continuous", True, non_gen = True)
    init_dofs(mesh)

    def run(shear_mod, pr):
        ek = ElasticKernelSet(shear_mod, pr)

        matrix = simple_matrix_assemble(mesh, qs, ek.k_d)

        # Uniform compression displacement
        def compress(x, d):
            x_length = np.sqrt(x[0] ** 2 + x[1] ** 2)
            return 0.2 * x[d] / x_length

        displacement_function = BasisFunctions.from_function(compress)

        # Assemble the rhs, composed of the displacements induced by the
        # traction inputs.
        print("Assembling RHS")
        rhs = simple_rhs_assemble(mesh, qs, displacement_function, ek.k_t)

        q = QuadGauss(degree + 1)
        rhs += mass_matrix_for_rhs(assemble_mass_matrix(mesh, q))

        soln_coeffs = np.linalg.solve(matrix, rhs)

        # Evaluate that solution at 400 points around the circle
        x, t = tools.evaluate_boundary_solution(400 / n_elements, soln_coeffs, mesh)

        # plt.figure(2)
        # plt.plot(x[:, 0], t[:, 0])
        # plt.xlabel(r'X')
        # plt.ylabel(r'$t_x$', fontsize = 18)

        # plt.figure(3)
        # plt.plot(x[:, 0], t[:, 1])
        # plt.xlabel(r'X')
        # plt.ylabel(r'$t_y$', fontsize = 18)
        # plt.show()
        return t

    t1 = run(shear_modulus, poisson_ratio)
    t2 = run(shear_modulus * 5, poisson_ratio)
    # Should be equal to machine precision. The discrete problem exactly
    # preserves this property of the continuous problem.
    np.testing.assert_almost_equal(t1 * 5, t2, 14)
    print np.sum(t1 * 5 - t2) / t1.size

if __name__ == "__main__":
    test_elastic_scaling()
