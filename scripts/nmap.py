from luvz import ZScript, run_script, Arg
from luvz.modules.process import sh

script = ZScript()

host = script.add_option("host", require=True)

@script.on("start", short="Short description")
def start():
  print(f"nmap -sV {host.value}")


if __name__ == "__main__":
  run_script(script)
