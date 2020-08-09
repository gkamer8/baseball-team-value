from distutils.core import setup
from Cython.Build import cythonize

import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

setup(ext_modules=cythonize(['team.pyx', 'league.pyx', 'player.pyx', 'prospect.pyx']), annotate=True)

# Compile using:
# python3 setup.py build_ext --inplace