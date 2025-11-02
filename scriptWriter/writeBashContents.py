import os
import logging
script_path = os.path.dirname(os.path.realpath(__file__))
interpreter_path = os.path.join(script_path, "..", "renderer", ".venv", "bin", "python3")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def writeToBashFile(url, text_mode=False):
  effective_interpreter = interpreter_path if os.path.exists(interpreter_path) else "python3"
  logger.info("Using interpreter: %s", effective_interpreter)
  logger.info("Searched for interpreter at: %s", interpreter_path)

  return f"""
  #!/bin/bash

  {effective_interpreter} \"{script_path}/../renderer/main.py\" -u \"{url}\"{" -t" if text_mode else ""}\n"""

def createBashFile(filePath, url, text_mode=False):
  with open(filePath, "w") as f:
    f.write(writeToBashFile(url, text_mode))

  os.chmod(filePath,0o755)
