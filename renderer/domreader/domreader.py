from render import FinderFile

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def dom_read(playwright, url: str) -> tuple[list[FinderFile], dict[FinderFile, tuple[int,int,int,int]], str]:
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
                                "href": href if href else None,
                            }
                        )
        except Exception as e:
            # Ignore errors from elements that disappeared
            pass

    browser.close()
    bboxes = {}
    for item in all_text_data:
        text_value = item["text"]
        position = (
            int((item["x"] + item["width"] / 2)),
            int((item["y"] + item["height"] / 2) * 2),
        )
        ff = FinderFile(
                title=text_value,
                position=position,
                href=item["href"],
                is_link=item["href"] is not None,
            )
        bboxes[ff] = (item["x"], item["y"], item["width"], item["height"])
        ret.append(ff)
    return (ret, bboxes, page_title)
