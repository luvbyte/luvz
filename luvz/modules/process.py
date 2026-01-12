import sys

from os import getcwd
from subprocess import Popen, PIPE


class Process:
  def __init__(self, proc: Popen):
    self._process = proc
  
  def wait(self) -> 'Process':
    self._process.wait()
    return self

  def output(self) -> str:
    if self._process.stdout:
      output = self._process.stdout.read().decode("utf-8").strip()
      return output
    return ""

  @property
  def returncode(self) -> int:
    return self._process.returncode

class ProcessBuilder:
  def __init__(self, cmd: str) -> None:
    self.cmd: str = cmd
    self.stdin = PIPE
    self.stdout = PIPE
    self.stderr = PIPE
    self.shell: bool = True
    self.cwd: str = getcwd()

  def pipe(self) -> Process:
    return self._run()

  def run(self) -> Process:
    self.stdin = sys.stdin
    self.stdout = sys.stdout
    self.stderr = sys.stderr
    return self._run()

  def _run(self) -> Process:
    proc = Popen(
      self.cmd,
      cwd=self.cwd,
      shell=self.shell,
      stdin=self.stdin,
      stdout=self.stdout,
      stderr=self.stderr,
    )
    return Process(proc).wait()


def sh(cmd: str) -> ProcessBuilder:
  return ProcessBuilder(cmd)
