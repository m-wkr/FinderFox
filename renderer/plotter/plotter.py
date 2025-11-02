import math

from renderer.render import FinderFile


def plotter_render():
    center_x, center_y = 500, 300
    radius = 150
    count = 100

    graph_items = [
        FinderFile(
            title=f"{i+1}",
            position=(
                int(center_x + math.sin(3 * i + math.pi / 2) * radius),
                int(center_y + math.sin(2 * i) * radius),
            ),
            tag="li",
        )
        for i in range(count)
    ]

    image_x, image_y = 100, 400

    image_items = [
        FinderFile(
            title="[Image]",
            position=(int(image_x + i % 4 * 16), int(image_y + i // 4 * 16)),
            tag="img",
            icon_path=f"icons/{i+1}.png",
        )
        for i in range(16)
    ]

    return [
        FinderFile(
            title="Example Link",
            position=(100, 100),
            is_link=True,
            href="https://example.com",
            tag="a",
        ),
        FinderFile(title="Cam Hack 2025", position=(100, 200), tag="h1"),
        FinderFile(title="Welcome to Cam Hack 2025!", position=(100, 300), tag="p"),
        *graph_items,
        *image_items,
    ]
