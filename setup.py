import setuptools
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy as np

# Cython packaging. This will be phased out in favor of a straight c++
# extension.
fast_package = 'codim1.fast'
ext = [
        Extension(fast_package + ".elastic_kernel",
            sources=["codim1/fast/elastic_kernel.pyx"]),
        Extension(fast_package + ".mesh",
            sources=["codim1/fast/mesh.pyx"]),
        Extension(fast_package + ".integration",
            sources=["codim1/fast/integration.pyx"]),
        Extension(fast_package + ".basis_funcs",
            sources=["codim1/fast/basis_funcs.pyx"])
      ]
ext = cythonize(ext)

ext.append(Extension(fast_package + '.fast_package',
                  ['codim1/fast/python_interface.cpp'],
                  include_dirs=['codim1/fast'],
                  library_dirs=['/'],
                  libraries=['boost_python'],
                  extra_compile_args=['-g']))

setuptools.setup(
   name = "codim1",
   version = '0.0.0',
   author = 'Ben Thompson',
   packages = ['codim1'],
   include_dirs = [np.get_include()],
   ext_modules=ext
)
