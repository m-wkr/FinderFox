<img src="docs/Banner.svg" width="100%">

**Browse the web with Finder. Plot graphs, follow links, and explore.**

> Why install Google Chrome when you have Finder?

## Preface

FinderFox is a web browser implemented within the MacOS Finder application, rendering webpages by manipulating the .DS_store file to correctly position and layer files. FinderFox has 4 main features, a graphical renderer, a "retro" file/text based renderer, an integrated search engine, and a mathematical plotting mode.

This project was part of the **CamHack 2025** event, scoring in the top 10 projects and also winning the "Hackiest Hack" track prize.

> Within tight 2 day constraints for CamHack 2025, we created this product for the theme "Unintended Behaviour".

![FinderFox Screenshot](docs/Screenshot1.png)

## Running FinderFox

Run `renderer/main.py` with Python 3.12 on macOS. You will need to install the dependencies in `renderer/pyproject.toml`, and have the [`fileicon`](https://github.com/mklement0/fileicon) utility installed.

```
usage: main.py [-h] [-u URL] [-p] [-t] [--no-links]

Turns Finder to a web browser.

options:
  -h, --help         show this help message and exit
  -u URL, --url URL  The URL to open. If plotting, this is ignored.
  -p, --plot         Make a nice plot.
  -t, --text         Use text-based rendering.
  --no-links         Disable link rendering.
```

In theory, this should work on any macOS version that is later than 10.6 (Snow Leopard, which is the first version that respects the `icvp` property in .DS_Store), given that Python and the dependencies could be properly installed. It is only tested on macOS 26.0.1 (Tahoe).

## Technical Overview

FinderFox operates by creating a temporary folder within the file system, asking Finder to open the directory and allowing it to render web pages.

> [!NOTE]  
> The repo structure is currently not ideal, as the project was created in a rush for the hackathon. We plan to refactor it in the future. Feel free to ask questions or contribute!

### Web Page Rendering

FinderFox is capable of rendering web pages in two modes: graphical and text-based.

In graphical mode, FinderFox uses the [Playwright](https://playwright.dev/python/) library to render the web page in a headless Chromium browser, taking a screenshot of the rendered page. The screenshot is then split into a grid of icons, which are saved as individual files in the temporary folder. The .DS_Store file is then manipulated to position these icons correctly within Finder (see [Manipulating .DS_Store and Icons](#manipulating-ds_store-and-icons)).

In text-based mode, Playwright is still used to fetch the web page, but instead of rendering it graphically, the DOM is extracted and positioned using JavaScript executed within the page context. Each word is saved as a separate file in the temporary folder, and the .DS_Store file is manipulated to position these text files correctly within Finder.

To avoid duplicate naming issues, zero-width spaces are appended to file names as necessary.

### Plots

When the `--plot` flag is used, FinderFox generates a mathematical parametric plot and an image that is larger than the icon sizes, which is achieved by splitting the plot into a grid of icons, similar to the graphical web page rendering mode. It is somewhat unfortunate that the icon sizes must remain consistent within a single folder.

### Links

Links function as Bash shell scripts that calls `main.py` with the target URL when double-clicked. In graphical mode, the link icons are overlaid on top of the rendered webpage at their respective positions. Some environment checking is done to ensure that the script is executable in the right directories.

The links are underlined using U+035F to simulate the appearance of underlined text, as Finder does not support text formatting in file names. Bold texts are converted to mathematical bold sans-serif Unicode characters.

### Search and URL Sanitation

FinderFox uses the [DuckDuckGo](https://duckduckgo.com/) search engine to handle search queries. There is a URL sanitation step that checks and tries to convert user input into valid URLs. If the input is not a valid URL, it is treated as a search query.

### Manipulating .DS_Store and Icons

This project relies on modifying the [.DS_Store](https://en.wikipedia.org/wiki/.DS_Store) file within a directory (and its parent directories) to manipulate how the Finder application displays files in Grid View.

Some reverse engineering was unavoidable due to the format being binary and proprietary. Nonetheless, our work is mostly based on [`ds_store`](https://github.com/dmgbuild/ds_store) Python library and [an excellent documentation by Wim Lewis](https://metacpan.org/dist/Mac-Finder-DSStore/view/DSStoreFormat.pod) in 2013, with some caveats on undocumented changes to the .DS_Store format over the past 12 years.

> **Our Findings**
> 
> More specifically, the precision of `Iloc` records is way less than 4 bytes, and `icvo` records (in both `icvo` and `icv4` modes) are no longer respected by Finder; instead, `icvp` is used solely to set icon view properties.
> 
> There are some hard limits on the values of `icvp` properties, e.g., `iconSize` must be between `16` and `512`, or otherwise Finder will silently revert to defaults. 
> There is also a deprecated `labelOnBottom` property that is not in the GUI but still respected by Finder. We used this to force labels to be shown to the right of the icons.
>
> It seems that, despite `textSize` being a property in `icvp`, it is supposed to be modified in macOS from System Settings > Accessibility > Display > Text Size. However, if the Text Size is set to "Customized in App" or "Use Preferred Reading Size", then the `textSize` property in `icvp` is respected by Finder.
>
> The `icvp` property (which contains a plist) would only work when an unknown specific set of properties are set. We reverse engineered an existing .DS_Store file and copied all existing fields to ensure compatibility, which includes `"backgroundColorBlue"`, `"gridSpacing"`, `"textSize"`, `"backgroundColorRed"`, `"backgroundType"`, `"backgroundColorGreen"`, `"gridOffsetX"`, `"gridOffsetY"`, `"scrollPositionY"`, `"showItemInfo"`, `"viewOptionsVersion"`, `"scrollPositionX"`, `"arrangeBy"`, `"labelOnBottom"`, `"iconSize"`, `"textSize"`, and `"showIconPreview"`.
>
> The Buddy Allocator used by `ds_store` library is capped at reading around 600kB of data, so very large .DS_Store files may cause issues. We are still investigating this.

We had to create subfolders within the main temporary folder, since some properties (like `icvp`) are only respected when set on the parent folder.

File and folder icons are programmatically handled by [`fileicon`](https://github.com/mklement0/fileicon) utility, which modifies related [resource forks](https://en.wikipedia.org/wiki/Resource_fork) to change their appearance.

### Some Final Remarks

- This is a hacky approach to manipulate Finder into a web browser, but fotunately each folder has a self-contained .DS_Store file, so we can create temporary folders without worrying about messing up the user's existing files.

- It should be noted that changing file icons cannot be parallelized due to how resource forks work on macOS, so rendering performance is somewhat limited by this.

- File name length is limited to 255 bytes on macOS, so long words are truncated accordingly.

- FinderFox currently truncates web pages so that the .DS_Store file does not exceed the size limit of the `ds_store` library. Future work may involve creating a custom .DS_Store parser/writer to overcome this limitation. It could also be unavoidable due to how Finder handles large .DS_Store files.

- This project is relatively new in its concept, as previous attempts on file icon manipulating were mostly limited to Windows desktop environments.

- We create quite a number of temporary files during rendering, which are mostly cleaned up after exiting the program. However, in case of crashes or forced termination, some temporary files may remain in the system temporary directory. Images used for icons are suitably placed with heavy leaverage on `__file__` to ensure proper path resolution.

## Future Work

Future improvements may include:
- Refactoring the codebase
- Enhancing rendering performance
- Proper image scaling and tiling in text-based rendering mode
- There is page navigation effort underway in `state_machine.py`

