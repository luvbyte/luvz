from .runner import any_run

class Event:
  def __init__(self, name, func, *args, **kwargs):
    self.name = name
    self.func = func
  
  def emit(self, *args, **kwargs):
    return any_run(self.func, *args, **kwargs)

class Events:
  def __init__(self):
    self._registers = {}

  def add(self, name: str, func, *args, **kwargs) -> Event:
    event = Event(name, func, *args, **kwargs)
    self._registers.setdefault(name, []).append(event)
    
    return event

  def has(self, name: str):
    return name in self._registers
  
  def get(self, name, default=None):
    return self._registers.get(name, default)

  def emit(self, name, *args, **kwargs):
    # print("Emit: ", name)
    for ev in self._registers.get(name, []):
      ev.emit(*args, **kwargs)
