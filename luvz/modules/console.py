import os
import sys
import time
import atexit
import select

from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich.console import Console
from rich.columns import Columns

from typing import Literal


class AdvConsole(Console):
  def __init__(self) -> None:
    super().__init__()

    atexit.register(self.__on_exit)

  # hide / show cursor
  def hide_cursor(self, hide: bool = True) -> None:
    if hide:
      sys.stdout.write("\033[?25l")  # Hide cursor
    else:
      sys.stdout.write("\033[?25h")  # Show cursor when stopping

  # clear screen
  def clear(self) -> None:
    os.system("cls" if os.name == "nt" else "clear")  # Windows: cls, Linux/macOS: clear

  # print empty lines
  def br(self, lines: int = 1) -> None:
    self.print(end="\n"*lines)

  # print panel
  def print_panel(
    self,
    content,
    title: str = "",
    subtitle: str = "",
    justify: Literal['left', 'right', 'center'] = "left",
    padding: bool = True,
    expand: bool = True,
    markup: bool = True
  ) -> None:
    # Add padding if requested
    if padding:
      content = f"\n{content}\n"

    # Create Text safely depending on markup flag
    if markup:
      text_obj = Text.from_markup(content, justify=justify)
    else:
      text_obj = Text(content, justify=justify)

    # Print Panel with text object
    self.print(
      Panel(
        text_obj,
        title=title,
        subtitle=subtitle,
        expand=expand
      )
    )

  # print text with align
  def print_text(self, text, markup: bool = True, align: Literal['left', 'right', 'center'] = "left"):
    text = Text.from_markup(text) if markup else Text(text)
    self.print(Align(text, align = align))

  def print_center(self, text: str, markup: bool = True):
    self.print_text(text, markup, "center")

  # equal=True, expand=True
  def columns(self, *args, **kwargs):
    return Columns(*args, **kwargs)

  def panel(self, *args, **kwargs):
    return Panel(*args, **kwargs)

  def print_list(
    self,
    items,
    border: bool = True,
    multi: bool = False,
    title: str | None = None,
    expand: bool = True,
    equal: bool = True,
    style: str = "white",
    index_color: str = "cyan"
  ) -> None:
    if not items:
      raise Exception("Items list cannot be empty")

    # Numbered items with style
    numbered_items = [
      f"[bold {index_color}]{i}.[/bold {index_color}] [bold {style}]{item}[/bold {style}]"
      for i, item in enumerate(items, start=1)
    ]

    # Build layout
    if multi:
      cpanel = Columns(numbered_items, expand=expand, equal=equal)
    else:
      cpanel = "\n".join(numbered_items)

    # Render with or without panel
    if border:
      self.print(Panel(cpanel, title=title, expand=expand))
    else:
      self.print(cpanel)
  
  def print_table(
    self, 
    columns, 
    rows, 
    title=None, 
    header_style="bold cyan",
    border_style="blue",
    col_style="green"
  ):
    table = Table(
      title=f"[bold magenta]{title}[/bold magenta]" if title else None,
      header_style=header_style,
      border_style=border_style
    )

    # Add columns
    for col in columns:
      table.add_column(col, style=col_style)

    # Add rows
    for row in rows:
      table.add_row(*[str(item) for item in row])
  
    self.print(table)

  # True - completed, False - canceled
  def wait_basic(self, seconds: float = 5, message="(Ctrl + C to stop)") -> bool:
    """Waits with a countdown, allows interruption with Ctrl+C."""
    try:
      self.hide_cursor()  # Hide cursor
      for i in reversed(range(0, seconds)):
        print(f"{message} : {i} ", end="\r", flush=True)
        time.sleep(1)
      return True  # Completed successfully
    except KeyboardInterrupt:
      # print("\nInterrupted!")
      return False  # Interrupted by user
    finally:
      self.hide_cursor(False)  # Show cursor
      sys.stdout.flush()

  def wait(self, timeout: float = 5.0, message: str = "Time remaining") -> bool:
    try:
      self.hide_cursor()  # Hide
      start_time = time.time()
      while True:
        elapsed = time.time() - start_time
        remaining = max(0, int(timeout - elapsed))
        # print(f"{message} : {remaining}", end="\r", flush=True)
        sys.stdout.write(f"\r{message} : {remaining}")
        sys.stdout.flush()
  
        # Check for input every 0.1s
        if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
          line = sys.stdin.readline()
          print()  # Move to next line after user input
          return True if line == '\n' else False

        if elapsed >= timeout:
          return True
    except KeyboardInterrupt:
      return False
    finally:
      self.hide_cursor(False)  # Show cursor
      sys.stdout.write("\r\033[K")
      sys.stdout.flush()

  # clean up
  def __on_exit(self) -> None:
    self.hide_cursor(False)

def convert_markup_to_text(markup_text) -> str:
  return Text.from_markup(markup_text).plain
