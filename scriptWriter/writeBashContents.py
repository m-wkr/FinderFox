import os

def writeToBashFile():
  return """
  #!/bin/bash
  
  python3 "../renderer/main.py
  """

def createBashFile(filePath):
  with open(filePath, "w") as f:
    f.write(writeToBashFile())

  os.chmod(filePath,0o755)