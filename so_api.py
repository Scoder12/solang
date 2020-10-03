"""Simple interface to the Stack Overflow answers API."""
import os
from pathlib import Path
import sys
from typing import Tuple, Union
from urllib.parse import urlencode

import requests


cache_dir = Path(".so_cache")
cache_dir.mkdir(exist_ok=True)


class CachedAPIInterface:
    """Simple interface to the Stack Overflow answers API."""

    def __init__(self, key: str, access_token: str) -> None:
        """Initialize class.

        Arguments can be obtained from https://SO-lang-tokens.scoder12.repl.co

        Args:
            key: API key from stack exchange
            access_token: Access token from stack exchange
        """
        self.key = key
        self.access_token = access_token

    def _perform_request(self, endpoint: str) -> dict:
        # hacky way of adding in the key
        url = f"https://api.stackexchange.com{endpoint}&" + urlencode(
            {"key": self.key, "access_token": self.access_token}
        )
        print(url)
        r = requests.get(url)
        # Don't raise for status because we want to see error message
        return r.json()

    def get_answer(self, ansid: Union[str, int], quiet: bool = False) -> str:
        """Retrive the body of answer ansid.

        Tries to load cached version, otherwise performs a request and writes to cache.
        """

        def log(msg: str) -> None:
            """Print data, obeying quiet kwarg."""
            if not quiet:
                print(msg)

        cached_path = str(cache_dir / f"a{ansid}.html")
        try:
            with open(cached_path, "r") as f:
                cached_data = f.read()
        except OSError:
            cached_data = None

        if cached_data:
            return cached_data

        log(f"[*] Downloading answer {ansid}")
        data = self._perform_request(
            f"/2.2/answers/{ansid}?site=stackoverflow&filter=withbody"
        )

        if "error" in data or "error_message" in data:
            raise ValueError(f"API reported error: {data}")

        log(
            f"[!] Request quota: {data.get('quota_remaining', '?')}/"
            f"{data.get('quota_max', '?')} left"
        )
        item = data["items"][0]
        body = item["body"]
        try:
            with open(cached_path, "w") as f:
                f.write(body)
        except OSError:
            print(f"WARNING: Unable to write to {cached_path}")
        return body


def from_environ() -> Tuple[str, str]:
    """Gets the api key and token from the environment.

    Returns:
        Tuple[str, str]: key, token
    """
    return CachedAPIInterface(os.environ["SOLANG_KEY"], os.environ["SOLANG_TOKEN"])


def main() -> None:
    """Main entrypoint for file."""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <answer_id>", file=sys.stderr)
        return

    quiet = "--quiet" in sys.argv
    client = from_environ()
    print(client.get_answer(sys.argv[1], quiet=quiet))


if __name__ == "__main__":
    main()
