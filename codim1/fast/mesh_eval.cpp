#include "mesh_eval.h"

MeshEval::MeshEval(std::vector<std::vector<double> > mesh_basis,
            std::vector<std::vector<double> > mesh_derivs,
            std::vector<std::vector<std::vector<double> > > mesh_coeffs):
    empty_vec(2),
    basis_eval(mesh_basis),
    deriv_eval(mesh_derivs)
{
    this->coeffs = mesh_coeffs; 
}

std::vector<double>
    MeshEval::eval_function(BasisEval& evaluator, 
            int element_idx, double x_hat)
{
    std::vector<double> val(2);
    double basis;
    for(int i = 0; i < basis_eval.order; i++)
    {
        // This is assuming that the basis is the same for both dimensions
        // in the mesh. This is a reasonable assumption.
        basis = evaluator.evaluate(element_idx, i, x_hat, empty_vec, 0);
        val[0] += coeffs[0][element_idx][i] * basis;
        val[1] += coeffs[1][element_idx][i] * basis;
    }
    return val;
}

std::vector<double>
    MeshEval::get_physical_point(int element_idx, double x_hat)
{
    return eval_function(basis_eval, element_idx, x_hat);
}

double MeshEval::get_jacobian(int element_idx, double x_hat)
{
    std::vector<double> deriv =
        eval_function(deriv_eval, element_idx, x_hat);
    return sqrt(pow(deriv[0], 2)  + pow(deriv[1], 2));
}

std::vector<double> MeshEval::get_normal(int element_idx, double x_hat)
{
    std::vector<double> deriv =
        eval_function(deriv_eval, element_idx, x_hat);
    double length = sqrt(pow(deriv[0], 2)  + pow(deriv[1], 2));
    std::vector<double> retval(2);
    retval[0] = -deriv[1] / length;
    retval[1] = deriv[0] / length;
    return retval;
}