import json
from typing import Any, Dict, List, Tuple


class Converter:
    def __init__(self, filename: str, width: int, height: int) -> None:
        self.__filename = filename
        self.__width = int(width)
        self.__height = int(height)
        self.elements: Dict[str, Dict[str, Any]] = {}

        try:
            with open(self.__filename, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception as e:
            print("Error reading file:", e)
            return

        if isinstance(data, list):
            root = {"tag": "root", "children": data}
        elif isinstance(data, dict):
            root = data
        else:
            print("Unexpected root JSON type:", type(data))
            return

        self._parse_node(root, 0, 0, self.__width, self.__height, path=root.get("tag", "root"))

    def _node_children(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        children = node.get("children")
        if isinstance(children, list):
            return children
        return []

    def _make_key(self, path: str, node: Dict[str, Any], index: int) -> str:
        attrs = node.get("attrs") or {}
        node_id = attrs.get("id")
        if node_id:
            return f"{path}/{node.get('tag', 'node')}#{node_id}"
        return f"{path}/{index}:{node.get('tag', 'node')}"

    def _record(self, key: str, node: Dict[str, Any], bbox: Tuple[int, int, int, int]) -> None:
        x, y, w, h = bbox
        self.elements[key] = {
            "tag": node.get("tag"),
            "attrs": node.get("attrs"),
            "text": node.get("text"),
            "bbox": {"x": x, "y": y, "width": w, "height": h},
        }

    def _parse_node(self, node: Dict[str, Any], x: int, y: int, w: int, h: int, path: str) -> None:
        key = path
        self._record(key, node, (x, y, w, h))

        children = self._node_children(node)
        if not children:
            return

        n = len(children)
        if n == 0:
            return

        child_h = max(0, h // n)
        for i, child in enumerate(children):
            child_y = y + i * child_h
            if i == n - 1:
                child_h_actual = y + h - child_y
            else:
                child_h_actual = child_h
            child_key = self._make_key(path, child, i)
            self._parse_node(child, x, child_y, w, child_h_actual, child_key)

    def get_text_elements(self) -> list[tuple[tuple[int,int], str]]:
        result = []
        for element in self.elements.values():
            if element["text"] != None and element["tag"] not in ["style"]:
                result.append(((element["bbox"]["x"], element["bbox"]["y"]), element["text"]))
        return result
        


def main():
    conv = Converter("renderer/converter/test_data.json", 1000, 1000)
    print(conv.get_text_elements())
    pass


if __name__ == "__main__":
    main()