import requests
from bs4 import BeautifulSoup
import sys
import textwrap
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from renderer.render import FinderFile

"""
class FinderFile:
    def __init__(
        self,
        title: str,
        position: tuple[int, int],
        is_link: bool = False,
        href: str | None = None,
        tag: str | None = None,
    ):
        self.title: str = title
        self.position: tuple[int, int] = position
        self.is_link: bool = is_link
        self.href: str | None = href
        self.tag: str | None = tag
"""

class CoordinateSystem:
    def __init__(self, url: str, width: int, height: int) -> None:  
        self.__url: str = url  
        self.__width: int = width
        self.__height: int = height
        data: requests.models.Response = requests.get(url)
        self.soup: BeautifulSoup = BeautifulSoup(data.text, 'html.parser')

    def __get_element_bboxes_playwright(self, selectors: list[str]) -> list[dict[str, int]]:
        results: list[dict[str, int]] = []
        viewport: tuple[int, int] = (self.__width, self.__height)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': viewport[0], 'height': viewport[1]})
            page.goto(self.__url)
            page.wait_for_load_state("networkidle")
            for sel in selectors:
                rect = page.evaluate(
                    """(s) => {
                        const el = document.querySelector(s);
                        if (!el) return null;
                        const r = el.getBoundingClientRect();
                        return {x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height)};
                    }""",
                    sel,
                )
                results.append(rect)
            browser.close()
        return results
    
    def coord_all(self, slice_size: int = 20) -> list[FinderFile]:
        elems = [el for el in self.soup.find_all(True)]
        selectors = [el.name for el in elems]
        bbox_results = self.__get_element_bboxes_playwright(selectors)
        
        result: list[FinderFile] = []
        skip_tags = {"html", "head", "meta", "script", "style"}
        for el, sel, rect in zip(elems, selectors, bbox_results):
            if not rect or el.name.lower() in skip_tags:
                continue
            
            title = el.get_text()
            is_link = el.name.lower() == "a"
            if href := el.get("href"):
                href = str(href)
            else:
                href = None
            position = (rect["x"] + int(rect["width"] / 2), rect["y"] + int(rect["height"] / 2))
            
            for t in textwrap.wrap(title, 20):
                result.append(FinderFile(title=t, position=position, is_link=is_link, href=href, tag=el.name.lower()))
            
        return result
        

def main():
    d = CoordinateSystem("https://google.com", 1000, 1000) # ds.get_width, ds.get_height
    coords = d.coord_all()
    pass

if __name__ == "__main__":
    main()