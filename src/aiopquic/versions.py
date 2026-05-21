"""Version + build-info reporter for aiopquic.

Usage:
    python -m aiopquic.versions
    aiopquic-versions                    # console-script entry point

Prints aiopquic's installed version + the picoquic / picotls submodule
SHAs captured at build time. SHAs come from `_build_info.py` written
by setup.py during wheel/editable install.
"""
from __future__ import annotations

import os
import sys

from aiopquic import __version__


def _build_info() -> tuple[str, str]:
    """Return (picoquic_sha, picotls_sha) — strings, never None.
    "unknown" if the build-info module wasn't generated (e.g. an
    older editable install rebuilt before setup.py captured SHAs)."""
    try:
        from aiopquic._build_info import PICOQUIC_SHA, PICOTLS_SHA
        return PICOQUIC_SHA, PICOTLS_SHA
    except ImportError:
        return "unknown", "unknown"


def print_versions(file=sys.stdout) -> None:
    import aiopquic
    pico_sha, ptls_sha = _build_info()
    src = os.path.dirname(aiopquic.__file__)
    print(f"aiopquic {__version__}", file=file)
    print(f"         {src}", file=file)
    print(f"picoquic {pico_sha}", file=file)
    print(f"picotls  {ptls_sha}", file=file)


def main() -> int:
    print_versions()
    return 0


if __name__ == "__main__":
    sys.exit(main())
