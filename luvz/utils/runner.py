import asyncio
import inspect



def any_run(func, *args, **kwargs):
  result = func(*args, **kwargs)

  if inspect.isawaitable(result):
    try:
      _loop = asyncio.get_running_loop()
    except RuntimeError:
      # No running loop → safe to create one
      return asyncio.run(result)
    else:
      # Running loop → schedule task
      return asyncio.create_task(result)

  return result

