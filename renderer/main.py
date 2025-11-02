from argparse import ArgumentParser
from playwright.sync_api import sync_playwright

from domreader.domreader import dom_read
from render import finder_render
from url_image_converter import URLImageConverter


def main():
    parser = ArgumentParser(description="Turns Finder to a web browser.")
    parser.add_argument(
        "-u", "--url", type=str, help="The URL to open. If plotting, this is ignored."
    )
    parser.add_argument("-p", "--plot", action="store_true", help="Make a nice plot.")
    parser.add_argument(
        "-t", "--text", action="store_true", help="Use text-based rendering."
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
            coords, _, title = dom_read(playwright, args.url)
        finder_render(title, coords)
        return
      
    converter = URLImageConverter(args.url, icon_limit=230)
    tokens, title = converter.get_image_display() + converter.get_link_display(), converter.title
    finder_render(title, tokens, icon_size=512)

if __name__ == "__main__":
    main()
