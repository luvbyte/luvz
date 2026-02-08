from luvz import ZScript, run_script, Arg


script = ZScript()

# These are global options
# username = script.add_option("username", require=True)
# host = script.add_option("host", "localhost")

# These are commands
# @script.on("foo")
#def foo(name: str, age: int = 25):
  #print(username.value)

#@script.on("bar")
#def bar(name: str, age: int = 25):
  #print(host.value)


if __name__ == "__main__":
  run_script(script)
