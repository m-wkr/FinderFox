import json

"""import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileMovedEvent

WATCH_DIR = "non_commit/rename_test"   # Need a search node
SCRIPT = "non_commit/test.py"   # Bash write with the url of the rename

class RenameHandler(FileSystemEventHandler):
    def on_moved(self, event):
        if not isinstance(event, FileMovedEvent):
            return
        old = event.src_path
        new = event.dest_path
        
        subprocess.run(["python3", SCRIPT, old, new])
        
        print(f"renamed: {old} -> {new}")

if __name__ == "__main__":
    obs = Observer()
    obs.schedule(RenameHandler(), str(WATCH_DIR), recursive=False)
    obs.start()
    try:
        obs.join()
    except KeyboardInterrupt:
        obs.stop()
        obs.join()"""

class State:
    def __init__(self, filename:str="state.json", url:str="https://camhack.org") -> None:
        with open(filename, "r") as state_file:
            state = json.loads(state_file.read())
        self.left: list[str] = state["left"] if "left" in state else []
        self.right: list[str] = state["right"] if "right" in state else []
        self.history: list[str] = state["history"] if "history" in state else []
        self.current: str = url
        
        with open(filename, "r") as state_file:
            pass
        """
        NEED TO INTEGRATE CORRECTLY
        - Should have a left and history of recently visited websites and be able to hyperlink the left and right with the latest
        """