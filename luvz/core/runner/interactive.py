import os
import sys
import types
import argparse

import asyncio
import inspect

from pathlib import Path
from datetime import datetime
from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser

from rich.text import Text
from rich.table import Table

from luvz.modules.process import sh
from .base import BANNER, RunnerBase
from luvz.core.context import ZScript, ScriptCommand


def make_options_parser():
  # script argparser
  script_argparse = Cmd2ArgumentParser()
  script_argparse.add_argument(
    'subcommand',
    nargs="?",
    choices=['required'],
    help='Display only required options'
  )
  return script_argparse

def make_commands_parser():
  # script argparser
  script_argparse = Cmd2ArgumentParser()
  script_argparse.add_argument(
    'subcommand',
    nargs="?",
    choices=['all'],
    help='Display all commands list'
  )
  return script_argparse

def make_cd_parser():
  # script argparser
  cd_argparse = Cmd2ArgumentParser()
  cd_argparse.add_argument('path', nargs="?", default=Path.home(), help='Change current directory')
  return cd_argparse


# cmd2 - interactive
class ZScriptRunner(Cmd):
  def __init__(self, script: ZScript):
    # bypassing cmd2 default argparse :)
    original_argv = sys.argv.copy()
    sys.argv = [sys.argv[0]]
    # init of Cmd
    super().__init__()
    # restoring argv
    sys.argv = original_argv

    self.base = RunnerBase(script, clear=True)
    self._register_commands()

    self.script.events.emit("it:init")

  @property
  def script(self) -> ZScript:
    return self.base.script

  # arg parser
  def _register_commands(self):
    for name, command in self.script.commands.items():
      desired_prog = command.argparser.prog or name

      @with_argparser(command.argparser)
      def do_func(inner_self, args, cmd=command):
        try:
          # run_maybe_async(cmd.run, args)
          cmd.run(args)
        except Exception as e:
          inner_self.exception(e)

      # cmd2's decorator changes both the argparser.prog and the function name
      # Fix them back:
      do_func.argparser.prog = desired_prog    # fixes Usage: text
      do_func.__name__ = f"do_{name}"  # fixes command name in help
      do_func.__qualname__ = f"do_{name}"  # also for introspection

      # finally bind the method to your instance
      setattr(self, f"do_{name}", types.MethodType(do_func, self))

  @property
  def scr(self):
    return self.base.scr

  @property
  def prompt(self):
    prompt = self.script.events.emit("prompt") or self.script.prompt
    return prompt() if callable(prompt) else prompt

  # --- commands
  def do_clear(self, _):
    self.scr.clear()

  def do_ls(self, line):
    sh(f"ls --color {line}").run()

  def do_pwd(self, _):
    self.scr.print(f"You are in: {os.getcwd()}")

  def do_exit(self, _):
    return True

  def complete_cd(self, text, line, begidx, endidx):
    return [
      str(path) for path in self.path_complete(text, line, begidx, endidx)
      if os.path.isdir(path)
    ]

  # Change Directory
  @with_argparser(make_cd_parser())
  def do_cd(self, args):
    try:
      os.chdir(args.path)
    except FileNotFoundError:
      self.exception(f"No such directory: '[green]{args.path}[/green]'")
    except Exception as e:
      self.exception(e)

  # ---- script
  @with_argparser(make_options_parser())
  def do_options(self, args):
    if args.subcommand == "required":
      self.base.print_options(True)
    else:
      self.base.print_options(False)

  @with_argparser(make_commands_parser())
  def do_commands(self, args):
    if args.subcommand == "all":
      self.base.print_commands_cmd2()
    else:
      self.base._print_commands(False)

  #--- setting option
  def help_zset(self):
    self.scr.print("[red]Usage[/red]: zset <name> <value>\n\nSET ZOption\n")

  def complete_zset(self, text, line, begidx, endidx):
    tokens = line.split()

    # Suggest option names when typing the option name
    if len(tokens) <= 1 or (begidx <= len(tokens[0]) + 1):
      return [name for name in self.script.options._options if name.startswith(text)]

    opt_name = tokens[1]

    # If typing the value
    if opt_name in self.script.options._options:
      opt = self.script.options._options[opt_name]

      # If the option has choices, show choices matching text
      if opt.choices:
        return [str(c) for c in opt.choices if str(c).startswith(text)]

      # Otherwise, use cmd2 built-in path completer
      return self.path_complete(text, line, begidx, endidx)

    return []

  def do_zset(self, line):
    if not line:
      self.scr.print("[red]Usage[/red]: zset <name> <value>\n")

    elif len(line.arg_list) < 2:
      self.scr.print("[red]Missing[/red]: <value>\n")
    else:
      try:
        # set
        name = line.arg_list[0]
        value = " ".join(line.arg_list[1:])
        
        self.script.options.set(name, value)
        self.scr.print(f"[red]Updated[/red]: {name}={value}\n")
      except Exception as e:
        self.exception(e.args[0])
  # ---

  def complete_help(self, text, line, begidx, endidx):
    commands = [name[3:] for name in dir(self) if name.startswith('do_') and not name.startswith("do__")]
    if not text:
      return commands
    return [cmd for cmd in commands if cmd.startswith(text)]

  def do_help(self, line):
    if line:
      return super().do_help(line)
    
    self.scr.print_panel("[red]Usage[/red]: command [ARGS] [-h]", padding=False)
    self.base.print_commands_cmd2()
    self.base.print_options()

  # ---- default
  def default(self, line):
    event = self.script.events.get("it:default")
    if event:
      return event.emit(line)
    self.scr.print(f"[blue]luvz[/blue]: Unknown command: [red]{line.command}[/red]")

  # ---- starts from here
  def _run(self):
    if self.script.intro: # TODO
      self.base.print_intro()

    self.cmdloop()

  def run(self):
    self.script.events.emit("it:run")
    
    self._run()

    self.script.events.emit("it:end")

  # Exception handling
  def exception(self, text):
    self.base.exception(text)



