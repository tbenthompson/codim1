import numpy as np
import matplotlib.pyplot as plt
from codim1.core import *
from codim1.assembly import *
from codim1.fast_lib import *
import codim1.core.tools as tools
import matplotlib as mpl
mpl.rcParams['lines.linewidth'] = 2

shear_modulus = 1.0
poisson_ratio = 0.25
n_elements_surface = 200
degree = 4
quad_min = degree + 1
quad_mult = 3
quad_max = quad_mult * degree
quad_logr = quad_mult * degree + (degree % 2)
quad_oneoverr = quad_mult * degree + (degree % 2)
interior_quad_pts = 13

ek = ElasticKernelSet(shear_modulus, poisson_ratio)

di = 0.5
df = 1.5
x_di = 0.0
x_df = 1.0
# fault angle
delta = np.arctan((df - di) / (x_df - x_di))
left_end = np.array((x_di, -di))
right_end = np.array((x_df, -df))
fault_vector = left_end - right_end
fault_tangential = fault_vector / np.linalg.norm(fault_vector)
fault_normal = np.array((fault_tangential[1], -fault_tangential[0]))

main_surface_left = (-10.0, 0.0)
main_surface_right = (10.0, 0.0)
mesh1 = simple_line_mesh(n_elements_surface,
                        main_surface_left,
                        main_surface_right)

per_step = 5
steps = 10
ray_lengths = [1.0] * per_step
for i in range(1, steps):
    ray_lengths.extend([2.0 ** float(i)] * per_step)

ray_left_dir = (-1.0, 0.0)
mesh2 = ray_mesh(main_surface_left, ray_left_dir, ray_lengths, flip = True)
ray_right_dir = (1.0, 0.0)
mesh3 = ray_mesh(main_surface_right, ray_right_dir, ray_lengths)
mesh = combine_meshes(mesh2, combine_meshes(mesh1, mesh3),
                      ensure_continuity = True)

bf = basis_from_degree(degree)
qs = QuadStrategy(mesh, quad_min, quad_max, quad_logr, quad_oneoverr)
apply_to_elements(mesh, "basis", bf, non_gen = True)
apply_to_elements(mesh, "continuous", True, non_gen = True)
init_dofs(mesh)

str_loc_norm = [(-fault_tangential, left_end, fault_normal),
               (fault_tangential, right_end, fault_normal)]
rhs = -point_source_rhs(mesh, qs, str_loc_norm, ek.k_rh)

matrix = simple_matrix_assemble(mesh, qs, ek.k_rh)

# The matrix produced by the hypersingular kernel is singular, so I need
# to provide some further constraint in order to remove rigid body motions.
# I impose a constraint that forces the average displacement to be zero.
apply_average_constraint(matrix, rhs, mesh)

soln_coeffs = np.linalg.solve(matrix, rhs)
x, u_soln = tools.evaluate_boundary_solution(4, soln_coeffs, mesh)


def analytical_free_surface(x, x_d, d, delta, s):
    """
    Analytical solution for the surface displacements from an infinite
    buried edge dislocation. Add two of them with opposite slip to represent
    an infinitely long thrust/normal fault.
    Extracted from chapter 3 of Segall 2010.
    """
    xsi = (x - x_d) / d
    factor = s / np.pi
    term1 = np.cos(delta) * np.arctan(xsi)
    term2 = (np.sin(delta) - xsi * np.cos(delta)) / (1 + xsi ** 2)
    ux = factor * (term1 + term2)
    term1 = np.sin(delta) * np.arctan(xsi)
    term2 = (np.cos(delta) + xsi * np.sin(delta)) / (1 + xsi ** 2)
    uy = -factor * (term1 + term2)
    return ux, uy

# Compute the exact solution
x_e = x[:, 0]
ux_exact1, uy_exact1 = analytical_free_surface(x_e, x_di, di, delta, -1.0)
ux_exact2, uy_exact2 = analytical_free_surface(x_e, x_df, df, delta, 1.0)
ux_exact = ux_exact1 + ux_exact2
uy_exact = uy_exact1 + uy_exact2

def comparison_plot():
    plt.plot(x_e, ux_exact, '*', label = 'Exact X Displacement')
    plt.plot(x_e, uy_exact, '*', label = 'Exact Y Displacement')
    plt.plot(x[:, 0],
             u_soln[:, 0], '8',
             linewidth = 2, label = 'Estimated X displacement')
    plt.plot(x[:, 0],
             u_soln[:, 1], '8',
             linewidth = 2, label = 'Estimated Y displacement')
    plt.axis([-30, 30, -1, 1])
    plt.xlabel(r'$x/d$', fontsize = 18)
    plt.ylabel(r'$u/s$', fontsize = 18)
    plt.legend()
    plt.show()

def error_plot():
    x_error = np.abs(ux_exact - u_soln[:, 0]) / np.abs(ux_exact)
    y_error = np.abs(uy_exact - u_soln[:, 1]) / np.abs(uy_exact)
    plt.figure(1)
    plt.xlim(-30, 30)
    plt.ylim(0, 0.0001)
    plt.plot(x_e, x_error, '*', label = '% X displacement Error')
    plt.plot(x_e, y_error, '*', label = '% Y displacement Error')
    plt.xlabel(r'$x/d$', fontsize = 18)
    plt.ylabel(r'$100\left(\frac{|u_{exact} - u_{est}|}{s}\right)$', fontsize = 18)
    plt.legend()
    plt.show()
error_plot()

import ipdb;ipdb.set_trace()
