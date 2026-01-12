import sys

from typing import Optional

def read_from_stdin() -> Optional[str]:
  if sys.stdin.isatty():  # True if running in terminal, no pipe
      return None
  return sys.stdin.read()

