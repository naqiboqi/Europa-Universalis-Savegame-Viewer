import csv
import json
import os
import re

from PIL import Image



DATA_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
SAVES_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "saves"))
EU4_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "eu4"))


def get_provinces_block(savefile_path: str):
    with open(savefile_path, "r", encoding="utf-8") as file:
        lines = iter(file)
        inside = False
        depth = 0
        data = []

        for line in file:
            line = line.strip()
            if not inside and line == "provinces={":
                next_line = next(lines, "").strip()
                if next_line == "-1={":
                    inside = True
                    depth = 2
                    data.extend([line + "\n", next_line + "\n"])
                    continue

            if inside:
                data.append(line + "\n")
                depth += line.count("{") - line.count("}")
                if depth == 0:
                    break

    return data


def get_country_provinces(datafile_path: str):
    with open(datafile_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    countries: dict[str, list[str]] = {}
    for i in range(len(lines)):
        line = lines[i]
        if is_province_subblock(line):
            j = i

            key = ""
            while not key:
                if j >= len(lines):
                    return countries

                search_line = lines[j].strip()
                key = get_country_id(search_line)
                if key:
                    prov_id = get_prov_id(line)
                    if key in countries:
                        countries[key].append(prov_id)
                    else:
                        countries[key] = [prov_id]
                    i = j
                else:
                    j += 1

    return countries

def get_prov_id(line: str):
    pattern = r"^-(\d+)={"
    match = re.match(pattern, line)
    return match.group(1) if match else None

def is_province_subblock(line: str):
    pattern = r"^-\d+={$"
    return bool(re.match(pattern, line))

def get_country_id(line: str):
    pattern = r'^owner="(\w+)"'
    match = re.match(pattern, line)
    return match.group(1) if match else None


def display_map(bmpath: str):
    bmp = Image.open(bmpath).convert(mode="RGB")
    bmp.show()
    input("Press any key to close")

def main():
    options = [f"{i}. {filename}" for i, filename in enumerate(os.listdir(SAVES_FOLDER), start=1)]

    file_option = None
    while not file_option:
        try:
            print("\n".join(options) + "\n")
            filenum = int(input("Enter savefile number to open: \n"))

            if not 1 <= filenum <= len(options):
                raise IndexError

            file_option = options[filenum - 1]
        except ValueError:
            print("Please enter a number.\n")
        except IndexError:
            print("Not a valid option.\n")


    savefile_path = file_option.split()[-1]
    filepath = os.path.join(SAVES_FOLDER, savefile_path)
    if filepath.endswith(".prov"):
        pass

    defpath = os.path.join(EU4_FOLDER, "definition.csv")
    province_colors = get_province_colors(defpath=defpath)

    bmppath = os.path.join(EU4_FOLDER, "provinces.bmp")
    bmp = Image.open(bmppath).convert("RGB")
    color_provinces(bmp, province_colors)

def color_provinces(bmp: Image.Image, province_colors: dict[str, tuple[int]]):
    provinces = {1}
    country_color = (8,  82,  165)
    pixels = bmp.load()
    width, height = bmp.size
    for x in range(width):
        for y in range(height):
            pixel_color = pixels[x, y]
            if pixel_color in province_colors and province_colors[pixel_color] in provinces:
                pixels[x, y] = country_color
                print(x, y)

    bmp.save("new.png")

def get_province_colors(defpath: str):
    colors: dict[str, tuple[int]] = {}
    with open(defpath, "r", encoding="latin-1") as file:
        reader = csv.reader(file, delimiter=";")
        for row in reader:
            try:
                prov_id = int(row[0])
                prov_color = tuple(map(int, row[1:4]))
                colors[prov_color] = prov_id
            except ValueError:
                continue

    return colors

if __name__ == "__main__":
    main()
