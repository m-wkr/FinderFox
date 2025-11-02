import os
script_path = os.path.dirname(os.path.realpath(__file__))

def writeToBashFile(url):
  return f"""
  #!/bin/bash
  
  python3 \"{script_path}/../renderer/main.py\" \"{url}\"\n"""

def createBashFile(filePath, url):
  with open(filePath, "w") as f:
    f.write(writeToBashFile(url))

  os.chmod(filePath,0o755)