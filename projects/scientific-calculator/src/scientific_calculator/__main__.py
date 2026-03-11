"""Entry point for running scientific_calculator as a module.

This file enables running the calculator with:
    $ python -m scientific_calculator

It simply imports and calls the main function from cli.py.
"""

import sys
from scientific_calculator.cli import main

if __name__ == "__main__":
    sys.exit(main())
