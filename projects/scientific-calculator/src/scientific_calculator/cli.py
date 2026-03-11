"""Main CLI application for the scientific calculator.

This module implements the interactive REPL (Read-Eval-Print Loop)
for the calculator, providing a user-friendly command-line interface
with graceful error handling and keyboard interrupt support.
"""

import signal
import sys
from typing import Optional

from scientific_calculator.utils import (
    clear_screen,
    format_help_text,
    format_welcome_message,
    get_version,
    parse_command,
    validate_input,
)
from scientific_calculator.errors import CalculatorError, InputError, ValidationError


class CalculatorCLI:
    """Interactive CLI calculator with REPL loop.

    This class implements the main command-line interface for the
    scientific calculator. It provides the REPL loop, command handling,
    and graceful error recovery.

    Attributes:
        running: Boolean flag indicating if the REPL is active.
        memory: Calculator memory register for memory operations.
        prompt: String displayed before user input.

    Example:
        >>> cli = CalculatorCLI()
        >>> cli.run()  # Starts the interactive calculator
    """

    def __init__(self) -> None:
        """Initialize the calculator CLI.

        Sets up the initial state including memory register,
        running flag, and configures signal handlers.
        """
        self.running: bool = False
        self.memory: float = 0.0
        self.prompt: str = "calc> "
        self._setup_signal_handlers()

    def _setup_signal_handlers(self) -> None:
        """Configure signal handlers for graceful shutdown.

        Sets up handlers for SIGINT (Ctrl+C) and SIGTERM to ensure
        clean exit when interrupted.
        """
        signal.signal(signal.SIGINT, self._signal_handler)
        try:
            signal.signal(signal.SIGTERM, self._signal_handler)
        except AttributeError:
            # SIGTERM not available on Windows
            pass

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle interrupt signals gracefully.

        Args:
            signum: Signal number received.
            frame: Current stack frame.
        """
        print("\n\nInterrupted. Shutting down gracefully...")
        self.shutdown()

    def display_welcome(self) -> None:
        """Display the calculator welcome message."""
        print(format_welcome_message())

    def display_help(self) -> None:
        """Display the help text."""
        print(format_help_text())

    def parse_and_execute(self, user_input: str) -> Optional[str]:
        """Parse user input and execute appropriate action.

        This method handles command parsing and dispatches to the
        appropriate handler. For this iteration, only commands are
        implemented; expression parsing will come in later iterations.

        Args:
            user_input: Raw input string from the user.

        Returns:
            Result string if applicable, None for operations without output.

        Raises:
            InputError: If input cannot be processed.
            ValidationError: If input fails validation checks.
        """
        # Validate input
        is_valid, error_msg = validate_input(user_input)

        if not is_valid:
            if error_msg:
                raise ValidationError(error_msg, user_input)
            return None  # Empty input, continue silently

        # Parse command
        cmd, args = parse_command(user_input)

        if not cmd:
            return None

        # Execute command
        result = self._execute_command(cmd, args)
        return result

    def _execute_command(self, cmd: str, args: list) -> Optional[str]:
        """Execute a parsed command.

        Args:
            cmd: The command name (lowercase).
            args: List of command arguments.

        Returns:
            Command result or None.
        """
        # Built-in commands
        if cmd in ('exit', 'quit'):
            self.shutdown()
            return None

        if cmd == 'help':
            self.display_help()
            return None

        if cmd in ('clear', 'cls'):
            clear_screen()
            self.display_welcome()
            return None

        # Memory commands (placeholders for now)
        if cmd == 'mc':
            self.memory = 0.0
            return "Memory cleared"

        if cmd == 'mr':
            return f"Memory: {self.memory}"

        if cmd == 'm+':
            # In full implementation, would add to memory
            return f"Added to memory. Total: {self.memory}"

        if cmd == 'history':
            return "History feature coming in next iteration..."

        # If not a command, treat as expression (placeholder)
        # Full expression parsing in SFG00-200+
        return f"Expression input received: '{cmd}'. Parsing coming in next iteration!"

    def shutdown(self) -> None:
        """Gracefully shut down the calculator.

        Prints goodbye message, sets running flag to False,
        and exits cleanly.
        """
        print("\nGoodbye! Thank you for using SeaForge Calculator.")
        self.running = False
        sys.exit(0)

    def handle_error(self, error: Exception) -> None:
        """Handle calculator errors gracefully.

        Args:
            error: Exception that occurred.
        """
        if isinstance(error, ValidationError):
            print(f"Error: {error}")
        elif isinstance(error, InputError):
            print(f"Input error: {error}")
        elif isinstance(error, CalculatorError):
            print(f"Calculator error: {error}")
        elif isinstance(error, KeyboardInterrupt):
            print("\n\nInterrupted by user. Use 'exit' or 'quit' to exit properly.")
        else:
            print(f"Unexpected error: {error}")

    def run(self) -> None:
        """Run the calculator REPL loop.

        This is the main entry point for the calculator. It displays
        the welcome message and enters the interactive loop until
        the user exits.
        """
        self.running = True
        self.display_welcome()

        while self.running:
            try:
                # Get user input
                user_input = input(self.prompt).strip()

                # Parse and execute
                result = self.parse_and_execute(user_input)

                # Display result if any
                if result is not None:
                    print(result)

            except EOFError:
                # Handle Ctrl+D
                print()
                self.shutdown()
            except KeyboardInterrupt:
                self.handle_error(KeyboardInterrupt())
            except (ValidationError, InputError) as e:
                self.handle_error(e)
            except Exception as e:
                self.handle_error(e)


def main() -> int:
    """Entry point for the calculator application.

    Returns:
        Exit code (0 for success).
    """
    cli = CalculatorCLI()
    try:
        cli.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
