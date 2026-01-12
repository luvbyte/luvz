import sys

# ------ Run types
def run_script_it(script, intro: bool = True):
  from .interactive import ZScriptRunner
  return ZScriptRunner(script).run(intro=intro)

def run_script_cli(script, intro: bool = False):
  from .cli import ZScriptRunnerCli
  return ZScriptRunnerCli(script).run(intro=intro)

def run_script(script, *args, **kwargs):
  return run_script_cli(script, *args, **kwargs) if len(sys.argv) > 1 else run_script_it(script, *args, **kwargs)
