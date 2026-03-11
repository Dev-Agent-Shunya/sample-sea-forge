"""Scientific Calculator - A Python CLI calculator with expression parsing.

This package provides a command-line interface calculator with support for
basic arithmetic, scientific functions, expression parsing with PEMDAS,
and memory/history management.

Example:
    Run the calculator from command line:
        $ python -m scientific_calculator

    Or import and use programmatically:
        >>> from scientific_calculator.cli import CalculatorCLI
        >>> calc = CalculatorCLI()
        >>> calc.run()

Attributes:
    __version__: The version string of the package.
    __author__: Package author information.

"""

from scientific_calculator.errors import CalculatorError, InputError, ValidationError

__version__ = "1.0.0"
__author__ = "SeaForge Development Team"
__license__ = "MIT"

__all__ = [
    "__version__",
    "__author__",
    "CalculatorError",
    "InputError",
    "ValidationError",
]
