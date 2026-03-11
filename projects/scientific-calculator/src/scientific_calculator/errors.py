"""Custom exception classes for scientific calculator.

This module defines the exception hierarchy used throughout
the scientific calculator application.
"""


class CalculatorError(Exception):
    """Base exception for calculator-related errors.

    This is the parent exception for all calculator-specific errors.
    All custom exceptions in the calculator should inherit from this.

    Attributes:
        message: The error message explaining what went wrong.
    """

    def __init__(self, message: str) -> None:
        """Initialize the exception with a message.

        Args:
            message: Human-readable description of the error.
        """
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of the error.

        Returns:
            The error message.
        """
        return self.message


class InputError(CalculatorError):
    """Exception raised for invalid user input.

    This exception is raised when the user provides input that cannot
    be processed, such as malformed expressions or invalid commands.

    Attributes:
        message: Description of why the input was invalid.
        input_text: The invalid input that caused the error (optional).
    """

    def __init__(self, message: str, input_text: str = "") -> None:
        """Initialize the input error.

        Args:
            message: Description of the error.
            input_text: The invalid input (for debugging/display).
        """
        self.input_text = input_text
        super().__init__(message)

    def __str__(self) -> str:
        """Return formatted error string.

        Returns:
            Error message with optional input reference.
        """
        if self.input_text:
            return f"{self.message} (input: '{self.input_text}')"
        return self.message


class ValidationError(InputError):
    """Exception raised for input that failed validation checks.

    This exception is used when input passes basic parsing but fails
    semantic validation, such as invalid characters, disallowed tokens,
    or safety checks.

    Attributes:
        message: Description of the validation failure.
        input_text: The validated input.
        violation: Specific validation rule that was violated.
    """

    def __init__(
        self, 
        message: str, 
        input_text: str = "",
        violation: str = ""
    ) -> None:
        """Initialize the validation error.

        Args:
            message: Description of the validation failure.
            input_text: The input that failed validation.
            violation: Specific rule or check that failed.
        """
        self.violation = violation
        super().__init__(message, input_text)

    def __str__(self) -> str:
        """Return formatted validation error.

        Returns:
            Error message with violation details.
        """
        base_msg = self.message
        if self.violation:
            base_msg = f"{base_msg} [violation: {self.violation}]"
        if self.input_text:
            return f"{base_msg} (input: '{self.input_text}')"
        return base_msg
