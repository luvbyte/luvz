from .base import RunnerUtils

from luvz.core.context import ZScript


# cli
class ZScriptRunnerCli:
  def __init__(self, script: ZScript):
    self.script = script
    self.utils = RunnerUtils(self.script)

    self.script.events.emit("cli:init")

  @property
  def scr(self):
    return self.utils.scr

  def _display_cli_help(self):
    self.utils.print_script_header()
    self.scr.print(f"[red]Usage[/red]: {self.script.script_name} command [ARGS] [-h]")
    self.scr.br()

    self.utils.print_commands_cli()
    
  def run(self, intro: bool = False):
    self.script.events.emit("run")
    args = self.script.args._raw_args

    if len(args) <= 0:
      args = ["-h"]

    command = args[0]
    command_args = args[1:]

    # Show help
    if command in ("-h", "--help"):
      return self._display_cli_help()
  
    if intro:
      self.utils.print_intro()
    
    func = self.script.commands.get(command)
    if func is None:
      self.exception(f"command '{command}' not found")
      return self.scr.br()

    func.run_cli(command_args)
  
  def exception(self, text):
    self.utils.exception(text)
