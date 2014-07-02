#include <cstdlib>
#include <cmath>

/* Two macros for debugging found on http://latedev.wordpress.com/2012/08/09/c-debug-macros/
 * Added the do {} while(0) construct for safety.
 */

#define DBGVAR( outstream, var) \
  do {(outstream) << "DBG: " << __FILE__ << "(" << __LINE__ << ") "\
       << #var << " = [" << (var) << "]" << std::endl;} while(0)

#define DBGMSG( outstream, msg) \
  do {(outstream) << "DBG: " << __FILE__ << "(" << __LINE__ << ") " \
       << msg << std::endl;} while(0)

/* A macro for testing comparisons of floating point values. */
#define REQUIREAE(a, b, eps) \
    do {\
        DBGMSG(std::cout, "Assert: " << a << "  almost equal to: " << b <<\
                  "  with precision: " << eps);\
        DBGMSG(std::cout, "Difference is: " << (a - b));\
        REQUIRE(std::fabs(a - b) < eps);\
    } while(0)

#define REQUIREAEVECTOR(a, b, eps) \
    do {\
        REQUIRE(a.size() == b.size());\
        for (unsigned int i = 0; i < a.size(); i++) {\
            REQUIREAE(a[i], b[i], eps);\
        }\
    } while (0)
