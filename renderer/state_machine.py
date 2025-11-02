import json

class State:
    def __init__(self, filename:str=f"{__file__}/../state.json", url:str="https://camhack.org") -> None:
        with open(filename, "r") as state_file:
            state = json.loads(state_file.read())
        self.history: list[str] = state["history"] if "history" in state else []
        self.current: str = url
        
        with open(filename, "w") as state_file:
            state = {
                "history" : self.history + [self.current],
            }
            state_file.write(json.dumps(state))

if __name__ == "__main__":
    State()