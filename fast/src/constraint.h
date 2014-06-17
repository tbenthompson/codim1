#ifndef __codim1_constraint_h
#define __codim1_constraint_h

#include <utility>
#include <vector>

/* A list of matrix constraints is generated from the mesh
 * connectivity and boundary conditions. These constraints
 * are represented by an integer referring to the relevant
 * degree of freedom and a float that multiplies that 
 * dofs value in the linear system. A rhs value is represented
 * by a dof id of -1. 
 * So, for example:
 * 4x + 3y = 2 ====> 4x + 3y - 2 = 0
 * would be a constraint list consisting of the tuples
 * [(x_dof, 4), (y_dof, 3), (RHS, -2)]
 *
 * Constraints are used to ensure continuity between
 * elements and to enforce displacement discontinuities between elements
 * that connect to another element with a displacement discontinuity 
 * boundary condition or solution type.
 *
 * Continuity constraints for a Lagrange interpolating basis that has a
 * node at the boundary will simply be of the form [(e1_dof, 1), (e2_dof, -1)]
 * because the two boundary dofs are set equal.
 *
 * TODO: CHANGE TO USE BOOST_STRONG_TYPEDEF?
 */ 
namespace codim1
{
    extern const int RHS = -1;

    typedef std::pair<int, float> DOFWeight;
    typedef std::vector<DOFWeight> Constraint;
    typedef std::vector<Constraint> ConstraintList;

    Constraint continuity_constraint(int dof1, int dof2) {
        return {
            DOFWeight(dof1, 1.0),
            DOFWeight(dof2, -1.0)
        };
    }

    /* This creates a constraint representing the offset between the value
     * of two DOFs. Primarily useful for imposing a fault slip as the 
     * displacement jump when a fault intersects the surface.
     * The direction of offset is from dof1 to dof2. So,
     * value[dof1] + offset = value[dof2]
     */
    Constraint offset_constraint(int dof1, int dof2, float offset) {
        Constraint c = continuity_constraint(dof1, dof2);
        c.push_back(DOFWeight(RHS, offset));
        return c;
    }
}

#endif