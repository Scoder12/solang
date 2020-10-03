"""SO Lang: compiler where you can only write stackoverflow answers."""
import abc
import json
import sys
import traceback

from so_api import CachedAPIInterface


# TODO: valid variable method with regex
class OutputLang(abc.ABC):
    """Base class that represents a language SO Lang can compile to."""

    @staticmethod
    @abc.abstractmethod
    def rename_variable(a: str, b: str) -> str:
        """Return the code to rename variable a to variable b."""
        pass

    @staticmethod
    @abc.abstractmethod
    def set_variable_to_literal(name: str, value: str) -> str:
        """Return the code to set variable name's value to value.

        Value is either a double-quoted string or a decimal literal.
        """
        pass


class CLike(OutputLang):
    """Base class for languages that use c-style assignment."""

    @staticmethod
    def rename_variable(a: str, b: str) -> str:
        """Return the code to rename variable a to variable b."""
        return f"{a} = {b}"

    @staticmethod
    def set_variable_to_literal(name: str, value: str) -> str:
        """Return the code to set variable name's value to value.

        Value is either a double-quoted string or a decimal literal.
        """
        return f"{name} = {value}"


class Python(CLike):
    """OutputLang representing python."""

    pass


class JavaScript(CLike):
    """OutputLang representing JavaScript."""

    pass


def parse_line(line: str, outlang: OutputLang) -> str:
    """Parse a single line of SO Lang code.

    Args:
        line: Line of code
        outlang: OutputLang to compile to
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return
    if line.startswith("rename"):
        parts = line.split(" ")
        if len(parts) < 3:
            raise ValueError("Usage: 'mv <a> <b>'")

        return outlang.rename_variable(parts[1], parts[2])

    if line.startswith("literal"):
        parts = line.split(" ")
        if len(parts) < 3:
            raise ValueError("Expected 'literal <a> <b>'")

        try:
            val = json.loads(parts[2])
            if type(val) not in [str, int]:
                raise TypeError()
        except (json.decoder.JSONDecodeError, TypeError):
            raise ValueError("Literal must be a double quoted string or number")

        return outlang.set_variable_to_literal(parts[1], val)

    # Interpret as answer id
    if not line.isdigit():
        raise ValueError("Invalid syntax")

    return "so_answer_not_implemented({ansid})"


class ParseError(Exception):
    """Represents an error that occurred while parsing."""

    pass


def parse(text: str, mode: OutputLang) -> str:  # TODO: Node support
    """Compile SO Lang Code.

    Args:
        text: SO Code to be parsed.
        mode: Language to transpile to.
    """
    res_lines = []

    for lineno, line in enumerate(text.split("\n")):
        indent = len(line) - len(line.lstrip())
        try:
            r = parse_line(line, mode)
        except Exception as e:
            raise ParseError(f"Parse error: {e} on line {lineno + 1}") from e

        for rl in r.split("\n"):
            res_lines.append(" " * indent + rl)

    return "\n".join(res_lines)


def main() -> None:
    """Command-line interface for SO Lang.

    Reads a file given on the command line and prints the parsed result.
    """
    DEBUG = True  # '--debug' in sys.argv

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <filename>", file=sys.stderr)
        sys.exit(1)
        return

    with open(sys.argv[1], "r") as f:
        text = f.read()

    try:
        r = parse(text, Python)
    except ParseError as e:
        print(str(e), file=sys.stderr)
        if DEBUG:
            traceback.print_exc()
        sys.exit(1)

    print(r)  # TODO: write to file


if __name__ == "__main__":
    main()
