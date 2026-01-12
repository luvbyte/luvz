import json
from pathlib import Path
from typing import IO, Any, Optional, Type, Union
from pydantic import BaseModel, ValidationError

def parse_file(
  file: IO | dict,
  model: Optional[Type[BaseModel]] = None,
  parse_type: str = "json"
) -> Any:
  try:
    if parse_type == "dict":
      data = file
    elif parse_type == "json":
      data = json.load(file)
    else:
      raise Exception(f"Unsupported parse type: {parse_type}")
  except Exception as e:
    raise Exception(f"Failed to parse file as {parse_type}: {e}")

  if model is None:
    return data

  try:
    return model.model_validate(data)
  except ValidationError:
    raise Exception(f"Invalid structure for model {model.__name__}")

def parse_config(
  file_path: Union[str, Path, dict],
  model: Optional[Type[BaseModel]] = None,
  parse_type: str = "json"
) -> Any:
  try:
    if isinstance(file_path, dict):
      return parse_file(file_path, model, "dict")
    with open(file_path, "r") as file:
      return parse_file(file, model, parse_type)
  except FileNotFoundError:
    raise FileNotFoundError(f"Config file not found: {file_path}")
  except json.JSONDecodeError:
    raise json.JSONDecodeError(f"Invalid JSON format: {file_path}")
  except Exception as e:
    raise Exception(f"Unexpected error parsing {file_path}: {e}")
