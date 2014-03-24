import cPickle
import time
import sys
import numpy as np
import matplotlib.pyplot as plt
from codim1.core.dof_handler import ContinuousDOFHandler
from codim1.core.mesh import Mesh
from codim1.core.matrix_assembler import MatrixAssembler
from codim1.core.rhs_assembler import RHSAssembler
from codim1.core.basis_funcs import BasisFunctions, Solution
from codim1.fast.elastic_kernel import AdjointTractionKernel,\
                                       RegularizedHypersingularKernel,\
                                       DisplacementKernel,\
                                       TractionKernel
from codim1.core.quad_strategy import QuadStrategy
from codim1.core.quadrature import QuadGauss
from codim1.core.mass_matrix import MassMatrix
from codim1.core.interior_point import InteriorPoint
import codim1.core.tools as tools

from matplotlib import rcParams
rcParams['axes.labelsize'] = 9
rcParams['xtick.labelsize'] = 9
rcParams['ytick.labelsize'] = 9
rcParams['legend.fontsize'] = 9
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Computer Modern Roman']
# rcParams['text.usetex'] = True


# Elastic parameter
shear_modulus = 1.0
poisson_ratio = 0.25

# Quadrature points for the various circumstances
quad_min = 4
quad_max = 12
quad_logr = 12
quad_oneoverr = 12
# I did some experiments and
# 13 Quadrature points seems like it gives error like 1e-10, lower
# than necessary, but nice for testing other components
interior_quad_pts = 13
# How many interior points to use.
x_pts = 40
y_pts = 40

n_elements = 80

def exact_edge_dislocation(X, Y):
    # The analytic solution for the
    # displacement fields due to an edge dislocation.
    nu = 0.25
    factor = (1.0 / (2 * np.pi))
    R = np.sqrt(X ** 2 + Y ** 2)
    ux = factor * (np.arctan(X / Y) + \
                   (1.0 / (2 * (1 - nu))) * (X * Y / (R ** 2)))
    uy = factor * ((((1 - 2 * nu) / (2 * (1 - nu))) * np.log(1.0 / R)) + \
                   (1.0 / (2 * (1 - nu))) * ((X ** 2) / (R ** 2)))
    return ux, uy

def plot_edge_dislocation():
    # Plot the solution for an edge dislocation with burgers
    x_pts = 50
    y_pts = 50
    x = np.linspace(-5, 5, x_pts)
    # Doesn't sample 0.0!
    y = np.linspace(-5, 5, y_pts)
    X, Y = np.meshgrid(x, y)
    ux, uy = exact_edge_dislocation(X + 1, Y)
    ux2, uy2 = exact_edge_dislocation(X - 1, Y)
    ux = ux2 - ux
    uy = uy2 - uy
    plt.figure(1)
    plt.imshow(ux)
    plt.colorbar()
    plt.figure(2)
    plt.imshow(uy)
    plt.colorbar()
    return ux, uy

def reload_and_postprocess():
    f = open('data/dislocation2/int_u.pkl', 'rb')
    int_u = cPickle.load(f)
    x = np.linspace(-5, 5, x_pts)
    # Doesn't sample 0.0!
    y = np.linspace(-5, 5, y_pts)
    X, Y = np.meshgrid(x, y)

    # Quiver plot
    quiver_plot = plt.quiver(X[::2, ::2], Y[::2, ::2],
                            int_u[0, ::2, ::2], int_u[1, ::2, ::2])
    plt.quiverkey(quiver_plot, 0.60, 0.95, 0.25, r'0.25', labelpos='W')
    plt.plot([-1, 1], [0, 0], 'r-', linewidth=4)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.xlim([-5, 5])
    plt.title(r'Displacement vectors for an edge dislocation ' +
              'from $x = 1$ to $x = -1$.')

    # Streamline plot
    plt.figure()
    quiver_plot = plt.streamplot(X, Y, int_u[0, :, :], int_u[1, :, :])
    plt.plot([-1, 1], [0, 0], 'r-', linewidth=4)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(r'Displacement streamlines for an edge dislocation ' +
              'from $x = 1$ to $x = -1$.')
    plt.show()
    sys.exit()
reload_and_postprocess()

ux_exact, uy_exact = plot_edge_dislocation()

start = time.time()

# The four kernels of linear elasticity!
# http://en.wikipedia.org/wiki/The_Three_Christs_of_Ypsilanti
k_d = DisplacementKernel(shear_modulus, poisson_ratio)
k_t = TractionKernel(shear_modulus, poisson_ratio)
k_tp = AdjointTractionKernel(shear_modulus, poisson_ratio)
k_h = RegularizedHypersingularKernel(shear_modulus, poisson_ratio)

mesh = Mesh.simple_line_mesh(n_elements)
bf = BasisFunctions.from_degree(1)
qs = QuadStrategy(mesh, quad_min, quad_max, quad_logr, quad_oneoverr)
qs_rhs = qs
dh = ContinuousDOFHandler(mesh, 1)

print('Assembling kernel matrix, Guu')
# TODO: Take the symmetry of Guu, Gpp into account in its assembly.
# Cut it in half!
matrix_assembler = MatrixAssembler(mesh, bf, dh, qs)
Guu = matrix_assembler.assemble_matrix(k_d)

# The prescribed displacement is 1.0 in the positive x direction.
fnc = lambda x, n: np.array([1.0, 0.0])
displacement_func = BasisFunctions.from_function(lambda x: fnc(x, 0))

print("Assembling RHS")
# The RHS kernel term.
rhs_assembler = RHSAssembler(mesh, bf, dh, qs_rhs)
rhs = rhs_assembler.assemble_rhs(displacement_func, k_t)

# Add the mass matrix term to the rhs. Arises from the cauchy singularity of
# the traction kernel.
mass_matrix = MassMatrix(mesh, bf, displacement_func, dh, QuadGauss(2),
                         compute_on_init = True)
rhs -= 0.5 * np.sum(mass_matrix.M, axis = 1)

# Solve Ax = b, where x are the coefficients over the solution basis
soln_coeffs = np.linalg.solve(Guu, rhs)

# Create a solution object that pairs the coefficients with the basis
soln = Solution(bf, dh, soln_coeffs)

print("Performing Interior Computation")
# TODO: Extract this interior point computation to some tool function.
x = np.linspace(-5, 5, x_pts)
# Doesn't sample 0.0!
y = np.linspace(-5, 5, y_pts)
int_ux = np.zeros((x_pts, y_pts))
int_uy = np.zeros((x_pts, y_pts))
ip = InteriorPoint(mesh, dh, qs)
for i in range(x_pts):
    for j in range(y_pts):
        print i, j
        traction_effect = ip.compute((x[i], y[j]), np.array((0.0, 0.0)),
                                     k_d, soln)
        displacement_effect = -ip.compute((x[i], y[j]), np.array([0.0, 0.0]),
                                          k_t, displacement_func)
        int_ux[j, i] = traction_effect[0] + displacement_effect[0]
        int_uy[j, i] = traction_effect[1] + displacement_effect[1]

#TODO: HACK to get the correct displacements for the dislocation
# doing the correct thing probably involves accounting for the displacements
# on both sides of the surface.
int_ux -= np.flipud(int_ux)
int_ux /= 2.0
int_uy += np.flipud(int_uy)
int_uy /= 2.0
int_u = np.array([int_ux, int_uy])
with open('int_u.pkl', 'wb') as f:
    cPickle.dump(int_u, f)

end = time.time()
print("Took: " + str(end - start) + " seconds")

plt.figure(3)
plt.title(r'$u_x$')
plt.imshow(int_ux)
plt.colorbar()
plt.figure(4)
plt.title(r'$u_y$')
plt.imshow(int_uy)
plt.colorbar()
plt.show()
import ipdb;ipdb.set_trace()
