from rich.table import Table
from luvz.core import __version__

import atexit


BANNER = r"""
[blue]██╗      ██╗   ██╗ ██╗   ██╗ ███████╗[/]
██║      ██║   ██║ ██║   ██║ ╚══███╔╝
[red]██║      ██║   ██║ ██║   ██║   ███╔╝ [/]
██║      ██║   ██║ ╚██╗ ██╔╝  ███╔╝  
[yellow]███████╗ ╚██████╔╝  ╚████╔╝  ███████╗[/]
╚══════╝  ╚═════╝    ╚═══╝   ╚══════╝
"""

class RunnerBase:
  def __init__(self, script, clear):
    self.script = script
    atexit.register(self.__on_exit)
    # emiting init
    self.script.events.emit("start")

    if clear if self.script.clear is None else self.script.clear:
      self.scr.clear()

  @property
  def scr(self): # global scr for runners
    return self.script.scr

  def print_header(self):
    self.scr.print_center(self.script.banner or BANNER)
    self.scr.print_center(f"luvz: [blue]luvbyte[/blue] | version: [red]{__version__}[/red]")

  def print_script_header(self):
    # Script header
    version = f" [red]v{self.script.version}[/red]" if self.script.version else ""
    author = self.script.author if self.script.author else "Someone [red]ᥫ᭡[/red]"
    self.scr.print_panel(f"✨ [blue]{self.script.name}[/blue]{version} by [green]{author}[/green]", padding=False)
  
  def print_intro(self):
    # if banner found print it
    if self.script.banner:
      self.scr.print_center(self.script.banner)
    # if its False then don't print any banner
    elif self.script.banner is not False:
      self.print_header()

    # script details
    self.print_script_header()

  def _print_commands(self, cmd2_commands: bool):
    commands = list(self.script.commands.items())

    self.scr.print_center(f"[italic magenta]{'No' if not cmd2_commands and len(commands) <= 0 else ''} Available Commands[/italic magenta]")

    # Split based on with and without short descriptions
    no_short, with_short = [], []
    for name, cmd in commands:
      (with_short if cmd.short else no_short).append((name, getattr(cmd, 'short', None)))

    if with_short or cmd2_commands:
      table = Table(header_style="bold cyan", border_style="blue", expand=True)
      table.add_column("Command", style="green")
      table.add_column("Description", style="yellow")

      # Predefined cmd2_commands rows
      if cmd2_commands:
        builtin_commands = {
          "alias": "Create command shortcuts",
          "edit": "Edit a script or configuration",
          "help": "Show help (use 'help -v' for verbose)",
          "history": "Show command history",
          "macro": "Record or play macros",
          "quit": "Exit the program",
          "run_pyscript": "Run a Python script",
          "run_script": "Run a script",
          "set": "Set configuration options",
          "shell": "Run shell commands",
          "shortcuts": "List available keyboard shortcuts",
          "options": "Script options",
          "commands": "Script commands",
          "zset": "Set ZOption",
          "---": "---"
        }
        for name, desc in builtin_commands.items():
          table.add_row(name, desc)

      # Add user commands with short descriptions
      for name, desc in with_short:
        table.add_row(name, desc)

      self.scr.print(table)

    if no_short:
      names = " ".join(name for name, _ in no_short)
      self.scr.print_panel(f"[blue]{names}[/blue]", padding=False)

  def print_commands_cmd2(self):
    return self._print_commands(True)

  def print_commands_cli(self):
    return self._print_commands(False)

  def print_options(self, required_only: bool = False):
    options = self.script.options._options

    # Filter only required options if present
    if required_only:
      options = {name: opt for name, opt in options.items() if opt.require}

    if not options:
      return self.scr.print_center(
        f"[italic red]Script has no{' required' if required_only else ''} options[/italic red]"
      )

    table = Table(
      title=f"[blue]Script{' Required' if required_only else ''} Options[/blue]",
      expand=True
    )

    for col, style in [
      ("Name", "cyan"),
      ("Value", "green"),
      ("Required", "magenta"),
      ("Type", "yellow"),
      ("Choices", "blue")
    ]:
      table.add_column(col, style=style, no_wrap=(col == "Name"))

    for name, opt in options.items():
      # Safely retrieve value
      try:
        val = opt.value
      except Exception:
        val = "[red]-[/red]"

      # Choices fallback to "-"
      choices = ", ".join(map(str, getattr(opt, "choices", []))) or "-"

      table.add_row(
        name,
        str(val),
        "Yes" if getattr(opt, "require", False) else "No",
        getattr(opt._type, "__name__", str(opt._type)),
        choices
      )

    self.scr.print(table)
  
  def __on_exit(self):
    self.script.events.emit("exit")

  def exception(self, text):
    self.scr.print(f"[red]Error:[/red] luvz: [blue]{text}[/blue]")

