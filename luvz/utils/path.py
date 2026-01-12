from pathlib import Path

from typing import Union

def ensure_dir(path: Union[Path, str]) -> Path:
  Path(path).mkdir(parents=True, exist_ok=True)
  return path
