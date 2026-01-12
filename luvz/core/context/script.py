import os
import sys
import cmd2
import inspect

from uuid import uuid4
from pathlib import Path

from luvz.modules.process import sh
from luvz.utils.path import ensure_dir
from luvz.modules.console import AdvConsole
from luvz.core.models.script import ScriptConfigModel

from .task import ScriptTasks
from .command import ScriptCommands, Arg


# ---- script events 

class ScriptEvent:
  def __init__(self, name, func, *args, **kwargs):
    self.name = name
    self.func = func
  
  def emit(self, *args, **kwargs):
    return self.func(*args, **kwargs)

class ScriptEvents:
  def __init__(self):
    self._registers = {}

  def add(self, name: str, func, *args, **kwargs) -> ScriptEvent:
    event = ScriptEvent(name, func, *args, **kwargs)
    self._registers.setdefault(name, []).append(event)
    
    return event

  def has(self, name: str):
    return name in self._registers
  
  def get(self, name, default=None):
    return self._registers.get(name, default)

  def emit(self, name, *args, **kwargs):
    for ev in self._registers.get(name, []):
      ev.emit(*args, **kwargs)

# ---- Config and ZOptions

class ScriptConfig:
  def __init__(self, config: ScriptConfigModel):
    self._config = config
    self.luvz_path = ensure_dir(Path.home() / ".luvz")

class ScriptOption:
  def __init__(self, name, value=None, require=False, type=str, choices=(), help=None):
    self.name = name
    self._value = value          # store actual value internally
    self._type = type
    self.choices = choices
    self.require = require
    
    self.help = help

  @property
  def value(self):
    """Return the value, enforcing 'require' rule."""
    if self.require and self._value is None:
      raise ValueError(f"Required option '{self.name}' is missing a value")
    return self._value

  @value.setter
  def value(self, new_value):
    # 1. cast the input
    try:
      casted = self._type(new_value)
    except (ValueError, TypeError):
      raise TypeError(
        f"Option '{self.name}' expects type {self._type.__name__}, "
        f"but got {new_value!r} of type {type(new_value).__name__}"
      )

    # 2. cast the choices to _type too, once, to be safe
    if self.choices:
      try:
        normalized_choices = tuple(self._type(c) for c in self.choices)
      except (ValueError, TypeError):
        raise ValueError(f"Choices for option '{self.name}' cannot be cast to {self._type.__name__}")
      if casted not in normalized_choices:
        raise ValueError(
          f"Invalid value for option '{self.name}': {casted!r}. "
          f"Allowed choices: {normalized_choices}"
        )

    # 3. enforce require
    if self.require and casted is None:
      raise ValueError(f"Cannot set None for required option '{self.name}'")

    self._value = casted
  
  def __str__(self):
    return self.value or ""

class ScriptOptions:
  def __init__(self):
    self._options = {}
  
  def add(self, name, *args, **kwargs):
    option = ScriptOption(name, *args, **kwargs)
    self._options[name] = option
    return option
  
  # sets option else raises error
  def set(self, name, value):
    if name not in self._options:
      raise KeyError(f"Option '{name}' does not exist")
    self._options[name].value = value

  # returns direct value
  def get(self, name):
    if name not in self._options:
      raise KeyError(f"Option '{name}' does not exist")
    return self._options[name].value
  
  def __call__(self, name):
    return self.get(name)

# ---- Script Args (argv)

class ScriptArgs:
  def __init__(self):
    self._raw_args = sys.argv[1:]

  def get(self, index, default=None):
    try:
      return self._raw_args[index]
    except ValueError:
      return default
  
  def __str__(self):
    return " ".join(self._raw_args)

# ---- ZScript

class ZScript:
  prompt = "| "
  banner = None
  def __init__(self, name=None, version=None, author=None, desc=None, config={}):
    # script paths
    self.script_full_path = Path(sys.argv[0])
    self.script_path = self.script_full_path.parent
    
    # with ext
    self.script_name = os.path.basename(sys.argv[0])
    # script meta
    self.name = (name or Path(sys.argv[0]).with_suffix("").name).capitalize()
    self.desc = desc
    self.author = author
    self.version = version

    self.scr = AdvConsole()
    self.options = ScriptOptions()
    self.config = ScriptConfig(ScriptConfigModel(**config))

    self.events = ScriptEvents()
    self.commands = ScriptCommands()
    self.tasks = ScriptTasks()

    self.sh = sh
    # finally parsing args
    self.args = ScriptArgs()

  @property
  def cwd(self):
    return os.getcwd()

  def arg(self, *args, **kwargs):
    return Arg(*args, **kwargs)

  def add_option(self, *args, **kwargs):
    return self.options.add(*args, **kwargs)

  def on(self, name, *args, **kwargs):
    def wrapper(func):
      if name.startswith("luvz:"):
        self.events.add(name[4:], func, *args, **kwargs)
      else:
        self.commands.add(name, func, *args, **kwargs)
    return wrapper

  def on_event(self, name, *args, **kwargs):
    def wrapper(func):
      self.events.add(name, func, *args, **kwargs)
    return wrapper

  def __call__(self, cmd):
    if cmd.startswith("$"):
      return self.sh(cmd[1:])

