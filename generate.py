from pixels2svg import pixels2svg
from PIL import Image
import json, shutil, os

def cleanup():
    # delete output css
    try:
        os.remove("platform-icons.css")
    except OSError:
        pass

    # delete output directories
    try:
        shutil.rmtree("png")
    except FileNotFoundError:
        pass

    try:
        shutil.rmtree("svg")
    except FileNotFoundError:
        pass

    # re-create them
    os.mkdir("png")
    os.mkdir("svg")

def create_platform_data(labelsets):
    data = ""
    for label in labelsets:
        # create selectors
        matches = ", ".join(
            [f'span.plicon[data-platform="{name}"]' for name in label["names"]] +
            [f'a.plicon-auto[href*="{url}"]::after' for url in label["urls"]]
        )

        # append css rule
        data += f"""{matches} {{
    -webkit-mask-image: url("svg/{label["names"][0]}.svg");
    mask-image: url("svg/{label["names"][0]}.svg");
}}"""
    return data

def generate_css(labelsets):
    # load css base
    base = ""
    with open("base.css") as f:
        base = f.read()
    
    # fill in platform data
    platform_data = create_platform_data(labelsets)
    base = base.replace("[[platform_data]]", platform_data)

    # write result to output css
    with open("platform-icons.css", "x") as f:
        f.write(base)

def main():
    cleanup()

    # load labels
    labelsets = []
    with open("labels.json") as f:
        labelsets = json.loads(f.read())

    # split map into single sprites
    with Image.open("icons.png") as i:
        icons = min(int(i.width/16), len(labelsets))
        for n in range(0, icons):
            label = labelsets[n]
            subimg = i.crop((n*16, 0, (n+1)*16, 16))
            subimg.save(f"png/{label['names'][0]}.png")

    # create svg versions
    for label in labelsets:
        png = f"png/{label['names'][0]}.png"
        pixels2svg(png, f"svg/{label['names'][0]}.svg")

    generate_css(labelsets)

if __name__ == "__main__":
    main()