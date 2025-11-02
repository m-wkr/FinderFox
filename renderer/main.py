from argparse import ArgumentParser
from playwright.sync_api import sync_playwright

from domreader.domreader import dom_read
from render import finder_render
from renderer.URLsanitiser import returnURL
from url_image_converter import URLImageConverter

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = ArgumentParser(description="Turns Finder to a web browser.")
    parser.add_argument(
        "-u", "--url", type=str, help="The URL to open. If plotting, this is ignored."
    )
    parser.add_argument("-p", "--plot", action="store_true", help="Make a nice plot.")
    parser.add_argument(
        "-t", "--text", action="store_true", help="Use text-based rendering."
    )
    parser.add_argument(
        "--no-links", action="store_true", help="Disable link rendering."
    )
    args = parser.parse_args()

    if not args.plot and not args.url:
        print(
            "Please provide either --url to open a webpage or --plot to make a nice plot."
        )
        return

    if args.plot:
        from renderer.plotter.plotter import plotter_render

        items = plotter_render()
        finder_render("Cam Hack 2025 - Plotter", items, icon_size=16)
        return

    if args.text:

        with sync_playwright() as playwright:
            coords, _, title = dom_read(playwright, returnURL(args.url), no_break=True)
        finder_render(title, coords)
        return
      
    converter = URLImageConverter(returnURL(args.url), icon_limit=300)
    image_tokens = converter.get_image_display()
    if args.no_links:
        link_tokens = []
    else:
        link_tokens = converter.get_link_display()
    # cover_tokens = converter.get_cover_display()
    cover_tokens = []

    tokens, title = image_tokens + link_tokens + cover_tokens, converter.title
    logger.info(f"Rendering {len(image_tokens)} image tokens and {len(link_tokens)} link tokens and {len(cover_tokens)} cover tokens.")

    finder_render(title, tokens, icon_size=512)

if __name__ == "__main__":
    main()
