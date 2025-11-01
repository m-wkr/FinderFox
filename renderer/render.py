import tempfile
import subprocess
import logging
import os
from ds_store import DSStore

from font import bold, underline

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class FinderFile:
    def __init__(
        self,
        title: str,
        position: tuple[int, int],
        is_link: bool = False,
        href: str | None = None,
        tag: str | None = None,
        icon_path: str | None = None,
    ):
        self.title: str = title
        self.position: tuple[int, int] = position
        self.is_link: bool = is_link
        self.href: str | None = href
        self.tag: str | None = tag
        self.icon_path: str | None = icon_path

def finder_render(site_name="Test Site", files: list[FinderFile] = []):
    with tempfile.TemporaryDirectory() as tmpdirname:
        logger.info("Created temporary directory %s", tmpdirname)
        os.mkdir(os.path.join(tmpdirname, site_name))

        for file in files:
            file.title = ""
            if file.is_link and file.href:
                logger.info("Creating symlink for %s to %s", file.title, file.href)
                file.title = underline(file.title)
                # TODO: Handle URLs
                os.symlink(file.href, os.path.join(tmpdirname, site_name, file.title))
                file_path = os.path.join(tmpdirname, site_name, file.title)
            else:
                if file.tag == "h1":
                    file.title = bold(file.title)
                file_path = os.path.join(tmpdirname, site_name, file.title)
                with open(file_path, "w") as f:
                    f.write("")
            if file.icon_path:
                subprocess.run([
                    "fileicon", "set", file_path, file.icon_path
                ])

        logger.info("Created %d files in %s", len(files), tmpdirname)

        with DSStore.open(os.path.join(tmpdirname, site_name, ".DS_Store"), "w+") as d:
            for i, file in enumerate(files):
                filename = file.title
                d[filename]["Iloc"] = file.position
            logger.info("Set icon positions in .DS_Store")

        with DSStore.open(os.path.join(tmpdirname, ".DS_Store"), "w+") as d:
            d[site_name]["icvp"] = {
                "backgroundColorBlue": 1.0,
                "gridSpacing": 54.0,
                "textSize": 12.0,
                "backgroundColorRed": 1.0,
                "backgroundType": 0,
                "backgroundColorGreen": 1.0,
                "gridOffsetX": 0.0,
                "gridOffsetY": 0.0,
                "scrollPositionY": 0.0,
                "showItemInfo": False,
                "viewOptionsVersion": 1,
                "scrollPositionX": 0,
                "arrangeBy": "none",
                "labelOnBottom": True,
                "iconSize": 16,
                "textSize": 16,
                "showIconPreview": False,
            }

        # Open the temporary directory in Finder
        subprocess.run(["open", os.path.join(tmpdirname, site_name)])
        logger.info("Opened Finder at %s", os.path.join(tmpdirname, site_name))

        # Blocking call to keep the temp directory alive for inspection
        input("Press Enter to continue...")
