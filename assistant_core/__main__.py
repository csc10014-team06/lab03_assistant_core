"""Allow ``python -m assistant_core``."""

import sys

from assistant_core.cli import entrypoint

sys.exit(entrypoint())
