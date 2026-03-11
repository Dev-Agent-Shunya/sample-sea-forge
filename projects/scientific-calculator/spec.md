# Scientific Calculator Specification

## Task Information
- **Task Code**: SFG00
- **Project Name**: Scientific Calculator
- **Phase**: Planning (000-099)
- **Branch**: SFG00-000-11/03/26
- **Platform**: SeaForge (Modified AutoForge)

---

## 1. Overview

The Scientific Calculator is a command-line interface (CLI) application that provides comprehensive mathematical computation capabilities. Built with Python, it offers both basic arithmetic operations and advanced scientific functions with expression parsing, memory management, and calculation history.

### Goals
1. Create a robust, user-friendly CLI calculator
2. Support expression parsing with proper operator precedence (PEMDAS)
3. Implement comprehensive scientific mathematical functions
4. Provide persistent memory and history features
5. Achieve high code quality with comprehensive unit tests
6. Follow SeaForge development workflow and standards

---

## 2. Feature Requirements

### 2.1 Basic Arithmetic Operations
| Operation | Symbol | Description |
|-----------|--------|-------------|
| Addition | `+` | Sum of two numbers |
| Subtraction | `-` | Difference between numbers |
| Multiplication | `*` | Product of two numbers |
| Division | `/` | Quotient of division |
| Modulo | `%` | Remainder of division |

### 2.2 Scientific Functions
| Function | Syntax | Description |
|----------|--------|-------------|
| Sine | `sin(x)` | Trigonometric sine (radians) |
| Cosine | `cos(x)` | Trigonometric cosine (radians) |
| Tangent | `tan(x)` | Trigonometric tangent (radians) |
| Logarithm (base 10) | `log(x)` | Base-10 logarithm |
| Natural Logarithm | `ln(x)` | Base-e logarithm |
| Square Root | `sqrt(x)` | Square root of number |
| Power | `pow(x, y)` or `x^y` | x raised to power y |
| Factorial | `fact(x)` or `x!` | Factorial of integer x |

### 2.3 Mathematical Constants
| Constant | Symbol | Value |
|----------|--------|-------|
| Pi | `pi` or `π` | 3.141592653589793 |
| Euler's Number | `e` | 2.718281828459045 |

### 2.4 Expression Parsing
- **PEMDAS Support**: Proper handling of operator precedence
  - Parentheses
  - Exponents
  - Multiplication/Division (left-to-right)
  - Addition/Subtraction (left-to-right)
- **Parentheses Support**: Nested parentheses for complex expressions
- **Decimal Numbers**: Floating-point precision support
- **Unary Operators**: Negative numbers support (e.g., `-5 + 3`)

### 2.5 Memory Functions
| Function | Key | Description |
|----------|-----|-------------|
| Memory Plus | `M+` | Add current value to memory |
| Memory Minus | `M-` | Subtract current value from memory |
| Memory Recall | `MR` | Recall stored memory value |
| Memory Clear | `MC` | Clear memory (set to 0) |

### 2.6 History Management
- Store last 100 calculations
- View history with command
- Recall previous results
- Clear history functionality

### 2.7 CLI Interface Features
- Interactive prompt with clear feedback
- Error handling with descriptive messages
- Help command listing all features
- Exit/quit commands
- Clear screen command

---

## 3. Technical Architecture

### 3.1 Technology Stack
- **Language**: Python 3.8+
- **Parser**: Custom recursive descent parser or `ast` module
- **Math Library**: `math` (standard library)
- **Testing**: `unittest` or `pytest`
- **CLI Framework**: Built-in `cmd` module or custom implementation

### 3.2 Architecture Components

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Interface Layer                      │
│         (Command parsing, user interaction, I/O)             │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Expression Evaluator                       │
│    (Tokenization, parsing, AST evaluation, precedence)       │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Math Operations Engine                     │
│       (Basic arithmetic, scientific functions, constants)    │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Memory & History Management                     │
│            (State persistence, storage, retrieval)           │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Core Modules

| Module | Responsibility |
|--------|----------------|
| `calculator.py` | Main entry point and CLI loop |
| `parser.py` | Expression tokenization and parsing |
| `evaluator.py` | AST evaluation and math operations |
| `memory.py` | Memory register management |
| `history.py` | Calculation history tracking |
| `constants.py` | Mathematical constants and configuration |

---

## 4. Project Structure

```
projects/scientific-calculator/
├── docs/
│   ├── spec.md              # This specification
│   └── features.md          # Feature breakdown
├── src/
│   ├── __init__.py
│   ├── calculator.py        # Main CLI application
│   ├── parser.py            # Expression parser
│   ├── evaluator.py         # Math evaluation engine
│   ├── memory.py            # Memory management
│   ├── history.py           # History tracking
│   └── constants.py         # Constants and config
├── tests/
│   ├── __init__.py
│   ├── test_parser.py       # Parser unit tests
│   ├── test_evaluator.py    # Evaluator unit tests
│   ├── test_memory.py       # Memory unit tests
│   ├── test_history.py      # History unit tests
│   └── test_integration.py  # Integration tests
├── data/
│   └── .gitkeep             # History persistence directory
├── requirements.txt         # Python dependencies
├── README.md               # Project documentation
└── run.py                  # Entry point script
```

---

## 5. Dependencies

### 5.1 Required (Standard Library)
| Package | Purpose |
|---------|---------|
| `math` | Mathematical functions |
| `ast` | Abstract syntax tree (optional parser approach) |
| `re` | Regular expressions for tokenization |
| `cmd` | CLI framework (optional) |
| `json` | History persistence format |
| `os` | File system operations |
| `sys` | System operations |

### 5.2 Optional (Third-party)
| Package | Purpose | Version |
|---------|---------|---------|
| `pytest` | Enhanced testing | ^7.0.0 |
| `pytest-cov` | Test coverage | ^4.0.0 |
| `readline` | Better CLI input handling | built-in |

### 5.3 requirements.txt
```
# Core dependencies (standard library only)
# No external packages required for basic functionality

# Development dependencies (optional)
pytest>=7.0.0
pytest-cov>=4.0.0
```

---

## 6. Interface Design

### 6.1 Command Examples
```
Scientific Calculator v1.0
Type 'help' for commands, 'exit' to quit

> 2 + 2
4.0

> sin(pi/2)
1.0

> sqrt(16) + pow(2, 3)
12.0

> M+
Memory: 12.0

> MR * 2
24.0

> history
1. 2 + 2 = 4.0
2. sin(pi/2) = 1.0
3. sqrt(16) + pow(2, 3) = 12.0
4. MR * 2 = 24.0

> exit
Goodbye!
```

### 6.2 Available Commands
| Command | Description |
|---------|-------------|
| `help` | Show help message |
| `history` | Show calculation history |
| `clear` | Clear screen |
| `exit` / `quit` | Exit calculator |
| `MC` | Memory clear |
| `MR` | Memory recall |
| `M+ <val>` | Memory add |
| `M- <val>` | Memory subtract |

---

## 7. Testing Strategy

### 7.1 Unit Test Coverage
- **Parser Tests**: Tokenization, AST generation, error handling
- **Evaluator Tests**: All mathematical operations, edge cases
- **Memory Tests**: Store, recall, clear operations
- **History Tests**: Add, retrieve, limit enforcement

### 7.2 Test Cases
- Basic arithmetic: `2+2`, `10/3`, `15%4`
- Scientific: `sin(0)`, `cos(pi)`, `sqrt(25)`, `fact(5)`
- Complex expressions: `(2+3)*4`, `2^3+5*2`
- Edge cases: Division by zero, `sqrt(-1)`, `fact(-1)`
- Memory operations: Sequential M+, M-, MR, MC
- History: 100+ entries, persistence

### 7.3 Coverage Target
- Minimum 90% code coverage
- All public methods tested
- Edge cases and error paths covered

---

## 8. Development Phases (SeaForge Workflow)

| Phase | ID Range | Description |
|-------|----------|-------------|
| Planning | 000-009 | Specification and design |
| Core Features | 010-199 | Basic arithmetic and CLI |
| Scientific Functions | 200-399 | Advanced math operations |
| Memory & History | 400-599 | State management |
| Testing & Polish | 600-799 | Unit tests and refinement |
| Documentation | 800-999 | Final docs and release |

---

## 9. Acceptance Criteria

1. [ ] All basic arithmetic operations work correctly
2. [ ] All scientific functions produce accurate results
3. [ ] Expression parsing follows PEMDAS correctly
4. [ ] Memory functions (M+, M-, MR, MC) work as expected
5. [ ] History stores and displays last 100 calculations
6. [ ] CLI interface is intuitive and responsive
7. [ ] Unit tests achieve 90%+ coverage
8. [ ] Error handling provides clear feedback
9. [ ] Code follows PEP 8 style guidelines
10. [ ] Documentation is complete and accurate

---

## 10. SeaForge Integration Notes

- **Task Code**: SFG00
- **Planning Phase**: No PRs required (000-099)
- **Commit Format**: `plan(SFG00-000): <description>`
- **Development Phase**: PRs required (010-999)
- **Commit Format**: `feat(SFG00-010): <description>`
- **Branch Naming**: `SFG00-<ID>-<DD/MM/YY>`

---

*Document Version: 1.0*
*Created: 2026-03-11*
*Branch: SFG00-000-11/03/26*
