"""Utility functions for scientific calculator.

This module provides helper functions for the CLI interface,
including screen clearing, help text formatting, and input validation.
"""

import os
import platform
import re
from typing import List, Tuple


# Version constant
VERSION = "1.0.0"


def clear_screen() -> None:
    """Clear the terminal screen in a cross-platform manner.

    This function detects the operating system and uses the appropriate
    command to clear the terminal screen.

    Supported platforms:
        - Windows (nt): Uses 'cls' command
        - Unix/Linux/macOS: Uses 'clear' command

    Returns:
        None

    Example:
        >>> clear_screen()  # Clears the terminal
    """
    if platform.system().lower() == 'windows':
        os.system('cls')
    else:
        os.system('clear')


def format_help_text() -> str:
    """Generate formatted help text for the calculator.

    Returns a comprehensive help string containing usage instructions,
    available commands, and examples.

    Returns:
        A formatted multi-line help string.

    Example:
        >>> help_text = format_help_text()
        >>> print(help_text)
        SeaForge Scientific Calculator v1.0.0
        ...
    """
    help_lines = [
        f"SeaForge Scientific Calculator v{VERSION}",
        "=" * 50,
        "",
        "USAGE:",
        "  Enter mathematical expressions or use commands.",
        "",
        "AVAILABLE COMMANDS:",
        "  help          Show this help message",
        "  clear, cls    Clear the screen",
        "  exit, quit    Exit the calculator",
        "",
        "EXPRESSION SYNTAX:",
        "  Basic:        2 + 2, 10 * 5, 15 / 3",
        "  Grouping:     (2 + 3) * 4",
        "  Scientific:   sin(), cos(), tan(), log(), ln()",
        "  Power:        pow(x, y) or x^y",
        "  Root:         sqrt(x)",
        "  Constants:    pi, e",
        "",
        "MEMORY COMMANDS:",
        "  MC            Memory clear",
        "  MR            Memory recall",
        "  M+ <val>      Add to memory",
        "  M- <val>      Subtract from memory",
        "",
        "KEYBOARD SHORTCUTS:",
        "  Ctrl+C        Exit gracefully",
        "  Ctrl+D        Exit (EOF)",
        "",
        "EXAMPLES:",
        "  > 5 * (3 + 2)",
        "  > sin(pi / 2)",
        "  > sqrt(16) + 10",
        "  > M+",
        "  > MR * 2",
        "",
        "=" * 50,
    ]
    return "\n".join(help_lines)


def format_welcome_message() -> str:
    """Generate the calculator welcome message.

    Returns:
        A formatted welcome banner string.
    """
    return f"""\nSeaForge Scientific Calculator v{VERSION}
Type 'help' for commands, 'exit' to quit
"""


def validate_input(user_input: str) -> Tuple[bool, str]:
    """Validate user input for safety and correctness.

    This function checks if the input is safe to process by:
    - Checking for disallowed characters
    - Validating against dangerous patterns
    - Ensuring input is not empty after sanitization

    Args:
        user_input: The raw input string from the user.

    Returns:
        A tuple of (is_valid, error_message).
        - is_valid: Boolean indicating if input passed validation
        - error_message: Empty string if valid, otherwise contains error description

    Example:
        >>> valid, msg = validate_input("2 + 2")
        >>> valid
        True
        >>> validate_input("__import__('os').system('rm -rf /')")
        (False, 'Input contains potentially dangerous pattern: __')
    """
    # Empty check
    if not user_input or not user_input.strip():
        return False, ""

    sanitized = sanitize_input(user_input)
    if not sanitized:
        return False, ""

    # Dangerous patterns to block
    dangerous_patterns = [
        '__',  # Python dunder methods
        'import',  # Module imports
        'exec',  # Code execution
        'eval',  # Code evaluation
        'open',  # File operations
        'os.',  # OS module
        'sys.',  # System module
        'subprocess',  # Subprocess calls
        'compile',  # Code compilation
    ]

    lower_input = user_input.lower()
    for pattern in dangerous_patterns:
        if pattern in lower_input:
            return False, f"Input contains potentially dangerous pattern: {pattern}"

    # Check for only allowed characters
    # Allowed: alphanumeric, spaces, and math symbols +-*/()^!.,=<> and some text
    allowed_pattern = re.compile(r'^[\w\s+\-*/%().,^!<>=]+$')

    # Allow common command words and function names
    # Strip out known safe words before checking
    check_input = re.sub(
        r'\b(sin|cos|tan|log|ln|sqrt|pow|pi|e|mc|mr|help|clear|cls|exit|quit|history)m\b',
        '',
        lower_input
    )

    if check_input.strip() and not allowed_pattern.match(check_input.strip()):
        invalid_chars = set(re.findall(r'[^\w\s+\-*/%().,^!<>=]', check_input))
        return False, f"Invalid characters detected: {', '.join(sorted(invalid_chars))}"

    return True, ""


def sanitize_input(user_input: str) -> str:
    """Sanitize user input by removing whitespace and normalizing.

    Args:
        user_input: Raw input string from user.

    Returns:
        Sanitized input string with leading/trailing whitespace removed.

    Example:
        >>> sanitize_input("  2 + 2  ")
        '2 + 2'
        >>> sanitize_input("   ")
        ''
    """
    if not user_input:
        return ""
    return user_input.strip()


def parse_command(user_input: str) -> Tuple[str, List[str]]:
    """Parse user input into command and arguments.

    Args:
        user_input: Raw input string from user.

    Returns:
        A tuple of (command, arguments) where command is the first word
        and arguments is a list of remaining tokens.

    Example:
        >>> parse_command("M+ 5")
        ('m+', ['5'])
        >>> parse_command("help")
        ('help', [])
        >>> parse_command("sqrt(16)")
        ('sqrt(16)', [])
    """
    sanitized = sanitize_input(user_input)
    if not sanitized:
        return "", []

    parts = sanitized.split()
    if not parts:
        return "", []

    return parts[0].lower(), parts[1:]


def get_version() -> str:
    """Return the calculator version string.

    Returns:
        Version string in format 'X.Y.Z'.
    """
    return VERSION
