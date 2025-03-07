import csv
import os
import re



class EUColors:
    def __init__(self):
        self.default_province_colors: dict[tuple[int], int] = {}
        self.tag_colors: dict[str, tuple[int]] = {}
        self.tag_names: dict[str, str] = {} 

    @classmethod
    def load_colors(cls, map_data_folder: str, tag_data_folder: str):
        color = cls()
        print("Loading province definitions....")
        color.default_province_colors = color.load_default_province_colors(map_data_folder)

        print("Loading tag colors....")
        color.tag_names = color.load_tag_names(tag_data_folder)
        color.tag_colors = color.load_tag_colors()

        return color

    def load_default_province_colors(self, map_data_folder: str):
        colors: dict[tuple[int], int] = {}
        with open(os.path.join(map_data_folder, "definition.csv"), "r", encoding="latin-1") as file:
            reader = csv.reader(file, delimiter=";")
            for row in reader:
                try:
                    prov_id = int(row[0])
                    prov_color = tuple(map(int, row[1:4]))
                    colors[prov_color] = prov_id
                except ValueError:
                    continue

        return colors

    def load_tag_names(self, tag_data_folder: str):
        tag_names: dict[str, str] = {}
        tag_pattern = r"(\w{3})\s*=\s*\"([^\"]+)\""

        tag_files = os.listdir(tag_data_folder)
        for tag_file in tag_files:
            with open(os.path.join(tag_data_folder, tag_file), "r", encoding="latin-1") as file:
                for line in file:
                    if not line:
                        continue

                    match = re.match(tag_pattern, line)
                    if match:
                        tag = match.group(1)
                        filename = match.group(2)
                        tag_names[tag] = filename.removesuffix(".txt")
                    else:
                        print(f"Unable to find file or tag for {line}?")

        return tag_names

    def load_tag_colors(self):
        colors: dict[str, tuple[int]] = {}
        color_pattern = r"color\s*=\s*\{\s*(\d+)\s*(\d+)\s*(\d+)\s*\}"
        for tag, country_name in self.tag_names.items():
            try:
                country_path = os.path.join("data", country_name)
                with open(f"{country_path}.txt", "r", encoding="latin-1") as file:
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
                print(f"Unable to find country file {country_path} for tag {tag}")

        return colors
