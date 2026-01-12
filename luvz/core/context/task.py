from uuid import uuid4


class ScriptTask:
  def __init__(self, name):
    self.uid = uuid4().hex
    self.name = name

class ScriptTasks:
  def __init__(self):
    # taskID - Task
    self._active = {}

