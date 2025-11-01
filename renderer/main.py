from argparse import ArgumentParser

from render import FinderFile, finder_render
import math

from converter.converter import CoordinateSystem

def main():
    parser = ArgumentParser(description="Turns Finder to a web browser.")
    parser.add_argument(
        "url",
        type=str,
        help="The URL to open."
    )
    args = parser.parse_args()
    
    # center_x, center_y = 500, 300
    # radius = 150
    # count = 200

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
    #     *graph_items
    # ])

    d = CoordinateSystem(args.url, 1000, 1000) # ds.get_width, ds.get_height
    coords = list(d.coord_all().values())
    finder_render("Test Site", coords)

if __name__ == "__main__":
    main()
    # d = CoordinateSystem("https://www.educative.io/answers/how-to-use-gettext-in-beautiful-soup", 1000, 1000) # ds.get_width, ds.get_height
    # coords = d.coord_all()
    # pass
