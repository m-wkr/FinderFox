import tempfile
import subprocess
import logging
import os
import threading
import sys
from ds_store import DSStore

from font import bold, underline
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from scriptWriter import writeBashContents

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def set_icon_process(file_path: str, icon_path: str):
    subprocess.run(["fileicon", "set", file_path, icon_path])


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
    word_use_count = {}

    files.sort(key=lambda finder_file: finder_file.position[1])
    
    if len(files) > 200:
        y_threshold = files[199].position[1]
        files = [finder_file for finder_file in files if finder_file.position[1] <= y_threshold]
    
    coord_min, coord_max = 0, 10000
    valid_files = []

    for finder_file in files:
        x, y = finder_file.position
        if x < coord_min or y < coord_min or x > coord_max or y > coord_max:
            logger.warning(
                "Skipping %s due to out-of-range position %s",
                finder_file.title,
                finder_file.position,
            )
            continue
        valid_files.append(finder_file)
    files = valid_files

    with tempfile.TemporaryDirectory() as tmpdirname:
        logger.info("Created temporary directory %s", tmpdirname)
        os.mkdir(os.path.join(tmpdirname, site_name))

        for file in files:

            file.title = file.title.replace("/", "-").replace("\0", "").replace(".", "․").strip()

            if file.title == "":
                continue

            if len(file.title) > 20:
                logger.warning(
                    "Filename %s is too long, truncating to 20 characters", file.title
                )
                file.title = file.title[:20]

            word_use_count[file.title.lower()] = word_use_count.get(file.title.lower(), 0) + 1

            if word_use_count[file.title.lower()] > 1:
                file.title += "\u200B" * (word_use_count[file.title.lower()] - 1)

            if file.is_link and file.href:
                logger.info("Creating symlink for %s to %s", file.title, file.href)
                file.title = underline(file.title)
                file_path = os.path.join(tmpdirname, site_name, file.title)
                writeBashContents.createBashFile(file_path,file.href)
            else:
                if file.tag == "h1":
                    file.title = bold(file.title)
                file_path = os.path.join(tmpdirname, site_name, file.title)
                with open(file_path, "w") as f:
                    f.write("")

            threads = []

            if file.icon_path:
                t = threading.Thread(
                    target=set_icon_process, args=(file_path, file.icon_path)
                )
                threads.append(t)
            
            for t in threads:
                t.start()

            for t in threads:
                t.join()

        with DSStore.open(os.path.join(tmpdirname, site_name, ".DS_Store"), "w+") as d:
            for i, file in enumerate(files):
                if file.title == "":
                    continue
                logger.info(
                    "Setting icon position for %s to %s", file.title, file.position
                )
                filename = file.title[:32]
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
                "labelOnBottom": False,
                "iconSize": 512,
                "textSize": 16,
                "showIconPreview": False,
            }

        # Open the temporary directory in Finder
        subprocess.run(["open", os.path.join(tmpdirname, site_name)])
        logger.info("Opened Finder at %s", os.path.join(tmpdirname, site_name))

        # Blocking call to keep the temp directory alive for inspection
        input("Press Enter to continue...")
