import csv
import os
import re



def extract_province_colors(defpath: str):
    colors: dict[tuple[int], int] = {}
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

def extract_tag_colors(tag_files: list[str], tags_folder: str):
    missing = 0
    tags: dict[str, str] = {}

    tag_pattern = r"(\w{3})\s*=\s*\"([^\"]+)\""
    for tag_file in tag_files:
        with open(os.path.join(tags_folder, tag_file), "r", encoding="utf-8") as file:
            for line in file:
                if not line:
                    continue

                match = re.match(tag_pattern, line)
                if match:
                    tag = match.group(1)
                    filename = match.group(2)
                    tags[tag] = filename
                else:
                    print(f"Unable to find file or tag for {line}?")
                    missing += 1

    colors: dict[str, tuple[int]] = {}
    color_pattern = r"color\s*=\s*\{\s*(\d+)\s*(\d+)\s*(\d+)\s*\}"
    for tag, country_file in tags.items():
        try:
            country_path = os.path.join("data", country_file)
            with open(country_path, "r", encoding="latin-1") as file:
                for line in file:
                    if not line:
                        continue

                    match = re.match(color_pattern, line)
                    if match:
                        r = int(match.group(1))
                        g = int(match.group(2))
                        b = int(match.group(3))
                        colors[tag] = (r, g, b)
                        break
        except FileNotFoundError:
            print(f"Unable to find country file {filename}")

    return colors
