from render import FinderFile
from imageDecomposition import imageBreak
import time
import imageio
import logging
from pathlib import Path
from urllib.parse import urlparse
import base64
import hashlib

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def dom_read(playwright, url: str) -> tuple[list[FinderFile], str]:
    ret = []
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1200, "height": 600})
    page.goto(url)

    page.wait_for_load_state("networkidle")

    page_title = page.title()

    js_script = """
    (element) => {
        var text = '';
        for (var i = 0; i < element.childNodes.length; i++) {
            var child = element.childNodes[i];
            if (child.nodeType === 3) { // Node.TEXT_NODE
                text += child.nodeValue;
            }
        }
        return text.trim();
    }
    """

    all_text_data = []
    all_elements = page.locator("//*").all()

    logger.info(f"Found {len(all_elements)} elements. Checking for text...")

    for element in all_elements:
        try:
            if not element.is_visible():
                continue

            # Evaluate the JS function on the element
            text = element.evaluate(js_script)

            if text:
                # Get bounding box
                href = element.get_attribute("href")
                box = element.bounding_box()
                if box:
                    words = [w for w in text.split() if w]
                    if not words:
                        continue

                    cols = int(len(words) ** 0.7)
                    if cols * cols < len(words):
                        cols += 1
                    cols = max(1, cols)
                    rows = max(1, (len(words) + cols - 1) // cols)

                    cell_width = box["width"] / cols
                    cell_height = box["height"] / rows

                    for idx, word in enumerate(words):
                        row = idx // cols
                        col = idx % cols
                        all_text_data.append(
                            {
                                "text": word,
                                "x": box["x"] + col * cell_width,
                                "y": box["y"] + row * cell_height,
                                "width": cell_width,
                                "height": cell_height,
                                "href": urlparse(href) if href else None,
                            }
                        )
            elif element.evaluate("el => el.tagName.toLowerCase() === 'img'"):
                # Handle images
                src = element.get_attribute("src")
                if src:
                    box = element.bounding_box()
                    image_dir = Path.cwd() / "images"
                    image_dir.mkdir(parents=True, exist_ok=True)
                    try:
                        file_bytes = None
                        file_suffix = ".bin"
                        parsed_src = urlparse(src)
                        if parsed_src.scheme == "data":
                            header, b64_data = src.split(",", 1)
                            file_bytes = base64.b64decode(b64_data)
                            mime = header.split(";")[0]
                            if "/" in mime:
                                file_suffix = f".{mime.split('/', 1)[1]}"
                        else:
                            resolved_src = element.evaluate("node => node.src") or src
                            response = page.context.request.get(resolved_src, timeout=5000)
                            if response.ok:
                                file_bytes = response.body()
                                path_suffix = Path(urlparse(resolved_src).path).suffix
                                if path_suffix:
                                    file_suffix = path_suffix
                        if file_bytes:
                            filename = f"{hashlib.sha256(file_bytes).hexdigest()[:16]}{file_suffix}"
                            output_path = image_dir / filename
                            if not output_path.exists():
                                output_path.write_bytes(file_bytes)
                            logger.info("Saved image to %s", output_path)
                    except Exception as image_error:
                        logger.debug("Failed to save image: %s", image_error)
                    if box:
                        brokenIms=imageBreak(output_path,{'x':16,'y':16},{'x':box['x'],'y':box['y']})
                        for brokenIm in brokenIms:
                            brokenOutpath=image_dir / "brimage"+str(time.time())+".png"
                            imageio.imwrite(brokenOutpath,brokenIm['im'])
                            all_text_data.append(
                                {
                                    "text": "[Image]",
                                    "x": brokenIm['pos']['x'],
                                    "y": brokenIm['pos']['y'],
                                    "width": 16,
                                    "height": 16,
                                    "href": None,
                                    "icon_path": str(brokenOutpath) if brokenOutpath else None,
                                }
                            )
                            logger.info(f"Found image in element: {src[:10]}...")

        except Exception as e:
            # Ignore errors from elements that disappeared
            pass

    browser.close()

    for item in all_text_data:
        text_value = item["text"]
        position = (
            int((item["x"] + item["width"] / 2)),
            int((item["y"] + item["height"] / 2) * 2),
        )
        ret.append(
            FinderFile(
                title=text_value,
                position=position,
                href=item["href"],
                icon_path=item["icon_path"] if "icon_path" in item else None,
                is_link=item["href"] is not None,
            )
        )
    return (ret, page_title)