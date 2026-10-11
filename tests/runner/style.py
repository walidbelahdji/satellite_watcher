"""Terminal colors and response diff formatting."""

import difflib


class ANSI:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    MAGENTA = "\033[0;35m"
    GRAY = "\033[0;90m"
    DIM_RED = "\033[2;31m"
    DIM_GREEN = "\033[2;32m"
    DIM_BLACK = "\033[2;37m"
    RESET = "\033[0m"


def diff_strings(expected: str, actual: str) -> str:
    """Format a line diff with terminal colors."""
    output = []
    matcher = difflib.ndiff(expected.splitlines(True), actual.splitlines(True))
    for line in matcher:
        if line.startswith("+"):
            output.append(ANSI.DIM_GREEN)
        elif line.startswith("-"):
            output.append(ANSI.DIM_RED)
        elif line.startswith("?"):
            continue
        else:
            output.append(ANSI.DIM_BLACK)
        output.append(line[2:])
    return f"{''.join(output)}{ANSI.RESET}"
