"""Code to run if this package is used as a Python module."""

# Standard Python Libraries
import sys

from .assessment_data_import import main

return_code = main()

if return_code:
    sys.exit(return_code)
