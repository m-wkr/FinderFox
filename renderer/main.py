from argparse import ArgumentParser
from playwright.sync_api import sync_playwright

from domreader.domreader import dom_read
from render import finder_render
from url_image_converter import URLImageConverter


def main():
    parser = ArgumentParser(description="Turns Finder to a web browser.")
    parser.add_argument("url", type=str, help="The URL to open.")
    args = parser.parse_args()

    # center_x, center_y = 500, 300
    # radius = 150
    # count = 100

    # graph_items = [
    #     FinderFile(
    #         title=f"{i+1}",
    #         position=(
    #             int(center_x + math.sin(3 * i + math.pi / 2) * radius),
    #             int(center_y + math.sin(2 * i) * radius)
    #         ),
    #         tag="li"
    #     )
    #     for i in range(count)
    # ]

    # image_x, image_y = 100, 400

    # image_items = [
    #     FinderFile(
    #         title=f"i{i+1}",
    #         position=(
    #             int(image_x + i % 4 * 16),
    #             int(image_y + i // 4 * 16)
    #         ),
    #         tag="img",
    #         icon_path=f"icons/{i+1}.png"
    #     ) for i in range(16)
    # ]

    # finder_render(files=[
    #     FinderFile(
    #         title="Example Link",
    #         position=(100, 100),
    #         is_link=True,
    #         href="https://example.com",
    #         tag="a"
    #     ),
    #     FinderFile(
    #         title="Cam Hack 2025",
    #         position=(100, 200),
    #         tag="h1"
    #     ),
    #     FinderFile(
    #         title="Welcome to Cam Hack 2025!",
    #         position=(250, 200),
    #         tag="p"
    #     ),
    #     *graph_items,
    #     *image_items
    # ])

    # d = CoordinateSystem(args.url, 1000, 1000) # ds.get_width, ds.get_height
    # coords = list(d.coord_all(10))

    # with sync_playwright() as playwright:
    #     coords, title = dom_read(playwright, args.url)
    # finder_render(title, coords)

    converter = URLImageConverter(args.url, icon_limit=210)
    tokens, title = converter.get_image_display(), converter.title
    finder_render(title, tokens)

if __name__ == "__main__":
    main()
