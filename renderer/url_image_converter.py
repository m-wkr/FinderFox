from render import FinderFile
from playwright.sync_api import sync_playwright
from PIL import Image
from io import BytesIO
from domreader.domreader import dom_read


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
        self.__img: Image.Image = self.__get_img(url)
        self.__ref: dict[tuple[int, int], FinderFile] = self.__get_ref(url)
            
    def __get_img(self, url) -> Image.Image:
        with sync_playwright() as p:
            browser = p.firefox.launch()
            page = browser.new_page()
            page.goto(url)
            browser.new_context().set_extra_http_headers(self.__header)
            page.wait_for_load_state("networkidle")
            img_bytes: bytes = page.screenshot(full_page=True)
            browser.close()
        img = Image.open(BytesIO(img_bytes)).convert('RGB')
        return img
    
    def __get_ref(self, url):
        with sync_playwright() as playwright:
            coords, self.title = dom_read(playwright, url)
        coords = list(filter(lambda x: x.is_link, coords))
        result = {}
        for coord in coords:
            clamp_multiple = lambda x, base: base * round(x/base)
            key = (clamp_multiple(coord.position[0], self.__icon_size[0]), clamp_multiple(coord.position[1], self.__icon_size[1]))
            result[key] = coord
        return result
        
        
            
    def get_image_display(self, icon_size:tuple[int,int]=(512,512)) -> list[FinderFile]:
        result = []
        ix, iy = icon_size
        vx, vy = self.__img.size
        positions = [[(ix*x, iy*y)for x in range(vx//ix)] for y in range(vy//iy)]
        if not (vx/ix).is_integer():
            for row in positions:
                row.append((vx-ix, row[0][1]))
        if not (vy/iy).is_integer():
            positions.append(list(zip([x for (x, _) in positions[0]], [vy-iy for _ in range(len(positions[0]))])))
        count = 0
        for row in positions:
            for x, y in row:
                icon_path = f"renderer/url_icon/{count}.png"
                self.__img.crop((x, y, x+ix, y+iy)).save(icon_path)
                if value := self.__ref.get((x,y)):
                    href = value.href
                    is_link = value.is_link
                else:
                    href = None
                    is_link = False
                result.append(FinderFile(
                    title="",
                    position=(x,y),
                    href=href,
                    is_link=is_link,
                    icon_path=icon_path
                ))
                count += 1
                if count >= self.__icon_limit:
                    return result
        return result
    
if __name__ == "__main__":
    
    # Returns a FinderFile list, overwrite url_icon directory
    # You can input an different icon_size (int, int) default is 512, 512
    
    converter = URLImageConverter("https://en.wikipedia.org/wiki/Railtrack")
    tokens, title = converter.get_image_display(), converter.title
    pass