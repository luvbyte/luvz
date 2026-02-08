from .base import RunnerBase

from luvz.core.context import ZScript


# cli
class ZScriptRunnerCli:
  def __init__(self, script: ZScript):
    self.base = RunnerBase(script, clear=False)

    self.script.events.emit("cli:init")

  @property
  def scr(self):
    return self.base.scr
  
  @property
  def script(self) -> ZScript:
    return self.base.script

  def _display_cli_help(self):
    self.base.print_script_header()
    self.scr.print(f"[red]Usage[/red]: {self.script.script_name} command [ARGS] [-h]")
    self.scr.br()

    self.base.print_commands_cli()

  def _run(self):
    args = self.script.args._raw_args

    if len(args) <= 0:
      args = ["-h"]

    command = args[0]
    command_args = args[1:]

    # Show help
    if command in ("-h", "--help"):
      return self._display_cli_help()

    if self.script.intro:
      self.base.print_intro()

    func = self.script.commands.get(command)
    if func is None:
      self.exception(f"command '{command}' not found")
      return self.scr.br()

    func.run_cli(command_args)

  def run(self):
    self.script.events.emit("cli:run")
    
    self._run()

    self.script.events.emit("cli:end")
  
  def exception(self, text):
    self.base.exception(text)
