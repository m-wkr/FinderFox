import sys
import math
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from renderer.render import FinderFile
from playwright.sync_api import sync_playwright
from PIL import Image
from io import BytesIO
from renderer.domreader.domreader import dom_read
from renderer.state_machine import State


class URLImageConverter:
    def __init__(self, url: str, icon_limit:int=200, icon_size=(512,512)) -> None:
        self.__icon_limit: int = icon_limit
        self.__icon_size: tuple[int, int] = icon_size
        self.title = ""
        self.__header = {
            "User-Agent": "CamHack/1.0 (mailto:your-email@example.com) Python/3.x requests",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        state_path = Path(__file__).parent / "state.json"
        self.__state = State(str(state_path))
        self.__img: Image.Image = self.__get_img(url)
        ### get_ref and get_natigation_buttons has the side effect of populating the ref_bboxes dict
        self.__ref_bboxes: dict[FinderFile, tuple[int,int,int,int]] = {}
        self.__get_navigation_buttons()
        self.__ref: list[FinderFile] = self.__get_ref(url)
        self.__links: int = len(self.__ref)
    
    def set_state(self, url):
        self.__state = State(url)
        self.__img: Image.Image = self.__get_img(url)
        self.__ref: list[FinderFile] = self.__get_ref(url)
            
    def __get_img(self, url) -> Image.Image:
        with sync_playwright() as p:
            browser = p.firefox.launch()
            page = browser.new_page()
            page.goto(url)
            browser.new_context().set_extra_http_headers(self.__header)
            page.wait_for_load_state("networkidle")
            img_bytes: bytes = page.screenshot(full_page=True)
            browser.close()
        img = Image.open(BytesIO(img_bytes)).convert('RGBA')
        return img
    
    def __get_state_history_ref(self):
        token = []
        
        if self.__state.history != []:
            token.append(FinderFile(title="[Image]", position=(0,0), is_link=True, href=self.__state.history[-1]))
        return token
    
    def __get_ref(self, url):
        with sync_playwright() as playwright:
            coords, self.__ref_bboxes, self.title = dom_read(playwright, url)
        tokens = list(filter(lambda x: x.is_link, coords))
        tokens.extend(self.__get_state_history_ref())
        self.__ref_bboxes = {k: v for k, v in self.__ref_bboxes.items() if k in tokens}
        return tokens
    
    def __linkless_tiling(self) -> list[tuple[int, int]]:
        ix, iy = self.__icon_size
        vx, vy = self.__img.size
        positions = [(ix*x, iy*y) for x in range(math.ceil(vx/ix)) for y in range(math.ceil(vy//iy))]
        return positions
    
    def __link_tiling(self) -> list[tuple[int, int]]:
        positions = []
        for (x,y,w,h) in self.__ref_bboxes.values():
            x = int(x / 4) * 4
            y = int(y / 4) * 4
            w = int(w)
            h = int(h)
            positions.append((x,y))
        return positions
    
    def __link_cover_tiling(self) -> list[tuple[int, int]]:
        positions = []
        for (x,y,w,h) in self.__ref_bboxes.values():
            x = int(x / 4) * 4
            y = int(y / 4) * 4
            w = int(w)
            h = int(h)
            positions.append((x+w,y))
            positions.append((x,y+h))
        return positions
    
    """def __link_with_cover_tiling(self) -> list[tuple[int, int]]:
        positions = []
        for (x,y,w,h) in self.__ref_bboxes.values():
            x = int(x)
            y = int(y)
            w = int(w)
            h = int(h)
            positions.append((x,y))
            positions.append((x+w,y))
            positions.append((x,y+h))
        return positions"""
    
    def __get_navigation_buttons(self):
        #ICON BACK 64, 64 Top Left
        #ICON BACK 64, 64 Top Right
        back_pos, search_pos = (0,0), (self.__img.size[0], 0)
        if self.__state.history != []:
            is_link = True
            href = self.__state.history[-1]
        else:
            is_link = False
            href = None
        ff = [
            FinderFile(title="[Image]", position=back_pos, is_link=is_link, href=href, icon_path="url_icon/search.png"),
            FinderFile(title="[Image]", position=search_pos, icon_path="url_icon/back.png"),
        ]
        
        for f in ff:
            self.__ref_bboxes[f] = (f.position[0], f.position[1], 64, 64)
        
    def __set_image_display(self, positions:list[tuple[int, int]], limit:int=0):
        bbpos_to_ref = {(int(bbox[0]), int(bbox[1])): ref for ref, bbox in self.__ref_bboxes.items()}
        result = []
        ix, iy = self.__icon_size
        for x, y in positions:
            icon_path = Path(__file__).parent / "url_icon" / f"{self.__icon_limit}.png"
            self.__img.crop((x, y, x+ix, y+iy)).save(icon_path)
            
            if ref := bbpos_to_ref.get((x,y)):
                is_link = True
                href = ref.href
            else:
                is_link = False
                href = None
    
            result.append(FinderFile(
                title="[Image]",
                position=(x,y),
                is_link=is_link,
                href=href,
                icon_path=str(icon_path)
            ))
            
            self.__icon_limit -= 1
            if limit >= self.__icon_limit:
                return result
        return result
            
    def get_image_display(self) -> list[FinderFile]:
        positions = self.__linkless_tiling()
        return self.__set_image_display(positions, limit=self.__links*3)
    
    """def get_link_display_with_cover(self) -> list[FinderFile]:
        positions = self.__link_with_cover_tiling()
        return self.__set_image_display(positions)"""
    
    def get_link_display(self) -> list[FinderFile]:
        positions = self.__link_tiling()
        return self.__set_image_display(positions)
    
    def get_cover_display(self) -> list[FinderFile]:
        positions = self.__link_cover_tiling()
        return self.__set_image_display(positions)
    
    
    
if __name__ == "__main__":
    
    # Returns a FinderFile list, overwrite url_icon directory
    # You can input an different icon_size (int, int) default is 512, 512
    
    converter = URLImageConverter("https://camhack.org/")
    tokens, _, title = converter.get_image_display(), converter.get_link_display(), converter.title
    pass