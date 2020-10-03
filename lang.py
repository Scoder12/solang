import sys
import traceback
import re

from bs4 import BeautifulSoup

import so_api


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, inp: str, client: so_api.CachedAPIInterface) -> None:
        self.inp = inp
        self.client = client

        self._current_block = None
        self._lno = 0
        self._output = []

    def err(self, msg: str) -> None:
        raise ParseError("On line {self._lno}: {self.msg}")

    @staticmethod
    def fmt_code(code: str) -> str:
        # TODO: find lowest amount of spaces on the left of each line and strip that many
        # print("fmt", repr(code))
        return code

    def get_answer(self, ans_id: int, tag_ind: int) -> str:
        answer_html = self.client.get_answer(ans_id)
        soup = BeautifulSoup(answer_html, "html.parser")
        code_tags = soup.find_all("code")

        try:
            target = code_tags[tag_ind]
        except IndexError:
            self.err(
                f"Tried to get snippet {tag_ind} (0-based) when there are only {len(code_tags)} snippets"
            )

        return self.fmt_code(target.get_text())

    def _flush(self) -> None:
        if self._current_block:
            self._output.append(self._current_block)
            self._current_block = None

    def _parse_line(self, l: str) -> None:
        args = l.split(" ")
        if all(i.isdigit() for i in args[:2]):  # Its an answer id
            self._flush()
            code_num = 0 if len(args) < 2 else int(args[2])
            self._current_block = self.get_answer(int(args[0]), code_num)
        elif l.startswith("/"):
            if self._current_block is None:
                self.err("Attempted replacement before answer declaration")
            parts = l.split("/")
            # First one is "" due to line starting with /, so need 3
            if len(parts) < 3:
                self.err(
                    f"Expected replacement in the form of '/pattern/repl', got {l}"
                )
            pattern, repl = parts[1:3]
            self._current_block = re.sub(pattern, repl, self._current_block)
        else:
            self.err("Unrecognized expression")

    def parse(self) -> str:
        for l in self.inp.split("\n"):
            self._lno += 1
            l = l.strip().split("#")[0]
            if not l:
                continue
            self._parse_line(l)
        self._flush()
        return "\n\n\n".join(self._output)


def main() -> None:
    """Command-line interface for SO Lang.

    Reads a file given on the command line and prints the parsed result.
    """
    DEBUG = True  # '--debug' in sys.argv

    if len(sys.argv) < 3:
        print(
            f"Usage: {sys.argv[0]} <filename> <output (- for stdout)>", file=sys.stderr
        )
        sys.exit(1)
        return

    with open(sys.argv[1], "r") as f:
        text = f.read()

    client = so_api.from_environ()
    p = Parser(text, client)
    try:
        r = p.parse()
    except ParseError as e:
        print(str(e), file=sys.stderr)
        if DEBUG:
            traceback.print_exc()
        sys.exit(1)

    if sys.argv[2] == "-":
        print(r)
    else:
        print(f"[-] Writing {sys.argv[2]}")
        with open(sys.argv[2], "w") as f:
            f.write(r + "\n")


if __name__ == "__main__":
    main()
